"""Verify edge replays, historical gates and byte-reproducible evidence."""
import json
from pathlib import Path

from .tables import IDENTITY, encoded, load, read, render, sampled

BASE = Path('audit/native')
HERE = BASE/'rb339'
RAW = HERE/'evidence'
PARENT = BASE/'rb338/evidence'


def historical():
    results = {}
    for lane in range(2):
        name = f'history{lane}.json'
        current = json.loads((RAW/name).read_text())
        assert current==json.loads((PARENT/name).read_text()), name
        results.update(current)
    for mode, parent in (('A6','A6-1'),('B4','B4-1'),('RB332','RB332-1'),('T3','R0-0-1')):
        recorded = load(RAW,mode+'-1')
        original = load(PARENT,parent)
        assert all(recorded[k]==original[k] for k in IDENTITY), mode
        results[mode] = recorded
    assert (RAW/'legacy.txt').read_bytes()==Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    return results


def main():
    historical()
    rows = read(RAW,PARENT)
    sample = sampled(rows)
    assert render(rows,sample)==(HERE/'TABLES.md').read_text()
    assert encoded(sample)==(HERE/'SAMPLED_BODY_OUTS.json.gz').read_bytes()
    print('Verified replay gates, all eight R3 identities, E1 repeat, and byte-identical evidence tables and sample.')


if __name__=='__main__':
    main()
