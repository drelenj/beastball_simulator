"""Parent-side launcher for B1 workers; intentionally imports no simulator."""
from pathlib import Path
import subprocess
import sys


WORKER_MODULES=frozenset({'b1.run','b1.g1'})


def run_worker(module, arguments=(), *, cwd=None, timeout=300):
    """Run a declared B1 entrypoint in a process that owns all Pocket state."""
    if module not in WORKER_MODULES:
        raise ValueError(f'not a declared B1 worker: {module}')
    root=Path(cwd) if cwd is not None else Path(__file__).resolve().parents[1]
    return subprocess.run([sys.executable,'-m',module,*map(str,arguments)],
                          cwd=root,text=True,capture_output=True,
                          timeout=timeout,check=False)
