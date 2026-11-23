import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import GenerationStatusPanel from '../components/GenerationStatus/GenerationStatusPanel.jsx'

describe('GenerationStatusPanel Component', () => {
  it('returns null when no job is provided', () => {
    const { container } = render(<GenerationStatusPanel job={null} />)
    expect(container.firstChild).toBeNull()
  })

  it('renders pending status with job ID, prompt, and indeterminate bar', () => {
    const job = {
      job_id: 'task-gen-alpha-001',
      status: 'pending',
      prompt: 'A futuristic cyber sword',
      created_at: new Date().toISOString(),
      output_format: 'glb',
      is_mock: false,
    }

    const { container } = render(<GenerationStatusPanel job={job} />)

    expect(screen.getByText(/3D Generation Task/i)).toBeInTheDocument()
    expect(screen.getByText(/ID: task-gen-alpha-001/i)).toBeInTheDocument()
    expect(screen.getByText(/A futuristic cyber sword/i)).toBeInTheDocument()
    expect(container.querySelector('.status-pill-pending')).toBeInTheDocument()
    expect(screen.getByText(/Live Backend/i)).toBeInTheDocument()
  })

  it('renders processing status with live backend tag', () => {
    const job = {
      job_id: 'task-proc-999',
      status: 'processing',
      prompt: 'A golden goblet',
      created_at: new Date().toISOString(),
      output_format: 'obj',
      is_mock: false,
    }

    const { container } = render(<GenerationStatusPanel job={job} />)

    expect(container.querySelector('.status-pill-processing')).toBeInTheDocument()
    expect(screen.getByText(/Format: OBJ/i)).toBeInTheDocument()
  })

  it('renders completed status with Inspect in 3D Viewer action', () => {
    const onViewIn3D = vi.fn()
    const job = {
      job_id: 'task-comp-001',
      status: 'completed',
      prompt: 'A sci-fi crystal',
      model_url: '/models/sample-crystal.obj',
      created_at: new Date().toISOString(),
      output_format: 'glb',
      is_mock: false,
    }

    const { container } = render(<GenerationStatusPanel job={job} onViewIn3D={onViewIn3D} />)

    expect(container.querySelector('.status-pill-completed')).toBeInTheDocument()
    const viewBtn = screen.getByRole('button', { name: /inspect in 3d viewer/i })
    expect(viewBtn).toBeInTheDocument()

    fireEvent.click(viewBtn)
    expect(onViewIn3D).toHaveBeenCalledWith('/models/sample-crystal.obj')
  })

  it('renders failed status with error message and retry button', () => {
    const onRetry = vi.fn()
    const job = {
      job_id: 'task-fail-002',
      status: 'failed',
      prompt: 'Invalid prompt structure',
      error_message: 'GPU memory limit exceeded',
      created_at: new Date().toISOString(),
      is_mock: false,
    }

    render(<GenerationStatusPanel job={job} onRetry={onRetry} />)

    expect(screen.getByText(/Generation Failed/i)).toBeInTheDocument()
    expect(screen.getByText(/GPU memory limit exceeded/i)).toBeInTheDocument()

    const retryBtn = screen.getByRole('button', { name: /retry backend request/i })
    fireEvent.click(retryBtn)
    expect(onRetry).toHaveBeenCalledTimes(1)
  })

  it('renders unavailable (503) status with FastAPI engine pending notice', () => {
    const onSimulate = vi.fn()
    const onRetry = vi.fn()
    const job = {
      job_id: 'task-503-003',
      status: 'unavailable',
      prompt: 'Neon cyber tree',
      error_message: 'Text-to-3D generation engine is not yet integrated into the backend pipeline.',
      created_at: new Date().toISOString(),
      is_mock: false,
    }

    render(
      <GenerationStatusPanel
        job={job}
        onSimulatePipeline={onSimulate}
        onRetry={onRetry}
      />
    )

    expect(screen.getByText(/Service Unavailable \(503\)/i)).toBeInTheDocument()
    expect(screen.getByText(/FastAPI Backend: Request Validated \(HTTP 503\)/i)).toBeInTheDocument()

    const simBtn = screen.getByRole('button', { name: /run simulated pipeline demo/i })
    fireEvent.click(simBtn)
    expect(onSimulate).toHaveBeenCalledTimes(1)
  })

  it('handles dismiss action callback', () => {
    const onDismiss = vi.fn()
    const job = {
      job_id: 'task-dismiss-1',
      status: 'completed',
      prompt: 'Test asset',
      created_at: new Date().toISOString(),
    }

    render(<GenerationStatusPanel job={job} onDismiss={onDismiss} />)

    const dismissBtn = screen.getByRole('button', { name: /dismiss status notification/i })
    fireEvent.click(dismissBtn)
    expect(onDismiss).toHaveBeenCalledTimes(1)
  })
})
