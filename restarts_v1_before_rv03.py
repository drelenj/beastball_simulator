"""Restarts v1 for the Pocket 4.0 prototype  (proposed working rules, see RESTARTS_NOTES.md)

  First Hunt        every quarter: 10 m circle, contestants 1.5 m from the ball, ball live when it exits the circle, 6 s limit then repeat
  Scrimmage restart after the first legal tackle: ball at the tackle spot, tackled player snaps, tackler 'nose' (1.2 m) or upright 5 m back,
                    LOS through the ball, offside: offence +1 tackle count (2 = turnover), defence resets the count to 0
  40-m Scrimmage Snap after a score: conceding team snaps from the centre of its own 40 m line, both teams behind their own 40 m line,
                    snap must go to another player, fresh possession (count 0, 45 s)
  Toss-in           ball over a boundary: other team of the last touch, thrower outside at the crossing point, 3 m clearance, 4 s, no self
                    recovery, no direct score (the engine already enforces the last two); archers cannot act in a dead ball

Archers cannot draw or fire until the ball has left the circle (Hunt rule).
Switch: system 'restarts'; individual off-flags rs_no_hunt / rs_no_scrim / rs_no_snap40 / rs_no_toss (pass in off=(...)).
Everything physical moves: nobody is teleported into formation except the First Hunt set-up (a stationary pre-whistle placement).
"""
import math
from collections import Counter

SET = dict(snap_line=40., snap_min_s=3., snap_max_s=12.,
           scrim_min_s=2., scrim_max_s=6., scrim_snapper_wait_s=3.5, nose_gap=1.2, back_gap=5., nose_mass=205.,
           toss_min_s=1.5, toss_deadline_s=4., toss_clear=3.,
           hunt_r=5., hunt_gap=1.5, hunt_limit_s=6., react_jitter_s=.03, retake_cap=3)

# formation tables for the snap (u = metres from own goal line, y = lane offsets from centre)
DEPTH = {'STR': 36., 'SCT': 35., 'PDR': 34., 'PFD': 30., 'HNT': 31., 'TRK': 29., 'SEN': 24., 'TRP': 21., 'GRD': 17.}
LANE = {'STR': 10., 'SCT': 36., 'PDR': 22., 'PFD': 8., 'HNT': 18., 'TRK': 22., 'SEN': 8., 'TRP': 32., 'GRD': 9.}
SNAPPER_PREF = ('SEN', 'PFD', 'HNT', 'GRD', 'TRK', 'PDR', 'TRP', 'SCT', 'STR')
HUNT_PREF = ('HNT', 'TRK', 'PDR', 'SCT', 'PFD', 'TRP', 'GRD', 'STR', 'SEN')


def _clamp(v, a, b): return max(a, min(b, v))


