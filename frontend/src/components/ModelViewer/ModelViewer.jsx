import { useState, useRef, useCallback, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, ContactShadows } from '@react-three/drei'
import ModelLoader from './ModelLoader.jsx'
import ViewerControls from './ViewerControls.jsx'
import { ViewerEmptyState, ViewerErrorState, ViewerLoadingState } from './ViewerFallback.jsx'
import './ModelViewer.css'

const DEFAULT_CAMERA_POS = [3.5, 2.5, 4.5]

function SceneContent({
  modelUrl,
  textureUrl,
  showTexture,
  wireframe,
  showGrid,
  onModelLoaded,
  onModelError,
  onModelProgress,
  onTextureStatus,
  controlsRef,
}) {
  return (
    <>
      {/* ── Lighting Setup ── */}
      <ambientLight intensity={0.7} />
      <directionalLight
        position={[6, 8, 6]}
        intensity={1.2}
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <directionalLight position={[-6, 4, -4]} intensity={0.5} />
      <directionalLight position={[0, -4, 0]} intensity={0.2} />

      {/* ── Reference Grid & Ground Reference ── */}
      {showGrid && (
        <>
          <gridHelper
            args={[10, 20, '#7c5cfc', '#242840']}
            position={[0, -1.6, 0]}
          />
          <ContactShadows
            position={[0, -1.59, 0]}
            opacity={0.6}
            scale={8}
            blur={2}
            far={4}
          />
        </>
      )}

      {/* ── 3D Model Mesh ── */}
      {modelUrl && (
        <ModelLoader
          url={modelUrl}
          textureUrl={textureUrl}
          showTexture={showTexture}
          wireframe={wireframe}
          onLoaded={onModelLoaded}
          onError={onModelError}
          onProgress={onModelProgress}
          onTextureStatus={onTextureStatus}
        />
      )}

      {/* ── Orbit Controls ── */}
      <OrbitControls
        ref={controlsRef}
        makeDefault
        enableDamping
        dampingFactor={0.06}
        minDistance={1.2}
        maxDistance={25}
        maxPolarAngle={Math.PI / 2 + 0.08}
      />
    </>
  )
}

