import React, { useState } from 'react'
import { User, Bell, Shield, Palette, Save, Check } from 'lucide-react'
import './Settings.css'

const settingsTabs = [
  { id: 'profile',  label: 'Profile',       icon: User },
  { id: 'notifs',   label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Security',      icon: Shield },
  { id: 'appearance', label: 'Appearance',  icon: Palette },
]

function Settings() {
  const [activeTab, setActiveTab] = useState('profile')
  const [savedNotice, setSavedNotice] = useState(false)

  function handleSave() {
    setSavedNotice(true)
    setTimeout(() => setSavedNotice(false), 2000)
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
              <div className="settings-form">
                <div className="settings-field">
                  <label>Full Name</label>
                  <input className="input" defaultValue="Samiksha Patil" />
                </div>
                <div className="settings-field">
                  <label>Email Address</label>
                  <input className="input" type="email" defaultValue="samiksha@polygen.ai" />
                </div>
                <div className="settings-field">
                  <label>Username</label>
                  <input className="input" defaultValue="samiksha_patil" />
                </div>
                <div className="settings-field">
                  <label>Role / Title</label>
                  <input className="input" defaultValue="Frontend Developer" />
                </div>
              </div>
              <div className="settings-actions">
                <button className="btn btn-primary" onClick={handleSave}>
                  {savedNotice ? <Check size={14} /> : <Save size={14} />}
                  {savedNotice ? 'Saved!' : 'Save Changes'}
                </button>
                <button className="btn btn-ghost">Cancel</button>
              </div>
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
              <div className="settings-form">
                <div className="settings-field">
                  <label>Current Password</label>
                  <input className="input" type="password" placeholder="••••••••" />
                </div>
                <div className="settings-field">
                  <label>New Password</label>
                  <input className="input" type="password" placeholder="••••••••" />
                </div>
                <div className="settings-field">
                  <label>Confirm New Password</label>
                  <input className="input" type="password" placeholder="••••••••" />
                </div>
              </div>
              <div className="settings-actions">
                <button className="btn btn-primary">Update Password</button>
              </div>
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
