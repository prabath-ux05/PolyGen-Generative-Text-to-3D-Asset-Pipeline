
"""In-memory caching for texture images."""

from collections import OrderedDict
from pathlib import Path

from PIL import Image


class TextureCache:
    """Cache loaded texture images to reduce repeated disk reads."""

    def __init__(self, max_items: int = 20):
        if max_items < 1:
            raise ValueError("max_items must be at least 1.")

        self.max_items = max_items
        self._cache = OrderedDict()

    def load(self, image_path: str | Path) -> Image.Image:
        """Load a texture or return its cached copy."""

        path = Path(image_path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"Texture not found: {path}")

        if not path.is_file():
            raise ValueError(f"Texture path is not a file: {path}")

        stat = path.stat()
        cache_key = (str(path), stat.st_mtime_ns, stat.st_size)

        # Remove older cached versions of the same file.
        stale_keys = [
            key for key in self._cache
            if key[0] == str(path) and key != cache_key
        ]

        for key in stale_keys:
            del self._cache[key]

        # Return a copy when the image is already cached.
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key].copy()

        # Load the image and detach it from the file.
        with Image.open(path) as image:
            image.load()
            cached_image = image.copy()

        self._cache[cache_key] = cached_image

        # Remove the least recently used item when full.
        while len(self._cache) > self.max_items:
            self._cache.popitem(last=False)

        return cached_image.copy()

    def clear(self) -> None:
        """Remove all cached textures."""
        self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Return the number of cached texture images."""
        return len(self._cache)
