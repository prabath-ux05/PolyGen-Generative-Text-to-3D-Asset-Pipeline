"""Synthetic geometry adapter for deterministic integration tests and offline local execution.

This adapter provides procedural geometry generation without invoking neural networks or
downloading model weights. It is explicitly isolated and marked as synthetic to ensure it
is never mistaken for real AI inference.
"""

from typing import Any
import trimesh


class SyntheticGeometryAdapter:
    """Explicitly isolated synthetic geometry generator.

    Produces deterministic 3D meshes for pipeline integration testing and local demos.
    Never silently replaces real neural inference.
    """

    ADAPTER_NAME: str = "synthetic_geometry_adapter"
    IS_SYNTHETIC: bool = True

    @classmethod
    def generate(cls, prompt: str, components: Any = None) -> trimesh.Trimesh:
        """Generate a valid, manifold synthetic mesh based on the prompt.

        Args:
            prompt: Text prompt describing the target object.
            components: Optional model components (ignored by synthetic adapter).

        Returns:
            A clean, watertight trimesh.Trimesh object.
        """
        prompt_lower = (prompt or "").lower().strip()

        # Deterministic shape selection based on prompt keywords
        if any(kw in prompt_lower for kw in ["sphere", "orb", "ball", "planet"]):
            mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        elif any(kw in prompt_lower for kw in ["cylinder", "column", "pillar", "tube", "bottle"]):
            mesh = trimesh.creation.cylinder(radius=0.5, height=2.0)
        elif any(kw in prompt_lower for kw in ["torus", "ring", "donut"]):
            mesh = trimesh.creation.torus(major_radius=1.0, minor_radius=0.3)
        elif any(kw in prompt_lower for kw in ["cone", "pyramid", "hat"]):
            mesh = trimesh.creation.cone(radius=0.8, height=1.6)
        else:
            # Default procedural primitive: a centered cube/box
            mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))

        return mesh
