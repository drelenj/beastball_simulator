"""Off-ball actions v0 (PRISM_OFFACT=1; needs the field PRISM layer).  Every field player who does not have the ball chooses among five actions, on his own beliefs, about every decision interval
(his PRISM decision_interval_s, at least .4 s; an action is held for its interval so he does not dither):
  RUN_OPEN   run to an open area: candidate spots around the engine's own target (so the formation / lane intention stays among the candidates), scored by believed openness (distance to the nearest believed
             opponent), believed pass-lane clearance from the carrier, progress toward goal, and distance from where the engine would have him.  (offence)
  ENGAGE     go to a believed opponent and fight hand to hand (the hand fight itself is physical: hand_fight_v0).  Offence: screen the defender who most threatens the carrier; defence: take the receiver / nearest attacker.
  CALL       as RUN_OPEN but he also calls for the ball (a voice call, heard by a team-mate within PRISM_CALL_R m after .25 s, locating him +-1.5 m, even if the passer cannot see him).  Worth it when the carrier is pressed.  (offence)
  WAIT       hold position (worth it when he is already open and in a good spot).
  FREE_BALL  run to where he believes a free ball (loose, or a pass in the air) can be met: candidate meeting times along the ball path his own eye believes, chosen with noise that shrinks with his
             In-Air Ball Pursuit (pass in flight) or Live Ball Pursuit (loose ground ball) rating; he commits only if he is among the three he believes can reach it first.
Placeholder scoring [P]: these are first rules to be replaced by what the emergent runs show; ratings enter as noise (1 - rating) on the option values and through PRISM perception.  Stats in S.fstats: oa_<action>, oa_calls.
"""
import os, math, random, zlib
import prism_ratings_v0 as PR
G = 9.81
OPEN_CAP, LANE_CAP = 10., 8.
W_OPEN, W_LANE, W_PROG, W_STAY = 1.0, 1.2, .25, .12
NOISE_SIG = float(os.environ.get('PRISM_OA_SIG', '2.0'))       # [P] option-value noise (value units) at judgement 0
FB_SIG = float(os.environ.get('PRISM_OA_FB', '2.5'))      # [P] metres of mislocation at pursuit rating 0
ENG_BASE = float(os.environ.get('PRISM_OA_ENG', '12.0'))      # [P] value of screening a defender at the carrier's side (same scale as the open-space values, ~10-20)
CALL_BONUS = float(os.environ.get('PRISM_OA_CALL', '2.5'))
def install(CO, S):
    Policy = CO.policies.Policy; o_targets = Policy.targets
    S.oa = {}; S.calls = {}; S.oa_over = {}
    def held(pid, key, now, win=.6): return random.Random(zlib.crc32(('%s|%s|%d|%s' % (getattr(S, 'seed', 1), pid, int(now / win), key)).encode())).gauss(0., 1.)
    def believed(pr, oid, now):
        b = pr.bget(oid)
        if b is None or pr.confidence(oid, now) < S.CONF_MIN: return None
        return pr.at_bounded(b, now) if S.BOUNDED else b.at(now)
    def speed(q): return max(5., .85 * getattr(q.a, 'maximum_speed', 9.))
    import importlib
    def free_ball_plan(s, q, pr, now):
        """(target point, cost) of the best believed meeting point for a free ball, or None if q has not got the ball in his eye"""
        bb = S.ball_belief(S.m, q, 3) if getattr(S, 'ball_belief', None) is not None else None
        if bb is None: return None
        x, y, z, vx, vy, vz = bb; mode = s.ball.mode.value; air = (mode == 'passed' and z > .3)
        R = PR.rj(S.RT(q.id), 'air_pursuit' if air else 'live_pursuit'); sg = NOISE_SIG * (1. - R)
        import types
        core = free_ball_plan.core; ns = types.SimpleNamespace(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, radius=s.ball.radius)
        path = core.predict_path(ns, G, S.m.assume.get('ball_drag', .015), S.m.assume.get('ball_restitution', .7745966692)); sp = speed(q); hh = getattr(q, 'hand_height', .72 * q.a.height); best = None
        cands = []
        for i in range(1, 15):
            t = .2 * i; k = min(len(path) - 1, int(round(t / .05)))
            if k <= 0: continue
            _, px, py, pz = path[k]
            if not (0 < px < 100 and 0 < py < 100): break
            late = max(0., math.hypot(px - q.x, py - q.y) / sp - t)
            if air and pz > hh + .9 * q.a.reach + .8: late += 2.            # above anything he can reach
            cands.append(((px, py), late + sg * .4 * held(q.id, 'f%d' % i, now), late, t))
        best = None
        if cands:                       # the EARLIEST meeting point he judges he can make (within .25 s of the best judged one): meet it, do not follow it
            thr = min(c[1] for c in cands) + .25
            best = next(c for c in cands if c[1] <= thr)
        if best is not None:      # misjudging where the ball will be: a held offset, 0 at rating 1
            o = FB_SIG * (1. - R) * min(1., best[3] / 1.2); ver = s.ball.version      # a misread of THIS ball's course, held for the whole course and fading as the ball arrives (the last moment is seen well)
            best = ((max(1., min(99., best[0][0] + o * held(q.id, 'fx%s' % ver, now, 8.))), max(1., min(99., best[0][1] + o * held(q.id, 'fy%s' % ver, now, 8.)))),) + best[1:]
        return best
    free_ball_plan.core = importlib.import_module(CO.match.Match.__module__)
    def believed_rank(s, q, pr, pt, now, t_me):
        """how many players he BELIEVES (team-mates and opponents he can place) would get to pt sooner than he would"""
        n = 0
        for o in s.players.values():
            if o.id == q.id or not o.active or o.role != 'field': continue
            pos = believed(pr, o.id, now)
            if pos is not None and math.hypot(pos[0] - pt[0], pos[1] - pt[1]) / speed(o) < t_me: n += 1
        return n
    def open_spots(s, q, pr, now, base, cpos, sgn, opp_pos):
        out = []
        pts = [base] + [(base[0] + r * math.cos(a), base[1] + r * math.sin(a)) for r in (4., 8.) for a in [k * math.pi / 4 for k in range(8)]]
        for (px, py) in pts:
            px = max(3., min(97., px)); py = max(3., min(97., py))
            op = min((math.hypot(ox - px, oy - py) for ox, oy in opp_pos), default=OPEN_CAP)
            lane = LANE_CAP if cpos is None else min((CO.policies.segment_distance(ox, oy, cpos[0], cpos[1], px, py)[0] for ox, oy in opp_pos), default=LANE_CAP)
            v = W_OPEN * min(op, OPEN_CAP) + W_LANE * min(lane, LANE_CAP) + W_PROG * sgn * (px - q.x) - W_STAY * math.hypot(px - base[0], py - base[1])
            out.append((v, (px, py), op))
        return out
    def decide(self, s, q, pr, base):
        now = s.now / 1000.; sgn = s.attack_sign(q.team); att = s.owner == q.team; b = s.ball
        J = PR.rj(S.RT(q.id), 'judgment'); sg = NOISE_SIG * (1. - J)
        opp_pos = [p for p in (believed(pr, o.id, now) for o in s.players.values() if o.team != q.team and o.active and o.role == 'field') if p is not None]
        # free ball
        if b.carrier is None and b.mode.value in ('loose', 'passed'):
            fb = free_ball_plan(s, q, pr, now)
            if fb is not None and fb[2] < 1.2 and believed_rank(s, q, pr, fb[0], now, math.hypot(fb[0][0] - q.x, fb[0][1] - q.y) / speed(q)) < 3: return 'FREE_BALL', fb[0], False
            return 'DEFAULT', base, False
        c = s.players.get(b.carrier) if b.carrier else None
        if c is None: return 'DEFAULT', base, False
        cpos = (q.x, q.y) if c.id == q.id else believed(pr, c.id, now)
        if att and c.team == q.team:
            spots = open_spots(s, q, pr, now, base, cpos, sgn, opp_pos); vbest, pbest, opn = max(spots, key=lambda t: t[0] + sg * held(q.id, 'o%.0f%.0f' % t[1], now))
            pressed = cpos is not None and min((math.hypot(ox - cpos[0], oy - cpos[1]) for ox, oy in opp_pos), default=30.) < 6.
            here = next((t for t in spots if t[1] == (max(3., min(97., base[0])), max(3., min(97., base[1])))), spots[0])
            v = {'RUN_OPEN': vbest + sg * held(q.id, 'a1', now), 'WAIT': here[0] + 1.5 * (here[2] > 6.) + sg * held(q.id, 'a2', now),
                 'CALL': vbest - 1.0 + (CALL_BONUS if pressed and opn > 5. else 0.) + sg * held(q.id, 'a3', now)}
            # engage: screen the believed defender who threatens the carrier most (closest to him), if he is not far
            thr = [(math.hypot(po[0] - cpos[0], po[1] - cpos[1]), o, po) for o in s.players.values() if o.team != q.team and o.active and o.role == 'field' and cpos is not None for po in [believed(pr, o.id, now)] if po is not None]
            eng = None
            if thr:
                d_, o_, po_ = min(thr, key=lambda t: t[0] + .15 * math.hypot(t[2][0] - q.x, t[2][1] - q.y))
                ux, uy = cpos[0] - po_[0], cpos[1] - po_[1]; n_ = math.hypot(ux, uy) or 1.
                eng = (max(1., min(99., po_[0] + ux / n_ * .9)), max(1., min(99., po_[1] + uy / n_ * .9)))
                v['ENGAGE'] = ENG_BASE + (8. - min(8., d_)) * 1.0 - .25 * math.hypot(eng[0] - q.x, eng[1] - q.y) + (6. if pressed else 0.) + sg * held(q.id, 'a4', now)
            k = max(v, key=v.get)
            return k, (eng if k == 'ENGAGE' else (pbest if k in ('RUN_OPEN', 'CALL') else (q.x, q.y))), k == 'CALL'
        if (not att) and c.team != q.team:
            # defence: take the nearest believed attacker who is not the carrier, if he is close; otherwise the engine's own mark/zone
            near = [(math.hypot(po[0] - q.x, po[1] - q.y), po) for o in s.players.values() if o.team != q.team and o.id != c.id and o.active and o.role == 'field' for po in [believed(pr, o.id, now)] if po is not None]
            if near:
                d_, po = min(near, key=lambda t: t[0])
                if d_ < 8. and (d_ + sg * held(q.id, 'd', now)) < 6.: return 'ENGAGE', (max(1., min(99., po[0] - sgn * .0)), max(1., min(99., po[1]))), False
        return 'DEFAULT', base, False
    def targets(self, s):
        out = o_targets(self, s)
        if os.environ.get('PRISM_OFFACT', '0') != '1' or getattr(S, 'm', None) is None: return out
        now_ms = s.now
        for pid in [k for k, v in S.oa_over.items() if s.players[k].team == self.team]: S.oa_over.pop(pid, None)
        for q in s.players.values():
            if q.team != self.team or q.role != 'field' or not q.active or q.id not in out or q.id not in S.fprism or q.id == s.ball.carrier: continue
            pr = S.fprism[q.id]; st = S.oa.get(q.id)
            ivl = max(.4, getattr(pr, 'prof', {}).get('decision_interval_s', .4)) * 1000.
            if st is None or now_ms - st[0] >= ivl or st[4] != s.ball.version:
                kind, tgt, call = decide(self, s, q, pr, out[q.id]); S.oa[q.id] = st = (now_ms, kind, tgt, call, s.ball.version)
                S.fstats['oa_' + kind] += 1
                if call: S.calls[q.id] = (now_ms, q.x, q.y); S.fstats['oa_calls'] += 1
            kind, tgt = st[1], st[2]
            if kind == 'DEFAULT': continue
            out[q.id] = (q.x, q.y) if kind == 'WAIT' else tgt; S.oa_over[q.id] = out[q.id]
        return out
    Policy.targets = targets
    # the engine's own receiver routing and receiver-spot logic run AFTER the policy and overwrite targets; an action this player chose on his own beliefs stands
    Match = CO.match.Match
    for nm in ('route_receiver', 'c4c2_targets'):
        if hasattr(Match, nm):
            def mk(o):
                def w(self, tg):
                    keep = {pid: tg[pid] for pid in S.oa_over if pid in tg}
                    r = o(self, tg)
                    if os.environ.get('PRISM_OFFACT', '0') == '1':
                        for pid, t in keep.items(): tg[pid] = t
                    return r
                return w
            setattr(Match, nm, mk(getattr(Match, nm)))
