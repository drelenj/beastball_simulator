"""RB-3.5 PROVISIONAL (owner canon rulings 17-18 Nov 2026), native-rb/3 only.

Zone residence by zone:
- A DEFENDER (team not in passive possession) is covered only in the Keeper Zone he
  defends (his own team's zone): zone_unmarked foul after zone_residence_ms of live time
  unmarked. Marked = an opposing active field player within zone_marked_distance_m.
- An ATTACKER (team in passive possession) is covered only in the Keeper Zone he
  attacks: zone_residence (turnover restart) after zone_residence_ms of live time.
- Timer behaviour unchanged: it resets when he is marked or leaves the zone; one call
  per step, then all timers clear (as before).
Diagnosis (log only): a zone_foul_diagnosis event at every zone_unmarked /
zone_residence call, and a cumulative zone_time_summary at every period end.
"""
import math
from collections import Counter


def state(e):
    st = getattr(e, 'rb35', None)
    if st is None:
        st = e.rb35 = dict(entry={}, exit={}, own_exit={}, in_own={}, time={t: Counter() for t in ('A', 'B')}, player={})
    return st


def covered_zone(s, team, pp):
    """Zone index a player of `team` is covered in: attacked zone if his team has passive
    possession, otherwise the zone he defends."""
    return s.own_zone(s.other(team)) if team == pp else s.own_zone(team)


def zone_centre(s, zn):
    return (0., 50.) if zn == 0 else (100., 50.)


def opponents_near(s, p, radius):
    return any(q.active and q.team != p.team and q.role == 'field' and math.hypot(q.x - p.x, q.y - p.y) <= radius
               for q in s.players.values())


def account(port, dt):
    """Live-time share of defenders (field players, Keepers excluded) inside their own zone."""
    s, e = port.m.s, port.m.e
    pp = e.possession.pp
    if dt <= 0 or pp is None:
        return
    team = s.other(pp); t = state(e)['time'][team]
    for p in s.players.values():
        if not p.active or p.team != team or p.role != 'field':
            continue
        t['defender_ms'] += dt
        cfg = port.config; pc = state(e)['player'].setdefault(p.id, Counter()); pc['defender_ms'] += dt
        marking = opponents_near(s, p, cfg.defender_mark_distance_m)
        leash = math.hypot(s.ball.x - p.x, s.ball.y - p.y) <= cfg.defender_ball_leash_m
        if marking or leash:
            t['baseline_satisfied_ms'] += dt; pc['baseline_satisfied_ms'] += dt
        if e.zone(p.x, p.y) == s.own_zone(team):
            t['in_own_zone_ms'] += dt
            if not opponents_near(s, p, 5.):
                t['in_own_zone_unmarked_ms'] += dt


def diagnosis(port, p, zn, kind, start):
    s, e = port.m.s, port.m.e
    st = state(e); pp = e.possession.pp
    cx, cy = zone_centre(s, zn); b = s.ball; carrier = s.players.get(b.carrier)
    offence = [q for q in s.players.values() if q.active and q.team == pp and q.role != 'archer' and q.id != p.id]
    off_ball = [q for q in offence if q.id != b.carrier]
    near = lambda pool: min(pool, key=lambda q: (math.hypot(q.x - p.x, q.y - p.y), q.id), default=None)
    nob, nany = near(off_ball), near(offence)
    d = lambda q: round(math.hypot(q.x - p.x, q.y - p.y), 3)
    entered = st['entry'].get(p.id, start); exited = st['exit'].get(p.id)
    e.emit('zone_foul_diagnosis', 'RB-3.5-report', kind=kind,
           fouler=dict(id=p.id, team=p.team, role=p.role, x=round(p.x, 3), y=round(p.y, 3),
                       zone='own' if zn == s.own_zone(p.team) else 'attacked',
                       distance_to_zone_centre=round(math.hypot(p.x - cx, p.y - cy), 3),
                       live_ms_in_zone=s.live_ms - entered, live_ms_unmarked=s.live_ms - start,
                       reentered_within_5s=exited is not None and s.live_ms - exited <= 5000,
                       # leaving resets the timer, so a re-entry inside the last 5 s cannot precede a call;
                       # the time since the last exit is logged to show re-entry just before the timer started.
                       live_ms_since_last_exit=None if exited is None else s.live_ms - exited,
                       frozen_or_immune_prev_10s=p.freeze_until > 0 and p.immune_until >= s.now - 10000),
           ball=dict(x=round(b.x, 3), y=round(b.y, 3), status=e.possession.public().ball_status,
                     distance_to_zone_centre=round(math.hypot(b.x - cx, b.y - cy), 3),
                     carrier=dict(id=carrier.id, x=round(carrier.x, 3), y=round(carrier.y, 3), distance_to_fouler=d(carrier)) if carrier else None,
                     distance_to_fouler=round(math.hypot(b.x - p.x, b.y - p.y), 3)),
           possession_team=pp,
           nearest_off_ball_offence=dict(id=nob.id, role=nob.role, x=round(nob.x, 3), y=round(nob.y, 3), distance_to_fouler=d(nob),
                                         distance_to_zone_centre=round(math.hypot(nob.x - cx, nob.y - cy), 3)) if nob else None,
           nearest_offence_any=dict(id=nany.id, role=nany.role, distance_to_fouler=d(nany)) if nany else None,
           offence_within_10m=sum(d(q) <= 10 for q in offence), offence_within_20m=sum(d(q) <= 20 for q in offence),
           teammates_in_same_zone=sum(1 for q in s.players.values() if q.active and q.team == p.team and q.id != p.id
                                      and q.role != 'archer' and e.zone(q.x, q.y) == zn))


