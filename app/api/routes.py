from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import HTMLRequest, Report, URLRequest
from app.services.lint_service import lint_from_html, lint_from_url

router = APIRouter()


@router.post("/lint-url", response_model=Report)
def lint_url(payload: URLRequest):
    try:
        return lint_from_url(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lint-html", response_model=Report)
def lint_html(payload: HTMLRequest):
    try:
        return lint_from_html(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
