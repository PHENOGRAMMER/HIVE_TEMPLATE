from __future__ import annotations

import re

import bleach
from markupsafe import Markup


ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "a",
}

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
}

ALLOWED_PROTOCOLS = {
    "http",
    "https",
    "mailto",
}

DISALLOWED_CONTENT_PATTERN = re.compile(
    r"<(script|style|iframe|object|embed)\b[^>]*>.*?</\1\s*>",
    re.IGNORECASE | re.DOTALL,
)


def sanitize_html(value: str | None) -> Markup | None:
    """
    Sanitize HTML imported from an external inspection template.

    Formatting and links are preserved where safe.
    Potentially dangerous markup is removed.
    """

    if not value:
        return None

    value = DISALLOWED_CONTENT_PATTERN.sub("", value)

    return Markup(
        bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=True,
        )
    )
