"""PRISM v0 - Archer, SHADOW MODE.  Perception + Information only.  Decisions are NOT changed: the engine's archer still decides from true state.
The shadow archer builds its own belief state from what it could sense and we log how wrong it is, and what its aim would have been.

PROVISIONAL PARAMETERS (marked P): every number below is a placeholder to make the stage testable, none is canon.  Ratings are the only per-athlete knobs:
  awareness (a.awareness), decision_speed (a.decision_speed).  Geometry comes from the platform (eye height) and body sizes.
"""
import math, random
from prism_reference import cone_probability
from prism_perception_v012 import Tracker2, perception_profile
from prism_reference import radar_probability
from collections import Counter

PARAMS = dict(
    tick_ms=100,            # P  perception update rate (10 Hz)
    fov_half_deg=100.,      # P  usable half field of view (~200 deg total)
    fovea_half_deg=15.,     # P  half-angle of full-fidelity attention cone
    slew_dps=120.,          # P  gaze slew rate, deg/s, scaled by (.6 + .4 awareness)
    periph_detect=(.35, .40),   # P  per-tick detection prob outside fovea = a + b*awareness
    noise_base_m=.01, noise_per_m=.0025,    # P  position noise sigma = (base + per_m*range) * (1 + 2*offaxis) * (1.3 - .6*awareness)
    vel_alpha=.4,           # P  velocity filter gain on finite differences (mode 'diff')
    vel_mode='lsq', ab_a=.5, ab_b=.15, win_s=.4, acc_cap=15., lat_scale=1.,   # P  velocity estimator: 'diff' | 'ab' (alpha-beta filter) | 'lsq' (windowed linear regression)
    memory_s=2.0,           # P  belief usable-confidence time constant, x(.7+.6*awareness)
    att_lat=.5,             # P  ATTENTION: observation latency multiplier for the entity the archer is locked on (drawing on / tracking)
    hold_p=0.,              # P  INFERENCE: do not release unless estimated hit probability >= this (0 = always fire)
    pred_ref_s=.3,          # P  horizon at which the predictor's own track error is measured
    sig_prior_m=3.,         # P  track error assumed for a player not yet tracked for long
    torso=.55, head=.95,    # fractions of body height used for line-of-sight tests
)

def unit3(dx, dy, dz):
    n = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
    return dx / n, dy / n, dz / n

