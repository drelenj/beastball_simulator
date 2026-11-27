"""Verify historical fingerprints, trial reconciliation and all generated artifacts."""
import json
from pathlib import Path

from .tables import IDENTITY, episodes, game_rows, load, render

BASE = Path('audit/native')
HERE = BASE/'rb338'
RAW = HERE/'evidence'
PARENT = BASE/'rb337/evidence'


def historical():
    results = {}
    for n in range(2):
        filename = f'history{n}.json'
        actual = json.loads((RAW/filename).read_text())
        expected = json.loads((PARENT/filename).read_text())
        assert actual==expected, filename
        results.update(actual)
    for name in ('RB332','A6','B4'):
        latest = load(RAW,f'{name}-1')
        saved = load(PARENT,f'{name}-1')
        assert all(latest[k]==saved[k] for k in IDENTITY),name
        results[name] = latest
    assert (RAW/'legacy.txt').read_bytes()==Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    return results


def main():
    historical()
    rows = game_rows(RAW,PARENT)
    sample = episodes(rows)
    assert render(rows,sample)==(HERE/'TABLES.md').read_text()
    assert json.dumps(sample,ensure_ascii=False,indent=2)+'\n'==(HERE/'SAMPLED_BODY_OUTS.json').read_text()
    print('Verified legacy and historical hashes, all R0 replays, R3 repeat, budget and body-out reconciliation, and byte-identical tables.')


if __name__=='__main__':
    main()
