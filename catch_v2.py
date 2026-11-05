"""Catch model v2 (CATCH_V2=1).  One model for every athlete, Keepers included.
 - Strength of hands: the energy a catcher can arrest, capacity(x) = CAP_LO + (CAP_HI - CAP_LO) x^CAP_P, x = (catching - .4)/.6, times (1 - (miss/R)^2).
     CAP_HI = 2.5 x the ball's kinetic energy at the fastest pass a 100 Throw Power can make (V_POWER), so a 100 Catcher secures it (~100%) and a 40 Catcher never does.
     CAP_LO = 400 J (a 40 secures ~30 m/s passes reliably, none above ~45 m/s); CAP_P = 3.6 puts the League-average 70 at ~1.1 kJ (secure to ~60-70 m/s).  All [P].
 - P(secure) = 1 / (1 + (E/capacity)^8): a threshold with a short soft edge, not the old gentle (E/cap)^2 slope.
 - Reach: the hand sphere is 0.9 x reach for everyone (the Keeper's extra 10% is gone); a longer reach catches balls a shorter reach cannot (absolute metres).
 - Readiness (time to set the hands): tau = the athlete's PRISM Reaction latency x att_lat (he is tracking the ball), replacing catch_reaction_s x (1.3 - .6 awareness).
Height places the hands (hand_height = z + .62 height); Jump rating sets how far the feet leave the ground.  (Unchanged: engine airborne posture.)"""
import os, math, importlib
import throwing_v1 as T
import prism_archer_v0 as A
JUMP_OBS = int(os.environ.get('PRISM_JUMP_OBS', '8'))      # sightings a player wants before committing to a jump (vertical speed is noisy: ~1.2 m/s at 8 sightings)
PRISM_JUMP = os.environ.get('PRISM_JUMP', '1') == '1'     # the field jump decision reads the player's own belief about the ball (needs the PRISM eye)
HAND_CONTEST = os.environ.get('HAND_CONTEST', '1') == '1'
HC_WINDOW_MS = float(os.environ.get('HC_WINDOW_MS', '40')); HC_TIE = float(os.environ.get('HC_TIE', '.15')); HC_CAP = float(os.environ.get('HC_CAP', '2.0'))
HC_KR, HC_KM, HC_KS, HC_KT, HC_KC, HC_KP = 5.0, 0.7, 1.0, 3.3, 3.0, 5.0     # [P] pillar scales: a full spread of one pillar = about +-2 logits (88%)
CAP_LO = float(os.environ.get('CATCH_CAP_LO', '400')); CAP_P = float(os.environ.get('CATCH_CAP_P', '3.6')); CAP_K = float(os.environ.get('CATCH_K', '8')); CAP_HI_X = float(os.environ.get('CATCH_CAP_HI_X', '2.5'))
def install(CO, S):
    Match = CO.match.Match; ctau = {}
    def cap_hi(m): return CAP_HI_X * .5 * m * T.V_POWER ** 2
    def catch_capacity(self, skill, miss):
        x = max(0., min(1., (skill - .4) / .6)); hi = cap_hi(self.assume['ball_mass_kg'])
        return (CAP_LO + (hi - CAP_LO) * x ** CAP_P) * max(0., 1. - miss * miss)
    def catch_secure(self, energy, capacity):
        return 0. if capacity <= 1e-9 else 1. / (1. + (energy / capacity) ** CAP_K)
    def kp_tau(self, p, default):
        f = getattr(S, 'RT', None)
        if f is None: return default
        rt = f(p.id); key = (p.id, tuple(sorted(rt.items())))
        t = ctau.get(key)
        if t is None:
            pr = A.ArcherPrism('tau', .5, p.a.decision_speed, dict(vel_mode='lsq', win_s=.4)); pr.apply_ratings(rt); t = ctau[key] = pr.latency_s * pr.P['att_lat']
        return t
    o_move = Match.move_players
    def update_jumps(self):
        """Keepers keep the engine rule.  A field player leaves the ground for a free ball that will pass within his hand sphere but above his standing reach (and within what his Jump rating can add),
        timed so the apex of the jump meets the ball (windows of one engine step).  The decision still reads the true ball path: Perception of that is the next job."""
        s = self.s; b = s.ball; g = self.assume['gravity']
        if b.carrier is not None: return
        for p in self.active_field():
            if p.role == 'keeper' or not self.e.eligible(p) or p.posture != 'upright' or b.last_releaser == p.id or p.a.jump_height <= .05: continue
            bel = (getattr(S, 'ball_belief', None) or (lambda m, q, n=None: None))(self, p, JUMP_OBS) if PRISM_JUMP else (b.x, b.y, b.z, b.vx, b.vy, b.vz)
            if bel is None: continue
            bx, by, bz, bvx, bvy, bvz = bel
            rx, ry = bx - p.x, by - p.y; d0 = math.hypot(rx, ry)
            if d0 > 30. or d0 < .3: continue
            vh = math.hypot(bvx, bvy)
            if vh < 1.: continue
            vcl = -(rx * bvx + ry * bvy) / d0
            if vcl < 1.: continue
            tc = d0 / vcl; miss = abs(rx * bvy - ry * bvx) / vh; Rh = .9 * p.a.reach
            if miss > Rh: continue
            zp = bz + bvz * tc - .5 * g * tc * tc; stand = p.hand_height
            if zp <= stand + .65 * Rh or zp > stand + Rh + p.a.jump_height: continue
            vz = math.sqrt(2 * g * p.a.jump_height); L = zp - (stand + Rh)                    # lift his feet must give so the hand sphere reaches the ball's height when it arrives
            if L <= 0: L = 1e-3
            disc = vz * vz - 2 * g * L
            if disc < 0: continue
            t1, t2 = (vz - math.sqrt(disc)) / g, (vz + math.sqrt(disc)) / g                  # times after take-off in which his feet are at least L off the ground
            if t1 - .02 <= tc <= t2:
                p.vz = vz; p.posture = 'airborne'; self.stats['field_jumps'] = self.stats.get('field_jumps', 0) + 1
    def move_players(self, ms, targets):
        r = o_move(self, ms, targets); update_jumps(self); return r
    Match.move_players = move_players
    core = importlib.import_module(Match.__module__)
    def hc_logit(self, a, b):
        """Hand contest between two athletes whose hands are on the same ball: logit that `a` wins.  Four balanced pillars, each +-HC_CAP when its spread is full and the others are even:
        physical (reach, mass, strength), technical (Catching), resistance (Contact Resistance, Balance), perception (PRISM Reaction latency: who reads it first)."""
        phys = HC_KR * math.log(max(.5, a.a.reach) / max(.5, b.a.reach)) + HC_KM * math.log(a.a.mass / b.a.mass) + HC_KS * (a.a.strength - b.a.strength)
        tech = HC_KT * (a.a.catching - b.a.catching)
        res = HC_KC * ((a.a.contact_resistance + a.a.balance) / 2. - (b.a.contact_resistance + b.a.balance) / 2.)
        per = HC_KP * (kp_tau(self, b, .1) - kp_tau(self, a, .1))
        cap = lambda v: max(-HC_CAP, min(HC_CAP, v))
        return cap(phys) + cap(tech) + cap(res) + cap(per)
    def hc_acquire(self, cands, at, f, near, p, ms, point):
        ev = lambda g, q: core.Event('acquire', q.id, data={'ball_point': point(g), 'c1_contact': True, **({'c4c_kind': 'catch'} if self.c4c and q.role == 'keeper' else {})}, at=int(g * ms))
        base = [ev(g, q) for g, w, _, q, good, _ in cands if good and int(g * ms) == at and (q is p or g != f or abs(w - near) < 1e-9)]
        if not HAND_CONTEST: return base
        grp = [c for c in cands if c[4] and (c[0] - f) * ms <= HC_WINDOW_MS]
        if len(grp) < 2 or len({c[3].team for c in grp}) < 2: return base
        # contest among the secure hands within the window: a tournament by pairwise hand contest, the leader meets each challenger of the other team in order of contact
        lead = grp[0]; self.stats['hand_contests'] = self.stats.get('hand_contests', 0) + 1
        for ch in grp[1:]:
            if ch[3].team == lead[3].team: continue
            z = hc_logit(self, lead[3], ch[3])
            if abs(z) < HC_TIE: self.stats['hand_ties'] = self.stats.get('hand_ties', 0) + 1; return [ev(lead[0], lead[3]), ev(ch[0], ch[3])] if False else [ev(max(lead[0], ch[0]), lead[3]), ev(max(lead[0], ch[0]), ch[3])]
            if self.rng['ball'].random() >= 1. / (1. + math.exp(-z)): lead = ch
        self.stats['hand_win_' + ('lead' if lead is grp[0] else 'chal')] = self.stats.get('hand_win_' + ('lead' if lead is grp[0] else 'chal'), 0) + 1
        return [ev(lead[0], lead[3])]
    Match.hc_acquire = hc_acquire; Match.hc_logit = hc_logit
    Match.catch_capacity = catch_capacity; Match.catch_secure = catch_secure; Match.catch_tau = kp_tau
