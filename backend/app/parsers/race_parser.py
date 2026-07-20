"""Parser for race details stored in local HTML files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup, Tag


class RaceParser:
    """Extract race metadata from a local HTML document."""

    _FIELDS = {
        "date": ("date", "tarih"),
        "hippodrome": ("hippodrome", "hipodrom", "hippodromu"),
        "race_number": ("race number", "race no", "race", "koşu no", "koşu"),
        "distance": ("distance", "mesafe"),
        "surface": ("surface", "track", "pist", "zemin"),
    }

    def parse(self, file_path: str) -> dict[str, Any]:
        """Read a local HTML file and return its race metadata.

        Missing values are ``None``, so the returned dictionary always has
        the same five keys. File reading errors propagate to the caller.
        """
        html = Path(file_path).read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        return {
            field: self._extract_field(soup, field, labels)
            for field, labels in self._FIELDS.items()
        }

    def _extract_field(
        self, soup: BeautifulSoup, field: str, labels: tuple[str, ...]
    ) -> str | None:
        attribute_names = (f"data-{field.replace('_', '-')}", field)
        for attribute_name in attribute_names:
            element = soup.find(attrs={attribute_name: True})
            if isinstance(element, Tag):
                value = element.get(attribute_name) or element.get_text(" ", strip=True)
                if value:
                    return self._normalise(str(value))

        for label in labels:
            label_element = soup.find(
                string=re.compile(rf"^\s*{re.escape(label)}\s*:?\s*$", re.I)
            )
            if label_element is None or label_element.parent is None:
                continue

            sibling = label_element.parent.find_next_sibling()
            if isinstance(sibling, Tag):
                value = sibling.get_text(" ", strip=True)
                if value:
                    return self._normalise(value)

            parent_text = self._normalise(label_element.parent.get_text(" ", strip=True))
            value = re.sub(rf"^\s*{re.escape(label)}\s*:?\s*", "", parent_text, flags=re.I)
            if value and value.casefold() != label.casefold():
                return value

        return None

    @staticmethod
    def _normalise(value: str) -> str:
        return " ".join(value.split())
