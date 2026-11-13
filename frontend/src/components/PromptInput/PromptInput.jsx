import { useState, useRef } from 'react'
import { Sparkles, ArrowRight, Lightbulb, X, AlertCircle, Loader2 } from 'lucide-react'
import { promptSuggestions } from '../../data/mockData.js'
import './PromptInput.css'

const MAX_CHARS = 500
const MIN_CHARS = 4

function PromptInput({ onGenerate, isProcessing = false }) {
  const [prompt, setPrompt] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [validationError, setValidationError] = useState('')
  const textareaRef = useRef(null)

  const charCount = prompt.length
  const isOverLimit = charCount > MAX_CHARS
  const isTooShort = prompt.trim().length > 0 && prompt.trim().length < MIN_CHARS
  const isNearLimit = charCount >= MAX_CHARS * 0.9 && !isOverLimit

  function validate() {
    const trimmed = prompt.trim()
    if (!trimmed) {
      setValidationError('Please enter a description for the 3D model you want to generate.')
      return false
    }
    if (trimmed.length < MIN_CHARS) {
      setValidationError(`Prompt is too brief. Please enter at least ${MIN_CHARS} characters.`)
      return false
    }
    if (trimmed.length > MAX_CHARS) {
      setValidationError(`Prompt exceeds maximum character limit of ${MAX_CHARS} characters.`)
      return false
    }
    setValidationError('')
    return true
  }

  function handleGenerate() {
    if (isProcessing) return
    if (!validate()) {
      textareaRef.current?.focus()
      return
    }
    if (onGenerate) {
      onGenerate(prompt.trim())
    }
  }

  function handleClear() {
    setPrompt('')
    setValidationError('')
    textareaRef.current?.focus()
  }

  function handleSuggestionClick(suggestion) {
    setPrompt(suggestion)
    setValidationError('')
    textareaRef.current?.focus()
  }

  function handleKeyDown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div className="prompt-section">
      <div
        className={`prompt-box ${isFocused ? 'prompt-box-focused' : ''} ${
          validationError ? 'prompt-box-error' : ''
        }`}
      >
        {/* Top gradient glow */}
        <div className="prompt-glow" aria-hidden="true" />

        <div className="prompt-box-inner">
          <Sparkles size={18} className="prompt-sparkle-icon" />
          <textarea
            ref={textareaRef}
            className="prompt-textarea"
            placeholder="Describe the 3D model you want to create (e.g. materials, shape, lighting, details)…"
            value={prompt}
            onChange={(e) => {
              setPrompt(e.target.value)
              if (validationError) setValidationError('')
            }}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            maxLength={MAX_CHARS + 50}
            rows={4}
            disabled={isProcessing}
            aria-label="3D model description prompt"
            aria-invalid={!!validationError}
            aria-describedby={validationError ? 'prompt-error-msg' : undefined}
          />
          {prompt.length > 0 && !isProcessing && (
            <button
              type="button"
              className="prompt-clear-btn"
              onClick={handleClear}
              title="Clear prompt text"
              aria-label="Clear prompt"
            >
              <X size={15} />
            </button>
          )}
        </div>

        {/* Validation message row */}
        {validationError && (
          <div className="prompt-error-banner" id="prompt-error-msg" role="alert">
            <AlertCircle size={14} />
            <span>{validationError}</span>
          </div>
        )}

        <div className="prompt-footer">
          <div className="prompt-footer-left">
            <span
              className={`prompt-char-count ${
                isOverLimit
                  ? 'prompt-char-over'
                  : isNearLimit
                  ? 'prompt-char-warning'
                  : ''
              }`}
            >
              {charCount} / {MAX_CHARS}
            </span>
            {isTooShort && (
              <span className="prompt-char-note">
                Min {MIN_CHARS} chars
              </span>
            )}
            <span className="prompt-hint">
              <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to generate
            </span>
          </div>

          <button
            type="button"
            className={`btn btn-primary btn-lg prompt-generate-btn ${
              isProcessing ? 'prompt-btn-loading' : ''
            }`}
            onClick={handleGenerate}
            disabled={isProcessing || isOverLimit}
            aria-label="Generate 3D model"
          >
            {isProcessing ? (
              <>
                <Loader2 size={16} className="spin-icon" />
                <span>Generating…</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Generate 3D</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* ── Selectable Prompt Suggestions (Day 2 Task 3) ── */}
      <div className="prompt-suggestions">
        <span className="prompt-suggestions-label">
          <Lightbulb size={13} />
          Select an example:
        </span>
        <div className="prompt-suggestions-list" role="list">
          {promptSuggestions.map((suggestion, index) => (
            <button
              key={index}
              type="button"
              className="prompt-suggestion-chip"
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isProcessing}
              title={`Use prompt: "${suggestion}"`}
              role="listitem"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PromptInput
