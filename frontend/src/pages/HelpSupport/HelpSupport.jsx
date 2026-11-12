import React, { useState } from 'react'
import { MessageCircle, BookOpen, Mail, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import './HelpSupport.css'

const faqs = [
  {
    q: 'How long does 3D generation take?',
    a: 'Generation time depends on complexity and quality settings. Draft quality typically completes in 30–60 seconds, while Ultra quality may take 3–5 minutes.',
  },
  {
    q: 'What 3D file formats are supported?',
    a: 'PolyGen supports GLB, OBJ, FBX, and STL export formats. GLB is recommended for web viewers and game engines.',
  },
  {
    q: 'Can I use generated assets commercially?',
    a: 'Yes. All assets generated with a Pro plan are royalty-free and can be used in commercial projects.',
  },
  {
    q: 'How do I improve generation quality?',
    a: 'Use detailed, descriptive prompts. Specify material, style, lighting conditions, and scale. Use the Ultra quality setting for production work.',
  },
  {
    q: 'Is there a polygon limit?',
    a: 'The polygon target slider allows you to control output complexity from 1K to 100K polygons. Higher counts produce more detailed meshes.',
  },
]

function FAQItem({ q, a }) {
  const [open, setOpen] = useState(false)
  return (
    <div className={`faq-item ${open ? 'faq-open' : ''}`}>
      <button className="faq-question" onClick={() => setOpen(v => !v)}>
        <span>{q}</span>
        {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      {open && <div className="faq-answer">{a}</div>}
    </div>
  )
}

function HelpSupport() {
  return (
    <div className="help-page">
      <div className="help-header">
        <h1 className="page-title">Help & Support</h1>
        <p className="page-subtitle">Find answers, documentation, and contact our support team.</p>
      </div>

      <div className="help-cards-row">
        {[
          { icon: BookOpen,      title: 'Documentation',    desc: 'Read the full PolyGen API and pipeline docs.',  action: 'Open Docs',    color: 'purple' },
          { icon: MessageCircle, title: 'Live Chat',        desc: 'Chat with the support team in real time.',       action: 'Start Chat',   color: 'blue' },
          { icon: Mail,          title: 'Email Support',    desc: 'Send us a message and we\'ll reply within 24h.', action: 'Send Email',   color: 'green' },
        ].map(({ icon: Icon, title, desc, action, color }) => (
          <div key={title} className="help-card card card-hover">
            <div className={`help-card-icon help-icon-${color}`}>
              <Icon size={22} strokeWidth={1.6} />
            </div>
            <h3 className="help-card-title">{title}</h3>
            <p className="help-card-desc">{desc}</p>
            <button className="btn btn-secondary btn-sm help-card-btn">
              {action}
              <ExternalLink size={12} />
            </button>
          </div>
        ))}
      </div>

      <div className="help-faq">
        <h2 className="section-title">Frequently Asked Questions</h2>
        <div className="faq-list">
          {faqs.map(item => (
            <FAQItem key={item.q} {...item} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default HelpSupport
