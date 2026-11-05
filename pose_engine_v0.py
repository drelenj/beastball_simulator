"""Pocket 4.0 hook layer: carry poses + evasion maneuvers on the ball carrier (spec v0.1.1, lab v0.1.4 numbers).  Enabled with PRISM_MANEUVERS=1.
Flag off: install() is never called and the engine is untouched.

What it does (every number [P], taken from the maneuver lab):
  pose      each ball carrier has a pose_maneuvers_v0.Carrier FSM (loaded/extended/exposed/tucked/braced, adjacent steps, tells, execution).  The release-delay hook reads this pose.
  policy    ~10 Hz: a carrier with a defender inside TRIGGER_M and closing may start juke / spin / stiff-arm / truck; the choice is by his own ratings (placeholder policy, no PRISM belief yet).
  motion    juke / spin: lateral offset (agility) spread over the execution + a speed cost; applied as a position nudge and a speed scale (the engine's own contact kernel handles bodies).
  tackle    Engine.tackle (the grounding commit): an executing maneuver can defeat it with probability from a skill contest (lab outcome tables); a defeated grounding is logged and the carrier keeps going.
  strip     Engine.strip (kernel-scheduled strip): accepted with probability (1 - resist[pose]) / (1 - resist[exposed]), capped at 1 (a pose cannot make a strip MORE likely than the engine scheduled).
  contact   an engagement on the carrier aborts transitions / tells / pending maneuvers (Carrier.on_contact).
"""
import math, random, json
from collections import Counter
import pose_maneuvers_v0 as PM

TRIGGER_M = 7.0           # [P] a defender this close and closing makes the carrier consider a maneuver
CLOSING_MIN = 6.0         # [P] m/s
DECIDE_MS = 100           # [P] decision tick
COOLDOWN_MS = 1200        # [P] between maneuvers
BASE = {'juke': .50, 'spin': .45, 'stiffarm': .55, 'truck': .55}     # [P] evade probability for equal ratings
K_SKILL = .6              # [P] weight of the rating gap
JUKE_MIN, JUKE_AGI = .7, .9
SPIN_OFFSET = .5
JUKE_COST, SPIN_COST = .10, .18
REF_POSE = 'tucked'      # the engine's scheduled strip rate is taken to be that of an Exposed carry
STRIP_FLOOR = .1
import os
NUDGE = float(os.environ.get('PM_NUDGE', '1.0'))      # [P] scale on the lateral displacement of juke/spin (calibration knob)
TELL_READ = .5            # [P] a fully read tell halves the carrier's evade chance
OUT_MS = 1500             # a maneuver is 'clear' if no grounding follows within this long


