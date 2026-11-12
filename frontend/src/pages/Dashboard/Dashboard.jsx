import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Zap, Info } from 'lucide-react'
import StatsCard from '../../components/StatsCard/StatsCard.jsx'
import PromptInput from '../../components/PromptInput/PromptInput.jsx'
import RecentAssets from '../../components/RecentAssets/RecentAssets.jsx'
import EmptyState from '../../components/EmptyState/EmptyState.jsx'
import { mockStats } from '../../data/mockData.js'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  const [lastPrompt, setLastPrompt] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)

  function handleGenerate(prompt) {
    setIsGenerating(true)
    setLastPrompt(prompt)
    // TODO (Day 2): POST to /api/generate with { prompt }
    setTimeout(() => setIsGenerating(false), 2000)
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
            Describe any object, scene, or character in natural language and PolyGen's
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
        <PromptInput onGenerate={handleGenerate} />

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
          <h2 className="section-title">3D Preview</h2>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/create')}>
            Open Full Viewer
            <ArrowRight size={13} />
          </button>
        </div>
        <div className="dashboard-preview-area card">
          <EmptyState
            title="No Model Generated Yet"
            description="Your generated 3D model will appear here. Enter a description above and click 'Generate 3D' to create your first asset."
          />
        </div>
      </section>

      {/* ── Recent Assets ── */}
      <section className="dashboard-section">
        <RecentAssets limit={6} />
      </section>
    </div>
  )
}

export default Dashboard
