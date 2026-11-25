"""RB-3.28 live workload and rulebook-owned dead-ball rotation."""
from math import hypot

from native.roster import throw_error_base_deg

# Behavioural calibration defaults. Rates are reserve units per simulated second.
FIELD_RECOVERY = .00035
SPRINT_DRAIN = .004
BENCH_RECOVERY = .002
NEUTRAL_EFFORT = .50
EFFORT_EXPONENT = .40
STAMINA_SENSITIVITY = .30
STAMINA_RATE_RANGE = .65
PHYSICAL_LOSS = .40
TECHNIQUE_LOSS = .30
OUTPUT_UPDATE_MS = 500
REST_THRESHOLD = .60
RETURN_THRESHOLD = .75
KEEPER_REGULATION_MIN_MS = 36 * 60_000

POSITION_GROUPS = (
    frozenset(('PDR', 'STR', 'SCT')),
    frozenset(('PFD', 'HNT', 'TRK', 'SEN')),
    frozenset(('TRP', 'GRD')),
)
GROUP = {position: index for index, members in enumerate(POSITION_GROUPS) for position in members}
PHYSICAL = ('braking', 'turning', 'strength', 'jump_height', 'agility')
TECHNIQUE = ('tackling', 'blocking', 'ball_handling', 'passing', 'catching', 'archery_accuracy')


def reserve_after(reserve, stamina, effort, seconds, *, bench=False):
    if bench:
        rate = BENCH_RECOVERY
    else:
        # Preserve the exact standing and sprint endpoints. The midpoint is
        # neutral at average Stamina and shifts modestly for other athletes.
        effort -= STAMINA_SENSITIVITY * (stamina - .70) * (4 * effort * (1 - effort))
        relative = (effort - NEUTRAL_EFFORT) / NEUTRAL_EFFORT
        factor = 1 + STAMINA_RATE_RANGE * (stamina - .70)
        rate = -relative * (FIELD_RECOVERY * factor if relative <= 0 else SPRINT_DRAIN / factor)
    return min(1., max(0., reserve + rate * seconds))


def technique(rating, reserve):
    return rating * (1 - TECHNIQUE_LOSS * (1 - reserve) * (1 - rating))


def select_substitute(outgoing, candidates, roster):
    position, _ = roster.get(outgoing.id, (None, 0.))
    group = GROUP.get(position)

    def rank(candidate):
        label, overall = roster.get(candidate.id, (None, 0.))
        tier = (0 if position and position == label else
                1 if group is not None and group == GROUP.get(label) else 2)
        return tier, -overall, candidate.id

    incoming = min(candidates, key=rank, default=None)
    return (incoming, ('position', 'group', 'overall')[rank(incoming)[0]]) if incoming else (None, None)


