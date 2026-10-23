# Running on Replit

This imported project keeps its existing FastAPI backend and plain JavaScript
frontend. FastAPI serves both the API and frontend; no separate frontend build
or server is needed.

## Start

Use the **Start application** workflow (the Run button), which runs:

```sh
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 5000
```

The app opens in Preview. API documentation is at `/docs`; the health endpoint
is `/api/health`.

Python dependencies are listed in `requirements.txt` and installed in Replit's
managed Python environment. Do not create a virtual environment.

## Configuration and data

No credentials or external services are required to run the default demo.
Until ingestion produces a database snapshot, trends use the explicitly labelled
mock dataset. SQLite defaults to `data/app.db`.

Optional ingestion settings are described in `.env.example`. Configure actual
credentials in Replit Secrets, not committed files. Do not trigger live ingestion
as part of startup or testing.

## Checks

```sh
python -m pytest -q
python scripts/validate_data.py
```

The data validator currently warns about the existing unverified course
`example_placeholder`. The refresh endpoint is protected: set `REFRESH_TOKEN` in Replit Secrets
to enable it (it also has a 30-minute cooldown).
