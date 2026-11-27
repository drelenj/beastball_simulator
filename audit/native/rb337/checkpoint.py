"""Render the checkpoint from the archived comparison and gate records."""
import argparse
import json
from pathlib import Path
from statistics import mean, stdev
from math import sqrt

from .tables import ARMS, collect, load, metrics

def render_checkpoint():
    audit = Path('audit/native')
    root = audit / 'rb337'
    evidence = root / 'evidence'
    parent = audit / 'rb336/evidence'
    rows = collect(evidence, parent)
    values = {arm: [metrics(row) for row in rows[arm]] for arm in ARMS}

    def line(label, key, indices=range(8)):
        series = {arm: [values[arm][i][key] for i in indices] for arm in ARMS}
        cells = [f'{mean(v):.2f}' for v in series.values()]
        for a,b in [('L1','L0'),('L2','L0'),('L2','L1')]:
            diffs = [x-y for x,y in zip(series[a],series[b])]
            d, se = mean(diffs), stdev(diffs)/sqrt(len(diffs))
            cells.append(f'{d:+.2f} ± {se:.2f}'+(' ~' if abs(d)<=2*se else ''))
        return '| '+' | '.join([label,*cells])+' |'

    first = {arm:rows[arm][0] for arm in ARMS}
    identity = {}
    for lane in range(2):
        identity.update(json.loads((evidence/f'history{lane}.json').read_text()))
    for name in ('RB332','A6','B4'):
        identity[name]=load(evidence,name+'-1')
    identity.update(first)
    suite = (evidence/'pytest.txt').read_text().splitlines()[-1].strip()
    legacy = (evidence/'legacy.txt').read_text().strip()
    body = 'Carrier body-outs, total'
    margin = 'Second team minus first team margin'
    fumbles = 'Possession-ending fumbles, classified'
    overall = {arm:mean(v[body] for v in values[arm]) for arm in ARMS}
    loss_records = [f for games in rows.values() for r in games for f in r['rb337']['fumbles']]
    def detail(label):
        return sum(row['detail'] == label for row in loss_records)

    lines = [
        '# OWNER BRIEFING',
        '',
        '1. **Accomplished.** IMPLEMENTED the two universal traction settings on the three-tackle trial. TESTED all 24 games in the paired comparison and archived named box scores and event measures.',
        '2. **What Native can do now.** The same Agility rating controls stronger braking and turning for every role. Native can replay the original three-tackle trial and run either traction setting. '
          f'Across the eight pairs, carrier body-outs averaged {overall["L0"]:.2f}, {overall["L1"]:.2f} and {overall["L2"]:.2f} per team per game at 1×, 1.5× and 2×.',
        '3. **Unproven.** The two pairings do not establish a league-wide effect. Unresolved fumble attributions are itemized below.',
        '4. **Blocking.** None for this checkpoint.',
        '5. **Recommended action.** Keep L0 as the reference. The 1.5× body-out change was within paired noise, and 2× increased self-run end-line exits. Both higher scales increased possessions.',
        '',
        '## Build and evidence',
        '',
        'Parent `3dc4eef3aa871f72d8c13ef46a4b3b81b5c4bac3`, branch `codex/rb-3-37-traction`. Engine commit `570fd12`, corrected loss-event observer `e19353d`. CPython 3.13.5. Workbook SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.',
        '',
        (root/'CONSUMERS.md').read_text().rstrip(),
        '',
        '## Paired games',
        '',
        'Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3. The five Garvian–Ala baseline games were replayed to collect the new observers and checked against the archived T3 fingerprints. All 24 games finished with invariants passing and every restart resolved. No league soak ran. At most two simulator processes ran in parallel.',
        '',
        'Counts are per team per game, rates are game-level percentages, and CPU is per game. Differences use the same pairing and seed. A tilde denotes a difference within two paired standard errors.',
        '',
        '| Measure | L0 | L1 | L2 | L1 − L0 | L2 − L0 | L2 − L1 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for key in (body,'Carrier body-out sideline self-run','Carrier body-out sideline after contact','Carrier body-out end line self-run','Carrier body-out end line after contact',
                'Passed balls out','Held end-line flights staying in play','Possessions/team','Mean possession duration (s)',
                'Points/team','Carry goals','Targeted drops','Interceptions (ledger)',fumbles,'Event Keeper save rate (%)','Takedown success (%)',
                'CPU seconds/game'):
        lines.append(line(key,key))
    for label, indices in [('Garvian–Ala',range(5)),('Yukïma–Isu’Kari',range(5,8))]:
        for key in (body, 'Possessions/team', 'Points/team',margin):
            lines.append(line(f'{label}, {key}',key,indices))
    lines.extend([
        '',
        'The 1.5× scale left total body-outs within paired noise at −0.25 ± 1.31. The 2× scale raised self-run end-line exits by 2.44 ± 0.78 versus L0 and by 1.50 ± 0.58 versus L1. Its change in total exits versus L0, +2.06 ± 1.34, remained within paired noise. Possessions rose by 8.56 ± 2.44 at 1.5× and 16.38 ± 2.97 at 2× versus L0. Both matchups’ signed margin differences stayed within paired noise.',
        '',
        'The [complete paired tables](rb337/TABLES.md) include per-pairing and combined possession endpoints, line and contact splits, scoring mix, passing, evasion, Keeper outcomes, turning radii and individual scores. A dash marks an unavailable denominator or a contrast with fewer than two paired observations.',
        '',
        '## Fumble diagnosis',
        '',
        f'The observer reconciled all {len(loss_records)} possession-ending fumbles to the box ledger. Other includes {detail("freeze of carrier")} witnessed carrier freezes, {detail("unresolved forced release")} unresolved forced releases and {detail("unlinked ledger attribution")} unlinked ledger attributions. Initial observer smoke records were replayed after the attribution fix.',
        '',
        '| Classification | L0 | L1 | L2 | L1 − L0 | L2 − L0 | L2 − L1 |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ])
    for key in (k for k in values['L0'][0] if k.startswith(('Fumble ','Other fumble, ','Related turnover ')) and ', Handling ' not in k):
        lines.append(line(key,key))
    lines.extend([
        '',
        'Strip and reception-drop turnovers are reported separately where the engine uses a different ledger label. The complete tables split each cause by the athlete’s kickoff Ball Handling band. A drop uses the intended receiver’s rating. The `rb337.fumbles` and `rb337.supplemental_losses` records identify the player and available source timing. Evasion outcome definitions are in the [observer documentation](rb337/README.md).',
        '',
        '## Gates',
        '',
        f'- a) full suite. TESTED with `pytest -q b1 native` after the source changes. {suite}.',
        '- b) six legacy hashes. TESTED byte for byte against `native/evidence/rb3-reach/legacy-hashes.txt`.',
        '- c) L1 seed 1 repeats exactly. TESTED. All archived values except measured CPU and sampled profiling data are equal, including the named box scores and fumble observations.',
        '- d)–h) unchanged (compat, CORE, RB-3.28, RB-3.31, RB-3.32 combined 99-74 trace 0045e62d...2601 state b2b68575...d9de). TESTED against the recorded identities.',
        '- i) A6 (61-105, trace 2437b808...6aee), B4 (57-112, trace f424c4ee...e9c9) and T3 (44-122, trace 539c5548...09c9) seed 1 reproduce exactly with the new switches OFF; record score, trace, state and config digest of L1 and L2 seed 1. TESTED.',
        '',
        '| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |',
        '| --- | ---: | --- | --- | --- |',
    ])
    for name in ('compatibility','core','R1','PLANNED','RB332','A6','B4','L0','L1','L2'):
        r=identity[name]
        lines.append(f"| {name} | {r['score']['A']}–{r['score']['B']} | `{r['trace_hash']}` | `{r['state_hash']}` | `{r['config_digest']}` |")
    lines.extend(['','Legacy 3,000-step windows, seeds 1 and 3.','','```',legacy,'```','','## Reproduction','',
        'The [reproduction guide](rb337/README.md) pins the workbook and lists the match, aggregation and verification commands. Each gzip file under [raw evidence](rb337/evidence/) embeds both the named JSON box score and named CSV box score. Game keys follow `{arm}-{pair}-{seed}`, with 0 for Garvian–Ala and 1 for Yukïma–Isu’Kari. Historical replays, the L1 repeat, the legacy hash report and the full suite log are in the same directory.',
        '',
        '```bash',
        'python3.13 -m audit.native.rb337.tables audit/native/rb337/evidence audit/native/rb336/evidence /tmp/rb337-tables.md',
        'cmp /tmp/rb337-tables.md audit/native/rb337/TABLES.md',
        'python3.13 -m audit.native.rb337.check',
        '```',
        '',
        '## Open questions',
        '',
        'No CANON interpretation was needed. The two scales remain trial settings.',
        '',
    ])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    args.out.write_text(render_checkpoint(), encoding='utf8')


if __name__ == '__main__':
    main()
