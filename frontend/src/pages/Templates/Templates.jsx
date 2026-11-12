import React from 'react'
import { useNavigate } from 'react-router-dom'
import { LayoutTemplate, Users } from 'lucide-react'
import { mockTemplates } from '../../data/mockData.js'
import './Templates.css'

function Templates() {
  const navigate = useNavigate()

  return (
    <div className="templates-page">
      <div className="templates-header">
        <div>
          <h1 className="page-title">Templates</h1>
          <p className="page-subtitle">Start from a pre-configured template to accelerate your generation.</p>
        </div>
      </div>

      <div className="templates-grid">
        {mockTemplates.map(tpl => (
          <div key={tpl.id} className="template-card card card-hover">
            <div className="template-card-top">
              <div className="template-icon-wrap">
                <LayoutTemplate size={20} color="var(--accent-primary)" strokeWidth={1.6} />
              </div>
              <span className="badge badge-purple">{tpl.category}</span>
            </div>
            <h3 className="template-name">{tpl.name}</h3>
            <p className="template-desc">{tpl.description}</p>
            <div className="template-footer">
              <span className="template-uses">
                <Users size={12} />
                {tpl.uses.toLocaleString()} uses
              </span>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => navigate('/create', { state: { template: tpl } })}
              >
                Use Template
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Templates
