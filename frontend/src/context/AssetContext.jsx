import { createContext, useContext, useState, useEffect } from 'react'

const AssetContext = createContext(null)

// Enriched assets matching Day 5 backend and mesh-processing contracts
const initialEnrichedAssets = [
  {
    id: 'asset-001',
    generationId: 'gen-202611-001',
    name: 'Medieval Castle',
    prompt: 'A weathered medieval castle with stone walls, towers, and a drawbridge in fantasy style',
    status: 'completed',
    createdAt: '2026-11-18T14:30:00Z',
    format: 'GLB',
    modelUrl: '/models/sample-crystal.obj',
    thumbnailColor: '#7c5cfc',
    meshMetadata: {
      vertices: 14280,
      faces: 24150,
      dimensions: { x: '4.20m', y: '5.10m', z: '3.80m' },
      polygonTarget: 25000,
      submeshes: 3,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: true,
      textureStatus: 'applied', // 'applied' | 'untextured' | 'missing' | 'generating'
      diffuseUrl: '/textures/crystal-diffuse.png',
      resolution: '2048 × 2048',
      textureMapType: 'Diffuse (Albedo PBR)',
      format: 'PNG',
    },
  },
  {
    id: 'asset-002',
    generationId: 'gen-202611-002',
    name: 'Futuristic Spaceship',
    prompt: 'Sleek futuristic spaceship with glowing engines, aerodynamic hull and cockpit details',
    status: 'completed',
    createdAt: '2026-11-18T12:15:00Z',
    format: 'OBJ',
    modelUrl: '/models/sample-chair.obj',
    thumbnailColor: '#5b8def',
    meshMetadata: {
      vertices: 8240,
      faces: 15600,
      dimensions: { x: '2.80m', y: '1.40m', z: '6.50m' },
      polygonTarget: 16000,
      submeshes: 2,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: true,
      textureStatus: 'applied',
      diffuseUrl: '/textures/chair-diffuse.png',
      resolution: '2048 × 2048',
      textureMapType: 'Diffuse (Albedo PBR)',
      format: 'PNG',
    },
  },
  {
    id: 'asset-003',
    generationId: 'gen-202611-003',
    name: 'Ancient Dragon',
    prompt: 'Massive ancient dragon with detailed scales, wings, horns, and coiled tail',
    status: 'processing',
    createdAt: '2026-11-18T16:00:00Z',
    format: 'GLB',
    modelUrl: null,
    thumbnailColor: '#f59e0b',
    meshMetadata: null, // Generation pending
    textureInfo: {
      hasTexture: false,
      textureStatus: 'generating',
      diffuseUrl: null,
      resolution: 'Pending',
      textureMapType: 'PBR Maps',
      format: '—',
    },
  },
  {
    id: 'asset-004',
    generationId: 'gen-202611-004',
    name: 'Forest Cottage',
    prompt: 'Cozy forest cottage with moss-covered stone roof, wooden chimney and porch',
    status: 'completed',
    createdAt: '2026-11-17T14:00:00Z',
    format: 'OBJ',
    modelUrl: '/models/sample-crystal.obj',
    thumbnailColor: '#22c55e',
    meshMetadata: {
      vertices: 5720,
      faces: 9840,
      dimensions: { x: '3.50m', y: '3.20m', z: '4.10m' },
      polygonTarget: 10000,
      submeshes: 1,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: true,
      textureStatus: 'missing', // Test case: Texture missing -> triggers error state & fallback material!
      diffuseUrl: '/textures/missing-texture.png',
      resolution: '1024 × 1024',
      textureMapType: 'Diffuse (Missing)',
      format: 'PNG',
    },
  },
  {
    id: 'asset-005',
    generationId: 'gen-202611-005',
    name: 'Crystal Sword',
    prompt: 'Enchanted crystal sword with glowing blue runes and ornate gold handle',
    status: 'failed',
    createdAt: '2026-11-17T11:30:00Z',
    format: '—',
    modelUrl: null,
    thumbnailColor: '#ef4444',
    meshMetadata: null,
    textureInfo: {
      hasTexture: false,
      textureStatus: 'missing',
      diffuseUrl: null,
      resolution: '—',
      textureMapType: '—',
      format: '—',
    },
    errorMessage: 'Geometry synthesis timed out after 120s (HTTP 504 Gateway Timeout).',
  },
  {
    id: 'asset-006',
    generationId: 'gen-202611-006',
    name: 'Alien Planet Monolith',
    prompt: 'Alien planet surface with towering crystalline rock formations and two moons',
    status: 'completed',
    createdAt: '2026-11-16T09:45:00Z',
    format: 'GLB',
    modelUrl: '/models/sample-crystal.obj',
    thumbnailColor: '#38bdf8',
    meshMetadata: {
      vertices: 21300,
      faces: 38200,
      dimensions: { x: '8.40m', y: '12.00m', z: '8.40m' },
      polygonTarget: 40000,
      submeshes: 4,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: false,
      textureStatus: 'untextured', // Test case: Explicitly untextured clay model
      diffuseUrl: null,
      resolution: 'Untextured',
      textureMapType: 'Procedural Clay',
      format: '—',
    },
  },
  {
    id: 'asset-007',
    generationId: 'gen-202611-007',
    name: 'Ergonomic Office Chair',
    prompt: 'A modern ergonomic office chair with breathable mesh back and caster wheels',
    status: 'completed',
    createdAt: '2026-11-15T15:20:00Z',
    format: 'OBJ',
    modelUrl: '/models/sample-chair.obj',
    thumbnailColor: '#a855f7',
    meshMetadata: {
      vertices: 7200,
      faces: 12400,
      dimensions: { x: '0.65m', y: '1.10m', z: '0.65m' },
      polygonTarget: 15000,
      submeshes: 2,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: true,
      textureStatus: 'applied',
      diffuseUrl: '/textures/chair-diffuse.png',
      resolution: '2048 × 2048',
      textureMapType: 'Diffuse (Fabric Weave)',
      format: 'PNG',
    },
  },
  {
    id: 'asset-008',
    generationId: 'gen-202611-008',
    name: 'Low-Poly Pine Tree',
    prompt: 'A stylized low-poly pine tree with autumn-colored foliage and wooden trunk',
    status: 'completed',
    createdAt: '2026-11-14T10:00:00Z',
    format: 'GLB',
    modelUrl: '/models/sample-crystal.obj',
    thumbnailColor: '#10b981',
    meshMetadata: {
      vertices: 3200,
      faces: 5400,
      dimensions: { x: '2.10m', y: '4.80m', z: '2.10m' },
      polygonTarget: 6000,
      submeshes: 1,
      topology: 'Watertight Manifold',
    },
    textureInfo: {
      hasTexture: true,
      textureStatus: 'applied',
      diffuseUrl: '/textures/crystal-diffuse.png',
      resolution: '2048 × 2048',
      textureMapType: 'Diffuse (Stylized)',
      format: 'PNG',
    },
  },
]

