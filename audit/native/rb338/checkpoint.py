"""Render the checkpoint with the same inputs as the paired evidence tables."""
from argparse import ArgumentParser
from pathlib import Path
from statistics import mean

from .check import BASE, PARENT, RAW, historical
from .tables import ARMS, game_rows, grid, intervals, measurements, quantile

SUMMARY = (
    'Arrows released (legal)', 'Arrows net charged', 'Arrow impacts on players',
    'Freezes', 'Freezes (carrier)', 'Carrier-freeze fumbles', 'Possessions/team',
    'Mean possession duration (s)', 'Carrier body-outs',
    'Carrier out, contact push', 'Carrier out, maneuver path',
    'Carrier out, steering overshoot with aim inside', 'Carrier out, aim outside',
    'Carrier out, frozen or stunned', 'Carrier out, other', 'Points/team',
    'Second team minus first team margin', 'CPU seconds/game',
)


def report():
    hist = historical()
    rows = game_rows(RAW,PARENT)
    metrics = {a:[measurements(r) for r in games] for a,games in rows.items()}
    brief = {k:[mean(r[k] for r in metrics[a]) for a in ARMS] for k in
             ('Arrows released (legal)','Freezes','Carrier-freeze fumbles','Possessions/team')}
    values = lambda key: ' / '.join(f'{n:.2f}' for n in brief[key])
    suite = (RAW/'pytest.txt').read_text().splitlines()[-1]
    assert ' passed' in suite and ' failed' not in suite and ' error' not in suite, suite
    people = 'Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3'
    elapsed = [x for run in rows['R0'] for x in intervals(run['rb338'],'now')]
    live = [x for run in rows['R0'] for x in intervals(run['rb338'],'live_ms')]
    distribution = lambda clocks: ' / '.join(f'{quantile(clocks,p):.2f}' for p in (.1,.5,.9))

    freeze_exhausted_early = sum(v[1]==0 for game in rows['R2'] for v in game['rb338']['periods']['1'].values())
    period_arrow_exhausted = sum(v[0]==0 for game in rows['R3'] for period in ('1','2','3','4')
                                 for v in game['rb338']['periods'][period].values())
    overtime = [f"pair {game['pair']} seed {game['seed']}" for game in rows['R3']
                if len(game['rb338']['periods'])>4]

    lines = [
        '# OWNER BRIEFING',
        '',
        '1. **Accomplished.** DESIGN COMPLETE, IMPLEMENTED and TESTED. The current rulebook defaults to three tackles. The branch adds an opt-in Archer draw-and-aim cycle, two team budget trials and a read-only carrier body-out observer.',
        '2. **What Native can do now.** Use one budget per Archer team across a match, or reset it each period. '
        f'In R0 / R1 / R2 / R3 order, freezes averaged {values("Freezes")} per team per game. '
        f'Carrier-freeze fumbles averaged {values("Carrier-freeze fumbles")}, and possessions averaged {values("Possessions/team")}.',
        '3. **Unproven.** Budget selection still belongs to the owner. The two pairings measure these configurations on the trial sample. The body-out classes describe event timing and motion evidence.',
        '4. **Blocking.** None for this checkpoint.',
        '5. **Recommended action.** Review the match and period spending curves alongside freezes, possession endings and score margins before choosing a budget.',
        '',
        '## Source, schedule and reproduction',
        '',
        'Parent `ad3d9aeaa14beb6cc27d0c60bc7122306683bbbc`. Archer implementation `bd89a8dd228c6189dc214bbecedac2aacf1e30aa`. Final engine and observer source `09d901259d7d1e6efce988c8b118b83719920362` on `codex/rb-3-38-archer`. CPython 3.13.5. The ratings 0.4 workbook is pinned at SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.',
        '',
        f'The schedule was {people}. There were 24 new trial games and eight read-only R0 replays to capture exact release times and body-out histories missing from the inherited evidence. All eight R0 score, trace, state and config fingerprints match the RB-3.37 L0 files. All 32 scheduled games finished with invariants passing and every restart resolved. At most two simulator processes ran in parallel.',
        '',
        'The [reproduction guide](rb338/README.md) lists commands. The [raw results](rb338/evidence/) contain per-game event observations plus named CSV and JSON box scores. The [complete paired tables](rb338/TABLES.md) include all requested means, paired contrasts, spending by minute and margins. The [20 sampled exits](rb338/SAMPLED_BODY_OUTS.json) list each decision and physics sample in their rolling histories.',
        '',
        '## Rules and mechanism',
        '',
        '- The current `RulebookConfigV3` sets three tackles. Archived runners explicitly request their original two-tackle config. Named T3 stays at three. Config records retain the old serialized form at two so the historical digest stays stable.',
        '- Before the trial, Native cognition queried a 2,600 ms wait after the previous release and the motor scheduled a 600 ms draw. The frozen core also contains a 2-second cooldown and a 5-second reload, but Native disables that reload and uses its own release authority.',
        f'- On R0, elapsed-clock release intervals pooled by same Archer are {distribution(elapsed)} seconds at P10 / P50 / P90. The live-clock counterparts are {distribution(live)} seconds. The main tables also report the means of the within-game quantiles.',
        '- `archer_cycle` defaults OFF. When enabled, draw takes 1,000 × [1 + 0.6 × (0.70 − Strength)] ms and aim takes 800 × [1 + 0.6 × (0.70 − Archery Accuracy)] ms. A new target restarts aim after the original draw deadline. Final aim uses the athlete’s delivered observation and velocity estimate. The engine validates the target and deadline and charges only at release.',
        '- R2 allots 25 arrows and five freezes per team for the entire match. R3 allots 10 and four each regulation period, then five and two each overtime period. Neither trial resets its budget on possession changes. Both maintain the existing illegal-release charge and dead-ball refunds. The quiver invariant checks the effective allocation.',
        '- Budget counts come through the public view. The Archer compares the existing option values with the cost of spending a limited shot. The reserve uses the existing carrier-target value at the observed distance, multiplied by the fraction of remaining possible cycles that cannot be covered by the smaller of the two resource balances. Holding a draw spends nothing. The same seeded Disruption decision error applies.',
        '- The observer stores every body-out with the previous two seconds of committed physics and decisions, including before the player became the carrier. The [witness definitions](rb338/README.md) give the classification priority and distinguish observed contact timing from causation.',
        '',
    ]
    grid(lines,{a:[{k:r[k] for k in SUMMARY} for r in arm] for a,arm in metrics.items()},range(8),'Combined highlights')
    lines.extend([
        'Counts are per team per game unless labelled. Paired contrasts use matching seeds and opponents. A tilde marks effects within two paired standard errors. See the complete tables for the matchup splits, event-based Keeper rates and named box rates.',
        '',
        'R1 reduced total freezes by 36.69 ± 5.40 versus R0. Its changes in carrier-freeze fumbles and possessions stayed within paired noise. R2 and R3 reduced both, with possession differences of −20.75 ± 3.75 and −14.88 ± 4.73 versus R0. Combined mean score and signed margin changes stayed within paired noise.',
        '',
        f'By the end of period 1, {freeze_exhausted_early} of 16 teams had spent all five match-budget freezes in R2. In R3, teams used their full arrow budget in {period_arrow_exhausted} of 64 regulation team-periods. The R3 overtime case was {", ".join(overtime)} and reconciled to its separate overtime budget.',
        '',
        'In R0, 13.94 of 19.19 carrier body-outs per team per game had an inside locomotion target and no recent-contact or active-maneuver classification. This was the largest category in every arm. R3 recorded 4.25 ± 1.41 more body-outs than R2.',
        '',
        '## Gates',
        '',
        f'- a) Full suite. TESTED with `pytest -q b1 native`. {suite}.',
        '- b) The six legacy hashes match the saved 3,000-step windows on seeds 1 and 3 byte for byte.',
        '- c) R3 seed 1 repeats exactly, including event observations and named box scores. CPU and profiling samples are timing measurements.',
        '- d)–h) Compatibility, CORE, RB-3.28, RB-3.31 and RB-3.32 reproduced their recorded scores and full trace, state and config fingerprints.',
        '- i) A6, B4 and T3 seed 1 reproduced exactly. R1, R2 and R3 seed-1 fingerprints are recorded below.',
        '',
        '| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |',
        '| --- | ---: | --- | --- | --- |',
    ])
    fingerprints = [(k,hist[k]) for k in ('compatibility','core','R1','PLANNED','RB332','A6','B4')]
    fingerprints[2] = ('RB-3.28 threshold rotation',hist['R1'])
    fingerprints.extend([('T3 / R0',rows['R0'][0]),*((a,rows[a][0]) for a in ('R1','R2','R3'))])
    for mode,r in fingerprints:
        lines.append(f"| {mode} | {r['score']['A']}–{r['score']['B']} | `{r['trace_hash']}` | `{r['state_hash']}` | `{r['config_digest']}` |")
    lines += ['','Legacy outputs are in [legacy.txt](rb338/evidence/legacy.txt). The generated tables and episode sample reproduce byte for byte with the commands above.','','## Open questions','','The choice of budget size and reset scope remains with the owner.','']
    return '\n'.join(lines)


def main():
    parser = ArgumentParser()
    parser.add_argument('out',type=Path,nargs='?',default=BASE/'HP-002_RB338_CHECKPOINT.md')
    parser.parse_args().out.write_text(report(),encoding='utf8')


if __name__=='__main__':
    main()
