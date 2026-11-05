"""Canonical event-log hash, identical to the one in tools/t1_capture.py (functions norm/canon copied verbatim).
usage:  python3 tools/t1_canon_hash.py <log.json | log.jsonl> [more files]      prints SHA-256 of the canonical form
        python3 tools/t1_canon_hash.py --selftest                              checks the canonicaliser against a fixed vector
Accepted inputs: a JSON array of event dicts, or JSON Lines with one event dict per line.
Canonical form: dict keys sorted as strings, tuples read as lists, floats replaced by repr(float) strings (full precision), compact separators, UTF-8.
Caveat: the input must carry the same values the simulator produced.  A serializer that writes 5.0 as 5, rounds floats, or reorders list items
will change the hash.  The authoritative path is to run tools/t1_capture.py in your own environment and compare log_sha256 with MANIFEST.json."""
import sys, json, hashlib
def norm(o):
    if isinstance(o, dict): return {str(k): norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)): return [norm(v) for v in o]
    if isinstance(o, float): return repr(o)
    return o
def canon(o): return json.dumps(norm(o), default=str, separators=(',', ':'))
def digest(o): return hashlib.sha256(canon(o).encode()).hexdigest()
def load(path):
    txt = open(path, encoding='utf-8').read()
    try: return json.loads(txt)
    except json.JSONDecodeError: return [json.loads(l) for l in txt.splitlines() if l.strip()]
SELFTEST = [{'event': 'x', 'data': {'b': 1.5, 'a': (1, 2), 3: None, 'c': 5.0}, 't': 0.1}, {'event': 'y', 'data': {}}]
SELFTEST_SHA = "78f4d879736a87941fd1b068dc41820c0f8bd992d3a7228892f8567ed85c62ce"   # expected digest of SELFTEST on any platform
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        d = digest(SELFTEST); print(canon(SELFTEST)); print(d, "OK" if d == SELFTEST_SHA else "MISMATCH"); sys.exit(0 if d == SELFTEST_SHA else 1)
    for p in a: print(digest(load(p)), p)
