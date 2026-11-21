import { useState, useEffect } from 'react'
import {
  User,
  Bell,
  Sliders,
  Palette,
  HelpCircle,
  Save,
  Check,
  Key,
  Copy,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Activity,
  AlertCircle,
  Info,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import { checkBackendHealth } from '../../services/generationService.js'
import './Settings.css'

const settingsTabs = [
  { id: 'profile', label: 'Profile Information', icon: User },
  { id: 'account', label: 'Account & Generation', icon: Sliders },
  { id: 'appearance', label: 'Theme & Viewport', icon: Palette },
  { id: 'notifs', label: 'Notifications', icon: Bell },
  { id: 'help', label: 'Help & Support', icon: HelpCircle },
]

const faqs = [
  {
    q: 'How does PolyGen generate 3D assets from prompts?',
    a: 'PolyGen utilizes generative diffusion models (Shap-E / TripoSR architecture) to synthesize 3D signed distance fields, extract geometry meshes via marching cubes, and bake PBR diffuse textures.',
  },
  {
    q: 'Which 3D export formats are supported?',
    a: 'PolyGen supports Wavefront OBJ and binary GLTF (GLB), both natively loadable in our Three.js viewer, Blender, Unreal Engine, and Unity.',
  },
  {
    q: 'How are settings and assets persisted?',
    a: 'Settings and local asset changes are saved to your browser session storage. When user account services are deployed on the FastAPI backend, cloud database sync will be enabled.',
  },
]

function Settings() {
  const { user, updateProfile } = useAuth()
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState('profile')
  const [savedNotice, setSavedNotice] = useState(false)

  // Profile State
  const [fullName, setFullName] = useState(user?.name || 'Samiksha Patil')
  const [email, setEmail] = useState(user?.email || 'samiksha@polygen.ai')
  const [role, setRole] = useState(user?.role || 'Frontend Developer')
  const [organization, setOrganization] = useState('PolyGen AI Lab')
  const [bio, setBio] = useState('Building interactive 3D WebGL interfaces and generative AI tools.')

  // Account & Generation Preferences State
  const [defaultFormat, setDefaultFormat] = useState('GLB')
  const [defaultQuality, setDefaultQuality] = useState('Standard')
  const [defaultPolyCount, setDefaultPolyCount] = useState(15000)
  const [apiKey, setApiKey] = useState('polygen_sk_live_9809238fae1f48c3b97898f4')
  const [copiedKey, setCopiedKey] = useState(false)

  // Appearance State
  const [themeMode, setThemeMode] = useState('dark')
  const [defaultViewerBg, setDefaultViewerBg] = useState('nebula')
  const [defaultLighting, setDefaultLighting] = useState('default')

  // Notification State
  const [notifComplete, setNotifComplete] = useState(true)
  const [notifFailed, setNotifFailed] = useState(true)
  const [notifSound, setNotifSound] = useState(false)
  const [notifDigest, setNotifDigest] = useState(false)

  // Diagnostics State
  const [healthStatus, setHealthStatus] = useState(null)
  const [checkingHealth, setCheckingHealth] = useState(false)
  const [openFaqIndex, setOpenFaqIndex] = useState(null)

  useEffect(() => {
    if (user) {
      setFullName(user.name || '')
      setEmail(user.email || '')
      setRole(user.role || '')
    }
  }, [user])

  function handleSaveProfile(e) {
    e.preventDefault()
    setSavedNotice(true)
    updateProfile({ name: fullName, email, role })
    showToast({
      title: 'Profile Saved',
      message: 'Account profile details saved in local session.',
      type: 'success',
    })
    setTimeout(() => setSavedNotice(false), 2000)
  }

  function handleSaveAccountSettings(e) {
    e.preventDefault()
    showToast({
      title: 'Generation Preferences Saved',
      message: `Default format set to ${defaultFormat} (${defaultPolyCount.toLocaleString()} target polygons).`,
      type: 'success',
    })
  }

  function handleCopyApiKey() {
    navigator.clipboard.writeText(apiKey)
    setCopiedKey(true)
    showToast({
      title: 'API Key Copied',
      message: 'Key copied to clipboard.',
      type: 'info',
    })
    setTimeout(() => setCopiedKey(false), 2000)
  }

  function handleRegenerateKey() {
    const newKey = 'polygen_sk_live_' + Math.random().toString(36).substring(2, 12) + Math.random().toString(36).substring(2, 12)
    setApiKey(newKey)
    showToast({
      title: 'API Key Rotated',
      message: 'A new local session token has been generated.',
      type: 'warning',
    })
  }

  async function handleCheckBackendHealth() {
    setCheckingHealth(true)
    const result = await checkBackendHealth()
    setCheckingHealth(false)
    setHealthStatus(result)
    if (result.isOnline) {
      showToast({
        title: 'Backend Online',
        message: 'FastAPI server at http://127.0.0.1:8000 is healthy.',
        type: 'success',
      })
    } else {
      showToast({
        title: 'Backend Offline',
        message: result.error || 'Could not connect to FastAPI server.',
        type: 'error',
      })
    }
  }

  return (
    <div className="settings-page">
      {/* ── Header ── */}
      <div className="settings-header">
        <h1 className="page-title">Settings & Preferences</h1>
        <p className="page-subtitle">
          Manage your profile, 3D generation preferences, viewport themes, and system diagnostics.
        </p>
      </div>

      <div className="settings-layout">
        {/* ── Tab Navigation ── */}
        <nav className="settings-tabs card" role="tablist" aria-label="Settings categories">
          {settingsTabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              role="tab"
              aria-selected={activeTab === id}
              className={`settings-tab-btn ${activeTab === id ? 'settings-tab-active' : ''}`}
              onClick={() => setActiveTab(id)}
            >
              <Icon size={16} strokeWidth={1.8} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        {/* ── Panel Content ── */}
        <div className="settings-panel card">
          {/* TAB 1: Profile Information */}
          {activeTab === 'profile' && (
            <div className="settings-section">
              <div className="settings-section-header">
                <div>
                  <h2 className="settings-section-title">Profile Information</h2>
                  <p className="settings-section-desc">Personalize your identity across the PolyGen studio.</p>
                </div>
                <div className="settings-session-badge">
                  <span className="status-dot status-dot-green" />
                  Local Session
                </div>
              </div>

              <div className="settings-avatar-row">
                <div className="settings-avatar-preview">
                  {fullName ? fullName.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase() : 'PG'}
                </div>
                <div className="settings-avatar-info">
                  <div className="settings-avatar-name">{fullName || 'PolyGen Creator'}</div>
                  <div className="settings-avatar-role">{role || '3D Designer'}</div>
                  <span className="badge badge-purple">Pro Plan Tier</span>
                </div>
              </div>

              <form className="settings-form" onSubmit={handleSaveProfile}>
                <div className="settings-form-row">
                  <div className="settings-field">
                    <label htmlFor="settings-name">Full Name</label>
                    <input
                      id="settings-name"
                      className="input"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                    />
                  </div>
                  <div className="settings-field">
                    <label htmlFor="settings-email">Email Address</label>
                    <input
                      id="settings-email"
                      className="input"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="settings-form-row">
                  <div className="settings-field">
                    <label htmlFor="settings-role">Professional Role / Title</label>
                    <input
                      id="settings-role"
                      className="input"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                    />
                  </div>
                  <div className="settings-field">
                    <label htmlFor="settings-org">Organization / Studio</label>
                    <input
                      id="settings-org"
                      className="input"
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                    />
                  </div>
                </div>

                <div className="settings-field">
                  <label htmlFor="settings-bio">Biography / Studio Focus</label>
                  <textarea
                    id="settings-bio"
                    className="textarea"
                    rows={3}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                  />
                </div>

                <div className="settings-support-notice">
                  <Info size={14} className="text-muted" />
                  <div>
                    <strong>Session Persistence Notice</strong>
                    <p>Profile details are preserved in your browser session. Cloud user syncing will activate when backend auth services are deployed.</p>
                  </div>
                </div>

                <div className="settings-actions">
                  <button type="submit" className="btn btn-primary">
                    {savedNotice ? <Check size={14} /> : <Save size={14} />}
                    {savedNotice ? 'Saved!' : 'Save Profile'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                      setFullName(user?.name || '')
                      setEmail(user?.email || '')
                      setRole(user?.role || '')
                    }}
                  >
                    Reset
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* TAB 2: Account & Generation Settings */}
          {activeTab === 'account' && (
            <div className="settings-section">
              <div className="settings-section-header">
                <div>
                  <h2 className="settings-section-title">Generation Preferences & API</h2>
                  <p className="settings-section-desc">Configure default 3D synthesis formats, polygon targets, and developer tokens.</p>
                </div>
              </div>

              <form className="settings-form" onSubmit={handleSaveAccountSettings}>
                {/* Default 3D Format */}
                <div className="settings-field">
                  <label>Default Output Format</label>
                  <div className="settings-pill-selector">
                    {['GLB', 'OBJ', 'FBX', 'STL'].map((fmt) => (
                      <button
                        key={fmt}
                        type="button"
                        className={`pill-option-btn ${defaultFormat === fmt ? 'pill-option-active' : ''}`}
                        onClick={() => setDefaultFormat(fmt)}
                      >
                        {fmt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Default Quality */}
                <div className="settings-field">
                  <label>Default Synthesis Quality</label>
                  <div className="settings-pill-selector">
                    {['Draft', 'Standard', 'High', 'Ultra'].map((q) => (
                      <button
                        key={q}
                        type="button"
                        className={`pill-option-btn ${defaultQuality === q ? 'pill-option-active' : ''}`}
                        onClick={() => setDefaultQuality(q)}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Target Polygons Slider */}
                <div className="settings-field">
                  <div className="slider-label-row">
                    <label htmlFor="settings-poly-slider">Default Polygon Target</label>
                    <span className="slider-value-badge">{defaultPolyCount.toLocaleString()} polygons</span>
                  </div>
                  <input
                    id="settings-poly-slider"
                    type="range"
                    min={1000}
                    max={80000}
                    step={1000}
                    value={defaultPolyCount}
                    onChange={(e) => setDefaultPolyCount(Number(e.target.value))}
                    className="range-input"
                  />
                  <div className="slider-limits">
                    <span>1K (Low-Poly)</span>
                    <span>80K (Production Asset)</span>
                  </div>
                </div>

                <div className="settings-divider" />

                {/* API Key Management */}
                <div className="settings-field">
                  <label>Developer API Token (Personal Access Key)</label>
                  <div className="api-key-box">
                    <Key size={15} className="text-accent" />
                    <code className="api-key-code">{apiKey}</code>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={handleCopyApiKey}
                    >
                      {copiedKey ? <Check size={13} className="text-green" /> : <Copy size={13} />}
                      {copiedKey ? 'Copied' : 'Copy'}
                    </button>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={handleRegenerateKey}
                    >
                      Rotate Key
                    </button>
                  </div>
                  <p className="field-hint">
                    Use this Bearer token in the <code>Authorization</code> header when connecting directly to <code>http://127.0.0.1:8000/api/v1/</code>.
                  </p>
                </div>

                <div className="settings-actions">
                  <button type="submit" className="btn btn-primary">
                    <Save size={14} />
                    Save Generation Preferences
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* TAB 3: Theme & Viewport Appearance */}
          {activeTab === 'appearance' && (
            <div className="settings-section">
              <div className="settings-section-header">
                <div>
                  <h2 className="settings-section-title">Theme & 3D Viewport Appearance</h2>
                  <p className="settings-section-desc">Customize UI color palettes, lighting presets, and canvas backgrounds.</p>
                </div>
              </div>

              {/* Theme Mode */}
              <div className="settings-field">
                <label>Dashboard Interface Theme</label>
                <div className="theme-options-grid">
                  <div
                    className={`theme-card ${themeMode === 'dark' ? 'theme-card-selected' : ''}`}
                    onClick={() => setThemeMode('dark')}
                  >
                    <div className="theme-preview-box theme-dark-preview">
                      <div className="preview-nav" />
                      <div className="preview-content">
                        <div className="preview-card" />
                      </div>
                    </div>
                    <div className="theme-card-label">
                      <strong>Dark Charcoal (Default)</strong>
                      <span>Deep navy SaaS aesthetic</span>
                    </div>
                  </div>

                  <div
                    className={`theme-card ${themeMode === 'slate' ? 'theme-card-selected' : ''}`}
                    onClick={() => setThemeMode('slate')}
                  >
                    <div className="theme-preview-box theme-slate-preview">
                      <div className="preview-nav" />
                      <div className="preview-content">
                        <div className="preview-card" />
                      </div>
                    </div>
                    <div className="theme-card-label">
                      <strong>Studio Slate</strong>
                      <span>Neutral studio gray palette</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Viewport Default Background */}
              <div className="settings-field">
                <label>Default 3D Viewport Background</label>
                <div className="settings-pill-selector">
                  {[
                    { id: 'nebula', label: 'Dark Nebula' },
                    { id: 'studio', label: 'Studio Slate' },
                    { id: 'black', label: 'Pitch Black' },
                    { id: 'cyber', label: 'Cyber Grid' },
                  ].map((bg) => (
                    <button
                      key={bg.id}
                      type="button"
                      className={`pill-option-btn ${defaultViewerBg === bg.id ? 'pill-option-active' : ''}`}
                      onClick={() => {
                        setDefaultViewerBg(bg.id)
                        showToast({
                          title: 'Viewport Background Set',
                          message: `Default background changed to ${bg.label}.`,
                          type: 'info',
                        })
                      }}
                    >
                      {bg.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Viewport Default Lighting */}
              <div className="settings-field">
                <label>Default Studio Lighting</label>
                <div className="settings-pill-selector">
                  {[
                    { id: 'default', label: 'Default Balanced' },
                    { id: 'studio', label: 'Studio Dramatic' },
                    { id: 'soft', label: 'Soft Diffused' },
                  ].map((l) => (
                    <button
                      key={l.id}
                      type="button"
                      className={`pill-option-btn ${defaultLighting === l.id ? 'pill-option-active' : ''}`}
                      onClick={() => {
                        setDefaultLighting(l.id)
                        showToast({
                          title: 'Lighting Preset Set',
                          message: `Default lighting set to ${l.label}.`,
                          type: 'info',
                        })
                      }}
                    >
                      {l.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Notifications */}
          {activeTab === 'notifs' && (
            <div className="settings-section">
              <div className="settings-section-header">
                <div>
                  <h2 className="settings-section-title">Notification Preferences</h2>
                  <p className="settings-section-desc">Choose which pipeline events trigger desktop alerts and toasts.</p>
                </div>
              </div>

              <div className="settings-toggle-list">
                <div className="settings-toggle-item">
                  <div>
                    <p className="settings-toggle-label">Generation Completed Alert</p>
                    <p className="settings-toggle-desc">Show a high-priority toast when 3D synthesis completes.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notifComplete}
                      onChange={(e) => setNotifComplete(e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>

                <div className="settings-toggle-item">
                  <div>
                    <p className="settings-toggle-label">Generation Failure Notification</p>
                    <p className="settings-toggle-desc">Alert when a generation job encounters an error or timeout.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notifFailed}
                      onChange={(e) => setNotifFailed(e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>

                <div className="settings-toggle-item">
                  <div>
                    <p className="settings-toggle-label">Audio Chime on Completion</p>
                    <p className="settings-toggle-desc">Play a subtle audio notification when the 3D model loads into the viewport.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notifSound}
                      onChange={(e) => setNotifSound(e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>

                <div className="settings-toggle-item">
                  <div>
                    <p className="settings-toggle-label">Weekly Activity Digest</p>
                    <p className="settings-toggle-desc">Receive a summary of models generated, poly counts, and quota usage.</p>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={notifDigest}
                      onChange={(e) => setNotifDigest(e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: Help & Support */}
          {activeTab === 'help' && (
            <div className="settings-section">
              <div className="settings-section-header">
                <div>
                  <h2 className="settings-section-title">Help, Support & Diagnostics</h2>
                  <p className="settings-section-desc">System health checks, documentation resources, and FAQs.</p>
                </div>
              </div>

              {/* System Diagnostics Box */}
              <div className="diagnostics-card">
                <div className="diagnostics-header">
                  <div className="diagnostics-title-row">
                    <Activity size={16} className="text-accent" />
                    <strong>System Diagnostics & Backend Probe</strong>
                  </div>
                  <button
                    type="button"
                    className="btn btn-secondary btn-xs"
                    onClick={handleCheckBackendHealth}
                    disabled={checkingHealth}
                  >
                    {checkingHealth ? 'Pinging…' : 'Check FastAPI Health'}
                  </button>
                </div>

                <div className="diagnostics-grid">
                  <div className="diag-item">
                    <span className="diag-label">WebGL 2.0 Engine</span>
                    <span className="diag-val text-green">Hardware Accelerated</span>
                  </div>
                  <div className="diag-item">
                    <span className="diag-label">Three.js Version</span>
                    <span className="diag-val font-mono">r187 / R3F v8.18</span>
                  </div>
                  <div className="diag-item">
                    <span className="diag-label">FastAPI Endpoint</span>
                    <span className="diag-val font-mono">http://127.0.0.1:8000</span>
                  </div>
                  <div className="diag-item">
                    <span className="diag-label">Backend Connection</span>
                    <span className={`diag-val ${healthStatus?.isOnline ? 'text-green' : 'text-yellow'}`}>
                      {healthStatus ? (healthStatus.isOnline ? 'Online (200 OK)' : 'Offline / Mock Mode') : 'Ready to Probe'}
                    </span>
                  </div>
                </div>
              </div>

              {/* FAQ Accordion */}
              <div className="settings-faq-section">
                <h3 className="settings-subtitle">Frequently Asked Questions</h3>
                <div className="faq-accordion-list">
                  {faqs.map((f, idx) => {
                    const isOpen = openFaqIndex === idx
                    return (
                      <div key={idx} className="faq-accordion-item">
                        <button
                          type="button"
                          className="faq-accordion-trigger"
                          onClick={() => setOpenFaqIndex(isOpen ? null : idx)}
                          aria-expanded={isOpen}
                        >
                          <span>{f.q}</span>
                          {isOpen ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                        </button>
                        {isOpen && <div className="faq-accordion-body">{f.a}</div>}
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Contact Support */}
              <div className="support-banner">
                <AlertCircle size={16} className="text-accent" />
                <div className="support-banner-content">
                  <strong>Need technical assistance?</strong>
                  <p>Check the full documentation or reach out to the PolyGen engineering team.</p>
                </div>
                <a
                  href="https://github.com/prabath-ux05/PolyGen-Generative-Text-to-3D-Asset-Pipeline"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary btn-sm"
                >
                  <ExternalLink size={13} />
                  GitHub Repository
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Settings
