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
| **Text-to-3D Generation Engine** | **Janvi** | Text conditioning, 3D generative model inference, and raw geometry generation. | Planned (Placeholder) |
| **Frontend & 3D Viewer** | **Samiksha** | Web dashboard, prompt submission interface, real-time status tracking, and 3D asset viewer. | Planned (Placeholder) |
| **Texture Engine & Mesh Processing** | **Jay** | PBR material synthesis, texture baking, retopology, mesh decimation, and format export. | Planned (Placeholder) |

> *Note: Modules assigned to Janvi, Samiksha, and Jay are currently scaffolded as initial placeholders and will be implemented in subsequent development phases.*

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
├── ai_generation/                # [Placeholder] Text-to-3D generation engine
│
├── texture_engine/               # [Placeholder] PBR texture generation & baking
│
├── mesh_processing/              # [Placeholder] Retopology, decimation & UV unwrapping
│
├── frontend/                     # [Placeholder] Web dashboard & 3D viewer
│
├── shared/                       # Shared models, constants, and contracts
│   └── contracts/
│
├── generated_assets/             # Storage for generated pipeline assets (git-ignored)
│   ├── meshes/                   # Generated 3D geometries (.obj, .gltf, .glb)
│   └── textures/                 # Synthesized texture maps (diffuse, normal, roughness)
│
├── docs/                         # Architecture documentation & API specs
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

