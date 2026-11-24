import { Box, AlertTriangle, RefreshCw, Sparkles } from 'lucide-react'

export function ViewerEmptyState({ onSelectSample }) {
  return (
    <div className="viewer-fallback-overlay viewer-empty-overlay">
      <div className="viewer-fallback-card">
        <div className="viewer-fallback-icon-wrap empty-pulse">
          <Box size={36} strokeWidth={1.5} className="viewer-fallback-icon" />
          <div className="viewer-orbit-ring" />
        </div>
        <div className="viewer-badge-pill">
          <Sparkles size={11} />
          Interactive 3D Engine
        </div>
        <h3 className="viewer-fallback-title">Your 3D model will appear here.</h3>
        <p className="viewer-fallback-desc">
          Generate an asset using the prompt pipeline, enter a model URL, or load a sample model to test the interactive viewer.
        </p>

        {onSelectSample && (
          <div className="viewer-sample-buttons">
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={() => onSelectSample('/models/sample-crystal.obj', 'Crystal')}
            >
              <Sparkles size={13} />
              Load Sample Crystal (OBJ)
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => onSelectSample('/models/sample-chair.obj', 'Chair')}
            >
              <Box size={13} />
              Load Sample Chair (OBJ)
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export function ViewerErrorState({ error, onRetry, onFallback }) {
  return (
    <div className="viewer-fallback-overlay viewer-error-overlay" role="alert">
      <div className="viewer-fallback-card viewer-error-card">
        <div className="viewer-fallback-icon-wrap error-pulse">
          <AlertTriangle size={34} strokeWidth={1.7} className="viewer-error-icon" />
        </div>
        <div className="viewer-badge-pill badge-pill-error">
          Model Load Error
        </div>
        <h3 className="viewer-fallback-title">Failed to load 3D model</h3>
        <p className="viewer-fallback-desc">
          {error || 'Unable to parse the supplied 3D model file. Ensure the file path is accessible and conforms to standard OBJ/GLTF format.'}
        </p>
        <div className="viewer-fallback-actions">
          {onRetry && (
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={onRetry}
            >
              <RefreshCw size={13} />
              Retry Loading
            </button>
          )}
          {onFallback && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onFallback}
            >
              <Box size={13} />
              Load Test Model Instead
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export function ViewerLoadingState({ message = 'Loading 3D asset…', progress }) {
  return (
    <div className="viewer-fallback-overlay viewer-loading-overlay">
      <div className="viewer-loading-card">
        <div className="viewer-loading-spinner" />
        <p className="viewer-loading-text">{message}</p>
        {typeof progress === 'number' && progress >= 0 && (
          <div className="viewer-loading-bar-wrap">
            <div
              className="viewer-loading-bar-fill"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
