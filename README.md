# PolyGen — Generative Text-to-3D Asset Pipeline

PolyGen is an end-to-end generative AI pipeline designed to convert natural language prompts into production-ready 3D assets complete with geometry, textures, and mesh optimization.

---

## 1. Problem Statement

Creating high-quality 3D assets for games, simulations, virtual reality, and digital media is traditionally a labor-intensive, multi-step process requiring specialized modeling, sculpting, UV unwrapping, and texturing skills. While generative AI has accelerated 2D media creation, automated text-to-3D generation remains fragmented, often producing dense meshes with poor topology, unoptimized UVs, or uncoordinated textures that cannot be directly integrated into real-time rendering engines.

PolyGen solves this bottleneck by providing a cohesive pipeline that translates descriptive text prompts into optimized, textured 3D models with production-friendly formats and clean topology.

---

## 2. Main Project Objectives

- **Automated Text-to-3D Generation**: Synthesize complete 3D meshes from natural language prompts.
- **PBR Texture Synthesis**: Generate and map realistic textures and materials corresponding to 3D geometry.
- **Mesh Post-Processing & Optimization**: Perform automated retopology, decimation, manifold checking, and UV unwrapping for game/real-time engine readiness.
- **Unified Pipeline Orchestration**: Coordinate microservices through a FastAPI backend and task management system.
- **Interactive Web Interface**: Provide a responsive dashboard with an interactive 3D viewer for asset preview, inspection, and export.

---

## 3. Core Modules & Team Allocation

| Module | Responsible | Scope & Responsibility | Status |
| :--- | :--- | :--- | :--- |
| **Backend & AI Pipeline Orchestration** | **Team Lead** | API gateway, pipeline orchestration, asset lifecycle, service integration, and storage. | In Progress (Day 1 Scaffold) |
| **Text-to-3D Generation Engine** | **Janvi** | Prompt processing, Shap-E model management and loading, generation pipeline, mesh validation, OBJ/GLB export, metadata, error handling, performance monitoring, configuration, and benchmarking. | Implemented (Days 1–10; 145 Tests Passed) |
| **Frontend & 3D Viewer** | **Samiksha** | Web dashboard, prompt submission interface, real-time status tracking, and 3D asset viewer. | Planned (Placeholder) |
| **Texture Engine & Mesh Processing** | **Jay** | PBR material synthesis, texture baking, retopology, mesh decimation, and format export. | Planned (Placeholder) |

> *Note: Janvi's Text-to-3D Generation Engine has been implemented and tested. The modules assigned to Samiksha and Jay remain scaffolded as initial placeholders and will be implemented in subsequent development phases.*

---

## 4. Initial Project Structure

