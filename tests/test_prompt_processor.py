import pytest

from ai_generation.prompt_processor import (
    ProcessedPrompt,
    PromptProcessor,
    PromptValidationError,
)


def test_clean_prompt_removes_extra_spaces():
    processor = PromptProcessor()
    assert processor.clean_prompt("  a   wooden   chair  ") == "a wooden chair"


def test_clean_prompt_handles_newlines():
    processor = PromptProcessor()
    assert processor.clean_prompt("a wooden\nchair") == "a wooden chair"


def test_clean_prompt_normalizes_unicode():
    processor = PromptProcessor()
    assert processor.clean_prompt("Ａ wooden chair") == "A wooden chair"


def test_process_valid_prompt():
    result = PromptProcessor().process_prompt("A wooden chair")
    assert result.cleaned_prompt == "A wooden chair"
    assert result.word_count == 3
    assert result.character_count == 14


def test_process_prompt_preserves_original():
    original = "  A   wooden chair  "
    result = PromptProcessor().process_prompt(original)
    assert result.original_prompt == original


def test_empty_prompt_is_rejected():
    with pytest.raises(PromptValidationError):
        PromptProcessor().process_prompt("   ")


def test_short_prompt_is_rejected():
    with pytest.raises(PromptValidationError):
        PromptProcessor(min_length=5).process_prompt("cat")


def test_long_prompt_is_rejected():
    with pytest.raises(PromptValidationError):
        PromptProcessor(max_length=10).process_prompt("A very large object")


def test_non_string_prompt_is_rejected():
    with pytest.raises(PromptValidationError):
        PromptProcessor().process_prompt(123)


def test_null_character_is_rejected():
    with pytest.raises(PromptValidationError):
        PromptProcessor().process_prompt("wood\x00en chair")


def test_result_is_processed_prompt():
    result = PromptProcessor().process_prompt("A small red car")
    assert isinstance(result, ProcessedPrompt)


def test_result_converts_to_dictionary():
    result = PromptProcessor().process_prompt("A small red car")
    data = result.to_dict()
    assert data["cleaned_prompt"] == "A small red car"
    assert data["word_count"] == 4


def test_invalid_minimum_length_configuration():
    with pytest.raises(ValueError):
        PromptProcessor(min_length=0)


def test_invalid_length_range_configuration():
    with pytest.raises(ValueError):
        PromptProcessor(min_length=20, max_length=10)
