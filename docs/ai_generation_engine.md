# PolyGen AI Generation Engine

## Overview

The AI generation engine coordinates prompt processing, model loading,
mesh generation, validation, export, performance monitoring, and metadata.

## Main modules

- `model_manager.py`: manages model selection and status.
- `models/model_loader.py`: loads Shap-E components.
- `prompt_processor.py`: validates and prepares text prompts.
- `generator.py`: coordinates the generation workflow.
- `config.py`: stores and validates engine configuration.
- `benchmark.py`: measures generation across multiple prompts.
- `generation_validator.py`: validates generated meshes.
- `exporter.py`: exports generated mesh files.
- `generation_metadata.py`: stores generation details.
- `error_handler.py`: converts failures into structured errors.
- `performance_monitor.py`: records generation timing.

## Configuration

The engine reads optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `POLYGEN_OUTPUT_DIR` | `artifacts/generated` | Generated mesh directory |
| `POLYGEN_METADATA_DIR` | `artifacts/metadata` | Metadata directory |
| `POLYGEN_DEFAULT_FORMAT` | `obj` | Default export format |
| `POLYGEN_MIN_PROMPT_LENGTH` | `3` | Minimum prompt length |
| `POLYGEN_MAX_PROMPT_LENGTH` | `500` | Maximum prompt length |
| `POLYGEN_DEVICE` | `auto` | `auto`, `cpu`, or `cuda` |

Example PowerShell configuration:

```powershell
$env:POLYGEN_DEVICE = "cpu"
$env:POLYGEN_DEFAULT_FORMAT = "obj"
$env:POLYGEN_OUTPUT_DIR = "artifacts/generated"
```

## Generation adapter

`TextTo3DGenerator` accepts a `generation_fn` callback. The callback receives
the processed prompt and loaded model components and must return a mesh
that the validation and export stages can process.

A real Shap-E inference adapter and its model weights are required for
actual AI-generated output. Tests can use a synthetic mesh to verify
the surrounding pipeline without downloading model weights.

## Benchmarking

`BenchmarkRunner` accepts a generator and a collection of prompts.
It records successful and failed generations, elapsed time, output paths,
and optional error codes. Reports can be saved as JSON.

## Running tests

```powershell
python -m pytest -q
```

The end-to-end tests use a synthetic mesh. Passing them verifies the
pipeline integration, not the quality or performance of real Shap-E inference.
