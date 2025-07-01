from typing import Optional

import requests
from bs4 import BeautifulSoup


class HTMLParser:
    """
    An HTML page loader and parser.
    """

    def fetch(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Loads HTML by URL.
        Returns an HTML string or None in case of an error.
        """
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            return None

    def parse(self, html: str) -> BeautifulSoup:
        """
        Parses the passed HTML and returns a BeautifulSoup object.
        """
        return BeautifulSoup(html, "lxml")
