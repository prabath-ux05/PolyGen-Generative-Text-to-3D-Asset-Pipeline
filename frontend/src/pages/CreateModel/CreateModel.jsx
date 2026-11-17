import { useState, useRef, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Wand2, Settings2, Sliders, Info } from 'lucide-react'
import PromptInput from '../../components/PromptInput/PromptInput.jsx'
import ModelViewer from '../../components/ModelViewer/ModelViewer.jsx'
import GenerationStatusPanel from '../../components/GenerationStatus/GenerationStatusPanel.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import {
  submitGeneration,
  simulateMockGeneration,
  ServiceUnavailableError,
  ValidationError,
  NetworkError,
} from '../../services/generationService.js'
import './CreateModel.css'

const qualityOptions = ['Draft', 'Standard', 'High', 'Ultra']
const formatOptions  = ['GLB', 'OBJ', 'FBX', 'STL']
const styleOptions   = ['Realistic', 'Stylized', 'Low Poly', 'Sci-Fi', 'Fantasy']

function CreateModel() {
  const location = useLocation()
  const { showToast } = useToast()
  const selectedTemplate = location.state?.template || null
  const passedAsset = location.state?.asset || null

  const [quality, setQuality]   = useState('Standard')
  const [format, setFormat]     = useState('OBJ')
  const [style, setStyle]       = useState('Realistic')
  const [polyTarget, setPolyTarget] = useState(10000)
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentJob, setCurrentJob] = useState(null)
  const abortControllerRef = useRef(null)

  const [activeModelUrl, setActiveModelUrl] = useState(() => {
    if (passedAsset?.name?.toLowerCase().includes('chair')) return '/models/sample-chair.obj'
    return '/models/sample-crystal.obj'
  })

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  async function handleGenerate(promptText, outputFormat) {
    const targetFormat = (outputFormat || format || 'glb').toLowerCase()
    setIsGenerating(true)

    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    const controller = new AbortController()
    abortControllerRef.current = controller

    const initialJob = {
      job_id: null,
      prompt: promptText,
      output_format: targetFormat,
      status: 'submitted',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      error_message: null,
      is_mock: false,
    }
    setCurrentJob(initialJob)

    showToast({
      title: 'Submitting Generation Task',
      message: `POST /api/v1/generations (${targetFormat.toUpperCase()})`,
      type: 'info',
    })

    try {
      const response = await submitGeneration({
        prompt: promptText,
        outputFormat: targetFormat,
        signal: controller.signal,
      })

      setIsGenerating(false)
      const jobResponse = {
        job_id: response.job_id || 'live-job-' + Date.now(),
        prompt: response.prompt || promptText,
        output_format: response.output_format || targetFormat,
        status: response.status || 'pending',
        created_at: response.created_at || new Date().toISOString(),
        updated_at: response.updated_at || new Date().toISOString(),
        error_message: response.error_message || null,
        is_mock: false,
      }
      setCurrentJob(jobResponse)
      showToast({
        title: 'Backend Job Dispatched',
        message: `Task ID: ${jobResponse.job_id}`,
        type: 'success',
      })
    } catch (err) {
      setIsGenerating(false)
      if (err.name === 'AbortError') return

      if (err instanceof ServiceUnavailableError || err.status === 503) {
        setCurrentJob({
          job_id: 'FastAPI (HTTP 503)',
          prompt: promptText,
          output_format: targetFormat,
          status: 'unavailable',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Backend Engine Notice (503)',
          message: 'Text-to-3D generation engine is not yet integrated.',
          type: 'warning',
          duration: 6000,
        })
      } else if (err instanceof ValidationError) {
        setCurrentJob({
          job_id: 'Validation Error (HTTP 422)',
          prompt: promptText,
          output_format: targetFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Request Validation Error',
          message: err.message,
          type: 'error',
        })
      } else if (err instanceof NetworkError) {
        setCurrentJob({
          job_id: 'Network Error',
          prompt: promptText,
          output_format: targetFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Backend Offline',
          message: 'Unable to connect to FastAPI at http://127.0.0.1:8000.',
          type: 'error',
          duration: 6000,
        })
      } else {
        setCurrentJob({
          job_id: 'Error',
          prompt: promptText,
          output_format: targetFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message || 'Error communicating with backend.',
          is_mock: false,
        })
        showToast({
          title: 'Generation Error',
          message: err.message || 'An error occurred.',
          type: 'error',
        })
      }
    }
  }

  function handleSimulateDemo() {
    if (!currentJob?.prompt) return
    setIsGenerating(true)
    showToast({
      title: 'Starting Pipeline Simulation',
      message: 'Running mock generation lifecycle (pending → processing → completed)…',
      type: 'info',
    })

    simulateMockGeneration({
      prompt: currentJob.prompt,
      outputFormat: currentJob.output_format || 'glb',
      onStatusChange: (updatedJob) => {
        setCurrentJob(updatedJob)
        if (updatedJob.status === 'completed') {
          setIsGenerating(false)
          setActiveModelUrl(updatedJob.model_url)
          showToast({
            title: '3D Asset Synthesized (Demo Mode)',
            message: 'Model loaded into the studio 3D viewer.',
            type: 'success',
          })
        }
      },
    }).catch((err) => {
      setIsGenerating(false)
      showToast({ title: 'Simulation Error', message: err.message, type: 'error' })
    })
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

          <PromptInput onGenerate={handleGenerate} isProcessing={isGenerating} defaultFormat={format} />

          {currentJob && (
            <GenerationStatusPanel
              job={currentJob}
              onDismiss={() => setCurrentJob(null)}
              onViewIn3D={(url) => {
                if (url) setActiveModelUrl(url)
              }}
              onSimulatePipeline={handleSimulateDemo}
              onRetry={() => handleGenerate(currentJob.prompt, currentJob.output_format)}
            />
          )}

          <div className="create-preview-area" style={{ height: '480px', marginTop: '16px' }}>
            <ModelViewer modelUrl={activeModelUrl} height="480px" />
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
