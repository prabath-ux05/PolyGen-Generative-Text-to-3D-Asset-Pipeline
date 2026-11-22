
"""Tests for the texture caching system."""

import pytest
from PIL import Image

from texture_engine.texture_cache import TextureCache


def test_load_texture_successfully(tmp_path):
    """A texture should load and enter the cache."""
    path = tmp_path / "texture.png"
    Image.new("RGB", (128, 128), "red").save(path)

    cache = TextureCache()
    image = cache.load(path)

    assert image.size == (128, 128)
    assert image.mode == "RGB"
    assert cache.cache_size == 1


def test_repeated_load_uses_cache(tmp_path):
    """Loading the same texture twice should reuse the cache."""
    path = tmp_path / "texture.png"
    Image.new("RGB", (64, 64), "blue").save(path)

    cache = TextureCache()

    first = cache.load(path)
    second = cache.load(path)

    assert first.tobytes() == second.tobytes()
    assert first is not second
    assert cache.cache_size == 1


def test_returned_image_does_not_modify_cache(tmp_path):
    """Changing a returned image must not change the cached image."""
    path = tmp_path / "texture.png"
    Image.new("RGB", (32, 32), "red").save(path)

    cache = TextureCache()

    first = cache.load(path)
    first.paste("blue", (0, 0, 32, 32))

    second = cache.load(path)

    assert second.getpixel((0, 0)) == (255, 0, 0)


def test_clear_cache(tmp_path):
    """Clearing the cache should remove all cached textures."""
    path = tmp_path / "texture.png"
    Image.new("RGB", (64, 64)).save(path)

    cache = TextureCache()
    cache.load(path)

    cache.clear()

    assert cache.cache_size == 0


def test_missing_texture_raises_error(tmp_path):
    """Loading a missing texture should raise FileNotFoundError."""
    cache = TextureCache()

    with pytest.raises(FileNotFoundError):
        cache.load(tmp_path / "missing.png")


def test_cache_respects_maximum_items(tmp_path):
    """The cache should remove the least recently used item."""
    cache = TextureCache(max_items=2)

    first_path = tmp_path / "first.png"
    second_path = tmp_path / "second.png"
    third_path = tmp_path / "third.png"

    Image.new("RGB", (16, 16), "red").save(first_path)
    Image.new("RGB", (16, 16), "green").save(second_path)
    Image.new("RGB", (16, 16), "blue").save(third_path)

    cache.load(first_path)
    cache.load(second_path)

    # Access the first image again, making the second least recently used.
    cache.load(first_path)

    cache.load(third_path)

    assert cache.cache_size == 2

    # The second image should have been evicted.
    assert str(second_path.resolve()) not in [
        key[0] for key in cache._cache
    ]


def test_invalid_max_items():
    """A cache size below one should raise ValueError."""
    with pytest.raises(ValueError, match="at least 1"):
        TextureCache(max_items=0)


def test_updated_texture_is_reloaded(tmp_path):
    """A changed file should replace its older cached version."""
    path = tmp_path / "texture.png"

    Image.new("RGB", (32, 32), "red").save(path)

    cache = TextureCache()
    first = cache.load(path)

    Image.new("RGB", (64, 64), "blue").save(path)

    second = cache.load(path)

    assert first.size == (32, 32)
    assert second.size == (64, 64)
    assert cache.cache_size == 1
