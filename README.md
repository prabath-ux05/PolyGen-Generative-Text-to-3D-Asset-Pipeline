
# PolyGen — Generative Text-to-3D Asset Pipeline

PolyGen is an end-to-end generative AI pipeline designed to convert natural language prompts into 3D assets with geometry, textures, and mesh processing capabilities.

---

## 1. Problem Statement

Creating high-quality 3D assets for games, simulations, virtual reality, and digital media is traditionally a labor-intensive, multi-step process requiring specialized modeling, sculpting, UV unwrapping, and texturing skills. While generative AI has accelerated 2D media creation, automated text-to-3D generation remains fragmented, often producing dense meshes with poor topology, unoptimized UVs, or uncoordinated textures that cannot be directly integrated into real-time rendering engines.

PolyGen aims to solve this bottleneck by providing a cohesive pipeline that translates descriptive text prompts into textured 3D models with production-friendly formats and mesh processing capabilities.

---

## 2. Main Project Objectives

- **Automated Text-to-3D Generation**: Synthesize 3D meshes from natural language prompts.
- **PBR Texture Synthesis**: Generate and apply realistic textures and materials corresponding to 3D geometry.
- **Mesh Post-Processing & Optimization**: Perform mesh validation, UV preparation, geometry inspection, and optimization for real-time asset workflows.
- **Unified Pipeline Orchestration**: Coordinate modules through a backend and pipeline management system.
- **Interactive Web Interface**: Provide a responsive dashboard with an interactive 3D viewer for asset preview, inspection, and export.

---

## 3. Core Modules & Team Allocation

| Module | Responsible | Scope & Responsibility | Status |
| :--- | :--- | :--- | :--- |
| **Backend & AI Pipeline Orchestration** | **Team Lead** | API gateway, pipeline orchestration, asset lifecycle, service integration, and storage. | In Progress |
| **Text-to-3D Generation Engine** | **Janvi** | Text conditioning, 3D generative model inference, and raw geometry generation. | In Progress |
| **Frontend & 3D Viewer** | **Samiksha** | Web dashboard, prompt submission interface, real-time status tracking, and 3D asset viewer. | In Progress |
| **Texture Engine & Mesh Processing** | **Jay** | Texture generation, PBR material application, mesh inspection, UV mapping/validation, and GLB export. | Implemented |

> Note: The Texture Engine & Mesh Processing module has been implemented and tested. Other modules are developed and integrated by their respective team members.
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
├── backend/                         # Backend service (FastAPI)
│   ├── app/
│   │   ├── api/                     # API router definitions
│   │   ├── core/                    # Core configuration and settings
│   │   ├── schemas/                  # Pydantic schemas / DTOs
│   │   ├── services/                 # Pipeline orchestration & business logic
│   │   └── main.py                  # FastAPI entrypoint
│   └── tests/                        # Backend automated tests
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
├── ai_generation/                    # AI-assisted texture generation
│   ├── texture_generator.py           # Hugging Face texture generation
│   ├── fallback_texture.py            # Local procedural texture generation
│   └── texture_workflow.py            # Texture generation + mesh workflow
│
├── texture_engine/                   # Texture processing and material pipeline
│   ├── texture_validator.py            # Texture validation
│   ├── texture_cache.py                # Texture caching
│   ├── texture_processor.py             # Texture processing
│   ├── material_builder.py              # PBR material construction
│   ├── texture_applier.py               # Texture application to meshes
│   └── pipeline.py                      # Integrated asset processing pipeline
│
├── mesh_processing/                   # Mesh loading, inspection, UV and export
│   ├── mesh_loader.py                  # Mesh loading
│   ├── mesh_inspector.py               # Geometry and quality inspection
│   ├── uv_mapper.py                    # UV mapping preparation
│   ├── uv_validator.py                 # UV validation
│   └── mesh_exporter.py                # GLB export and verification
│
├── frontend/                           # Web dashboard & 3D viewer
├── shared/                              # Shared models, constants, and contracts
├── generated_assets/                    # Generated assets (local storage)
│   ├── meshes/
│   └── textures/
│
├── docs/                                 # Architecture documentation
├── .gitignore
├── README.md
└── requirements.txt
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

- Python 3.10+
- pip
- Git
- Virtual environment (`venv`)

### 1. Clone the repository

```bash
git clone https://github.com/prabath-ux05/PolyGen-Generative-Text-to-3D-Asset-Pipeline.git
cd PolyGen-Generative-Text-to-3D-Asset-Pipeline
```

### 2. Create and activate a virtual environment

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. How to Run the FastAPI Server

Start the local development server with auto-reload:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, access:

