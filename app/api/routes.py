from fastapi import APIRouter, HTTPException

from app.models.schemas import HTMLRequest, Report, URLRequest
from app.services.lint_service import lint_from_html, lint_from_url

router = APIRouter()


@router.post("/lint-url", response_model=Report)
def lint_url(payload: URLRequest):
    """Lint a page by URL, with grouping by sections and iframes."""
    try:
        return lint_from_url(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lint-html", response_model=Report)
def lint_html(payload: HTMLRequest):
    """Lint raw HTML string, with grouping by sections and iframes."""
    try:
        return lint_from_html(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
