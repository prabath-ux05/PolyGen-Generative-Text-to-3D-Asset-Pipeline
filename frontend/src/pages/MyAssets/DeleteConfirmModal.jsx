import { Trash2, AlertTriangle, X } from 'lucide-react'

function DeleteConfirmModal({ asset, isOpen, onClose, onConfirm }) {
  if (!isOpen || !asset) return null

  return (
    <div className="modal-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="delete-modal-card card"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="delete-modal-header">
          <div className="delete-modal-icon-wrap">
            <Trash2 size={22} className="text-red" />
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

        <div className="delete-modal-content">
          <h3 className="delete-modal-title">Delete &ldquo;{asset.name}&rdquo;?</h3>
          <p className="delete-modal-desc">
            Are you sure you want to delete this 3D model? It will be permanently removed
            from your asset library and viewport history.
          </p>

          <div className="delete-modal-notice">
            <AlertTriangle size={14} className="text-yellow" />
            <div>
              <strong>Backend Support Notice</strong>
              <p>
                Server-side deletion endpoint (<code>DELETE /api/v1/assets/{'{id}'}</code>)
                is not yet mounted on FastAPI. This action removes the model from your active frontend session.
              </p>
            </div>
          </div>
        </div>

        <div className="delete-modal-actions">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm delete-confirm-btn"
            onClick={() => {
              onConfirm(asset.id)
              onClose()
            }}
          >
            <Trash2 size={13} />
            Confirm Delete
          </button>
        </div>
      </div>
    </div>
  )
}

export default DeleteConfirmModal
