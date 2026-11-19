import { useState, useRef, useCallback, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, ContactShadows } from '@react-three/drei'
import ModelLoader from './ModelLoader.jsx'
import ViewerControls from './ViewerControls.jsx'
import { ViewerEmptyState, ViewerErrorState, ViewerLoadingState } from './ViewerFallback.jsx'
import './ModelViewer.css'

const CAMERA_PRESETS = {
  reset: [3.5, 2.5, 4.5],
  fit: [2.8, 2.0, 3.6],
  front: [0, 0, 5.5],
  side: [5.5, 0, 0],
  top: [0, 6.0, 0.001],
  iso: [4.2, 3.2, 4.2],
}

function SceneContent({
  modelUrl,
  textureUrl,
  showTexture,
  wireframe,
  showGrid,
  lightingPreset,
  onModelLoaded,
  onModelError,
  onModelProgress,
  onTextureStatus,
  controlsRef,
}) {
  return (
    <>
      {/* ── Lighting Presets (Task 1: Studio, Soft, Default) ── */}
      {lightingPreset === 'studio' ? (
        <>
          <ambientLight intensity={0.35} color="#c7d2fe" />
          <directionalLight
            position={[7, 9, 6]}
            intensity={1.8}
            color="#ffffff"
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
          />
          <directionalLight position={[-5, 6, -6]} intensity={1.2} color="#a5b4fc" />
          <directionalLight position={[-6, 2, 4]} intensity={0.4} color="#60a5fa" />
          <directionalLight position={[0, -3, 0]} intensity={0.2} />
        </>
      ) : lightingPreset === 'soft' ? (
        <>
          <ambientLight intensity={0.95} color="#f8fafc" />
          <directionalLight position={[4, 6, 4]} intensity={0.6} color="#fed7aa" />
          <directionalLight position={[-4, 4, -4]} intensity={0.5} color="#e0e7ff" />
          <directionalLight position={[0, 5, 0]} intensity={0.4} />
        </>
      ) : (
        /* Default Balanced Lighting */
        <>
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
        </>
      )}

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
  generationId = null,
  assetName = null,
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

  // Viewport Settings (Task 1)
  const [showGrid, setShowGrid] = useState(true)
  const [wireframe, setWireframe] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [lightingPreset, setLightingPreset] = useState('default') // 'default' | 'studio' | 'soft'
  const [backgroundPreset, setBackgroundPreset] = useState('nebula') // 'nebula' | 'studio' | 'black' | 'cyber'

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

  // Camera Preset Controls (Task 1: Reset, Fit, Front, Side, Top, Iso)
  const handleSetCameraView = useCallback((presetKey) => {
    if (!controlsRef.current) return
    const controls = controlsRef.current
    const targetPos = CAMERA_PRESETS[presetKey] || CAMERA_PRESETS.reset
    const camera = controls.object

    if (camera) {
      camera.position.set(...targetPos)
      camera.lookAt(0, 0, 0)
    }
    controls.target.set(0, 0, 0)
    controls.update()
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
    const reloadUrl = currentUrl
    setCurrentUrl('')
    setTimeout(() => setCurrentUrl(reloadUrl), 50)
  }, [currentUrl])

  return (
    <div
      ref={containerRef}
      className={`model-viewer-container viewer-bg-${backgroundPreset} ${
        isFullscreen ? 'model-viewer-fullscreen' : ''
      } ${className}`}
      style={{ height: isFullscreen ? '100vh' : height }}
    >
      {/* ── 3D WebGL Canvas ── */}
      <div className="viewer-canvas-wrapper">
        <Canvas
          camera={{ position: CAMERA_PRESETS.reset, fov: 45, near: 0.1, far: 1000 }}
          dpr={[1, 2]}
          gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
        >
          <SceneContent
            modelUrl={currentUrl}
            textureUrl={currentTextureUrl}
            showTexture={showTexture}
            wireframe={wireframe}
            showGrid={showGrid}
            lightingPreset={lightingPreset}
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

      {/* ── Toolbar & Top Controls (Task 1 & Task 2) ── */}
      <ViewerControls
        onSetCameraView={handleSetCameraView}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        showGrid={showGrid}
        onToggleGrid={() => setShowGrid((v) => !v)}
        wireframe={wireframe}
        onToggleWireframe={() => setWireframe((v) => !v)}
        showTexture={showTexture}
        onToggleTexture={() => setShowTexture((v) => !v)}
        textureStatus={textureStatus}
        lightingPreset={lightingPreset}
        onSelectLighting={setLightingPreset}
        backgroundPreset={backgroundPreset}
        onSelectBackground={setBackgroundPreset}
        isFullscreen={isFullscreen}
        onToggleFullscreen={handleToggleFullscreen}
        modelStats={modelStats}
        currentModelUrl={currentUrl}
        generationId={generationId}
        assetName={assetName}
        onSelectModel={handleSelectModel}
      />

      {/* Navigation Hint */}
      <div className="viewer-instructions-hint" aria-hidden="true">
        <span>Rotate: Left Click | Pan: Right Click | Zoom: Scroll</span>
      </div>
    </div>
  )
}

export default ModelViewer
