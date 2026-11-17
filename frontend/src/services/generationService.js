/**
 * PolyGen Generation API Service
 *
 * Implements client-side communication with the FastAPI backend per the Day 1–5
 * backend API contract specification.
 *
 * Backend endpoints:
 *   - GET  /health               -> Health check
 *   - POST /api/v1/generations   -> Text-to-3D generation request (returns HTTP 503 until engine integrated)
 *   - GET  /api/v1/generations/{id} -> (Planned Day 6+ status endpoint)
 */

export const MIN_PROMPT_LENGTH = 1
export const MAX_PROMPT_LENGTH = 1000

export const OutputFormat = Object.freeze({
  OBJ: 'obj',
  GLB: 'glb',
})

export const GenerationJobStatus = Object.freeze({
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
})

// Custom Error Classes
export class GenerationApiError extends Error {
  constructor(message, status = 0, detail = null) {
    super(message)
    this.name = 'GenerationApiError'
    this.status = status
    this.detail = detail
  }
}

export class ValidationError extends GenerationApiError {
  constructor(detail, status = 422) {
    const message = Array.isArray(detail)
      ? detail.map((e) => e.msg || e.message).join('; ')
      : typeof detail === 'string'
      ? detail
      : 'Invalid generation request parameters.'
    super(message, status, detail)
    this.name = 'ValidationError'
  }
}

export class ServiceUnavailableError extends GenerationApiError {
  constructor(detail = 'Text-to-3D generation engine is not yet integrated.', status = 503) {
    super(detail, status, detail)
    this.name = 'ServiceUnavailableError'
  }
}

export class NetworkError extends GenerationApiError {
  constructor(originalError, targetUrl) {
    const message = `Unable to connect to PolyGen backend API at ${targetUrl}. Ensure the FastAPI server is running.`
    super(message, 0, originalError?.message)
    this.name = 'NetworkError'
  }
}

/**
 * Resolves the API base URL from Vite environment variables or defaults to relative proxy URL.
 */
export function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL
  if (envUrl && typeof envUrl === 'string') {
    return envUrl.replace(/\/$/, '')
  }
  return '' // Uses Vite dev proxy '/api' configured in vite.config.js
}

/**
 * Validates prompt input strictly according to backend constraints:
 * - 1 to 1,000 characters
 * - Non-empty and not composed solely of whitespace
 */
export function validatePrompt(prompt) {
  if (prompt === null || prompt === undefined) {
    return { valid: false, error: 'Prompt is required.' }
  }
  const trimmed = String(prompt).trim()
  if (trimmed.length < MIN_PROMPT_LENGTH) {
    return { valid: false, error: 'Prompt cannot be empty or contain only whitespace.' }
  }
  if (trimmed.length > MAX_PROMPT_LENGTH) {
    return {
      valid: false,
      error: `Prompt exceeds maximum allowed length of ${MAX_PROMPT_LENGTH} characters.`,
    }
  }
  return { valid: true, sanitized: trimmed }
}

/**
 * Checks backend health status via GET /health.
 */
