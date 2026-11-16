import { useState, useEffect } from 'react'
import { User, Bell, Shield, Palette, Save, Check } from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import './Settings.css'

const settingsTabs = [
  { id: 'profile',  label: 'Profile',       icon: User },
  { id: 'notifs',   label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Security',      icon: Shield },
  { id: 'appearance', label: 'Appearance',  icon: Palette },
]

function Settings() {
  const { user, updateProfile } = useAuth()
  const { showToast } = useToast()
  const [activeTab, setActiveTab] = useState('profile')
  const [savedNotice, setSavedNotice] = useState(false)

  const [fullName, setFullName] = useState(user?.name || 'Samiksha Patil')
  const [email, setEmail] = useState(user?.email || 'samiksha@polygen.ai')
  const [role, setRole] = useState(user?.role || 'Frontend Developer')

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
      title: 'Profile Updated',
      message: 'Account profile details saved in local session.',
      type: 'success',
    })
    setTimeout(() => setSavedNotice(false), 2000)
  }

  function handlePasswordUpdate(e) {
    e.preventDefault()
    showToast({
      title: 'Password Updated',
      message: 'Password simulated update complete (Demo Mode).',
      type: 'success',
    })
  }

  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account, preferences, and application settings.</p>
      </div>

      <div className="settings-layout">
        {/* Tab Nav */}
        <nav className="settings-tabs">
          {settingsTabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              className={`settings-tab-btn ${activeTab === id ? 'settings-tab-active' : ''}`}
              onClick={() => setActiveTab(id)}
            >
              <Icon size={15} strokeWidth={1.8} />
              {label}
            </button>
          ))}
        </nav>

        {/* Panel */}
        <div className="settings-panel card">
          {activeTab === 'profile' && (
            <div className="settings-section">
              <h2 className="settings-section-title">Profile Information</h2>
              <form className="settings-form" onSubmit={handleSaveProfile}>
                <div className="settings-field">
                  <label htmlFor="settings-name">Full Name</label>
                  <input
                    id="settings-name"
                    className="input"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
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
                  />
                </div>
                <div className="settings-field">
                  <label htmlFor="settings-role">Role / Title</label>
                  <input
                    id="settings-role"
                    className="input"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  />
                </div>
                <div className="settings-actions">
                  <button type="submit" className="btn btn-primary">
                    {savedNotice ? <Check size={14} /> : <Save size={14} />}
                    {savedNotice ? 'Saved!' : 'Save Changes'}
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost"
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

          {activeTab === 'notifs' && (
            <div className="settings-section">
              <h2 className="settings-section-title">Notification Preferences</h2>
              <div className="settings-toggle-list">
                {[
                  ['Generation Complete', 'Notify when a 3D model finishes generating'],
                  ['Generation Failed', 'Notify when a generation job encounters an error'],
                  ['Weekly Summary', 'Receive a weekly digest of your activity'],
                  ['Product Updates', 'News about PolyGen features and improvements'],
                ].map(([label, desc]) => (
                  <div key={label} className="settings-toggle-item">
                    <div>
                      <p className="settings-toggle-label">{label}</p>
                      <p className="settings-toggle-desc">{desc}</p>
                    </div>
                    <label className="toggle-switch">
                      <input type="checkbox" defaultChecked />
                      <span className="toggle-slider" />
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="settings-section">
              <h2 className="settings-section-title">Security</h2>
              <form className="settings-form" onSubmit={handlePasswordUpdate}>
                <div className="settings-field">
                  <label htmlFor="settings-curr-pwd">Current Password</label>
                  <input id="settings-curr-pwd" className="input" type="password" placeholder="••••••••" required />
                </div>
                <div className="settings-field">
                  <label htmlFor="settings-new-pwd">New Password</label>
                  <input id="settings-new-pwd" className="input" type="password" placeholder="••••••••" required />
                </div>
                <div className="settings-field">
                  <label htmlFor="settings-conf-pwd">Confirm New Password</label>
                  <input id="settings-conf-pwd" className="input" type="password" placeholder="••••••••" required />
                </div>
                <div className="settings-actions">
                  <button type="submit" className="btn btn-primary">Update Password</button>
                </div>
              </form>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="settings-section">
              <h2 className="settings-section-title">Appearance</h2>
              <p className="settings-appearance-note">Theme customization coming in a future update.</p>
              <div className="settings-theme-preview">
                <div className="theme-swatch theme-swatch-current">
                  <span />
                  Dark (Current)
                </div>
                <div className="theme-swatch theme-swatch-disabled">
                  <span />
                  Light (Soon)
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Settings
