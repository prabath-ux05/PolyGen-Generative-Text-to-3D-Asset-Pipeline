import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import PromptInput from '../components/PromptInput/PromptInput.jsx'
import { MAX_PROMPT_LENGTH } from '../services/generationService.js'

describe('PromptInput and Prompt Validation', () => {
  it('renders correctly with default state', () => {
    render(<PromptInput onGenerate={vi.fn()} isProcessing={false} />)

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    expect(textarea).toBeInTheDocument()
    expect(textarea.value).toBe('')

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    expect(generateBtn).toBeInTheDocument()
    expect(generateBtn).not.toBeDisabled()
  })

  it('rejects an empty prompt and displays validation error message', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} isProcessing={false} />)

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    fireEvent.click(generateBtn)

    expect(onGenerate).not.toHaveBeenCalled()
    expect(
      screen.getByText(/please enter a description for the 3d model you want to generate/i)
    ).toBeInTheDocument()
  })

  it('rejects whitespace-only prompt', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} isProcessing={false} />)

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    fireEvent.change(textarea, { target: { value: '       ' } })

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    fireEvent.click(generateBtn)

    expect(onGenerate).not.toHaveBeenCalled()
    expect(
      screen.getByText(/please enter a description for the 3d model you want to generate/i)
    ).toBeInTheDocument()
  })

  it('disables the generate button and shows over-limit styling when prompt exceeds MAX_PROMPT_LENGTH', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} isProcessing={false} />)

    const longText = 'a'.repeat(MAX_PROMPT_LENGTH + 1)
    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    fireEvent.change(textarea, { target: { value: longText } })

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    expect(generateBtn).toBeDisabled()

    const charCounter = screen.getByText(new RegExp(`${MAX_PROMPT_LENGTH + 1} / ${MAX_PROMPT_LENGTH}`))
    expect(charCounter).toHaveClass('prompt-char-over')
  })

  it('accepts valid prompt and submits trimmed text and selected format', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} isProcessing={false} defaultFormat="glb" />)

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    fireEvent.change(textarea, {
      target: { value: '   A glowing cybernetic sword with neon runes   ' },
    })

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    fireEvent.click(generateBtn)

    expect(onGenerate).toHaveBeenCalledTimes(1)
    expect(onGenerate).toHaveBeenCalledWith(
      'A glowing cybernetic sword with neon runes',
      'glb'
    )
  })

  it('updates prompt when suggestion pill is clicked and clears previous errors', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} isProcessing={false} />)

    // Trigger validation error first
    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    fireEvent.click(generateBtn)
    expect(screen.getByText(/please enter a description/i)).toBeInTheDocument()

    // Click first suggestion pill
    const suggestionPills = screen.getAllByRole('listitem')
    expect(suggestionPills.length).toBeGreaterThan(0)
    fireEvent.click(suggestionPills[0])

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    expect(textarea.value.length).toBeGreaterThan(0)
    expect(screen.queryByText(/please enter a description/i)).not.toBeInTheDocument()
  })

  it('disables textarea and button when isProcessing is true', () => {
    render(<PromptInput onGenerate={vi.fn()} isProcessing={true} />)

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    expect(textarea).toBeDisabled()

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    expect(generateBtn).toBeDisabled()
  })

  it('allows format selection between GLB and OBJ', () => {
    const onGenerate = vi.fn()
    render(<PromptInput onGenerate={onGenerate} defaultFormat="glb" />)

    const objFormatBtn = screen.getByRole('button', { name: /^OBJ$/i })
    fireEvent.click(objFormatBtn)

    const textarea = screen.getByRole('textbox', { name: /3d model description prompt/i })
    fireEvent.change(textarea, { target: { value: 'Sci-fi hovercar asset' } })

    const generateBtn = screen.getByRole('button', { name: /generate 3d/i })
    fireEvent.click(generateBtn)

    expect(onGenerate).toHaveBeenCalledWith('Sci-fi hovercar asset', 'obj')
  })
})
