"""Unit tests for ShapEInferenceAdapter."""

import numpy as np
import pytest
import trimesh

from ai_generation.generation_validator import MeshValidationError
from ai_generation.generator import TextTo3DGenerator
from ai_generation.model_manager import ModelManager, ModelStatus
from ai_generation.models.model_loader import ModelComponents
from ai_generation.models.shap_e_adapter import ShapEInferenceAdapter


class FakeShapEMesh:
    """Mock object simulating the output of Shap-E tri_mesh()."""

    def __init__(self, verts=None, faces=None):
        box = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
        self.verts = verts if verts is not None else np.asarray(box.vertices, dtype=np.float32)
        self.faces = faces if faces is not None else np.asarray(box.faces, dtype=np.int32)


class FakeTorchMesh:
    """Mock object simulating Shap-E TorchMesh with a .tri_mesh() method."""

    def __init__(self, verts=None, faces=None):
        self._inner = FakeShapEMesh(verts=verts, faces=faces)

    def tri_mesh(self):
        return self._inner


class FakeTensor:
    """Mock tensor object with detach().cpu().numpy() interface."""

    def __init__(self, data):
        self._data = np.asarray(data)

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self._data


class FakeTensorMesh:
    """Mock Shap-E mesh whose vertices and faces are torch-like tensors."""

    def __init__(self):
        box = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
        self.verts = FakeTensor(box.vertices)
        self.faces = FakeTensor(box.faces)


# ---------------------------------------------------------------------------
# Device configuration tests
# ---------------------------------------------------------------------------


def test_reexported_import():
    from ai_generation.shap_e_adapter import (
        ShapEInferenceAdapter as ReexportedAdapter,
    )

    assert ReexportedAdapter is ShapEInferenceAdapter


def test_device_detection():
    detected = ShapEInferenceAdapter.detect_device()
    assert detected in {"cpu", "cuda"}


def test_explicit_cpu_device():
    adapter = ShapEInferenceAdapter(device="cpu")
    assert adapter.device == "cpu"


def test_explicit_cuda_device():
    adapter = ShapEInferenceAdapter(device="cuda")
    assert adapter.device == "cuda"


def test_invalid_device_raises_value_error():
    with pytest.raises(ValueError, match="Invalid device"):
        ShapEInferenceAdapter(device="tpu_v4")


# ---------------------------------------------------------------------------
# Model loading and caching tests
# ---------------------------------------------------------------------------


def test_adapter_starts_unloaded():
    adapter = ShapEInferenceAdapter(device="cpu")
    assert adapter.is_loaded is False


def test_model_loading_and_caching():
    load_model_calls = []
    load_config_calls = []
    diffusion_calls = []

    def fake_load_model(name, device):
        load_model_calls.append((name, device))
        return f"model-{name}"

    def fake_load_config(name):
        load_config_calls.append(name)
        return {"config_name": name}

    def fake_diffusion_from_config(config):
        diffusion_calls.append(config)
        return "fake-diffusion"

    adapter = ShapEInferenceAdapter(device="cpu")

    # First load
    models = adapter.load_models(
        load_model_fn=fake_load_model,
        load_config_fn=fake_load_config,
        diffusion_from_config_fn=fake_diffusion_from_config,
    )

    assert adapter.is_loaded is True
    assert models["transmitter"] == "model-transmitter"
    assert models["model"] == "model-text300M"
    assert models["diffusion"] == "fake-diffusion"
    assert len(load_model_calls) == 2
    assert len(load_config_calls) == 1
    assert len(diffusion_calls) == 1

    # Second load (must use cache without re-invoking loaders)
    cached_models = adapter.load_models(
        load_model_fn=fake_load_model,
        load_config_fn=fake_load_config,
        diffusion_from_config_fn=fake_diffusion_from_config,
    )

    assert cached_models["transmitter"] is models["transmitter"]
    assert len(load_model_calls) == 2  # No new calls
    assert len(load_config_calls) == 1
    assert len(diffusion_calls) == 1


def test_unload_releases_models():
    adapter = ShapEInferenceAdapter(device="cpu")
    adapter.load_models(
        load_model_fn=lambda name, device: f"m-{name}",
        load_config_fn=lambda name: {},
        diffusion_from_config_fn=lambda cfg: "diff",
    )
    assert adapter.is_loaded is True

    adapter.unload()
    assert adapter.is_loaded is False


def test_model_loading_failure_wraps_runtime_error():
    def failing_loader(name, device):
        raise ValueError("Corrupt weights checkpoint")

    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(RuntimeError, match="Failed to load Shap-E model components"):
        adapter.load_models(
            load_model_fn=failing_loader,
            load_config_fn=lambda name: {},
            diffusion_from_config_fn=lambda cfg: "diff",
        )
    assert adapter.is_loaded is False


# ---------------------------------------------------------------------------
# Prompt conditioning & latent sampling tests
# ---------------------------------------------------------------------------


