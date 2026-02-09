# Functional Programming for AI Video Generation

A comprehensive guide to using functional programming principles in AI video generation systems.

## Key Principles

### 1. Pure Functions
- **No side effects**: Functions don't modify external state
- **Deterministic**: Same input always produces same output
- **Testable**: Easy to test and reason about

```python
# Pure function example
def normalize_frames(frames: torch.Tensor) -> torch.Tensor:
    """Normalize video frames to [0, 1] range."""
    return (frames - frames.min()) / (frames.max() - frames.min())

# Not pure - modifies external state
def process_frames_impure(frames, output_path):
    frames = normalize_frames(frames)  # Pure
    save_to_file(frames, output_path)  # Side effect
    return frames
```

### 2. Immutability
- **Use dataclasses with `frozen=True`**
- **Create new objects instead of modifying existing ones**
- **Use `replace()` for updates**

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class VideoConfig:
    prompt: str
    num_frames: int
    height: int
    width: int

# Create variations (immutable)
base_config = VideoConfig("sunset", 16, 512, 512)
high_quality = replace(base_config, num_frames=32, height=1024)
```

### 3. Function Composition
- **Combine functions using `compose()` or `pipe()`**
- **Build complex pipelines from simple functions**

```python
from functools import reduce

def compose(*functions):
    """Compose functions from right to left."""
    return reduce(lambda f, g: lambda x: f(g(x)), functions)

# Pipeline: normalize -> resize -> add_noise
pipeline = compose(
    add_noise,
    partial(resize_frames, size=(256, 256)),
    normalize_frames
)

result = pipeline(video_frames)
```

### 4. Higher-Order Functions
- **Functions that take functions as arguments**
- **Functions that return functions**

```python
def map_transform(func, data):
    """Apply function to each element."""
    return list(map(func, data))

def filter_data(predicate, data):
    """Filter data using predicate."""
    return list(filter(predicate, data))

def reduce_data(reducer, data, initial=None):
    """Reduce data using reducer function."""
    if initial is not None:
        return reduce(reducer, data, initial)
    return reduce(reducer, data)

# Usage
frame_counts = map_transform(lambda x: x["frames"], video_configs)
high_quality = filter_data(lambda x: x["quality"] == "high", video_configs)
total_frames = reduce_data(lambda acc, x: acc + x["frames"], video_configs, 0)
```

### 5. Currying and Partial Application
- **Break down functions with multiple parameters**
- **Create specialized functions from general ones**

```python
from functools import partial

def create_video_generator(model_name, device, precision):
    def generate_video(prompt, num_frames):
        return f"Generated using {model_name} on {device}"
    return generate_video

# Partial application
generate_high_quality = partial(
    create_video_generator("diffusion-v1", "cuda", "fp16"),
    num_frames=32
)

result = generate_high_quality("beautiful sunset")
```

## Benefits

### 1. Testability
```python
def test_normalize_frames():
    input_frames = torch.tensor([0, 5, 10])
    expected = torch.tensor([0.0, 0.5, 1.0])
    result = normalize_frames(input_frames)
    assert torch.allclose(result, expected)
```

### 2. Parallelization
```python
async def process_batch_parallel(configs):
    """Process multiple configs in parallel."""
    tasks = [process_config(config) for config in configs]
    return await asyncio.gather(*tasks)
```

### 3. Debugging
```python
def debug_pipeline():
    """Debug pipeline step by step."""
    frames = load_frames()
    print(f"Original: {frames.shape}")
    
    normalized = normalize_frames(frames)
    print(f"Normalized: {normalized.shape}")
    
    resized = resize_frames(normalized, (256, 256))
    print(f"Resized: {resized.shape}")
    
    return resized
```

### 4. Reusability
```python
# Reusable processing functions
def create_processing_pipeline(*steps):
    """Create processing pipeline from steps."""
    return compose(*steps)

# Different pipelines using same functions
fast_pipeline = create_processing_pipeline(
    normalize_frames,
    partial(resize_frames, size=(256, 256))
)

