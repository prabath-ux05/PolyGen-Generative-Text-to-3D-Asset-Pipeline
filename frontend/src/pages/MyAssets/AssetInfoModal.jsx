import { useState } from 'react'
import {
  X,
  Copy,
  Check,
  Download,
  Trash2,
  Edit2,
  Box,
  Layers,
  Palette,
  Maximize2,
  Sparkles,
  AlertTriangle,
  Info,
  Clock,
  CheckCircle,
  Loader,
  XCircle,
} from 'lucide-react'
import ModelViewer from '../../components/ModelViewer/ModelViewer.jsx'
import './MyAssets.css'

const statusConfig = {
  completed: { label: 'Completed', icon: CheckCircle, badgeClass: 'badge-green' },
  processing: { label: 'Processing', icon: Loader, badgeClass: 'badge-yellow' },
  failed: { label: 'Failed', icon: XCircle, badgeClass: 'badge-red' },
}

function AssetInfoModal({
  asset,
  isOpen,
  onClose,
  onDelete,
  onRename,
  onDownload,
  onOpenInStudio,
}) {
  const [copiedPrompt, setCopiedPrompt] = useState(false)
  const [textureMode, setTextureMode] = useState('textured') // 'textured' | 'clay'
  const [textureImgError, setTextureImgError] = useState(false)

  if (!isOpen || !asset) return null

  const status = statusConfig[asset.status] || statusConfig.completed
  const StatusIcon = status.icon
  const hasTexture = asset.textureInfo?.hasTexture && asset.textureInfo?.diffuseUrl
  const isMissingTexture = asset.textureInfo?.textureStatus === 'missing'

  function handleCopyPrompt() {
    if (!asset.prompt) return
    navigator.clipboard.writeText(asset.prompt)
    setCopiedPrompt(true)
    setTimeout(() => setCopiedPrompt(false), 2000)
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="asset-modal-container card"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="asset-modal-header">
          <div className="asset-modal-title-group">
            <div className="asset-modal-icon-badge" style={{ background: `${asset.thumbnailColor}22` }}>
              <Box size={20} style={{ color: asset.thumbnailColor }} />
            </div>
            <div>
              <div className="asset-modal-title-row">
                <h2 className="asset-modal-title">{asset.name}</h2>
                <button
                  type="button"
                  className="btn btn-ghost btn-icon btn-sm"
                  onClick={() => onRename && onRename(asset)}
                  title="Rename Asset"
                >
                  <Edit2 size={13} />
                </button>
              </div>
              <div className="asset-modal-sub-badges">
                <span className={`badge ${status.badgeClass}`}>
                  <StatusIcon size={11} className={asset.status === 'processing' ? 'spin-icon' : ''} />
                  {status.label}
                </span>
                <span className="badge badge-purple">{asset.format || 'GLB'}</span>
                <span className="asset-modal-genid">ID: {asset.generationId || asset.id}</span>
              </div>
            </div>
          </div>

          <div className="asset-modal-header-actions">
            {onOpenInStudio && asset.status === 'completed' && (
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => onOpenInStudio(asset)}
              >
                <Maximize2 size={13} />
                Open in Studio
              </button>
            )}
            <button
              type="button"
              className="btn btn-ghost btn-icon asset-modal-close-btn"
              onClick={onClose}
              aria-label="Close modal"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="asset-modal-body">
          {/* Left Column: 3D Viewport or Status State */}
          <div className="asset-modal-viewport-section">
            <div className="asset-modal-canvas-wrap">
              {asset.status === 'completed' && asset.modelUrl ? (
                <ModelViewer
                  modelUrl={asset.modelUrl}
                  textureUrl={hasTexture && !isMissingTexture ? asset.textureInfo.diffuseUrl : null}
                  showTexture={textureMode === 'textured'}
                  height="100%"
                />
              ) : asset.status === 'processing' ? (
                <div className="asset-modal-empty-view">
                  <Loader size={36} className="spin-icon text-accent" />
                  <h4>Model Generation in Progress</h4>
                  <p>Synthesizing geometry, NeRF fields, and textures. Status: Processing.</p>
                </div>
              ) : asset.status === 'failed' ? (
                <div className="asset-modal-empty-view">
                  <XCircle size={36} className="text-red" />
                  <h4>Generation Failed</h4>
                  <p>{asset.errorMessage || 'Text-to-3D pipeline failed during mesh extraction.'}</p>
                </div>
              ) : (
                <div className="asset-modal-empty-view">
                  <Box size={36} className="text-muted" />
                  <h4>No 3D Model File Available</h4>
                  <p>Model output file is not available in local test assets.</p>
                </div>
              )}
            </div>

            {/* Quick Shader Control Banner */}
            {asset.status === 'completed' && (
              <div className="asset-modal-shader-bar">
                <span className="shader-bar-label">
                  <Palette size={13} />
                  Shading Comparison:
                </span>
                <div className="shader-toggle-group">
                  <button
                    type="button"
                    className={`shader-toggle-btn ${textureMode === 'textured' ? 'shader-toggle-active' : ''}`}
                    onClick={() => setTextureMode('textured')}
                  >
                    Textured PBR
                  </button>
                  <button
                    type="button"
                    className={`shader-toggle-btn ${textureMode === 'clay' ? 'shader-toggle-active' : ''}`}
                    onClick={() => setTextureMode('clay')}
                  >
                    Untextured Clay
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Complete Metadata & Texture Inspector */}
          <div className="asset-modal-details-section">
            {/* Original Prompt */}
            <div className="asset-detail-card">
              <div className="asset-detail-card-header">
                <span className="asset-detail-title">Original Prompt</span>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm btn-icon"
                  onClick={handleCopyPrompt}
                  title="Copy Prompt"
                >
                  {copiedPrompt ? <Check size={13} className="text-green" /> : <Copy size={13} />}
                </button>
              </div>
              <p className="asset-prompt-full">&ldquo;{asset.prompt}&rdquo;</p>
              <div className="asset-created-row">
                <Clock size={12} />
                <span>Generated on {new Date(asset.createdAt).toLocaleString()}</span>
              </div>
            </div>

            {/* Mesh Processing Metadata (Task 4) */}
            <div className="asset-detail-card">
              <div className="asset-detail-card-header">
                <span className="asset-detail-title">
                  <Layers size={14} className="text-accent" />
                  Mesh Processing Metrics
                </span>
                <span className="asset-source-tag">Supplied by Mesh Pipeline</span>
              </div>

              {asset.meshMetadata ? (
                <div className="asset-metrics-grid">
                  <div className="asset-metric-item">
                    <span className="metric-label">Vertices</span>
                    <span className="metric-val">{asset.meshMetadata.vertices.toLocaleString()}</span>
                  </div>
                  <div className="asset-metric-item">
                    <span className="metric-label">Polygons / Faces</span>
                    <span className="metric-val metric-val-highlight">
                      {asset.meshMetadata.faces.toLocaleString()}
                    </span>
                  </div>
                  <div className="asset-metric-item">
                    <span className="metric-label">Dimensions (X×Y×Z)</span>
                    <span className="metric-val metric-val-mono">
                      {asset.meshMetadata.dimensions.x} × {asset.meshMetadata.dimensions.y} × {asset.meshMetadata.dimensions.z}
                    </span>
                  </div>
                  <div className="asset-metric-item">
                    <span className="metric-label">Target Polys</span>
                    <span className="metric-val">
                      {asset.meshMetadata.polygonTarget ? asset.meshMetadata.polygonTarget.toLocaleString() : 'Auto'}
                    </span>
                  </div>
                  <div className="asset-metric-item">
                    <span className="metric-label">Sub-Meshes</span>
                    <span className="metric-val">{asset.meshMetadata.submeshes || 1}</span>
                  </div>
                  <div className="asset-metric-item">
                    <span className="metric-label">Topology</span>
                    <span className="metric-val text-green">{asset.meshMetadata.topology || 'Manifold'}</span>
                  </div>
                </div>
              ) : (
                <div className="asset-metrics-empty">
                  <Info size={13} />
                  <span>Mesh metadata not available until generation and optimization complete.</span>
                </div>
              )}
            </div>

            {/* Texture Output & Preview Panel (Task 5) */}
            <div className="asset-detail-card">
              <div className="asset-detail-card-header">
                <span className="asset-detail-title">
                  <Palette size={14} className="text-accent" />
                  Texture Synthesis & Output
                </span>
                <span className={`badge ${
                  asset.textureInfo?.textureStatus === 'applied'
                    ? 'badge-green'
                    : asset.textureInfo?.textureStatus === 'missing'
                    ? 'badge-red'
                    : 'badge-purple'
                }`}>
                  {asset.textureInfo?.textureStatus === 'applied'
                    ? 'Textured'
                    : asset.textureInfo?.textureStatus === 'missing'
                    ? 'Texture Missing'
                    : asset.textureInfo?.textureStatus === 'untextured'
                    ? 'Untextured Clay'
                    : 'Generating Texture'}
                </span>
              </div>

              {/* Texture Swatch / Preview */}
              <div className="texture-preview-box">
                {asset.textureInfo?.diffuseUrl && !isMissingTexture ? (
                  <div className="texture-swatch-wrap">
                    <img
                      src={asset.textureInfo.diffuseUrl}
                      alt={`${asset.name} 2D texture`}
                      className="texture-swatch-img"
                      onError={() => setTextureImgError(true)}
                    />
                    {textureImgError && (
                      <div className="texture-swatch-error">
                        <AlertTriangle size={18} />
                        <span>Texture image unreachable</span>
                      </div>
                    )}
                  </div>
                ) : isMissingTexture ? (
                  <div className="texture-missing-banner">
                    <AlertTriangle size={16} className="text-yellow" />
                    <div>
                      <strong>Missing Texture Output</strong>
                      <p>2D diffuse map could not be located. A fallback procedural clay material is rendered in the 3D viewer.</p>
                    </div>
                  </div>
                ) : (
                  <div className="texture-clay-banner">
                    <Sparkles size={16} className="text-accent" />
                    <div>
                      <strong>Untextured / Clay Mode</strong>
                      <p>Asset synthesized without diffuse textures. Displaying high-contrast PBR clay shader.</p>
                    </div>
                  </div>
                )}

                <div className="texture-specs-list">
                  <div className="texture-spec-row">
                    <span className="spec-label">Resolution</span>
                    <span className="spec-val">{asset.textureInfo?.resolution || '—'}</span>
                  </div>
                  <div className="texture-spec-row">
                    <span className="spec-label">Map Type</span>
                    <span className="spec-val">{asset.textureInfo?.textureMapType || 'Diffuse (Albedo)'}</span>
                  </div>
                  <div className="texture-spec-row">
                    <span className="spec-label">Format</span>
                    <span className="spec-val">{asset.textureInfo?.format || 'PNG'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="asset-modal-footer">
          <div className="asset-modal-footer-left">
            <button
              type="button"
              className="btn btn-ghost btn-sm text-red"
              onClick={() => onDelete && onDelete(asset)}
            >
              <Trash2 size={13} />
              Delete Asset
            </button>
          </div>

          <div className="asset-modal-footer-right">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onDownload && onDownload(asset)}
              disabled={asset.status !== 'completed'}
            >
              <Download size={13} />
              Download {asset.format || '3D Asset'}
            </button>
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={onClose}
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AssetInfoModal
