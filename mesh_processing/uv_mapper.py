"""Generate UV coordinates for 3D meshes."""

import numpy as np
import trimesh


def generate_uv(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Generate normalized planar UV coordinates for a mesh.

    The projection axis is selected based on the smallest mesh dimension.
    The original mesh is not modified.

    Returns:
        A copy of the mesh with generated UV coordinates.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected a trimesh.Trimesh object.")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("Cannot generate UVs for an empty mesh.")

    vertices = np.asarray(mesh.vertices)

    if not np.isfinite(vertices).all():
        raise ValueError("Mesh contains non-finite vertex coordinates.")

    # Find the mesh dimensions.
    bounds = mesh.bounds
    minimum = bounds[0]
    maximum = bounds[1]
    dimensions = maximum - minimum

    # Project along the smallest dimension.
    projection_axis = int(np.argmin(dimensions))

    # Keep the other two axes for UV mapping.
    uv_axes = [
        axis for axis in range(3)
        if axis != projection_axis
    ]

    projected = vertices[:, uv_axes]

    # Normalize projected coordinates into the 0-1 range.
    uv_min = projected.min(axis=0)
    uv_max = projected.max(axis=0)
    uv_range = uv_max - uv_min

    # Prevent division by zero for flat or degenerate dimensions.
    uv_range[uv_range == 0] = 1.0

    uv = (projected - uv_min) / uv_range

    # Work on a copy to preserve the original mesh.
    mapped_mesh = mesh.copy()

    # Attach the generated UV coordinates.
    mapped_mesh.visual = trimesh.visual.TextureVisuals(
        uv=uv
    )

    return mapped_mesh