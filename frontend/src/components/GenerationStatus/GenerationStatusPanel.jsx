import {
  Clock,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Loader2,
  X,
  Play,
  RotateCcw,
  Box,
  Eye,
  Info,
} from 'lucide-react'
import './GenerationStatusPanel.css'

function formatDate(isoString) {
  if (!isoString) return 'Just now'
  try {
    const d = new Date(isoString)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return 'Just now'
  }
}

export function GenerationStatusPanel({
  job,
  onDismiss,
  onViewIn3D,
  onSimulatePipeline,
  onRetry,
}) {
  if (!job) return null

  const isUnavailable = job.status === 'unavailable' || job.status === 503
  const isFailed = job.status === 'failed'
  const isCompleted = job.status === 'completed'
  const isProcessing = job.status === 'processing'
  const isPending = job.status === 'pending'
  const isSubmitted = job.status === 'submitted'

  const statusPillClass =
    isCompleted ? 'status-pill-completed' :
    isFailed ? 'status-pill-failed' :
    isUnavailable ? 'status-pill-unavailable' :
    isProcessing ? 'status-pill-processing' :
    isPending ? 'status-pill-pending' :
    'status-pill-submitted'

  const StatusIcon =
    isCompleted ? CheckCircle2 :
    isFailed ? AlertCircle :
    isUnavailable ? AlertTriangle :
    isProcessing ? Loader2 :
    isPending ? Clock :
    Loader2

  return (
    <div
      className={`gen-status-panel gen-status-panel-${job.status}`}
      role="region"
      aria-label="Generation Pipeline Status"
    >
      {/* ── Header ── */}
      <div className="gen-status-header">
        <div className="gen-status-title-row">
          <h4 className="gen-status-title">
            <Box size={16} className="text-accent" />
            3D Generation Task
          </h4>
          {job.job_id && (
            <span className="gen-status-id-badge" title={`Job ID: ${job.job_id}`}>
              ID: {job.job_id.length > 18 ? job.job_id.slice(0, 18) + '…' : job.job_id}
            </span>
          )}
        </div>

        <div className="gen-status-actions-top">
          <span className={`gen-status-pill ${statusPillClass}`}>
            <StatusIcon
              size={12}
              className={isProcessing || isSubmitted ? 'spin-icon' : ''}
            />
            {job.status === 'unavailable' ? 'Service Unavailable (503)' : job.status}
          </span>

          {job.is_mock ? (
            <span className="gen-mock-tag" title="Running in simulated demo mode">
              Demo Mode
            </span>
          ) : (
            <span className="gen-live-tag" title="Connected to FastAPI backend">
              Live Backend
            </span>
          )}

          {onDismiss && (
            <button
              type="button"
              className="gen-status-dismiss-btn"
              onClick={onDismiss}
              aria-label="Dismiss status notification"
            >
              <X size={15} />
            </button>
          )}
        </div>
      </div>

      {/* ── Original Prompt ── */}
      {job.prompt && (
        <div className="gen-status-prompt-box">
          <p className="gen-status-prompt-text">
            <strong>Prompt:</strong> &ldquo;{job.prompt}&rdquo;
          </p>
        </div>
      )}

      {/* ── Metadata Row ── */}
      <div className="gen-status-meta-row">
        <div className="gen-status-meta-item">
          <Clock size={12} />
          <span>Submitted: {formatDate(job.created_at)}</span>
        </div>
        {job.output_format && (
          <div className="gen-status-meta-item">
            <Box size={12} />
            <span>Format: {String(job.output_format).toUpperCase()}</span>
          </div>
        )}
        {job.updated_at && job.updated_at !== job.created_at && (
          <div className="gen-status-meta-item">
            <span>Updated: {formatDate(job.updated_at)}</span>
          </div>
        )}
      </div>

      {/* ── Indeterminate Activity Indicator for Pending/Processing ── */}
      {(isProcessing || isPending || isSubmitted) && (
        <div className="gen-status-activity">
          <div className="gen-indeterminate-bar">
            <div className="gen-indeterminate-fill" />
          </div>
        </div>
      )}

      {/* ── Special HTTP 503 Notice Box (FastAPI Engine Pending) ── */}
      {isUnavailable && (
        <div className="gen-status-503-box">
          <AlertTriangle size={18} />
          <div className="gen-status-503-content">
            <h5>FastAPI Backend: Request Validated (HTTP 503)</h5>
            <p>
              {job.error_message ||
                'Text-to-3D generation engine is not yet integrated into the backend pipeline.'}
            </p>
            <p className="gen-status-503-note">
              Per Team Lead Day 1–5 specifications: The API received and validated your request successfully. Full AI generation engine execution will activate in upcoming backend integration phases.
            </p>
          </div>
        </div>
      )}

      {/* ── Standard Error Box ── */}
      {isFailed && (
        <div className="gen-status-error-box">
          <AlertCircle size={18} />
          <div className="gen-status-error-text">
            <h5>Generation Failed</h5>
            <p>{job.error_message || 'An unexpected error occurred during model generation.'}</p>
          </div>
        </div>
      )}

      {/* ── Action Buttons ── */}
      <div className="gen-status-footer">
        {isCompleted && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => onViewIn3D && onViewIn3D(job.model_url || '/models/sample-crystal.obj')}
          >
            <Eye size={13} />
            Inspect in 3D Viewer
          </button>
        )}

        {isUnavailable && onSimulatePipeline && (
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onSimulatePipeline}
            title="Preview full pipeline lifecycle and 3D viewer in simulated demo mode"
          >
            <Play size={13} />
            Run Simulated Pipeline Demo
          </button>
        )}

        {(isFailed || isUnavailable) && onRetry && (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onRetry}
          >
            <RotateCcw size={13} />
            Retry Backend Request
          </button>
        )}

        {isCompleted && (
          <span className="text-secondary" style={{ fontSize: 12, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Info size={12} />
            Model ready for rotation & inspection
          </span>
        )}
      </div>
    </div>
  )
}

export default GenerationStatusPanel
