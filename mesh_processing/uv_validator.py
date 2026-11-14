
"""Validate UV coordinates on 3D meshes."""

import numpy as np
import trimesh


def validate_uv(mesh: trimesh.Trimesh) -> dict:
    """
    Check whether a mesh has valid UV coordinates.

    Returns a JSON-compatible validation report.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected a trimesh.Trimesh object.")

    warnings = []

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("Cannot validate UVs on an empty mesh.")

    visual = mesh.visual

    uv = getattr(visual, "uv", None)

    if uv is None:
        return {
            "has_uv": False,
            "is_valid": False,
            "uv_count": 0,
            "expected_count": len(mesh.vertices),
            "quality_status": "warning",
            "warnings": ["Mesh does not contain UV coordinates."],
        }

    uv = np.asarray(uv)

    if uv.ndim != 2 or uv.shape[1] != 2:
        warnings.append("UV coordinates must have exactly two components.")

    elif len(uv) != len(mesh.vertices):
        warnings.append(
            "UV coordinate count does not match the vertex count."
        )

    elif not np.isfinite(uv).all():
        warnings.append("UV coordinates contain non-finite values.")

    elif np.any(uv < 0) or np.any(uv > 1):
        warnings.append("UV coordinates extend outside the [0, 1] range.")

    is_valid = len(warnings) == 0

    return {
        "has_uv": True,
        "is_valid": is_valid,
        "uv_count": len(uv),
        "expected_count": len(mesh.vertices),
        "quality_status": "good" if is_valid else "warning",
        "warnings": warnings,
    }
