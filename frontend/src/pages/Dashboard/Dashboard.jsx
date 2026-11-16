import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Zap, Info } from 'lucide-react'
import StatsCard from '../../components/StatsCard/StatsCard.jsx'
import PromptInput from '../../components/PromptInput/PromptInput.jsx'
import RecentAssets from '../../components/RecentAssets/RecentAssets.jsx'
import ModelViewer from '../../components/ModelViewer/ModelViewer.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import { mockStats } from '../../data/mockData.js'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [lastPrompt, setLastPrompt] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeModelUrl, setActiveModelUrl] = useState('/models/sample-crystal.obj')

  function handleGenerate(prompt) {
    setIsGenerating(true)
    setLastPrompt(prompt)

    showToast({
      title: 'Prompt Submitted',
      message: `Queued generation for: "${prompt.length > 50 ? prompt.slice(0, 50) + '…' : prompt}"`,
      type: 'info',
    })

    // Simulated pipeline submission
    setTimeout(() => {
      setIsGenerating(false)
      setActiveModelUrl('/models/sample-crystal.obj')
      showToast({
        title: '3D Asset Synthesized',
        message: 'Pipeline output rendered in the interactive 3D viewer.',
        type: 'success',
      })
    }, 2200)
  }

  function handleAssetPreview(asset) {
    // Choose sample model based on asset or format
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

      {/* ── Prompt Input ── */}
      <section className="dashboard-section">
        <PromptInput onGenerate={handleGenerate} isProcessing={isGenerating} />

        {/* Generation Status */}
        {isGenerating && (
          <div className="dashboard-generating-notice">
            <div className="dash-spinner" />
            <span>Submitting your prompt to the generation pipeline…</span>
            <span className="dashboard-mock-label">
              <Info size={12} />
              Mock – real API not yet connected
            </span>
          </div>
        )}

        {lastPrompt && !isGenerating && (
          <div className="dashboard-prompt-echo">
            <span>Last prompt:</span>
            <q>{lastPrompt}</q>
          </div>
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
      <section className="dashboard-section">
        <div className="dashboard-section-header">
          <h2 className="section-title">Interactive 3D Viewer</h2>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/create')}>
            Open Full Studio
            <ArrowRight size={13} />
          </button>
        </div>
        <div className="dashboard-preview-area" style={{ height: '500px' }}>
          <ModelViewer modelUrl={activeModelUrl} height="500px" />
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
