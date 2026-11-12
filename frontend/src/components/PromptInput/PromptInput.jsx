import React, { useState } from 'react'
import { Sparkles, ArrowRight, Lightbulb } from 'lucide-react'
import { promptSuggestions } from '../../data/mockData.js'
import './PromptInput.css'

const MAX_CHARS = 500

function PromptInput({ onGenerate }) {
  const [prompt, setPrompt] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const charCount = prompt.length
  const isOverLimit = charCount > MAX_CHARS
  const canGenerate = prompt.trim().length > 3 && !isOverLimit

  function handleGenerate() {
    if (!canGenerate) return
    if (onGenerate) onGenerate(prompt.trim())
    // Placeholder – real generation dispatched from parent
  }

  function handleSuggestionClick(suggestion) {
    setPrompt(suggestion)
  }

  function handleKeyDown(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleGenerate()
    }
  }

  return (
    <div className="prompt-section">
      <div className={`prompt-box ${isFocused ? 'prompt-box-focused' : ''}`}>
        {/* Gradient glow decoration */}
        <div className="prompt-glow" aria-hidden="true" />

        <div className="prompt-box-inner">
          <Sparkles size={18} className="prompt-sparkle-icon" />
          <textarea
            className="prompt-textarea"
            placeholder="Describe the 3D model you want to create…"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            maxLength={MAX_CHARS + 50}
            rows={4}
            aria-label="3D model description"
          />
        </div>

        <div className="prompt-footer">
          <div className="prompt-footer-left">
            <span className={`prompt-char-count ${isOverLimit ? 'prompt-char-over' : ''}`}>
              {charCount} / {MAX_CHARS}
            </span>
            <span className="prompt-hint">
              <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to generate
            </span>
          </div>
          <button
            className={`btn btn-primary btn-lg prompt-generate-btn ${!canGenerate ? 'prompt-btn-disabled' : ''}`}
            onClick={handleGenerate}
            disabled={!canGenerate}
            aria-label="Generate 3D model"
          >
            <Sparkles size={16} />
            Generate 3D
            <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* ── Suggestions ── */}
      <div className="prompt-suggestions">
        <span className="prompt-suggestions-label">
          <Lightbulb size={13} />
          Try an example:
        </span>
        <div className="prompt-suggestions-list">
          {promptSuggestions.slice(0, 4).map((s, i) => (
            <button
              key={i}
              className="prompt-suggestion-chip"
              onClick={() => handleSuggestionClick(s)}
              title={s}
            >
              {s.length > 42 ? s.slice(0, 42) + '…' : s}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PromptInput
