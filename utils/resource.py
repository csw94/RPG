"""Resolve bundled resources in development and PyInstaller builds."""

from pathlib import Path
import sys


def resource_path(relative_path: str) -> str:
    """Return an absolute path to a bundled resource."""
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return str(base_path / relative_path)
