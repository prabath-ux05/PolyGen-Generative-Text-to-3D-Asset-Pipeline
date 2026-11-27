"""Isolated Shap-E inference adapter for text-to-3D mesh generation.

Provides prompt-conditioned latent diffusion sampling, mesh decoding,
trimesh conversion, geometry validation, and model lifecycle management.
Follows the generation_fn(prompt, components) contract and uses lazy
imports so the rest of the project and test suite run without shap-e installed.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np
import trimesh

from ai_generation.generation_validator import MeshValidator, MeshValidationError


class ShapEInferenceAdapter:
    """Inference adapter for OpenAI's Shap-E text-to-3D model.

    Manages model loading and caching, latent diffusion sampling,
    mesh decoding via the transmitter, and conversion to validated
    trimesh.Trimesh geometry.
    """

    ADAPTER_NAME: str = "shap_e_inference_adapter"
    IS_SYNTHETIC: bool = False

    def __init__(
        self,
        device: Optional[str] = None,
        guidance_scale: float = 15.0,
        karras_steps: int = 64,
        mesh_validator: Optional[MeshValidator] = None,
    ):
        """Initialize the Shap-E inference adapter.

        Args:
            device: Compute device ('cpu', 'cuda', or None for auto-detect).
            guidance_scale: Classifier-free guidance scale for diffusion (default 15.0).
            karras_steps: Number of diffusion sampling steps (default 64).
            mesh_validator: Optional custom MeshValidator instance.
        """
        self.device = self._resolve_device(device)
        self.guidance_scale = float(guidance_scale)
        self.karras_steps = int(karras_steps)
        self.mesh_validator = mesh_validator or MeshValidator()

        # Model component cache
        self._transmitter: Optional[Any] = None
        self._model: Optional[Any] = None
        self._diffusion: Optional[Any] = None

    @staticmethod
    def detect_device() -> str:
        """Detect best available compute device (CUDA if available, else CPU)."""
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
        except (ImportError, Exception):
            pass
        return "cpu"

    @classmethod
    def _resolve_device(cls, device: Optional[str]) -> str:
        """Validate and resolve device string."""
        if device is None or device == "auto":
            return cls.detect_device()

        device_clean = str(device).strip().lower()
        if device_clean != "cpu" and not device_clean.startswith("cuda"):
            raise ValueError(
                f"Invalid device '{device}'. Must be 'cpu', 'cuda', or None."
            )
        return device_clean

    @property
    def is_loaded(self) -> bool:
        """Check whether all required model components are loaded."""
        return (
            self._transmitter is not None
            and self._model is not None
            and self._diffusion is not None
        )

    def load_models(
        self,
        load_model_fn: Optional[Callable] = None,
        load_config_fn: Optional[Callable] = None,
        diffusion_from_config_fn: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """Load and cache the Shap-E model components.

        Reuses already loaded models if available. Supports custom loader
        callables for unit testing and dependency injection.

        Returns:
            Dict containing transmitter, model, and diffusion components.

        Raises:
            ImportError: If shap-e is not installed.
            RuntimeError: If model loading fails.
        """
        if self.is_loaded:
            return {
                "transmitter": self._transmitter,
                "model": self._model,
                "diffusion": self._diffusion,
                "device": self.device,
            }

        # Resolve loader functions (lazy import if not injected)
        if (
            load_model_fn is None
            or load_config_fn is None
            or diffusion_from_config_fn is None
        ):
            try:
                from shap_e.models.download import (
                    load_model as real_load_model,
                    load_config as real_load_config,
                )
                from shap_e.diffusion.gaussian_diffusion import (
                    diffusion_from_config as real_diffusion_from_config,
                )

                load_model_fn = load_model_fn or real_load_model
                load_config_fn = load_config_fn or real_load_config
                diffusion_from_config_fn = (
                    diffusion_from_config_fn or real_diffusion_from_config
                )
            except ImportError as exc:
                raise ImportError(
                    "Shap-E is not installed. Please install the shap-e package "
                    "before loading model weights."
                ) from exc

        try:
            transmitter = load_model_fn("transmitter", device=self.device)
            model = load_model_fn("text300M", device=self.device)
            diff_config = load_config_fn("diffusion")
            diffusion = diffusion_from_config_fn(diff_config)

            self._transmitter = transmitter
            self._model = model
            self._diffusion = diffusion

            return {
                "transmitter": self._transmitter,
                "model": self._model,
                "diffusion": self._diffusion,
                "device": self.device,
            }
        except Exception as exc:
            self.unload()
            raise RuntimeError(
                f"Failed to load Shap-E model components: {exc}"
            ) from exc

    def unload(self) -> None:
        """Release loaded model components and clear GPU cache if applicable."""
        self._transmitter = None
        self._model = None
        self._diffusion = None

        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except (ImportError, Exception):
            pass

    def sample_latents(
        self,
        prompt: str,
        model: Optional[Any] = None,
        diffusion: Optional[Any] = None,
        batch_size: int = 1,
        guidance_scale: Optional[float] = None,
        karras_steps: Optional[int] = None,
        sample_latents_fn: Optional[Callable] = None,
    ) -> Any:
        """Sample 3D latents conditioned on the input text prompt.

        Args:
            prompt: Text prompt describing the 3D asset.
            model: Optional diffusion model (defaults to cached model).
            diffusion: Optional diffusion sampler (defaults to cached diffusion).
            batch_size: Number of latent samples to generate (default 1).
            guidance_scale: Guidance scale (defaults to instance setting).
            karras_steps: Sampling steps (defaults to instance setting).
            sample_latents_fn: Optional custom sample_latents function for testing.

        Returns:
            Sampled latent or collection of latents.
        """
        active_model = model or self._model
        active_diffusion = diffusion or self._diffusion

        if active_model is None or active_diffusion is None:
            models = self.load_models()
            active_model = active_model or models["model"]
            active_diffusion = active_diffusion or models["diffusion"]

        scale = self.guidance_scale if guidance_scale is None else float(guidance_scale)
        steps = self.karras_steps if karras_steps is None else int(karras_steps)

        if sample_latents_fn is None:
            try:
                from shap_e.diffusion.sample import sample_latents as real_sample_latents

                sample_latents_fn = real_sample_latents
            except ImportError as exc:
                raise ImportError(
                    "Shap-E is not installed. Please install the shap-e package "
                    "to sample latents."
                ) from exc

        try:
            use_fp16 = self.device != "cpu"
            torch_device = None
            try:
                import torch

                torch_device = torch.device(self.device)
            except Exception:
                pass

            latents = sample_latents_fn(
                batch_size=batch_size,
                model=active_model,
                diffusion=active_diffusion,
                guidance_scale=scale,
                model_kwargs=dict(texts=[prompt]),
                progress=False,
                clip_denoised=True,
                use_fp16=use_fp16,
                use_karras=True,
                karras_steps=steps,
                sigma_min=1e-3,
                sigma_max=160,
                s_churn=0,
                device=torch_device,
            )
            return latents
        except Exception as exc:
            # Check specifically for CUDA OutOfMemoryError
            is_cuda_oom = False
            try:
                import torch

                if hasattr(torch.cuda, "OutOfMemoryError") and isinstance(
                    exc, torch.cuda.OutOfMemoryError
                ):
                    is_cuda_oom = True
            except (ImportError, Exception):
                pass

            if not is_cuda_oom:
                exc_type_name = type(exc).__name__
                exc_msg = str(exc).lower()
                if "outofmemoryerror" in exc_type_name.lower() or (
                    "out of memory" in exc_msg
                    and ("cuda" in exc_msg or "gpu" in exc_msg)
                ):
                    is_cuda_oom = True

            if is_cuda_oom:
                try:
                    self.unload()
                except Exception:
                    pass

                raise RuntimeError(
                    "CUDA out of memory during Shap-E diffusion sampling. "
                    "Try reducing prompt complexity, lowering karras_steps, or switching to CPU device."
                ) from exc

            raise RuntimeError(
                f"Failed to sample Shap-E latents: {exc}"
            ) from exc

    def decode_mesh(
        self,
        latent: Any,
        transmitter: Optional[Any] = None,
        decode_latent_mesh_fn: Optional[Callable] = None,
    ) -> Any:
        """Decode a latent representation into a Shap-E mesh.

        Args:
            latent: Latent representation from sample_latents.
            transmitter: Optional transmitter model (defaults to cached transmitter).
            decode_latent_mesh_fn: Optional custom decode function for testing.

        Returns:
            Decoded Shap-E mesh object (typically TorchMesh or TriMesh).
        """
        active_transmitter = transmitter or self._transmitter
        if active_transmitter is None:
            models = self.load_models()
            active_transmitter = models["transmitter"]

        # Support single latent passed from batch (list, tuple, or batched tensor)
        single_latent = latent
        if isinstance(latent, (list, tuple)) and len(latent) > 0:
            single_latent = latent[0]
        elif hasattr(latent, "shape") and hasattr(latent, "__getitem__"):
            shape = getattr(latent, "shape", ())
            if len(shape) >= 2 and shape[0] == 1:
                single_latent = latent[0]

        if decode_latent_mesh_fn is not None:
            try:
                raw = decode_latent_mesh_fn(active_transmitter, single_latent)
                if hasattr(raw, "tri_mesh") and callable(raw.tri_mesh):
                    return raw.tri_mesh()
                return raw
            except Exception as exc:
                raise RuntimeError(f"Failed to decode mesh: {exc}") from exc

        # Check if transmitter has direct decode method
        if hasattr(active_transmitter, "decode_to_mesh"):
            try:
                raw = active_transmitter.decode_to_mesh(single_latent)
                if hasattr(raw, "tri_mesh") and callable(raw.tri_mesh):
                    return raw.tri_mesh()
                return raw
            except Exception as exc:
                raise RuntimeError(f"Failed to decode mesh: {exc}") from exc

        # Fallback to standard shap_e utility
        try:
            from shap_e.util.notebooks import decode_latent_mesh as real_decode

            raw = real_decode(active_transmitter, single_latent)
            if hasattr(raw, "tri_mesh") and callable(raw.tri_mesh):
                return raw.tri_mesh()
            return raw
        except ImportError as exc:
            raise ImportError(
                "Shap-E is not installed. Please install the shap-e package "
                "to decode meshes."
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to decode mesh: {exc}") from exc

    def to_trimesh(self, decoded_mesh: Any) -> trimesh.Trimesh:
        """Convert a decoded Shap-E mesh into a trimesh.Trimesh object.

        Args:
            decoded_mesh: Mesh object with verts and faces attributes,
                          TorchMesh with tri_mesh() method,
                          or existing trimesh.Trimesh.

        Returns:
            trimesh.Trimesh geometry.

        Raises:
            MeshValidationError: If the mesh data is invalid or cannot be converted.
        """
        if isinstance(decoded_mesh, trimesh.Trimesh):
            return decoded_mesh

        if decoded_mesh is None:
            raise MeshValidationError("Decoded mesh is None")

        # Unwrap if TorchMesh object with tri_mesh() method
        source_mesh = decoded_mesh
        if hasattr(decoded_mesh, "tri_mesh") and callable(decoded_mesh.tri_mesh):
            decoded_mesh = decoded_mesh.tri_mesh()

        verts = getattr(
            decoded_mesh, "verts", getattr(decoded_mesh, "vertices", None)
        )
        faces = getattr(decoded_mesh, "faces", None)

        if verts is None or faces is None:
            raise MeshValidationError(
                "Decoded mesh must provide 'verts' (or 'vertices') and 'faces' attributes"
            )

        # Convert torch Tensor to numpy array if applicable
        if hasattr(verts, "detach"):
            verts = verts.detach().cpu().numpy()
        elif not isinstance(verts, np.ndarray):
            verts = np.asarray(verts)

        if hasattr(faces, "detach"):
            faces = faces.detach().cpu().numpy()
        elif not isinstance(faces, np.ndarray):
            faces = np.asarray(faces)

        if verts.ndim != 2 or verts.shape[1] != 3:
            raise MeshValidationError(
                f"Vertex array must have shape (N, 3), got shape {verts.shape}"
            )

        if faces.ndim != 2 or faces.shape[1] != 3:
            raise MeshValidationError(
                f"Faces array must have shape (M, 3), got shape {faces.shape}"
            )

        if len(verts) == 0:
            raise MeshValidationError("Decoded mesh has zero vertices")

        if len(faces) == 0:
            raise MeshValidationError("Decoded mesh has zero faces")

        try:
            mesh = trimesh.Trimesh(
                vertices=verts.astype(np.float64),
                faces=faces.astype(np.int64),
                process=False,
            )
        except Exception as exc:
            raise MeshValidationError(
                f"Failed to construct trimesh.Trimesh: {exc}"
            ) from exc

        # Attach valid vertex colors if available from decoded mesh
        vertex_colors = self._extract_vertex_colors(decoded_mesh, len(verts))
        if vertex_colors is None and source_mesh is not decoded_mesh:
            vertex_colors = self._extract_vertex_colors(source_mesh, len(verts))

        if vertex_colors is not None:
            try:
                mesh.visual.vertex_colors = vertex_colors
            except Exception:
                pass

        return mesh

    @staticmethod
    def _extract_vertex_colors(
        mesh_obj: Any, num_vertices: int
    ) -> Optional[np.ndarray]:
        """Extract and validate vertex colors from decoded mesh if present."""
        if mesh_obj is None:
            return None

        raw_colors = None

        # Check Shap-E vertex_channels dict
        channels = getattr(mesh_obj, "vertex_channels", None)
        if (
            isinstance(channels, dict)
            and "R" in channels
            and "G" in channels
            and "B" in channels
        ):
            try:
                r = (
                    channels["R"].detach().cpu().numpy()
                    if hasattr(channels["R"], "detach")
                    else np.asarray(channels["R"])
                )
                g = (
                    channels["G"].detach().cpu().numpy()
                    if hasattr(channels["G"], "detach")
                    else np.asarray(channels["G"])
                )
                b = (
                    channels["B"].detach().cpu().numpy()
                    if hasattr(channels["B"], "detach")
                    else np.asarray(channels["B"])
                )
                if r.ndim == 1 and g.ndim == 1 and b.ndim == 1:
                    raw_colors = np.column_stack([r, g, b])
            except Exception:
                raw_colors = None

        # Fallback to direct vertex_colors or colors attributes
        if raw_colors is None:
            for attr in ("vertex_colors", "colors"):
                val = getattr(mesh_obj, attr, None)
                if val is not None:
                    try:
                        raw_colors = (
                            val.detach().cpu().numpy()
                            if hasattr(val, "detach")
                            else np.asarray(val)
                        )
                        break
                    except Exception:
                        raw_colors = None

        if raw_colors is None:
            return None

        # Validation: Must be 2D array of shape (N, 3) or (N, 4)
        if not isinstance(raw_colors, np.ndarray) or raw_colors.ndim != 2:
            return None

        if raw_colors.shape[0] != num_vertices:
            return None

        if raw_colors.shape[1] not in (3, 4):
            return None

        # Must be finite
        if not np.isfinite(raw_colors).all():
            return None

        # Normalize/convert values:
        # If float in [0.0, 1.0], scale to [0, 255] uint8
        # If already [0, 255] integer or float, convert to uint8
        try:
            if np.issubdtype(raw_colors.dtype, np.floating):
                min_val = float(np.min(raw_colors))
                max_val = float(np.max(raw_colors))
                if min_val >= 0.0 and max_val <= 1.0:
                    return np.clip(
                        np.round(raw_colors * 255.0), 0, 255
                    ).astype(np.uint8)
                elif min_val >= 0.0 and max_val <= 255.0:
                    return np.clip(
                        np.round(raw_colors), 0, 255
                    ).astype(np.uint8)
                else:
                    return None
            elif np.issubdtype(raw_colors.dtype, np.integer):
                min_val = int(np.min(raw_colors))
                max_val = int(np.max(raw_colors))
                if min_val >= 0 and max_val <= 255:
                    return raw_colors.astype(np.uint8)
                else:
                    return None
            else:
                return None
        except Exception:
            return None

    def validate_mesh(self, mesh: trimesh.Trimesh) -> Any:
        """Validate the resulting trimesh using MeshValidator.

        Raises:
            MeshValidationError: If geometry validation fails.
        """
        return self.mesh_validator.validate_or_raise(mesh)

    def _resolve_components(
        self, components: Optional[Any]
    ) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
        """Extract transmitter, text_model, and diffusion from components if provided."""
        if components is None:
            return None, None, None

        transmitter = None
        model = None
        diffusion = None

        if hasattr(components, "transmitter"):
            transmitter = components.transmitter
        elif isinstance(components, dict):
            transmitter = components.get("transmitter")

        if hasattr(components, "text_model"):
            model = components.text_model
        elif hasattr(components, "model"):
            model = components.model
        elif isinstance(components, dict):
            model = components.get("text_model") or components.get("model")

        if hasattr(components, "diffusion"):
            diffusion = components.diffusion
        elif isinstance(components, dict):
            diffusion = components.get("diffusion")

        return transmitter, model, diffusion

    def generate(
        self,
        prompt: str,
        components: Optional[Any] = None,
        **kwargs: Any,
    ) -> trimesh.Trimesh:
        """Generate a validated 3D mesh from a text prompt.

        Follows the generation_fn(prompt, components) contract.

        Args:
            prompt: Text prompt describing the 3D asset.
            components: Optional pre-loaded ModelComponents or dict.
            **kwargs: Additional parameters (guidance_scale, karras_steps, custom hooks).

        Returns:
            Validated trimesh.Trimesh object.

        Raises:
            ValueError: If prompt is empty or invalid.
            ImportError: If shap-e is required but not installed.
            RuntimeError: If latent sampling or mesh decoding fails.
            MeshValidationError: If the produced mesh fails quality validation.
        """
        if not prompt or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        cleaned_prompt = prompt.strip()

        # Extract pre-loaded components if supplied
        c_transmitter, c_model, c_diffusion = self._resolve_components(components)

        # Ensure required models are available
        active_transmitter = (
            c_transmitter or kwargs.get("transmitter") or self._transmitter
        )
        active_model = c_model or kwargs.get("model") or self._model
        active_diffusion = (
            c_diffusion or kwargs.get("diffusion") or self._diffusion
        )

        if (
            active_transmitter is None
            or active_model is None
            or active_diffusion is None
        ):
            loaded = self.load_models(
                load_model_fn=kwargs.get("load_model_fn"),
                load_config_fn=kwargs.get("load_config_fn"),
                diffusion_from_config_fn=kwargs.get("diffusion_from_config_fn"),
            )
            active_transmitter = active_transmitter or loaded["transmitter"]
            active_model = active_model or loaded["model"]
            active_diffusion = active_diffusion or loaded["diffusion"]

        # Sample latents
        sample_latents_fn = kwargs.get("sample_latents_fn")
        guidance_scale = kwargs.get("guidance_scale", self.guidance_scale)
        karras_steps = kwargs.get("karras_steps", self.karras_steps)

        latents = self.sample_latents(
            prompt=cleaned_prompt,
            model=active_model,
            diffusion=active_diffusion,
            batch_size=1,
            guidance_scale=guidance_scale,
            karras_steps=karras_steps,
            sample_latents_fn=sample_latents_fn,
        )

        # Decode mesh
        decode_latent_mesh_fn = kwargs.get("decode_latent_mesh_fn")
        raw_mesh = self.decode_mesh(
            latent=latents,
            transmitter=active_transmitter,
            decode_latent_mesh_fn=decode_latent_mesh_fn,
        )

        # Convert to trimesh
        mesh = self.to_trimesh(raw_mesh)

        # Validate geometry
        self.validate_mesh(mesh)

        return mesh

    def __call__(
        self,
        prompt: str,
        components: Optional[Any] = None,
        **kwargs: Any,
    ) -> trimesh.Trimesh:
        """Allow the adapter instance to be invoked directly as generation_fn."""
        return self.generate(prompt, components, **kwargs)
