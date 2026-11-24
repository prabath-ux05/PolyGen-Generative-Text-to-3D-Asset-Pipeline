import { useState, useEffect } from 'react'
import { Edit2, AlertCircle, X, Check } from 'lucide-react'

function RenameModal({ asset, isOpen, onClose, onSave }) {
  const [newName, setNewName] = useState('')

  useEffect(() => {
    if (asset) {
      setNewName(asset.name || '')
    }
  }, [asset])

  if (!isOpen || !asset) return null

  function handleSubmit(e) {
    e.preventDefault()
    if (!newName.trim()) return
    onSave(asset.id, newName.trim())
    onClose()
  }

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="rename-modal-card card"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="rename-modal-header">
          <div className="rename-modal-title-row">
            <div className="rename-modal-icon-wrap">
              <Edit2 size={18} className="text-accent" />
            </div>
            <h3 className="rename-modal-title">Rename 3D Asset</h3>
          </div>
          <button
            type="button"
            className="btn btn-ghost btn-icon btn-sm"
            onClick={onClose}
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="rename-modal-form">
          <label className="rename-modal-label">
            Asset Name
            <input
              type="text"
              className="input rename-modal-input"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Enter new model name…"
              autoFocus
              maxLength={80}
            />
          </label>

          <div className="rename-modal-notice">
            <AlertCircle size={14} className="text-muted" />
            <div>
              <strong>Backend Support Notice</strong>
              <p>
                Server endpoint <code>PATCH /api/v1/assets/{'{id}'}</code> is pending backend implementation.
                Renaming will update this asset within your active session.
              </p>
            </div>
          </div>

          <div className="rename-modal-actions">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-sm"
              disabled={!newName.trim() || newName.trim() === asset.name}
            >
              <Check size={13} />
              Save Name
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RenameModal
