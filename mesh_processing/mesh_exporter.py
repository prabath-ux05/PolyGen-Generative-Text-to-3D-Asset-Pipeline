"""Export processed and textured meshes to GLB format."""

from pathlib import Path

import trimesh


def export_mesh(
    mesh: trimesh.Trimesh,
    output_path: str | Path,
) -> dict:
    """
    Export a mesh to GLB and verify that the exported file can be reloaded.

    GLB is selected because it supports mesh geometry, UV coordinates,
    materials, and embedded textures in a single file.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("Expected a trimesh.Trimesh object.")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("Cannot export an empty mesh.")

    output_path = Path(output_path)

    if output_path.suffix.lower() != ".glb":
        raise ValueError("Only .glb export is supported.")

    # Create the output directory if it does not exist.
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export the mesh.
    try:
        mesh.export(output_path, file_type="glb")
    except Exception as exc:
        raise RuntimeError(f"Failed to export GLB: {exc}") from exc

    # Confirm that the file was created successfully.
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError("GLB export failed: output file is empty.")

    # Reload the exported model to verify it is readable.
    try:
        loaded_scene = trimesh.load(
            output_path,
            force="scene",
            process=False,
        )
    except Exception as exc:
        raise RuntimeError(f"Exported GLB could not be reloaded: {exc}") from exc

    if not isinstance(loaded_scene, trimesh.Scene):
        raise RuntimeError("Exported GLB did not load as a valid scene.")

    if len(loaded_scene.geometry) == 0:
        raise RuntimeError("Exported GLB contains no geometry.")

    # Calculate geometry information after reloading.
    exported_vertices = sum(
        len(geometry.vertices)
        for geometry in loaded_scene.geometry.values()
        if isinstance(geometry, trimesh.Trimesh)
    )

    exported_faces = sum(
        len(geometry.faces)
        for geometry in loaded_scene.geometry.values()
        if isinstance(geometry, trimesh.Trimesh)
    )

    if exported_vertices == 0 or exported_faces == 0:
        raise RuntimeError("Exported GLB contains invalid mesh geometry.")

    report = {
        "success": True,
        "file_name": output_path.name,
        "file_path": str(output_path.resolve()),
        "file_format": "glb",
        "file_size_bytes": output_path.stat().st_size,
        "geometry_count": len(loaded_scene.geometry),
        "vertex_count": exported_vertices,
        "face_count": exported_faces,
        "verified": True,
        "warnings": [],
    }

    return report