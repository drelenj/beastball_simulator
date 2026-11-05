"""Off-ball block (screen) option for the offence.  A team with block_rate > 0 sends up to k = round(block_rate * 4) off-ball attackers to screen the defenders who are
closest to the carrier: the blocker walks to a point 0.9 m in front of the defender on the carrier's side (a frontal, legal contact), so the physics' existing block engagement
(strength x blocking x mass, push, legality incl. blindside) decides what happens.  Nothing here decides an outcome.
genome: block_rate 0..1 (how many blockers), block_reach m (only defenders within this distance of the carrier are screened).
Limitation [P]: blockers pick targets from true positions (the off-ball offence layer has no PRISM perception yet).
Switch: BLOCK_OPTION=1 (default on; a team with block_rate 0 is unchanged).  Parameters per team in BG['A'|'B'].
"""
import math, os
BG = {'A': dict(block_rate=0., block_reach=10.), 'B': dict(block_rate=0., block_reach=10.)}
STATS = {}
PAIRS = []          # (t_ms, blocker, defender, mode) first assignment of each pair
MIND = {}; TGT = {}; TRACE = {}
_HOLD = {}          # (team, defender) -> (blocker, until_ms): an assignment is kept for a while so blockers do not dither
def mode(): return os.environ.get('BLOCK_MODE', 'persist')
def summary(log, window_ms=3000):
    """per game: assigned pairs, pairs where the blocker actually engaged that defender within window_ms, and all offence block engagements"""
    ev = [(e['t_ms'], e['data']['actor'], e['data']['target']) for e in log if e['event'] == 'engagement' and e['data'].get('kind') == 'block']
    hit = 0
    for t, b, d, _ in PAIRS:
        if any(t <= te <= t + window_ms and ((a == b and x == d) or (a == d and x == b)) for te, a, x in ev): hit += 1
    return dict(pairs=len(PAIRS), pairs_with_contact=hit)
ASSIGN = {}        # team -> {blocker: (defender, until_ms)}  persistent assignments (mode 'persist')
REACH_BLOCKER = 9.  # a blocker is only sent to a defender he can plausibly reach (surface gap, m)
def install(P):
    CO = P.CORE; Pol = CO.policies.Policy; o_t = Pol.targets
    def gap(a, b): return math.hypot(a.x - b.x, a.y - b.y) - (a.radius + b.radius)
    def targets(self, s):
        out = o_t(self, s)
        g = BG.get(self.team)
        if os.environ.get('BLOCK_OPTION', '1') != '1' or not g or g['block_rate'] <= 0. or s.owner != self.team or s.ball.carrier is None:
            ASSIGN.pop(self.team, None); return out
        c = s.players.get(s.ball.carrier)
        if c is None or c.team != self.team: return out
        k = int(round(g['block_rate'] * 4))
        if k <= 0: return out
        md = mode(); persist = md == 'persist'
        mates = {p.id: p for p in s.players.values() if p.team == self.team and p.active and p.role == 'field' and p.id != c.id and p.eligible(s.now) and p.posture == 'upright'}
        foes = {q.id: q for q in s.players.values() if q.team != self.team and q.active and q.role == 'field' and q.eligible(s.now)}
        A = ASSIGN.setdefault(self.team, {})
        if persist:
            for b, (d, until) in list(A.items()):                       # keep an assignment while it is alive and still reachable
                q = foes.get(d); p = mates.get(b)
                if q is None or p is None or until <= s.now or math.hypot(q.x - c.x, q.y - c.y) > g['block_reach'] + 4. or gap(p, q) > 14.: del A[b]
        def closing(q): return ((c.x - q.x) * q.vx + (c.y - q.y) * q.vy) / (math.hypot(q.x - c.x, q.y - c.y) or 1.)
        if persist and len(A) < k:
            taken = {d for d, _ in A.values()}
            cands = sorted((q for q in foes.values() if q.id not in taken and math.hypot(q.x - c.x, q.y - c.y) <= g['block_reach'] and closing(q) > -2.),
                           key=lambda q: math.hypot(q.x - c.x, q.y - c.y) - .5 * closing(q))
            for q in cands:
                if len(A) >= k: break
                free = [p for p in mates.values() if p.id not in A and gap(p, q) <= REACH_BLOCKER]
                if not free: continue
                ux, uy = c.x - q.x, c.y - q.y; n = math.hypot(ux, uy) or 1.
                # prefer a blocker already on the carrier's side of the defender (he does not have to get round him), then the nearest
                p = min(free, key=lambda p: gap(p, q) + (0. if ((p.x - q.x) * ux + (p.y - q.y) * uy) > 0 else 4.))
                A[p.id] = (q.id, s.now + 2500)
                if not any(b == p.id and d == q.id and t > s.now - 3000 for t, b, d, _ in PAIRS[-12:]): PAIRS.append((s.now, p.id, q.id, md))
        if not persist:
            return _legacy(self, s, out, g, c, k, mates, foes, md)
        for b, (d, _) in A.items():
            p, q = mates[b], foes[d]
            sp = max(8., 0.8 * p.a.maximum_speed); tl = min(1.0, max(0., gap(p, q)) / sp)
            fx, fy = q.x + q.vx * tl, q.y + q.vy * tl; ux, uy = c.x - fx, c.y - fy; n = math.hypot(ux, uy) or 1.
            out[b] = (min(99., max(1., fx + ux / n * .9)), min(99., max(1., fy + uy / n * .9)))
            STATS['assigned'] = STATS.get('assigned', 0) + 1; TRACE.setdefault((b, d), []).append((s.now, round(gap(p, q), 2)))
        return out
    def _legacy(self, s, out, g, c, k, mates, foes, md):
        pred = md == 'predict'; defs = sorted((q for q in foes.values() if math.hypot(q.x - c.x, q.y - c.y) <= g['block_reach']), key=lambda q: math.hypot(q.x - c.x, q.y - c.y))[:k]; used = set()
        for q in defs:
            cand = [p for p in mates.values() if p.id not in used]
            if not cand: break
            p = min(cand, key=lambda p: math.hypot(p.x - q.x, p.y - q.y)); used.add(p.id)
            fx, fy = (q.x + q.vx * .4, q.y + q.vy * .4) if pred else (q.x, q.y); ux, uy = c.x - fx, c.y - fy; n = math.hypot(ux, uy) or 1.
            out[p.id] = (min(99., max(1., fx + ux / n * .9)), min(99., max(1., fy + uy / n * .9))); STATS['assigned'] = STATS.get('assigned', 0) + 1; TRACE.setdefault((p.id, q.id), []).append((s.now, round(math.hypot(p.x - q.x, p.y - q.y) - p.radius - q.radius, 2)))
            if not any(b == p.id and d == q.id and t > s.now - 3000 for t, b, d, _ in PAIRS[-12:]): PAIRS.append((s.now, p.id, q.id, md))
        return out
    Pol.targets = targets
