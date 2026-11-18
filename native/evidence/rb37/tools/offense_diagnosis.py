"""RB-3.7 offense diagnosis (report only; runs no match).

Reads the RB-3.8 soak raw logs (claude/soak-rb-3-8 @ 3364aa0, native/evidence/rb38-soak/{real,control}/raw-*.json.gz)
and the read-only observer files (native/evidence/rb37/observe/observe-*.json.gz, same matches, same hashes).

python3 native/evidence/rb37/tools/offense_diagnosis.py --soak <dir with real/ control/> --observe native/evidence/rb37/observe --out native/evidence/rb37
"""
import argparse, bisect, gzip, json, math
from collections import Counter, defaultdict
from pathlib import Path

MATCHES = [('real', s) for s in range(1, 11)] + [('control', s) for s in range(1, 4)]
LIVE = ('live', 'opening', 'flight')


def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return None if not xs else round(xs[len(xs) // 2], 2)


def quart(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return None
    at = lambda f: round(xs[min(len(xs) - 1, int(round(f * (len(xs) - 1))))], 2)
    return dict(n=len(xs), min=round(xs[0], 2), q1=at(.25), median=at(.5), q3=at(.75), max=round(xs[-1], 2))


def team_of(pid): return pid.split(':')[0] if pid else None


def load(path):
    return json.load(gzip.open(path, 'rt')) if str(path).endswith('.gz') else json.loads(Path(path).read_text())


class Match:
    def __init__(self, soak, observe, block, seed):
        self.name = f'{block}-seed{seed:02d}'
        raw = load(Path(soak) / block / f'raw-{self.name}.json.gz')
        self.res = load(Path(soak) / block / f'{self.name}.json')
        self.log = raw['log']; self.raw = raw
        op = Path(observe) / f'observe-{self.name}.json.gz'
        self.obs = load(op) if op.exists() else None
        # attack direction per log record: initial ends from the first period-start snap (own 40 = 60 -> own end 100)
        first = next(r for r in self.log if r['event'] == 'restart_awarded' and r['data']['reason'] == 'period_start')
        t = first['data']['team']; own = 100 if first['data']['spot'][0] == 60 else 0
        ends = {t: own, ('B' if t == 'A' else 'A'): 100 - own}; self.ends_at = []
        for r in self.log:
            if r['event'] == 'ends_exchanged': ends = {k: 100 - v for k, v in ends.items()}
            self.ends_at.append(dict(ends))
        self.snap = {s['id']: s for s in self.obs['snaps']} if self.obs else {}
        self.t2live = [(r['t_ms'], r['live_ms']) for r in self.log]

    def goal(self, i, team): return 100 - self.ends_at[i][team]

    def gdist(self, i, team, x, y):
        return math.hypot(x - self.goal(i, team), y - 50)

    def possessions(self):
        idx = [i for i, r in enumerate(self.log) if r['event'] == 'rb_quota_reset']
        out = []
        for k, i in enumerate(idx):
            j = idx[k + 1] if k + 1 < len(idx) else len(self.log) - 1
            out.append((self.log[i]['data']['ruling']['team'], i, j))
        return out


def end_cause(m, team, i, j):
    """Why possession [i, j) ended (j = next quota reset, or the end of the log)."""
    log = m.log
    if j >= len(log) - 1 and log[j]['event'] != 'rb_quota_reset':
        return 'period/match end', None
    k = j
    while k > i:
        r = log[k]
        if r['event'] == 'restart_awarded':
            reason = r['data']['reason']
            if reason == 'boundary': return 'boundary: ' + boundary_kind(m, i, k, team), k
            if reason == 'goal': return 'goal scored', k
            if reason == 'second_tackle': return 'second tackle', k
            if reason in ('period_start',): return 'period/match end', k
            if reason.startswith('ZR') or reason == 'zone_residence': return 'zone rule (ZR-*/zone_residence)', k
            if reason in ('defence_minor', 'offence_minor_turnover', 'major', 'minor_count_plus'): return 'foul: ' + reason, k
            return 'award: ' + reason, k
        if r['event'] == 'possession' and r['data']['team'] != team:
            return 'lost in play: ' + loose_kind(m, i, k, team), k
        k -= 1
    return 'other', None


def last_ball_action(m, i, k, team):
    for q in range(k, i, -1):
        r = m.log[q]; e = r['event']; d = r['data']
        if e == 'release' and team_of(d['player']) == team: return d['kind'], q
        if e == 'restart_release' and d.get('team') == team: return 'restart_pass', q
        if e == 'freeze' and d.get('was_carrier') and team_of(d['player']) == team: return 'carrier_frozen', q
        if e == 'strip' and team_of(d['target']) == team: return 'strip', q
        if e == 'control': return 'control:' + ('own' if team_of(d['player']) == team else 'opp'), q
    return None, None


def boundary_kind(m, i, k, team):
    b = m.log[k - 1] if m.log[k - 1]['event'] == 'boundary' else next((m.log[q] for q in range(k, i, -1) if m.log[q]['event'] == 'boundary'), None)
    if b and b['data'].get('carrier'): return 'carrier stepped out'
    kind, q = last_ball_action(m, i, k, team)
    lt = b['data'].get('last_touch') if b else None
    who = 'own' if lt == team else 'opp'
    return {'pass': f'pass went out (last touch {who})', 'restart_pass': f'restart throw went out (last touch {who})',
            'shot': 'shot missed out', 'loose': 'loose ball out'}.get(kind, f'other out (last touch {who})')


def loose_kind(m, i, k, team):
    kind, q = last_ball_action(m, i, k, team)
    if kind == 'loose':                       # forced release: find the cause just before
        for z in range(q, max(i, q - 8), -1):
            e = m.log[z]['event']
            if e == 'freeze' and m.log[z]['data'].get('was_carrier'): return 'carrier frozen by arrow (ball loose)'
            if e == 'strip': return 'strip'
            if e in ('c3_grounding', 'tackle_count'): return 'ball loose at tackle/grounding'
        return 'forced loose release'
    return {'pass': 'pass intercepted or loose after pass', 'restart_pass': 'restart throw intercepted or loose',
            'shot': 'shot saved/recovered by defence', 'carrier_frozen': 'carrier frozen by arrow (ball loose)',
            'strip': 'strip', 'control:own': 'loose after own control (fumble/contest)', 'control:opp': 'other'}.get(kind, 'other')


def q1_q2(m):
    rows = []
    for team, i, j in m.possessions():
        cause, k = end_cause(m, team, i, j)
        lv = [q for q in range(i, (k or j) + 1) if m.log[q]['phase'] in LIVE]
        dur = m.log[k or j]['live_ms'] - m.log[i]['live_ms']
        if lv:
            s, e = lv[0], lv[-1]
            ds = m.gdist(s, team, *m.log[s]['ball'][:2]); de = m.gdist(e, team, *m.log[e]['ball'][:2])
            best = min(m.gdist(q, team, *m.log[q]['ball'][:2]) for q in lv)
            xbest = min(abs(m.log[q]['ball'][0] - m.goal(q, team)) for q in lv)
            # carrier track (every step) for the furthest advance with the ball
            if m.obs:
                t0, t1 = m.log[i]['live_ms'], m.log[k or j]['live_ms']
                tr = m.obs['carrier_track']; lo = bisect.bisect_left(tr, [t0]); hi = bisect.bisect_right(tr, [t1 + 1])
                for live, c, x, y, own in tr[lo:hi]:
                    if team_of(c) == team:
                        g = 100 - own; best = min(best, math.hypot(x - g, y - 50)); xbest = min(xbest, abs(x - g))
        else:
            ds = de = best = xbest = None
        shots = sum(1 for q in range(i, j) if m.log[q]['event'] == 'release' and m.log[q]['data']['kind'] == 'shot' and team_of(m.log[q]['data']['player']) == team)
        passes = sum(1 for q in range(i, j) if m.log[q]['event'] == 'release' and m.log[q]['data']['kind'] == 'pass' and team_of(m.log[q]['data']['player']) == team)
        rows.append(dict(team=team, cause=cause, duration_ms=dur, start_dist=ds, end_dist=de, best_dist=best, best_xdist=xbest,
                         shots=shots, passes=passes, first_tackles=sum(1 for q in range(i, j) if m.log[q]['event'] == 'restart_awarded' and m.log[q]['data']['reason'] == 'first_tackle')))
    return rows


def q3(m):
    out = Counter(); rows = []; last_restart = -10 ** 9
    for q, r in enumerate(m.log):
        e, d = r['event'], r['data']
        if e == 'restart_release': last_restart = r['live_ms']
        if e not in ('release', 'restart_release'): continue
        kind = d.get('kind', 'restart_pass') if e == 'release' else 'restart_pass'
        if kind not in ('pass', 'restart_pass'): continue
        passer = d.get('player') or d.get('taker'); team = team_of(passer); target = d.get('target')
        result = 'unresolved'
        for z in range(q + 1, min(len(m.log), q + 400)):
            x = m.log[z]; xe = x['event']
            if xe == 'control':
                c = x['data']['player']
                result = ('complete_to_target' if c == target else 'complete_other') if team_of(c) == team else 'intercepted'; break
            if xe == 'boundary': result = 'out_of_bounds'; break
            if xe in ('restart_awarded', 'goal'): result = 'dead_before_control'; break
            if xe == 'release' and x['data']['player'] != passer: result = 'deflected_rereleased'; break
        geo = None
        s = m.snap.get(r['id'])
        if s and target:
            P = {p[0]: p for p in s['players']}
            if passer in P and target in P:
                a, b = P[passer], P[target]
                dist = math.hypot(b[3] - a[3], b[4] - a[4])
                opp = [p for p in s['players'] if p[1] != team]
                def seg(p):
                    dx, dy = b[3] - a[3], b[4] - a[4]; L = dx * dx + dy * dy or 1
                    f = max(0., min(1., ((p[3] - a[3]) * dx + (p[4] - a[4]) * dy) / L))
                    return math.hypot(p[3] - a[3] - f * dx, p[4] - a[4] - f * dy)
                lane = min((seg(p) for p in opp), default=99.)
                nearest_def_to_target = min((math.hypot(p[3] - b[3], p[4] - b[4]) for p in opp), default=99.)
                gx = 100 - s['ends'][team]; tgt_in_att_zone = math.hypot(b[3] - gx, b[4] - 50) < 20
                own_g = s['ends'][team]; tgt_in_own_zone = math.hypot(b[3] - own_g, b[4] - 50) < 20
                geo = dict(distance=round(dist, 2), lane_clearance=round(lane, 2), defender_to_target=round(nearest_def_to_target, 2),
                           target_frozen=bool(b[5]), target_in_attacked_zone=tgt_in_att_zone, target_in_own_zone=tgt_in_own_zone)
        speed = math.sqrt(sum(c * c for c in d['velocity']))
        close = None
        if m.obs and target:
            fl = m.obs['ball_flight']; lo = bisect.bisect_left(fl, [r['live_ms']])
            pts = []
            for f in fl[lo:lo + 60]:
                if f[0] > r['live_ms'] + 3000: break
                if f[6] == passer and f[7] == target and f[8] is not None:
                    pts.append((math.hypot(f[3] - f[8], f[4] - f[9]), f[5]))
            if pts: close = min(pts)
        rows.append(dict(kind=kind, team=team, result=result, after_restart_ms=r['live_ms'] - last_restart, geo=geo,
                         speed=round(speed, 2), closest_to_target=None if close is None else round(close[0], 2),
                         ball_z_at_closest=None if close is None else close[1]))
    return rows


def q4(m):
    if not m.obs: return []
    tr = m.obs['carrier_track']; outs = [r for r in m.log if r['event'] == 'carry_outcome']
    rows = []
    for cs in m.obs['carry_starts']:
        pid, team = cs['player'], cs['team']
        out = next((r for r in outs if r['data']['player'] == pid and r['data']['started_ms'] == cs['t_ms']), None)
        end_live = out['live_ms'] if out else cs['live_ms']
        g = 100 - cs['ends'][team]
        lo = bisect.bisect_left(tr, [cs['live_ms']]); pts = [(x, y) for live, c, x, y, own in tr[lo:] if live <= end_live and c == pid]
        me = next(p for p in cs['players'] if p[0] == pid)
        sd = math.hypot(me[3] - g, me[4] - 50)
        close = min([math.hypot(x - g, y - 50) for x, y in pts] + [sd])
        covered = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        opp = [p for p in cs['players'] if p[1] != team]
        within5 = sum(1 for p in opp if math.hypot(p[3] - me[3], p[4] - me[4]) <= 5)
        keeper = next((p for p in opp if p[2] == 'k'), None)
        rows.append(dict(team=team, start_dist=round(sd, 2), closest=round(close, 2), covered=round(covered, 2),
                         held_ms=end_live - cs['live_ms'], defenders_within_5m=within5,
                         keeper_dist=round(math.hypot(keeper[3] - me[3], keeper[4] - me[4]), 2) if keeper else None,
                         outcome=out['data']['outcome'] if out else 'no_outcome', ended_by=out['data']['ended_by'] if out else None))
    return rows


def carrier_choices(m):
    """What the ball carrier decides by distance band to the goal he attacks (observer decisions)."""
    if not m.obs: return {}
    res = defaultdict(Counter)
    for live, pid, x, y, kind, aim, opts, ze in m.obs['carrier_decisions']:
        team = team_of(pid)
        # ends at that live time: nearest log record
        i = bisect.bisect_left([r['live_ms'] for r in m.log], live); i = min(i, len(m.log) - 1)
        d = m.gdist(i, team, x, y)
        band = 'under 20' if d < 20 else '20-32' if d < 32 else '32-50' if d < 50 else '50+'
        res[band][kind] += 1
        if band == 'under 20' and ze >= 3000: res['under 20 & zone timer >= 3 s'][kind] += 1
    return {k: dict(v) for k, v in res.items()}


def q5(m):
    rows = []
    for q, r in enumerate(m.log):
        if r['event'] != 'release' or r['data']['kind'] != 'shot': continue
        pid = r['data']['player']; team = team_of(pid)
        outcome = 'unresolved'
        for z in range(q + 1, min(len(m.log), q + 200)):
            x = m.log[z]; xe = x['event']
            if xe == 'goal': outcome = 'scored'; break
            if xe == 'keeper_contact': outcome = 'keeper save/touch'; break
            if xe == 'frame_contact': outcome = 'hit frame'; break
            if xe == 'boundary': outcome = 'missed (out)'; break
            if xe == 'control': outcome = 'blocked/recovered by ' + ('own' if team_of(x['data']['player']) == team else 'defence'); break
            if xe == 'touch': outcome = 'deflected'; break
        s = m.snap.get(r['id']); prox = None; dist = None
        if s:
            P = {p[0]: p for p in s['players']}
            if pid in P:
                a = P[pid]; g = 100 - s['ends'][team]; dist = math.hypot(a[3] - g, a[4] - 50)
                prox = sum(1 for p in s['players'] if p[1] != team and p[2] != 'k' and math.hypot(p[3] - a[3], p[4] - a[4]) <= 5)
        band = None if dist is None else 'under10' if dist < 10 else '10_to20' if dist < 20 else '20plus'
        rows.append(dict(team=team, outcome=outcome, distance=None if dist is None else round(dist, 2), band=band, defenders_within_5m=prox))
    return rows


def q6(m, poss):
    arrows = sum(1 for r in m.log if r['event'] == 'arrow_release'); freezes = [r for r in m.log if r['event'] == 'freeze']
    carrier = sum(1 for r in freezes if r['data'].get('was_carrier'))
    ended_by_carrier_freeze = sum(1 for p in poss if p['cause'] == 'lost in play: carrier frozen by arrow (ball loose)')
    # receiver frozen: a freeze of the target of the pass in flight
    rec = 0; last_target = None
    for r in m.log:
        if r['event'] in ('release', 'restart_release'): last_target = r['data'].get('target')
        if r['event'] == 'control': last_target = None
        if r['event'] == 'freeze' and r['ball_mode'] == 'passed' and r['data']['player'] == last_target: rec += 1
    return dict(arrows=arrows, freezes=len(freezes), carrier_freezes=carrier, receiver_freezes=rec,
                arrows_per_possession=round(arrows / len(poss), 3), freezes_per_possession=round(len(freezes) / len(poss), 3),
                possessions_ended_by_carrier_freeze=ended_by_carrier_freeze)


def q7(m):
    kinds = Counter(); lost5 = Counter(); spots = defaultdict(list); log = m.log
    rel = [(q, r) for q, r in enumerate(log) if r['event'] == 'restart_release']
    award_of = {}
    for q, r in enumerate(log):
        if r['event'] == 'restart_awarded': award_of[r['data']['restart_id']] = r
    for q, r in rel:
        a = award_of.get(r['data']['restart_id']); reason = a['data']['reason'] if a else '?'; team = r['data']['team']
        kinds[reason] += 1
        lost = False
        for z in range(q + 1, len(log)):
            x = log[z]
            if x['live_ms'] - r['live_ms'] > 5000: break
            if x['event'] == 'rb_quota_reset' and x['data']['ruling']['team'] != team: lost = True; break
        if lost: lost5[reason] += 1
        if a: spots[reason].append(m.gdist(q, team, *a['data']['spot'][:2]))
    return dict(released_by_reason=dict(kinds), lost_within_5s=dict(lost5),
                spot_distance_to_attacked_goal={k: quart(v) for k, v in spots.items()})


def q8(m):
    rows = []
    for q, r in enumerate(m.log):
        e = r['event']
        if e == 'tackle_count': kind = 'tackle'
        elif e == 'possession': kind = 'turnover_in_play'
        else: continue
        s = m.snap.get(r['id']) if e == 'tackle_count' else None
        if e == 'possession':           # snapshot at the control event at the same t
            c = next((log for log in [m.log[z] for z in range(q, max(0, q - 3), -1)] if log['event'] == 'control'), None)
            s = m.snap.get(c['id']) if c else None
        if not s: continue
        bx, by = s['ball']; off = r['data'].get('target') if e == 'tackle_count' else None
        losing = team_of(off) if off else ('B' if r['data']['team'] == 'A' else 'A')
        d5 = sum(1 for p in s['players'] if p[1] != losing and p[2] == 'f' and math.hypot(p[3] - bx, p[4] - by) <= 5)
        d25 = sum(1 for p in s['players'] if p[1] != losing and p[2] == 'f' and math.hypot(p[3] - bx, p[4] - by) <= 25)
        a5 = sum(1 for p in s['players'] if p[1] == losing and p[2] == 'f' and math.hypot(p[3] - bx, p[4] - by) <= 5)
        rows.append(dict(kind=kind, defenders_5m=d5, defenders_25m=d25, attackers_5m=a5))
    return rows


def summarise(ms):
    if not ms: return None
    P = [p for m in ms for p in m['poss']]
    n = len(P)
    by = defaultdict(list)
    for p in P: by[p['cause']].append(p['duration_ms'])
    q1 = sorted(((c, len(v), round(len(v) / n, 4), med(v)) for c, v in by.items()), key=lambda x: -x[1])
    passes = [x for m in ms for x in m['passes']]
    res3 = Counter(x['result'] for x in passes if x['kind'] == 'pass'); res3r = Counter(x['result'] for x in passes if x['kind'] == 'restart_pass')
    fail = lambda x: x['result'] in ('intercepted', 'out_of_bounds')
    early = Counter(x['kind'] for x in passes if fail(x) and x['after_restart_ms'] <= 5000)
    geo = [x['geo'] for x in passes if x['geo'] and x['kind'] == 'pass']
    def band_table(kind):
        t = defaultdict(Counter)
        for x in passes:
            if x['kind'] != kind or not x['geo']: continue
            d = x['geo']['distance']; db = '<6 m' if d < 6 else '6-8 m' if d < 8 else '8-12 m' if d < 12 else '12-20 m' if d < 20 else '20+ m'
            t[db]['ok' if x['result'].startswith('complete') else 'fail'] += 1
        return {k: dict(v, fail_rate=round(v['fail'] / max(1, v['fail'] + v['ok']), 3)) for k, v in sorted(t.items())}
    fails = [x for x in passes if x['result'] in ('intercepted', 'out_of_bounds') and x['closest_to_target'] is not None]
    oks = [x for x in passes if x['result'].startswith('complete') and x['closest_to_target'] is not None]
    car = [x for m in ms for x in m['carries']]; sh = [x for m in ms for x in m['shots']]; d8 = [x for m in ms for x in m['defense']]
    return dict(
        matches=len(ms), possessions=n, possessions_per_team_per_match=round(n / len(ms) / 2, 1),
        median_possession_live_s=round(med([p['duration_ms'] for p in P]) / 1000, 2),
        q1_end_causes=[dict(cause=c, count=k, share=s, median_live_s=None if d is None else round(d / 1000, 2)) for c, k, s, d in q1],
        q1_possessions_with_shot=sum(1 for p in P if p['shots']), q1_first_tackles_inside_possessions=sum(p['first_tackles'] for p in P),
        q2=dict(start_distance=quart([p['start_dist'] for p in P]), end_distance=quart([p['end_dist'] for p in P]),
                furthest_advance_distance=quart([p['best_dist'] for p in P]),
                reached_opposing_40=sum(1 for p in P if p['best_xdist'] is not None and p['best_xdist'] <= 40),
                reached_keeper_zone_edge_20m=sum(1 for p in P if p['best_dist'] is not None and p['best_dist'] <= 20),
                reached_cognition_shot_range_32m=sum(1 for p in P if p['best_dist'] is not None and p['best_dist'] <= 32)),
        q3=dict(passes_per_possession=round(sum(p['passes'] for p in P) / n, 3), open_play_pass_results=dict(res3),
                completion_rate=round((res3['complete_to_target'] + res3['complete_other']) / max(1, sum(res3.values())), 3),
                restart_throw_results=dict(res3r), failures_within_5s_of_restart=dict(early),
                pass_distance=quart([g['distance'] for g in geo]), lane_clearance=quart([g['lane_clearance'] for g in geo]),
                nearest_defender_to_target=quart([g['defender_to_target'] for g in geo]),
                target_frozen=sum(g['target_frozen'] for g in geo), target_in_own_zone=sum(g['target_in_own_zone'] for g in geo),
                target_in_attacked_zone=sum(g['target_in_attacked_zone'] for g in geo), with_geometry=len(geo),
                speed=quart([x['speed'] for x in passes]), fail_rate_by_distance_open_play=band_table('pass'),
                fail_rate_by_distance_restart=band_table('restart_pass'),
                closest_ball_to_target_failed=quart([x['closest_to_target'] for x in fails]),
                closest_ball_to_target_completed=quart([x['closest_to_target'] for x in oks]),
                failed_passing_within_3m_of_target=sum(1 for x in fails if x['closest_to_target'] <= 3.),
                failed_with_flight_data=len(fails)),
        q4=dict(carries=len(car), start_distance=quart([c['start_dist'] for c in car]), closest_approach=quart([c['closest'] for c in car]),
                closest_approach_any=min((c['closest'] for c in car), default=None),
                distance_covered=quart([c['covered'] for c in car]), held_s=quart([c['held_ms'] / 1000 for c in car]),
                defenders_within_5m_at_start=quart([c['defenders_within_5m'] for c in car]),
                keeper_distance_at_start=quart([c['keeper_dist'] for c in car]),
                outcomes=dict(Counter(c['outcome'] for c in car)), ended_by=dict(Counter(c['ended_by'] for c in car))),
        q4_carrier_choices=merge([m['choices'] for m in ms]),
        q5=dict(shots=len(sh), bands=dict(Counter(s['band'] for s in sh)), outcomes=dict(Counter(s['outcome'] for s in sh)),
                defenders_within_5m=quart([s['defenders_within_5m'] for s in sh]), distance=quart([s['distance'] for s in sh])),
        q6=dict(arrows=sum(m['arrows']['arrows'] for m in ms), freezes=sum(m['arrows']['freezes'] for m in ms),
                carrier_freezes=sum(m['arrows']['carrier_freezes'] for m in ms), receiver_freezes=sum(m['arrows']['receiver_freezes'] for m in ms),
                possessions_ended_by_carrier_freeze=sum(m['arrows']['possessions_ended_by_carrier_freeze'] for m in ms),
                arrows_per_possession=round(sum(m['arrows']['arrows'] for m in ms) / n, 3), freezes_per_possession=round(sum(m['arrows']['freezes'] for m in ms) / n, 3)),
        q7=dict(per_match={k: round(v / len(ms), 1) for k, v in sum((Counter(m['restarts']['released_by_reason']) for m in ms), Counter()).items()},
                lost_within_5s_per_match={k: round(v / len(ms), 1) for k, v in sum((Counter(m['restarts']['lost_within_5s']) for m in ms), Counter()).items()}),
        q8=dict(at_tackle=dict(defenders_within_5m=quart([d['defenders_5m'] for d in d8 if d['kind'] == 'tackle']),
                               defenders_within_25m=quart([d['defenders_25m'] for d in d8 if d['kind'] == 'tackle']),
                               attackers_within_5m=quart([d['attackers_5m'] for d in d8 if d['kind'] == 'tackle'])),
                at_turnover=dict(defenders_within_5m=quart([d['defenders_5m'] for d in d8 if d['kind'] == 'turnover_in_play']),
                                 defenders_within_25m=quart([d['defenders_25m'] for d in d8 if d['kind'] == 'turnover_in_play']),
                                 attackers_within_5m=quart([d['attackers_5m'] for d in d8 if d['kind'] == 'turnover_in_play']))))


def merge(dicts):
    out = defaultdict(Counter)
    for d in dicts:
        for k, v in d.items(): out[k].update(v)
    return {k: dict(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--soak', required=True); ap.add_argument('--observe', required=True); ap.add_argument('--out', required=True)
    a = ap.parse_args(); per = []
    for block, seed in MATCHES:
        m = Match(a.soak, a.observe, block, seed)
        if m.obs:
            assert (m.obs['trace_hash'], m.obs['state_hash']) == (m.res['trace_hash'], m.res['state_hash']), m.name
            assert m.obs['log_len'] == len(m.log), m.name
        poss = q1_q2(m)
        per.append(dict(name=m.name, block=block, observed=bool(m.obs), poss=poss, passes=q3(m), carries=q4(m), shots=q5(m),
                        arrows=q6(m, poss), restarts=q7(m), defense=q8(m), choices=carrier_choices(m),
                        restart_awards=dict(Counter(r['data']['reason'] for r in m.log if r['event'] == 'restart_awarded'))))
    report = dict(real=summarise([x for x in per if x['block'] == 'real']), control=summarise([x for x in per if x['block'] == 'control']),
                  per_match={x['name']: dict(possessions=len(x['poss']), restart_awards=x['restart_awards'], observed=x['observed'],
                                             end_causes=dict(Counter(p['cause'] for p in x['poss']))) for x in per})
    Path(a.out).mkdir(parents=True, exist_ok=True)
    (Path(a.out) / 'offense_diagnosis.json').write_text(json.dumps(report, indent=1, sort_keys=True) + '\n')
    print(json.dumps(report['real'], indent=1)[:6000])


if __name__ == '__main__':
    main()
