import { useState, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Box, User, Mail, Lock, Eye, EyeOff, ArrowRight, AlertCircle, Info, Check, ArrowLeft } from 'lucide-react'
import { useAuth } from '../../context/AuthContext.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import './Auth.css'

function SignUp() {
  const navigate = useNavigate()
  const { signup, isDemoMode } = useAuth()
  const { showToast } = useToast()

  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const [errors, setErrors] = useState({})
  const [isLoading, setIsLoading] = useState(false)

  // Password strength evaluation
  const passwordCriteria = useMemo(() => {
    return {
      hasMinLength: password.length >= 8,
      hasUpper: /[A-Z]/.test(password),
      hasNumber: /[0-9]/.test(password),
      hasSpecial: /[^A-Za-z0-9]/.test(password),
    }
  }, [password])

  const strengthScore = useMemo(() => {
    if (!password) return 0
    let score = 0
    if (passwordCriteria.hasMinLength) score += 1
    if (passwordCriteria.hasUpper) score += 1
    if (passwordCriteria.hasNumber) score += 1
    if (passwordCriteria.hasSpecial) score += 1
    return score
  }, [password, passwordCriteria])

  const strengthLabel = useMemo(() => {
    switch (strengthScore) {
      case 1:
        return { text: 'Weak', class: 'weak', activeClass: 'active-weak' }
      case 2:
        return { text: 'Fair', class: 'fair', activeClass: 'active-fair' }
      case 3:
        return { text: 'Good', class: 'good', activeClass: 'active-good' }
      case 4:
        return { text: 'Strong', class: 'strong', activeClass: 'active-strong' }
      default:
        return { text: 'None', class: '', activeClass: '' }
    }
  }, [strengthScore])

  function validateForm() {
    const newErrors = {}
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (!fullName.trim()) {
      newErrors.fullName = 'Full name is required.'
    } else if (fullName.trim().length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters.'
    }

    if (!email.trim()) {
      newErrors.email = 'Email address is required.'
    } else if (!emailRegex.test(email.trim())) {
      newErrors.email = 'Please provide a valid email address.'
    }

    if (!password) {
      newErrors.password = 'Password is required.'
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters.'
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Confirmation password is required.'
    } else if (confirmPassword !== password) {
      newErrors.confirmPassword = 'Passwords do not match.'
    }

    if (!agreeTerms) {
      newErrors.agreeTerms = 'You must accept the Terms of Service to create an account.'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e) {
    e.preventDefault()

    if (!validateForm()) {
      showToast({
        title: 'Validation Errors',
        message: 'Please review and correct the marked form fields.',
        type: 'error',
      })
      return
    }

    setIsLoading(true)

    setTimeout(async () => {
      try {
        await signup({ fullName, email, rememberMe: true })
        setIsLoading(false)

        showToast({
          title: 'Account Created!',
          message: `Welcome to PolyGen, ${fullName}! Workspace initialized in Demo Mode.`,
          type: 'success',
          duration: 5000,
        })

        navigate('/')
      } catch {
        setIsLoading(false)
        showToast({
          title: 'Sign Up Error',
          message: 'An error occurred during account registration.',
          type: 'error',
        })
      }
    }, 800)
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
          <h1 className="auth-title">Create your account</h1>
          <p className="auth-subtitle">Generate high-fidelity 3D assets from text in seconds</p>
        </div>

        {isDemoMode && (
          <div className="auth-demo-badge" role="region" aria-label="Demo mode notice">
            <Info size={16} />
            <div>
              <strong>Demo Registration Mode</strong>
              Live FastAPI backend does not yet provide user persistence. This account will run locally in simulated demo mode.
            </div>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          {/* Full Name */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="signup-name">
              Full Name <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <User size={16} className="auth-input-icon" />
              <input
                id="signup-name"
                type="text"
                className={`auth-input ${errors.fullName ? 'has-error' : ''}`}
                placeholder="e.g. Samiksha Patil"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value)
                  if (errors.fullName) setErrors((prev) => ({ ...prev, fullName: null }))
                }}
                disabled={isLoading}
                autoComplete="name"
              />
            </div>
            {errors.fullName && (
              <span className="auth-error-msg" role="alert">
                <AlertCircle size={12} /> {errors.fullName}
              </span>
            )}
          </div>

          {/* Email Address */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="signup-email">
              Email Address <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <Mail size={16} className="auth-input-icon" />
              <input
                id="signup-email"
                type="email"
                className={`auth-input ${errors.email ? 'has-error' : ''}`}
                placeholder="samiksha@polygen.ai"
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
            <label className="auth-label" htmlFor="signup-password">
              Password <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <Lock size={16} className="auth-input-icon" />
              <input
                id="signup-password"
                type={showPassword ? 'text' : 'password'}
                className={`auth-input ${errors.password ? 'has-error' : ''}`}
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  if (errors.password) setErrors((prev) => ({ ...prev, password: null }))
                }}
                disabled={isLoading}
                autoComplete="new-password"
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

            {/* Password Strength Indicator */}
            {password.length > 0 && (
              <div className="pwd-strength-container" aria-live="polite">
                <div className="pwd-strength-bars">
                  {[1, 2, 3, 4].map((step) => (
                    <div
                      key={step}
                      className={`pwd-strength-bar ${
                        step <= strengthScore ? strengthLabel.activeClass : ''
                      }`}
                    />
                  ))}
                </div>
                <div className="pwd-strength-meta">
                  <span className="pwd-strength-label">Password Strength:</span>
                  <span className={`pwd-strength-text ${strengthLabel.class}`}>
                    {strengthLabel.text}
                  </span>
                </div>
                <div className="pwd-rules-list">
                  <span className={`pwd-rule-item ${passwordCriteria.hasMinLength ? 'valid' : ''}`}>
                    <Check size={11} /> 8+ characters
                  </span>
                  <span className={`pwd-rule-item ${passwordCriteria.hasUpper ? 'valid' : ''}`}>
                    <Check size={11} /> Uppercase letter
                  </span>
                  <span className={`pwd-rule-item ${passwordCriteria.hasNumber ? 'valid' : ''}`}>
                    <Check size={11} /> Number (0-9)
                  </span>
                  <span className={`pwd-rule-item ${passwordCriteria.hasSpecial ? 'valid' : ''}`}>
                    <Check size={11} /> Special symbol (!@#$)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="signup-confirm-password">
              Confirm Password <span className="required">*</span>
            </label>
            <div className="auth-input-wrapper">
              <Lock size={16} className="auth-input-icon" />
              <input
                id="signup-confirm-password"
                type={showConfirmPassword ? 'text' : 'password'}
                className={`auth-input ${errors.confirmPassword ? 'has-error' : ''}`}
                placeholder="Re-enter your password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value)
                  if (errors.confirmPassword) setErrors((prev) => ({ ...prev, confirmPassword: null }))
                }}
                disabled={isLoading}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="auth-toggle-pwd"
                onClick={() => setShowConfirmPassword((v) => !v)}
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
              >
                {showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.confirmPassword && (
              <span className="auth-error-msg" role="alert">
                <AlertCircle size={12} /> {errors.confirmPassword}
              </span>
            )}
          </div>

          {/* Terms & Conditions Checkbox */}
          <div className="auth-field">
            <label className="auth-checkbox-label" htmlFor="signup-terms">
              <input
                id="signup-terms"
                type="checkbox"
                checked={agreeTerms}
                onChange={(e) => {
                  setAgreeTerms(e.target.checked)
                  if (errors.agreeTerms) setErrors((prev) => ({ ...prev, agreeTerms: null }))
                }}
                disabled={isLoading}
              />
              <span>
                I agree to the <a href="#terms" onClick={(e) => e.preventDefault()} style={{ color: 'var(--accent-primary)' }}>Terms of Service</a> and <a href="#privacy" onClick={(e) => e.preventDefault()} style={{ color: 'var(--accent-primary)' }}>Privacy Policy</a>
              </span>
            </label>
            {errors.agreeTerms && (
              <span className="auth-error-msg" role="alert">
                <AlertCircle size={12} /> {errors.agreeTerms}
              </span>
            )}
          </div>

          {/* Create Account Submit */}
          <button
            type="submit"
            className="btn btn-primary auth-submit-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="dash-spinner" style={{ width: 16, height: 16 }} />
                <span>Creating Account…</span>
              </>
            ) : (
              <>
                <span>Create Account</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="auth-divider">
          <span>Social Authentication</span>
        </div>

        {/* Google sign-up UI condition check */}
        <div className="auth-oauth-notice">
          <Info size={14} />
          <span>Google Sign-Up provider integration</span>
          <span className="auth-oauth-badge">Backend OAuth Pending</span>
        </div>

        <div className="auth-footer">
          Already have an account?
          <Link to="/login">Sign in here</Link>
        </div>
      </div>
    </div>
  )
}

export default SignUp
