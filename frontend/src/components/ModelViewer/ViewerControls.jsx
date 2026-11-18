import { useState } from 'react'
import {
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Grid,
  Maximize2,
  Minimize2,
  Info,
  Layers,
  Palette,
  X,
  FileCode,
  Box,
} from 'lucide-react'

function ViewerControls({
  onResetView,
  onZoomIn,
  onZoomOut,
  showGrid,
  onToggleGrid,
  wireframe,
  onToggleWireframe,
  showTexture = true,
  onToggleTexture,
  textureStatus,
  isFullscreen,
  onToggleFullscreen,
  modelStats,
  currentModelUrl,
  onSelectModel,
}) {
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [showModelPicker, setShowModelPicker] = useState(false)

  const testModels = [
    { label: 'Sample Crystal (OBJ)', url: '/models/sample-crystal.obj', format: 'OBJ' },
    { label: 'Sample Chair (OBJ)', url: '/models/sample-chair.obj', format: 'OBJ' },
    { label: 'Test Invalid URL (Error Test)', url: '/models/non-existent-model.obj', format: 'OBJ' },
    { label: 'Clear / Empty Viewport', url: '', format: '—' },
  ]

  return (
    <div className="viewer-controls-wrapper">
      {/* ── Top Bar: Active model pill & model switcher ── */}
      <div className="viewer-top-bar">
        <div className="viewer-model-badge">
          <Box size={13} className="text-accent" />
          <span className="viewer-model-badge-name">
            {currentModelUrl
              ? currentModelUrl.split('/').pop()
              : 'No Model Loaded'}
          </span>
          {modelStats && (
            <span className="viewer-model-badge-poly">
              {modelStats.triangles?.toLocaleString() || '0'} tris
            </span>
          )}
        </div>

        <div className="viewer-model-picker-wrap">
          <button
            type="button"
            className="btn btn-ghost btn-sm viewer-picker-btn"
            onClick={() => setShowModelPicker((v) => !v)}
            title="Switch 3D model"
          >
            <FileCode size={13} />
            <span>Switch Model</span>
          </button>

          {showModelPicker && (
            <div className="viewer-picker-dropdown">
              <div className="viewer-picker-header">
                <span>Select 3D Test Asset</span>
                <button
                  type="button"
                  className="viewer-picker-close"
                  onClick={() => setShowModelPicker(false)}
                >
                  <X size={12} />
                </button>
              </div>
              <div className="viewer-picker-list">
                {testModels.map((m, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className={`viewer-picker-item ${
                      currentModelUrl === m.url ? 'picker-item-active' : ''
                    }`}
                    onClick={() => {
                      if (onSelectModel) onSelectModel(m.url, m.label)
                      setShowModelPicker(false)
                    }}
                  >
                    <span>{m.label}</span>
                    <span className="picker-format-tag">{m.format}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Floating Viewport Toolbar ── */}
      <div className="viewer-toolbar" role="toolbar" aria-label="3D Viewer Controls">
        {/* Reset View */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onResetView}
          title="Reset Camera View"
          aria-label="Reset View"
        >
          <RotateCcw size={16} />
        </button>

        <div className="viewer-tool-separator" />

        {/* Zoom In */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onZoomIn}
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn size={16} />
        </button>

        {/* Zoom Out */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onZoomOut}
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut size={16} />
        </button>

        <div className="viewer-tool-separator" />

        {/* Grid Toggle */}
        <button
          type="button"
          className={`viewer-tool-btn ${showGrid ? 'viewer-tool-active' : ''}`}
          onClick={onToggleGrid}
          title={showGrid ? 'Hide Reference Grid' : 'Show Reference Grid'}
          aria-label="Toggle Grid"
          aria-pressed={showGrid}
        >
          <Grid size={16} />
        </button>

        {/* Wireframe Toggle */}
        <button
          type="button"
          className={`viewer-tool-btn ${wireframe ? 'viewer-tool-active' : ''}`}
          onClick={onToggleWireframe}
          title={wireframe ? 'Solid Shading' : 'Wireframe Inspection'}
          aria-label="Toggle Wireframe"
          aria-pressed={wireframe}
        >
          <Layers size={16} />
        </button>

        {/* Texture Comparison Toggle (Task 5: Compare textured vs untextured clay) */}
        {onToggleTexture && (
          <button
            type="button"
            className={`viewer-tool-btn ${showTexture ? 'viewer-tool-active' : ''}`}
            onClick={onToggleTexture}
            title={showTexture ? 'Texture Active: Click to view Untextured Clay' : 'Clay Active: Click to apply 2D Texture'}
            aria-label="Toggle Texture Shading"
            aria-pressed={showTexture}
          >
            <Palette size={16} />
          </button>
        )}

        <div className="viewer-tool-separator" />

        {/* Model Information */}
        <button
          type="button"
          className={`viewer-tool-btn ${showInfoModal ? 'viewer-tool-active' : ''}`}
          onClick={() => setShowInfoModal((v) => !v)}
          title="Model Information & Statistics"
          aria-label="Model Information"
          aria-expanded={showInfoModal}
        >
          <Info size={16} />
        </button>

        {/* Fullscreen Toggle */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onToggleFullscreen}
          title={isFullscreen ? 'Exit Fullscreen' : 'View Fullscreen'}
          aria-label="Toggle Fullscreen"
        >
          {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
        </button>
      </div>

      {/* ── Model Info Flyout Modal ── */}
      {showInfoModal && (
        <div className="viewer-info-modal" role="dialog" aria-labelledby="viewer-info-title">
          <div className="viewer-info-header">
            <h4 id="viewer-info-title" className="viewer-info-title">
              <Info size={14} className="text-accent" />
              3D Asset Inspection
            </h4>
            <button
              type="button"
              className="viewer-info-close"
              onClick={() => setShowInfoModal(false)}
              aria-label="Close information modal"
            >
              <X size={14} />
            </button>
          </div>

          <div className="viewer-info-body">
            {modelStats ? (
              <div className="viewer-info-grid">
                <div className="viewer-info-row">
                  <span className="info-label">Asset Source</span>
                  <span className="info-val info-val-mono" title={modelStats.url}>
                    {modelStats.url?.split('/').pop() || 'Loaded Model'}
                  </span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Format</span>
                  <span className="info-val">{modelStats.format || 'OBJ'}</span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Polygons (Tris)</span>
                  <span className="info-val info-val-highlight">
                    {modelStats.triangles?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Vertices</span>
                  <span className="info-val">
                    {modelStats.vertices?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Sub-Meshes</span>
                  <span className="info-val">{modelStats.meshCount || 1}</span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Bounding Box</span>
                  <span className="info-val info-val-mono">
                    {modelStats.dimensions
                      ? `${modelStats.dimensions.x} × ${modelStats.dimensions.y} × ${modelStats.dimensions.z}`
                      : 'Normalized (3 units)'}
                  </span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Texture Map</span>
                  <span className={`info-val ${
                    textureStatus?.status === 'loaded'
                      ? 'info-val-success'
                      : textureStatus?.status === 'error'
                      ? 'info-val-warning'
                      : ''
                  }`}>
                    {textureStatus?.status === 'loaded'
                      ? (showTexture ? 'Textured (PBR Map)' : 'Untextured Clay (Comparison)')
                      : textureStatus?.status === 'error'
                      ? 'Missing (Fallback Clay)'
                      : showTexture
                      ? 'PBR Shading'
                      : 'Untextured Clay'}
                  </span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Auto-Centering</span>
                  <span className="info-val info-val-success">Applied [0, 0, 0]</span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Shading</span>
                  <span className="info-val">{wireframe ? 'Wireframe' : 'PBR Standard Mesh'}</span>
                </div>
              </div>
            ) : (
              <p className="viewer-info-empty">
                No active 3D model loaded in the viewport. Select or generate a model to inspect its geometry metrics.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ViewerControls
