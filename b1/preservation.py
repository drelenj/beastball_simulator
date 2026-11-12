"""Repository inventory helpers for the frozen B0 tree."""
from __future__ import annotations

import hashlib
from pathlib import Path


def historical_files(root: Path):
    """Yield files inherited from B0, excluding B1 and runtime byproducts."""
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.parts[0] in {"b1", ".git"}:
            continue
        if "__pycache__" in relative.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        yield path


def historical_hashes(root: Path):
    root = Path(root)
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in historical_files(root)
    }
