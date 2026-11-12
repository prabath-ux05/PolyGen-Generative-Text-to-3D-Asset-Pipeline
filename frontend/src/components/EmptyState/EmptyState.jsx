import React from 'react'
import { Box, Sparkles, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import './EmptyState.css'

function EmptyState({ title, description, actionLabel, actionPath, icon: Icon = Box }) {
  const navigate = useNavigate()

  return (
    <div className="empty-state">
      <div className="empty-state-visual" aria-hidden="true">
        {/* Animated 3D wireframe grid */}
        <div className="empty-grid-wrapper">
          <div className="empty-grid" />
          <div className="empty-grid-overlay" />
        </div>

        {/* Center icon */}
        <div className="empty-icon-ring">
          <div className="empty-icon-inner">
            <Icon size={36} strokeWidth={1.4} className="empty-icon" />
          </div>
          {/* Orbiting dots */}
          <div className="empty-orbit">
            <span className="empty-orbit-dot empty-orbit-dot-1" />
            <span className="empty-orbit-dot empty-orbit-dot-2" />
            <span className="empty-orbit-dot empty-orbit-dot-3" />
          </div>
        </div>
      </div>

      <div className="empty-state-content">
        <div className="empty-state-badge badge badge-purple">
          <Sparkles size={10} />
          AI-Powered
        </div>
        <h2 className="empty-state-title">
          {title || '3D Preview'}
        </h2>
        <p className="empty-state-desc">
          {description ||
            'Your generated 3D model will appear here. Enter a description above and hit "Generate 3D" to get started.'}
        </p>
        {actionLabel && actionPath && (
          <button
            className="btn btn-primary"
            onClick={() => navigate(actionPath)}
          >
            {actionLabel}
            <ArrowRight size={15} />
          </button>
        )}
      </div>
    </div>
  )
}

export default EmptyState
