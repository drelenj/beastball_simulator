"""FAB-1c restart metric: release and timeout are reported separately, by kind.

Read-only harness measurement. It reads true state to describe what happened;
nothing here is visible to cognition and nothing here changes the match (no
random draws, no state writes, not part of the trace or state hash).

Per restart it records, at the award, whether any eligible taker could physically
reach the taker spot inside the rule window, and, while the restart is open,
whether a teammate stood at a legal throwable distance from the spot. The
functional bar of FAB-1c is the timeout rate among restarts where both held.
"""
import math

TOSS_WINDOW_MS, SNAP_WINDOW_MS = 5500, 10000
OVERHEAD_MS = 1500        # claim latency + decision cadence + release wind-up (measurement allowance)
THROW_MIN_M, THROW_MAX_M = 4., 34.
KINDS = ('toss', 'scrim', 'snap40')


def travel_ms(distance, top, acceleration, braking):
    """Time to cover a distance from rest and stop, with the athlete's own limits."""
    ramp = top*top/(2*acceleration)+top*top/(2*braking)
    if distance <= ramp:
        return 1000*math.sqrt(2*distance*(1/acceleration+1/braking))
    return 1000*(top/acceleration+top/braking+(distance-ramp)/top)


class RestartMetric:
    def __init__(self):
        self.rows = {}
        self.current = None

    def observe(self, port):
        s = port.m.s
        r = s.restart
        rid = getattr(r, 'native_id', None) if r is not None else None
        if rid is None:
            self.current = None
            return
        row = self.rows.get(rid)
        if row is None:
            snapper = r.rs.get('snapper')
            window = TOSS_WINDOW_MS if r.kind == 'toss' else SNAP_WINDOW_MS
            best = None
            for p in s.players.values():
                if not p.active or p.team != r.team:
                    continue
                if snapper is not None and p.id != snapper:
                    continue
                if snapper is None and p.role != 'field':
                    continue
                wait = max(0, p.freeze_until-s.now, (p.next_action-s.now) if p.posture == 'grounded' else 0)
                top = p.a.maximum_speed * (1. if 'planning_speed' in getattr(port.config,'rb333',()) else .88)
                t = wait+travel_ms(math.dist((p.x, p.y), r.taker_spot), top, p.a.acceleration, p.a.braking)
                best = t if best is None else min(best, t)
            row = self.rows[rid] = dict(kind=r.kind, reason=r.reason, team=r.team, created_ms=s.now,
                                        best_travel_ms=None if best is None else round(best),
                                        taker_reachable=best is not None and best+OVERHEAD_MS <= window,
                                        target_available=False, claimed_ms=None)
        if row['claimed_ms'] is None and r.taker:
            row['claimed_ms'] = s.now-row['created_ms']
        if not row['target_available']:
            row['target_available'] = any(
                p.active and p.team == r.team and p.role != 'archer' and p.id != r.taker
                and THROW_MIN_M <= math.hypot(p.x-r.x, p.y-r.y) <= THROW_MAX_M
                for p in s.players.values())
        self.current = rid

    def summary(self, results):
        out = {}
        for kind in KINDS+('all',):
            rows = [(rid, row) for rid, row in self.rows.items() if kind in ('all', row['kind'])]
            def count(pred, subset=rows):
                return sum(1 for rid, row in subset if pred(results.get(rid, 'pending')))
            eligible = [(rid, row) for rid, row in rows if row['taker_reachable'] and row['target_available']]
            n, m = len(rows), len(eligible)
            released = count(lambda st: st == 'released')
            timeout = count(lambda st: st.endswith('_timeout'))
            el_released = count(lambda st: st == 'released', eligible)
            el_timeout = count(lambda st: st.endswith('_timeout'), eligible)
            out[kind] = dict(awarded=n, released=released, timeout=timeout,
                             play_clock_expiry=count(lambda st: st == 'play_clock_expiry'),
                             superseded=count(lambda st: st.startswith('superseded') or st.startswith('procedural')),
                             ended_by_period=count(lambda st: st in ('end_of_period', 'period_end', 'match_end')),
                             pending=count(lambda st: st == 'pending'),
                             release_rate=released/n if n else None, timeout_rate=timeout/n if n else None,
                             eligible=m, eligible_released=el_released, eligible_timeout=el_timeout,
                             eligible_timeout_rate=el_timeout/m if m else None,
                             not_reachable=sum(1 for rid, row in rows if not row['taker_reachable']),
                             no_target=sum(1 for rid, row in rows if not row['target_available']))
        out['unobserved']=len(set(results)-set(self.rows))   # awarded and closed inside one step
        return out
