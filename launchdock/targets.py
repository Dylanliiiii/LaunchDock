from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse


def looks_like_url(value: str) -> bool:
    text = normalized_target_text(value)
    if text is None:
        return False
    parsed = urlparse(text)
    return parsed.scheme in {"http", "https", "file"} and bool(parsed.netloc or parsed.path)


def normalized_target_text(value: str) -> str | None:
    text = value.strip()
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1].strip()
    if text.startswith('"') or text.endswith('"'):
        return None
    return text


def is_valid_target(value: str) -> bool:
    text = normalized_target_text(value)
    if not text:
        return False
    if looks_like_url(text):
        return True
    return Path(text).expanduser().exists()


def open_target(value: str) -> None:
    text = normalized_target_text(value)
    if not text:
        return
    if looks_like_url(text):
        webbrowser.open_new_tab(text)
        return
    path = Path(text).expanduser()
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])
