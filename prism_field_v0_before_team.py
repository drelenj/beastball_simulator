"""PRISM v0.2 - FIELD PLAYERS, first step: the BALL CARRIER perceives its opponents through its own cone and radar.
Every field player of both teams keeps its own perception (ArcherPrism core: cone, radar, latency, tracks, beliefs), ticked at 10 Hz.
Only the carrier's own decisions read beliefs (flag PRISM_FIELD=1):
  - Policy.targets  -> the carrier's destination (lane choice among 5 lanes, scored by room to the 4 nearest opponents)
  - Policy.pass_ranked / pass_choice -> the passer's option ranking (lane clearance, pressure)
Opponents the carrier does not know are hidden for the call; known ones are shown at their belief position/velocity.  Teammates, ball and public status stay true (provisional).
v0.6 (PRISM_OFFBALL=1): every field player chooses his own target through his own view of the opponents.  Keepers: see prism_keeper_v0.  Teammates, the free ball and public status still read true for field players.  Ratings come from PRISM_FIELD_RATINGS (json, neutral = .5).
"""
import math, os, json, random
from collections import Counter
import prism_archer_v0 as A
import prism_perception_v012 as PP
import prism_ratings_v0 as PR

FIELD = os.environ.get('PRISM_FIELD', '0') == '1'
FR = json.loads(os.environ.get('PRISM_FIELD_RATINGS', '{}'))
TICK_MS = 100; CONF_MIN = .3
SKIP = set()   # player ids whose perception is not ticked (drills: parked players)
DEF = os.environ.get('PRISM_DEF', '0') == '1'            # v0.4: the nearest DEF_K defenders choose their pursuit targets from their own beliefs about the attackers
DEF_K = int(os.environ.get('PRISM_DEF_K', '3'))
OFFBALL = os.environ.get('PRISM_OFFBALL', '0') == '1'      # v0.6: every other field player (off-ball attackers, the rest of the defenders) chooses his own target through his own view of the opponents
OFF_K = int(os.environ.get('PRISM_OFF_K', '99'))            # at most this many such players per team, nearest the ball first
BOUNDED = os.environ.get('PRISM_BOUNDED', '0') == '1'          # stale beliefs extrapolate with decaying velocity (prevents long-memory phantoms)
BALLVIEW = os.environ.get('PRISM_BALLVIEW', '1') == '1'        # a defender's ball position is his belief about the opposing carrier, not the true ball
CARRIER_BELIEF = os.environ.get('PRISM_CARRIER_BELIEF', '1') == '1'   # an opposing carrier is never 'hidden' (that leaked his true position); he is shown at his believed one
AUDIT = os.environ.get('PRISM_AUDIT', '0') == '1'            # diagnostic: sentinel test for leaks through hidden bodies
JUDGE_DEF = os.environ.get('PRISM_JUDGE_DEF', '0') == '1'     # defenders choose among intercept points (options and lookahead scale with Judgment)
JD_NOISE = float(os.environ.get('PRISM_JD_NOISE', '3.0')); JD_HABIT = float(os.environ.get('PRISM_JD_HABIT', '3.0'))   # [P] v3 selection noise (m) and pull to the habitual option (m) at Judgment 0
JD_L = float(os.environ.get('PRISM_JD_L', '2.0')); JD_ALAT = float(os.environ.get('PRISM_JD_ALAT', '3.0'))   # [P] candidate horizon (s) and the lateral acceleration a carrier is assumed able to add (m/s^2)
HIDE_CARRIER = os.environ.get('PRISM_HIDE_CARRIER', '0') == '1'   # diagnostic: the opposing carrier is never a player in a defender's view; only the (belief) ball tells him where he is
FOCUS_ONLY = os.environ.get('PRISM_FOCUS_ONLY', '')          # diagnostic: slew | memory | pulse | tracked | identify
PURSUIT_R = float(os.environ.get('PRISM_PURSUIT_R', '6'))   # a defender decision is a pursuit when his true target is within this of the carrier

