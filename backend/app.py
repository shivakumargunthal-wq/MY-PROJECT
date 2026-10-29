import os
import sqlite3
import threading
import time
import uuid
from flask import Flask, jsonify, render_template, request

try:
    from .passages import get_random_passage
    from .typing_logic import calculate_speed_results, validate_submission
except ImportError:
    from passages import get_random_passage
    from typing_logic import calculate_speed_results, validate_submission

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "frontend", "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "frontend", "static"),
)
app.config["SECRET_KEY"] = os.environ.get("TYPEBLAZE_SECRET_KEY", "local-development-only-key")

DATABASE = os.path.join(os.path.dirname(__file__), "typeblaze.db")
sessions = {}
sessions_lock = threading.Lock()
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_DURATIONS = {30, 60, 120}


def database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS results (
                test_id TEXT PRIMARY KEY,
                passage TEXT NOT NULL,
                typed_text TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                duration INTEGER NOT NULL,
                gross_wpm REAL NOT NULL,
                net_wpm REAL NOT NULL,
                accuracy REAL NOT NULL,
                correct_characters INTEGER NOT NULL,
                incorrect_characters INTEGER NOT NULL,
                elapsed_seconds REAL NOT NULL,
                completed_at REAL NOT NULL
            )
        """)


def error_response(message, status=400):
    return jsonify({"ok": False, "error": message}), status


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "status": "healthy", "service": "TypeBlaze"})


@app.get("/api/passage")
def passage():
    difficulty = request.args.get("difficulty", "easy")
    if difficulty not in VALID_DIFFICULTIES:
        return error_response("Difficulty must be easy, medium, or hard")
    return jsonify({"ok": True, "passage": get_random_passage(difficulty), "difficulty": difficulty})


@app.post("/api/test/start")
def start_test():
    data = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty")
    try:
        duration = int(data.get("duration"))
    except (TypeError, ValueError):
        return error_response("Duration is required")

    if difficulty not in VALID_DIFFICULTIES:
        return error_response("Difficulty must be easy, medium, or hard")
    if duration not in VALID_DURATIONS:
        return error_response("Duration must be 30, 60, or 120 seconds")

    test_id = uuid.uuid4().hex
    passage = get_random_passage(difficulty)
    started_at = time.time()
    with sessions_lock:
        sessions[test_id] = {
            "passage": passage,
            "difficulty": difficulty,
            "duration": duration,
            "started_at": started_at,
            "finished": False,
        }
    return jsonify({
        "ok": True,
        "test_id": test_id,
        "passage": passage,
        "difficulty": difficulty,
        "duration": duration,
        "server_time": started_at,
    })


@app.post("/api/test/finish")
def finish_test():
    data = request.get_json(silent=True) or {}
    test_id = data.get("test_id")
    typed_text = data.get("typed_text")

    if not isinstance(test_id, str):
        return error_response("A valid test ID is required")
    valid_text, text_error = validate_submission(typed_text)
    if not valid_text:
        return error_response(text_error)

    now = time.time()
    with sessions_lock:
        session = sessions.get(test_id)
        if session is None:
            return error_response("Test session not found", 404)
        if session["finished"]:
            return error_response("This test has already been submitted", 409)

        elapsed = max(0.0, now - session["started_at"])
        grace_period = 2.0
        if elapsed > session["duration"] + grace_period:
            session["finished"] = True
            return error_response("Test session has expired", 410)

        session["finished"] = True
        # Completed text may finish before the duration; otherwise elapsed is capped at duration.
        elapsed = min(elapsed, float(session["duration"]))

    passage = session["passage"]
    finished_by_completion = typed_text.strip() == passage.strip()
    elapsed_seconds = elapsed if elapsed >= 1 else 1.0
    if not finished_by_completion and elapsed_seconds < session["duration"]:
        elapsed_seconds = min(elapsed_seconds, session["duration"])

    results = calculate_speed_results(
        typed_text, passage, elapsed_seconds=elapsed_seconds
    )
    result = {
        "test_id": test_id,
        "passage": passage,
        "typed_text": typed_text,
        "difficulty": session["difficulty"],
        "duration": session["duration"],
        "completed_at": now,
        **results,
        "completed": finished_by_completion,
        "feedback": performance_feedback(results["net_wpm"]),
    }

    with database() as connection:
        connection.execute("""
            INSERT OR IGNORE INTO results
            (test_id, passage, typed_text, difficulty, duration, gross_wpm, net_wpm,
             accuracy, correct_characters, incorrect_characters, elapsed_seconds, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_id, passage, typed_text, session["difficulty"], session["duration"],
            results["gross_wpm"], results["net_wpm"], results["accuracy"],
            results["correct_characters"], results["incorrect_characters"],
            elapsed_seconds, now,
        ))
    return jsonify({"ok": True, "result": result})


@app.get("/api/results/<test_id>")
def get_result(test_id):
    if not test_id or len(test_id) > 100:
        return error_response("Invalid test ID")
    with database() as connection:
        row = connection.execute("SELECT * FROM results WHERE test_id = ?", (test_id,)).fetchone()
    if row is None:
        return error_response("Result not found", 404)
    result = dict(row)
    result["ok"] = True
    result["completed"] = len(result["typed_text"] or "") >= len(result["passage"] or "")
    return jsonify({"ok": True, "result": result})


def performance_feedback(net_wpm):
    if net_wpm >= 80:
        return "Blazing fast! Your speed and control are exceptional."
    if net_wpm >= 50:
        return "Excellent pace. You are typing comfortably and efficiently."
    if net_wpm >= 30:
        return "Great progress! Build consistency to push your speed higher."
    if net_wpm >= 15:
        return "Good foundation. Focus on accuracy and rhythm to improve."
    return "Keep practicing! Accuracy first, and speed will follow."


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return error_response("Endpoint not found", 404)
    return render_template("index.html"), 404


init_database()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
