"""Shared setup helpers for test scripts."""

import sys
from pathlib import Path


def configure_utf8_stdio():
    """Prefer UTF-8 output without detaching wrapped streams."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def add_src_to_path():
    src_path = Path(__file__).resolve().parents[1]
    src_path_str = str(src_path)
    if src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
    return src_path
