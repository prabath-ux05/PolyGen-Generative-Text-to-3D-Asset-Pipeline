import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import {
  ViewerEmptyState,
  ViewerErrorState,
  ViewerLoadingState,
} from '../components/ModelViewer/ViewerFallback.jsx'

describe('ModelViewer Fallback Components', () => {
  describe('ViewerEmptyState', () => {
    it('renders empty viewport messaging and interactive badges', () => {
      render(<ViewerEmptyState />)

      expect(screen.getByText(/Your 3D model will appear here/i)).toBeInTheDocument()
      expect(screen.getByText(/Interactive 3D Engine/i)).toBeInTheDocument()
      expect(
        screen.getByText(/Generate an asset using the prompt pipeline/i)
      ).toBeInTheDocument()
    })

    it('renders sample model buttons and triggers selection callback', () => {
      const onSelectSample = vi.fn()
      render(<ViewerEmptyState onSelectSample={onSelectSample} />)

      const crystalBtn = screen.getByRole('button', { name: /Load Sample Crystal \(OBJ\)/i })
      const chairBtn = screen.getByRole('button', { name: /Load Sample Chair \(OBJ\)/i })

      expect(crystalBtn).toBeInTheDocument()
      expect(chairBtn).toBeInTheDocument()

      fireEvent.click(crystalBtn)
      expect(onSelectSample).toHaveBeenCalledWith('/models/sample-crystal.obj', 'Crystal')

      fireEvent.click(chairBtn)
      expect(onSelectSample).toHaveBeenCalledWith('/models/sample-chair.obj', 'Chair')
    })
  })

  describe('ViewerErrorState', () => {
    it('renders error notice and custom error message', () => {
      render(
        <ViewerErrorState
          error="Network timeout: Failed to fetch GLB buffer"
          onRetry={vi.fn()}
        />
      )

      expect(screen.getByText(/Failed to load 3D model/i)).toBeInTheDocument()
      expect(screen.getByText(/Network timeout: Failed to fetch GLB buffer/i)).toBeInTheDocument()
      expect(screen.getByText(/Model Load Error/i)).toBeInTheDocument()
    })

    it('triggers onRetry and onFallback callbacks when clicked', () => {
      const onRetry = vi.fn()
      const onFallback = vi.fn()

      render(
        <ViewerErrorState
          error="Invalid OBJ format"
          onRetry={onRetry}
          onFallback={onFallback}
        />
      )

      const retryBtn = screen.getByRole('button', { name: /Retry Loading/i })
      const fallbackBtn = screen.getByRole('button', { name: /Load Test Model Instead/i })

      fireEvent.click(retryBtn)
      expect(onRetry).toHaveBeenCalledTimes(1)

      fireEvent.click(fallbackBtn)
      expect(onFallback).toHaveBeenCalledTimes(1)
    })
  })

  describe('ViewerLoadingState', () => {
    it('renders loading spinner and default loading text', () => {
      render(<ViewerLoadingState />)

      expect(screen.getByText(/Loading 3D asset…/i)).toBeInTheDocument()
    })

    it('renders custom message and progress percentage bar', () => {
      const { container } = render(
        <ViewerLoadingState message="Downloading binary mesh…" progress={65} />
      )

      expect(screen.getByText(/Downloading binary mesh…/i)).toBeInTheDocument()
      const fillBar = container.querySelector('.viewer-loading-bar-fill')
      expect(fillBar).toHaveStyle({ width: '65%' })
    })
  })
})
