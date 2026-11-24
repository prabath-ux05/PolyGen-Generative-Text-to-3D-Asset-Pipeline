# PolyGen — Backend Integration Specification

This document details the backend API contracts, setup procedures, and integration interfaces for **PolyGen — Generative Text-to-3D Asset Pipeline**. It is designed for frontend developers (Samiksha), text-to-3D engine developers (Janvi), and texture/mesh optimization developers (Jay).

---

## 1. Backend Setup & Startup

### Prerequisites
- Python 3.10+ (tested with Python 3.13)
- Virtual environment (`venv`)

### Installation & Server Start
```bash
# 1. Activate virtual environment
# Windows:
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Base API URL
```text
http://127.0.0.1:8000
```

Interactive Documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 2. CORS Configuration (Frontend Integration)

CORS is configured on all API routes to allow cross-origin requests from frontend development servers:

- **Default Allowed Origins**:
  - `http://localhost:3000` (React / Next.js default)
  - `http://127.0.0.1:3000`
  - `http://localhost:5173` (Vite default)
  - `http://127.0.0.1:5173`
  - `http://localhost:8080`
  - `http://127.0.0.1:8080`
- **Custom Origins**: Configure via environment variable `ALLOWED_ORIGINS` (comma-separated).
- **Credentials**: `allow_credentials=True` (restricted to explicit origins; no wildcard `*` with credentials).
- **Allowed Methods**: `GET`, `POST`, `PATCH`, `OPTIONS`, `HEAD`.

---

## 3. Endpoints & API Contracts

### Overview of Endpoints

| Method | Endpoint | Description | Status |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API root metadata and welcome | **Operational** |
| `GET` | `/health` | Health check for deployment monitoring | **Operational** |
| `POST` | `/api/v1/generations` | Submit a Text-to-3D generation request | **Scaffolded (503 Service Unavailable)** |
| `GET` | `/api/v1/generations/{job_id}` | Retrieve generation job status & details | **Operational (In-Memory)** |
| `PATCH` | `/api/v1/generations/{job_id}/status` | Controlled status transition | **Operational (In-Memory)** |

---

### Endpoint Details

#### 1. System Endpoints

##### `GET /`
- **Response `200 OK`**:
  ```json
  {
    "name": "PolyGen API",
    "description": "Generative Text-to-3D Asset Pipeline",
    "status": "online",
    "docs_url": "/docs"
  }
  ```

##### `GET /health`
- **Response `200 OK`**:
  ```json
  {
    "app": "PolyGen API",
    "status": "healthy",
    "version": "0.1.0"
  }
  ```

---

#### 2. Generation Request Endpoint

##### `POST /api/v1/generations`
- **Description**: Validates input prompt and output format. Returns HTTP 503 until Janvi's AI generation engine is connected.
- **Request Body (`GenerationRequest`)**:
  ```json
  {
    "prompt": "A low-poly medieval wooden cart",
    "output_format": "glb"
  }
  ```
- **Validation Rules**:
  - `prompt`: Required string, 1 to 1,000 characters. Rejects empty strings and whitespace-only. Strips surrounding whitespace automatically.
  - `output_format`: Optional string, defaults to `"glb"`. Case-insensitive. Supported: `"glb"`, `"obj"`.
- **Response `503 Service Unavailable` (`ServiceUnavailableResponse`)**:
  ```json
  {
    "detail": "Text-to-3D generation engine is not yet integrated."
  }
  ```
- **Error Response `422 Unprocessable Content`**: Returned if prompt is missing, invalid, or format is unsupported.

---

#### 3. Job Retrieval Endpoint

##### `GET /api/v1/generations/{job_id}`
- **Path Parameter**: `job_id` (UUID format, e.g. `550e8400-e29b-41d4-a716-446655440000`).
- **Response `200 OK` (`GenerationJobResponse`)**:
  ```json
  {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt": "A low-poly medieval wooden cart",
    "output_format": "glb",
    "status": "processing",
    "created_at": "2026-11-20T10:00:00.000000Z",
    "updated_at": "2026-11-20T10:02:15.000000Z",
    "error_message": null
  }
  ```
- **Error Response `404 Not Found` (`ErrorResponse`)**:
  ```json
  {
    "detail": "Generation job with ID '550e8400-e29b-41d4-a716-446655440000' not found."
  }
  ```
- **Error Response `422 Unprocessable Content`**: Returned if `job_id` is not a valid UUID string.

---

#### 4. Job Status Update Endpoint

##### `PATCH /api/v1/generations/{job_id}/status`
- **Path Parameter**: `job_id` (UUID).
- **Request Body (`GenerationJobStatusUpdateRequest`)**:
  ```json
  {
    "status": "completed",
    "error_message": null
  }
  ```
- **Valid Status Values**: `"pending"`, `"processing"`, `"completed"`, `"failed"`.
- **Lifecycle Transition Rules**:
  ```text
  pending ──► processing ──┬──► completed (terminal)
                           └──► failed (terminal)
  ```
  - `pending` → `processing`
  - `processing` → `completed`
  - `processing` → `failed` (supports passing `error_message`)
- **Response `200 OK`**: Returns updated `GenerationJobResponse` with refreshed `updated_at`.
- **Error Response `409 Conflict` (`ErrorResponse`)**:
  ```json
  {
    "detail": "Cannot transition job '550e8400-e29b-41d4-a716-446655440000' from 'pending' to 'completed'. Allowed transitions from 'pending': ['processing']."
  }
  ```
- **Error Response `404 Not Found`**: Returned if job UUID does not exist.
- **Error Response `422 Unprocessable Content`**: Returned if status is not an allowed enum value or UUID is malformed.

---

## 4. Current Working vs. Planned Functionality

### Currently Working (Backend Foundation)
- [x] FastAPI modular routing (`api/router.py`, `routes/system.py`, `routes/generations.py`).
- [x] Input validation for prompt length, whitespace, and 3D output formats (`GLB`, `OBJ`).
- [x] CORS middleware enabling local frontend dev servers (`3000`, `5173`, `8080`).
- [x] In-memory job lifecycle management (`GenerationJobService`).
- [x] Timezone-aware UTC timestamp tracking (`created_at`, `updated_at`).
- [x] Controlled state transition engine with 409 Conflict rejection for illegal transitions.
- [x] Retrieval API (`GET /api/v1/generations/{job_id}`).
- [x] Status update API (`PATCH /api/v1/generations/{job_id}/status`).
- [x] Comprehensive automated test suite (86 tests).

### Planned for Team Integration
- [ ] **AI Pipeline Integration (Janvi)**: Wiring `POST /api/v1/generations` to trigger text-to-3D model inference.
- [ ] **Texture & Mesh Processing (Jay)**: Automated retopology and PBR texture map baking.
- [ ] **Frontend Dashboard & 3D Viewer (Samiksha)**: Polling `GET /api/v1/generations/{job_id}` and rendering GLB/OBJ models via Three.js / Babylon.js.
- [ ] **Persistent Storage**: Migration from in-memory dictionary to PostgreSQL/SQLite and asset storage (S3/local disk).
- [ ] **Background Execution**: Celery / Redis or FastAPI BackgroundTasks for asynchronous model execution.
