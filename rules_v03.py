"""RULES_FLOW v0.3 in the engine, behind RULES_V03=1 (default off).  Installed by pocket4_proto after the other patches.
Step 1 (this file): marking 5 m, flat scoring, minor/major discipline ladder, minor fouls change the tackle count, half-goal award.
  - Minor fouls: no exclusion for the 1st-3rd; the 4th is 60 s; the 5th is a disqualification.  Warnings are dropped (a warning becomes a minor).
  - Majors: only danger/serious (intentional head contact, intentional off-ball trip).  Engine reasons hold, deliberate delay, transition_foul become MINOR [P: unspecified in canon].
  - Defence minor: tackle count -1 (floor 0); at 0 the offence is awarded a half goal in periods 1-3, a full goal in period 4 / overtime, and keeps possession.
  - Offence minor: tackle count +1; the second is a turnover.  Offence keeps the ball after the first.
  - Offside, the Contact Scrimmage, substitutes for exclusions, archer limits: later steps.
"""
import os
FLAT = dict(inner_points=2, release_points=2, outside_points=2, carry_value=2)
def on(): return os.environ.get('RULES_V03', '0') == '1'
def settings(st):
    if not on(): return st
    st = dict(st)
    if os.environ.get('RV03_FLAT', '1') == '1': st.update(FLAT)
    if os.environ.get('RV03_MARK', '1') == '1': st['marking_distance'] = 5.0
    return st