def test_sample_latents_passes_prompt_and_params():
    sampled_kwargs = {}

    def fake_sample_latents(**kwargs):
        sampled_kwargs.update(kwargs)
        return ["fake-latent-vector"]

    adapter = ShapEInferenceAdapter(device="cpu", guidance_scale=12.5, karras_steps=32)

    latents = adapter.sample_latents(
        prompt="a sleek red racing car",
        model="fake-model",
        diffusion="fake-diffusion",
        sample_latents_fn=fake_sample_latents,
    )

    assert latents == ["fake-latent-vector"]
    assert sampled_kwargs["batch_size"] == 1
    assert sampled_kwargs["model"] == "fake-model"
    assert sampled_kwargs["diffusion"] == "fake-diffusion"
    assert sampled_kwargs["guidance_scale"] == 12.5
    assert sampled_kwargs["model_kwargs"] == {"texts": ["a sleek red racing car"]}
    assert sampled_kwargs["karras_steps"] == 32
    assert sampled_kwargs["progress"] is False
    assert sampled_kwargs["clip_denoised"] is True
    assert sampled_kwargs["use_karras"] is True
    assert sampled_kwargs["use_fp16"] is False  # cpu device


# ---------------------------------------------------------------------------
# Mesh decoding & conversion tests
# ---------------------------------------------------------------------------


def test_decode_mesh_with_callable():
    decode_calls = []

    def fake_decode(transmitter, latent):
        decode_calls.append((transmitter, latent))
        return FakeShapEMesh()

    adapter = ShapEInferenceAdapter(device="cpu")
    mesh = adapter.decode_mesh(
        latent="latent-1",
        transmitter="fake-transmitter",
        decode_latent_mesh_fn=fake_decode,
    )

    assert isinstance(mesh, FakeShapEMesh)
    assert decode_calls == [("fake-transmitter", "latent-1")]


def test_decode_mesh_unwraps_torch_mesh():
    def fake_decode(transmitter, latent):
        return FakeTorchMesh()

    adapter = ShapEInferenceAdapter(device="cpu")
    mesh = adapter.decode_mesh(
        latent="latent-1",
        transmitter="fake-transmitter",
        decode_latent_mesh_fn=fake_decode,
    )
    assert isinstance(mesh, FakeShapEMesh)


def test_decode_mesh_with_transmitter_method():
    class TransmitterWithDecode:
        def decode_to_mesh(self, latent):
            return FakeShapEMesh()

    adapter = ShapEInferenceAdapter(device="cpu")
    mesh = adapter.decode_mesh(
        latent=["latent-item"],
        transmitter=TransmitterWithDecode(),
    )
    assert isinstance(mesh, FakeShapEMesh)


def test_to_trimesh_from_shap_e_mesh():
    adapter = ShapEInferenceAdapter(device="cpu")
    raw = FakeShapEMesh()

    tm = adapter.to_trimesh(raw)

    assert isinstance(tm, trimesh.Trimesh)
    assert len(tm.vertices) == len(raw.verts)
    assert len(tm.faces) == len(raw.faces)


def test_to_trimesh_from_torch_mesh():
    adapter = ShapEInferenceAdapter(device="cpu")
    torch_mesh = FakeTorchMesh()

    tm = adapter.to_trimesh(torch_mesh)

    assert isinstance(tm, trimesh.Trimesh)
    assert len(tm.vertices) > 0
    assert len(tm.faces) > 0


def test_to_trimesh_from_tensor_mesh():
    adapter = ShapEInferenceAdapter(device="cpu")
    tensor_mesh = FakeTensorMesh()

    tm = adapter.to_trimesh(tensor_mesh)

    assert isinstance(tm, trimesh.Trimesh)
    assert len(tm.vertices) > 0
    assert len(tm.faces) > 0


def test_to_trimesh_passes_existing_trimesh():
    adapter = ShapEInferenceAdapter(device="cpu")
    existing = trimesh.creation.box()
    assert adapter.to_trimesh(existing) is existing


# ---------------------------------------------------------------------------
# Validation & error handling tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("invalid_prompt", ["", "   ", None, 12345])
def test_generate_invalid_prompt_raises_value_error(invalid_prompt):
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(ValueError, match="Prompt must be a non-empty string"):
        adapter.generate(invalid_prompt)


def test_to_trimesh_none_raises_validation_error():
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(MeshValidationError, match="Decoded mesh is None"):
        adapter.to_trimesh(None)


def test_to_trimesh_missing_attributes_raises_validation_error():
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(MeshValidationError, match="must provide 'verts'"):
        adapter.to_trimesh(object())


def test_to_trimesh_empty_geometry_raises_validation_error():
    adapter = ShapEInferenceAdapter(device="cpu")
    empty_mesh = FakeShapEMesh(
        verts=np.zeros((0, 3)),
        faces=np.zeros((0, 3)),
    )
    with pytest.raises(MeshValidationError, match="zero vertices"):
        adapter.to_trimesh(empty_mesh)


def test_to_trimesh_invalid_shape_raises_validation_error():
    adapter = ShapEInferenceAdapter(device="cpu")
    bad_shape_mesh = FakeShapEMesh(
        verts=np.zeros((4, 2)),  # 2D coordinates instead of 3D
        faces=np.zeros((2, 3)),
    )
    with pytest.raises(MeshValidationError, match="shape"):
        adapter.to_trimesh(bad_shape_mesh)


