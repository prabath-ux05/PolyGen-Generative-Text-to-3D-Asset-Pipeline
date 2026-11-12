import React, { useState, useRef, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import {
  Search,
  Bell,
  Menu,
  ChevronDown,
  LogIn,
  UserPlus,
  User,
  Settings,
  LogOut,
  Sparkles,
} from 'lucide-react'
import './Navbar.css'

function Navbar({ pageTitles, onMenuToggle }) {
  const location = useLocation()
  const navigate = useNavigate()
  const [searchValue, setSearchValue] = useState('')
  const [profileOpen, setProfileOpen] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(true)
  const [unreadCount, setUnreadCount] = useState(3)
  const profileRef = useRef(null)
  const notifRef = useRef(null)
  const searchInputRef = useRef(null)

  const pageTitle = pageTitles[location.pathname] || 'Dashboard'

  // Close dropdowns on outside click & handle Cmd/Ctrl+K shortcut
  useEffect(() => {
    function handleClickOutside(e) {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false)
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotificationsOpen(false)
      }
    }
    function handleKeyDown(e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        searchInputRef.current?.focus()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [])

  function handleSearchKeyDown(e) {
    if (e.key === 'Enter' && searchValue.trim()) {
      navigate(`/assets?q=${encodeURIComponent(searchValue.trim())}`)
    }
  }

  const mockNotifications = [
    { id: 1, text: 'Medieval Castle generation complete', time: '2m ago', type: 'success' },
    { id: 2, text: 'Ancient Dragon is processing…', time: '15m ago', type: 'processing' },
    { id: 3, text: 'Crystal Sword generation failed', time: '1h ago', type: 'error' },
  ]

  return (
    <header className="navbar">
      {/* ── Left: menu + title ── */}
      <div className="navbar-left">
        <button
          className="btn btn-ghost btn-icon navbar-menu-btn"
          onClick={onMenuToggle}
          aria-label="Toggle sidebar"
        >
          <Menu size={20} />
        </button>
        <div className="navbar-title-block">
          <h1 className="navbar-page-title">{pageTitle}</h1>
          <span className="navbar-breadcrumb">PolyGen / {pageTitle}</span>
        </div>
      </div>

      {/* ── Centre: Search ── */}
      <div className="navbar-search-wrap">
        <Search size={15} className="navbar-search-icon" />
        <input
          ref={searchInputRef}
          className="navbar-search-input"
          type="search"
          placeholder="Search assets, prompts, history…"
          value={searchValue}
          onChange={e => setSearchValue(e.target.value)}
          onKeyDown={handleSearchKeyDown}
          aria-label="Search"
        />
        <kbd className="navbar-search-kbd">⌘K</kbd>
      </div>

      {/* ── Right: actions ── */}
      <div className="navbar-right">
        {isAuthenticated ? (
          <>
            {/* Notifications */}
            <div className="navbar-dropdown-wrap" ref={notifRef}>
              <button
                className="btn btn-ghost btn-icon navbar-icon-btn"
                onClick={() => setNotificationsOpen(v => !v)}
                aria-label="Notifications"
                aria-expanded={notificationsOpen}
              >
                <Bell size={18} />
                {unreadCount > 0 && (
                  <span className="navbar-notif-badge">{unreadCount}</span>
                )}
              </button>

              {notificationsOpen && (
                <div className="navbar-dropdown navbar-notif-dropdown" role="menu">
                  <div className="navbar-dropdown-header">
                    <span className="navbar-dropdown-title">Notifications</span>
                    <button
                      className="navbar-dropdown-action"
                      onClick={() => setUnreadCount(0)}
                    >
                      Mark all read
                    </button>
                  </div>
                  <div className="navbar-dropdown-list">
                    {mockNotifications.map(n => (
                      <div key={n.id} className={`navbar-notif-item navbar-notif-${n.type}`}>
                        <span className={`status-dot status-dot-${n.type === 'success' ? 'green' : n.type === 'error' ? 'red' : 'yellow'}`} />
                        <div className="navbar-notif-text">
                          <p>{n.text}</p>
                          <span>{n.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Profile */}
            <div className="navbar-dropdown-wrap" ref={profileRef}>
              <button
                className="navbar-profile-btn"
                onClick={() => setProfileOpen(v => !v)}
                aria-label="Profile menu"
                aria-expanded={profileOpen}
              >
                <div className="navbar-avatar">SP</div>
                <div className="navbar-profile-info">
                  <span className="navbar-profile-name">Samiksha</span>
                  <span className="navbar-profile-plan">
                    <Sparkles size={10} />
                    Pro Plan
                  </span>
                </div>
                <ChevronDown
                  size={14}
                  className={`navbar-chevron ${profileOpen ? 'navbar-chevron-open' : ''}`}
                />
              </button>

              {profileOpen && (
                <div className="navbar-dropdown navbar-profile-dropdown" role="menu">
                  <div className="navbar-dropdown-header navbar-profile-header">
                    <div className="navbar-avatar navbar-avatar-lg">SP</div>
                    <div>
                      <p className="navbar-dropdown-name">Samiksha Patil</p>
                      <p className="navbar-dropdown-email">samiksha@polygen.ai</p>
                    </div>
                  </div>
                  <div className="navbar-dropdown-divider" />
                  <div className="navbar-dropdown-list">
                    <button
                      className="navbar-dropdown-item"
                      role="menuitem"
                      onClick={() => {
                        setProfileOpen(false)
                        navigate('/settings')
                      }}
                    >
                      <User size={15} /> Profile
                    </button>
                    <button
                      className="navbar-dropdown-item"
                      role="menuitem"
                      onClick={() => {
                        setProfileOpen(false)
                        navigate('/settings')
                      }}
                    >
                      <Settings size={15} /> Settings
                    </button>
                  </div>
                  <div className="navbar-dropdown-divider" />
                  <div className="navbar-dropdown-list">
                    <button
                      className="navbar-dropdown-item navbar-dropdown-item-danger"
                      role="menuitem"
                      onClick={() => {
                        setProfileOpen(false)
                        setIsAuthenticated(false)
                      }}
                    >
                      <LogOut size={15} /> Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="navbar-auth-actions">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setIsAuthenticated(true)}
            >
              <LogIn size={15} />
              Log In
            </button>
            <button
              className="btn btn-primary btn-sm"
              onClick={() => setIsAuthenticated(true)}
            >
              <UserPlus size={15} />
              Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Navbar
