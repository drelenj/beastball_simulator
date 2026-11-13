"""EMERGENCE-1 read-out: aggregate tournament JSONL rows by label, paired sign test,
plain-words description.  python -m b1.emergence.readout rows.jsonl [--a L --b L] [--out F.md]"""
import argparse
import json
from collections import Counter, defaultdict
from math import comb
from pathlib import Path


def sign_test_p(wins, losses):
    """Exact two-sided sign test (binomial, p = 0.5) on non-tied pairs."""
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def _ok(r):
    return r.get('status') in (None, 'final', 'time_limit') and isinstance(r.get('score'), dict)


def _gd(r, label):
    """Goal difference of `label` in a row, or None if the label is not exactly one side."""
    a, b = r.get('label_A'), r.get('label_B')
    if (a == label) == (b == label):
        return None
    d = r['score']['A'] - r['score']['B']
    return d if a == label else -d


def paired_summary(rows, a, b):
    """Label b versus label a. Unit = seed (and period_s): goal difference of b summed over
    the side assignments played for that seed."""
    units, wdl = defaultdict(list), Counter()
    for r in rows:
        if not _ok(r) or {r.get('label_A'), r.get('label_B')} != {a, b}:
            continue
        d = _gd(r, b)
        units[(r.get('seed'), r.get('period_s'))].append(d)
        wdl['win' if d > 0 else 'loss' if d < 0 else 'draw'] += 1
    tot = [sum(v) for _, v in sorted(units.items(), key=lambda kv: str(kv[0]))]
    w, l, dr = sum(x > 0 for x in tot), sum(x < 0 for x in tot), sum(x == 0 for x in tot)
    return {'a': a, 'b': b, 'pairs': len(tot), 'both_sides_pairs': sum(len(v) == 2 for v in units.values()),
            'b_pair_wins': w, 'pair_draws': dr, 'b_pair_losses': l,
            'mean_goal_diff_per_pair': round(sum(tot) / len(tot), 3) if tot else None,
            'sign_test_p': round(sign_test_p(w, l), 6), 'matches': sum(wdl.values()),
            'b_match_wins': wdl['win'], 'match_draws': wdl['draw'], 'b_match_losses': wdl['loss']}


def aggregate(rows):
    """Per-label mean of every numeric per-team metric (label's own team, either side)."""
    acc, net, kinds, n = defaultdict(lambda: defaultdict(list)), defaultdict(Counter), defaultdict(Counter), Counter()
    for r in rows:
        if not _ok(r) or not r.get('metrics'):
            continue
        for side in ('A', 'B'):
            lab, m = r.get('label_' + side), r['metrics'].get(side) or {}
            n[lab] += 1
            acc[lab]['score'].append(r['score'][side])
            for k, v in m.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    acc[lab][k].append(v)
            for k, v in (m.get('pass_network') or {}).items():
                net[lab][k] += v
            for k, v in (m.get('decisions_by_kind') or {}).items():
                kinds[lab][k] += v
            for k, v in (m.get('pass_len_hist') or {}).items():
                acc[lab]['pass_len_' + k].append(v)
    means = {lab: {k: round(sum(v) / len(v), 3) for k, v in d.items() if v} for lab, d in acc.items()}
    return means, net, kinds, n


def render(rows, a=None, b=None):
    labels = Counter(x for r in rows for x in (r.get('label_A'), r.get('label_B')))
    a = a or ('baseline' if 'baseline' in labels else labels.most_common(1)[0][0])
    b = b or next((l for l, _ in labels.most_common() if l != a), a)
    st = Counter(str(r.get('status')) for r in rows)
    ps = paired_summary(rows, a, b)
    means, net, kinds, n = aggregate(rows)
    L = ['# EMERGENCE-1 read-out', '', f'Rows: {len(rows)}; by status {dict(st)}. Comparison: `{b}` versus `{a}`.', '',
         '## Results (the only quality measure)', '', '| quantity | value |', '|---|---|']
    L += [f'| {k} | {v} |' for k, v in ps.items()]
    L += ['', f'## Descriptive metrics per team-match (mean; n = {n.get(a, 0)} for `{a}`, {n.get(b, 0)} for `{b}`)', '',
          f'| metric | {a} | {b} | diff |', '|---|---|---|---|']
    big = []
    for k in sorted(set(means.get(a, {})) | set(means.get(b, {}))):
        x, y = means.get(a, {}).get(k), means.get(b, {}).get(k)
        d = round(y - x, 3) if x is not None and y is not None else None
        L.append(f'| {k} | {x} | {y} | {d} |')
        if d is not None and abs(x) > 1e-9 and abs(d) / abs(x) > .2:
            big.append((k, x, y))
    for lab in (a, b):
        tot = sum(kinds[lab].values()) or 1
        L += ['', f'Decision mix `{lab}`: ' + ', '.join(f'{k} {100 * v / tot:.1f}%' for k, v in kinds[lab].most_common(10)),
              f'Pass network `{lab}` (passer slot > target slot, releases): ' + (', '.join(f'{k}: {v}' for k, v in net[lab].most_common(8)) or 'none')]
    L += ['', '## Plain words', '']
    if ps['pairs'] == 0:
        L.append(f'No matches between `{a}` and `{b}` were found.')
    elif ps['sign_test_p'] >= .05:
        L.append(f"`{b}` vs `{a}` over {ps['pairs']} paired seeds: {ps['b_pair_wins']} gained, {ps['b_pair_losses']} lost, {ps['pair_draws']} tied "
                 f"(exact sign-test p = {ps['sign_test_p']}): no result difference beyond noise was shown.")
    else:
        L.append(f"`{b}` vs `{a}` over {ps['pairs']} paired seeds: {ps['b_pair_wins']} gained, {ps['b_pair_losses']} lost, {ps['pair_draws']} tied "
                 f"(exact sign-test p = {ps['sign_test_p']}, mean goal difference {ps['mean_goal_diff_per_pair']} per pair).")
    if big:
        L.append('Metric differences larger than 20% relative (descriptive only; no significance tested for metrics): '
                 + '; '.join(f'{k} {x} -> {y}' for k, x, y in big) + '.')
    else:
        L.append('No descriptive metric differs by more than 20% relative (descriptive only; no significance tested for metrics).')
    return '\n'.join(L) + '\n'


def load(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rows')
    ap.add_argument('--a')
    ap.add_argument('--b')
    ap.add_argument('--out')
    x = ap.parse_args()
    text = render(load(x.rows), x.a, x.b)
    if x.out:
        Path(x.out).write_text(text)
    print(text)


if __name__ == '__main__':
    main()
