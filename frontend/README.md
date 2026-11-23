# PolyGen â€” Frontend Dashboard & Interactive 3D Viewer

A modern, production-grade AI SaaS web application for **PolyGen (Generative Text-to-3D Asset Pipeline)**. This module provides a responsive web interface allowing creators, game developers, and 3D technical artists to synthesize, inspect, manage, and download high-fidelity 3D assets from natural language prompts.

---

## 1. Module Overview & Role

- **Module**: Frontend Dashboard & Interactive 3D Viewer
- **Owner / Lead**: Samiksha Patil (Frontend & 3D Viewer Lead)
- **Assigned Git Branch**: `feature/frontend-viewer`
- **Upstream Repository**: [PolyGen-Generative-Text-to-3D-Asset-Pipeline](https://github.com/prabath-ux05/PolyGen-Generative-Text-to-3D-Asset-Pipeline)

The frontend interfaces directly with the FastAPI backend orchestration layer (`backend/app/api/routes/generations.py`), adhering to agreed request/response contracts and providing seamless fallback mechanisms during backend service integration phases.

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | [React](https://react.dev/) | `^18.3.1` | Component-based UI architecture |
| **Build Tool** | [Vite](https://vitejs.dev/) | `^5.3.1` | Ultra-fast HMR and optimized production bundling |
| **3D Rendering** | [Three.js](https://threejs.org/) | `^0.187.0` | Low-level WebGL graphics engine |
| **3D React Fiber** | [@react-three/fiber](https://r3f.docs.pmnd.rs/) | `^8.18.0` | Declarative Three.js scene graph in React |
| **3D Helpers** | [@react-three/drei](https://github.com/pmndrs/drei) | `^9.123.0` | Orbit controls, loaders, contact shadows, environment |
| **Icons** | [Lucide React](https://lucide.dev/) | `^0.395.0` | Consistent, accessible modern SVG icon set |
| **Routing** | [React Router DOM](https://reactrouter.com/) | `^6.23.1` | Client-side page navigation and deep-linking |
| **Unit Testing** | [Vitest](https://vitest.dev/) | `^1.6.1` | High-performance unit testing framework |
| **DOM Testing** | [@testing-library/react](https://testing-library.com/) | `^16.3.2` | Component user-interaction testing in jsdom |
| **Linting** | [ESLint](https://eslint.org/) | `^8.57.0` | Code quality and React hooks static analysis |

---

## 3. Getting Started & Installation

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher

### Quick Start
```bash
# 1. Navigate to the frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Launch local development server
npm run dev
```

The application will be live at `http://localhost:5173/`.

### Development Scripts
| Command | Action |
| :--- | :--- |
| `npm run dev` | Starts Vite dev server with Hot Module Replacement (HMR) |
| `npm run build` | Compiles and minifies production assets into `dist/` |
| `npm run preview` | Previews the production build locally |
| `npm run lint` | Runs ESLint across all `.js` and `.jsx` source files (0 errors / 0 warnings required) |
| `npm test` | Runs the automated Vitest test suite in CI/headless mode |

---

## 4. Environment Variables

Create a `.env` file in the `frontend/` directory (or use `.env.local` for local development):

```env
# URL pointing to the FastAPI backend API service
VITE_API_BASE_URL=http://localhost:8000
```

> **Note**: Do not commit `.env` or `.env.local` files containing private credentials or machine-specific network addresses. An example configuration template is maintained in `frontend/.env.example`.

---

## 5. Folder Structure & Architecture

```
frontend/
â”œâ”€â”€ public/
â”‚   â”œâ”€â”€ models/                   # Local sample 3D test assets (OBJ & GLB)
â”‚   â””â”€â”€ textures/                 # Sample PBR diffuse textures
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ components/               # Modular, reusable UI components
â”‚   â”‚   â”œâ”€â”€ EmptyState/           # Fallback and empty state cards
â”‚   â”‚   â”œâ”€â”€ GenerationStatus/     # Lifecycle status banner (Pending, Processing, 503, Completed)
â”‚   â”‚   â”œâ”€â”€ ModelViewer/          # 3D Canvas, ModelLoader, ViewerControls, Fallback states
â”‚   â”‚   â”œâ”€â”€ Navbar/               # Top header with search, auth controls, notifications
â”‚   â”‚   â”œâ”€â”€ PromptInput/          # Natural language prompt textarea, suggestions, format toggle
â”‚   â”‚   â”œâ”€â”€ RecentAssets/         # Dashboard recent generation cards
â”‚   â”‚   â”œâ”€â”€ Sidebar/              # Left navigation rail with active page highlights
â”‚   â”‚   â”œâ”€â”€ StatsCard/            # Overview metric summary cards
â”‚   â”‚   â””â”€â”€ Toast/                # Global toast notifications
â”‚   â”œâ”€â”€ context/                  # React state providers
â”‚   â”‚   â”œâ”€â”€ AssetContext.jsx      # Asset collection, filtering, rename, delete actions
â”‚   â”‚   â”œâ”€â”€ AuthContext.jsx       # User profile session & demo authentication mode
â”‚   â”‚   â””â”€â”€ ToastContext.jsx      # Non-blocking user notification dispatcher
â”‚   â”œâ”€â”€ data/                     # Mock data dictionaries and default assets
â”‚   â”œâ”€â”€ pages/                    # Main application route views
â”‚   â”‚   â”œâ”€â”€ Auth/                 # Login & SignUp pages with full client validation
â”‚   â”‚   â”œâ”€â”€ CreateModel/          # Dedicated 3D generation studio & viewport
â”‚   â”‚   â”œâ”€â”€ Dashboard/            # SaaS dashboard overview with prompt bar & recent assets
â”‚   â”‚   â”œâ”€â”€ GenerationHistory/    # Historical task log
â”‚   â”‚   â”œâ”€â”€ HelpSupport/          # API docs & support FAQ
â”‚   â”‚   â”œâ”€â”€ MyAssets/             # Asset library with search, filter, grid/list view, modal inspection
â”‚   â”‚   â”œâ”€â”€ Settings/             # Pipeline preferences & API keys
â”‚   â”‚   â””â”€â”€ Templates/            # Starter prompt inspiration library
â”‚   â”œâ”€â”€ services/
â”‚   â”‚   â””â”€â”€ generationService.js  # FastAPI client, HTTP error handling, polling, simulation
â”‚   â”œâ”€â”€ styles/                   # Design system variables, dark theme tokens, layout CSS
â”‚   â”œâ”€â”€ test/                     # Automated Vitest test suite
â”‚   â”‚   â”œâ”€â”€ setup.js              # jsdom environment setup & WebGL/ResizeObserver mocks
â”‚   â”‚   â”œâ”€â”€ AssetManagement.test.jsx
â”‚   â”‚   â”œâ”€â”€ AuthValidation.test.jsx
â”‚   â”‚   â”œâ”€â”€ Dashboard.test.jsx
â”‚   â”‚   â”œâ”€â”€ GenerationStatus.test.jsx
â”‚   â”‚   â”œâ”€â”€ PromptValidation.test.jsx
â”‚   â”‚   â””â”€â”€ ViewerFallback.test.jsx
â”‚   â”œâ”€â”€ App.jsx                   # Application route configuration
â”‚   â””â”€â”€ main.jsx                  # Application root entry point
â”œâ”€â”€ package.json
â”œâ”€â”€ vite.config.js
â””â”€â”€ README.md
```

---

## 6. Key Features & Capabilities

### 6.1 Interactive 3D Model Viewer (`ModelViewer.jsx`)
- **Multi-Format Support**: Dedicated loaders for both **Wavefront OBJ** (`OBJLoader`) and **GLTF/GLB** (`useGLTF` / `GLTFLoader`).
- **Automated Framing**: Dynamically computes 3D bounding boxes (`Box3`), centers geometries around scene origin `(0, 0, 0)`, and normalizes scale to fit the camera frustum without manual repositioning.
- **Advanced Camera Controls**: Smooth orbit controls (Rotate, Zoom, Pan) with 6 quick-angle presets:
  - Default / Reset (`[3.5, 2.5, 4.5]`)
  - Fit to View (`[2.8, 2.0, 3.6]`)
  - Front View (`[0, 0, 5.5]`)
  - Side Profile (`[5.5, 0, 0]`)
  - Top View (`[0, 6.0, 0.001]`)
  - Isometric View (`[4.2, 3.2, 4.2]`)
- **Lighting Presets**: Studio Lighting (accent rims), Soft Diffuse, and Default Directional with soft contact shadows.
- **Shading Modes**: One-click toggles between **PBR Textured**, **Untextured Clay**, and **Wireframe Overlay**.
- **Viewport Backgrounds**: Seamless toggles between Studio Dark (`#0e1118`), Neutral Slate (`#1e293b`), and Deep Void (`#050810`).
- **Native Fullscreen**: Expands the WebGL Canvas into full-screen immersive mode with esc-key detection.
- **Model Inspector Panel**: Displays live geometry analytics including vertices, polygon faces, physical bounding dimensions ($X \times Y \times Z$), and topology manifold verification.

### 6.2 Prompt Pipeline & Generation Lifecycle (`generationService.js`)
- **Natural Language Input**: Character limits enforced (1â€“1000 characters) with real-time counter, quick example pills, and keyboard shortcuts (`Ctrl + Enter`).
- **Backend Lifecycle Integration**:
  - `POST /api/v1/generations`: Submits `prompt` and `output_format` (returns `HTTP 202 Accepted` with `GenerationJobResponse`).
  - `GET /api/v1/generations/{job_id}`: Polls task progress (`pending` â†’ `processing` â†’ `completed` / `failed`).
  - `GET /api/v1/generations/{job_id}/asset`: Retrieves live binary GLB mesh asset.
- **FastAPI HTTP 503 Engine Handling**: Gracefully handles backend responses when the generation engine is unintegrated, clearly informing users while offering a simulated pipeline demonstration mode to preview full lifecycle transitions.

### 6.3 Asset Management Library (`MyAssets.jsx`)
- **Live Search & Filter**: Real-time query search across asset names and prompt texts.
- **Multi-Facet Filtering**: Filter by generation status (`all`, `completed`, `processing`, `failed`), format (`GLB`, `OBJ`, `FBX`), and texture mode (`Textured`, `Clay`).
- **Flexible Presentation**: One-click toggle between responsive card grid and tabular list views.
- **Asset Operations**: Open in 3D Viewer, View Full Technical Specifications Modal, Download Model file, Rename Asset, and Delete Asset with modal confirmations.

### 6.4 Authentication UI (`Auth/`)
- **Sign In & Sign Up Views**: Form validation with real-time feedback, email format checks, password strength analyzer (evaluating length, casing, numbers, and special symbols), password match validation, and terms confirmation.
- **Clear Demo Notice**: Explicit UI indicators inform users that authentication currently operates in frontend session mode pending backend OAuth service integration.

---

## 7. Automated Test Suite

The frontend includes a comprehensive Vitest unit test suite covering 100% of critical paths across validation, UI states, and fallback handling.

```bash
# Run all tests
npm test

# Run tests with interactive UI (if vitest ui is installed)
npm test -- --ui

# Run specific test file
npm test -- run src/test/PromptValidation.test.jsx
```

### Test Coverage Summary:
| Test Suite | Tests | Scope Verified |
| :--- | :---: | :--- |
| `PromptValidation.test.jsx` | 8 | Empty prompt rejection, length validation (1â€“1000 chars), whitespace trimming, suggestion selection, format toggle, disabled state during generation. |
| `AuthValidation.test.jsx` | 8 | Login required fields, email regex validation, password length, visibility toggle, SignUp required fields, password strength scoring (Weak â†’ Strong), password confirmation match. |
| `GenerationStatus.test.jsx` | 7 | Null safety, pending status with indeterminate activity bar, processing status, completed state with 3D viewer launch button, failed state with error message & retry, 503 notice banner & simulation trigger, dismiss callback. |
| `ViewerFallback.test.jsx` | 6 | Empty viewport card with sample buttons, sample crystal/chair selection callbacks, error state card with custom message, retry callback, loading card with dynamic progress percentage. |
| `AssetManagement.test.jsx` | 6 | Asset card rendering, search query filtering by name & prompt, empty search result state, grid vs list view toggling, format pill filtering (GLB vs OBJ), modal inspection dialog launch. |
| `Dashboard.test.jsx` | 4 | Hero title rendering, statistics metrics cards, prompt input integration with mock 3D viewport, recent assets gallery rendering. |
| **Total** | **39** | **100% Pass Rate (0 failures)** |

---

## 8. Git Branching & Contribution Protocol

To ensure clean coordination across the PolyGen repository:
- All frontend changes must be committed to the assigned branch: `feature/frontend-viewer`.
- Do not commit directly to `main`.
- Exclude `node_modules/`, `dist/`, `.env`, and OS generated files (`.DS_Store`, `Thumbs.db`).
- All commits follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
  - `feat(frontend): ...` for new features
  - `fix(frontend): ...` for bug fixes
  - `test(frontend): ...` for test suite additions
  - `docs(frontend): ...` for documentation updates
