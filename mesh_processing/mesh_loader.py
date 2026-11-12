
"""Load and inspect 3D mesh files in OBJ, GLB, and GLTF formats."""

from dataclasses import dataclass
from pathlib import Path

import trimesh


SUPPORTED_FORMATS = {".obj", ".glb", ".gltf"}


@dataclass
class MeshLoadResult:
    """Contains a loaded mesh and its basic metadata."""

    mesh: trimesh.Trimesh
    metadata: dict


def load_mesh(file_path: str | Path) -> MeshLoadResult:
    """
    Load a 3D model and return its geometry and metadata.

    Supported formats: OBJ, GLB, GLTF.
    """

    path = Path(file_path)

    # Validate the input path.
    if not path.exists():
        raise FileNotFoundError(f"Mesh file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Expected a file, received: {path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {path.suffix}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    if path.stat().st_size == 0:
        raise ValueError("Mesh file is empty.")

    # Load the model as a scene to support multi-object files.
    try:
        loaded = trimesh.load(
            path,
            force="scene",
            process=False,
        )
    except Exception as exc:
        raise ValueError(f"Failed to load mesh file: {exc}") from exc

    # Extract geometry while preserving scene transformations.
    if isinstance(loaded, trimesh.Scene):
        mesh = loaded.to_geometry()

        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("The file contains no valid mesh geometry.")

    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded

    else:
        raise ValueError("The file did not contain a supported mesh.")

    # Validate the extracted mesh.
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("The loaded mesh has no vertices or faces.")

    # Extract mesh information.
    bounds = mesh.bounds
    dimensions = mesh.extents

    metadata = {
        "file_name": path.name,
        "file_format": path.suffix.lower().lstrip("."),
        "vertex_count": len(mesh.vertices),
        "face_count": len(mesh.faces),
        "dimensions": dimensions.tolist(),
        "bounds": bounds.tolist(),
        "is_watertight": bool(mesh.is_watertight),
    }

    return MeshLoadResult(
        mesh=mesh,
        metadata=metadata,
    )
