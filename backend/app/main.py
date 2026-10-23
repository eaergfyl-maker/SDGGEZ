"""App entry point. Owner: Member 1.

    uvicorn backend.app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config
from .api.routes import router

app = FastAPI(title="Future-Ready RPG", version="0.1.0")
app.include_router(router, prefix="/api")

class NoCacheStaticFiles(StaticFiles):
    """Make browser check with the server before reusing a cached file, so an update is
    picked up straight away. Unchaned files still cost only a tiny "304 Not Modified" reply."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache"
        return response
    
app.mount("/", NoCacheStaticFiles(directory=config.FRONTEND_DIR, html=True), name="frontend")