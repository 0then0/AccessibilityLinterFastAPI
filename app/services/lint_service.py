import ipaddress
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.models.schemas import (
    HTMLRequest,
    Issue,
    Report,
    SectionReport,
    URLRequest,
)
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
    """Fetch HTML from URL and lint all sections."""
    if not _is_safe_url(request.url):
        raise ValueError(f"URL points to forbidden network resource: {request.url}")
    html = parser.fetch(request.url)
    if html is None:
        raise ValueError(f"Cannot fetch URL: {request.url}")
    return _lint_with_sections(html, url=str(request.url))


def lint_from_html(request: HTMLRequest) -> Report:
    """Lint HTML string for all sections."""
    return _lint_with_sections(request.html, url=None)


def _is_safe_url(u: str) -> bool:
    """Disallow private or loopback IPs in URL hostname."""
    parsed = urlparse(str(u))
    hostname = parsed.hostname
    if not hostname:
        return False
    try:
        addr = ipaddress.ip_address(hostname)
        return not (addr.is_private or addr.is_loopback)
    except ValueError:
        # hostname is not an IP, allow
        return True


def _extract_sections(
    soup: BeautifulSoup,
) -> List[Tuple[str, BeautifulSoup, Optional[str]]]:
    results = []
    for idx, element in enumerate(soup.find_all("section")):
        id_attr = element.get("id")
        class_list = element.get("class") or []
        class_attr = class_list[0] if class_list else None
        heading = element.find(re.compile(r"h[1-6]"))
        heading_text = heading.get_text(strip=True) if heading else None

        if id_attr:
            name = f"section#{id_attr}"
        elif class_attr:
            name = f"section.{class_attr}"
        elif heading_text:
            name = f"section: {heading_text}"
        else:
            name = f"section-{idx + 1}"

        selector = f"section:nth-of-type({idx + 1})"
        results.append((name, element, selector))
    return results


def _extract_iframes(
    soup: BeautifulSoup,
) -> List[Tuple[str, BeautifulSoup, Optional[str]]]:
    results = []
    for idx, iframe in enumerate(soup.find_all("iframe")):
        src = iframe.get("src", "")
        title = iframe.get("title")
        if title:
            name = f"iframe: {title}"
        elif src:
            domain = urlparse(src).netloc
            name = f"iframe@{domain}"
        else:
            name = f"iframe-{idx + 1}"

        selector = f"iframe:nth-of-type({idx + 1})"
        html = parser.fetch(src) if src and _is_safe_url(src) else None
        iframe_soup = parser.parse(html) if html else BeautifulSoup(str(iframe), "lxml")
        results.append((name, iframe_soup, selector))
    return results


def _lint_with_sections(html: str, url: Optional[str]) -> Report:
    """
    Parse HTML, split into root + <section> + <iframe>, run validators,
    and build a Report with SectionReport entries.
    """
    root_soup = parser.parse(html)
    items: List[Tuple[str, BeautifulSoup, Optional[str]]] = []

    # root page section
    items.append(("root", root_soup, None))
    # page sections
    items.extend(_extract_sections(root_soup))
    # iframe contents
    items.extend(_extract_iframes(root_soup))

    sections: List[SectionReport] = []
    all_issues: List[Issue] = []

    for name, sect_soup, selector in items:
        issues: List[Issue] = []
        for v in validators:
            issues.extend(v.validate(sect_soup))
        sections.append(SectionReport(name=name, selector=selector, issues=issues))
        all_issues.extend(issues)

    total = len(all_issues)
    error_count = sum(1 for i in all_issues if i.code.startswith("WCAG"))
    warning_count = total - error_count

    summary = {"total": total, "errors": error_count, "warnings": warning_count}

    return Report(url=url, sections=sections, summary=summary)
