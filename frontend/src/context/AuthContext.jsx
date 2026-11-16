import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

// Default demo user profile (no sensitive credentials)
const DEFAULT_DEMO_USER = {
  name: 'Samiksha Patil',
  email: 'samiksha@polygen.ai',
  avatar: 'SP',
  role: 'Frontend Developer',
  plan: 'Pro Plan',
}

const DEMO_STORAGE_KEY = 'polygen_demo_session'

export function AuthProvider({ children }) {
  // Initialize from session metadata if previously remembered, otherwise default demo user
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem(DEMO_STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        // Ensure no passwords exist in storage
        if (parsed && parsed.email) {
          delete parsed.password
          return parsed
        }
      }
    } catch {
      // Ignore JSON parsing errors
    }
    return DEFAULT_DEMO_USER
  })

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return true // Default logged-in state for dashboard exploration
  })

  // Explicit notice flag: Backend Auth API is not yet available
  const isDemoMode = true

  const login = async ({ email, rememberMe = false }) => {
    // Note: No backend auth endpoint exists in FastAPI scaffold yet.
    // Simulating authentication without storing any passwords.
    const namePart = email.split('@')[0]
    const formattedName = namePart
      .replace(/[._-]/g, ' ')
      .replace(/\b\w/g, (c) => c.toUpperCase())

    const initials = formattedName
      .split(' ')
      .map((w) => w[0])
      .slice(0, 2)
      .join('')
      .toUpperCase() || 'PG'

    const sessionUser = {
      name: formattedName || 'PolyGen Creator',
      email: email.trim().toLowerCase(),
      avatar: initials,
      role: '3D Artist',
      plan: 'Pro Plan',
    }

    setUser(sessionUser)
    setIsAuthenticated(true)

    if (rememberMe) {
      try {
        localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(sessionUser))
      } catch {
        // Storage unavailable
      }
    } else {
      try {
        localStorage.removeItem(DEMO_STORAGE_KEY)
      } catch {
        // Storage unavailable
      }
    }

    return { success: true, user: sessionUser }
  }

  const signup = async ({ fullName, email, rememberMe = false }) => {
    // Note: No backend auth endpoint exists in FastAPI scaffold yet.
    // Simulating account registration in Demo Mode.
    const trimmedName = fullName.trim()
    const initials = trimmedName
      .split(' ')
      .map((w) => w[0])
      .slice(0, 2)
      .join('')
      .toUpperCase() || 'PG'

    const sessionUser = {
      name: trimmedName,
      email: email.trim().toLowerCase(),
      avatar: initials,
      role: 'Creator',
      plan: 'Free Trial',
    }

    setUser(sessionUser)
    setIsAuthenticated(true)

    if (rememberMe) {
      try {
        localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(sessionUser))
      } catch {
        // Storage unavailable
      }
    }

    return { success: true, user: sessionUser }
  }

  const logout = () => {
    setIsAuthenticated(false)
    setUser(null)
    try {
      localStorage.removeItem(DEMO_STORAGE_KEY)
    } catch {
      // Storage unavailable
    }
  }

  const updateProfile = (data) => {
    setUser((prev) => {
      const updated = { ...prev, ...data }
      delete updated.password
      try {
        if (localStorage.getItem(DEMO_STORAGE_KEY)) {
          localStorage.setItem(DEMO_STORAGE_KEY, JSON.stringify(updated))
        }
      } catch {
        // Storage unavailable
      }
      return updated
    })
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isDemoMode,
        login,
        signup,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
