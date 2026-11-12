/**
 * MOCK DATA – for UI development only.
 * Replace with real API calls when backend endpoints are ready.
 * All data marked with [MOCK] should be fetched from /api/* endpoints.
 */

// [MOCK] Dashboard statistics
export const mockStats = [
  {
    id: 'total_generations',
    label: 'Total Generations',
    value: '1,284',
    change: '+12%',
    changeType: 'positive',
    icon: 'Layers',
    color: 'purple',
  },
  {
    id: 'completed_models',
    label: 'Completed Models',
    value: '1,106',
    change: '+8%',
    changeType: 'positive',
    icon: 'CheckCircle',
    color: 'green',
  },
  {
    id: 'processing_jobs',
    label: 'Processing Jobs',
    value: '7',
    change: '2 queued',
    changeType: 'neutral',
    icon: 'Loader',
    color: 'yellow',
  },
  {
    id: 'saved_assets',
    label: 'Saved Assets',
    value: '342',
    change: '+24 this week',
    changeType: 'positive',
    icon: 'Archive',
    color: 'blue',
  },
]

// [MOCK] Recent generated assets
export const mockRecentAssets = [
  {
    id: 'asset-001',
    name: 'Medieval Castle',
    prompt: 'A weathered medieval castle with stone walls, towers, and a drawbridge...',
    status: 'completed',
    createdAt: '2026-11-11T18:30:00Z',
    thumbnailColor: '#7c5cfc',
    format: 'GLB',
    polygons: '12.4K',
  },
  {
    id: 'asset-002',
    name: 'Futuristic Spaceship',
    prompt: 'Sleek futuristic spaceship with glowing engines and angular hull...',
    status: 'completed',
    createdAt: '2026-11-11T16:15:00Z',
    thumbnailColor: '#5b8def',
    format: 'OBJ',
    polygons: '8.2K',
  },
  {
    id: 'asset-003',
    name: 'Ancient Dragon',
    prompt: 'Massive ancient dragon with detailed scales, wings, and fierce expression...',
    status: 'processing',
    createdAt: '2026-11-11T20:00:00Z',
    thumbnailColor: '#f59e0b',
    format: 'GLB',
    polygons: '—',
  },
  {
    id: 'asset-004',
    name: 'Forest Cottage',
    prompt: 'Cozy forest cottage with moss-covered roof, wooden beams, and chimney...',
    status: 'completed',
    createdAt: '2026-11-10T14:00:00Z',
    thumbnailColor: '#22c55e',
    format: 'FBX',
    polygons: '5.7K',
  },
  {
    id: 'asset-005',
    name: 'Crystal Sword',
    prompt: 'Enchanted crystal sword with blue glow and ornate handle...',
    status: 'failed',
    createdAt: '2026-11-10T11:30:00Z',
    thumbnailColor: '#ef4444',
    format: '—',
    polygons: '—',
  },
  {
    id: 'asset-006',
    name: 'Alien Planet',
    prompt: 'Alien planet surface with towering rock formations and two moons...',
    status: 'completed',
    createdAt: '2026-11-09T09:45:00Z',
    thumbnailColor: '#38bdf8',
    format: 'GLB',
    polygons: '21.3K',
  },
]

// [MOCK] Example prompt suggestions
export const promptSuggestions = [
  'A detailed Viking longship with dragon prow and oars',
  'Futuristic robot with glowing blue eyes and mechanical joints',
  'Ancient Egyptian temple with hieroglyphs and sandstone columns',
  'Steampunk airship with propellers, gears, and brass fittings',
  'Fantasy mushroom house in an enchanted forest',
  'Modern sports car with sleek aerodynamic body and LED lights',
]

// [MOCK] Generation history
export const mockHistory = [
  ...mockRecentAssets,
  {
    id: 'asset-007',
    name: 'Samurai Armor',
    prompt: 'Traditional Japanese samurai armor with intricate detail...',
    status: 'completed',
    createdAt: '2026-11-08T15:20:00Z',
    thumbnailColor: '#7c5cfc',
    format: 'OBJ',
    polygons: '14.1K',
  },
  {
    id: 'asset-008',
    name: 'Tropical Island',
    prompt: 'Small tropical island with palm trees, sandy beach and coral reef...',
    status: 'completed',
    createdAt: '2026-11-07T10:00:00Z',
    thumbnailColor: '#22c55e',
    format: 'GLB',
    polygons: '32.6K',
  },
]

// [MOCK] Templates
export const mockTemplates = [
  { id: 'tpl-001', name: 'Game Character', category: 'Characters', description: 'Optimized for real-time game engines with low poly count.', uses: 892 },
  { id: 'tpl-002', name: 'Architectural Viz', category: 'Architecture', description: 'High detail for architectural visualization projects.', uses: 456 },
  { id: 'tpl-003', name: 'Product Mockup', category: 'Products', description: 'Clean and commercial product visualization style.', uses: 1204 },
  { id: 'tpl-004', name: 'VFX Asset', category: 'Visual Effects', description: 'Optimized for visual effects and film production pipelines.', uses: 319 },
  { id: 'tpl-005', name: 'Nature & Terrain', category: 'Environments', description: 'Procedural terrain and organic nature elements.', uses: 677 },
  { id: 'tpl-006', name: 'Sci-Fi Prop', category: 'Props', description: 'Hard surface sci-fi props with PBR materials.', uses: 541 },
]
