import { NavLink, Link } from 'react-router-dom'
import {
  LayoutDashboard,
  Wand2,
  FolderOpen,
  History,
  LayoutTemplate,
  Settings,
  HelpCircle,
  Box,
  X,
  ChevronRight,
  LogIn,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import './Sidebar.css'

const navItems = [
  { path: '/',         label: 'Dashboard',          icon: LayoutDashboard },
  { path: '/create',   label: 'Create 3D Model',    icon: Wand2 },
  { path: '/assets',   label: 'My Assets',          icon: FolderOpen },
  { path: '/history',  label: 'Generation History', icon: History },
  { path: '/templates',label: 'Templates',          icon: LayoutTemplate },
]

const bottomItems = [
  { path: '/settings', label: 'Settings',     icon: Settings },
  { path: '/help',     label: 'Help & Support', icon: HelpCircle },
]

function Sidebar({ isOpen, onClose }) {
  const { user, isAuthenticated } = useAuth()
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose} aria-hidden="true" />}

      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`} aria-label="Main navigation">
        {/* ── Logo ── */}
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Box size={22} strokeWidth={1.8} />
          </div>
          <div className="sidebar-logo-text">
            <span className="sidebar-logo-name">PolyGen</span>
            <span className="sidebar-logo-tagline">3D Asset Pipeline</span>
          </div>
          <button className="sidebar-close-btn" onClick={onClose} aria-label="Close sidebar">
            <X size={18} />
          </button>
        </div>

        <div className="sidebar-divider" />

        {/* ── Main Nav ── */}
        <nav className="sidebar-nav" role="navigation">
          <span className="sidebar-section-label">Navigation</span>
          <ul className="sidebar-nav-list">
            {navItems.map(({ path, label, icon: Icon }) => (
              <li key={path}>
                <NavLink
                  to={path}
                  end={path === '/'}
                  className={({ isActive }) =>
                    `sidebar-nav-item ${isActive ? 'sidebar-nav-item-active' : ''}`
                  }
                  onClick={onClose}
                >
                  <Icon size={18} strokeWidth={1.8} className="sidebar-nav-icon" />
                  <span className="sidebar-nav-label">{label}</span>
                  {path === '/create' && (
                    <span className="sidebar-nav-badge">New</span>
                  )}
                  <ChevronRight size={14} className="sidebar-nav-chevron" />
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* ── Spacer ── */}
        <div className="sidebar-spacer" />

        <div className="sidebar-divider" />

        {/* ── Bottom Nav ── */}
        <nav className="sidebar-nav sidebar-nav-bottom">
          <ul className="sidebar-nav-list">
            {bottomItems.map(({ path, label, icon: Icon }) => (
              <li key={path}>
                <NavLink
                  to={path}
                  className={({ isActive }) =>
                    `sidebar-nav-item ${isActive ? 'sidebar-nav-item-active' : ''}`
                  }
                  onClick={onClose}
                >
                  <Icon size={18} strokeWidth={1.8} className="sidebar-nav-icon" />
                  <span className="sidebar-nav-label">{label}</span>
                  <ChevronRight size={14} className="sidebar-nav-chevron" />
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* ── User Profile ── */}
        {isAuthenticated && user ? (
          <div className="sidebar-user">
            <div className="sidebar-user-avatar">{user.avatar || 'PG'}</div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user.name}</span>
              <span className="sidebar-user-role">{user.role || '3D Creator'}</span>
            </div>
            <div className="sidebar-user-status">
              <span className="status-dot status-dot-green" title="Active" />
            </div>
          </div>
        ) : (
          <div className="sidebar-user">
            <div className="sidebar-user-avatar" style={{ background: 'var(--bg-card)' }}>
              G
            </div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">Guest Mode</span>
              <span className="sidebar-user-role">Demo Access</span>
            </div>
            <Link
              to="/login"
              onClick={onClose}
              className="btn btn-primary btn-sm"
              style={{ padding: '6px 10px', fontSize: '11px', gap: '4px' }}
              title="Sign in"
            >
              <LogIn size={12} />
              Sign In
            </Link>
          </div>
        )}
      </aside>
    </>
  )
}

export default Sidebar