def install(CO, S, seed_fn=lambda: 1):
    Match, Engine = CO.match.Match, CO.engine.Engine
    norm = CO.geometry.norm
    o_step, o_tackle, o_strip, o_engage = Match.step, Engine.tackle, Engine.strip, Engine.engage

    class St:
        pass

    def st(m):
        z = getattr(m, 'pm', None)
        if z is None:
            z = m.pm = St(); z.car = None; z.fsm = None; z.last_dec = -10 ** 9; z.cool = -10 ** 9; z.man = None; z.stats = Counter(); z.log = []
            z.rng = random.Random(1000003 * seed_fn() + 17); z.last_now = 0; z.open_out = []
            S.pm = z
        return z

    def ratings(p):
        a = p.a; return dict(agi=a.agility, str=a.strength, tech=a.ball_handling, bal=a.balance, mass=a.mass, tack=a.tackling, rdelay=a.decision_speed)

    def unit(x, y):
        n = math.hypot(x, y) or 1e-9; return x / n, y / n

    def new_carrier(m, z, p):
        near = min((norm(q.x - p.x, q.y - p.y) for q in m.s.players.values() if q.team != p.team and q.active and q.role != 'archer'), default=99.)
        z.car = p.id; z.fsm = PM.Carrier('tucked' if near < 8. else 'exposed'); z.man = None; z.cool = m.s.now

    def nearest_threat(m, p):
        best = None
        for q in m.s.players.values():
            if q.team == p.team or not q.active or q.role == 'archer' or not m.e.eligible(q): continue
            dx, dy = q.x - p.x, q.y - p.y; d = math.hypot(dx, dy)
            if d < 1e-6: continue
            closing = -((q.vx - p.vx) * dx + (q.vy - p.vy) * dy) / d      # >0 when the gap is shrinking
            if best is None or d < best[0]: best = (d, q, closing, dx, dy)
        return best

    def decide(m, z, p):
        th = nearest_threat(m, p)
        if th is None: return
        d, q, cl, dx, dy = th
        if d > TRIGGER_M or cl < CLOSING_MIN or m.s.now - z.cool < COOLDOWN_MS: return
        if z.fsm.active or z.fsm.pending or z.fsm.in_transition: return
        rc, rd = ratings(p), ratings(q)
        # placeholder policy: expected value ~ the lab's outcome tables, by own ratings; weights read his own strengths
        v = {'juke': .45 + .3 * rc['agi'], 'spin': .40 + .3 * rc['agi'] * rc['tech'],
             'stiffarm': .35 + .4 * rc['str'] * rc['tech'], 'truck': .30 + .5 * rc['str'] * min(1.4, rc['mass'] / max(1., rd['mass']))}
        v['none'] = .62
        amp = .08 + (float(os.environ.get('PRISM_CD_SIG', '.5')) * (1. - S.RJ(p.id, 'carrier_duel')) if os.environ.get('PRISM_JSPLIT', '0') == '1' and hasattr(S, 'RJ') else 0.)   # Carrier Duel: how reliably the best maneuver is the one tried
        kind = max(v, key=lambda k: v[k] + z.rng.uniform(-amp, amp))
        if kind == 'none': z.cool = m.s.now - COOLDOWN_MS + 400; z.stats['ctl_n'] += 1; z.open_out.append(['none', m.s.now]); return
        side = 1 if (dx * -p.vy + dy * p.vx) > 0 else -1          # defender on the left of travel (+1): break right
        side = -side
        z.fsm.start_maneuver(kind); z.pend_side = side; z.stats['try_' + kind] += 1; z.cool = m.s.now

    def apply_motion(m, z, p, dt_ms):
        f = z.fsm
        while z.log_seen < len(f.log):
            t, ev, k = f.log[z.log_seen]; z.log_seen += 1
            if ev == 'start':
                rc = ratings(p); ag = rc['agi']
                off = NUDGE * (JUKE_MIN + JUKE_AGI * ag if k == 'juke' else SPIN_OFFSET if k == 'spin' else 0.)
                z.man = dict(kind=k, T=PM.EXEC_MS[k] / 1000., off=off, side=getattr(z, 'pend_side', 1), left=PM.EXEC_MS[k] / 1000.)
                cost = JUKE_COST if k == 'juke' else SPIN_COST if k == 'spin' else 0.
                if cost: p.vx *= 1 - cost * (1.3 - ag); p.vy *= 1 - cost * (1.3 - ag)
                z.stats['start_' + k] += 1; z.open_out.append([k, m.s.now])
            elif ev in ('done', 'interrupted'): z.man = None
        mn = z.man
        if mn and mn['off'] and f.active:
            dt = dt_ms / 1000.; ux, uy = unit(p.vx, p.vy); step = mn['off'] * min(dt, mn['left']) / mn['T']
            p.x += -uy * mn['side'] * step; p.y += ux * mn['side'] * step; mn['left'] -= dt

    def step(self):
        o_step(self)
        z = st(self); s = self.s
        dt = max(0, s.now - z.last_now); z.last_now = s.now
        cid = s.ball.carrier
        if cid is None or s.phase != CO.types.Phase.LIVE:
            z.car = None; z.fsm = None; z.man = None; return
        p = s.players[cid]
        if z.car != cid: new_carrier(self, z, p); z.log_seen = 0
        # pose policy when no maneuver is pending: tuck under pressure, relax otherwise (loaded/extended come from the throw decision)
        f = z.fsm
        if f.pending is None and not f.active and f.tell_left <= 0 and not f.in_transition and not f.pinned:
            th = nearest_threat(self, p)
            want = 'tucked' if (th and th[0] < 8.) else 'exposed'
            if f.pose in ('exposed', 'tucked') and f.pose != want: f.request_pose(want)
        if s.now - z.last_dec >= DECIDE_MS:
            z.last_dec = s.now; decide(self, z, p)
        f.step(dt)
        keep = []
        for k_, t0 in z.open_out:
            if s.now - t0 >= OUT_MS: z.stats['out_clear_' + k_] += 1
            else: keep.append([k_, t0])
        z.open_out = keep
        apply_motion(self, z, p, dt)
        z.stats['pose_' + f.pose] += 1

    def engage(self, actor, target, kind='tackle', *a, **k):
        ok = o_engage(self, actor, target, kind, *a, **k)
        z = getattr(getattr(self, 'match', None), 'pm', None)
        if ok and z and z.fsm and kind == 'tackle' and target == z.car: z.fsm.on_contact(); z.stats['contacts'] += 1
        return ok

    def contest(kind, rc, rd):
        if kind == 'juke': gap = rc['agi'] - rd['agi']
        elif kind == 'spin': gap = rc['agi'] * rc['tech'] - rd['agi'] * rd['tech']
        elif kind == 'stiffarm': gap = rc['str'] * (.5 + .5 * rc['tech']) - rd['str'] * (.5 + .5 * rd['tech'])
        else: gap = rc['str'] * rc['mass'] / 100. - rd['str'] * rd['tack'] * rd['mass'] / 100. if False else (rc['str'] * rc['mass'] - rd['str'] * rd['mass']) / 120.
        return max(.05, min(.9, BASE[kind] + K_SKILL * gap))

    def tackle(self, actor, target, body='knee', witnessed=False):
        z = getattr(getattr(self, 'match', None), 'pm', None)
        kind0 = (z.fsm.active or (z.man['kind'] if z.man else None)) if (z and z.fsm and target == z.car) else None   # contact clears fsm.active first; z.man persists to the next tick
        if kind0 in BASE:
            kind = kind0; a, t = self.s.players[actor], self.s.players[target]
            pe = contest(kind, ratings(t), ratings(a)); z.stats['tackle_vs_' + kind] += 1
            fp = getattr(S, 'fprism', {}).get(actor) if os.environ.get('PRISM_DEF', '0') == '1' else None
            if fp is not None:     # a defender who actually sees the carrier reads the tell: Clarity/Focus ride in his confidence, Instinct classifies it
                conf = fp.confidence(target, self.s.now / 1000.); ins = float(getattr(S, 'RT', lambda _: {})(actor).get('instinct', .5))
                read = conf * ins; pe *= (1. - TELL_READ * read); z.stats['tell_read_x100'] += int(round(100 * read)); z.stats['tell_read_n'] += 1
            if z.rng.random() < pe:
                z.stats['evaded_' + kind] += 1; self.emit('maneuver_evade', 'P4-man', actor=actor, target=target, kind=kind, p=round(pe, 3))
                return False
        if z and z.fsm and target == z.car and z.open_out:
            for k_, t0 in z.open_out: z.stats['out_tackled_' + k_] += 1
            z.open_out = []
        return o_tackle(self, actor, target, body, witnessed)

    def strip(self, actor, target, witnessed=False):
        z = getattr(getattr(self, 'match', None), 'pm', None)
        if z and z.fsm and target == z.car:
            r = z.fsm.strip_resistance(); acc = min(1., max(STRIP_FLOOR, (1. - r) / (1. - PM.STRIP_RESIST[REF_POSE])))
            z.stats['strip_sched_' + z.fsm.pose] += 1
            if acc < 1. and z.rng.random() > acc:
                z.stats['strip_blocked_' + z.fsm.pose] += 1; return False
            z.stats['strip_ok_' + z.fsm.pose] += 1
        return o_strip(self, actor, target, witnessed)

    Match.step = step; Engine.engage = engage; Engine.tackle = tackle; Engine.strip = strip
    return st
