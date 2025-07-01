from typing import List, Optional

from bs4 import BeautifulSoup

from app.models.schemas import HTMLRequest, Issue, Report, URLRequest
from app.parsers import HTMLParser
from app.validators.wcag_validators import (
    AltTextValidator,
    ContrastValidator,
    SemanticStructureValidator,
    Validator,
)

parser = HTMLParser()

validators: List[Validator] = [
    AltTextValidator(),
    ContrastValidator(),
    SemanticStructureValidator(),
]


def lint_from_url(request: URLRequest) -> Report:
    html = parser.fetch(request.url)
    if html is None:
        raise ValueError(f"Cannot fetch URL: {request.url}")
    return _lint_html(html, url=str(request.url))


def lint_from_html(request: HTMLRequest) -> Report:
    return _lint_html(request.html)


def _lint_html(html: str, url: Optional[str] = None) -> Report:
    """
    Parse HTML and run all validators, produce report.
    """
    soup: BeautifulSoup = parser.parse(html)
    issues: List[Issue] = []
    for v in validators:
        issues.extend(v.validate(soup))

    total = len(issues)
    errors = sum(1 for i in issues if i.code.startswith("WCAG"))
    warnings = total - errors

    return Report(
        url=url,
        issues=issues,
        summary={"total": total, "errors": errors, "warnings": warnings},
    )
