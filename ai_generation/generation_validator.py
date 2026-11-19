"""Validate generated 3D meshes before export."""

from dataclasses import dataclass

import numpy as np
import trimesh


class MeshValidationError(ValueError):
    """Raised when a generated mesh fails validation."""


@dataclass(frozen=True)
class MeshValidationReport:
    """Store mesh validation results."""

    valid: bool
    errors: tuple
    warnings: tuple
    vertex_count: int
    face_count: int
    is_watertight: bool

    def to_dict(self):
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "vertex_count": self.vertex_count,
            "face_count": self.face_count,
            "is_watertight": self.is_watertight,
        }


class MeshValidator:
    """Check geometry, topology and basic mesh quality."""

    def __init__(
        self,
        min_vertices=3,
        min_faces=1,
        require_watertight=False,
    ):
        if min_vertices < 3:
            raise ValueError("Minimum vertices must be at least 3")

        if min_faces < 1:
            raise ValueError("Minimum faces must be at least 1")

        self.min_vertices = min_vertices
        self.min_faces = min_faces
        self.require_watertight = require_watertight

    def validate(self, mesh):
        """Return a report describing the mesh."""
        errors = []
        warnings = []

        if not isinstance(mesh, trimesh.Trimesh):
            return MeshValidationReport(
                valid=False,
                errors=("Input must be a trimesh.Trimesh object",),
                warnings=(),
                vertex_count=0,
                face_count=0,
                is_watertight=False,
            )

        vertex_count = len(mesh.vertices)
        face_count = len(mesh.faces)

        if mesh.is_empty:
            errors.append("Mesh is empty")

        if vertex_count < self.min_vertices:
            errors.append(
                f"Mesh needs at least {self.min_vertices} vertices"
            )

        if face_count < self.min_faces:
            errors.append(
                f"Mesh needs at least {self.min_faces} faces"
            )

        if vertex_count and not np.isfinite(mesh.vertices).all():
            errors.append("Mesh contains non-finite vertex coordinates")

        if face_count:
            if mesh.faces.min() < 0 or mesh.faces.max() >= vertex_count:
                errors.append("Mesh contains invalid face indices")

        watertight = False

        if vertex_count and face_count:
            try:
                watertight = bool(mesh.is_watertight)
            except Exception:
                warnings.append("Could not determine watertight status")

            try:
                face_areas = mesh.area_faces

                if not np.isfinite(face_areas).all():
                    errors.append("Mesh contains non-finite face areas")
                elif np.any(face_areas <= 1e-12):
                    warnings.append("Mesh contains degenerate faces")
            except Exception:
                warnings.append("Could not calculate face areas")

            if not watertight:
                message = "Mesh is not watertight"

                if self.require_watertight:
                    errors.append(message)
                else:
                    warnings.append(message)

            try:
                components = mesh.split(only_watertight=False)

                if len(components) > 1:
                    warnings.append(
                        f"Mesh contains {len(components)} disconnected components"
                    )
            except Exception:
                warnings.append("Could not inspect mesh components")

        return MeshValidationReport(
            valid=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
            vertex_count=vertex_count,
            face_count=face_count,
            is_watertight=watertight,
        )

    def validate_or_raise(self, mesh):
        """Validate a mesh and raise an error if it is invalid."""
        report = self.validate(mesh)

        if not report.valid:
            details = "; ".join(report.errors)
            raise MeshValidationError(details)

        return report
