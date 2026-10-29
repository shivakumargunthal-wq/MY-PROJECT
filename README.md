# TypeBlaze

TypeBlaze is a responsive Flask typing speed tester with server-side sessions, timing, scoring, and result history.

## Requirements

- Python 3.10 or newer
- Flask and pytest

## Setup

```powershell
cd "c:\Users\shiva\OneDrive\Desktop\MY PROJECT"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python backend\app.py
```

Open `http://127.0.0.1:5000`.

## Tests

```powershell
python -m pytest -q
```

## Production deployment

Flask's built-in server is for local development only. Deploy behind a production WSGI server, for example Gunicorn on Linux:

```text
pip install gunicorn
gunicorn --workers 3 --bind 0.0.0.0:8000 backend.app:app
```

Use HTTPS, a persistent secret key, and a real database/session store for multiple application workers.

## Scoring method

- Standard word length: 5 characters.
- Gross WPM: `(characters typed / 5) / elapsed minutes`.
- Error penalty: each incorrect character subtracts 0.2 net WPM words; Net WPM is `max(0, gross WPM - incorrect characters / 5)`.
- Accuracy: correct character positions divided by all submitted characters, or 100% for empty submissions.
