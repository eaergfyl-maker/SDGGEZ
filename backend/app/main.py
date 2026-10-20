"""App entry point. Owner: Member 1.

    uvicorn backend.app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config
from .api.routes import router

app = FastAPI(title="Future-Ready RPG", version="0.1.0")
app.include_router(router, prefix="/api")
app.mount("/", StaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")
