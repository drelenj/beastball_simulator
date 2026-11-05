"""Experiment scorer: one match/drill log -> per-team metrics under the experiment's rules (RULES_FLOW_v0.3).  Pure function of the event log; changes nothing in the engine.
Flat scoring [C]: every goal = 2 points, a half goal = 1; a goal carried in is tracked as a Carry; releases are tracked by distance with success rates.
Overlay [P]: the new minor-foul tackle-count rule (defence minor: count -1, at 0 a half goal in Q1-Q3 / full goal in Q4+OT, offence keeps the ball; offence minor: count +1) is applied to the engine's
fouls as an OVERLAY, because the engine does not implement it.  Engine fouls that are not major/danger are treated as minors [P].  The overlay is reported separately from engine goals.
Teams: 'A' attacks x=100, 'B' attacks x=0 (checked against the goal events' origin_to_goal_m).
"""
import math, collections
GOAL_PTS, HALF_PTS = 2, 1
BANDS = ((0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 200))
SHOT_KINDS = ('shot', 'kick', 'strike')

def team_of(pid): return pid[0] if pid else None
def goal_x(team): return 100. if team == 'A' else 0.
def band(d):
    for lo, hi in BANDS:
        if lo <= d < hi: return '%d-%d' % (lo, hi if hi < 200 else 99)
    return '30-99'

def score(log, keys=('A', 'B')):
    engine_rules = any(e['event'] in ('foul_award', 'minor_recorded') for e in log)
    m = {t: collections.Counter() for t in keys}; det = {t: collections.defaultdict(collections.Counter) for t in keys}
    kinds = collections.Counter(); owner = None; count = 0; adv = {t: 0. for t in keys}; last = {t: None for t in keys}; poss_start = {}; poss_max = {t: 0. for t in keys}
    for e in log:
        ev, d = e['event'], e.get('data', {}); per = e.get('period', 1); bx = e['ball'][0] if e.get('ball') else None
        o = e.get('owner')
        # distance progressed: forward movement of the ball along the attack axis while a team owns it (coarse: sampled at logged events)
        if o in keys and bx is not None:
            sgn = 1. if o == 'A' else -1.
            if last[o] is not None and owner == o: adv[o] += max(0., sgn * (bx - last[o]))
            last[o] = bx
        if ev == 'possession_change':
            t, prev = d.get('team'), d.get('previous')
            if prev in keys and t in keys and t != prev and d.get('reason') != 'goal': m[prev]['turnover'] += 1; det[prev]['turnover_by'][d.get('reason', '?')] += 1
            count = 0; owner = t
            if t in keys: poss_start[t] = bx; last[t] = bx
        elif ev == 'tackle_count': count = d['count_to'] if isinstance(d.get('count_to'), int) else count + 1
        elif ev == 'release':
            kinds[d.get('kind')] += 1
            t = team_of(d.get('player'))
            if t in keys and d.get('kind') in SHOT_KINDS:
                org = d.get('origin', {}).get('origin')
                if org: dist = abs(goal_x(t) - org[0]) if True else 0; m[t]['shot_attempts'] += 1; det[t]['attempts'][band(math.hypot(goal_x(t) - org[0], org[1] - 50.))] += 1
        elif ev == 'goal':
            t = d.get('team')
            if t not in keys: continue
            carry = d.get('method') == 'carry'; org = d.get('release_origin')
            dist = d.get('origin_to_goal_m') if d.get('origin_to_goal_m') is not None else (math.hypot(goal_x(t) - org[0], org[1] - 50.) if org else None)
            m[t]['goals'] += 1; m[t]['points_flat'] += GOAL_PTS
            if carry: m[t]['carry_goals'] += 1
            elif dist is not None: m[t]['release_goals'] += 1; det[t]['goals_by_band'][band(dist)] += 1; det[t]['goal_dist_sum']['m'] += dist
        elif ev == 'engagement' and d.get('kind') == 'block':
            t = team_of(d.get('actor'))
            if t in keys: m[t]['blocks'] += 1; m[t]['blocks_offence' if e.get('owner') == t else 'blocks_defence'] += 1
        elif ev == 'foul_award':
            t = d.get('team')
            if t in keys: m[t]['awards_half' if d.get('points') == 1 else 'awards_full'] += 1; m[t]['award_points'] += d.get('points', 0)
        elif ev == 'foul':
            a = team_of(d.get('actor')); eng_major = bool(d.get('major') or d.get('danger'))
            if a not in keys: continue
            m[a]['major_fouls' if eng_major else 'minor_fouls'] += 1
            if not eng_major and owner in keys and not engine_rules:
                if a != owner:                       # defence minor
                    if count >= 1: count -= 1; m[a]['minor_count_cost'] += 1
                    else:
                        pts = HALF_PTS if per <= 3 else GOAL_PTS; m[owner]['overlay_points'] += pts; m[owner]['overlay_awards_half' if per <= 3 else 'overlay_awards_full'] += 1
                else:                                # offence minor
                    count += 1; m[a]['minor_count_cost'] += 1
                    if count >= 2: m[a]['overlay_turnover'] += 1; count = 0
    for t in keys: m[t]['distance_progressed_m'] = round(adv[t], 1)
    out = {}
    for t in keys:
        c = {k: 0 for k in ('blocks','blocks_offence','blocks_defence','award_points','turnover','shot_attempts','goals','points_flat','carry_goals','release_goals','minor_fouls','major_fouls','minor_count_cost','overlay_points','overlay_awards_half','overlay_awards_full','overlay_turnover')}; c.update(m[t]); sa = c.get('shot_attempts', 0); c['shot_success_rate'] = round(c.get('release_goals', 0) / sa, 3) if sa else None
        c['attempts_by_band'] = dict(det[t]['attempts']); c['goals_by_band'] = dict(det[t]['goals_by_band']); c['turnovers_by_reason'] = dict(det[t]['turnover_by'])
        c['band_success'] = {b: round(det[t]['goals_by_band'].get(b, 0) / n, 3) for b, n in det[t]['attempts'].items() if n}
        c['points_flat_total'] = c.get('points_flat', 0) + c.get('overlay_points', 0) + c.get('award_points', 0)
        out[t] = c
    out['_release_kinds'] = dict(kinds)
    return out