def install(P):
    CO = P.CORE; Match = CO.engine.Engine; Phase = CO.types.Phase
    o_foul, o_disc = Match.foul, Match.discipline; stats = P.__dict__.setdefault('V03', {})   # Match here is the Engine class
    def count(k, n=1): stats[k] = stats.get(k, 0) + n
    def discipline(self, pid, kind, permanent=False):
        if not on(): return o_disc(self, pid, kind, permanent)
        p = self.s.players[pid]
        if kind == 'warning': kind = 'minor'
        if kind == 'major' and not getattr(self, '_v03_major', False) and not permanent: kind = 'minor'
        if kind == 'minor':
            n = p.minor_count + 1; count('minor_recorded')
            if n <= 3: p.minor_count = n; self.emit('minor_recorded', 'V03', player=pid, minors=n); return
            if n == 4: p.minor_count = 0; o_disc(self, pid, 'minor', permanent); p.minor_count = 4; count('minor_exclusion'); return
            p.minor_count = n; return o_disc(self, pid, 'dq', True)
        return o_disc(self, pid, kind, permanent)
    def foul_spot(self, off, spot, victim):
        s = self.s; sg = s.attack_sign(off); pts = [spot]
        if victim and victim in s.players: pts.append((s.players[victim].x, s.players[victim].y))
        return max(pts, key=lambda p: sg * p[0])                  # the spot of the ball or of the foul, whichever is closer to the goal attacked
    def to_scrim(self, off, fs):
        s = self.s
        if os.environ.get('RV03_SCRIM', '1') == '1' and s.restart is not None and s.restart.team == off and s.phase == Phase.DEAD:
            keepc = s.tackle_count; mk = Match.scrim_helpers[0]; mk(self, off, fs[0], fs[1], None, None, False, 'foul'); s.tackle_count = keepc
    def foul(self, actor, victim=None, reason='hold', major=False, danger=False, penalty=False, certain=False, carry=False, advantage=False, disqualify=False):
        if not on(): return o_foul(self, actor, victim, reason, major, danger, penalty, certain, carry, advantage, disqualify)
        s = self.s; a = s.players[actor]; self._v03_major = bool(danger or reason == 'serious_foul' or (major and reason in ('serious_foul',)))
        is_minor = not self._v03_major and not penalty and not certain and not disqualify
        try:
            if not (is_minor and s.phase == Phase.LIVE and s.owner in ('A', 'B') and s.penalty is None and not s.extension and s.advantage is None and s.recovery is None):
                return o_foul(self, actor, victim, reason, major, danger, penalty, certain, carry, advantage, disqualify)
            off = s.owner; spot = (s.ball.x, s.ball.y)
            if a.team != off:                                      # defence minor
                if s.tackle_count >= 1:
                    s.tackle_count -= 1; count('def_minor_count_cost'); self.emit('foul', '11;15', actor=actor, victim=victim, reason=reason, major=False, danger=False, penalty=False)
                    self.discipline(actor, 'minor'); keep = s.tackle_count
                    fs = foul_spot(self, off, spot, victim); keep_c = keep; self.award(off, *fs, 'foul', foul=True); s.tackle_count = keep_c; to_scrim(self, off, fs); return
                pts = 1 if s.period <= 3 else 2; s.score[off] += pts; count('half_goal' if pts == 1 else 'full_goal_award')
                self.emit('foul', '11;15', actor=actor, victim=victim, reason=reason, major=False, danger=False, penalty=False)
                self.emit('foul_award', 'V03', team=off, points=pts, reason=reason, period=s.period); self.discipline(actor, 'minor')
                fs = foul_spot(self, off, spot, victim); self.award(off, *fs, 'foul', foul=True); s.tackle_count = 0; to_scrim(self, off, fs); return
            # offence minor: count +1; the second is a turnover (the original path awards the other team)
            if s.tackle_count >= 1: count('off_minor_turnover'); return o_foul(self, actor, victim, reason, major, danger, penalty, certain, carry, advantage, disqualify)
            count('off_minor_count_cost'); self.emit('foul', '11;15', actor=actor, victim=victim, reason=reason, major=False, danger=False, penalty=False)
            fs = foul_spot(self, off, spot, victim); self.discipline(actor, 'minor'); self.award(off, *fs, 'foul', foul=True); s.tackle_count = 1; to_scrim(self, off, fs)
        finally: self._v03_major = False
    Match.foul = foul; Match.discipline = discipline
    # ---- step 2: always 12 on the field (a substitute covers every exclusion/DQ); forfeit only if fewer than 12 of 22 are available ----
    o_tg, o_no, o_fz = Match.terminal_ground, Match.new_owner, Match.freeze
    def terminal_ground(self, team, reason):
        if on() and reason == 'minimum_lineup':
            avail = sum(1 for p in self.s.players.values() if p.team == team and p.available and not p.injured and not p.disqualified)
            if avail >= 12: return
            reason = 'insufficient_players'
        return o_tg(self, team, reason)
    Match.terminal_ground = terminal_ground
    M = CO.match.Match; o_auto = M.auto_substitutions
    def auto_substitutions(self):
        o_auto(self)
        if not on(): return
        s = self.s
        if s.phase not in (Phase.LIVE, Phase.DEAD, Phase.AWARD, Phase.BREAK): return
        for team in ('A', 'B'):
            low = s.ends[team] == 0; gatex = 75 if low else 25
            while True:
                activefield = [p for p in s.players.values() if p.team == team and p.active and p.role == 'field']
                bench = [p for p in s.players.values() if p.team == team and not p.active and p.available and not p.injured and not p.disqualified and p.exclusion_ms <= 0]
                if len(activefield) >= 10 or not bench: break
                p = max(bench, key=lambda p: p.fatigue); p.role = 'field'; p.x = gatex; p.y = .1 if low else 99.9; p.active = True
                self.e.slot_fill(p); self.e.emit('slot_return', 'V03:always12', player=p.id); count('substitute_for_exclusion')
    M.auto_substitutions = auto_substitutions
    # ---- step 2: archers: 25 arrows and at most five freezes per possession ----
    ARROWS, FREEZES = 25, 5
    def new_owner(self, team, reason):
        changed = o_no(self, team, reason)
        if on() and changed:
            for q in self.s.quivers.values(): q.allocation = ARROWS; q.spent = 0; q.loaded = min(5, ARROWS)
            self._v03_freezes = {'A': 0, 'B': 0}; count('possessions_reset')
        return changed
    def freeze(self, pid, arrow=None, panel=True, direct=True, in_range=True):
        if not on(): return o_fz(self, pid, arrow, panel, direct, in_range)
        shooter = self.s.other(self.s.players[pid].team); fz = getattr(self, '_v03_freezes', None)
        if fz is None: fz = self._v03_freezes = {'A': 0, 'B': 0}
        if fz[shooter] >= FREEZES: self.emit('freeze_limit', 'V03', team=shooter, player=pid); count('freeze_blocked'); return False
        ok = o_fz(self, pid, arrow, panel, direct, in_range)
        if ok: fz[shooter] += 1; count('freezes')
        return ok
    Match.new_owner = new_owner; Match.freeze = freeze

    # ---- step 3: the Contact Scrimmage (RV03_SCRIM=0 switches this step off).  The scrimmage itself (snapper, tackler alignment, line of scrimmage, offside check,
    # dead-ball movement) is restarts_v1's; this layer feeds it the canon cases: scrimmage inside the Keeper Zone, the 10 m reset, the turnover restart, foul restarts,
    # the 10 s snap window, and the possession-clock rule.
    SCRIM = lambda: on() and os.environ.get('RV03_SCRIM', '1') == '1'
    WINDOW = 10000
    clampf = lambda v, lo, hi: max(lo, min(hi, v))
    o_tackle = Match.tackle
    def turnover_spot(self, team, bx, by):
        sg = self.s.attack_sign(team); own = 0. if sg > 0 else 100.; x40 = own + sg * 40.
        return (bx if sg * bx > sg * x40 else x40), by
    def make_scrimmage(self, team, x, y, snapper=None, tackler=None, reset10=False, cause=''):
        s = self.s; sg = s.attack_sign(team); gx = 100. if sg > 0 else 0.
        x, y = clampf(x, 1., 99.), clampf(y, 1., 99.)
        if reset10 and abs(gx - x) < 10.: x = gx - sg * 10.; count('reset_to_10m')
        s.recovery = None; s.reconstruction = None; s.restart = None; s.award_spot = None; s.award_deadline = None
        self.award(team, x, y, 'scrimmage', foul=False, normalize=False); r = s.restart
        if r is None or r.reason != 'scrimmage': return None
        heavy = bool(tackler and getattr(s.players[tackler].a, 'mass', 0.) >= 205.)
        r.kind = 'scrim'; r.clearance = .9; r.taker = None
        r.rs = dict(kind='scrim', snapper=snapper, tackler=tackler, nose=heavy, retakes=0, att=0, dfn=0)
        r.v03 = dict(clock=s.possession_ms > 10000, chain=0)
        count('scrimmage'); self.emit('scrimmage_set', 'V03', snapper=snapper, tackler=tackler, spot=[round(x, 2), round(y, 2)], count=s.tackle_count, cause=cause, clock_runs=r.v03['clock'])
        return r
    def scrim_penalty(self, kind, cause):
        """offence (missed snap window, offence offside): count +1 and the spot 5 m back; a second one is a turnover."""
        s = self.s; r = s.restart; team = r.team; sg = s.attack_sign(team); n = s.tackle_count + 1; rs = r.rs
        count('off_penalty_' + cause); self.emit('scrimmage_penalty', 'V03', team=team, kind=kind, cause=cause, count_to=n)
        if n >= 2:
            other = s.other(team); self.new_owner(other, 'scrimmage_penalty'); x, y = turnover_spot(self, other, r.x - sg * 5., r.y); s.restart = None
            return make_scrimmage(self, other, x, y, None, None, False, 'turnover_after_' + cause)
        s.tackle_count = n; x, y = clampf(r.x - sg * 5., 1., 99.), r.y
        nr = make_scrimmage(self, team, x, y, rs.get('snapper'), rs.get('tackler'), False, cause)
        return nr
    def tackle(self, actor, target, body='knee', witnessed=False):
        s = self.s
        if not SCRIM(): return o_tackle(self, actor, target, body, witnessed)
        own0, cnt0, bx, by = s.owner, s.tackle_count, s.ball.x, s.ball.y; a, t = s.players[actor], s.players[target]
        res = o_tackle(self, actor, target, body, witnessed)
        if not res or s.phase == Phase.PENALTY: return res
        if cnt0 == 0 and own0 == t.team and s.tackle_count == 1 and (s.recovery is not None or (s.restart is not None and s.restart.kind == 'inbound')):
            make_scrimmage(self, t.team, bx, by, target, actor, True, 'first_tackle')
        elif own0 == t.team and s.owner == a.team and s.tackle_count == 0 and s.phase == Phase.AWARD:
            x, y = turnover_spot(self, a.team, bx, by); s.restart = None; make_scrimmage(self, a.team, x, y, None, actor, False, 'second_tackle')
        return res
    Match.tackle = tackle; Match.scrim_helpers = (make_scrimmage, turnover_spot); _HOOK[0] = scrim_penalty
    M = CO.match.Match; o_step = M.step
    def step(self):
        s = self.s; t0 = s.now; r0 = s.restart
        o_step(self)
        if not SCRIM(): return
        r = s.restart
        if s.phase == Phase.DEAD and r is not None and r is r0 and r.kind == 'scrim' and getattr(r, 'v03', None) is not None:
            v = r.v03; dt = max(0, s.now - t0)
            if v['clock'] and s.owner == r.team: s.possession_ms = max(500, s.possession_ms - dt)       # [P] the clock runs in the window when more than 0:10 remained; floored at 0.5 s
            if s.now - r.created_at >= WINDOW and r.reason == 'scrimmage':
                count('missed_window'); self.e.emit('snap_window_missed', 'V03', waited_ms=s.now - r.created_at); scrim_penalty(self.e, 'offence', 'missed_window')
    M.step = step

def scrim_penalty_hook(engine, kind, cause):
    import sys
    P = sys.modules.get('pocket') or None
    return _HOOK[0](engine, kind, cause)
_HOOK = [None]

# ---- no kicking (RV03_NOKICK=1 by default when RULES_V03=1): the game is throwing and carrying only ----
def install_nokick(P):
    CO = P.CORE; M = CO.match.Match; o_pass, o_shot = M.make_pass, M.make_shot; stats = P.__dict__.setdefault('V03', {})
    on_ = lambda: on() and os.environ.get('RV03_NOKICK', '1') == '1'
    def make_pass(self, p, q, kind='pass', *a, **k):
        if on_() and kind == 'kick': kind = 'pass'; stats['kick_to_throw'] = stats.get('kick_to_throw', 0) + 1
        return o_pass(self, p, q, kind, *a, **k)
    def make_shot(self, p, execute=False):
        if not on_(): return o_shot(self, p, execute)
        k0 = p.a.kicking; p.a.kicking = p.a.passing        # a shot is a throw: the aim and the wind-up come from the thrower's passing skill
        try: return o_shot(self, p, execute)
        finally: p.a.kicking = k0
    M.make_pass = make_pass; M.make_shot = make_shot
