import { useState, useRef, useEffect } from 'react'
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
  Camera,
  Sun,
  Monitor,
  Copy,
  Check,
} from 'lucide-react'

function ViewerControls({
  onSetCameraView,
  onZoomIn,
  onZoomOut,
  showGrid,
  onToggleGrid,
  wireframe,
  onToggleWireframe,
  showTexture = true,
  onToggleTexture,
  textureStatus,
  lightingPreset = 'default',
  onSelectLighting,
  backgroundPreset = 'nebula',
  onSelectBackground,
  isFullscreen,
  onToggleFullscreen,
  modelStats,
  currentModelUrl,
  generationId,
  assetName,
  onSelectModel,
}) {
  const [showInfoPanel, setShowInfoPanel] = useState(false)
  const [showModelPicker, setShowModelPicker] = useState(false)
  const [showCameraMenu, setShowCameraMenu] = useState(false)
  const [showLightingMenu, setShowLightingMenu] = useState(false)
  const [showBackgroundMenu, setShowBackgroundMenu] = useState(false)
  const [copiedSpecs, setCopiedSpecs] = useState(false)

  const cameraMenuRef = useRef(null)
  const lightingMenuRef = useRef(null)
  const bgMenuRef = useRef(null)

  // Close popovers on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (cameraMenuRef.current && !cameraMenuRef.current.contains(e.target)) {
        setShowCameraMenu(false)
      }
      if (lightingMenuRef.current && !lightingMenuRef.current.contains(e.target)) {
        setShowLightingMenu(false)
      }
      if (bgMenuRef.current && !bgMenuRef.current.contains(e.target)) {
        setShowBackgroundMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const testModels = [
    { label: 'Sample Crystal (OBJ)', url: '/models/sample-crystal.obj', format: 'OBJ' },
    { label: 'Sample Chair (OBJ)', url: '/models/sample-chair.obj', format: 'OBJ' },
    { label: 'Test Invalid URL (Error Test)', url: '/models/non-existent-model.obj', format: 'OBJ' },
    { label: 'Clear / Empty Viewport', url: '', format: '—' },
  ]

  const cameraViews = [
    { key: 'reset', label: 'Default Perspective' },
    { key: 'fit', label: 'Fit Model to View' },
    { key: 'front', label: 'Front View (Z-Axis)' },
    { key: 'side', label: 'Side View (X-Axis)' },
    { key: 'top', label: 'Top View (Y-Axis)' },
    { key: 'iso', label: 'Isometric View' },
  ]

  const lightingPresets = [
    { id: 'default', label: 'Default Lighting', desc: 'Balanced ambient & directional key' },
    { id: 'studio', label: 'Studio Dramatic', desc: 'Rim light, high-contrast key, fill' },
    { id: 'soft', label: 'Soft Diffused', desc: 'High ambient, low-contrast shadows' },
  ]

  const backgroundPresets = [
    { id: 'nebula', label: 'Dark Nebula', color: '#15192b' },
    { id: 'studio', label: 'Studio Slate', color: '#1e293b' },
    { id: 'black', label: 'Pitch Black', color: '#050508' },
    { id: 'cyber', label: 'Cyber Grid', color: '#0b0f19' },
  ]

  function handleCopySpecs() {
    if (!modelStats) return
    const specsText = `PolyGen 3D Model Specifications
----------------------------------
Asset: ${assetName || currentModelUrl?.split('/').pop() || 'Model'}
Generation ID: ${generationId || 'Local Asset'}
Format: ${modelStats.format || 'OBJ'}
Polygons: ${modelStats.triangles?.toLocaleString() || 0} tris
Vertices: ${modelStats.vertices?.toLocaleString() || 0}
Bounding Box: ${modelStats.dimensions ? `${modelStats.dimensions.x}m × ${modelStats.dimensions.y}m × ${modelStats.dimensions.z}m` : '3.2 units'}
Sub-Meshes: ${modelStats.meshCount || 1}
Texture Status: ${textureStatus?.status || (showTexture ? 'Textured' : 'Clay')}
Source: ${modelStats.url || currentModelUrl}`

    navigator.clipboard.writeText(specsText)
    setCopiedSpecs(true)
    setTimeout(() => setCopiedSpecs(false), 2000)
  }

  return (
    <div className="viewer-controls-wrapper">
      {/* ── Top Bar: Active model pill & model switcher ── */}
      <div className="viewer-top-bar">
        <div className="viewer-model-badge">
          <Box size={13} className="text-accent" />
          <span className="viewer-model-badge-name">
            {assetName || (currentModelUrl ? currentModelUrl.split('/').pop() : 'No Model Loaded')}
          </span>
          {modelStats && (
            <span className="viewer-model-badge-poly">
              {modelStats.triangles?.toLocaleString() || '0'} tris
            </span>
          )}
          {generationId && (
            <span className="viewer-model-badge-genid" title={`Generation ID: ${generationId}`}>
              {generationId.length > 14 ? generationId.slice(0, 14) + '…' : generationId}
            </span>
          )}
        </div>

        <div className="viewer-top-actions">
          {/* Switch Model Dropdown */}
          <div className="viewer-model-picker-wrap">
            <button
              type="button"
              className="btn btn-ghost btn-sm viewer-picker-btn"
              onClick={() => setShowModelPicker((v) => !v)}
              title="Switch 3D test asset"
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
      </div>

      {/* ── Floating Viewport Toolbar (Task 1 & Task 2) ── */}
      <div className="viewer-toolbar" role="toolbar" aria-label="3D Viewer Controls">
        {/* Reset Camera */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={() => onSetCameraView('reset')}
          title="Reset Camera View (Default)"
          aria-label="Reset View"
        >
          <RotateCcw size={15} />
        </button>

        {/* Camera Views Menu (Task 1: Front, Side, Top, Iso, Fit) */}
        <div className="viewer-popover-wrap" ref={cameraMenuRef}>
          <button
            type="button"
            className={`viewer-tool-btn ${showCameraMenu ? 'viewer-tool-active' : ''}`}
            onClick={() => {
              setShowCameraMenu((v) => !v)
              setShowLightingMenu(false)
              setShowBackgroundMenu(false)
            }}
            title="Camera View Presets (Front, Side, Top, Iso)"
            aria-label="Camera Views"
            aria-expanded={showCameraMenu}
          >
            <Camera size={15} />
          </button>

          {showCameraMenu && (
            <div className="viewer-dropdown-panel viewer-camera-dropdown">
              <div className="viewer-dropdown-title">Camera Angles</div>
              {cameraViews.map((v) => (
                <button
                  key={v.key}
                  type="button"
                  className="viewer-dropdown-item"
                  onClick={() => {
                    onSetCameraView(v.key)
                    setShowCameraMenu(false)
                  }}
                >
                  <span>{v.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="viewer-tool-separator" />

        {/* Zoom In & Out */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onZoomIn}
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn size={15} />
        </button>
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onZoomOut}
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut size={15} />
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
          <Grid size={15} />
        </button>

        {/* Wireframe Toggle (Task 1) */}
        <button
          type="button"
          className={`viewer-tool-btn ${wireframe ? 'viewer-tool-active' : ''}`}
          onClick={onToggleWireframe}
          title={wireframe ? 'Solid Shading' : 'Wireframe Inspection'}
          aria-label="Toggle Wireframe"
          aria-pressed={wireframe}
        >
          <Layers size={15} />
        </button>

        {/* Texture Comparison Toggle (Task 1) */}
        {onToggleTexture && (
          <button
            type="button"
            className={`viewer-tool-btn ${showTexture ? 'viewer-tool-active' : ''}`}
            onClick={onToggleTexture}
            title={showTexture ? 'Texture Active: Click to view Untextured Clay' : 'Clay Active: Click to apply 2D Texture'}
            aria-label="Toggle Texture Shading"
            aria-pressed={showTexture}
          >
            <Palette size={15} />
          </button>
        )}

        <div className="viewer-tool-separator" />

        {/* Lighting Presets Menu (Task 1: Studio, Soft, Default) */}
        <div className="viewer-popover-wrap" ref={lightingMenuRef}>
          <button
            type="button"
            className={`viewer-tool-btn ${lightingPreset !== 'default' || showLightingMenu ? 'viewer-tool-active' : ''}`}
            onClick={() => {
              setShowLightingMenu((v) => !v)
              setShowCameraMenu(false)
              setShowBackgroundMenu(false)
            }}
            title={`Lighting: ${lightingPreset.charAt(0).toUpperCase() + lightingPreset.slice(1)}`}
            aria-label="Lighting Controls"
            aria-expanded={showLightingMenu}
          >
            <Sun size={15} />
          </button>

          {showLightingMenu && (
            <div className="viewer-dropdown-panel viewer-lighting-dropdown">
              <div className="viewer-dropdown-title">Lighting Setup</div>
              {lightingPresets.map((l) => (
                <button
                  key={l.id}
                  type="button"
                  className={`viewer-dropdown-item ${lightingPreset === l.id ? 'dropdown-item-active' : ''}`}
                  onClick={() => {
                    onSelectLighting(l.id)
                    setShowLightingMenu(false)
                  }}
                >
                  <div>
                    <div className="dropdown-item-name">{l.label}</div>
                    <div className="dropdown-item-desc">{l.desc}</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Background Presets Menu (Task 1: Nebula, Studio, Black, Cyber) */}
        <div className="viewer-popover-wrap" ref={bgMenuRef}>
          <button
            type="button"
            className={`viewer-tool-btn ${backgroundPreset !== 'nebula' || showBackgroundMenu ? 'viewer-tool-active' : ''}`}
            onClick={() => {
              setShowBackgroundMenu((v) => !v)
              setShowCameraMenu(false)
              setShowLightingMenu(false)
            }}
            title="Viewport Background"
            aria-label="Background Controls"
            aria-expanded={showBackgroundMenu}
          >
            <Monitor size={15} />
          </button>

          {showBackgroundMenu && (
            <div className="viewer-dropdown-panel viewer-bg-dropdown">
              <div className="viewer-dropdown-title">Background Theme</div>
              {backgroundPresets.map((b) => (
                <button
                  key={b.id}
                  type="button"
                  className={`viewer-dropdown-item ${backgroundPreset === b.id ? 'dropdown-item-active' : ''}`}
                  onClick={() => {
                    onSelectBackground(b.id)
                    setShowBackgroundMenu(false)
                  }}
                >
                  <span className="bg-preset-dot" style={{ background: b.color }} />
                  <span>{b.label}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="viewer-tool-separator" />

        {/* Expandable Model Information Panel (Task 2) */}
        <button
          type="button"
          className={`viewer-tool-btn ${showInfoPanel ? 'viewer-tool-active' : ''}`}
          onClick={() => setShowInfoPanel((v) => !v)}
          title="Expandable Model Information & Metrics"
          aria-label="Model Information"
          aria-expanded={showInfoPanel}
        >
          <Info size={15} />
        </button>

        {/* Fullscreen Toggle (Task 1) */}
        <button
          type="button"
          className="viewer-tool-btn"
          onClick={onToggleFullscreen}
          title={isFullscreen ? 'Exit Fullscreen' : 'View Fullscreen'}
          aria-label="Toggle Fullscreen"
        >
          {isFullscreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
        </button>
      </div>

      {/* ── Expandable Model Information Panel (Task 2) ── */}
      {showInfoPanel && (
        <div
          className="viewer-info-panel-expandable"
          role="region"
          aria-labelledby="viewer-panel-title"
        >
          <div className="viewer-info-header">
            <div className="viewer-info-title-wrap">
              <Info size={15} className="text-accent" />
              <h4 id="viewer-panel-title" className="viewer-info-title">
                Model Information
              </h4>
            </div>
            <div className="viewer-info-header-actions">
              {modelStats && (
                <button
                  type="button"
                  className="btn btn-ghost btn-xs"
                  onClick={handleCopySpecs}
                  title="Copy technical specifications"
                >
                  {copiedSpecs ? <Check size={12} className="text-green" /> : <Copy size={12} />}
                  <span>{copiedSpecs ? 'Copied!' : 'Copy'}</span>
                </button>
              )}
              <button
                type="button"
                className="viewer-info-close"
                onClick={() => setShowInfoPanel(false)}
                aria-label="Close information panel"
              >
                <X size={14} />
              </button>
            </div>
          </div>

          <div className="viewer-info-body">
            {modelStats ? (
              <div className="viewer-info-grid">
                {/* Asset Name */}
                <div className="viewer-info-row">
                  <span className="info-label">Asset Name</span>
                  <span className="info-val font-semibold">
                    {assetName || modelStats.url?.split('/').pop() || '3D Asset'}
                  </span>
                </div>

                {/* Generation ID (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Generation ID</span>
                  <span className="info-val info-val-mono" title={generationId || 'Local Asset'}>
                    {generationId || 'gen-local-session'}
                  </span>
                </div>

                {/* Format (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Format</span>
                  <span className="info-val badge-tag">{modelStats.format || 'OBJ'}</span>
                </div>

                {/* Dimensions (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Dimensions (X×Y×Z)</span>
                  <span className="info-val info-val-mono">
                    {modelStats.dimensions
                      ? `${modelStats.dimensions.x}m × ${modelStats.dimensions.y}m × ${modelStats.dimensions.z}m`
                      : '3.20m normalized'}
                  </span>
                </div>

                {/* Vertices (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Vertices</span>
                  <span className="info-val">{modelStats.vertices?.toLocaleString() || '0'}</span>
                </div>

                {/* Faces / Polygons (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Faces / Triangles</span>
                  <span className="info-val info-val-highlight">
                    {modelStats.triangles?.toLocaleString() || '0'} tris
                  </span>
                </div>

                {/* Texture Information (Task 2) */}
                <div className="viewer-info-row">
                  <span className="info-label">Texture Info</span>
                  <span className={`info-val ${
                    textureStatus?.status === 'loaded'
                      ? 'info-val-success'
                      : textureStatus?.status === 'error'
                      ? 'info-val-warning'
                      : ''
                  }`}>
                    {textureStatus?.status === 'loaded'
                      ? (showTexture ? 'Applied PBR Diffuse' : 'Untextured Clay')
                      : textureStatus?.status === 'error'
                      ? 'Missing (Fallback Clay)'
                      : showTexture
                      ? 'PBR Shading'
                      : 'Untextured Clay'}
                  </span>
                </div>

                {/* Lighting Active */}
                <div className="viewer-info-row">
                  <span className="info-label">Lighting Preset</span>
                  <span className="info-val">
                    {lightingPreset.charAt(0).toUpperCase() + lightingPreset.slice(1)} Studio
                  </span>
                </div>

                {/* Sub-Meshes & Centering */}
                <div className="viewer-info-row">
                  <span className="info-label">Sub-Meshes</span>
                  <span className="info-val">{modelStats.meshCount || 1} mesh</span>
                </div>
                <div className="viewer-info-row">
                  <span className="info-label">Coordinates</span>
                  <span className="info-val info-val-success">Origin Centered [0, 0, 0]</span>
                </div>
              </div>
            ) : (
              <div className="viewer-info-empty-state">
                <Box size={28} className="text-muted" />
                <p>No model loaded in viewport. Select a model to inspect its geometry metrics.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ViewerControls