quality_pipeline = create_processing_pipeline(
    normalize_frames,
    partial(resize_frames, size=(1024, 1024)),
    add_noise
)
```

## Best Practices

### 1. Avoid Classes When Possible
```python
# Instead of class-based approach
class VideoProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, frames):
        return self._normalize(frames)
    
    def _normalize(self, frames):
        return frames / 255.0

# Use functional approach
def process_video(frames, config):
    return normalize_frames(frames, config)

def normalize_frames(frames, config):
    return frames / 255.0
```

### 2. Use Type Hints
```python
from typing import Callable, List, Dict, Any, Tuple

def create_pipeline(
    steps: List[Callable[[torch.Tensor], torch.Tensor]]
) -> Callable[[torch.Tensor], torch.Tensor]:
    """Create processing pipeline."""
    return compose(*steps)
```

### 3. Handle Errors Functionally
```python
from dataclasses import dataclass
from typing import Union

@dataclass
class Success:
    value: Any

@dataclass
class Failure:
    error: str

Result = Union[Success, Failure]

def safe_operation(operation: Callable, data: Any) -> Result:
    """Safely execute operation."""
    try:
        return Success(operation(data))
    except Exception as e:
        return Failure(str(e))
```

### 4. Use Lazy Evaluation
```python
def create_video_generator(prompts: List[str]):
    """Lazy video generator."""
    for i, prompt in enumerate(prompts):
        yield f"video_{i}_{prompt.replace(' ', '_')}.mp4"

# Only generates videos when needed
for video in create_video_generator(["sunset", "ocean"]):
    process_video(video)
```

## Examples

### Video Processing Pipeline
```python
def create_video_pipeline():
    """Create complete video processing pipeline."""
    
    # Pure functions
    def load_frames(path: str) -> torch.Tensor:
        return torch.load(path)
    
    def normalize_frames(frames: torch.Tensor) -> torch.Tensor:
        return (frames - frames.min()) / (frames.max() - frames.min())
    
    def resize_frames(frames: torch.Tensor, size: Tuple[int, int]) -> torch.Tensor:
        return torch.nn.functional.interpolate(
            frames.unsqueeze(0), size=size, mode='bilinear'
        ).squeeze(0)
    
    def save_frames(frames: torch.Tensor, path: str) -> str:
        torch.save(frames, path)
        return path
    
    # Compose pipeline
    pipeline = compose(
        partial(save_frames, path="output.pt"),
        partial(resize_frames, size=(256, 256)),
        normalize_frames,
        load_frames
    )
    
    return pipeline

# Usage
pipeline = create_video_pipeline()
output_path = pipeline("input.pt")
```

### Async Processing
```python
async def process_videos_async(video_paths: List[str]) -> List[str]:
    """Process multiple videos asynchronously."""
    
    async def process_single_video(path: str) -> str:
        # Simulate processing
        await asyncio.sleep(1)
        return f"processed_{path}"
    
    # Process in parallel
    tasks = [process_single_video(path) for path in video_paths]
    return await asyncio.gather(*tasks)
```

### Configuration Management
```python
def create_config_validator():
    """Create configuration validator."""
    
    def validate_dimensions(config: Dict[str, Any]) -> bool:
        return config.get("height", 0) % 64 == 0 and config.get("width", 0) % 64 == 0
    
    def validate_frames(config: Dict[str, Any]) -> bool:
        return 8 <= config.get("num_frames", 0) <= 64
    
    def validate_prompt(config: Dict[str, Any]) -> bool:
        return bool(config.get("prompt", "").strip())
    
    # Combine validators
    validators = [validate_dimensions, validate_frames, validate_prompt]
    
    def validate_config(config: Dict[str, Any]) -> bool:
        return all(validator(config) for validator in validators)
    
    return validate_config
```

## Conclusion

Functional programming provides:
- **Better testability** through pure functions
- **Improved maintainability** through immutability
- **Enhanced reusability** through composition
- **Easier debugging** through clear data flow
- **Better parallelization** through stateless operations

Use these principles to create more robust, maintainable, and scalable AI video generation systems. 