- **API Root**: http://127.0.0.1:8000/
- **Health Check**: http://127.0.0.1:8000/health
- **Interactive Swagger Docs**: http://127.0.0.1:8000/docs
- **Alternative ReDoc**: http://127.0.0.1:8000/redoc

---

## 7. How to Run Tests

Run the entire project test suite:

```bash
python -m pytest -q
```

Run tests with verbose output:

```bash
python -m pytest -v
```

Run specific module tests:

```bash
python -m pytest mesh_processing/tests -v
python -m pytest texture_engine/tests -v
python -m pytest ai_generation/tests -v
```

Latest verified result for the complete project test suite:

**90 passed**

---

## 8. Texture Synthesis & Mesh Processing — Jay

The Texture Synthesis & Mesh Processing module handles mesh loading, inspection, UV preparation, texture generation, PBR material application, validation, and textured asset export.

### Features

- Mesh loading for supported 3D formats using Trimesh.
- Mesh geometry and quality inspection.
- Mesh validation and geometry reporting.
- UV coordinate validation.
- UV mapping preparation for meshes without UV coordinates.
- Texture validation and processing.
- Texture caching.
- PBR material construction and application.
- Text-driven texture generation through Hugging Face inference.
- Local procedural fallback texture generation for testing and development.
- Integrated texture generation and mesh processing workflow.
- GLB export with reload verification.

### Module Structure

```text
mesh_processing/
├── mesh_loader.py
├── mesh_inspector.py
├── uv_mapper.py
├── uv_validator.py
├── mesh_exporter.py
└── tests/

texture_engine/
├── texture_validator.py
├── texture_cache.py
├── texture_processor.py
├── material_builder.py
├── texture_applier.py
├── pipeline.py
└── tests/

ai_generation/
├── texture_generator.py
├── fallback_texture.py
├── texture_workflow.py
└── tests/
```

### Mesh Processing Workflow

1. Load the input mesh.
2. Inspect mesh geometry and dimensions.
3. Analyze mesh quality and structural properties.
4. Validate existing UV coordinates.
5. Prepare UV mapping when required.
6. Validate the resulting UV coordinates.
7. Apply the texture and PBR material.
8. Validate the final textured mesh.
9. Export the processed asset to GLB.
10. Reload the exported GLB to verify export integrity.

### Texture Generation

The module supports AI-based texture generation using Hugging Face Inference.

The texture generator accepts a text prompt and generates a texture image that can be used in the mesh texturing pipeline.

The default model is:

`black-forest-labs/FLUX.1-schnell`

Texture generation is configurable through the inference provider and requires appropriate Hugging Face access and available inference credits.

### Procedural Fallback

A local procedural fallback texture generator is available for development and testing without external AI inference.

The fallback:

- Generates texture images locally.
- Supports configurable output dimensions.
- Saves the generated texture to a specified location.
- Returns generation details, including output path, dimensions, and generator information.

The procedural fallback is intended for local testing and pipeline verification; it is not AI-generated texture synthesis.

### End-to-End Texture Workflow

The integrated workflow combines texture generation and mesh processing.

```text
Input Mesh + Text Prompt
          │
          ▼
   Texture Generation
   ├── Hugging Face AI Generator
   └── Local Procedural Fallback
          │
          ▼
     Mesh Processing
          │
          ▼
   Mesh Inspection
          │
          ▼
    UV Preparation
          │
          ▼
   Texture Application
          │
          ▼
   PBR Material Setup
          │
          ▼
   UV & Asset Validation
          │
          ▼
    GLB Export
          │
          ▼
 Export Reload Verification
          │
          ▼
    Textured 3D Asset
```

### Example Usage

```python
from ai_generation.texture_workflow import generate_and_texture_asset

result = generate_and_texture_asset(
    mesh_path="input_mesh.glb",
    prompt="realistic dark oak wood texture",
    texture_path="generated_textures/wood.png",
    output_path="outputs/textured_wood.glb",
    use_fallback=True,
)

print(result["success"])
print(result["output_file"])
```

Use `use_fallback=True` to generate a local procedural texture.

Use `use_fallback=False` to use the Hugging Face AI texture generation provider.

### Output

The integrated pipeline produces a textured GLB asset containing the processed mesh and applied material.

The output includes processing information such as:

- Mesh inspection report.
- Geometry statistics.
- UV validation results.
- Texture generation report.
- Texture application details.
- Material properties.
- Export status.
- Output file information.
- Validation warnings, if any.

### Testing

Run all tests for the module:

```bash
python -m pytest ai_generation/tests mesh_processing/tests texture_engine/tests -v
```

Run the complete PolyGen test suite:

```bash
python -m pytest -q
```

## AI Generation Engine

See [AI Generation Engine documentation](docs/ai_generation_engine.md) for configuration, pipeline modules, benchmarking, and test instructions.
