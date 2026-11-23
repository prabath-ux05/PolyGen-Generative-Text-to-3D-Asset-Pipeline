import { describe, it, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Login from '../pages/Auth/Login.jsx'
import SignUp from '../pages/Auth/SignUp.jsx'
import { AuthProvider } from '../context/AuthContext.jsx'
import { ToastProvider } from '../context/ToastContext.jsx'

function renderWithProviders(ui) {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <ToastProvider>{ui}</ToastProvider>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('Auth Validation - Login Page', () => {
  it('renders login form elements and demo mode indicator', () => {
    renderWithProviders(<Login />)

    expect(screen.getByPlaceholderText(/name@example\.com/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in to polygen/i })).toBeInTheDocument()
    expect(screen.getByText(/demo \/ mock authentication active/i)).toBeInTheDocument()
  })

  it('validates required fields on empty submit', async () => {
    renderWithProviders(<Login />)

    const submitBtn = screen.getByRole('button', { name: /sign in to polygen/i })
    fireEvent.click(submitBtn)

    expect(await screen.findByText(/email address is required/i)).toBeInTheDocument()
    expect(screen.getByText(/password is required/i)).toBeInTheDocument()
  })

  it('validates invalid email format and short password', async () => {
    renderWithProviders(<Login />)

    const emailInput = screen.getByPlaceholderText(/name@example\.com/i)
    const passwordInput = screen.getByPlaceholderText(/enter your password/i)

    fireEvent.change(emailInput, { target: { value: 'invalid-email-format' } })
    fireEvent.change(passwordInput, { target: { value: '123' } })

    const submitBtn = screen.getByRole('button', { name: /sign in to polygen/i })
    fireEvent.click(submitBtn)

    expect(await screen.findByText(/please enter a valid email address/i)).toBeInTheDocument()
    expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
  })

  it('toggles password visibility between password and text', () => {
    renderWithProviders(<Login />)

    const passwordInput = screen.getByPlaceholderText(/enter your password/i)
    expect(passwordInput).toHaveAttribute('type', 'password')

    const toggleBtn = screen.getByRole('button', { name: /show password/i })
    fireEvent.click(toggleBtn)

    expect(passwordInput).toHaveAttribute('type', 'text')

    const hideBtn = screen.getByRole('button', { name: /hide password/i })
    fireEvent.click(hideBtn)

    expect(passwordInput).toHaveAttribute('type', 'password')
  })
})

describe('Auth Validation - SignUp Page', () => {
  it('renders sign up form elements', () => {
    renderWithProviders(<SignUp />)

    expect(screen.getByPlaceholderText(/samiksha patil/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/samiksha@polygen\.ai/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/create a strong password/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/re-enter your password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument()
  })

  it('validates required fields on empty submit', async () => {
    renderWithProviders(<SignUp />)

    const submitBtn = screen.getByRole('button', { name: /create account/i })
    fireEvent.click(submitBtn)

    expect(await screen.findByText(/full name is required/i)).toBeInTheDocument()
    expect(screen.getByText(/email address is required/i)).toBeInTheDocument()
    expect(screen.getByText(/^password is required\.$/i)).toBeInTheDocument()
    expect(screen.getByText(/confirmation password is required/i)).toBeInTheDocument()
    expect(screen.getByText(/you must accept the terms/i)).toBeInTheDocument()
  })

  it('evaluates password strength dynamically', () => {
    renderWithProviders(<SignUp />)

    const passwordInput = screen.getByPlaceholderText(/create a strong password/i)

    // Weak: min 8 chars only
    fireEvent.change(passwordInput, { target: { value: 'password' } })
    expect(screen.getByText(/weak/i)).toBeInTheDocument()

    // Fair: min 8 + uppercase
    fireEvent.change(passwordInput, { target: { value: 'Password' } })
    expect(screen.getByText(/fair/i)).toBeInTheDocument()

    // Good: min 8 + uppercase + number
    fireEvent.change(passwordInput, { target: { value: 'Password12' } })
    expect(screen.getByText(/good/i)).toBeInTheDocument()

    // Strong: min 8 + uppercase + number + special
    fireEvent.change(passwordInput, { target: { value: 'Password12!#' } })
    expect(screen.getByText(/strong/i)).toBeInTheDocument()
  })

  it('validates password matching on confirm password', async () => {
    const { container } = renderWithProviders(<SignUp />)

    const nameInput = screen.getByPlaceholderText(/samiksha patil/i)
    const emailInput = screen.getByPlaceholderText(/samiksha@polygen\.ai/i)
    const passInput = screen.getByPlaceholderText(/create a strong password/i)
    const confirmPassInput = screen.getByPlaceholderText(/re-enter your password/i)
    const termsCheckbox = container.querySelector('#signup-terms')

    fireEvent.change(nameInput, { target: { value: 'Samiksha Patil' } })
    fireEvent.change(emailInput, { target: { value: 'samiksha@polygen.ai' } })
    fireEvent.change(passInput, { target: { value: 'StrongPass123!' } })
    fireEvent.change(confirmPassInput, { target: { value: 'DifferentPass123!' } })
    fireEvent.click(termsCheckbox)

    const submitBtn = screen.getByRole('button', { name: /create account/i })
    fireEvent.click(submitBtn)

    expect(await screen.findByText(/passwords do not match/i)).toBeInTheDocument()
  })
})
