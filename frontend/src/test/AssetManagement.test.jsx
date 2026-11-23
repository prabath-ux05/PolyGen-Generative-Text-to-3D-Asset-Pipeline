import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import MyAssets from '../pages/MyAssets/MyAssets.jsx'
import { AssetProvider } from '../context/AssetContext.jsx'
import { ToastProvider } from '../context/ToastContext.jsx'

// Mock ModelViewer
vi.mock('../components/ModelViewer/ModelViewer.jsx', () => ({
  default: () => <div data-testid="mock-modal-viewer">Model Viewer Mock</div>,
}))

function renderMyAssets() {
  return render(
    <MemoryRouter>
      <AssetProvider>
        <ToastProvider>
          <MyAssets />
        </ToastProvider>
      </AssetProvider>
    </MemoryRouter>
  )
}

describe('MyAssets Management Page', () => {
  it('renders page header and initial asset cards', () => {
    renderMyAssets()

    expect(screen.getByRole('heading', { level: 1, name: /My Assets/i })).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Search by asset name or prompt…/i)).toBeInTheDocument()

    expect(screen.getByText('Medieval Castle')).toBeInTheDocument()
    expect(screen.getByText('Futuristic Spaceship')).toBeInTheDocument()
  })

  it('filters assets by search query (by name and prompt)', () => {
    renderMyAssets()

    const searchInput = screen.getByPlaceholderText(/Search by asset name or prompt…/i)
    fireEvent.change(searchInput, { target: { value: 'Spaceship' } })

    expect(screen.getByText('Futuristic Spaceship')).toBeInTheDocument()
    expect(screen.queryByText('Medieval Castle')).not.toBeInTheDocument()
  })

  it('shows empty state when search matches no assets', () => {
    renderMyAssets()

    const searchInput = screen.getByPlaceholderText(/Search by asset name or prompt…/i)
    fireEvent.change(searchInput, { target: { value: 'nonexistent-query-xyz' } })

    expect(screen.getByText(/No matching assets found/i)).toBeInTheDocument()
  })

  it('toggles between grid and list views', () => {
    const { container } = renderMyAssets()

    expect(container.querySelector('.assets-grid-layout')).toBeInTheDocument()

    const listViewBtn = screen.getByRole('button', { name: /List view/i })
    fireEvent.click(listViewBtn)

    expect(container.querySelector('.assets-list-container')).toBeInTheDocument()
  })

  it('filters assets by format filter pill (OBJ vs GLB)', () => {
    renderMyAssets()

    const objFilterBtn = screen.getByRole('button', { name: /^OBJ$/i })
    fireEvent.click(objFilterBtn)

    expect(screen.getByText('Futuristic Spaceship')).toBeInTheDocument()
    expect(screen.queryByText('Medieval Castle')).not.toBeInTheDocument()
  })

  it('opens Asset Details modal when clicking an asset card', () => {
    renderMyAssets()

    const castleCard = screen.getByTitle('Medieval Castle')
    fireEvent.click(castleCard)

    expect(screen.getByRole('button', { name: /Close modal/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Medieval Castle' })).toBeInTheDocument()
  })
})
