import re
from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup, Tag

from app.models.schemas import Issue


class Validator(ABC):
    """
    Abstract base class for all WCAG validators.
    """

    @abstractmethod
    def validate(self, soup: BeautifulSoup) -> List[Issue]:
        """
        Analyze the parsed HTML and return a list of Issue objects.
        """
        pass


class AltTextValidator(Validator):
    """
    Check that all <img> tags have non-empty alt attributes.
    """

    def validate(self, soup: BeautifulSoup) -> List[Issue]:
        issues: List[Issue] = []
        for img in soup.find_all("img"):
            alt = img.get("alt", "").strip()
            if not alt:
                issues.append(
                    Issue(
                        code="WCAG1.1.1",
                        message="Image element missing non-empty alt attribute",
                        selector=img.name,
                        context=str(img)[:100],
                    )
                )
        return issues


class ContrastValidator(Validator):
    """
    Check that text/background color contrast meets WCAG minimum ratio (4.5:1 for normal text).
    Only inline styles with hex colors are considered.
    """

    HEX_COLOR_RE = re.compile(r"#([0-9a-fA-F]{6})")
    MIN_CONTRAST_RATIO = 4.5

    def _hex_to_rgb(self, hex_str: str) -> tuple[float, float, float]:
        """Convert '#rrggbb' to normalized RGB [0–1]."""
        r = int(hex_str[1:3], 16) / 255.0
        g = int(hex_str[3:5], 16) / 255.0
        b = int(hex_str[5:7], 16) / 255.0
        return r, g, b

    def _relative_luminance(self, rgb: tuple[float, float, float]) -> float:
        """Compute relative luminance for an sRGB triple."""

        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = rgb
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)

    def _contrast_ratio(self, lum1: float, lum2: float) -> float:
        """Compute contrast ratio between two luminances."""
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        return (lighter + 0.05) / (darker + 0.05)

    def validate(self, soup: BeautifulSoup) -> List[Issue]:
        issues: List[Issue] = []
        # default background color if none specified
        default_bg = "#ffffff"
        default_bg_lum = self._relative_luminance(self._hex_to_rgb(default_bg))

        # find all tags containing visible text
        for tag in soup.find_all(text=True):
            parent: Tag = tag.parent  # the element wrapping this text node
            text = tag.strip()
            if not text:
                continue

            style = parent.get("style", "")
            # extract text color and background-color
            color_match = re.search(r"color\s*:\s*(#[0-9a-fA-F]{6})", style)
            bg_match = re.search(
                r"background(?:-color)?\s*:\s*(#[0-9a-fA-F]{6})", style
            )

            if not color_match:
                continue  # skip elements without explicit text color

            text_color = color_match.group(1)
            bg_color = bg_match.group(1) if bg_match else default_bg

            # compute luminances and ratio
            text_lum = self._relative_luminance(self._hex_to_rgb(text_color))
            bg_lum = self._relative_luminance(self._hex_to_rgb(bg_color))
            ratio = self._contrast_ratio(text_lum, bg_lum)

            if ratio < self.MIN_CONTRAST_RATIO:
                issues.append(
                    Issue(
                        code="WCAG1.4.3",
                        message=(
                            f"Insufficient contrast ratio {ratio:.2f}:1 "
                            f"for text '{text[:30]}'"
                        ),
                        selector=parent.name,
                        context=str(parent)[:100],
                    )
                )

        return issues


class SemanticStructureValidator(Validator):
    """
    Check for presence of semantic landmarks (e.g., <header>, <nav>, <main>, <footer>).
    """

    REQUIRED_TAGS = ["header", "nav", "main", "footer"]

    def validate(self, soup: BeautifulSoup) -> List[Issue]:
        issues: List[Issue] = []
        for tag in self.REQUIRED_TAGS:
            if not soup.find(tag):
                issues.append(
                    Issue(
                        code="WCAG1.3.1",
                        message=f"Missing semantic <{tag}> element",
                        selector=tag,
                        context="",
                    )
                )
        return issues


# Export all validators
__all__ = [
    "Validator",
    "AltTextValidator",
    "ContrastValidator",
    "SemanticStructureValidator",
]