class FatigueRotation:
    def __init__(self, port, rosters):
        self.port = port
        players = port.m.s.players.values()
        self.roster = {f'{team}:{pid}': (position, overall) for team, roster in rosters.items()
                       for pid, position, overall in getattr(roster, 'rotation_candidates', ())}
        self.starters = {(p.team, p.slot): p.id for p in players if p.active}
        self.assigned = {p.id: p.role for p in players}
        self.base = {p.id: (tuple(getattr(p.a, k) for k in PHYSICAL + TECHNIQUE),
                            p.native_max_throw_speed, p.native_throw_error_base_deg)
                     for p in players}
        self.played_ms = dict.fromkeys(self.assigned, 0)
        self.regulation_ms = dict.fromkeys(self.assigned, 0)
        self.regulation_limit_ms = port.config.periods * port.config.period_seconds * 1000
        self.next_output_ms = 0
        self.last_restart = None
        self.due = set()

    @staticmethod
    def execution_rating(player, name):
        return technique(player.native_registry[name], player.fatigue)

    def apply_output(self, p):
        values, top, error = self.base[p.id]
        reserve = p.fatigue
        physical = 1 - PHYSICAL_LOSS * (1 - reserve)
        for name, rating in zip(PHYSICAL, values):
            setattr(p.a, name, rating * physical)
        for name, rating in zip(TECHNIQUE, values[len(PHYSICAL):]):
            setattr(p.a, name, technique(rating, reserve))
        p.native_max_throw_speed = top * physical
        p.native_throw_error_base_deg = error if reserve == 1 else throw_error_base_deg(p.a.passing)

    def advance(self, now, live, active):
        state = self.port.m.s
        elapsed = (state.now - now) * .001
        live_delta = state.live_ms - live
        live_seconds = live_delta * .001
        regulation_delta = min(state.live_ms, self.regulation_limit_ms) - min(live, self.regulation_limit_ms)
        if not elapsed:
            return
        update_output = state.now >= self.next_output_ms
        if update_output:
            self.next_output_ms = state.now + OUTPUT_UPDATE_MS
        for p in state.players.values():
            previous = p.fatigue
            if p.id not in active:
                if previous < 1:
                    p.fatigue = reserve_after(previous, 0., 0., elapsed, bench=True)
            else:
                self.played_ms[p.id] += live_delta
                self.regulation_ms[p.id] += regulation_delta
                if live_delta and p.role != 'archer' and p.eligible(state.now):
                    # Max of achieved speed and current drive demand, normalized
                    # to attainable sprint speed. Brake-distance work is v²=2ad.
                    top = max(1., p.a.maximum_speed * (.70 + .30 * previous))
                    speed = hypot(p.vx, p.vy)
                    distance = hypot(p.target[0] - p.x, p.target[1] - p.y)
                    work = max(speed * speed, 2 * p.a.braking * distance)
                    effort = min(1., (work ** .5 / top) ** EFFORT_EXPONENT)
                else:
                    effort = 0.
                p.fatigue = reserve_after(previous, p.a.endurance, effort, live_seconds)
                if live_delta and p.role == 'field' and p.fatigue <= REST_THRESHOLD:
                    self.due.add(p.id)
                if elapsed > live_seconds:
                    p.fatigue = reserve_after(p.fatigue, p.a.endurance, 0., elapsed - live_seconds)
            if update_output and (p.fatigue < 1 or p.native_max_throw_speed != self.base[p.id][1]):
                self.apply_output(p)

    def choose(self, outgoing, candidates):
        return select_substitute(outgoing, (p for p in candidates if p.fatigue >= RETURN_THRESHOLD),
                                 self.roster)

    def rotate(self):
        engine = self.port.m.e
        s = engine.s
        restart = s.restart
        if (s.phase != self.port.types.Phase.DEAD or restart is None
                or restart.native_id == self.last_restart or restart.rs.get('formation')):
            return
        self.last_restart = restart.native_id
        active = {(p.team, p.slot): p for p in s.players.values() if p.active}
        for slot, starter in self.starters.items():
            outgoing = active.get(slot)
            incoming = s.players[starter]
            if (outgoing is not None and outgoing.role == 'field' and incoming.role == 'field'
                    and not incoming.active and incoming.fatigue >= RETURN_THRESHOLD):
                if self.swap(outgoing, incoming, 'starter_return', 'starter_slot'):
                    active[slot] = incoming

        for slot, outgoing in active.items():
            if outgoing.fatigue > REST_THRESHOLD and outgoing.id not in self.due:
                continue
            if outgoing.role == 'keeper':
                if (self.starters.get(slot) != outgoing.id
                        or self.regulation_ms[outgoing.id] < KEEPER_REGULATION_MIN_MS):
                    continue
            elif outgoing.role != 'field':
                continue
            candidates = (p for p in s.players.values() if p.team == outgoing.team and not p.active
                          and p.role == outgoing.role
                          and engine.rb_can_enter(p) and p.id not in self.starters.values())
            incoming, tier = self.choose(outgoing, candidates)
            if incoming is not None:
                self.swap(outgoing, incoming, 'fatigue', tier)

    def swap(self, outgoing, incoming, reason, tier):
        return self.port.m.e.rb_substitute(outgoing.id, incoming.id,
                                           rotation_reason=reason, rotation_tier=tier)

    def log_swap(self, outgoing, incoming, reason, tier):
        e = self.port.m.e
        self.due.discard(outgoing.id)
        self.due.discard(incoming.id)
        event = 'rotation_substitution' if reason == 'required_cover' else 'fatigue_substitution'
        e.emit(event, 'RB-3.28', team=outgoing.team, role=outgoing.role,
               outgoing=outgoing.id, incoming=incoming.id, slot=incoming.slot,
               live_ms=e.s.live_ms, outgoing_energy=outgoing.fatigue,
               incoming_energy=incoming.fatigue, reason=reason, tier=tier)

    def record(self):
        starters = self.starters.values()
        return {pid: dict(role=self.assigned[pid], starter=pid in starters, live_ms=ms,
                          regulation_ms=self.regulation_ms[pid],
                          energy=self.port.m.s.players[pid].fatigue)
                for pid, ms in self.played_ms.items()}


# Remove the old fatigue writes in the private kernel only. Keep its existing
# reserve multipliers for speed, acceleration and force.
KERNEL_PATCHES = (
    ('p.fatigue=min(1,p.fatigue+dt*.006*p.a.endurance);continue', 'continue'),
    ("""   intensity=(p.speed/max(1,p.a.maximum_speed))**2
   if self.e.live()or s.phase==Phase.PENALTY:
    cost=(.00015+.006*intensity)*(1.25-p.a.endurance*.6)*self.assume['fatigue_rate']
    p.fatigue=clamp(p.fatigue-dt*cost,.15,1)
   elif p.speed<2:p.fatigue=min(1,p.fatigue+dt*.002*p.a.endurance)
""", ''),
    ('  for p in idle:p.fatigue=min(1,p.fatigue+dta*.006*p.a.endurance)\n', ''),
    ("""   intensity=(p.speed/max(1,p.a.maximum_speed))**2
   if live:
    cost=(.00015+.006*intensity)*(1.25-p.a.endurance*.6)*A['fatigue_rate']
    p.fatigue=clamp(p.fatigue-dta*cost,.15,1)
   elif p.speed<2:p.fatigue=min(1,p.fatigue+dta*.002*p.a.endurance)
""", ''),
)
