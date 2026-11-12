import React, { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Wand2, Settings2, Sliders, Info } from 'lucide-react'
import PromptInput from '../../components/PromptInput/PromptInput.jsx'
import EmptyState from '../../components/EmptyState/EmptyState.jsx'
import './CreateModel.css'

const qualityOptions = ['Draft', 'Standard', 'High', 'Ultra']
const formatOptions  = ['GLB', 'OBJ', 'FBX', 'STL']
const styleOptions   = ['Realistic', 'Stylized', 'Low Poly', 'Sci-Fi', 'Fantasy']

function CreateModel() {
  const location = useLocation()
  const selectedTemplate = location.state?.template || null
  const [quality, setQuality]   = useState('Standard')
  const [format, setFormat]     = useState('GLB')
  const [style, setStyle]       = useState('Realistic')
  const [polyTarget, setPolyTarget] = useState(10000)
  const [isGenerating, setIsGenerating] = useState(false)

  function handleGenerate() {
    setIsGenerating(true)
    // TODO (Day 2): POST to /api/generate with { prompt, quality, format, style, polyTarget }
    setTimeout(() => setIsGenerating(false), 2000)
  }

  return (
    <div className="create-model-page">
      <div className="create-model-layout">
        {/* ── Left: Prompt + Preview ── */}
        <div className="create-model-main">
          <div className="create-model-header">
            <div>
              <h1 className="page-title">Create 3D Model</h1>
              <p className="page-subtitle">Describe what you want to generate and configure the output settings.</p>
            </div>
            <span className="badge badge-purple">
              <Wand2 size={10} />
              AI Generation
            </span>
          </div>

          {selectedTemplate && (
            <div className="create-config-notice">
              <Info size={12} />
              <span>Template active: <strong>{selectedTemplate.name}</strong> ({selectedTemplate.category})</span>
            </div>
          )}

          <PromptInput onGenerate={handleGenerate} />

          {isGenerating && (
            <div className="create-config-notice">
              <Info size={12} />
              <span>Mock generation queued with {quality} quality ({format}) — real API integration in Day 2.</span>
            </div>
          )}

          <div className="create-preview-area card">
            <EmptyState
              title="3D Preview Canvas"
              description="Your generated model will render here. Rotate, zoom, and inspect every detail of your 3D asset."
            />
          </div>
        </div>

        {/* ── Right: Configuration Panel ── */}
        <aside className="create-config-panel card">
          <div className="create-config-header">
            <Settings2 size={16} />
            <span>Generation Settings</span>
          </div>

          <div className="create-config-notice">
            <Info size={12} />
            <span>Settings are UI-only today. API integration in Day 2.</span>
          </div>

          {/* Quality */}
          <div className="create-config-group">
            <label className="create-config-label">
              <Sliders size={13} />
              Output Quality
            </label>
            <div className="create-option-grid">
              {qualityOptions.map(q => (
                <button
                  key={q}
                  className={`create-option-btn ${quality === q ? 'create-option-active' : ''}`}
                  onClick={() => setQuality(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Export Format */}
          <div className="create-config-group">
            <label className="create-config-label">Export Format</label>
            <div className="create-option-grid">
              {formatOptions.map(f => (
                <button
                  key={f}
                  className={`create-option-btn ${format === f ? 'create-option-active' : ''}`}
                  onClick={() => setFormat(f)}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Style */}
          <div className="create-config-group">
            <label className="create-config-label">Visual Style</label>
            <div className="create-option-grid create-option-grid-col">
              {styleOptions.map(s => (
                <button
                  key={s}
                  className={`create-option-btn create-option-btn-wide ${style === s ? 'create-option-active' : ''}`}
                  onClick={() => setStyle(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Polygon Target */}
          <div className="create-config-group">
            <label className="create-config-label">
              Polygon Target
              <span className="create-poly-value">{polyTarget.toLocaleString()}</span>
            </label>
            <input
              type="range"
              min={1000}
              max={100000}
              step={1000}
              value={polyTarget}
              onChange={e => setPolyTarget(Number(e.target.value))}
              className="create-range-input"
            />
            <div className="create-range-labels">
              <span>1K</span><span>100K</span>
            </div>
          </div>

          {/* Summary */}
          <div className="create-config-summary">
            <div className="create-summary-row">
              <span>Quality</span><strong>{quality}</strong>
            </div>
            <div className="create-summary-row">
              <span>Format</span><strong>{format}</strong>
            </div>
            <div className="create-summary-row">
              <span>Style</span><strong>{style}</strong>
            </div>
            <div className="create-summary-row">
              <span>Polygons</span><strong>{polyTarget.toLocaleString()}</strong>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}

export default CreateModel
