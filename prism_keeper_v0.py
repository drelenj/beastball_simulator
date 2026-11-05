"""PRISM v0.5 - KEEPERS perceive the free ball through the same PRISM parts a field player uses (flag PRISM_KEEPER=1).
What changes: the C4c Keeper no longer reads the TRUE ball state at the instant it changed course.  Instead
  - his gaze slews toward the ball at his Focus slew rate (prism_archer gaze model), so a fast ball can leave the fovea;
  - every SAMPLE_MS the ball is an observation only if it is inside his cone (half-angle and reach from Vision), not hidden behind another body (line of sight),
    and passes the cone detection probability (Clarity); position noise is PRISM's noise_sigma (range, off-axis, Awareness, Clarity);
  - an observation is delivered after his latency (Reaction), halved for the entity he is locked on (att_lat) as for any PRISM athlete tracking a target;
  - his belief is a short least-squares fit (position + velocity, vertical with gravity) of the last delivered observations taken after the course change, carried forward to now;
  - he may not plan until MIN_OBS observations have been delivered: the read time is latency + (MIN_OBS-1) x SAMPLE_MS, not a fixed constant.
Unchanged (still omniscient, listed so nothing is hidden): the trigger that a new course exists (engine ball version), positioning against the true ball and carrier, wind-up and confront triggers, the catch model.
Ratings: S.RT(pid) (same table as field players) or PRISM_KEEPER_RATINGS json override.  All numbers [P] provisional."""
import math, os, json, types
from collections import Counter
import prism_archer_v0 as A
import prism_perception_v012 as PP
from prism_reference import cone_probability

SAMPLE_MS = int(os.environ.get('KP_SAMPLE_MS', '20')); MIN_OBS = int(os.environ.get('KP_MINOBS', '5')); FIT_N = int(os.environ.get('KP_FITN', '8'))
ANT = os.environ.get('KP_ANT', '1') == '1'; INS = os.environ.get('KP_INS', '1') == '1'; JUD = os.environ.get('KP_JUD', '1') == '1'
PRIOR_DEG = float(os.environ.get('KP_PRIOR_DEG', '10'))     # [P] angular spread of shots about the line to the goal centre (the Anticipation prior)
KJ_NOISE = float(os.environ.get('KP_JNOISE', '3.0'))        # [P] Judgment: plan-point selection noise (m) at Judgment 0, as the field-player defenders use
KEEPER_EYE = os.environ.get('PRISM_KEEPER', '0') == '1'      # Keepers track the ball (and the carrier) through PRISM
CATCHERS = os.environ.get('PRISM_CATCHERS', '1') == '1'      # field players near a free ball track it through the same eye (for jumping and, next, catching)
CATCH_RANGE = float(os.environ.get('PRISM_CATCH_RANGE', '35'))
KR = json.loads(os.environ.get('PRISM_KEEPER_RATINGS', '{}'))

