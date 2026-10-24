# Clyro Frontend

This directory contains Clyro's browser interface.

## Structure

- `index.html` — the MVP interface, styles, and browser-side interaction.

The current frontend intentionally uses plain HTML, CSS, and JavaScript. FastAPI serves this page at `/`, while comparison requests go to `POST /api/compare`.

## Run locally

Start the FastAPI backend from the `backend` directory:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --app-dir .
```

Then open `http://127.0.0.1:8000`.

A separate JavaScript framework or frontend build step is not required for this MVP.