def residence(port, before_live):
    s, e, cfg = port.m.s, port.m.e, port.config
    st = state(e); pp = e.possession.pp
    account(port, s.live_ms - before_live)
    for p in s.players.values():
        zn = e.zone(p.x, p.y)
        own = zn is not None and zn == s.own_zone(p.team)       # own-zone memory for the athlete's view
        if st['in_own'].get(p.id) and not own:
            st['own_exit'][p.id] = s.live_ms
        st['in_own'][p.id] = own
        inside = zn is not None and zn == covered_zone(s, p.team, pp)
        if inside and p.id not in st['entry']:
            st['entry'][p.id] = s.live_ms
        elif not inside and p.id in st['entry']:
            st['exit'][p.id] = s.live_ms; del st['entry'][p.id]
        if not p.active or p.role != 'field' or not inside:
            e.residence.pop(p.id, None); continue
        marked = p.team != pp and any(q.active and q.team != p.team and q.role == 'field'
                                      and math.hypot(q.x - p.x, q.y - p.y) <= cfg.zone_marked_distance_m for q in s.players.values())
        if marked:
            e.residence.pop(p.id, None); continue
        start = e.residence.setdefault(p.id, s.live_ms)
        if s.live_ms - start >= cfg.zone_residence_ms:
            if p.team == pp:
                diagnosis(port, p, zn, 'zone_residence', start)
                e.award(s.other(p.team), p.x, p.y, 'zone_residence', fresh=True, normalize=False)
            else:
                diagnosis(port, p, zn, 'zone_unmarked', start)
                e.foul(p.id, reason='zone_unmarked')
            e.residence.clear(); break


def install(co, cfg):
    if cfg.version != 'native-rb/3':
        return
    E = co.engine.Engine
    old_end = E.end_period

    def end_period(self):
        t = state(self)['time']
        row = {}
        for team, c in t.items():
            total = c['defender_ms']
            row[team] = dict(defender_ms=total, in_own_zone_ms=c['in_own_zone_ms'], in_own_zone_unmarked_ms=c['in_own_zone_unmarked_ms'],
                             share_in_own_zone=round(c['in_own_zone_ms'] / total, 4) if total else None,
                             share_in_own_zone_unmarked=round(c['in_own_zone_unmarked_ms'] / total, 4) if total else None,
                             baseline_satisfied_ms=c['baseline_satisfied_ms'],
                             share_baseline_satisfied=round(c['baseline_satisfied_ms'] / total, 4) if total else None)
        row['players'] = {pid: round(c['baseline_satisfied_ms'] / c['defender_ms'], 4) for pid, c in sorted(state(self)['player'].items()) if c['defender_ms']}
        self.emit('zone_time_summary', 'RB-3.5-report', cumulative=True, period=self.s.period, teams=row)
        return old_end(self)
    E.end_period = end_period
