from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.api.routes import router as api_router
from app.frontend.routes import router as frontend_router

app = FastAPI(
    title="Accessibility Linter",
    version="0.1.0",
    description="Service for linting HTML/URL against WCAG rules",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(frontend_router)
app.include_router(api_router, prefix="/api")
