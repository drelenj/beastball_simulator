"""Off-ball hand fighting v0 (HAND_FIGHT=1; needs CATCH_V2 for the pillar logit).  Two opposing field athletes, neither the carrier, both upright and live, whose hands can reach each other
(the engine's own contact range, .7 x (reach_a + reach_b) between surfaces), are in a hand fight.  Nothing here picks a winner by itself; the contest is physical:
 - the same four balanced pillars as the ball hand contest (catch_v2.hc_logit): reach/mass/strength, technical (Blocking here), contact resistance + balance, PRISM perception (who reads the other first).
   z = logit that A is ahead; s = tanh(z/2) in (-1, 1) is how far ahead.  Exact ties (|z| < HC_TIE) are a locked grip: no net force.
 - the leader puts a net hand force F = HF_FG x (leader's weight) x |s| on the other along the line between them: impulse J = F dt, the loser's velocity changes by J/m_loser away from the leader
   and the leader's by -HF_REACT J/m_leader (action and reaction, Newton), both recorded as velocity imposed by another athlete (c3_push) so the engine's legality witness sees it.
 - the same impulse loads the loser's balance exactly as a collision does (shock = dv / (shock_speed x (.5 + balance)) x HF_SHOCK), so a hard push by a strong athlete against a weak-balance one can ground him.
 - lawful in front, foul from behind: if one athlete is inside the other's rear cone (the engine's blindside rule) and is the one closing on him (>= HF_CLOSE m/s), that is a 'blindside' foul by the closer, once per pair per HF_COOL_MS.
 - a pair separates when the push or the athletes' own movement takes them out of reach, so a defender who wins a fight sheds the blocker simply by being pushed clear of him; no outcome is scripted.
Contact band (DreLen, 4 Nov): a hand may be on another athlete only below the neck and above the hip (shoulders and arms included); pushing and stabbing are legal, pulling and gripping are not.
 - where the hand lands: aim = middle of the target's legal band (.66 x his height); it lands with a spread .12 x his height x (1.4 - Blocking) (technique), arms adjusting freely to the height difference. Landing above .82 or below .5 of his height is a
   band foul ('high_contact' / 'low_contact', minor), judged once when a pair first engages, on the athlete who was closing on the other.
 - pull / grip: a fighter who is clearly losing (s <= -HF_GRIP_S) may grab to hold on. Hazard per second = HF_GRIP_RATE x |s| x (1 - (Blocking + Judgment)/2).  A grab is a 'holding' foul (seen with probability HF_DETECT) and the grip cancels
   HF_GRIP_FRAC of the leader's net force on him for HF_GRIP_MS: the foul is the price of holding on.
Stats on the match: hf_pairs (new engagements), hf_steps, hf_fouls, hf_lead_off / hf_lead_def (which side led), hf_ties, hf_falls.
Knobs [P]: HF_FG (fraction of the leader's own weight at full lead, default .5); HF_FOUL_GAP (m, hands must actually be on the back: surface gap, default .3); HF_REACT (.6), HF_SHOCK (1.0), HF_CLOSE (.5), HF_COOL_MS (2000).  Limitation [P]: every hand-reach pair fights, whether or not either athlete 'decided' to; a later version can make engaging a decision on beliefs."""
import os, math, random, zlib
import catch_v2 as C2
HAND_FIGHT = os.environ.get('HAND_FIGHT', '0') == '1'
HF_FG = float(os.environ.get('HF_FG', '.5')); HF_REACT = float(os.environ.get('HF_REACT', '.6')); HF_SHOCK = float(os.environ.get('HF_SHOCK', '1.0'))
HF_BAND_LO, HF_BAND_HI, HF_AIM, HF_SPREAD = .5, .82, .66, .12
HF_GRIP_S = float(os.environ.get('HF_GRIP_S', '.5')); HF_GRIP_RATE = float(os.environ.get('HF_GRIP_RATE', '.4')); HF_GRIP_FRAC = float(os.environ.get('HF_GRIP_FRAC', '.6')); HF_GRIP_MS = float(os.environ.get('HF_GRIP_MS', '1000')); HF_DETECT = float(os.environ.get('HF_DETECT', '.7'))
HF_CLOSE = float(os.environ.get('HF_CLOSE', '.5')); HF_COOL_MS = float(os.environ.get('HF_COOL_MS', '2000')); HF_FOUL_GAP = float(os.environ.get('HF_FOUL_GAP', '.3')); HC_TIE = float(os.environ.get('HC_TIE', '.15'))
def install(CO, S):
    import importlib
    Match = CO.match.Match; core = importlib.import_module(Match.__module__); Phase = core.Phase; Event = core.Event
    o_move = Match.move_players
    def fight_logit(self, a, b):
        """as the ball hand contest (catch_v2.hc_logit) but the technical pillar is Blocking, not Catching"""
        cap = lambda v: max(-C2.HC_CAP, min(C2.HC_CAP, v))
        phys = C2.HC_KR * math.log(max(.5, a.a.reach) / max(.5, b.a.reach)) + C2.HC_KM * math.log(a.a.mass / b.a.mass) + C2.HC_KS * (a.a.strength - b.a.strength)
        tech = C2.HC_KT * (a.a.blocking - b.a.blocking)
        res = C2.HC_KC * ((a.a.contact_resistance + a.a.balance) / 2. - (b.a.contact_resistance + b.a.balance) / 2.)
        per = C2.HC_KP * (self.catch_tau(b, .1) - self.catch_tau(a, .1))
        return cap(phys) + cap(tech) + cap(res) + cap(per)
    def rng(pid, qid, now_ms, tag): return random.Random(zlib.crc32(('%s|%s|%s|%s|%s' % (getattr(S, 'seed', 1), pid, qid, int(now_ms // 100), tag)).encode()))
    def st(self, k, v=1): self.stats[k] = self.stats.get(k, 0) + v
    def PRISM_J(self, p):
        import prism_ratings_v0 as _PR
        rt = S.RT(p.id) if getattr(S, 'RT', None) else _PR.NEUTRAL
        return _PR.rj(rt, 'defender_duel' if p.team != self.s.owner else 'judgment')
    def band_foul(self, p, q, now):
        """where p's hand lands on q: True if outside q's legal band (shoulders to hip)"""
        r = rng(p.id, q.id, now, 'band'); zc = (HF_AIM + HF_SPREAD * (1.4 - p.a.blocking) * r.gauss(0., 1.))   # fraction of q's height
        return 'high_contact' if zc > HF_BAND_HI else ('low_contact' if zc < HF_BAND_LO else None)
    def foul(self, p, q, why, detect=1.):
        if detect < 1. and rng(p.id, q.id, self.s.now, 'det' + why).random() >= detect: st(self, 'hf_unseen_' + why); return
        st(self, 'hf_fouls'); st(self, 'hf_foul_' + why)
        self.c3_events.append(Event('foul', p.id, q.id, {'reason': why, 'major': False, 'danger': False}, at=max(0, int(getattr(self, 'c3_adv', 100)) - 1)))
    def fight(self):
        s = self.s
        if getattr(self, '_hf_s', None) is not s: self._hf_s = s; self._hf_eng = set(); self._hf_cool = {}; self._hf_grip = {}
        if s.phase != Phase.LIVE or not hasattr(self, 'hc_logit'): self._hf_eng = set(); return
        ps = [p for p in self.active_field() if p.role == 'field' and self.e.eligible(p) and p.posture == 'upright' and p.id != s.ball.carrier]
        dt = max(1, getattr(self, 'c3_adv', 100)) / 1000.; now = s.now; seen = set(); owner = s.owner
        for i, a in enumerate(ps):
            for b in ps[i + 1:]:
                if a.team == b.team: continue
                oka, wa = self.e.contact_legal(a, b, 'block'); okb, wb = self.e.contact_legal(b, a, 'block')
                if wa not in ('legal', 'blindside') or wb not in ('legal', 'blindside') or (wa == 'blindside' and wb == 'blindside'): continue
                key = (a.id, b.id); seen.add(key); dx, dy = b.x - a.x, b.y - a.y; d = math.hypot(dx, dy) or 1e-6; ex, ey = dx / d, dy / d
                if key not in self._hf_eng:
                    st(self, 'hf_pairs')
                    for p, q, why, (ux, uy) in ((a, b, wa, (ex, ey)), (b, a, wb, (-ex, -ey))):
                        closing = p.vx * ux + p.vy * uy >= HF_CLOSE
                        if why == 'blindside' and d - a.radius - b.radius <= HF_FOUL_GAP and closing and now >= self._hf_cool.get((p.id, q.id), 0):
                            self._hf_cool[(p.id, q.id)] = now + HF_COOL_MS; foul(self, p, q, 'blindside')
                        elif why == 'legal' and closing:
                            bf = band_foul(self, p, q, now)
                            if bf and now >= self._hf_cool.get((p.id, q.id), 0): self._hf_cool[(p.id, q.id)] = now + HF_COOL_MS; foul(self, p, q, bf)
                st(self, 'hf_steps'); z = fight_logit(self, a, b)
                if abs(z) < HC_TIE: st(self, 'hf_ties'); continue
                lead, lose, sgn = (a, b, 1.) if z > 0 else (b, a, -1.)
                st(self, 'hf_lead_' + ('off' if lead.team == owner else 'def'))
                sv = abs(math.tanh(z / 2.)); gripped = now < self._hf_grip.get((lose.id, lead.id), 0)
                if sv >= HF_GRIP_S and not gripped:        # the loser may grab to hold on: legal pushing is all he is allowed, so this is the price
                    role_j = PRISM_J(self, lose)
                    if rng(lose.id, lead.id, now, 'grip').random() < HF_GRIP_RATE * sv * (1. - (lose.a.blocking + role_j) / 2.) * dt:
                        self._hf_grip[(lose.id, lead.id)] = now + HF_GRIP_MS; gripped = True; foul(self, lose, lead, 'holding', HF_DETECT); st(self, 'hf_grips')
                F = HF_FG * lead.a.mass * self.assume.get('gravity', 9.81) * sv * ((1. - HF_GRIP_FRAC) if gripped else 1.)
                J = F * dt
                ux, uy = (ex * sgn, ey * sgn)                       # from the leader toward the loser
                dvl = J / lose.a.mass; dvw = HF_REACT * J / lead.a.mass
                lose.vx += ux * dvl; lose.vy += uy * dvl; lead.vx -= ux * dvw; lead.vy -= uy * dvw
                if hasattr(self, 'c3_push'):
                    self.c3_push(lose, ux * dvl, uy * dvl, lead.id, now); self.c3_push(lead, -ux * dvw, -uy * dvw, lose.id, now)
                if hasattr(self, 'c3_add'):
                    A = self.assume; shock = HF_SHOCK * dvl / (A.get('shock_speed_mps', 3.) * (.5 + lose.a.balance))
                    self.c3_add(lose, ('hand', lead.id), shock, True, now)
        self._hf_eng = seen
    def move_players(self, ms, targets):
        r = o_move(self, ms, targets); fight(self); return r
    Match.move_players = move_players
