"""Export validated 3D meshes into OBJ and GLB formats."""

from pathlib import Path
from uuid import uuid4
import re

import numpy as np
import trimesh


class MeshExportError(Exception):
    """Raised when mesh validation or export fails."""


class MeshExporter:
    """Validate and export 3D meshes with unique filenames."""

    SUPPORTED_FORMATS = {"obj", "glb"}

    def __init__(self, output_dir="artifacts/generated"):
        self.output_dir = Path(output_dir)

    def validate_mesh(self, mesh):
        """Check whether a mesh contains valid geometry."""
        if not isinstance(mesh, trimesh.Trimesh):
            raise MeshExportError(
                "Input must be a trimesh.Trimesh object"
            )

        if mesh.is_empty:
            raise MeshExportError("Mesh cannot be empty")

        if len(mesh.vertices) == 0:
            raise MeshExportError("Mesh has no vertices")

        if len(mesh.faces) == 0:
            raise MeshExportError("Mesh has no faces")

        if not np.isfinite(mesh.vertices).all():
            raise MeshExportError(
                "Mesh contains invalid vertex values"
            )

        return True

    def _create_output_path(self, filename, file_format):
        """Create a unique output path without overwriting files."""
        extension = file_format.lower()

        if filename is not None:
            safe_name = Path(str(filename)).stem.strip()

            if (
                not safe_name
                or not re.fullmatch(r"[A-Za-z0-9 _-]+", safe_name)
            ):
                raise MeshExportError("Invalid output filename")

            base_name = safe_name
        else:
            base_name = "model"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_path = self.output_dir / f"{base_name}.{extension}"

        if output_path.exists():
            output_path = self.output_dir / (
                f"{base_name}_{uuid4().hex[:8]}.{extension}"
            )

        return output_path

    def export(self, mesh, file_format="obj", filename=None):
        """Validate and export a mesh as OBJ or GLB."""
        if not isinstance(file_format, str):
            raise MeshExportError("File format must be a string")

        selected_format = file_format.lower().strip()

        if selected_format not in self.SUPPORTED_FORMATS:
            raise MeshExportError(
                f"Unsupported format: {file_format}. "
                "Supported formats are OBJ and GLB."
            )

        self.validate_mesh(mesh)

        output_path = self._create_output_path(
            filename, selected_format
        )

        try:
            exported_data = mesh.export(file_type=selected_format)

            if isinstance(exported_data, str):
                exported_data = exported_data.encode("utf-8")

            if not isinstance(exported_data, bytes):
                raise MeshExportError(
                    "Exporter returned an unsupported data type"
                )

            if not exported_data:
                raise MeshExportError("Export produced empty output")

            output_path.write_bytes(exported_data)

            if (
                not output_path.exists()
                or output_path.stat().st_size == 0
            ):
                raise MeshExportError(
                    "Exported file is empty or missing"
                )

            return output_path

        except MeshExportError:
            raise
        except Exception as exc:
            raise MeshExportError(
                f"Failed to export mesh as {selected_format}: {exc}"
            ) from exc
