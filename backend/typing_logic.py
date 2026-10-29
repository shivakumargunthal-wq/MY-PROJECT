from time import monotonic


def compare_characters(typed_text, passage):
    """Compare text by position; missing positions are errors and extras count as errors."""
    typed_text = typed_text or ""
    passage = passage or ""
    correct = 0
    incorrect = 0

    for index in range(max(len(typed_text), len(passage))):
        expected = passage[index] if index < len(passage) else None
        actual = typed_text[index] if index < len(typed_text) else None
        if actual is not None and actual == expected:
            correct += 1
        else:
            incorrect += 1

    return {"correct": correct, "incorrect": incorrect}


def calculate_accuracy(correct, total):
    if total <= 0:
        return 100.0
    return round((max(correct, 0) / total) * 100, 2)


def elapsed_minutes(started_at, finished_at, minimum_seconds=1.0):
    elapsed = max(minimum_seconds, float(finished_at) - float(started_at))
    return elapsed / 60.0


def calculate_speed_results(typed_text, passage, started_at=None, finished_at=None, elapsed_seconds=None):
    typed_text = typed_text or ""
    passage = passage or ""
    comparison = compare_characters(typed_text, passage)
    if elapsed_seconds is None:
        if started_at is None or finished_at is None:
            elapsed_seconds = 0
        else:
            elapsed_seconds = max(1.0, float(finished_at) - float(started_at))

    elapsed_seconds = max(1.0, min(float(elapsed_seconds), 86400.0))
    total_submitted = len(typed_text)
    gross_wpm = round(((total_submitted / 5) / elapsed_seconds) * 60, 2)

    # One incorrect character deducts the same number of five-character words.
    error_penalty = comparison["incorrect"] / 5
    net_wpm = round(max(0, gross_wpm - error_penalty), 2)
    accuracy = calculate_accuracy(comparison["correct"], total_submitted)
    return {
        "gross_wpm": gross_wpm,
        "net_wpm": net_wpm,
        "accuracy": accuracy,
        "correct_characters": comparison["correct"],
        "incorrect_characters": comparison["incorrect"],
        "errors": comparison["incorrect"],
        "total_characters": total_submitted,
        "elapsed_seconds": round(elapsed_seconds, 2),
        "error_penalty_per_error_words": 0.2,
    }


def validate_submission(typed_text, max_length=5000):
    if not isinstance(typed_text, str):
        return False, "Typed text must be a string"
    if len(typed_text) > max_length:
        return False, "Typed text is too long"
    return True, None
