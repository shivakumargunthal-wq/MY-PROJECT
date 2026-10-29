import pytest
from backend.typing_logic import calculate_accuracy, calculate_speed_results, compare_characters


def test_wpm_calculation():
    result = calculate_speed_results("hello world", "hello world", elapsed_seconds=60)
    assert result["gross_wpm"] == 2.2
    assert result["correct_characters"] == 11


def test_accuracy_calculation():
    assert calculate_accuracy(8, 10) == 80.0


def test_empty_input_is_safe():
    result = calculate_speed_results("", "hello", elapsed_seconds=60)
    assert result["gross_wpm"] == 0
    assert result["accuracy"] == 100.0
    assert result["incorrect_characters"] == 5


def test_incorrect_characters():
    comparison = compare_characters("hello Xorld", "hello world")
    assert comparison["correct"] == 10
    assert comparison["incorrect"] == 1


def test_extra_characters_count_as_errors():
    comparison = compare_characters("hello world!!", "hello world")
    assert comparison["incorrect"] == 2
