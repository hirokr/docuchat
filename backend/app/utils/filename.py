"""Filename sanitization utilities."""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE_CHARS = re.compile(r"[^\w.\- ]", re.UNICODE)
_MAX_FILENAME_LEN = 200


def sanitize_filename(filename: str) -> str:
    """Return a safe basename for storage."""
    name = Path(filename).name.strip()
    if not name:
        return "document.pdf"
    name = _UNSAFE_CHARS.sub("_", name)
    if len(name) > _MAX_FILENAME_LEN:
        stem = Path(name).stem[: _MAX_FILENAME_LEN - 4]
        suffix = Path(name).suffix or ".pdf"
        name = f"{stem}{suffix}"
    return name
