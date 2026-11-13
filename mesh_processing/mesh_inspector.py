
"""Inspect 3D meshes and generate quality reports."""

import json
import math
from pathlib import Path

import trimesh


def inspect_mesh(mesh: trimesh.Trimesh) -> dict:
    """
    Calculate mesh statistics and identify basic quality issues.

    Returns a JSON-compatible dictionary.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected a trimesh.Trimesh object.")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("Cannot inspect an empty mesh.")

    # Basic geometry statistics
    vertex_count = len(mesh.vertices)
    face_count = len(mesh.faces)

    dimensions = mesh.extents.tolist()
    bounds = mesh.bounds.tolist()

    surface_area = float(mesh.area)
    is_watertight = bool(mesh.is_watertight)
    is_winding_consistent = bool(mesh.is_winding_consistent)

    # Volume is meaningful for a closed, consistently oriented mesh.
    volume = (
        abs(float(mesh.volume))
        if is_watertight and is_winding_consistent
        else None
    )

    # Identify faces with zero or nearly zero area.
    degenerate_face_count = sum(
        1 for area in mesh.area_faces if float(area) <= 1e-12
    )

    # Generate quality warnings.
    warnings = []

    if not is_watertight:
        warnings.append("Mesh is not watertight (it may contain holes).")

    if not is_winding_consistent:
        warnings.append("Mesh face winding is inconsistent.")

    if degenerate_face_count > 0:
        warnings.append(
            f"Mesh contains {degenerate_face_count} degenerate face(s)."
        )

    if not math.isfinite(surface_area):
        warnings.append("Mesh surface area is not finite.")

    if any(
        not math.isfinite(float(value))
        for vertex in mesh.vertices
        for value in vertex
    ):
        warnings.append("Mesh contains non-finite vertex coordinates.")

    return {
        "vertex_count": vertex_count,
        "face_count": face_count,
        "dimensions": dimensions,
        "bounds": bounds,
        "surface_area": surface_area,
        "volume": volume,
        "is_watertight": is_watertight,
        "is_winding_consistent": is_winding_consistent,
        "degenerate_face_count": degenerate_face_count,
        "quality_status": "warning" if warnings else "good",
        "warnings": warnings,
    }


def save_inspection_report(report: dict, output_path: str | Path) -> Path:
    """Save a mesh inspection report as a formatted JSON file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, allow_nan=False)

    return path
