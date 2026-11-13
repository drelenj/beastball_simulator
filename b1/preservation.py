"""Repository inventory helpers for the frozen B0 tree."""
from __future__ import annotations

import hashlib
import json
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


def verify_baseline(root: Path, inventory: Path):
    """Check every recorded baseline file before accepting new evidence."""
    root = Path(root)
    expected = json.loads(Path(inventory).read_text())
    if not isinstance(expected, dict) or not expected:
        raise ValueError("empty or invalid baseline inventory")
    problems = []
    for relative, digest in sorted(expected.items()):
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError(f"invalid baseline path: {relative}")
        target = root / path
        if not target.is_file():
            problems.append(f"missing: {relative}")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            problems.append(f"modified: {relative}")
    if problems:
        raise RuntimeError("B0 baseline verification failed: " + "; ".join(problems))
    return len(expected)