def test_validation_fails_on_nan_vertices():
    adapter = ShapEInferenceAdapter(device="cpu")
    nan_verts = np.array([
        [0.0, 0.0, 0.0],
        [1.0, np.nan, 0.0],
        [0.0, 1.0, 0.0],
    ])
    faces = np.array([[0, 1, 2]])
    nan_mesh = FakeShapEMesh(verts=nan_verts, faces=faces)

    with pytest.raises(MeshValidationError, match="non-finite vertex"):
        adapter.generate(
            prompt="a nan box",
            sample_latents_fn=lambda **kw: ["latent"],
            decode_latent_mesh_fn=lambda t, l: nan_mesh,
            components={"model": "m", "transmitter": "t", "diffusion": "d"},
        )


# ---------------------------------------------------------------------------
# Missing dependency handling tests
# ---------------------------------------------------------------------------


def test_missing_shap_e_raises_import_error_on_load():
    """When shap_e is not installed, calling real load_models raises clean ImportError."""
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(ImportError, match="Shap-E is not installed"):
        adapter.load_models()


def test_missing_shap_e_raises_import_error_on_sample_latents():
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(ImportError, match="Shap-E is not installed"):
        adapter.sample_latents(
            prompt="chair",
            model="dummy-model",
            diffusion="dummy-diffusion",
        )


def test_missing_shap_e_raises_import_error_on_decode():
    adapter = ShapEInferenceAdapter(device="cpu")
    with pytest.raises(ImportError, match="Shap-E is not installed"):
        adapter.decode_mesh(
            latent="latent",
            transmitter="dummy-transmitter",
        )


# ---------------------------------------------------------------------------
# Contract compliance & end-to-end integration tests
# ---------------------------------------------------------------------------


def test_generate_and_callable_interface():
    adapter = ShapEInferenceAdapter(device="cpu")

    def mock_sample(**kwargs):
        return ["mock-latent"]

    def mock_decode(transmitter, latent):
        return FakeShapEMesh()

    # Via generate()
    mesh1 = adapter.generate(
        prompt="a stone archway",
        sample_latents_fn=mock_sample,
        decode_latent_mesh_fn=mock_decode,
        components={"model": "m", "transmitter": "t", "diffusion": "d"},
    )
    assert isinstance(mesh1, trimesh.Trimesh)

    # Via __call__()
    mesh2 = adapter(
        prompt="a stone archway",
        sample_latents_fn=mock_sample,
        decode_latent_mesh_fn=mock_decode,
        components={"model": "m", "transmitter": "t", "diffusion": "d"},
    )
    assert isinstance(mesh2, trimesh.Trimesh)


def test_generate_with_model_components_dataclass():
    adapter = ShapEInferenceAdapter(device="cpu")

    comps = ModelComponents(
        text_model="text-model-instance",
        transmitter="transmitter-instance",
        device="cpu",
    )

    captured = {}

    def mock_sample(**kwargs):
        captured["model"] = kwargs["model"]
        return ["mock-latent"]

    def mock_decode(transmitter, latent):
        captured["transmitter"] = transmitter
        return FakeShapEMesh()

    mesh = adapter.generate(
        prompt="a wooden bowl",
        components=comps,
        sample_latents_fn=mock_sample,
        decode_latent_mesh_fn=mock_decode,
        # Supply diffusion so load_models() isn't triggered
        diffusion="diffusion-from-test",
    )

    assert isinstance(mesh, trimesh.Trimesh)
    assert captured["model"] == "text-model-instance"
    assert captured["transmitter"] == "transmitter-instance"


def test_integration_with_text_to_3d_generator(tmp_path):
    """Verify adapter integrates cleanly into TextTo3DGenerator as generation_fn."""
    adapter = ShapEInferenceAdapter(device="cpu")

    # Wire adapter methods with mock implementations to avoid downloads
    adapter._model = "mock-model"
    adapter._transmitter = "mock-transmitter"
    adapter._diffusion = "mock-diffusion"

    class AdapterWrapper:
        """Callable wrapper passing the mock hooks to adapter."""

        def __call__(self, prompt, components):
            return adapter(
                prompt=prompt,
                components=components,
                sample_latents_fn=lambda **kw: ["latent"],
                decode_latent_mesh_fn=lambda t, l: FakeShapEMesh(),
            )

    class MockModelLoader:
        def load_components(self):
            return ModelComponents(
                text_model="mock-model",
                transmitter="mock-transmitter",
                device="cpu",
            )

    manager = ModelManager(device="cpu")
    generator = TextTo3DGenerator(
        model_manager=manager,
        model_loader=MockModelLoader(),
        metadata_directory=tmp_path / "metadata",
        generation_fn=AdapterWrapper(),
    )

    result = generator.generate("A classic table")

    assert result.output_path.exists()
    assert manager.get_status("shap-e") == ModelStatus.READY
    assert result.metadata.prompt == "A classic table"
