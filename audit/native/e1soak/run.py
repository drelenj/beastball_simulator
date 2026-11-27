"""E1 league soak: fixed schedule, resumable, one compressed result per game.

python -m audit.native.a6soak.run schedule OUT          write OUT/schedule.json (deterministic)
python -m audit.native.a6soak.run play OUT BOOK LANE N  play every game i with i % N == LANE
python -m audit.native.a6soak.run status OUT            count finished, failed and missing games
"""
import gzip
import json
import random
import sys
import traceback
from pathlib import Path

import audit.native.rb333.match as ladder

ARM = 'E1'
DIGEST = 'f207194a947cecf2f0fe66c72d837f54bf490742faa46f73de85b1fb90c3b3a9'
PREFLIGHT = dict(score={'A': 89, 'B': 96},
                 trace_hash='8145286b995dde65d454364b307051c94f65fba461a984e6818681837932e0c5',
                 state_hash='175ef33be73eb45fa3d77129b95f957946b837ba5e19ba1f5ef8f7e7284fc05c')
TEAMS = ('Ala Apex', 'Ala Marauders', 'Ashkara Ignivars', 'Bibi Nupi Barbarians', 'Bryjeer Flame Devils',
         'Dōmyu Dominators', 'Garahviq Immortals', 'Garvian Guardians', 'Güunlekia Serpents', 'G’Yanka Vanagu',
         'Hina’sola Hunters', 'Isu’Kari Sirenwings', 'Kalundu Shockwave', 'Kasuf Bloodravens',
         'Khemara Sunscourge', 'Lykessia Wolverines', 'Mbuya Ïmu Moonhawks', 'Ndomiri Sentinels',
         'Ndumba Specters', 'Nuk’yl Chiefs', 'Priya Arpaqu', 'Ursiria 65ers', 'Wibatu Rangers', 'Xenar Ignite',
         'Yukïma Cowhands', 'Zafiren Tidewings')


def schedule():
    # Balanced draw: rounds of random perfect matchings (13 games per round), no repeated pairing,
    # first 100 pairings kept, so every team plays 7 or 8 different opponents.
    rng = random.Random(20261125)
    pairs, seen = [], set()
    while len(pairs) < 100:
        order = list(TEAMS)
        rng.shuffle(order)
        round_pairs = [tuple(order[i:i + 2]) for i in range(0, len(order), 2)]
        if any(frozenset(p) in seen for p in round_pairs):
            continue
        seen.update(frozenset(p) for p in round_pairs)
        pairs.extend(round_pairs)
    games = []
    for index, (a, b) in enumerate(pairs[:100]):
        for seed in (1, 2):
            games.append(dict(id=f'r{index:03d}-s{seed}', teams=[a, b], seed=seed))
    for seed in range(1, 11):
        games.append(dict(id=f'ga-s{seed:02d}', teams=['Garvian Guardians', 'Ala Apex'], seed=seed))
    return games


def play_one(game, book):
    ladder.PAIRS = (tuple(game['teams']),)
    return ladder.run(ARM, game['seed'], book, 0, diagnostics=False)


def write(path, row):
    tmp = path.with_suffix('.tmp')
    tmp.write_bytes(gzip.compress(json.dumps(row, ensure_ascii=False).encode(), mtime=0))
    tmp.replace(path)


def main(argv):
    cmd, out = argv[0], Path(argv[1])
    games_dir = out / 'games'
    if cmd == 'schedule':
        out.mkdir(parents=True, exist_ok=True)
        (out / 'schedule.json').write_text(json.dumps(schedule(), ensure_ascii=False, indent=1) + '\n')
        print('schedule', len(schedule()))
        return 0
    games = json.loads((out / 'schedule.json').read_text())
    if games != schedule():
        print('schedule.json does not match the fixed schedule; regenerate it'); return 2
    if cmd == 'preflight':
        row = play_one(dict(id='preflight', teams=['Garvian Guardians', 'Ala Apex'], seed=1), Path(argv[2]))
        ok = row['config_digest'] == DIGEST and all(row[k] == v for k, v in PREFLIGHT.items())
        print('PREFLIGHT', 'PASS' if ok else 'FAIL', row['score'], row['trace_hash'], row['state_hash'], row['config_digest'])
        return 0 if ok else 1
    if cmd == 'play':
        book, lane, lanes = Path(argv[2]), int(argv[3]), int(argv[4])
        games_dir.mkdir(parents=True, exist_ok=True)
        for i, game in enumerate(games):
            if i % lanes != lane:
                continue
            path = games_dir / f"{game['id']}.json.gz"
            if path.exists() or path.with_suffix('.failed').exists():
                continue
            try:
                row = play_one(game, book)
                row.update(game_id=game['id'], teams=game['teams'])
                write(path, row)
                print(game['id'], row['score'], row['status'], round(row['cpu_s'], 1), flush=True)
            except Exception:
                path.with_suffix('.failed').write_text(traceback.format_exc())
                print(game['id'], 'FAILED', flush=True)
        return 0
    if cmd == 'status':
        done = failed = 0
        missing = []
        bad = []
        for game in games:
            path = games_dir / f"{game['id']}.json.gz"
            if path.exists():
                done += 1
                row = json.loads(gzip.decompress(path.read_bytes()))
                if game['teams'] == ['Garvian Guardians', 'Ala Apex'] and row['config_digest'] != DIGEST:
                    bad.append(game['id'])
            elif path.with_suffix('.failed').exists():
                failed += 1
            else:
                missing.append(game['id'])
        print(f'finished {done}  failed {failed}  missing {len(missing)}  wrong-digest {len(bad)}')
        if missing: print('missing:', ' '.join(missing))
        if bad: print('wrong-digest:', ' '.join(bad))
        return 0
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
