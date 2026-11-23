"""Run the paired benchmark as a child and record peak resident memory."""
import json
import os
import resource
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
out = root / "audit/native/rb323-validation/evidence/benchmark-memory.json"
env = os.environ.copy()
env["PYTHONPATH"] = "." + (":" + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
subprocess.run([sys.executable, "audit/native/rb323/benchmark.py", "--steps", "1500", "--out", str(out)], cwd=root, env=env, check=True)
usage = resource.getrusage(resource.RUSAGE_CHILDREN)
summary = {
    "workload": "paired benchmark, 2 seeds x 2 modes x 1500 steps",
    "peak_rss_kib": usage.ru_maxrss,
    "child_user_cpu_s": usage.ru_utime,
    "child_system_cpu_s": usage.ru_stime,
    "benchmark": json.loads(out.read_text()),
}
(out.parent / "benchmark-resource.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: v for k, v in summary.items() if k != "benchmark"}, indent=2))
