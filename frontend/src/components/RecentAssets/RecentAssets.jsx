import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Clock, Download, Eye, MoreHorizontal, CheckCircle, Loader, XCircle } from 'lucide-react'
import { mockRecentAssets } from '../../data/mockData.js'
import './RecentAssets.css'

const statusConfig = {
  completed: { label: 'Completed', icon: CheckCircle, color: 'green' },
  processing: { label: 'Processing', icon: Loader,       color: 'yellow' },
  failed:     { label: 'Failed',     icon: XCircle,      color: 'red' },
}

function formatDate(isoString) {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now - date
  const diffH = Math.floor(diffMs / 3_600_000)
  const diffD = Math.floor(diffMs / 86_400_000)
  if (diffH < 1)  return 'Just now'
  if (diffH < 24) return `${diffH}h ago`
  if (diffD < 7)  return `${diffD}d ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function AssetCard({ asset, onPreview }) {
  const status = statusConfig[asset.status] || statusConfig.completed
  const StatusIcon = status.icon

  return (
    <div className="asset-card card card-hover">
      {/* Thumbnail */}
      <div className="asset-thumb" style={{ '--thumb-color': asset.thumbnailColor }}>
        <div className="asset-thumb-bg" aria-hidden="true" />
        <div className="asset-thumb-icon">
          <div className="asset-3d-shape" aria-hidden="true" />
        </div>
        {asset.status === 'processing' && (
          <div className="asset-thumb-overlay">
            <Loader size={20} className="asset-loading-spinner" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="asset-info">
        <div className="asset-info-top">
          <h3 className="asset-name">{asset.name}</h3>
          <button className="btn btn-ghost btn-icon asset-more-btn" aria-label="More options">
            <MoreHorizontal size={15} />
          </button>
        </div>

        <p className="asset-prompt">{asset.prompt}</p>

        <div className="asset-meta">
          <span className={`badge badge-${status.color}`}>
            <StatusIcon size={10} className={asset.status === 'processing' ? 'spin-icon' : ''} />
            {status.label}
          </span>
          {asset.format !== '—' && (
            <span className="asset-format">{asset.format}</span>
          )}
          {asset.polygons !== '—' && (
            <span className="asset-polygons">{asset.polygons} polys</span>
          )}
        </div>

        <div className="asset-footer">
          <span className="asset-date">
            <Clock size={11} />
            {formatDate(asset.createdAt)}
          </span>
          {asset.status === 'completed' && (
            <div className="asset-actions">
              <button
                className="btn btn-ghost btn-sm asset-action-btn"
                aria-label="Preview"
                onClick={() => onPreview && onPreview(asset)}
              >
                <Eye size={13} />
                Preview
              </button>
              <button
                className="btn btn-secondary btn-sm asset-action-btn"
                aria-label="Download"
                title="Download available when backend is connected"
              >
                <Download size={13} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function RecentAssets({ limit = 6, searchQuery = '', viewMode = 'grid' }) {
  const navigate = useNavigate()
  const [filter, setFilter] = useState('all')
  const filters = ['all', 'completed', 'processing', 'failed']

  const normalizedQuery = searchQuery.trim().toLowerCase()
  const filtered = mockRecentAssets
    .filter(a => filter === 'all' || a.status === filter)
    .filter(a =>
      !normalizedQuery ||
      a.name.toLowerCase().includes(normalizedQuery) ||
      a.prompt.toLowerCase().includes(normalizedQuery)
    )
    .slice(0, limit)

  function handlePreview() {
    navigate('/create')
  }

  return (
    <section className="recent-assets">
      <div className="recent-assets-header">
        <div>
          <h2 className="section-title">Recent Generations</h2>
          <p className="recent-assets-count">{filtered.length} of {mockRecentAssets.length} assets</p>
        </div>
        <div className="recent-assets-filters">
          {filters.map(f => (
            <button
              key={f}
              className={`recent-filter-btn ${filter === f ? 'recent-filter-active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {filtered.length > 0 ? (
        <div className={`recent-assets-grid ${viewMode === 'list' ? 'recent-assets-list' : ''}`}>
          {filtered.map(asset => (
            <AssetCard key={asset.id} asset={asset} onPreview={handlePreview} />
          ))}
        </div>
      ) : (
        <div className="recent-assets-empty">
          <p>No {filter !== 'all' ? filter : ''} assets match your search.</p>
        </div>
      )}
    </section>
  )
}

export default RecentAssets
