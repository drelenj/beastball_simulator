"""Run the whole suite and record a compact machine-readable summary."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
r = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-rA', 'b1', '-p', 'no:cacheprovider', '-W', 'ignore'],
                   cwd=ROOT, text=True, capture_output=True, timeout=1500)
lines = [l for l in r.stdout.splitlines() if l.startswith(('PASSED', 'FAILED', 'ERROR')) or ' passed' in l or ' failed' in l]
out = ROOT / 'b1/emergence/results'
(out / 'tests_pytest_b1.txt').write_text('\n'.join(lines) + '\n')
s = {'command': 'python3 -m pytest -q b1', 'returncode': r.returncode, 'summary': lines[-1] if lines else '',
     'passed': sum(l.startswith('PASSED') for l in lines), 'not_ok': [l for l in lines if l.startswith(('FAILED', 'ERROR'))],
     'by_file': dict(Counter(l.split('::')[0].split()[-1] for l in lines if l.startswith('PASSED')))}
(out / 'tests_summary.json').write_text(json.dumps(s, sort_keys=True, indent=1) + '\n')
print(json.dumps(s))