export async function checkBackendHealth(options = {}) {
  const { signal, timeout = 5000 } = options
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/health`

  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)
  const combinedSignal = signal || controller.signal

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: combinedSignal,
    })
    clearTimeout(timer)

    if (!response.ok) {
      return {
        isOnline: false,
        status: response.status,
        error: `Backend returned HTTP ${response.status}`,
      }
    }

    const data = await response.json()
    return { isOnline: true, status: response.status, data }
  } catch (err) {
    clearTimeout(timer)
    return {
      isOnline: false,
      status: 0,
      error: err.name === 'AbortError' ? 'Health check timed out' : err.message,
    }
  }
}

/**
 * Submits a Text-to-3D generation request to POST /api/v1/generations.
 *
 * @param {Object} params
 * @param {string} params.prompt - Natural language description (1–1000 characters).
 * @param {string} [params.outputFormat='glb'] - Target 3D format ('glb' or 'obj').
 * @param {AbortSignal} [params.signal] - Optional abort signal for cancellation.
 * @returns {Promise<Object>} Backend generation job response or throws typed error.
 */
export async function submitGeneration({ prompt, outputFormat = OutputFormat.GLB, signal }) {
  // 1. Client-side validation against backend constraints
  const validation = validatePrompt(prompt)
  if (!validation.valid) {
    throw new ValidationError(validation.error)
  }

  // 2. Format validation
  const normalizedFormat = String(outputFormat).toLowerCase()
  if (normalizedFormat !== OutputFormat.OBJ && normalizedFormat !== OutputFormat.GLB) {
    throw new ValidationError(
      `Unsupported output format '${outputFormat}'. Must be 'glb' or 'obj'.`
    )
  }

  const payload = {
    prompt: validation.sanitized,
    output_format: normalizedFormat,
  }

  const baseUrl = getApiBaseUrl()
  const targetUrl = `${baseUrl}/api/v1/generations`

  let response
  try {
    response = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError') {
      throw err
    }
    throw new NetworkError(err, targetUrl || 'http://127.0.0.1:8000')
  }

  // Handle Response Status Codes
  if (response.status === 503) {
    let detailMsg = 'Text-to-3D generation engine is not yet integrated.'
    try {
      const errorJson = await response.json()
      if (errorJson?.detail) detailMsg = errorJson.detail
    } catch {
      // Use default message
    }
    throw new ServiceUnavailableError(detailMsg, 503)
  }

  if (response.status === 422) {
    let errorDetail = 'Validation error'
    try {
      const errorJson = await response.json()
      errorDetail = errorJson.detail || errorDetail
    } catch {
      // Use default
    }
    throw new ValidationError(errorDetail, 422)
  }

  if (!response.ok) {
    let errorMsg = `Server error (HTTP ${response.status})`
    try {
      const errorJson = await response.json()
      if (errorJson.detail) errorMsg = errorJson.detail
    } catch {
      // Use default
    }
    throw new GenerationApiError(errorMsg, response.status)
  }

  // HTTP 200/201/202 (Future Day 6+ behavior)
  try {
    const data = await response.json()
    return data
  } catch (err) {
    throw new GenerationApiError('Invalid JSON response returned by backend.', response.status)
  }
}

/**
 * Retrieves the status of an ongoing generation job.
 * Note: Status endpoint (GET /api/v1/generations/{id}) is scheduled for future backend Day 6+.
 */
export async function getGenerationStatus(jobId, options = {}) {
  const { signal } = options
  const baseUrl = getApiBaseUrl()
  const targetUrl = `${baseUrl}/api/v1/generations/${jobId}`

  try {
    const response = await fetch(targetUrl, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal,
    })

    if (response.status === 404 || response.status === 501 || response.status === 503) {
      return {
        available: false,
        status: response.status,
        message: 'Generation status endpoint is not yet mounted on backend.',
      }
    }

    if (!response.ok) {
      throw new GenerationApiError(`Failed to fetch job status (HTTP ${response.status})`, response.status)
    }

    const data = await response.json()
    return { available: true, data }
  } catch (err) {
    if (err.name === 'AbortError') throw err
    return {
      available: false,
      error: err.message,
      message: 'Status endpoint unreachable.',
    }
  }
}

/**
 * Simulated Generation Pipeline for offline and UI demonstration.
 *
 * Emits strictly backend-supported GenerationJobStatus values:
 * pending -> processing -> completed
 *
 * Clearly marked with is_mock: true to ensure full transparency.
 */
export function simulateMockGeneration({
  prompt,
  outputFormat = OutputFormat.GLB,
  onStatusChange,
  signal,
}) {
  return new Promise((resolve, reject) => {
    const validation = validatePrompt(prompt)
    if (!validation.valid) {
      reject(new ValidationError(validation.error))
      return
    }

    const jobId =
      typeof crypto !== 'undefined' && crypto.randomUUID
        ? crypto.randomUUID()
        : '550e8400-e29b-41d4-a716-' + Math.random().toString(36).substring(2, 10)

    const now = new Date().toISOString()
    const jobState = {
      job_id: jobId,
      prompt: validation.sanitized,
      output_format: outputFormat.toLowerCase(),
      status: GenerationJobStatus.PENDING,
      created_at: now,
      updated_at: now,
      error_message: null,
      is_mock: true,
      model_url:
        outputFormat.toLowerCase() === 'obj'
          ? '/models/sample-crystal.obj'
          : '/models/sample-crystal.obj',
    }

    if (signal?.aborted) {
      reject(new DOMException('Simulation aborted', 'AbortError'))
      return
    }

    // 1. Initial pending state
    if (onStatusChange) onStatusChange({ ...jobState })

    // 2. Transition to processing after 1.2s
    const timer1 = setTimeout(() => {
      if (signal?.aborted) return
      jobState.status = GenerationJobStatus.PROCESSING
      jobState.updated_at = new Date().toISOString()
      if (onStatusChange) onStatusChange({ ...jobState })

      // 3. Transition to completed after 2.0s
      const timer2 = setTimeout(() => {
        if (signal?.aborted) return
        jobState.status = GenerationJobStatus.COMPLETED
        jobState.updated_at = new Date().toISOString()
        if (onStatusChange) onStatusChange({ ...jobState })
        resolve(jobState)
      }, 2000)

      if (signal) {
        signal.addEventListener('abort', () => clearTimeout(timer2))
      }
    }, 1200)

    if (signal) {
      signal.addEventListener('abort', () => {
        clearTimeout(timer1)
        reject(new DOMException('Simulation aborted', 'AbortError'))
      })
    }
  })
}
