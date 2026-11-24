import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Box, Mail, Lock, Eye, EyeOff, ArrowRight, Sparkles, AlertCircle, Info, ArrowLeft } from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import './Auth.css'

function Login() {
  const navigate = useNavigate()
  const { login, isDemoMode } = useAuth()
  const { showToast } = useToast()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)

  const [errors, setErrors] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [showForgotBox, setShowForgotBox] = useState(false)
  const [forgotEmail, setForgotEmail] = useState('')

  // Validation rules
  function validateForm() {
    const newErrors = {}
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (!email.trim()) {
      newErrors.email = 'Email address is required.'
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = 'Please enter a valid email address (e.g., user@polygen.ai).'
    }

    if (!password) {
      newErrors.password = 'Password is required.'
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e) {
    e.preventDefault()

    if (!validateForm()) {
      showToast({
        title: 'Validation Failed',
        message: 'Please resolve the highlighted form errors before continuing.',
        type: 'error',
      })
      return
    }

    setIsLoading(true)

    // Simulate authentication delay
    setTimeout(async () => {
      try {
        await login({ email, rememberMe })
        setIsLoading(false)

        showToast({
          title: 'Welcome Back!',
          message: `Logged in successfully as ${email} (Demo Mode).`,
          type: 'success',
        })

        navigate('/')
      } catch {
        setIsLoading(false)
        showToast({
          title: 'Sign In Failed',
          message: 'An unexpected error occurred during demo sign-in.',
          type: 'error',
        })
      }
    }, 700)
  }

  function handleQuickFillDemo() {
    setEmail('samiksha@polygen.ai')
    setPassword('PolyGen2026!')
    setErrors({})
    showToast({
      title: 'Demo Credentials Loaded',
      message: 'Prefilled demo credentials for Samiksha Patil.',
      type: 'info',
    })
  }

  function handleSendReset(e) {
    e.preventDefault()
    if (!forgotEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(forgotEmail)) {
      showToast({
        title: 'Invalid Email',
        message: 'Please provide a valid email to receive reset instructions.',
        type: 'error',
      })
      return
    }

    showToast({
      title: 'Reset Link Dispatched',
      message: `Password reset simulation sent to ${forgotEmail}. No live emails sent in Demo Mode.`,
      type: 'info',
      duration: 5000,
    })
    setShowForgotBox(false)
    setForgotEmail('')
  }

  return (
    <div className="auth-page">
      <div className="auth-bg-glow auth-bg-glow-1" />
      <div className="auth-bg-glow auth-bg-glow-2" />

      <div className="auth-card">
        <Link to="/" className="auth-back-link">
          <ArrowLeft size={14} /> Back to Dashboard
        </Link>

        <div className="auth-header">
          <Link to="/" className="auth-logo">
            <div className="auth-logo-icon">
              <Box size={22} strokeWidth={2} />
            </div>
            <span className="auth-logo-text">PolyGen</span>
          </Link>
          <h1 className="auth-title">Welcome back</h1>
          <p className="auth-subtitle">Sign in to your PolyGen 3D asset generation workspace</p>
        </div>

        {isDemoMode && (
          <div className="auth-demo-badge" role="region" aria-label="Demo mode notice">
            <Info size={16} />
            <div>
              <strong>Demo / Mock Authentication Active</strong>
              Backend auth endpoints are scaffolded. This session runs in frontend demo mode; no plain-text passwords are saved.
            </div>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          {/* Email */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">
              Email Address <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <Mail size={16} className="auth-input-icon" />
              <input
                id="login-email"
                type="email"
                className={`auth-input ${errors.email ? 'has-error' : ''}`}
                placeholder="name@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  if (errors.email) setErrors((prev) => ({ ...prev, email: null }))
                }}
                disabled={isLoading}
                autoComplete="email"
              />
            </div>
            {errors.email && (
              <span className="auth-error-msg" role="alert">
                <AlertCircle size={12} /> {errors.email}
              </span>
            )}
          </div>

          {/* Password */}
          <div className="auth-field">
            <div className="auth-label">
              <label htmlFor="login-password">
                Password <span className="required">*</span>
              </label>
              <button
                type="button"
                className="auth-forgot-link"
                onClick={() => setShowForgotBox((v) => !v)}
              >
                Forgot password?
              </button>
            </div>
            <div className="auth-input-wrapper">
              <Lock size={16} className="auth-input-icon" />
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                className={`auth-input ${errors.password ? 'has-error' : ''}`}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  if (errors.password) setErrors((prev) => ({ ...prev, password: null }))
                }}
                disabled={isLoading}
                autoComplete="current-password"
              />
              <button
                type="button"
                className="auth-toggle-pwd"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && (
              <span className="auth-error-msg" role="alert">
                <AlertCircle size={12} /> {errors.password}
              </span>
            )}
          </div>

          {/* Inline Forgot Password Box */}
          {showForgotBox && (
            <div className="auth-forgot-box">
              <p>Enter your email and we will send a demo password reset link:</p>
              <div className="auth-input-wrapper">
                <Mail size={15} className="auth-input-icon" />
                <input
                  type="email"
                  className="auth-input"
                  placeholder="Enter registered email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={handleSendReset}
                >
                  Send Reset Link
                </button>
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowForgotBox(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Options Row */}
          <div className="auth-options-row">
            <label className="auth-checkbox-label" htmlFor="login-remember">
              <input
                id="login-remember"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
              />
              <span>Remember this session</span>
            </label>

            <button
              type="button"
              className="auth-quick-demo"
              onClick={handleQuickFillDemo}
              title="Autofill Samiksha Patil test account"
            >
              <Sparkles size={12} /> Demo Fill
            </button>
          </div>

          {/* Submit */}
          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="dash-spinner" style={{ width: 16, height: 16 }} />
                <span>Signing In…</span>
              </>
            ) : (
              <>
                <span>Sign In to PolyGen</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>Social Authentication</span>
        </div>

        {/* OAuth note per instructions */}
        <div className="auth-oauth-notice">
          <Info size={14} />
          <span>Google Workspace SSO integration</span>
          <span className="auth-oauth-badge">Backend Pending</span>
        </div>

        <div className="auth-footer">
          Don&apos;t have an account?
          <Link to="/signup">Create one now</Link>
        </div>
      </div>
    </div>
  )
}

export default Login