export function AssetProvider({ children }) {
  const [assets, setAssets] = useState(() => {
    try {
      const saved = localStorage.getItem('polygen_assets')
      if (saved) {
        return JSON.parse(saved)
      }
    } catch {
      // Fallback
    }
    return initialEnrichedAssets
  })

  useEffect(() => {
    try {
      localStorage.setItem('polygen_assets', JSON.stringify(assets))
    } catch {
      // Ignore storage errors
    }
  }, [assets])

  function deleteAsset(id) {
    setAssets((prev) => prev.filter((a) => a.id !== id))
  }

  function renameAsset(id, newName) {
    setAssets((prev) =>
      prev.map((a) => (a.id === id ? { ...a, name: newName.trim() } : a))
    )
  }

  function addAsset(newAsset) {
    setAssets((prev) => [newAsset, ...prev])
  }

  function resetToDefaults() {
    setAssets(initialEnrichedAssets)
  }

  function clearAllAssets() {
    setAssets([])
  }

  function getAssetById(id) {
    return assets.find((a) => a.id === id) || null
  }

  return (
    <AssetContext.Provider
      value={{
        assets,
        deleteAsset,
        renameAsset,
        addAsset,
        resetToDefaults,
        clearAllAssets,
        getAssetById,
      }}
    >
      {children}
    </AssetContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAssets() {
  const context = useContext(AssetContext)
  if (!context) {
    throw new Error('useAssets must be used within an AssetProvider')
  }
  return context
}