def install(CO, S):
    Engine = CO.engine.Engine; Match = CO.match.Match; geo = CO.geometry; types = CO.types
    Phase = types.Phase; Restart = types.Restart; norm = geo.norm
    S.rs_stats = Counter(); S.rs_log = []

    def on(name): return 'restarts' in S.on and ('rs_no_' + name) not in S.on
    def pos_of(pid):
        t = getattr(S, 'tend', {}).get(pid); return t.pos if t is not None else 'TRK'
    def uown(s, team, x): return abs(x - s.ends[team])
    def field(s, team=None):
        return [p for p in s.players.values() if p.active and p.role == 'field' and (team is None or p.team == team)]
    def x_from_u(s, team, u): e = s.ends[team]; return e + u if e == 0 else e - u

    def formation(s, team, line, exclude=(), defensive=False):
        """pid -> (x, y), every field player at or behind `line` metres from his own goal line."""
        groups = {}
        for p in sorted(field(s, team), key=lambda q: q.id):
            if p.id in exclude: continue
            groups.setdefault(pos_of(p.id), []).append(p)
        out = {}
        for pos, lst in groups.items():
            d = DEPTH.get(pos, 28.); w = LANE.get(pos, 20.)
            if defensive: d = min(line - 3., d + 6.)
            d = min(d, line - 1.5)
            n = len(lst)
            ys = [0.] if n == 1 else [-w, w] if n == 2 else [(-1 + 2 * i / (n - 1)) * w for i in range(n)]
            for p, y in zip(lst, ys): out[p.id] = (x_from_u(s, team, d), _clamp(50. + y, 3., 97.))
        return out

    # ---------------------------------------------------------------- bookkeeping on the Restart object (carried by award's keep logic)
    o_award = Engine.award
    def award(self, team, x, y, reason, foul=False, fresh=False, normalize=True):
        s = self.s; old = s.restart
        if 'restarts' in S.on and fresh and reason == 'goal' and on('snap40') and not (s.extension or s.game_ms <= 0):
            o_award(self, team, x_from_u(s, team, SET['snap_line']), 50., reason, foul, fresh, False)
            r = s.restart
            if r is not None and r.reason == 'goal':
                r.kind = 'snap40'; r.clearance = 20.; r.rs = dict(kind='snap40', retakes=0, att=0, dfn=0); S.rs_stats['snap40'] += 1
            return
        if 'restarts' in S.on and reason == 'boundary' and on('toss') and not foul and not fresh:
            R = s.keeper_zone_radius
            bx, by = _clamp(x, 0., 100.), _clamp(y, 0., 100.)
            gaps = {'x0': bx, 'x1': 100. - bx, 'y0': by, 'y1': 100. - by}; side = min(gaps, key=gaps.get)      # the line the ball left over
            if side == 'x0': bx = 0.
            elif side == 'x1': bx = 100.
            elif side == 'y0': by = 0.
            else: by = 100.
            for gx in (0., 100.):                      # no toss inside a Keeper Zone: slide along the goal line to the edge of the arc
                if bx == gx and abs(by - 50.) <= R + .5: by = 50. - (R + 1.) if by < 50. else 50. + (R + 1.)
            o_award(self, team, bx, by, reason, foul, fresh, False)
            r = s.restart
            if r is not None and r.reason == 'boundary':
                out = (bx + (-.4 if bx == 0. else .4 if bx == 100. else 0.), by + (-.4 if by == 0. else .4 if by == 100. else 0.))
                r.kind = 'inbound'; r.clearance = SET['toss_clear']; r.taker_spot = out; r.rs = dict(kind='toss', retakes=0); S.rs_stats['toss'] += 1
            return
        if 'restarts' in S.on and on('hunt') and reason == 'quarter_start' and fresh:
            return begin_quarter_hunt(self)
        o_award(self, team, x, y, reason, foul, fresh, normalize)
        r = s.restart
        if old is not None and r is not None and r is not old and getattr(old, 'rs', None) is not None and r.kind == old.kind:
            r.rs = old.rs           # the same restart retaken: keep its record
    Engine.award = award

    # ---------------------------------------------------------------- scrimmage restart (first tackle)
    o_first = Engine.first_tackle
    def first_tackle(self, a, t, bx, by):
        s = self.s
        if not ('restarts' in S.on and on('scrim')): return o_first(self, a, t, bx, by)
        team = t.team; attacked = s.own_zone(s.other(team)); bx = _clamp(bx, 0., 100.); by = _clamp(by, 0., 100.)
        if self.zone(bx, by) == attacked or s.advantage: return o_first(self, a, t, bx, by)      # goal-line inbound / pending advantage: unchanged
        R = s.keeper_zone_radius; sx, sy = _clamp(bx, 2., 98.), _clamp(by, 2., 98.)
        for gx in (0., 100.):
            d = norm(sx - gx, sy - 50.)
            if d <= R + .5: sx, sy = gx + (sx - gx) * (R + .6) / max(d, 1e-6), 50. + (sy - 50.) * (R + .6) / max(d, 1e-6)
        s.tackle_count = 1; s.engagements.clear(); s.tackle_ordinal += 1
        self.emit('tackle_count', 'C2-3', team=team, count_from=0, count_to=1, tackler=a.id, carrier=t.id, spot=[round(sx, 2), round(sy, 2)], procedure='scrimmage',
                  **({'ordinal_in_possession': s.tackle_ordinal} if self.c4_occ else {}))
        heavy = getattr(a.a, 'mass', 0.) >= SET['nose_mass']
        o_award(self, team, sx, sy, 'scrimmage', False, False, False)
        r = s.restart
        if r is not None and r.reason == 'scrimmage':
            r.kind = 'scrim'; r.clearance = .9; r.taker = None
            r.rs = dict(kind='scrim', snapper=t.id, tackler=a.id, nose=heavy, retakes=0, att=0, dfn=0); S.rs_stats['scrim'] += 1
            self.emit('scrimmage_set', 'RS-1', snapper=t.id, tackler=a.id, alignment='nose' if heavy else 'five_m', spot=[round(sx, 2), round(sy, 2)])
        return True
    Engine.first_tackle = first_tackle

    # ---------------------------------------------------------------- legality
    def violators(self, r):
        s = self.s; rs = r.rs; att, dfn = [], []
        if rs['kind'] == 'snap40':
            for p in field(s):
                if p.id == r.taker or p.posture != 'upright': continue
                if uown(s, p.team, p.x) > SET['snap_line'] + .3: (att if p.team == r.team else dfn).append(p)
        elif rs['kind'] == 'scrim':
            sg = s.attack_sign(r.team)
            for p in field(s):
                if p.id == r.taker or p.posture != 'upright': continue
                ua = sg * (p.x - r.x)
                if p.team == r.team:
                    if ua > -.3: att.append(p)
                elif ua < .3: dfn.append(p)
        return att, dfn

    o_ready = Engine.ready
    def ready(self, taker):
        s = self.s; r = s.restart
        if r is not None and 'restarts' in S.on and getattr(r, 'rs', None) is not None and r.rs['kind'] in ('snap40', 'scrim', 'toss'):
            rs = r.rs; age = (s.now - r.created_at) / 1000.
            lo, hi = {'snap40': (SET['snap_min_s'], SET['snap_max_s']), 'scrim': (SET['scrim_min_s'], SET['scrim_max_s']), 'toss': (SET['toss_min_s'], 99.)}[rs['kind']]
            if age < lo: return False
            if rs['kind'] != 'toss' and age < hi:
                a_, d_ = violators(self, r)
                if a_ or d_: return False
        return o_ready(self, taker)
    Engine.ready = ready

    o_release = Engine.restart_release
    def restart_release(self, taker, velocity, target=None, method='hand'):
        s = self.s; r = s.restart
        rs = getattr(r, 'rs', None) if r is not None else None
        if rs is None or 'restarts' not in S.on: return o_release(self, taker, velocity, target, method)
        kind = rs['kind']
        if kind == 'toss':
            if r.ready_at is not None and s.now - r.ready_at > SET['toss_deadline_s'] * 1000:
                self.emit('toss_late', 'RS-4', taker=taker); S.rs_stats['toss_late'] += 1
                self.award(s.other(r.team), r.x, r.y, 'restart_fault', fresh=True); return False
        else:
            att, dfn = violators(self, r)
            if rs['retakes'] >= SET['retake_cap']: att, dfn = [], []
            if att or dfn:
                rs['retakes'] += 1; names = ([p.id for p in att], [p.id for p in dfn])
                if att and dfn:
                    self.emit('restart_offside', 'RS-2', kind=kind, offence=names[0], defence=names[1], result='offsetting_retake'); S.rs_stats[kind + '_offset'] += 1
                elif dfn:
                    rs['dfn'] += 1; S.rs_stats[kind + '_def_offside'] += 1
                    worst = min(dfn, key=lambda p: norm(p.x - r.x, p.y - r.y))
                    if kind == 'scrim':
                        old = s.tackle_count; s.tackle_count = 0
                        self.emit('restart_offside', 'RS-2', kind=kind, defence=names[1], result='defensive_offside_count_reset', count_from=old, count_to=0)
                    else: self.emit('restart_offside', 'RS-2', kind=kind, defence=names[1], result='defensive_offside_retake')
                    if rs['dfn'] >= 2: self.pending_discipline.append((worst.id, 'minor' if rs['dfn'] >= 3 else 'warning', False))
                else:
                    rs['att'] += 1; S.rs_stats[kind + '_off_offside'] += 1
                    if kind == 'scrim':
                        s.tackle_count += 1
                        self.emit('restart_offside', 'RS-2', kind=kind, offence=names[0], result='offensive_offside_count_up', count_to=s.tackle_count)
                        if s.tackle_count >= 2:
                            self.new_owner(s.other(r.team), 'scrimmage_offside'); s.possession_ms = self.play_ms
                            self.award(s.other(r.team), r.x, r.y, 'scrimmage_offside', fresh=True, normalize=False); S.rs_stats['scrim_turnover_offside'] += 1
                            return False
                    else:
                        self.emit('restart_offside', 'RS-2', kind=kind, offence=names[0], result='offensive_offside_retake')
                        if rs['att'] >= 2:
                            self.award(s.other(r.team), r.x, r.y, 'restart_fault', fresh=True); S.rs_stats['snap40_turnover_offside'] += 1; return False
                self.award(r.team, r.x, r.y, 'defensive_restart_fault' if dfn and not att else 'offensive_restart_fault', foul=True)
                return False
        t_dead = (s.now - r.created_at) / 1000.
        ok = o_release(self, taker, velocity, target, method)
        if ok:
            S.rs_log.append((kind, round(t_dead, 2), rs['retakes'], s.period, round(s.live_ms / 1000., 1)))
        return ok
    Engine.restart_release = restart_release

    # ---------------------------------------------------------------- dead-ball movement
    o_td = Match.targets_dead
    def targets_dead(self):
        s = self.s; r = s.restart
        rs = getattr(r, 'rs', None) if r is not None else None
        if rs is None or 'restarts' not in S.on or r.ready_at is not None and r.taker is not None and False:
            return o_td(self)
        kind = rs['kind']
        if r.ready_at is None:                                    # choose the snapper / thrower before the engine picks the nearest man
            cands = [p for p in field(s, r.team) if p.eligible(s.now) and p.posture == 'upright']
            if kind == 'scrim':
                sn = s.players.get(rs['snapper'])
                if sn is not None and sn.active and sn.eligible(s.now) and (sn.posture == 'upright' or (s.now - r.created_at) / 1000. < SET['scrim_snapper_wait_s']): r.taker = sn.id if sn.eligible(s.now) else None
                else:
                    rs['snapper'] = None; r.taker = min(cands, key=lambda p: norm(p.x - r.x, p.y - r.y)).id if cands else None
            elif kind == 'snap40' and cands:
                r.taker = min(cands, key=lambda p: (SNAPPER_PREF.index(pos_of(p.id)) if pos_of(p.id) in SNAPPER_PREF else 9, norm(p.x - r.x, p.y - r.y), p.id)).id
            elif kind == 'toss' and cands:
                cur = s.players.get(r.taker) if r.taker else None
                if cur is None or cur.role != 'field':
                    r.taker = min(cands, key=lambda p: (norm(p.x - r.x, p.y - r.y), p.id)).id
        tg = o_td(self)
        if kind == 'snap40':
            for team in ('A', 'B'):
                spots = formation(s, team, SET['snap_line'], exclude=(r.taker,), defensive=(team != r.team))
                for pid, xy in spots.items():
                    if pid in tg or True: tg[pid] = xy
            if r.taker: tg[r.taker] = (r.x, r.y)
        elif kind == 'scrim':
            sg = s.attack_sign(r.team)
            for p in field(s):
                if p.id == r.taker: continue
                ua = sg * (p.x - r.x)
                if p.team == r.team:
                    tx = r.x - sg * (1.6 if ua > -1.6 else -ua) if ua > -1. else p.x
                    tg[p.id] = (_clamp(tx, 1., 99.), _clamp(p.y, 1., 99.))
                else:
                    if p.id == rs['tackler'] and p.posture == 'upright':
                        gap = SET['nose_gap'] if rs['nose'] else SET['back_gap']
                        tg[p.id] = (_clamp(r.x + sg * gap, 1., 99.), r.y)
                    else:
                        tx = r.x + sg * (1.6 if ua < 1.6 else ua) if ua < 1. else p.x
                        tg[p.id] = (_clamp(tx, 1., 99.), _clamp(p.y, 1., 99.))
        return tg
    Match.targets_dead = targets_dead

    # ---------------------------------------------------------------- First Hunt
    def place_support(self, exclude):
        s = self.s; moved = 0
        for team in ('A', 'B'):
            spots = formation(s, team, 44., exclude=exclude)
            for pid, (x, y) in spots.items():
                p = s.players[pid]; p.x, p.y, p.vx, p.vy = x, y, 0., 0.; moved += 1
        return moved

    o_begin = Engine.begin_hunt
    def begin_hunt(self):
        o_begin(self)
        s = self.s
        if not ('restarts' in S.on and on('hunt')): return
        for team, pid in zip(('A', 'B'), s.opening_contestants):
            p = s.players[pid]; sg = s.attack_sign(team)
            p.x, p.y, p.vx, p.vy = 50. - sg * SET['hunt_gap'], 50., 0., 0.
        place_support(self, exclude=set(s.opening_contestants))
        s.opening_deadline = None; s.hunt = dict(t0=s.now, period=s.period, contestants=list(s.opening_contestants), first_touch=None, react={}, last=s.now)
        import random
        rng = random.Random('%s-%s-%s' % (getattr(S, 'seed', 0), s.period, S.rs_stats['hunts_started']))
        for pid in s.opening_contestants:                  # reaction to the signal: his own decision speed plus a small seeded jitter
            s.hunt['react'][pid] = int(1000 * max(0.02, s.players[pid].a.decision_speed + rng.gauss(0, SET['react_jitter_s'])))
        S.rs_stats['hunts_started'] += 1
        self.emit('hunt_start', 'FH-1', contestants=list(s.opening_contestants), circle_r=SET['hunt_r'], gap=SET['hunt_gap'])
    Engine.begin_hunt = begin_hunt

    def begin_quarter_hunt(self):
        s = self.s
        s.owner = None; s.opening_failures = 0; s.opening_touched = False
        pick = []
        for team in ('A', 'B'):
            c = sorted([p for p in field(s, team) if p.eligible(s.now)], key=lambda p: (HUNT_PREF.index(pos_of(p.id)) if pos_of(p.id) in HUNT_PREF else 9, p.id))
            pick.append(c[(s.period - 1) % min(3, len(c))].id)
        s.opening_contestants = pick
        s.restart = None; s.phase = Phase.OPENING
        self.begin_hunt()
        self.emit('quarter_hunt', 'FH-1', period=s.period)
    S.begin_quarter_hunt = begin_quarter_hunt

    o_acquire = Engine.acquire
    def acquire(self, pid, forced_joint=False):
        s = self.s; was = s.phase
        h = getattr(s, 'hunt', None)
        if was == Phase.OPENING and 'restarts' in S.on and on('hunt') and h is not None and h.get('live') is None and pid in h['react'] and not h.get('bypass') and s.now - h['t0'] < h['react'][pid]:
            return False                                   # he has not reacted to the signal yet
        ok = o_acquire(self, pid, forced_joint)
        if ok and was == Phase.OPENING and 'restarts' in S.on and on('hunt') and s.phase == Phase.LIVE and getattr(s, 'hunt', None) is not None and s.hunt.get('live') is None:
            s.phase = Phase.OPENING; s.opening_touched = False; s.opening_deadline = None
            if s.hunt['first_touch'] is None: s.hunt['first_touch'] = (pid, s.now)
        return ok
    Engine.acquire = acquire

    # ---------------------------------------------------------------- Archers hold until the ball has left the circle
    def hunt_pending(s):
        h = getattr(s, 'hunt', None)
        return s.phase == Phase.OPENING and h is not None and h.get('live') is None
    o_arrow_dec = Match.arrow_decisions
    def arrow_decisions(self):
        if 'restarts' in S.on and on('hunt') and hunt_pending(self.s):
            self.pending_draw.clear(); return
        return o_arrow_dec(self)
    Match.arrow_decisions = arrow_decisions
    o_shoot = Engine.shoot_arrow
    def shoot_arrow(self, pid, target, velocity, origin=None):
        if 'restarts' in S.on and on('hunt') and hunt_pending(self.s):
            S.rs_stats['archer_held_in_hunt'] += 1; return False          # nothing drawn, no ammunition spent, no foul
        return o_shoot(self, pid, target, velocity, origin)
    Engine.shoot_arrow = shoot_arrow

    o_joint = Engine.joint_control
    def joint_control(self, pids):
        s = self.s; h = getattr(s, 'hunt', None)
        if s.phase == Phase.OPENING and 'restarts' in S.on and on('hunt') and h is not None and h.get('live') is None:
            c = [p for p in pids if p in h['react']]
            if c:                                           # simultaneous first touch: the faster reaction (own decision speed + jitter) takes the ball
                win = min(c, key=lambda p: (h['react'][p], p)); S.rs_stats['hunt_joint_resolved'] += 1
                h['bypass'] = True
                try: Engine.acquire(self, win)
                finally: h['bypass'] = False
                return True
        return o_joint(self, pids)
    Engine.joint_control = joint_control

    o_elapse = Engine.elapse
    def elapse(self, dt, resolve=True):
        s = self.s; was = s.phase
        if was == Phase.OPENING and 'restarts' in S.on and on('hunt') and getattr(s, 'hunt', None) is not None and s.hunt.get('live') is None:
            keep = (s.game_ms, s.live_ms, s.possession_ms, s.extension)
            r = o_elapse(self, dt, resolve)
            s.game_ms, s.live_ms, s.possession_ms = keep[0], keep[1], keep[2]       # the quarter clock starts when the ball exits the circle
            return r
        return o_elapse(self, dt, resolve)
    Engine.elapse = elapse

    o_step = Match.step
    def step(self):
        o_step(self)
        s = self.s
        h = getattr(s, 'hunt', None)
        if h is None or h.get('live') is not None or 'restarts' not in S.on or not on('hunt') or s.phase != Phase.OPENING: return
        gap = s.now - h.get('last', s.now); h['last'] = s.now
        if gap > 2000: h['t0'] += gap                       # an intermission passed inside the step: the Hunt's own timer did not
        b = s.ball; d = norm(b.x - 50., b.y - 50.)
        if d - b.radius >= SET['hunt_r']:
            by_carry = b.carrier is not None
            h['live'] = s.now; s.phase = Phase.LIVE; s.opening_touched = True; s.opening_deadline = None
            if s.owner is not None: s.possession_ms = self.e.play_ms; s.tackle_count = 0
            S.rs_stats['hunts_live'] += 1; S.rs_stats['hunt_exit_carry' if by_carry else 'hunt_exit_loose'] += 1
            S.rs_log.append(('hunt', round((s.now - h['t0']) / 1000., 2), s.period, 'carry' if by_carry else 'loose', s.owner, h['first_touch'][0] if h['first_touch'] else None))
            self.e.emit('hunt_live', 'FH-9', method='carry' if by_carry else 'loose', owner=s.owner, duration_ms=s.now - h['t0'])
        elif (s.now - h['t0']) / 1000. >= SET['hunt_limit_s']:
            s.owner = None; S.rs_stats['hunt_timeouts'] += 1
            self.e.emit('hunt_timeout', 'FH-12', duration_ms=s.now - h['t0'], t0=h['t0'], period=s.period, carrier=b.carrier, ball=[round(b.x, 2), round(b.y, 2)], first_touch=h['first_touch'][0] if h['first_touch'] else None)
            self.e.failed_hunt('timeout')
    Match.step = step
    return Engine
