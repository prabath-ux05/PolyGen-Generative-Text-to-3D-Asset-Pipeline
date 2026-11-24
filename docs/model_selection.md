# Model Selection and Evaluation

## 1. Objective

PolyGen requires a text-to-3D generation model that can
convert text prompts into 3D assets.

## 2. Selected Model: OpenAI Shap-E

Shap-E is an open-source research model developed by OpenAI.
It supports generating 3D assets directly from text prompts.

Official repository:
https://github.com/openai/shap-e

## 3. Why Shap-E?

- Supports text-to-3D generation.
- Provides pretrained model components.
- Supports 3D asset representation.
- Can be integrated with Python.
- Provides a starting point for OBJ and other mesh exports.

## 4. Hardware Considerations

Development machine:
- Processor: Intel Core i3-1215U
- RAM: Approximately 8 GB
- GPU: Intel UHD Graphics
- NVIDIA CUDA: Not available
- Execution device: CPU

CPU inference may be slow and memory-intensive.
Actual generation performance must be benchmarked.

## 5. Alternative: TripoSR

TripoSR is primarily an image-to-3D model.
It requires an image as input, so it does not directly
meet our current text-to-3D requirement.

## 6. Current Implementation

The following components have been created:

- ModelManager: Registers and selects models.
- ShapEModelLoader: Provides lazy model loading.
- ModelStatus: Tracks model loading states.
- Automated tests: Verify selection, loading and error handling.

## 7. Current Limitations

- Shap-E model weights have not been downloaded.
- Actual text-to-3D inference has not been tested.
- CPU generation speed is not yet measured.
- OBJ export and mesh validation will be implemented
  in later development stages.

## 8. Next Evaluation Steps

1. Install and verify the Shap-E source package.
2. Test model loading.
3. Run sample text prompts.
4. Measure generation time and memory usage.
5. Validate generated 3D meshes.
