"""Verify saved experiment and historical identity evidence, without running a match."""
import argparse
import json
from pathlib import Path
from .tables import IDENTITY, load, render


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, default=Path('audit/native/rb334/evidence'))
    args = parser.parse_args()
    root = args.evidence
    historical = Path('audit/native/rb333/evidence')
    expected = json.loads((historical / 'identity.json').read_text())
    actual = {}
    for lane in (1, 2):
        actual.update(json.loads((root / f'historical-{lane}.json').read_text()))
    for mode, row in expected.items():
        assert all(actual[mode][key] == row[key] for key in IDENTITY), mode
    assert (root / 'legacy.txt').read_bytes() == Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    assert render(root, historical) == Path('audit/native/rb334/TABLES.md').read_text()
    print('Matched historical gates, all eight ladder fingerprints, A6 replay and offline tables.')
    print('A6 seed 1', {key: load(root, 'A6-1')[key] for key in IDENTITY})


if __name__ == '__main__':
    main()
