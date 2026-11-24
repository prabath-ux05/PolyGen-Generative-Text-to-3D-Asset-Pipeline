import { useState, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Grid,
  List,
  Search,
  Filter,
  Plus,
  Clock,
  Download,
  Eye,
  MoreVertical,
  CheckCircle,
  Loader,
  XCircle,
  Sparkles,
  Layers,
  Palette,
  Trash2,
  Edit2,
  RotateCcw,
  Box,
  SlidersHorizontal,
} from 'lucide-react'
import { useAssets } from '../../context/AssetContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import AssetInfoModal from './AssetInfoModal.jsx'
import DeleteConfirmModal from './DeleteConfirmModal.jsx'
import RenameModal from './RenameModal.jsx'
import './MyAssets.css'

const statusConfig = {
  completed: { label: 'Completed', icon: CheckCircle, badgeClass: 'badge-green', color: 'green' },
  processing: { label: 'Processing', icon: Loader, badgeClass: 'badge-yellow', color: 'yellow' },
  failed: { label: 'Failed', icon: XCircle, badgeClass: 'badge-red', color: 'red' },
}

function formatDate(isoString) {
  if (!isoString) return '—'
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffH = Math.floor(diffMs / 3_600_000)
  const diffD = Math.floor(diffMs / 86_400_000)
  if (diffH < 1) return 'Just now'
  if (diffH < 24) return `${diffH}h ago`
  if (diffD < 7) return `${diffD}d ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function MyAssets() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { showToast } = useToast()
  const { assets, deleteAsset, renameAsset, resetToDefaults, clearAllAssets } = useAssets()

  // State
  const [viewMode, setViewMode] = useState('grid') // 'grid' | 'list'
  const [searchVal, setSearchVal] = useState(() => searchParams.get('q') || '')
  const [statusFilter, setStatusFilter] = useState('all') // 'all' | 'completed' | 'processing' | 'failed'
  const [formatFilter, setFormatFilter] = useState('all') // 'all' | 'glb' | 'obj' | 'fbx' | 'stl'
  const [textureFilter, setTextureFilter] = useState('all') // 'all' | 'textured' | 'untextured'
  const [sortBy, setSortBy] = useState('newest') // 'newest' | 'oldest' | 'name-asc' | 'name-desc'

  // Modals state
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [assetToDelete, setAssetToDelete] = useState(null)
  const [assetToRename, setAssetToRename] = useState(null)
  const [activeMenuId, setActiveMenuId] = useState(null)

  // Filtering & Sorting (Task 2)
  const filteredAssets = useMemo(() => {
    let result = [...assets]

    // Search by name OR prompt
    const q = searchVal.trim().toLowerCase()
    if (q) {
      result = result.filter(
        (a) =>
          a.name.toLowerCase().includes(q) ||
          a.prompt.toLowerCase().includes(q) ||
          (a.generationId && a.generationId.toLowerCase().includes(q))
      )
    }

    // Filter by generation status
    if (statusFilter !== 'all') {
      result = result.filter((a) => a.status === statusFilter)
    }

    // Filter by model format
    if (formatFilter !== 'all') {
      result = result.filter(
        (a) => a.format && a.format.toLowerCase() === formatFilter.toLowerCase()
      )
    }

    // Filter by texture availability
    if (textureFilter === 'textured') {
      result = result.filter((a) => a.textureInfo?.hasTexture === true)
    } else if (textureFilter === 'untextured') {
      result = result.filter(
        (a) => !a.textureInfo?.hasTexture || a.textureInfo?.textureStatus === 'untextured'
      )
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === 'newest') {
        return new Date(b.createdAt) - new Date(a.createdAt)
      }
      if (sortBy === 'oldest') {
        return new Date(a.createdAt) - new Date(b.createdAt)
      }
      if (sortBy === 'name-asc') {
        return a.name.localeCompare(b.name)
      }
      if (sortBy === 'name-desc') {
        return b.name.localeCompare(a.name)
      }
      return 0
    })

    return result
  }, [assets, searchVal, statusFilter, formatFilter, textureFilter, sortBy])

  // Asset Actions (Task 3)
  function handleOpenInViewer(asset) {
    if (asset.modelUrl) {
      navigate('/create', { state: { asset } })
    } else {
      setSelectedAsset(asset)
    }
  }

  function handleViewDetails(asset) {
    setSelectedAsset(asset)
  }

  function handleDownload(asset) {
    if (asset.modelUrl) {
      const link = document.createElement('a')
      link.href = asset.modelUrl
      link.download = `${asset.name.toLowerCase().replace(/\s+/g, '-')}.${asset.format?.toLowerCase() || 'obj'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      showToast({
        title: `Downloading ${asset.name}`,
        message: `Saved as ${link.download}`,
        type: 'success',
      })
    } else {
      showToast({
        title: 'Download Unavailable',
        message: `Asset "${asset.name}" has no synthesized model file yet.`,
        type: 'warning',
      })
    }
  }

  function handleDeleteConfirmed(id) {
    const deleted = assets.find((a) => a.id === id)
    deleteAsset(id)
    if (selectedAsset?.id === id) {
      setSelectedAsset(null)
    }
    showToast({
      title: 'Asset Removed',
      message: `"${deleted?.name || 'Asset'}" deleted from active session.`,
      type: 'info',
    })
  }

  function handleRenameSaved(id, newName) {
    renameAsset(id, newName)
    if (selectedAsset?.id === id) {
      setSelectedAsset((prev) => ({ ...prev, name: newName }))
    }
    showToast({
      title: 'Asset Renamed',
      message: `Updated name to "${newName}".`,
      type: 'success',
    })
  }

  function handleResetFilters() {
    setSearchVal('')
    setStatusFilter('all')
    setFormatFilter('all')
    setTextureFilter('all')
    setSortBy('newest')
  }

  return (
    <div className="my-assets-page">
      {/* ── Page Header ── */}
      <div className="my-assets-header">
        <div className="my-assets-header-left">
          <div className="my-assets-badge badge badge-purple">
            <Box size={11} />
            Asset Library
          </div>
          <h1 className="page-title">My Assets</h1>
          <p className="page-subtitle">
            Manage, inspect, filter, and preview your synthesized 3D models and textures.
          </p>
        </div>

        <div className="my-assets-header-right">
          {/* Test State Helper Controls */}
          <div className="test-state-buttons">
            <button
              type="button"
              className="btn btn-ghost btn-xs text-muted"
              onClick={clearAllAssets}
              title="Empties the gallery to verify the Task 6 Empty State requirement"
            >
              Test Empty State
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-xs text-muted"
              onClick={resetToDefaults}
              title="Restores the sample 3D assets"
            >
              <RotateCcw size={11} />
              Reset Defaults
            </button>
          </div>

          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => navigate('/create')}
          >
            <Plus size={14} />
            Create 3D Model
          </button>
        </div>
      </div>

      {/* ── Search & Filter Toolbar (Task 2) ── */}
      <div className="my-assets-toolbar card">
        <div className="toolbar-search-row">
          {/* Search Input */}
          <div className="toolbar-search-wrap">
            <Search size={15} className="toolbar-search-icon" />
            <input
              type="text"
              className="input toolbar-search-input"
              placeholder="Search by asset name or prompt…"
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
            />
            {searchVal && (
              <button
                type="button"
                className="toolbar-search-clear"
                onClick={() => setSearchVal('')}
                aria-label="Clear search"
              >
                ×
              </button>
            )}
          </div>

          {/* Sort Selector */}
          <div className="toolbar-sort-wrap">
            <SlidersHorizontal size={13} className="text-muted" />
            <select
              className="select toolbar-sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              aria-label="Sort assets"
            >
              <option value="newest">Sort: Newest First</option>
              <option value="oldest">Sort: Oldest First</option>
              <option value="name-asc">Sort: Name (A – Z)</option>
              <option value="name-desc">Sort: Name (Z – A)</option>
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="toolbar-view-toggle">
            <button
              type="button"
              className={`view-toggle-btn ${viewMode === 'grid' ? 'view-toggle-active' : ''}`}
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
              title="Grid View"
            >
              <Grid size={15} />
            </button>
            <button
              type="button"
              className={`view-toggle-btn ${viewMode === 'list' ? 'view-toggle-active' : ''}`}
              onClick={() => setViewMode('list')}
              aria-label="List view"
              title="List View"
            >
              <List size={15} />
            </button>
          </div>
        </div>

        {/* Filter Pills Row */}
        <div className="toolbar-filters-row">
          <div className="filter-group">
            <span className="filter-group-label">
              <Filter size={11} />
              Status:
            </span>
            {['all', 'completed', 'processing', 'failed'].map((st) => (
              <button
                key={st}
                type="button"
                className={`filter-pill ${statusFilter === st ? 'filter-pill-active' : ''}`}
                onClick={() => setStatusFilter(st)}
              >
                {st.charAt(0).toUpperCase() + st.slice(1)}
              </button>
            ))}
          </div>

          <div className="filter-separator" />

          <div className="filter-group">
            <span className="filter-group-label">Format:</span>
            {['all', 'glb', 'obj', 'fbx'].map((fmt) => (
              <button
                key={fmt}
                type="button"
                className={`filter-pill ${formatFilter === fmt ? 'filter-pill-active' : ''}`}
                onClick={() => setFormatFilter(fmt)}
              >
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="filter-separator" />

          <div className="filter-group">
            <span className="filter-group-label">
              <Palette size={11} />
              Texture:
            </span>
            {[
              { id: 'all', label: 'All' },
              { id: 'textured', label: 'Textured' },
              { id: 'untextured', label: 'Clay / None' },
            ].map((t) => (
              <button
                key={t.id}
                type="button"
                className={`filter-pill ${textureFilter === t.id ? 'filter-pill-active' : ''}`}
                onClick={() => setTextureFilter(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Active filters count & reset */}
          {(searchVal || statusFilter !== 'all' || formatFilter !== 'all' || textureFilter !== 'all') && (
            <button
              type="button"
              className="btn btn-ghost btn-xs text-accent toolbar-reset-btn"
              onClick={handleResetFilters}
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* ── Gallery Counter Summary ── */}
      <div className="my-assets-count-row">
        <span>
          Showing <strong>{filteredAssets.length}</strong> of <strong>{assets.length}</strong> total assets
        </span>
        {assets.length > 0 && (
          <span className="asset-storage-hint">
            3D models stored locally in WebGL memory
          </span>
        )}
      </div>

      {/* ── Asset Gallery Content (Task 1 & Task 6) ── */}
      {assets.length === 0 ? (
        /* Empty State: Library has 0 assets (Task 6) */
        <div className="assets-empty-hero card">
          <div className="empty-hero-icon-wrap">
            <Box size={44} className="text-accent" />
          </div>
          <h2 className="empty-hero-title">No assets generated yet.</h2>
          <p className="empty-hero-desc">
            Transform text prompts into interactive 3D assets with real geometry and textures.
          </p>
          <button
            type="button"
            className="btn btn-primary empty-hero-btn"
            onClick={() => navigate('/create')}
          >
            <Sparkles size={14} />
            Create Your First 3D Model
          </button>
        </div>
      ) : filteredAssets.length === 0 ? (
        /* Empty State: Filters returned no results */
        <div className="assets-no-match card">
          <Search size={32} className="text-muted" />
          <h3>No matching assets found</h3>
          <p>
            No assets match &ldquo;{searchVal}&rdquo; with the selected filters.
          </p>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={handleResetFilters}
          >
            Clear All Filters
          </button>
        </div>
      ) : viewMode === 'grid' ? (
        /* ── Grid View ── */
        <div className="assets-grid-layout">
          {filteredAssets.map((asset) => {
            const status = statusConfig[asset.status] || statusConfig.completed
            const StatusIcon = status.icon
            const hasTex = asset.textureInfo?.hasTexture

            return (
              <div key={asset.id} className="asset-grid-card card card-hover">
                {/* Thumbnail / 3D Shape Preview (Task 1) */}
                <div
                  className="asset-grid-thumb"
                  style={{ '--card-thumb-color': asset.thumbnailColor }}
                  onClick={() => handleViewDetails(asset)}
                >
                  <div className="asset-grid-thumb-bg" aria-hidden="true" />
                  <div className="asset-grid-thumb-shape" aria-hidden="true">
                    <Box size={38} style={{ color: asset.thumbnailColor }} />
                  </div>

                  {asset.status === 'processing' && (
                    <div className="asset-grid-thumb-overlay">
                      <Loader size={26} className="spin-icon text-accent" />
                      <span>Generating…</span>
                    </div>
                  )}

                  {/* Badges on Thumbnail */}
                  <div className="asset-grid-badges-top">
                    <span className={`badge ${status.badgeClass}`}>
                      <StatusIcon size={10} className={asset.status === 'processing' ? 'spin-icon' : ''} />
                      {status.label}
                    </span>
                    {asset.format !== '—' && (
                      <span className="badge badge-purple">{asset.format}</span>
                    )}
                  </div>

                  {/* Texture pill */}
                  <div className="asset-grid-badges-bottom">
                    <span className={`texture-pill ${
                      hasTex && asset.textureInfo?.textureStatus === 'applied'
                        ? 'texture-pill-applied'
                        : asset.textureInfo?.textureStatus === 'missing'
                        ? 'texture-pill-missing'
                        : 'texture-pill-clay'
                    }`}>
                      <Palette size={9} />
                      {hasTex && asset.textureInfo?.textureStatus === 'applied'
                        ? 'Textured'
                        : asset.textureInfo?.textureStatus === 'missing'
                        ? 'Missing Tex'
                        : 'Clay'}
                    </span>
                  </div>
                </div>

                {/* Info Container */}
                <div className="asset-grid-info">
                  <div className="asset-grid-info-header">
                    <div>
                      <h3
                        className="asset-grid-name"
                        onClick={() => handleViewDetails(asset)}
                        title={asset.name}
                      >
                        {asset.name}
                      </h3>
                      <span className="asset-grid-id">ID: {asset.generationId || asset.id}</span>
                    </div>

                    {/* Actions Menu */}
                    <div className="asset-card-menu-wrap">
                      <button
                        type="button"
                        className="btn btn-ghost btn-icon btn-xs"
                        onClick={() => setActiveMenuId(activeMenuId === asset.id ? null : asset.id)}
                        aria-label="More actions"
                      >
                        <MoreVertical size={14} />
                      </button>

                      {activeMenuId === asset.id && (
                        <div
                          className="asset-dropdown-menu"
                          onClick={() => setActiveMenuId(null)}
                        >
                          <button
                            type="button"
                            className="dropdown-item"
                            onClick={() => handleViewDetails(asset)}
                          >
                            <Eye size={13} />
                            View Details
                          </button>
                          <button
                            type="button"
                            className="dropdown-item"
                            onClick={() => setAssetToRename(asset)}
                          >
                            <Edit2 size={13} />
                            Rename Asset
                          </button>
                          {asset.status === 'completed' && (
                            <button
                              type="button"
                              className="dropdown-item"
                              onClick={() => handleDownload(asset)}
                            >
                              <Download size={13} />
                              Download Model
                            </button>
                          )}
                          <div className="dropdown-divider" />
                          <button
                            type="button"
                            className="dropdown-item text-red"
                            onClick={() => setAssetToDelete(asset)}
                          >
                            <Trash2 size={13} />
                            Delete Asset
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Prompt Excerpt */}
                  <p className="asset-grid-prompt" title={asset.prompt}>
                    {asset.prompt}
                  </p>

                  {/* Mesh Stats (Task 4) */}
                  <div className="asset-grid-mesh-stats">
                    {asset.meshMetadata ? (
                      <>
                        <span title="Polygon count">
                          <Layers size={11} />
                          {asset.meshMetadata.faces.toLocaleString()} polys
                        </span>
                        <span>{asset.meshMetadata.vertices.toLocaleString()} verts</span>
                      </>
                    ) : (
                      <span className="text-muted">Metrics pending</span>
                    )}
                  </div>

                  {/* Footer Actions (Task 3) */}
                  <div className="asset-grid-footer">
                    <span className="asset-grid-date">
                      <Clock size={11} />
                      {formatDate(asset.createdAt)}
                    </span>

                    <div className="asset-grid-action-buttons">
                      <button
                        type="button"
                        className="btn btn-ghost btn-xs asset-btn-view"
                        onClick={() => handleViewDetails(asset)}
                        title="View Asset Details & 3D Model"
                      >
                        <Eye size={12} />
                        Details
                      </button>
                      {asset.status === 'completed' && (
                        <button
                          type="button"
                          className="btn btn-secondary btn-xs"
                          onClick={() => handleOpenInViewer(asset)}
                          title="Open in Studio 3D Viewer"
                        >
                          <Box size={12} />
                          3D
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        /* ── List View (Task 2) ── */
        <div className="assets-list-container card">
          <table className="assets-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Generation ID</th>
                <th>Original Prompt</th>
                <th>Format</th>
                <th>Status</th>
                <th>Metrics</th>
                <th>Texture</th>
                <th>Created</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssets.map((asset) => {
                const status = statusConfig[asset.status] || statusConfig.completed
                const StatusIcon = status.icon
                const hasTex = asset.textureInfo?.hasTexture

                return (
                  <tr key={asset.id} className="assets-table-row">
                    <td>
                      <div className="table-asset-name-cell" onClick={() => handleViewDetails(asset)}>
                        <div
                          className="table-asset-thumb"
                          style={{ background: `${asset.thumbnailColor}22` }}
                        >
                          <Box size={16} style={{ color: asset.thumbnailColor }} />
                        </div>
                        <span className="table-asset-title">{asset.name}</span>
                      </div>
                    </td>
                    <td>
                      <span className="table-mono-id">{asset.generationId || asset.id}</span>
                    </td>
                    <td>
                      <span className="table-prompt-cell" title={asset.prompt}>
                        {asset.prompt}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-purple">{asset.format || 'GLB'}</span>
                    </td>
                    <td>
                      <span className={`badge ${status.badgeClass}`}>
                        <StatusIcon size={10} className={asset.status === 'processing' ? 'spin-icon' : ''} />
                        {status.label}
                      </span>
                    </td>
                    <td>
                      {asset.meshMetadata ? (
                        <span className="table-metrics-cell">
                          {asset.meshMetadata.faces.toLocaleString()} tris
                        </span>
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td>
                      <span className={`texture-pill ${
                        hasTex && asset.textureInfo?.textureStatus === 'applied'
                          ? 'texture-pill-applied'
                          : asset.textureInfo?.textureStatus === 'missing'
                          ? 'texture-pill-missing'
                          : 'texture-pill-clay'
                      }`}>
                        {hasTex && asset.textureInfo?.textureStatus === 'applied'
                          ? 'Textured'
                          : asset.textureInfo?.textureStatus === 'missing'
                          ? 'Missing'
                          : 'Clay'}
                      </span>
                    </td>
                    <td>
                      <span className="table-date-cell">{formatDate(asset.createdAt)}</span>
                    </td>
                    <td className="text-right">
                      <div className="table-actions-cell">
                        <button
                          type="button"
                          className="btn btn-ghost btn-icon btn-xs"
                          onClick={() => handleViewDetails(asset)}
                          title="View Details"
                        >
                          <Eye size={13} />
                        </button>
                        {asset.status === 'completed' && (
                          <button
                            type="button"
                            className="btn btn-ghost btn-icon btn-xs"
                            onClick={() => handleDownload(asset)}
                            title="Download Model"
                          >
                            <Download size={13} />
                          </button>
                        )}
                        <button
                          type="button"
                          className="btn btn-ghost btn-icon btn-xs text-red"
                          onClick={() => setAssetToDelete(asset)}
                          title="Delete Asset"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Asset Details Modal (Task 4 & Task 5) ── */}
      {selectedAsset && (
        <AssetInfoModal
          asset={selectedAsset}
          isOpen={!!selectedAsset}
          onClose={() => setSelectedAsset(null)}
          onDelete={(a) => {
            setSelectedAsset(null)
            setAssetToDelete(a)
          }}
          onRename={(a) => {
            setSelectedAsset(null)
            setAssetToRename(a)
          }}
          onDownload={handleDownload}
          onOpenInStudio={handleOpenInViewer}
        />
      )}

      {/* ── Delete Confirmation Modal (Task 3) ── */}
      {assetToDelete && (
        <DeleteConfirmModal
          asset={assetToDelete}
          isOpen={!!assetToDelete}
          onClose={() => setAssetToDelete(null)}
          onConfirm={handleDeleteConfirmed}
        />
      )}

      {/* ── Rename Asset Modal (Task 3) ── */}
      {assetToRename && (
        <RenameModal
          asset={assetToRename}
          isOpen={!!assetToRename}
          onClose={() => setAssetToRename(null)}
          onSave={handleRenameSaved}
        />
      )}
    </div>
  )
}

export default MyAssets