```text
PolyGen/
│
├── backend/                      # Backend service (FastAPI)
│   ├── app/
│   │   ├── api/                  # API router definitions
│   │   ├── core/                 # Core configuration and settings
│   │   ├── schemas/              # Pydantic schemas / DTOs
│   │   ├── services/             # Pipeline orchestration & business logic
│   │   └── main.py               # FastAPI entrypoint & health endpoints
│   └── tests/                    # Backend automated test suite
│       └── test_health.py        # Health check & root API tests
│
├── ai_generation/                # Text-to-3D AI generation engine
│   ├── models/
│   │   └── model_loader.py       # Shap-E model loading
│   ├── __init__.py
│   ├── model_manager.py          # Model selection and device management
│   ├── prompt_processor.py       # Prompt validation and processing
│   ├── generator.py              # Complete generation workflow
│   ├── exporter.py               # OBJ and GLB mesh export
│   ├── generation_validator.py   # Generated mesh validation
│   ├── generation_metadata.py    # Generation metadata management
│   ├── performance_monitor.py    # Generation performance tracking
│   ├── error_handler.py          # Centralized error handling
│   ├── config.py                 # Generation configuration
│   └── benchmark.py              # Prompt benchmarking and reports
│
├── texture_engine/               # [Placeholder] PBR texture generation & baking
│
├── mesh_processing/              # [Placeholder] Retopology, decimation & UV unwrapping
│
├── frontend/                         # Web dashboard and interactive 3D asset viewer
│   ├── public/                       # Static public assets served directly
│   │   ├── models/                   # Sample 3D test assets (.obj)
│   │   └── textures/                 # Sample PBR diffuse textures (.png)
│   ├── src/                          # Application source code
│   │   ├── components/               # Modular, reusable UI components
│   │   │   ├── EmptyState/           # Fallback cards and empty gallery placeholder
│   │   │   ├── GenerationStatus/     # Pipeline lifecycle status panel (pending, processing, 503, completed, failed)
│   │   │   ├── ModelViewer/          # Interactive 3D WebGL viewport and controls
│   │   │   │   
│   │   │   │   
│   │   │   │   
│   │   │   │   
│   │   │   ├── Navbar/               # Top header with search, notifications & auth controls
│   │   │   ├── PromptInput/          # Prompt textarea, character counter, suggestions & format toggle
│   │   │   ├── RecentAssets/         # Dashboard recent generation preview cards
│   │   │   ├── Sidebar/              # Left navigation rail with active page highlights
│   │   │   ├── StatsCard/            # Generation overview metric summary cards
│   │   │   └── Toast/                # Floating notification toast component
│   │   ├── pages/                    # Application route views
│   │   │   ├── Auth/                 # Authentication pages (Login.jsx, SignUp.jsx) with validation
│   │   │   ├── CreateModel/          # Dedicated 3D model generation studio & workspace
│   │   │   ├── Dashboard/            # SaaS dashboard overview with prompt bar & 3D preview
│   │   │   ├── GenerationHistory/    # Historical log of generated 3D assets and jobs
│   │   │   ├── HelpSupport/          # API documentation, support & user FAQ
│   │   │   ├── MyAssets/             # Asset library with search, filtering, and view toggles
│   │   │   │   
│   │   │   ├── Settings/             # Generation preferences, formats & API configuration
│   │   │   └── Templates/            # Starter prompt inspiration & template cards
│   │   ├── services/                 # Backend API service integration
│   │   │   
│   │   ├── context/                  # React Context providers for global state & hooks (useAuth, useAssets, useToast)
│   │   │   
│   │   ├── data/                     # Mock data & sample presets
│   │   │
│   │   ├── styles/                   # Global style sheets & design tokens
│   │   │   
│   │   ├── test/                     # Automated Vitest test suite
│   │   │  
│   ├── .eslintrc.cjs                 # ESLint configuration for React & hooks
│   ├── index.html                    # Single-page HTML document entrypoint
│   ├── package.json                  # Frontend dependencies, scripts & metadata
│   ├── vite.config.js                # Vite build configuration & Vitest test runner setup
│   └── README.md                     # Frontend module architecture & setup documentation
│
├── shared/                       # Shared models, constants, and contracts
│   └── contracts/
│
├── generated_assets/             # Storage for generated pipeline assets (git-ignored)
│   ├── meshes/                   # Generated 3D geometries (.obj, .gltf, .glb)
│   └── textures/                 # Synthesized texture maps (diffuse, normal, roughness)
│
├── docs/                         # Architecture documentation & API specs
│   └── ai_generation_engine.md   # AI generation engine documentation
│
├── tests/                        # AI generation engine automated tests
│   ├── test_config.py
│   ├── test_benchmark.py
│   └── test_pipeline_e2e.py
│
├── .gitignore                    # Environment, cache, and large asset exclusions
├── README.md                     # Project documentation & setup instructions
└── requirements.txt              # Python project dependencies
```

---

## 5. Backend Setup Instructions

### Prerequisites
- Python 3.10+ (tested with Python 3.13)
- `pip` or virtual environment manager (`venv`)

### 1. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 6. How to Run the FastAPI Server

Start the local development server with auto-reload:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:
- **API Root**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 7. How to Run Tests

Execute the automated test suite with pytest:

```bash
pytest backend/tests
```

Or with verbose output:

```bash
pytest -v backend/tests
```

## AI Generation Engine

See [AI Generation Engine documentation](docs/ai_generation_engine.md) for configuration, pipeline modules, benchmarking, and test instructions.
