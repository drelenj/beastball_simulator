"""Build the native-v0/3 ten-seed table and manifest from recorded run results.
Reads result files only; runs no match. python -m native.v3_evidence --help
"""
import argparse
import json
from pathlib import Path


def row(r):
    ev = r['engine_events']; rm = r['restart_metric']; rr = r.get('restart_reasons', {})
    stats = r['team_stats']
    def kind(k):
        m = rm[k]
        return dict(awarded=m['awarded'], released=m['released'], timeout=m['timeout'],
                    release_rate=round(m['release_rate'], 4) if m['release_rate'] is not None else None,
                    timeout_rate=round(m['timeout_rate'], 4) if m['timeout_rate'] is not None else None,
                    eligible=m['eligible'], eligible_timeout=m['eligible_timeout'],
                    eligible_timeout_rate=round(m['eligible_timeout_rate'], 4) if m['eligible_timeout_rate'] is not None else None)
    return dict(seed=r['seed'], status=r['status'], period=r['period'], score=r['score'], result=r['result'],
                live_s=r['live_ms']/1000, runtime_s=r['runtime_s'], invariants=r['invariants'],
                trace_hash=r['trace_hash'], state_hash=r['state_hash'],
                restarts={k: kind(k) for k in ('toss', 'scrim', 'snap40', 'all')},
                restart_unobserved=rm['unobserved'],
                groundings=ev.get('c3_grounding', 0), tackle_count_events=ev.get('tackle_count', 0),
                first_tackles=rr.get('first_tackle'), second_tackles=rr.get('second_tackle'),
                holds_started=ev.get('c3_hold_start', 0), strips=ev.get('strip', 0), grips_broken=ev.get('c3_grip_broken', 0),
                snaps_released=rm['scrim']['released']+rm['snap40']['released'], tosses_released=rm['toss']['released'],
                offside_calls=ev.get('scrimmage_penalty', 0),
                minor_fouls=sum(s.get('minor_fouls', 0) for s in stats.values()),
                major_fouls=sum(s.get('major_fouls', 0) for s in stats.values()),
                foul_reasons=r['foul_reasons'], foul_awards=ev.get('foul_award', 0), goals=ev.get('goal', 0),
                turnovers=sum(s.get('turnovers', 0) for s in stats.values()), boundary=ev.get('boundary', 0),
                arrows=dict(released=ev.get('arrow_release', 0), missed=ev.get('arrow_miss', 0), freezes=ev.get('freeze', 0),
                            inert_impacts=ev.get('inert_impact', 0), body_or_ball_impacts=ev.get('arrow_geometry_impact', 0)),
                contact_intents=r.get('contact_intents', {}), collisions=ev.get('c3_collision', 0),
                scoring=r['scoring'])


def totals(rows):
    def s(f): return sum(f(r) or 0 for r in rows)
    out = {}
    for k in ('toss', 'scrim', 'snap40', 'all'):
        a, rel, to = s(lambda r: r['restarts'][k]['awarded']), s(lambda r: r['restarts'][k]['released']), s(lambda r: r['restarts'][k]['timeout'])
        el, elt = s(lambda r: r['restarts'][k]['eligible']), s(lambda r: r['restarts'][k]['eligible_timeout'])
        out[k] = dict(awarded=a, released=rel, timeout=to, release_rate=round(rel/a, 4) if a else None,
                      timeout_rate=round(to/a, 4) if a else None, eligible=el, eligible_timeout=elt,
                      eligible_timeout_rate=round(elt/el, 4) if el else None)
    n = len(rows)
    per = lambda f: None if any(f(r) is None for r in rows) else round(s(f)/n, 2)   # None = not recorded
    sc = [r['scoring'] for r in rows]
    bands = {}
    for b in ('under_10m', '10_to_20m', '20m_plus'):
        att = sum(x['shots'][b]['attempts'] for x in sc); pts = sum(x['shots'][b]['points'] for x in sc); g = sum(x['shots'][b]['goals'] for x in sc)
        bands[b] = dict(shot_attempts=att, shot_goals=g, points=pts, points_per_attempt=round(pts/att, 4) if att else None)
    carry_att = sum(x['carries']['attempts'] for x in sc); carry_pts = sum(x['carries']['points'] for x in sc)
    banded = dict(shots_by_band=bands, carries=dict(attempts=carry_att, goals=sum(x['carries']['goals'] for x in sc), points=carry_pts, points_per_attempt=round(carry_pts/carry_att, 4) if carry_att else None),
                  points_total_by_source={k: sum(x['points'][k] for x in sc) for k in ('shot_releases', 'carries', 'non_shot_releases', 'half_goals', 'full_goal_awards', 'total')})
    return dict(matches=n, scoring_basis='banded', banded=banded, restarts=out,
                per_match=dict(groundings=per(lambda r: r['groundings']), tackle_count_events=per(lambda r: r['tackle_count_events']),
                               first_tackles=per(lambda r: r['first_tackles']), second_tackles=per(lambda r: r['second_tackles']),
                               snaps_released=per(lambda r: r['snaps_released']), tosses_released=per(lambda r: r['tosses_released']),
                               offside_calls=per(lambda r: r['offside_calls']), minor_fouls=per(lambda r: r['minor_fouls']),
                               major_fouls=per(lambda r: r['major_fouls']), strips=per(lambda r: r['strips']),
                               arrows_released=per(lambda r: r['arrows']['released']), arrows_missed=per(lambda r: r['arrows']['missed']),
                               freezes=per(lambda r: r['arrows']['freezes']), goals=per(lambda r: r['goals']),
                               foul_awards=per(lambda r: r['foul_awards']), turnovers=per(lambda r: r['turnovers'])))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--soak', default='native/evidence/v0-3/soak'); ap.add_argument('--out', default='native/evidence/v0-3/ten-seed-table.json')
    a = ap.parse_args()
    rows = [row(json.loads(p.read_text())) for p in sorted(Path(a.soak).glob('seed-*.json'))]
    table = dict(config_version='native-v0/3', rows=rows, totals=totals(rows))
    Path(a.out).write_text(json.dumps(table, indent=2, sort_keys=True)+'\n')
    print(json.dumps(table['totals'], indent=1))

if __name__ == '__main__': main()
