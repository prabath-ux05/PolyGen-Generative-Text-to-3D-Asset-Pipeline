import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Zap, Info } from 'lucide-react'
import StatsCard from '../../components/StatsCard/StatsCard.jsx'
import PromptInput from '../../components/PromptInput/PromptInput.jsx'
import RecentAssets from '../../components/RecentAssets/RecentAssets.jsx'
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
import { mockStats } from '../../data/mockData.js'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeModelUrl, setActiveModelUrl] = useState('/models/sample-crystal.obj')
  const [currentJob, setCurrentJob] = useState(null)
  const abortControllerRef = useRef(null)

  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  async function handleGenerate(promptText, outputFormat = 'glb') {
    setIsGenerating(true)

    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    const controller = new AbortController()
    abortControllerRef.current = controller

    const initialJob = {
      job_id: null,
      prompt: promptText,
      output_format: outputFormat,
      status: 'submitted',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      error_message: null,
      is_mock: false,
    }
    setCurrentJob(initialJob)

    showToast({
      title: 'Submitting to Backend',
      message: `POST /api/v1/generations (${outputFormat.toUpperCase()})`,
      type: 'info',
    })

    try {
      const response = await submitGeneration({
        prompt: promptText,
        outputFormat,
        signal: controller.signal,
      })

      // In future when backend completes generation job
      setIsGenerating(false)
      const jobResponse = {
        job_id: response.job_id || 'live-job-' + Date.now(),
        prompt: response.prompt || promptText,
        output_format: response.output_format || outputFormat,
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
        // Backend HTTP 503 Engine Not Integrated
        setCurrentJob({
          job_id: 'FastAPI (HTTP 503)',
          prompt: promptText,
          output_format: outputFormat,
          status: 'unavailable',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Backend Service Notice (503)',
          message: 'Text-to-3D generation engine is not yet integrated.',
          type: 'warning',
          duration: 6000,
        })
      } else if (err instanceof ValidationError) {
        setCurrentJob({
          job_id: 'Validation Error (HTTP 422)',
          prompt: promptText,
          output_format: outputFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Request Validation Failed',
          message: err.message,
          type: 'error',
        })
      } else if (err instanceof NetworkError) {
        setCurrentJob({
          job_id: 'Connection Failed',
          prompt: promptText,
          output_format: outputFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message,
          is_mock: false,
        })
        showToast({
          title: 'Backend Offline',
          message: 'Unable to reach FastAPI backend at http://127.0.0.1:8000.',
          type: 'error',
          duration: 6000,
        })
      } else {
        setCurrentJob({
          job_id: 'API Error',
          prompt: promptText,
          output_format: outputFormat,
          status: 'failed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          error_message: err.message || 'An unexpected error occurred.',
          is_mock: false,
        })
        showToast({
          title: 'Generation Error',
          message: err.message || 'Error communicating with backend.',
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
            message: 'Model loaded into the interactive 3D viewer.',
            type: 'success',
          })
        }
      },
    }).catch((err) => {
      setIsGenerating(false)
      showToast({ title: 'Simulation Error', message: err.message, type: 'error' })
    })
  }

  function handleAssetPreview(asset) {
    const url = asset?.name?.toLowerCase().includes('chair')
      ? '/models/sample-chair.obj'
      : '/models/sample-crystal.obj'
    setActiveModelUrl(url)
    showToast({
      title: `Previewing ${asset.name}`,
      message: 'Loaded into interactive 3D viewer.',
      type: 'info',
    })
  }

  return (
    <div className="dashboard">
      {/* ── Hero Header ── */}
      <section className="dashboard-hero">
        <div className="dashboard-hero-content">
          <div className="dashboard-hero-badge badge badge-purple">
            <Zap size={11} />
            AI-Powered Generation
          </div>
          <h1 className="dashboard-hero-title">
            Create Anything in <span className="gradient-text">3D</span>
          </h1>
          <p className="dashboard-hero-desc">
            Describe any object, scene, or character in natural language and PolyGen&apos;s
            AI pipeline will generate a production-ready 3D asset with geometry,
            textures, and clean topology — in seconds.
          </p>
        </div>
        <div className="dashboard-hero-visual" aria-hidden="true">
          <div className="hero-bg-orb hero-orb-1" />
          <div className="hero-bg-orb hero-orb-2" />
        </div>
      </section>

      {/* ── Prompt Input & Status ── */}
      <section className="dashboard-section">
        <PromptInput onGenerate={handleGenerate} isProcessing={isGenerating} />

        {/* Generation Status Panel (Day 4 Integration) */}
        {currentJob && (
          <GenerationStatusPanel
            job={currentJob}
            onDismiss={() => setCurrentJob(null)}
            onViewIn3D={(url) => {
              if (url) setActiveModelUrl(url)
              document.getElementById('dashboard-viewer-section')?.scrollIntoView({ behavior: 'smooth' })
            }}
            onSimulatePipeline={handleSimulateDemo}
            onRetry={() => handleGenerate(currentJob.prompt, currentJob.output_format)}
          />
        )}
      </section>

      {/* ── Stats ── */}
      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <h2 className="section-title">Overview</h2>
          <span className="dashboard-mock-tag">
            <Info size={11} />
            Sample data
          </span>
        </div>
        <div className="dashboard-stats-grid">
          {mockStats.map(stat => (
            <StatsCard key={stat.id} {...stat} />
          ))}
        </div>
      </section>

      {/* ── 3D Preview Area ── */}
      <section className="dashboard-section" id="dashboard-viewer-section">
        <div className="dashboard-section-header">
          <h2 className="section-title">Interactive 3D Viewer</h2>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/create')}>
            Open Full Studio
            <ArrowRight size={13} />
          </button>
        </div>
        <div className="dashboard-preview-area" style={{ height: '500px' }}>
          <ModelViewer
            modelUrl={activeModelUrl}
            generationId={currentJob?.job_id || 'sample-model-preview'}
            assetName={currentJob?.prompt ? currentJob.prompt.slice(0, 24) : 'Sample Crystal'}
            height="500px"
          />
        </div>
      </section>

      {/* ── Recent Assets ── */}
      <section className="dashboard-section">
        <RecentAssets limit={6} onPreview={handleAssetPreview} />
      </section>
    </div>
  )
}

export default Dashboard