def install(CO, S, seed_fn):
    def RT(pid):
        """A player's ratings: the global PRISM_FIELD_RATINGS override (sweeps) if set, else his own (S.prism_r from prism_ratings_v0), else neutral .5."""
        return FR if FR else (getattr(S, 'prism_r', None) or {}).get(pid, PR.NEUTRAL)
    S.RT = RT
    Match = CO.match.Match; Policy = CO.policies.Policy
    S.fprism = {}; S.fstats = Counter(); S.flast = {}
    o_step = Match.step; o_targets = Policy.targets; o_rank = Policy.pass_ranked; o_choice = Policy.pass_choice

    def get(p):
        pr = S.fprism.get(p.id)
        if pr is None:
            pr = A.ArcherPrism(f'{seed_fn()}-F-{p.id}', .5, p.a.decision_speed, dict(vel_mode='lsq', win_s=.4))
            rt = RT(p.id); pr.apply_ratings(rt if not FOCUS_ONLY else dict(rt, focus=.5))
            if FOCUS_ONLY:       # diagnostic: only ONE focus-owned parameter takes the focus rating's value, the rest stay at focus=.5
                pf = PP.perception_profile(rt)
                if FOCUS_ONLY == 'slew': pr.P['slew_dps'] = pf['gaze_slew_dps'] / (.6 + .4 * .5)
                elif FOCUS_ONLY == 'memory': pr.P['memory_s'] = pf['belief_tau_s'] / (.7 + .6 * .5)
                elif FOCUS_ONLY == 'pulse': pr.prof['radar_pulse_period_s'] = pf['radar_pulse_period_s']
                elif FOCUS_ONLY == 'tracked': pr.prof['tracked_count'] = pf['tracked_count']
                elif FOCUS_ONLY == 'identify': pr.prof['identify_delay_s'] = pf['identify_delay_s']
            S.fprism[p.id] = pr
        return pr

    def step(self):
        r = o_step(self); s = self.s; now_ms = s.now
        if now_ms - S.flast.get('t', -9999) < TICK_MS: return r
        S.flast['t'] = now_ms; now = now_ms / 1000.
        live = [p for p in s.players.values() if p.active and p.role != 'archer']
        bodies_all = [dict(id=p.id, x=p.x, y=p.y, z=p.z, h=p.a.height, r=p.radius, team=p.team, vx=p.vx, vy=p.vy) for p in live]
        cid = s.ball.carrier
        for p in live:
            if p.role != 'field' or p.id in SKIP: continue
            pr = get(p); sgn = s.attack_sign(p.team)
            face = math.atan2(p.vy, p.vx) if math.hypot(p.vx, p.vy) > 1. else (p.facing if isinstance(p.facing, (int, float)) else (0. if sgn > 0 else math.pi))
            focus = (p.x + sgn * 15, p.y) if cid == p.id else (s.ball.x, s.ball.y)
            opp_c = s.players.get(cid) if cid and s.players.get(cid) is not None and s.players[cid].team != p.team else None
            pr.tick(now, (p.x, p.y, .72 * p.a.height), face, [b for b in bodies_all if b['id'] != p.id], focus, opp_c.id if opp_c else None)
        return r

    def with_view(s, p, fn):
        """Run fn() with opponents swapped for p's beliefs."""
        pr = S.fprism.get(p.id)
        if pr is None: return fn()
        now = s.now / 1000.; saved = []; hidden = []; ball_saved = None
        cq = s.players.get(s.ball.carrier) if s.ball.carrier else None
        if BALLVIEW and cq is not None and cq.team != p.team:
            # an opposing carrier's ball is where HE is: the defender knows it only as well as he knows the carrier (no free ball position)
            bq = pr.bget(cq.id); bl = s.ball
            if bq is not None: pos = pr.at_bounded(bq, now) if BOUNDED else bq.at(now); vel = pr.intent_vel(bq, now); pr.last_ball = (pos, vel); S.fstats['ball_view'] += 1
            elif getattr(pr, 'last_ball', None) is not None: pos, vel = pr.last_ball; S.fstats['ball_view_stale'] += 1
            else: pos, vel = (50., 50.), (0., 0.); S.fstats['ball_unaware'] += 1       # never seen the carrier: assume play is at midfield (uninformative), not the true ball
            if pos is not None: ball_saved = (bl, bl.x, bl.y, bl.vx, bl.vy); bl.x, bl.y = pos; bl.vx, bl.vy = vel
        for q in s.players.values():
            if q.team == p.team or q.role == 'archer' or not q.active: continue
            b = pr.bget(q.id)
            if CARRIER_BELIEF and cq is not None and q.id == cq.id and cq.team != p.team:
                # the policy finds the carrier by the ball's carrier id, so 'hiding' him leaves his TRUE position visible.  Always substitute what the defender believes (stale and bounded if he lost him).
                if b is not None: bx, by = (pr.at_bounded(b, now) if BOUNDED else b.at(now)); bvx, bvy = pr.intent_vel(b, now); S.fstats['carrier_belief'] += 1
                elif getattr(pr, 'last_ball', None) is not None: (bx, by), (bvx, bvy) = pr.last_ball; S.fstats['carrier_belief_stale'] += 1
                else: bx, by, bvx, bvy = 50., 50., 0., 0.; S.fstats['carrier_unaware'] += 1     # never seen him: uninformative placeholder, not his true position
                saved.append((q, q.x, q.y, q.vx, q.vy)); q.x, q.y, q.vx, q.vy = bx, by, bvx, bvy; continue
            if b is None or pr.confidence(q.id, now) < CONF_MIN or (HIDE_CARRIER and cq is not None and q.id == cq.id and cq.team != p.team): hidden.append(q); q.active = False; S.fstats['hidden_opp'] += 1; continue
            bx, by = (pr.at_bounded(b, now) if BOUNDED else b.at(now)); bvx, bvy = pr.intent_vel(b, now); saved.append((q, q.x, q.y, q.vx, q.vy)); q.x, q.y, q.vx, q.vy = bx, by, bvx, bvy; S.fstats['seen_opp'] += 1
        try:
            if not AUDIT or not hidden: return fn()
            r1 = fn()                                            # audit: if hiding really hides, moving the hidden bodies far away must change nothing
            sv = [(q, q.x, q.y) for q in hidden]
            for q in hidden: q.x, q.y = 1e6, 1e6
            try: r2 = fn()
            finally:
                for q, x, y in sv: q.x, q.y = x, y
            S.fstats['audit_n'] += 1; S.fstats['audit_diff'] += (r1 != r2)
            return r1
        finally:
            for q, x, y, vx, vy in saved: q.x, q.y, q.vx, q.vy = x, y, vx, vy
            for q in hidden: q.active = True
            if ball_saved is not None: bl, bl.x, bl.y, bl.vx, bl.vy = ball_saved[0], *ball_saved[1:]

    seg = CO.policies.segment_distance; clampf = lambda v, lo, hi: max(lo, min(hi, v))
    def regret(s, c, true_t, view_t):
        """Decision quality of the carrier's lane choice, scored on TRUE positions with the policy's own lane formula (room to the 4 nearest opponents - small lane penalties).
        regret = score(best lane under truth) - score(lane chosen from beliefs).  Only ordinary carries (not inside 14 m of the goal)."""
        sgn = s.attack_sign(c.team)
        if true_t is None or abs(s.attack_goal(c.team) - c.x) < 14: return
        opp = [q for q in s.players.values() if q.team != c.team and q.eligible(s.now) and q.role != 'archer']
        near = sorted(opp, key=lambda q: math.hypot(q.x - c.x, q.y - c.y))[:4]
        def sc(y):
            end = (clampf(c.x + sgn * 12, 0, 100), y); room = min((seg(q.x, q.y, c.x, c.y, *end)[0] for q in near), default=20)
            return room - .025 * abs(y - 50) - .08 * abs(y - c.y)
        opts = [clampf(c.y + dy, 4, 96) for dy in (-14, -7, 0, 7, 14)]; pick = min(opts, key=lambda y: abs(y - view_t[1]))
        r = max(sc(y) for y in opts) - sc(pick); S.fstats['reg_n'] += 1; S.fstats['reg_sum_x100'] += int(round(100 * r)); S.fstats['reg_zero'] += (r < 1e-9)
        S.fstats['reg_big'] += (r > 3.)
    def defend(self, s, out, c):
        """Defending team: each of the DEF_K defenders nearest the carrier re-chooses his own target through his own view of the attackers."""
        ds = sorted((d for d in s.players.values() if d.team == self.team and d.active and d.role == 'field' and d.id in out), key=lambda d: math.hypot(d.x - c.x, d.y - c.y))[:DEF_K]
        for d in ds:
            if d.id not in S.fprism: continue
            alt = with_view(s, d, lambda: o_targets(self, s))
            if d.id in alt:
                S.fstats['def_views'] += 1
                S.fstats['def_err_x100'] += int(round(100 * math.hypot(alt[d.id][0] - out[d.id][0], alt[d.id][1] - out[d.id][1])))   # how far his belief-based target is from the omniscient one
                S.fstats['def_unseen'] += (S.fprism[d.id].bget(c.id) is None or S.fprism[d.id].confidence(c.id, s.now / 1000.) < CONF_MIN)
                if JUDGE_DEF: alt[d.id] = judge_target(s, d, c, alt[d.id])
                def_regret(s, d, c, out[d.id], alt[d.id])
                out[d.id] = alt[d.id]
    _jn = {}
    JD_PROBE = os.environ.get('PRISM_JD_PROBE', '0') == '1'
    PJ = (0., .1, .3, .5, .7, .95, 1.)
    def _probe(s, d, c, T0, bc, bv, sp, n, z):
        """Paired counterfactual: game unchanged (aim at carrier); for the SAME decision, what each Judgment level would have chosen, scored on true state."""
        dist = math.hypot(c.x - d.x, c.y - d.y)
        if dist > 30 or dist < 10: return
        def miss(T):
            t = math.hypot(T[0] - d.x, T[1] - d.y) / sp; return math.hypot(T[0] - (c.x + c.vx * t), T[1] - (c.y + c.vy * t))
        cand = []
        for i in range(n):
            tau = .25 * i; T = (bc[0] + bv[0] * tau, bc[1] + bv[1] * tau); ta = math.hypot(T[0] - d.x, T[1] - d.y) / sp
            cand.append((T, math.hypot(T[0] - (bc[0] + bv[0] * ta), T[1] - (bc[1] + bv[1] * ta)) + .5 * JD_ALAT * ta * ta))
        S.fstats['pj_n'] += 1; S.fstats['pj_base_x100'] += int(round(100 * miss(T0)))
        S.fstats['pj_menu_oracle_x100'] += int(round(100 * min(miss(T) for T, _ in cand)))
        for J in PJ:
            bi = min(range(n), key=lambda i: cand[i][1] + JD_NOISE * (1. - J) * z[1][i] - (JD_HABIT * (1. - J) if i == 0 else 0.))
            S.fstats['pj_J%d_x100' % int(round(J * 100))] += int(round(100 * miss(cand[bi][0]))); S.fstats['pj_Jfar%d' % int(round(J * 100))] += (bi >= 4)
    def judge_target(s, d, c, T0):
        """Defender Judgment = quality of the CHOICE among options that already exist (v3).  Everyone sees the same menu: intercept points along the believed carrier track,
        tau = 0 (aim at the carrier) to JD_L s in .25 s steps, each scored by predicted miss with the full uncertainty charge (that comes from Inference, not Judgment).
        Judgment sets how reliably the best-scoring option is chosen: score noise sigma = JD_NOISE x (1-J) (held ~.6 s so it is a misjudgment, not jitter) and a pull toward the
        habitual option (tau = 0) of JD_HABIT x (1-J).  J = 1 takes the lowest predicted miss; J = 0 is mostly simple pursuit with noise.  Only for pursuit decisions."""
        pr = S.fprism.get(d.id); b = pr.bget(c.id) if pr else None
        if b is None: return T0
        now = s.now / 1000.; bc = pr.at_bounded(b, now) if BOUNDED else b.at(now); bv = pr.intent_vel(b, now)
        if math.hypot(T0[0] - bc[0], T0[1] - bc[1]) > PURSUIT_R: return T0
        J = float(RT(d.id).get('judgment', .5)); sp = max(math.hypot(d.vx, d.vy), 8.); n = int(round(JD_L / .25)) + 1
        z = _jn.get(d.id)
        if z is None or now - z[0] > .6 or len(z[1]) != n:
            rg = _jn.setdefault('rng', random.Random(7919 * int(getattr(S, 'seed', 1)) + 3)); z = _jn[d.id] = (now, [rg.gauss(0, 1) for _ in range(n)])
        if JD_PROBE: _probe(s, d, c, T0, bc, bv, sp, n, z); return T0
        best, bs = T0, 1e9
        for i in range(n):
            tau = .25 * i; T = (bc[0] + bv[0] * tau, bc[1] + bv[1] * tau); ta = math.hypot(T[0] - d.x, T[1] - d.y) / sp
            m = math.hypot(T[0] - (bc[0] + bv[0] * ta), T[1] - (bc[1] + bv[1] * ta)) + .5 * JD_ALAT * ta * ta
            sc = m + JD_NOISE * (1. - J) * z[1][i] - (JD_HABIT * (1. - J) if i == 0 else 0.)
            if sc < bs - 1e-9: best, bs = T, sc
        S.fstats['jd_n'] += 1; S.fstats['jd_moved_x100'] += int(round(100 * math.hypot(best[0] - T0[0], best[1] - T0[1])))
        return best
    def def_regret(s, d, c, true_t, view_t):
        """Defender decision regret.  A target T is scored on TRUE state by where the carrier really is when the defender arrives:
        miss(T) = | T - (carrier + carrier_velocity x t_arrive) |,  t_arrive = |T - d| / max(d speed, 8 m/s).  regret = miss(belief target) - miss(omniscient target).
        Only while the carrier is within 30 m (a pursuit decision) and not inside 10 m of the defender (closing technique takes over)."""
        dist = math.hypot(c.x - d.x, c.y - d.y)
        if dist > 30 or dist < 10: return
        if math.hypot(true_t[0] - c.x, true_t[1] - c.y) > PURSUIT_R: S.fstats['dreg_zone'] += 1; return      # his omniscient target is a zone/position, not a pursuit of the carrier: not scored
        sp = max(math.hypot(d.vx, d.vy), 8.)
        def miss(T):
            t = math.hypot(T[0] - d.x, T[1] - d.y) / sp
            return math.hypot(T[0] - (c.x + c.vx * t), T[1] - (c.y + c.vy * t))
        r = miss(view_t) - miss(true_t)
        S.fstats['dreg_n'] += 1; S.fstats['dreg_sum_x100'] += int(round(100 * r)); S.fstats['dreg_pos'] += (r > .25); S.fstats['dreg_big'] += (r > 2.)
        S.fstats['dreg_miss_view_x100'] += int(round(100 * miss(view_t))); S.fstats['dreg_miss_true_x100'] += int(round(100 * miss(true_t)))
    def targets(self, s):
        out = o_targets(self, s); c = s.players.get(s.ball.carrier)
        if DEF and c is not None and c.team != self.team: defend(self, s, out, c)
        if OFFBALL:
            ball_xy = (s.ball.x, s.ball.y); done = {c.id} if c is not None and c.team == self.team else set()
            if DEF and c is not None and c.team != self.team: done |= set(sorted((d.id for d in s.players.values() if d.team == self.team and d.active and d.role == 'field' and d.id in out), key=lambda i: math.hypot(s.players[i].x - c.x, s.players[i].y - c.y))[:DEF_K])
            rest = sorted((q for q in s.players.values() if q.team == self.team and q.active and q.role == 'field' and q.id in out and q.id in S.fprism and q.id not in done), key=lambda q: math.hypot(q.x - ball_xy[0], q.y - ball_xy[1]))[:OFF_K]
            for q in rest:
                alt = with_view(s, q, lambda: o_targets(self, s))
                if q.id in alt:
                    S.fstats['off_views'] += 1; S.fstats['off_err_x100'] += int(round(100 * math.hypot(alt[q.id][0] - out[q.id][0], alt[q.id][1] - out[q.id][1]))); out[q.id] = alt[q.id]
        if c is not None and c.team == self.team and c.role == 'field' and c.id in S.fprism:
            S.fstats['carrier_views'] += 1
            alt = with_view(s, c, lambda: o_targets(self, s))
            if c.id in alt:
                regret(s, c, out.get(c.id), alt[c.id]); out[c.id] = alt[c.id]
        return out
    def pass_ranked(self, s, p): return with_view(s, p, lambda: o_rank(self, s, p)) if p.role == 'field' else o_rank(self, s, p)
    def pass_choice(self, s, p): return with_view(s, p, lambda: o_choice(self, s, p)) if p.role == 'field' else o_choice(self, s, p)
    Match.step = step; Policy.targets = targets; Policy.pass_ranked = pass_ranked; Policy.pass_choice = pass_choice