def install(CO, S, seed_fn):
    Match = CO.match.Match; o_step = Match.step
    S.kprism = {}; S.kstats = Counter(); S.kprev = None
    def RT(pid):
        f = getattr(S, 'RT', None)
        rt = dict(KR) if KR else f(pid) if f else ((getattr(S, 'prism_r', None) or {}).get(pid) or {k: .7 for k in PP.RATINGS})
        m = getattr(S, 'm', None)
        if os.environ.get('PRISM_JSPLIT', '0') == '1' and m is not None and pid in m.s.players and m.s.players[pid].role == 'keeper' and 'goalkeeping' in rt: rt = dict(rt, judgment=rt['goalkeeping'])   # a Keeper's judgement is Goalkeeping
        return rt
    def get(p):
        k = S.kprism.get(p.id)
        if k is None:
            pr = A.ArcherPrism(f'{seed_fn()}-K-{p.id}', .5, p.a.decision_speed, dict(vel_mode='lsq', win_s=.4)); pr.apply_ratings(RT(p.id)); pr.latency_s *= float(os.environ.get('KP_LATX', '1')); pr.noise_mult *= float(os.environ.get('KP_NOISEX', '1'))
            k = S.kprism[p.id] = dict(pr=pr, obs=[], car=[], trk=[], miss=0, pend=[], course_n=0, course_used=0, course_t=0, next=0, last_tick=None)
        return k
    def prop(st, tau, g, dragc, r):
        x, y, z, vx, vy, vz = st; step_ = .005; drag = math.exp(-dragc * step_); t = 0.
        while t < tau - 1e-9:
            h = min(step_, tau - t); x += vx * h; y += vy * h; z += vz * h - .5 * g * h * h; vx *= drag; vy *= drag; vz = (vz - g * h) * drag; t += h
            if z <= r: z = r; vz = max(vz, 0.)
        return x, y, z, vx, vy, vz
    def back(st, tau, g, dragc, r):
        x, y, z, vx, vy, vz = st; step_ = .005; drag = math.exp(-dragc * step_); t = 0.
        while t < tau - 1e-9:
            h = min(step_, tau - t); d = drag if h == step_ else math.exp(-dragc * h); vx /= d; vy /= d; vz = vz / d + g * h; x -= vx * h; y -= vy * h; z -= vz * h - .5 * g * h * h; t += h
        return x, y, z, vx, vy, vz
    def detect(self, k, o, sig):
        """The Keeper notices a new course himself: a first sighting, a gap in sight, or two sightings in a row that the last course cannot explain (a deflection)."""
        tr = k['trk']
        if not tr or o[0] - tr[-1][0] > 250: k['course_n'] += 1; k['course_t'] = o[0]; k['trk'] = [o]; k['miss'] = 0; k['pend'] = []; return
        if len(tr) >= 3:
            e = estimate(self, tr[-6:]); dt = (o[0] - e[0]) / 1000.; g = self.assume['gravity']
            px, py, pz = e[1] + e[4] * dt, e[2] + e[5] * dt, e[3] + e[6] * dt - .5 * g * dt * dt
            if math.sqrt((o[2] - px) ** 2 + (o[3] - py) ** 2 + (o[4] - pz) ** 2) > 6. * sig + .4:
                k['miss'] += 1; k['pend'].append(o)
                if k['miss'] >= 2: k['course_n'] += 1; k['course_t'] = k['pend'][0][0]; k['trk'] = list(k['pend']); k['miss'] = 0; k['pend'] = []
                return
        k['miss'] = 0; k['pend'] = []; tr.append(o)
        if len(tr) > 12: del tr[:4]
    def estimate(self, ob):
        """Least-squares ball state from observations ob = [(t_capture, t_deliver, x, y, z)]: (t0, x, y, z, vx, vy, vz) at the last capture time (vertical with gravity)."""
        n = len(ob); t0 = ob[-1][0]; g = self.assume['gravity']; ts = [(o[0] - t0) / 1000. for o in ob]
        def lin(ys):
            tm = sum(ts) / n; ym = sum(ys) / n; den = sum((t - tm) ** 2 for t in ts) or 1e-9; v = sum((t - tm) * (y - ym) for t, y in zip(ts, ys)) / den; return ym - v * tm, v
        x0, vx = lin([o[2] for o in ob]); y0, vy = lin([o[3] for o in ob]); z0, vz = lin([o[4] + .5 * g * t * t for o, t in zip(ob, ts)])
        return t0, x0, y0, z0, vx, vy, vz
    def tracked(self, p):
        if p.role == 'keeper': return KEEPER_EYE and p.active
        if not CATCHERS or p.role != 'field' or not p.active: return False
        b = self.s.ball
        return b.carrier is None and ((b.vx * b.vx + b.vy * b.vy) > 4. or (os.environ.get('PRISM_OFFACT', '0') == '1' and b.mode.value == 'loose' and b.z < 1.5)) and math.hypot(b.x - p.x, b.y - p.y) < CATCH_RANGE and p.posture != 'grounded'
    def lat_ms(k): return 1000. * k['pr'].latency_s * k['pr'].P['att_lat']
    def step(self):
        if getattr(S, 'kowner', None) is not self.s: S.kowner = self.s; S.kprism.clear(); S.kprev = None   # a new match: forget the last one's observations, gaze and timers (before the engine's first step of it)
        r = o_step(self); s = self.s; now = s.now
        b = s.ball; cur = (b.x, b.y, b.z, b.vx, b.vy, b.vz); ver = getattr(b, 'version', None)
        pv = S.kprev; S.kprev = (now, cur, ver)
        if os.environ.get('KP_DBG') and now < 1400: print('CALL now', now, 'carrier', b.carrier, 'mode', b.mode, 'release_time', getattr(b, 'release_time', None), 'ball', [round(v, 1) for v in cur[:3]])
        tc = max([t for t in (getattr(b, 'release_time', None), getattr(b, 'course_time', None)) if t is not None] or [-1e18])
        # ball state at a sample time inside (prev step, now]: the free flight run backward from the current state, but never before the last course change
        def ball_at(t):
            if b.carrier is None and tc <= t < now: return back(cur, (now - t) / 1000., self.assume['gravity'], self.assume['ball_drag'], b.radius)
            return cur
        for p in s.players.values():
            if not tracked(self, p): continue
            k = get(p)
            lo = pv[0] if pv is not None else now
            if b.carrier is None and tc <= now and (pv is None or pv[0] < tc): lo = tc - 1      # the course began inside the interval the last call did not see: sample it from its start
            if k['next'] <= lo: k['next'] = lo + 1
            if b.carrier is None and k['next'] < tc <= now: k['next'] = int(tc) + 1
            while k['next'] <= now:
                ts = min(k['next'], now); k['next'] += SAMPLE_MS
                bx, by, bz = ball_at(ts)[:3]; pr = k['pr']; P = pr.P
                eye = (p.x, p.y, .72 * p.a.height); face = math.atan2(p.vy, p.vx) if math.hypot(p.vx, p.vy) > 1. else (p.facing if isinstance(p.facing, (int, float)) else (0. if s.attack_sign(p.team) < 0 else math.pi))
                pr.tick(ts / 1000., eye, face, [], (bx, by), None)           # gaze slews toward the ball; no body observations here
                if b.carrier is not None and p.role != 'keeper': continue
                if b.carrier is not None:                                       # a carried ball is the carrier's business: he is perceived as a body, and his visible preparation (a wind-up) is a cue
                    c = s.players.get(b.carrier)
                    if c is not None and c.team != p.team:
                        ex_, ey_ = c.x - eye[0], c.y - eye[1]; ez_ = .55 * c.a.height - eye[2]; cr = math.sqrt(ex_ * ex_ + ey_ * ey_ + ez_ * ez_)
                        co = math.degrees(abs((math.atan2(ey_, ex_) - pr.gaze_az + math.pi) % (2 * math.pi) - math.pi))
                        if co <= P['fov_half_deg'] and cr <= pr.prof['cone_reach_m'] and A.line_of_sight(eye, c.x, c.y, .55 * c.a.height, [dict(id=q.id, x=q.x, y=q.y, z=q.z, h=q.a.height, r=q.radius) for q in s.players.values() if q.active and q.role != 'archer' and q.id not in (p.id, c.id)], None) \
                           and (co <= P['fovea_half_deg'] or pr.rng.random() <= cone_probability(co, (P['fov_half_deg'] - 60) / 60., pr.clarity, P['fovea_half_deg'])):
                            sg = pr.noise_sigma(cr, co / P['fov_half_deg']); k['car'].append((ts, ts + lat_ms(k), c.x + pr.rng.gauss(0, sg), c.y + pr.rng.gauss(0, sg), c.id)); S.kstats['car_obs'] += 1
                            if len(k['car']) > 40: del k['car'][:20]
                            pa = self.pending_ball_actions.get(b.carrier)
                            if pa is not None and pa[1] == 'shot':
                                if k.get('cue') is None or k['cue'][0] != c.id or ts - k['cue'][2] > 1500: k['cue'] = (c.id, ts, ts); S.kstats['cue_seen'] += 1   # (carrier, first captured, last captured)
                                else: k['cue'] = (c.id, k['cue'][1], ts)
                    continue
                if os.environ.get('KP_DBG') and p.id == 'B10' and ts < 1400: print('SAMPLE', ts, 'now', now, 'tc', tc, 'ball', round(bx,1), round(by,1), round(bz,1), 'gaze', round(math.degrees(pr.gaze_az),1))
                dx, dy, dz = bx - eye[0], by - eye[1], bz - eye[2]; rng_m = math.sqrt(dx * dx + dy * dy + dz * dz)
                off_deg = math.degrees(abs((math.atan2(dy, dx) - pr.gaze_az + math.pi) % (2 * math.pi) - math.pi))
                if off_deg > P['fov_half_deg'] or rng_m > pr.prof['cone_reach_m']: S.kstats['out_of_view'] += 1; continue
                bodies = [dict(id=q.id, x=q.x, y=q.y, z=q.z, h=q.a.height, r=q.radius) for q in s.players.values() if q.active and q.role != 'archer' and q.id != p.id]
                if not A.line_of_sight(eye, bx, by, bz, bodies, None): S.kstats['occluded'] += 1; continue
                if off_deg > P['fovea_half_deg'] and pr.rng.random() > cone_probability(off_deg, (P['fov_half_deg'] - 60) / 60., pr.clarity, P['fovea_half_deg']): S.kstats['missed'] += 1; continue
                sig = pr.noise_sigma(rng_m, off_deg / P['fov_half_deg']); g = pr.rng.gauss
                o_ = (ts, ts + lat_ms(k), bx + g(0, sig), by + g(0, sig), bz + g(0, sig)); k['obs'].append(o_); S.kstats['obs'] += 1; detect(self, k, o_, sig)
                if len(k['obs']) > 60: del k['obs'][:20]
        return r
    def delivered(self, p, seen):
        k = S.kprism.get(p.id)
        return [] if k is None else [o for o in k['obs'] if o[1] <= self.s.now and o[0] >= seen[1]][-FIT_N:]
    def kp_react(self, p, A_, sp, default, t_obs=None):
        k = get(p); pr = k['pr']; lat = lat_ms(k); t0 = t_obs if t_obs is not None else self.s.now
        ready = t0 + lat + MIN_OBS * SAMPLE_MS                                  # enough sightings of the ball to fit its course
        classified = False
        if INS:                                                                 # Instinct: a visible wind-up, once classified as a shot (classify_delay_s after he first sees it), lets him set before the release
            cue = k.get('cue'); cl = pr.prof['classify_delay_s'] * 1000.
            classified = cue is not None and t0 - cue[2] <= 600 and cue[1] + lat + cl <= t0; S.kstats['classified' if classified else 'unclassified'] += 1
        if JUD:                                                                 # Judgment: he decides on a cycle (decision_interval_s from his first sighting), not the instant he is ready
            ivl = pr.prof['decision_interval_s'] * 1000.; first = t0 + lat
            if ivl > 1: ready = first + math.ceil(max(0., ready - first) / ivl) * ivl
        return ready - t0 + (A_['keeper_unset_s'] * 1000. if sp > A_['keeper_set_mps'] and not classified else 0.)
    def kp_noticed(self, p, b, seen):
        k = S.kprism.get(p.id); return k is not None and k['course_n'] > k['course_used']
    def kp_aware(self, p):
        k = S.kprism.get(p.id); return getattr(p, 'c4c_seen', None) is not None or (k is not None and k['course_n'] > k['course_used'])
    def kp_tobs(self, p, default):
        k = S.kprism.get(p.id)
        if k is None: return default
        k['course_used'] = k['course_n']; return k['course_t']
    def kp_cross(self, p, cross):
        if cross is None or not JUD: return cross
        k = get(p); J = k['pr'].prof['options_considered']; Jr = RT(p.id).get('judgment', .7); i, t, y, z = cross
        sd = KJ_NOISE * (1. - Jr); rg = k['pr'].rng
        return (i, t, y + rg.gauss(0, sd), max(0., z + rg.gauss(0, sd)))
    def kp_wake(self, p, seen):
        k = S.kprism.get(p.id); s_ = self.s
        if k is None: return seen[2]
        ob = sorted(o for o in k['obs'] if o[0] >= seen[1])
        if len(ob) >= MIN_OBS: w = sorted(o[1] for o in ob)[MIN_OBS - 1]
        else: w = s_.now + (MIN_OBS - len(ob)) * SAMPLE_MS + lat_ms(k)
        return max(seen[2], w, s_.now + 1)
    def kp_ready(self, p, b, seen):
        ok = len(delivered(self, p, seen)) >= MIN_OBS
        if not ok: S.kstats['not_ready'] += 1
        return ok
    def kp_ball(self, p, b, seen):
        ob = delivered(self, p, seen); S.kstats['reads'] += 1
        if len(ob) < 2: return b
        n = len(ob); g = self.assume['gravity']; t0, x0, y0, z0, vx, vy, vz = estimate(self, ob)
        if ANT and p.role == 'keeper' and (pr_ := S.kprism[p.id]['pr']).intent_w > 0:               # Anticipation: Bayesian pull of the velocity toward 'a shot at the goal centre', as strong as the measurement is poor
            gx = self.s.ends[p.team]; sp3 = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.; ux, uy, uz = gx - x0, 50. - y0, 1.5 - z0; un = math.sqrt(ux * ux + uy * uy + uz * uz) or 1.
            rng_m = math.sqrt((x0 - p.x) ** 2 + (y0 - p.y) ** 2); sv = pr_.noise_sigma(rng_m, 0.) * math.sqrt(12. / (n * (n * n - 1.))) / (SAMPLE_MS / 1000.) if n >= 3 else sp3
            sm = math.degrees(sv / sp3) if sp3 > 1 else 90.; w = (pr_.intent_w / .7) * sm * sm / (sm * sm + PRIOR_DEG ** 2)
            vx, vy, vz = (1 - w) * vx + w * sp3 * ux / un, (1 - w) * vy + w * sp3 * uy / un, (1 - w) * vz + w * sp3 * uz / un; S.kstats['prior_w_sum'] += w
        x, y, z, vx, vy, vz = prop((x0, y0, max(b.radius, z0), vx, vy, vz), (self.s.now - t0) / 1000., g, self.assume['ball_drag'], b.radius)
        return types.SimpleNamespace(x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, radius=b.radius)
    def belief_xy(obs, now, tau_max=1500):
        d = [o for o in obs if o[1] <= now]
        if not d: return None
        last = d[-1]
        if now - last[0] > tau_max: return None
        win = [o for o in d if last[0] - o[0] <= 400][-6:]
        if len(win) >= 2:
            n = len(win); ts = [(o[0] - last[0]) / 1000. for o in win]; tm = sum(ts) / n; den = sum((t - tm) ** 2 for t in ts) or 1e-9
            def lin(ys): ym = sum(ys) / n; v = sum((t - tm) * (y - ym) for t, y in zip(ts, ys)) / den; return ym - v * tm, v
            x0, vx = lin([o[2] for o in win]); y0, vy = lin([o[3] for o in win])
        else: x0, y0, vx, vy = last[2], last[3], 0., 0.
        a = min((now - last[0]) / 1000., 1.0); return x0 + vx * a, y0 + vy * a, vx, vy
    o_pos = Match.c4c_position
    def c4c_position(self, p):
        """Positioning from what he perceives: the carrier / loose ball at their believed place and velocity, and a wind-up only once he has classified it."""
        s = self.s; b = s.ball; k = S.kprism.get(p.id); c = s.players.get(b.carrier) if b.carrier else None
        if k is None or (c is not None and c.team == p.team): return o_pos(self, p)
        now = s.now; saved = []; pend = None
        if c is not None:
            bel = belief_xy([o for o in k['car'] if o[4] == c.id], now)
            if bel is None:
                lastk = [o for o in k['car'] if o[4] == c.id]
                bel = (lastk[-1][2], lastk[-1][3], 0., 0.) if lastk else (50., 50., 0., 0.); S.kstats['car_stale'] += 1
            saved.append((c, c.x, c.y, c.vx, c.vy)); c.x, c.y, c.vx, c.vy = bel
            pa = self.pending_ball_actions.get(c.id); cue = k.get('cue')
            if pa is not None and INS:
                cl = k['pr'].prof['classify_delay_s'] * 1000.
                if not (cue is not None and cue[0] == c.id and now >= cue[1] + lat_ms(k) + cl): pend = (c.id, self.pending_ball_actions.pop(c.id))
            elif pa is not None and not (cue is not None and cue[0] == c.id and now >= cue[1] + lat_ms(k)): pend = (c.id, self.pending_ball_actions.pop(c.id))
            bel_ball = bel
        else:
            bel_ball = belief_xy(k['obs'], now)
            if bel_ball is None: bel_ball = (b.x, b.y, 0., 0.) if not k['obs'] else (k['obs'][-1][2], k['obs'][-1][3], 0., 0.); S.kstats['ball_stale'] += 1
        saved.append((b, b.x, b.y, b.vx, b.vy)); b.x, b.y, b.vx, b.vy = bel_ball
        try: return o_pos(self, p)
        finally:
            for q, x, y, vx, vy in saved: q.x, q.y, q.vx, q.vy = x, y, vx, vy
            if pend is not None: self.pending_ball_actions[pend[0]] = pend[1]
    Match.c4c_position = c4c_position
    def ball_belief(self, p, min_obs=None):
        """The free ball as player p believes it now (x, y, z, vx, vy, vz), or None until he has MIN_OBS delivered sightings of this course."""
        k = S.kprism.get(p.id)
        if k is None or k['course_n'] == 0: return None
        seen = (None, k['course_t'])
        if len(delivered(self, p, seen)) < (min_obs or MIN_OBS): return None
        bb = kp_ball(self, p, self.s.ball, seen)
        return None if not hasattr(bb, 'vz') else (bb.x, bb.y, bb.z, bb.vx, bb.vy, bb.vz)
    S.ball_belief = ball_belief
    Match.step = step; Match.kp_react = kp_react; Match.kp_ready = kp_ready; Match.kp_wake = kp_wake; Match.kp_ball = kp_ball; Match.kp_cross = kp_cross; Match.kp_noticed = kp_noticed; Match.kp_aware = kp_aware; Match.kp_tobs = kp_tobs
