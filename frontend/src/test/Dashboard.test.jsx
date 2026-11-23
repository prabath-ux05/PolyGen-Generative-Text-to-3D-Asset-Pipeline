import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard/Dashboard.jsx'
import { ToastProvider } from '../context/ToastContext.jsx'

// Mock ModelViewer to avoid heavy WebGL canvas in jsdom for Dashboard test
vi.mock('../components/ModelViewer/ModelViewer.jsx', () => ({
  default: ({ modelUrl }) => (
    <div data-testid="mock-model-viewer">
      <span>Viewer: {modelUrl}</span>
    </div>
  ),
}))

// Mock generationService
vi.mock('../services/generationService.js', async () => {
  const actual = await vi.importActual('../services/generationService.js')
  return {
    ...actual,
    submitGeneration: vi.fn(),
    simulateMockGeneration: vi.fn(),
  }
})

function renderDashboard() {
  return render(
    <MemoryRouter>
      <ToastProvider>
        <Dashboard />
      </ToastProvider>
    </MemoryRouter>
  )
}

describe('Dashboard Page Component', () => {
  it('renders hero title and PolyGen description', () => {
    const { container } = renderDashboard()

    const heroTitle = container.querySelector('.dashboard-hero-title')
    expect(heroTitle).toBeInTheDocument()
    expect(heroTitle.textContent).toContain('Create Anything in 3D')

    expect(
      screen.getByText(/Describe any object, scene, or character in natural language/i)
    ).toBeInTheDocument()
  })

  it('renders quick statistics cards', () => {
    renderDashboard()

    expect(screen.getByText(/Total Generations/i)).toBeInTheDocument()
    expect(screen.getByText(/Completed Models/i)).toBeInTheDocument()
    expect(screen.getByText(/Processing Jobs/i)).toBeInTheDocument()
    expect(screen.getByText(/Saved Assets/i)).toBeInTheDocument()
  })

  it('renders prompt input and 3D preview viewport', () => {
    renderDashboard()

    const textarea = screen.getByPlaceholderText(/Describe the 3D model you want to create/i)
    expect(textarea).toBeInTheDocument()

    const viewer = screen.getByTestId('mock-model-viewer')
    expect(viewer).toBeInTheDocument()
  })

  it('renders recent assets gallery section', () => {
    renderDashboard()

    expect(screen.getByText(/Recent Generations/i)).toBeInTheDocument()
    expect(screen.getAllByText(/Medieval Castle/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Futuristic Spaceship/i).length).toBeGreaterThan(0)
  })
})