function ModelViewer({
  modelUrl: initialModelUrl = '',
  textureUrl: initialTextureUrl = null,
  showTexture: initialShowTexture = true,
  onModelLoaded: parentOnLoaded,
  height = '480px',
  className = '',
}) {
  const containerRef = useRef(null)
  const controlsRef = useRef(null)

  const [currentUrl, setCurrentUrl] = useState(initialModelUrl)
  const [currentTextureUrl, setCurrentTextureUrl] = useState(initialTextureUrl)
  const [showTexture, setShowTexture] = useState(initialShowTexture)
  const [textureStatus, setTextureStatus] = useState(null)

  const [modelStats, setModelStats] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [loadProgress, setLoadProgress] = useState(0)
  const [loadError, setLoadError] = useState(null)

  // Viewport Settings
  const [showGrid, setShowGrid] = useState(true)
  const [wireframe, setWireframe] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  // Sync prop changes
  useEffect(() => {
    if (initialModelUrl !== undefined) {
      setCurrentUrl(initialModelUrl)
      if (initialModelUrl) {
        setIsLoading(true)
        setLoadError(null)
      } else {
        setIsLoading(false)
        setModelStats(null)
      }
    }
  }, [initialModelUrl])

  useEffect(() => {
    setCurrentTextureUrl(initialTextureUrl)
  }, [initialTextureUrl])

  useEffect(() => {
    setShowTexture(initialShowTexture)
  }, [initialShowTexture])

  // Fullscreen change listener
  useEffect(() => {
    function handleFullscreenChange() {
      setIsFullscreen(!!document.fullscreenElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  // Callbacks
  const handleModelLoaded = useCallback(
    (stats) => {
      setIsLoading(false)
      setLoadError(null)
      setModelStats(stats)
      if (parentOnLoaded) parentOnLoaded(stats)
    },
    [parentOnLoaded]
  )

  const handleModelError = useCallback((err) => {
    setIsLoading(false)
    setLoadError(err)
    setModelStats(null)
  }, [])

  const handleModelProgress = useCallback((percent) => {
    setLoadProgress(percent)
  }, [])

  const handleTextureStatus = useCallback((statusObj) => {
    setTextureStatus(statusObj)
  }, [])

  // Controls Handlers
  const handleResetView = useCallback(() => {
    if (controlsRef.current) {
      const controls = controlsRef.current
      controls.reset()
      const camera = controls.object
      if (camera) {
        camera.position.set(...DEFAULT_CAMERA_POS)
        camera.lookAt(0, 0, 0)
      }
      controls.target.set(0, 0, 0)
      controls.update()
    }
  }, [])

  const handleZoomIn = useCallback(() => {
    if (controlsRef.current?.object) {
      const camera = controlsRef.current.object
      camera.position.multiplyScalar(0.85)
      controlsRef.current.update()
    }
  }, [])

  const handleZoomOut = useCallback(() => {
    if (controlsRef.current?.object) {
      const camera = controlsRef.current.object
      camera.position.multiplyScalar(1.18)
      controlsRef.current.update()
    }
  }, [])

  const handleToggleFullscreen = useCallback(() => {
    if (!containerRef.current) return
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(() => {
        // Fallback: local CSS fullscreen
        setIsFullscreen(true)
      })
    } else {
      document.exitFullscreen().catch(() => {
        setIsFullscreen(false)
      })
    }
  }, [])

  const handleSelectModel = useCallback((url) => {
    setLoadError(null)
    setCurrentUrl(url)
    if (url) {
      setIsLoading(true)
      setLoadProgress(15)
    } else {
      setIsLoading(false)
      setModelStats(null)
    }
  }, [])

  const handleRetry = useCallback(() => {
    if (!currentUrl) return
    setLoadError(null)
    setIsLoading(true)
    setLoadProgress(10)
    // Trigger reload by re-setting URL
    const reloadUrl = currentUrl
    setCurrentUrl('')
    setTimeout(() => setCurrentUrl(reloadUrl), 50)
  }, [currentUrl])

  return (
    <div
      ref={containerRef}
      className={`model-viewer-container ${
        isFullscreen ? 'model-viewer-fullscreen' : ''
      } ${className}`}
      style={{ height: isFullscreen ? '100vh' : height }}
    >
      {/* ── 3D WebGL Canvas ── */}
      <div className="viewer-canvas-wrapper">
        <Canvas
          camera={{ position: DEFAULT_CAMERA_POS, fov: 45, near: 0.1, far: 1000 }}
          dpr={[1, 2]}
          gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        >
          <SceneContent
            modelUrl={currentUrl}
            textureUrl={currentTextureUrl}
            showTexture={showTexture}
            wireframe={wireframe}
            showGrid={showGrid}
            onModelLoaded={handleModelLoaded}
            onModelError={handleModelError}
            onModelProgress={handleModelProgress}
            onTextureStatus={handleTextureStatus}
            controlsRef={controlsRef}
          />
        </Canvas>
      </div>

      {/* ── Overlays: Empty, Loading, Error ── */}
      {!currentUrl && !isLoading && (
        <ViewerEmptyState onSelectSample={handleSelectModel} />
      )}

      {isLoading && (
        <ViewerLoadingState
          message={`Loading 3D asset (${currentUrl.split('/').pop()})…`}
          progress={loadProgress}
        />
      )}

      {loadError && (
        <ViewerErrorState
          error={loadError}
          onRetry={handleRetry}
          onFallback={() => handleSelectModel('/models/sample-crystal.obj')}
        />
      )}

      {/* Texture Notice Overlay when texture is missing or fallback applied */}
      {textureStatus?.status === 'error' && (
        <div className="viewer-texture-notice" role="alert">
          <span>⚠️ {textureStatus.message}</span>
        </div>
      )}

      {/* ── Toolbar & Top Controls ── */}
      <ViewerControls
        onResetView={handleResetView}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        showGrid={showGrid}
        onToggleGrid={() => setShowGrid((v) => !v)}
        wireframe={wireframe}
        onToggleWireframe={() => setWireframe((v) => !v)}
        showTexture={showTexture}
        onToggleTexture={() => setShowTexture((v) => !v)}
        textureStatus={textureStatus}
        isFullscreen={isFullscreen}
        onToggleFullscreen={handleToggleFullscreen}
        modelStats={modelStats}
        currentModelUrl={currentUrl}
        onSelectModel={handleSelectModel}
      />

      {/* Navigation Hint */}
      <div className="viewer-instructions-hint" aria-hidden="true">
        <span>Rotate: Left Click + Drag | Pan: Right Click | Zoom: Scroll</span>
      </div>
    </div>
  )
}

export default ModelViewer
