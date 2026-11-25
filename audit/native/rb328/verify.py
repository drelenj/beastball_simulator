"""Check the scored games and guard hashes against their recorded evidence."""
import argparse
import json
from pathlib import Path

from audit.native.rb327.match import PAIRS
from native.rulebook.fatigue_rotation import KEEPER_REGULATION_MIN_MS, RETURN_THRESHOLD, parameters


KEYS = ('score', 'trace_hash', 'state_hash', 'config_digest')


def read(path):
    return json.loads(path.read_text())


def fingerprints(row):
    return tuple(row[k] for k in KEYS)


def verify(root):
    prior = Path('audit/native/rb327/evidence/soak-off')
    expected = {(pair, seed) for pair in range(len(PAIRS))
                for seed in range(1, 11 if pair == 0 else 3)}
    for mode in ('off', 'on'):
        paths = sorted((root / mode).glob('*.json'))
        assert {tuple(map(int, p.stem.split('-'))) for p in paths} == expected
        for p in paths:
            row = read(p)
            pair, seed = map(int, p.stem.split('-'))
            assert tuple(row['teams']) == PAIRS[pair] and row['seed'] == seed
            assert row['status'] == 'final' and row['restart_completion_ratio'] == 1.
            assert row['invariants'] == 'passed' and 'drill_values_sha256' not in row['config']
            if mode == 'off':
                assert fingerprints(row) == fingerprints(read(prior / p.name)), p
                continue
            assert row['config']['fatigue_rotation_parameters'] == parameters()
            for event in row['fatigue_substitutions']:
                data = event['data']
                assert data['role'] != 'archer' and data['incoming_energy'] >= RETURN_THRESHOLD
                if data['role'] == 'keeper':
                    assert row['participation'][data['outgoing']]['regulation_ms'] >= KEEPER_REGULATION_MIN_MS
    assert fingerprints(read(root / 'on/0-1.json')) == fingerprints(read(root / 'replay-1.json'))
    assert (root / 'legacy.txt').read_bytes() == Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
    for name, score, trace, state in (
        ('compatibility', {'A': 57, 'B': 76},
         '44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072',
         '046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d'),
        ('core', {'A': 61, 'B': 80},
         'c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256',
         'c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745'),
    ):
        row = read(root / f'{name}.json')
        assert fingerprints(row)[:3] == (score, trace, state)
    print('Verified 40 final soak results, 20 exact RB-3.27 replays, 2 identity games, '
          '6 legacy rows and the full fatigue-on replay.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    verify(parser.parse_args().runs)