def seg_dist2d(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy
    f = 0. if L < 1e-12 else max(0., min(1., ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + f * dx), py - (ay + f * dy)), f

def line_of_sight(eye, tx, ty, tz, bodies, skip):
    """True if the eye can see point (tx,ty,tz): no other body's cylinder (radius r, z..z+h) crosses the sight line."""
    for b in bodies:
        if b['id'] == skip: continue
        d, f = seg_dist2d(b['x'], b['y'], eye[0], eye[1], tx, ty)
        if d < b['r']:
            z = eye[2] + (tz - eye[2]) * f
            if b['z'] <= z <= b['z'] + b['h']: return False
    return True

from prism_comms_v0 import CommsMixin

class Belief:
    __slots__ = ('x', 'y', 'vx', 'vy', 't', 'n', 'h', 'ax', 'ay', 'snap', 'sig')
    def __init__(self, x, y, t): self.x, self.y, self.vx, self.vy, self.t, self.n, self.h, self.ax, self.ay, self.snap, self.sig = x, y, 0., 0., t, 1, [(t, x, y)], 0., 0., [], None
    def at(self, now_s):
        a = max(0., now_s - self.t); a2 = .5 * a * a; return self.x + self.vx * a + self.ax * a2, self.y + self.vy * a + self.ay * a2
    def vel_at(self, now_s):
        a = min(.6, max(0., now_s - self.t)); return self.vx + self.ax * a, self.vy + self.ay * a

class ArcherPrism(CommsMixin):
    """One archer's perception + belief store.  Pure: no engine imports, deterministic given its rng."""
    def __init__(self, seed, awareness, decision_speed, params=None):
        self.P = dict(PARAMS, **(params or {})); self.aw = awareness; self.ds = decision_speed
        self.rng = random.Random(seed); self.noise_mult = 1.; self.last_dec = -9.; self.intent_w = 0.; self.goal = None; self.prof = None; self.clarity = SOFT_CLARITY; self.rng_t = random.Random(str(seed) + '-trk'); self.trk = None; self.trk_last = {}; self.ident = {}; self.bel = {}; self.queue = []; self.gaze_az = None; self.last_tick = None
        self._comms_init(); self.stats = Counter(); self.latency_s = self.P['lat_scale'] * decision_speed * (1.3 - .4 * awareness)
    def noise_sigma(self, rng_m, offaxis):
        P = self.P; return (P['noise_base_m'] + P['noise_per_m'] * rng_m) * (1 + 2 * offaxis) * (1.3 - .6 * self.aw) * self.noise_mult
    def visible(self, eye, b, bodies):
        P = self.P
        for f in (P['torso'], P['head']):
            if line_of_sight(eye, b['x'], b['y'], b['z'] + f * b['h'], bodies, b['id']): return True
        return False
    def tick(self, now_s, eye, facing_az, bodies, focus_xy, attend=None):
        """Advance perception to time now_s.  bodies: dicts with id,x,y,z,h,r.  Returns ids detected this tick."""
        P = self.P; dt = 0. if self.last_tick is None else now_s - self.last_tick; self.last_tick = now_s
        # gaze slews toward the believed focus (ball/carrier), limited by slew rate
        if focus_xy is not None:
            want = math.atan2(focus_xy[1] - eye[1], focus_xy[0] - eye[0])
        else: want = facing_az
        if self.gaze_az is None: self.gaze_az = want
        else:
            d = (want - self.gaze_az + math.pi) % (2 * math.pi) - math.pi; lim = math.radians(P['slew_dps']) * (.6 + .4 * self.aw) * dt
            self.gaze_az += max(-lim, min(lim, d))
        seen = []; tobs = []; tpend = []
        for b in bodies:
            dx, dy = b['x'] - eye[0], b['y'] - eye[1]; dz = b['z'] + P['torso'] * b['h'] - eye[2]; rng_m = math.sqrt(dx * dx + dy * dy + dz * dz)
            az = math.atan2(dy, dx); off = abs((az - self.gaze_az + math.pi) % (2 * math.pi) - math.pi); off_deg = math.degrees(off)
            if off_deg > P['fov_half_deg'] or (self.prof and rng_m > self.prof['cone_reach_m']): self.stats['out_of_fov'] += 1; continue
            if not self.visible(eye, b, bodies): self.stats['occluded'] += 1; continue
            if off_deg <= P['fovea_half_deg']: p = 1.
            elif SOFT: p = cone_probability(off_deg, (P['fov_half_deg'] - 60) / 60., self.clarity, P['fovea_half_deg'])   # v0.1.2 reference cone (Codex)
            else: p = P['periph_detect'][0] + P['periph_detect'][1] * self.aw
            if self.rng.random() > p: self.stats['missed_detection'] += 1; continue
            sig = self.noise_sigma(rng_m, off_deg / P['fov_half_deg'])
            ox, oy = b['x'] + self.rng.gauss(0, sig), b['y'] + self.rng.gauss(0, sig); lat = now_s + self.latency_s * (self.P['att_lat'] if b['id'] == attend else 1.)
            if TRACKID: tpend.append((lat, b['id'], ox, oy, off_deg <= P['fovea_half_deg']))
            else: self.queue.append((lat, b['id'], ox, oy, now_s))
            seen.append(b['id']); self.stats['detections'] += 1
            if TRACK: tobs.append((b['id'], b['x'] + self.rng_t.gauss(0, sig), b['y'] + self.rng_t.gauss(0, sig)))
        if self.prof: self.radar(now_s, eye, bodies, set(seen))
        if TRACKID and tpend:
            if self.trk is None: self.trk = Tracker2(max_age=TRACK_MAX_AGE)
            res = self.trk.update([(x, y, 'cone') for _, _, x, y, _ in tpend], now_s)
            for (lat, pid, x, y, fov), tr in zip(tpend, res):
                if tr.n == 1 or (REIDENT and fov): self.ident[tr.tid] = pid                 # identity from first sighting (cone classification), carried by track continuity
                self.queue.append((lat, tr.tid, x, y, now_s))
                if self.ident.get(tr.tid) != pid: self.stats['trk_wrong_ident'] += 1
        if TRACK and not TRACKID and tobs: self.track_diag(now_s, tobs)
        self.deliver(now_s)
        return seen
    def track_diag(self, now_s, tobs):
        """DIAGNOSTIC ONLY (PRISM_TRACK=1): feed anonymous observations to Tracker2 and score identity purity against truth.  Never feeds decisions."""
        if self.trk is None: self.trk = Tracker2(); self.trk_last = {}
        res = self.trk.update([(x, y, 'cone') for _, x, y in tobs], now_s)
        for (pid, _, _), tr in zip(tobs, res):
            self.stats['trk_obs'] += 1
            if tr.n == 1: self.stats['trk_new'] += 1
            else:
                prev = self.trk_last.get(tr.tid); self.stats['trk_cont'] += 1
                if prev is not None and prev != pid: self.stats['trk_swap'] += 1
                if tr.ambiguous: self.stats['trk_ambig'] += 1; self.stats['trk_ambig_swap'] += (prev is not None and prev != pid)
            self.trk_last[tr.tid] = pid
    def apply_ratings(self, r):
        """v0.1.2 eight-rating profile -> this Archer's perception.  Only the wired ratings act (vision, awareness, clarity, reaction, focus);
        instinct, anticipation, judgment have no Archer hook yet.  Neutral = all .5."""
        pf = perception_profile(r); self.prof = pf; self.aw = .5; P = self.P
        P['fov_half_deg'] = pf['cone_half_angle_deg']; P['slew_dps'] = pf['gaze_slew_dps'] / (.6 + .4 * .5); P['memory_s'] = pf['belief_tau_s'] / (.7 + .6 * .5)
        self.latency_s = P['lat_scale'] * pf['delay_s']; self.noise_mult = pf['cone_noise_scale'] / (1.6 - 1.2 * .5); self.intent_w = pf['intent_blend']; self.clarity = r.get('clarity', .5); self.next_pulse = 0.
    def radar(self, now_s, eye, bodies, seen_ids):
        pf = self.prof
        if now_s < self.next_pulse: return
        self.next_pulse = now_s + pf['radar_pulse_period_s']; R = pf['radar_radius_m']
        for b in bodies:
            d = math.hypot(b['x'] - eye[0], b['y'] - eye[1])
            if d > R or b['id'] in seen_ids: continue
            sp = math.hypot(b.get('vx', 0.), b.get('vy', 0.))
            if self.rng.random() > radar_probability(d, R, sp, 0 if self.visible(eye, b, bodies) else 1, 0): continue
            sg = (.5 + .1 * d) * (pf['radar_bearing_sigma_deg'] / 17.5)
            self.queue.append((now_s + self.latency_s + pf['radar_extra_delay_s'], b['id'], b['x'] + self.rng.gauss(0, sg), b['y'] + self.rng.gauss(0, sg), now_s)); self.stats['radar_blips'] += 1
    def intent_vel(self, b, now):
        """ANTICIPATION (v0.1.4): blend the observed velocity toward an intent prior -- opponents head for the goal they attack -- weighted by how consistent their observed heading already is with that intent.
        Weight = intent_w (= 0.7 x Anticipation) x consistency (1 at perfect alignment, 0 at >= 70 deg).  intent_w = 0 leaves the plain estimate untouched."""
        vx, vy = b.vel_at(now)
        if self.intent_w <= 0 or self.goal is None: return vx, vy
        sp = math.hypot(vx, vy)
        if sp < 1.: return vx, vy
        bx, by = b.at(now); dx, dy = self.goal[0] - bx, self.goal[1] - by; dn = math.hypot(dx, dy)
        if dn < 1.: return vx, vy
        ang = math.acos(max(-1., min(1., (vx * dx + vy * dy) / (sp * dn)))); w = self.intent_w * max(0., 1. - ang / math.radians(INTENT_MAX_DEG))
        return (1 - w) * vx + w * sp * dx / dn, (1 - w) * vy + w * sp * dy / dn
    def key(self, pid):
        """Belief key for a player.  Default: the true id.  TRACKID mode: the freshest anonymous track whose identity was established (at first sighting) as this player."""
        if not TRACKID: return pid
        best = None; bt = -1.
        for tid, who in self.ident.items():
            if who == pid:
                b = self.bel.get(tid)
                if b is not None and b.t > bt: best, bt = tid, b.t
        return best
    def bget(self, pid): return self.bel.get(self.key(pid))
    def ambiguous(self, pid):
        k = self.key(pid); tr = self.trk.tracks.get(k) if (TRACKID and self.trk and k is not None) else None
        return bool(tr and tr.ambiguous)
    def deliver(self, now_s):
        P = self.P
        keep = []
        for t_av, pid, x, y, t_obs in self.queue:
            if t_av <= now_s:
                b = self.bel.get(pid)
                if b is None: self.bel[pid] = Belief(x, y, t_obs)
                else:
                    if t_obs > b.t: self.update(b, x, y, t_obs)
            else: keep.append((t_av, pid, x, y, t_obs))
        self.queue = keep
    def update(self, b, x, y, t_obs):
        P = self.P; gap = t_obs - b.t; mode = P['vel_mode']
        if gap > 1.0: b.h = []                                   # stale: restart the estimate
        b.h.append((t_obs, x, y)); b.h = [o for o in b.h if t_obs - o[0] <= max(1.5, P['win_s'])]
        if mode == 'diff':
            if gap > 1.0: b.vx = b.vy = 0.
            else:
                a = P['vel_alpha']; b.vx, b.vy = (1 - a) * b.vx + a * (x - b.x) / gap, (1 - a) * b.vy + a * (y - b.y) / gap
            b.x, b.y = x, y
        elif mode == 'ab':
            if gap > 1.0: b.x, b.y, b.vx, b.vy = x, y, 0., 0.
            else:
                px, py = b.x + b.vx * gap, b.y + b.vy * gap; rx, ry = x - px, y - py
                b.x, b.y = px + P['ab_a'] * rx, py + P['ab_a'] * ry; b.vx += P['ab_b'] * rx / gap; b.vy += P['ab_b'] * ry / gap
        elif mode == 'quad':
            pts = [o for o in b.h if t_obs - o[0] <= P['win_s']]
            if len(pts) >= 4:
                import itertools
                tt = [o[0] - t_obs for o in pts]
                def fit(vals):
                    # normal equations for c0 + c1 t + c2 t^2
                    S = [sum(t ** k for t in tt) for k in range(5)]; R = [sum((t ** k) * v for t, v in zip(tt, vals)) for k in range(3)]
                    M = [[S[0], S[1], S[2], R[0]], [S[1], S[2], S[3], R[1]], [S[2], S[3], S[4], R[2]]]
                    for i in range(3):
                        piv = max(range(i, 3), key=lambda r: abs(M[r][i]))
                        if abs(M[piv][i]) < 1e-12: return None
                        M[i], M[piv] = M[piv], M[i]
                        for r in range(3):
                            if r != i:
                                f = M[r][i] / M[i][i]; M[r] = [a - f * c for a, c in zip(M[r], M[i])]
                    return [M[i][3] / M[i][i] for i in range(3)]
                fx, fy = fit([o[1] for o in pts]), fit([o[2] for o in pts])
                if fx and fy:
                    cap = P['acc_cap']; b.x, b.y, b.vx, b.vy = fx[0], fy[0], fx[1], fy[1]; b.ax = max(-cap, min(cap, 2 * fx[2])); b.ay = max(-cap, min(cap, 2 * fy[2]))
                else: b.x, b.y = x, y
            else:
                if gap <= 1.0 and len(pts) >= 2: a = P['vel_alpha']; b.vx, b.vy = (1 - a) * b.vx + a * (x - b.x) / gap, (1 - a) * b.vy + a * (y - b.y) / gap
                b.x, b.y = x, y
        else:   # lsq over the window
            pts = [o for o in b.h if t_obs - o[0] <= P['win_s']]
            if len(pts) >= 3:
                tm = sum(o[0] for o in pts) / len(pts); sxx = sum((o[0] - tm) ** 2 for o in pts)
                if sxx > 1e-9:
                    b.vx = sum((o[0] - tm) * o[1] for o in pts) / sxx; b.vy = sum((o[0] - tm) * o[2] for o in pts) / sxx
                    mx = sum(o[1] for o in pts) / len(pts); my = sum(o[2] for o in pts) / len(pts); b.x, b.y = mx + b.vx * (t_obs - tm), my + b.vy * (t_obs - tm)
                else: b.x, b.y = x, y
            else:
                if len(pts) >= 2 and gap <= 1.0:
                    a = P['vel_alpha']; b.vx, b.vy = (1 - a) * b.vx + a * (x - b.x) / gap, (1 - a) * b.vy + a * (y - b.y) / gap
                b.x, b.y = x, y
        b.t = t_obs; b.n += 1
        # INFERENCE: self-assessed predictability. Compare where the track says the player is now with where the track predicted, pred_ref_s ago.
        ref = P['pred_ref_s']; b.snap.append((t_obs, b.x, b.y, b.vx, b.vy)); b.snap = [o for o in b.snap if t_obs - o[0] <= 1.2]
        for o in b.snap:
            if abs((t_obs - ref) - o[0]) <= .06:
                dt = t_obs - o[0]; e = math.hypot(b.x - (o[1] + o[3] * dt), b.y - (o[2] + o[4] * dt)); b.sig = e if b.sig is None else .85 * b.sig + .15 * e; break
    def p_hit(self, pid, now_s, flight_s, rng_m, radius=.43):
        """Estimated probability the arrow lands within the body: Rayleigh with sigma = sqrt(sensor^2 + (track error x (horizon/ref)^2)^2); horizon = age of belief + flight."""
        b = self.bel.get(self.key(pid))
        if b is None: return 0.
        P = self.P; h = max(0., now_s - b.t) + flight_s; s300 = b.sig if b.sig is not None else P['sig_prior_m']
        so = (P['noise_base_m'] + P['noise_per_m'] * rng_m) * (1.3 - .6 * self.aw)
        sg = math.sqrt(so * so + (s300 * (h / P['pred_ref_s']) ** 2) ** 2); r = radius + .045
        return 1. - math.exp(-r * r / (2 * sg * sg))
    def at_bounded(self, b, now_s):
        """Position estimate that does not run away on a stale belief: velocity decays with a time constant (extrap_tau_s) and the acceleration term stops growing after .6 s.
        Belief.at() extrapolates without limit, so a belief kept alive by a long memory drifts far from the truth."""
        a = max(0., now_s - b.t); tau = self.P.get('extrap_tau_s', 1.2); ae = min(a, .6); k = tau * (1. - math.exp(-a / tau))
        return b.x + b.vx * k + .5 * b.ax * ae * ae, b.y + b.vy * k + .5 * b.ay * ae * ae
    def confidence(self, pid, now_s):
        b = self.bel.get(self.key(pid))
        if b is None: return 0.
        return math.exp(-(now_s - b.t) / (self.P['memory_s'] * (.7 + .6 * self.aw)))

VARIANTS = {'diff': dict(vel_mode='diff'), 'lsq_.4': dict(vel_mode='lsq', win_s=.4),
            'lsq_.4_noise_only': dict(vel_mode='lsq', win_s=.4, lat_scale=0.), 'lsq_.4_lag_only': dict(vel_mode='lsq', win_s=.4, noise_base_m=0., noise_per_m=0.),
            'lsq_.4_nonoise_nolag': dict(vel_mode='lsq', win_s=.4, noise_base_m=0., noise_per_m=0., lat_scale=0.)}

import os
DRIVE = os.environ.get('PRISM_DRIVE', '0') == '1'     # archer decides from its belief state instead of true state
RANGE_MARGIN = float(os.environ.get('PRISM_RANGE_MARGIN', '5' if DRIVE else '0')); RMAX = float(os.environ.get('ARCH_RMAX', '70'))
SOFT = os.environ.get('PRISM_SOFT', '0') == '1'; SOFT_CLARITY = float(os.environ.get('PRISM_CLARITY', '.5')); TRACK = os.environ.get('PRISM_TRACK', '0') == '1'
RATINGS = __import__('json').loads(os.environ.get('PRISM_RATINGS', 'null'))
JUDGE = os.environ.get('PRISM_JUDGE', '0') == '1'; JONLY = os.environ.get('PRISM_JONLY'); JONLY = set(JONLY.split(',')) if JONLY else None
INTENT_MAX_DEG = float(os.environ.get('PRISM_INTENT_DEG', '70'))
REIDENT = os.environ.get('PRISM_REIDENT', '1') == '1'; TRACKID = os.environ.get('PRISM_TRACKID', '0') == '1'; AMBIG = os.environ.get('PRISM_AMBIG', 'keep'); TRACK_MAX_AGE = float(os.environ.get('PRISM_TRK_AGE', '4'))
LITE = DRIVE or os.environ.get('PRISM_LITE', '0') == '1'

def install(CO, S, seed_fn, Counter=Counter):
    """Hook into the proto: perception tick every tick_ms of sim time per archer; log belief error at arrow releases and at 1 s samples."""
    Match, Engine = CO.match.Match, CO.engine.Engine; geo = CO.geometry
    S.veto = {}; S.prism = {}; S.prism_var = {}; S.prism_log = dict(release=[], sample=[]); S.prism_stats = Counter(); S.prism_pending = []
    o_step = Match.step; o_sa = Engine.shoot_arrow
    def setup(self):
        for tm in 'AB':
            a = next((p for p in self.s.players.values() if p.team == tm and p.role == 'archer'), None)
            if a is not None and tm not in S.prism:
                aw = float(__import__('os').environ.get('PRISM_AWARE', a.a.awareness))
                vs = {'lsq_.4': dict(VARIANTS['lsq_.4'], hold_p=float(os.environ.get('PRISM_HOLD', '0')), lat_scale=float(os.environ.get('PRISM_LAT', '1')))} if LITE else VARIANTS
                S.prism_var[tm] = {n: ArcherPrism(f'{seed_fn()}-{tm}', aw, a.a.decision_speed, v) for n, v in vs.items()}
                if RATINGS is not None:
                    for v_ in S.prism_var[tm].values(): v_.apply_ratings(RATINGS); v_.goal = (0. if a.x < 50 else 100., 50.)
                S.prism[tm] = (a.id, S.prism_var[tm]['lsq_.4'])
    def bodies_of(self):
        return [dict(id=p.id, x=p.x, y=p.y, z=p.z, h=p.a.height, r=p.radius, team=p.team, vx=p.vx, vy=p.vy) for p in self.s.players.values() if p.active and p.role != 'archer']
    def eye_of(self, a): return (a.x, a.y, .72 * a.a.height)
    def step(self):
        r = o_step(self); s = self.s
        if not S.prism: setup(self)
        now_ms = s.now
        for tm, (aid, pr) in S.prism.items():
            a = s.players[aid]
            if not a.active: continue
            if pr.last_tick is not None and now_ms / 1000. - pr.last_tick < PARAMS['tick_ms'] / 1000.: continue
            eye = eye_of(self, a); face = 0. if s.ends[tm] == 0 else math.pi
            bodies = bodies_of(self)
            ball = s.ball; carrier = s.players.get(ball.carrier); fx = (carrier.x, carrier.y) if carrier is not None else (ball.x, ball.y)
            bel_focus = pr.bget(carrier.id).at(now_ms / 1000.) if carrier is not None and pr.bget(carrier.id) is not None else None
            focus = bel_focus if bel_focus else fx if carrier is None else None
            pd = getattr(self, 'pending_draw', {}).get(tm)
            attend = pd[1] if pd else (carrier.id if carrier is not None else None)      # attention: the player being drawn on, else the ball carrier
            if pd and pr.bget(pd[1]) is not None: focus = pr.bget(pd[1]).at(now_ms / 1000.)
            for v in S.prism_var[tm].values(): v.tick(now_ms / 1000., eye, face, bodies, focus, attend)
        # due aim checks
        keep = []
        for it in S.prism_pending:
            if s.now >= it['due']:
                t = s.players[it['target']]; d = math.hypot(t.x - it['aim'][0], t.y - it['aim'][1]); it['rec'][it['key']] = round(d, 3); it['rec'][it['key'] + '_hit'] = d < t.radius + .045
            else: keep.append(it)
        S.prism_pending = keep
        # 1 s samples
        if now_ms // 1000 != getattr(S, '_prism_last_s', -1):
            S._prism_last_s = now_ms // 1000
            for tm, (aid, pr) in S.prism.items():
                a = s.players[aid]
                if not a.active: continue
                eye = eye_of(self, a); bodies = bodies_of(self); opp = [b for b in bodies if b['team'] != tm]
                inr = [b for b in opp if 10 <= math.dist(eye, (b['x'], b['y'], .55 * 2.5)) <= 70]
                vis = [b for b in inr if pr.visible(eye, b, bodies)]
                known = [b for b in inr if pr.confidence(b['id'], now_ms / 1000.) > .5]
                errs = [math.hypot(pr.bget(b['id']).at(now_ms / 1000.)[0] - b['x'], pr.bget(b['id']).at(now_ms / 1000.)[1] - b['y']) for b in known]
                per = {}
                for n, v in S.prism_var[tm].items():
                    pe, ve = [], []
                    for b in inr:
                        if v.confidence(b['id'], now_ms / 1000.) > .5:
                            bl = v.bget(b['id']); bx, by = bl.at(now_ms / 1000.); bvx, bvy = bl.vel_at(now_ms / 1000.); pe.append(math.hypot(bx - b['x'], by - b['y'])); ve.append(math.hypot(bvx - b['vx'], bvy - b['vy']))
                    per[n] = (sum(pe) / len(pe) if pe else None, sum(ve) / len(ve) if ve else None)
                S.prism_log['sample'].append(dict(t=now_ms // 1000, team=tm, in_range=len(inr), visible=len(vis), known=len(known), mean_err=(sum(errs) / len(errs) if errs else None), per=per))
        return r
    def shoot_arrow(self, pid, target, velocity, origin=None):
        if DRIVE and target != 'ball' and S.prism and origin is not None:
            tm = pid[0]; pr = S.prism[tm][1]; t = self.s.players[target]; hp = pr.P['hold_p']
            spd = math.sqrt(sum(v * v for v in velocity)); d = math.dist(origin, (t.x, t.y, .55 * t.a.height))
            ph = pr.p_hit(target, self.s.now / 1000., d / max(spd, 1.) * 1.05, d, t.radius)
            if hp > 0:
                S.prism_stats['p_hit_n'] += 1; S.prism_stats['p_hit_sum'] += ph
                if ph < hp: S.prism_stats['held'] += 1; S.veto[tm] = True; return None
                S.prism_stats['released'] += 1
            S.phit_last = ph
        ar = o_sa(self, pid, target, velocity, origin)
        if DRIVE and ar and target != 'ball' and S.prism: S.prism_log.setdefault('phit', []).append((ar.id, getattr(S, 'phit_last', None), target))
        if ar and target != 'ball' and S.prism:
            tm = pid[0]; _, pr = S.prism[tm]; s = self.s; t = s.players[target]; now = s.now / 1000.
            a = s.players[pid]; eye = origin; bodies = bodies_of(self)
            b = pr.bget(target); known = b is not None
            rec = dict(arrow=ar.id, team=tm, target=target, range=round(math.dist(eye, (t.x, t.y, .55 * t.a.height)), 1), visible=pr.visible(eye, next(x for x in bodies if x['id'] == target), bodies), v={})
            speed = math.sqrt(sum(v * v for v in velocity)); g, k = 9.81, .06
            def lead(x0, y0, vx, vy):
                T = geo.ballistic(eye, (x0, y0, .55 * t.a.height), speed, g, False)
                if not T: return None
                T = T[1]
                for _ in range(6):
                    tx, ty = x0 + vx * T, y0 + vy * T; dh = math.hypot(tx - eye[0], ty - eye[1]); sol = geo.ballistic(eye, (tx, ty, .55 * t.a.height), speed, g, False)
                    if not sol: return None
                    vxl, vyl, vzl = sol[0]; x = y = 0.; z = eye[2]; tt = 0.; dec = math.exp(-k * .01)
                    while tt < 6:
                        x += vxl * .01; y += vyl * .01; z += vzl * .01 - .5 * g * .0001; vxl *= dec; vyl *= dec; vzl = (vzl - g * .01) * dec; tt += .01
                        if math.hypot(x, y) >= dh: break
                    T = tt
                return (x0 + vx * T, y0 + vy * T, T)
            lo = lead(t.x, t.y, t.vx, t.vy)
            if lo: S.prism_pending.append(dict(due=s.now + int(lo[2] * 1000), target=target, aim=lo, rec=rec, key='miss_omni'))
            for name, vpr in S.prism_var[tm].items():
                b = vpr.bget(target)
                if b is None: rec['v'][name] = None; continue
                bx, by = b.at(now); bvx, bvy = vpr.intent_vel(b, now); r = dict(age_s=round(now - b.t, 3), pos_err=round(math.hypot(bx - t.x, by - t.y), 3), vel_err=round(math.hypot(bvx - t.vx, bvy - t.vy), 3)); rec['v'][name] = r
                lb = lead(bx, by, bvx, bvy)
                if lb and lo:
                    r['aim_divergence'] = round(math.hypot(lb[0] - lo[0], lb[1] - lo[1]), 3); S.prism_pending.append(dict(due=s.now + int(lb[2] * 1000), target=target, aim=lb, rec=r, key='miss_belief'))
            rec['known'] = rec['v'].get('lsq_.4') is not None
            S.prism_log['release'].append(rec)
        return ar
    CONF_MIN = .3
    def ad_hook(self, tm):
        """Swap every non-archer player's position/velocity for the archer's belief (and hide players it does not know), for the duration of one arrow_decisions call.
        Freeze/immunity/eligibility stay true: they are public information (DreLen, 30 Oct)."""
        if tm not in S.prism: return None
        a_ = self.s.players[S.prism[tm][0]]; eye_ = (a_.x, a_.y, .72 * a_.a.height)
        s = self.s; now = s.now / 1000.; pr = S.prism[tm][1]; saved = []; hidden = []; bel_pred = {}; lad = self.last_arrow_decision[tm]; S.veto[tm] = False
        for p in s.players.values():
            if p.role == 'archer' or not p.active: continue
            b = pr.bel.get(pr.key(p.id))
            if b is None or pr.confidence(p.id, now) < CONF_MIN or (AMBIG == 'hide' and pr.ambiguous(p.id)): hidden.append(p); p.active = False; S.prism_stats['hidden_%s' % tm] += 1; continue
            bx, by = b.at(now); bvx, bvy = pr.intent_vel(b, now)
            if RANGE_MARGIN > 0 and p.team != tm and math.dist(eye_, (bx, by, .55 * p.a.height)) > RMAX - RANGE_MARGIN: hidden.append(p); p.active = False; S.prism_stats['range_margin_hidden'] += 1; continue   # STRATEGY: keep a safety margin inside the legal range
            saved.append((p, p.x, p.y, p.vx, p.vy)); p.x, p.y, p.vx, p.vy = bx, by, bvx, bvy; bel_pred[p.id] = (bx, by, bvx, bvy)
        if JUDGE and pr.prof and pr.goal is not None:
            pf = pr.prof; k = int(pf['options_considered']); L = pf['lookahead_s']; ivl = pf['decision_interval_s']
            if JONLY is not None: k = k if 'k' in JONLY else 99; L = L if 'L' in JONLY else 0.; ivl = ivl if 'i' in JONLY else 0.     # ablation: keep only the named components
            if now - pr.last_dec < ivl:                                   # JUDGMENT: slower deliberation -> decide less often; between decisions the Archer holds
                S.veto[tm] = True; S.prism_stats['judge_skip'] += 1
                for p, *_ in saved: hidden.append(p); p.active = False
                saved_ids = set()
            else:
                pr.last_dec = now; cid = s.ball.carrier; opts = []
                for p, *_ in saved:
                    if p.team == tm: continue
                    bx, by, bvx, bvy = bel_pred[p.id]; dist_g = math.hypot(bx + bvx * L - pr.goal[0], by + bvy * L - pr.goal[1])   # JUDGMENT: threat judged L seconds ahead
                    opts.append((-1. if p.id == cid else dist_g, p))
                opts.sort(key=lambda o: o[0])
                for _, p in opts[k:]: hidden.append(p); p.active = False; S.prism_stats['judge_dropped'] += 1
        def undo():
            for p, x, y, vx, vy in saved: p.x, p.y, p.vx, p.vy = x, y, vx, vy
            for p in hidden: p.active = True
            if S.veto.get(tm): self.last_arrow_decision[tm] = lad; S.veto[tm] = False     # held fire: no cost, the archer keeps waiting for a better shot
        return undo
    if DRIVE: S.ad_hook = ad_hook
    else: S.ad_hook = None
    Match.step = step; Engine.shoot_arrow = shoot_arrow
