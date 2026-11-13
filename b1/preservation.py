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


def _git_blob_sha1(data: bytes):
    header=f"blob {len(data)}\0".encode()
    return hashlib.sha1(header+data).hexdigest()


def load_inventory(inventory: Path):
    """Return ``(algorithm, files, metadata)`` for v1 or canonical v2."""
    raw=json.loads(Path(inventory).read_text())
    if isinstance(raw, dict) and isinstance(raw.get('files'), dict):
        algorithm=raw.get('algorithm')
        if algorithm not in {'sha256','git-blob-sha1'}:
            raise ValueError(f"unsupported inventory algorithm: {algorithm}")
        return algorithm,raw['files'],raw
    if isinstance(raw, dict) and raw:
        return 'sha256',raw,{'schema':'b1-baseline-inventory-v1'}
    raise ValueError("empty or invalid baseline inventory")


def canonical_hashes(root: Path, inventory: Path):
    """Hash exactly the frozen commit paths; additions are out of scope."""
    algorithm,files,_=load_inventory(inventory)
    digest=(lambda b:hashlib.sha256(b).hexdigest()) if algorithm=='sha256' else _git_blob_sha1
    root=Path(root)
    return {relative:digest((root/relative).read_bytes())
            for relative in sorted(files) if (root/relative).is_file()}


def verify_baseline(root: Path, inventory: Path):
    """Check every recorded baseline file before accepting new evidence."""
    root = Path(root)
    algorithm,expected,_=load_inventory(inventory)
    digest=(lambda b:hashlib.sha256(b).hexdigest()) if algorithm=='sha256' else _git_blob_sha1
    problems = []
    for relative, expected_digest in sorted(expected.items()):
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError(f"invalid baseline path: {relative}")
        target = root / path
        if not target.is_file():
            problems.append(f"missing: {relative}")
        elif digest(target.read_bytes()) != expected_digest:
            problems.append(f"modified: {relative}")
    if problems:
        raise RuntimeError("B0 baseline verification failed: " + "; ".join(problems))
    return len(expected)
