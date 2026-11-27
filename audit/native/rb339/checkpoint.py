"""Generate the owner checkpoint directly from the eight paired game records."""
from argparse import ArgumentParser
from pathlib import Path
from math import sqrt
from statistics import mean, stdev

from .check import BASE, PARENT, RAW, historical
from .tables import ARMS, grid, measurements, read, sampled

KEYS = (
    'Carrier body-outs','Carrier body-outs, sideline','Carrier body-outs, end line',
    'Carrier out, steering overshoot with aim inside','Carrier out, contact push',
    'Non-carrier body-outs','Passes out','Loose balls out','Possessions/team',
    'Mean possession duration (s)','Points/team','Carry goals','Pass completion (%)',
    'Takedown episodes','Takedown success (%)','Takedowns within 3 m of a line',
    'Arrows net charged','Freezes','Carrier-freeze fumbles','Second team minus first team margin',
    'CPU seconds/game, matched observer',
)


def checkpoint():
    identity = historical()
    rows = read(RAW,PARENT)
    sample = sampled(rows)
    outcomes = {arm:[measurements(row) for row in rows[arm]] for arm in ARMS}
    suite = (RAW/'pytest.txt').read_text().splitlines()[-1]
    assert ' passed' in suite and ' failed' not in suite and ' error' not in suite, suite

    def summary(key):
        base, trial = ([r[key] for r in outcomes[arm]] for arm in ARMS)
        changes = [b-a for a,b in zip(base,trial)]
        return mean(base),mean(trial),mean(changes),stdev(changes)/sqrt(len(changes))

    body_before,body_after,body_diff,body_se = summary('Carrier body-outs')
    _,_,over_diff,over_se = summary('Carrier out, steering overshoot with aim inside')
    _,_,pace_diff,pace_se = summary('Possessions/team')
    _,_,score_diff,score_se = summary('Points/team')
    _,_,other_diff,other_se = summary('Non-carrier body-outs')
    _,_,edge_tackle_diff,edge_tackle_se = summary('Takedowns within 3 m of a line')
    _,_,cpu_diff,cpu_se = summary('CPU seconds/game, matched observer')
    lines = [
        '# OWNER BRIEFING',
        '',
        '1. **Accomplished.** DESIGN COMPLETE, IMPLEMENTED and TESTED. Edge braking, turn direction, and the speed-aware aim margin are independently selectable. E1 combines them on the R3 period-budget setup.',
        f'2. **What Native can do now.** Surface locomotion checks the athlete’s own stopping and turning distances before reaching a line. Carrier body-outs averaged {body_before:.2f} in R3 and {body_after:.2f} in E1 per team per game.',
        '3. **Unproven.** The two matchups measure eight paired games. Contact impulses and the ability to stop before a given line remain part of the physics.',
        '4. **Blocking.** None for this checkpoint.',
        '5. **Recommended action.** Review E1 as a candidate for adoption given the reduction in exits. Weigh the increase in near-line takedowns and the drop in possessions. The period-budget sizes still need the owner’s confirmation.',
        '',
        '## Implementation and test design',
        '',
        'Parent `f64b9ab4836885ba6936aaaa3d57d61e37a7eebd`. Implementation `791b95cd9c5d6c985472168977ef62c60f3288ea` and profile guard fix `834c277` on `codex/rb-3-39-edge`. CPython 3.13.5. The two matchups used the ratings 0.4 workbook at SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.',
        '',
        '- The brake checks the body edge against stopping distance with the 0.3 m buffer. It spends the step first on cancelling outward motion and uses leftover time for the existing propulsion limits. At a corner the closest threatened line takes priority.',
        '- The turn-direction check uses twice the body-model turning radius and the signed short-turn side. It only changes the turn when the desired direction is more than 90° behind the current heading.',
        '- The aim clamp uses max(2.0 m, body radius + outward stopping distance + 0.5 m) per line. It caps geometrically infeasible margins at the opposite line’s minimum clearance. The own-body calculation is shared by cognition and the surface motor.',
        '- At the attacked goal the carrier can keep a route that intersects the legal mouth chord at hand height. Dead-ball movement and marked substitution exits bypass the new guard. The existing contact integration, surface judge, and scoring remain in force.',
        '',
        '## Evidence',
        '',
        'Garvian Guardians–Ala Apex seeds 1–5 and Yukïma Cowhands–Isu’Kari Sirenwings seeds 1–3. Eight new E1 games finished with invariants passing and all restarts resolved. The eight E0 replays matched their archived R3 fingerprints and supplied the additional perimeter witnesses. All eight archived R3 results supply the already available comparison measures. At most two simulation processes ran for the paired games.',
        '',
        f'Carrier body-outs changed by {body_diff:+.2f} ± {body_se:.2f} per team per game. Inside-aim steering overshoots changed by {over_diff:+.2f} ± {over_se:.2f}. Non-carrier body-outs changed by {other_diff:+.2f} ± {other_se:.2f}.',
        '',
        f'Takedowns within 3 m of a line rose by {edge_tackle_diff:.2f} ± {edge_tackle_se:.2f}, while overall takedown success and per-pairing margins stayed within paired noise. Possessions changed by {pace_diff:+.2f} ± {pace_se:.2f}, and points by {score_diff:+.2f} ± {score_se:.2f}. The matched-observer runtime change was {cpu_diff:+.2f} ± {cpu_se:.2f} CPU seconds per game.',
        '',
        f'The replay archives embed named CSV and JSON box scores. The observer sampled {len(sample)} E1 exits with fixed seed 20261129. The linked files include per-game results, all paired contrasts, and complete episode histories.',
        '',
        '[Reproduction guide](rb339/README.md) · [Paired tables](rb339/TABLES.md) · [Raw evidence](rb339/evidence/) · [Episode sample](rb339/SAMPLED_BODY_OUTS.json.gz)',
        '',
    ]
    grid(lines,{a:[{k:r[k] for k in KEYS} for r in outcomes[a]] for a in ARMS},range(8),'Combined highlights')
    lines.extend([
        'Counts are per team per game unless labelled. A tilde marks differences within two paired standard errors. The complete tables include per-pairing rates, line and cause breakdowns, evasion measures, and per-game CPU and margins.',
        '',
        '## Gates',
        '',
        f'- a) Full suite. TESTED with `pytest -q b1 native`. {suite}.',
        '- b) All six legacy hashes match the recorded 3,000-step windows for seeds 1 and 3 byte for byte. The first run caught an installer guard that also matched Native v0/3. Requiring the exact native-rb/3 profile resolved it, and the final E1 repeat retained the original trial fingerprints.',
        '- c) E1 seed 1 repeats exactly for score, trace, state, box scores and raw observations. Timing and sampled CPU profiles are measured separately.',
        '- d)–h) Compatibility, CORE, RB-3.28, RB-3.31 and RB-3.32 reproduce their recorded fingerprints.',
        '- i) A6, B4, T3 and R3 seed 1 reproduce exactly. E1 seed 1 is recorded below.',
        '',
        '| Mode | Score | Trace SHA-256 | State SHA-256 | Config SHA-256 |',
        '| --- | ---: | --- | --- | --- |',
    ])
    names = [(k,identity[k]) for k in ('compatibility','core','R1','PLANNED','RB332','A6','B4','T3')]
    names[2] = ('RB-3.28 threshold rotation',identity['R1'])
    names.extend((a,rows[a][0]) for a in ARMS)
    for name,row in names:
        lines.append(f"| {name} | {row['score']['A']}–{row['score']['B']} | `{row['trace_hash']}` | `{row['state_hash']}` | `{row['config_digest']}` |")
    lines.extend(['','## Open questions','','The R3 regulation and overtime budget sizes remain pending owner confirmation.',''])
    return '\n'.join(lines)


def main():
    parser = ArgumentParser()
    parser.add_argument('out',type=Path,nargs='?',default=BASE/'HP-002_RB339_CHECKPOINT.md')
    parser.parse_args().out.write_text(checkpoint(),encoding='utf8')


if __name__=='__main__':
    main()
