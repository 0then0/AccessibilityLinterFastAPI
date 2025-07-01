from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class URLRequest(BaseModel):
    url: HttpUrl = Field(
        ..., max_length=2_048, description="The address of the HTML page to check"
    )


class HTMLRequest(BaseModel):
    html: constr(min_length=1, max_length=100_000)


class Issue(BaseModel):
    code: str = Field(..., description="WCAG rule code (for example, 'WCAG1')")
    message: str = Field(..., description="Problem description")
    selector: Optional[str] = Field(
        None, description="CSS selector for the problematic element"
    )
    context: Optional[str] = Field(None, description="Fragment of the HTML context")


class Report(BaseModel):
    url: Optional[HttpUrl] = Field(None, description="The verified URL, if applicable")
    issues: List[Issue] = Field(..., description="List of issues found")
    summary: dict = Field(
        ...,
        description="Brief statistics: total number of checks, number of errors and warnings",
    )


__all__ = ["URLRequest", "HTMLRequest", "Issue", "Report"]
