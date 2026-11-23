"""Assert independent replay hashes and print concise match/performance facts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E = ROOT / "audit/native/rb323-validation/evidence"
REF = ROOT / "audit/native/rb323/evidence"

def read(path):
    return json.loads(path.read_text())

def fingerprint(row):
    return tuple(row[k] for k in ("status", "score", "steps", "trace_hash", "state_hash", "config_digest"))

compat = read(E / "compatibility-real.json")
compat_ref = read(REF / "compatibility-real.json")
assert fingerprint(compat) == fingerprint(compat_ref)
assert compat["restart_awarded"] == compat["restart_closed"]

enabled = read(E / "individuation-real-seed1.json")
enabled_2 = read(E / "individuation-real-seed1-repeat.json")
enabled_ref = read(REF / "individual-1.json")
enabled_ref_2 = read(REF / "individual-2.json")
assert fingerprint(enabled) == fingerprint(enabled_2)
assert fingerprint(enabled) == fingerprint(enabled_ref) == fingerprint(enabled_ref_2)
assert enabled["restart_awarded"] == enabled["restart_closed"]
assert enabled_2["restart_awarded"] == enabled_2["restart_closed"]

for label, row in (("compatibility", compat), ("individuation/1", enabled)):
    print(label, "score", row["score"], "steps", row["steps"], "runtime_s", row["runtime_s"],
          "restart", row["restart_closed"], "/", row["restart_awarded"],
          "decisions", row["decisions_total"],
          "decisions_per_s", round(row["decisions_total"] / row["runtime_s"], 2),
          "trace", row["trace_hash"], "state", row["state_hash"], "config", row["config_digest"])
print("Independent same-seed full-match fingerprints identical: yes")
print("Compatibility run matches archived RB-3.22 fixture: yes")
