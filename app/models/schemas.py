from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class URLRequest(BaseModel):
    url: HttpUrl = Field(..., description="Page URL to lint")


class HTMLRequest(BaseModel):
    html: constr(min_length=1, max_length=100_000) = Field(
        ..., description="Raw HTML string to lint"
    )


class Issue(BaseModel):
    code: str = Field(..., description="WCAG rule code, e.g., 'WCAG1.1.1'")
    message: str = Field(..., description="Description of the issue")
    selector: Optional[str] = Field(
        None, description="CSS selector of affected element"
    )
    context: Optional[str] = Field(None, description="HTML snippet around the issue")


class SectionReport(BaseModel):
    name: str = Field(..., description="Section name or iframe identifier")
    selector: Optional[str] = Field(
        None, description="CSS selector for the section or iframe"
    )
    issues: List[Issue] = Field(..., description="List of issues in this section")


class Report(BaseModel):
    url: Optional[HttpUrl] = Field(
        None, description="Original page URL if linted by URL"
    )
    sections: List[SectionReport] = Field(
        ..., description="Grouped report by sections and iframes"
    )
    summary: Dict[str, int] = Field(
        ..., description="Summary counts: total, errors, warnings"
    )


__all__ = [
    "URLRequest",
    "HTMLRequest",
    "Issue",
    "SectionReport",
    "Report",
]
