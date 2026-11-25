"""Coach rotation, applied by the rulebook before restart placement."""
from collections import defaultdict

from native.roster import engine_order

from .fatigue_rotation import (
    FatigueRotation, GROUP, POSITION_GROUPS, KEEPER_REGULATION_MIN_MS, REST_THRESHOLD,
    RETURN_THRESHOLD, select_substitute,
)

REST_WINDOW_MS = 4 * 60_000


def split_waves(starters, roster):
    groups = defaultdict(list)
    for player in starters:
        position, _ = roster.get(player.id, (None, 0.))
        groups[GROUP.get(position, len(POSITION_GROUPS))].append(player)
    waves = ([], [])
    for _, group in sorted(groups.items()):
        first = len(waves[0]) > len(waves[1])
        for index, player in enumerate(group):
            waves[(first + index) % 2].append(player)
    return waves


def resting_wave(live_ms, period_ms, period):
    # Overtime is distinct even if a custom test truncated regulation.
    if period > 4 or live_ms >= 4 * period_ms:
        return None
    index, elapsed = divmod(live_ms, period_ms)
    if index % 2 == 0 and elapsed >= period_ms - REST_WINDOW_MS:
        return 0
    if index % 2 == 1 and elapsed < REST_WINDOW_MS:
        return 1
    return None


class PlannedRotation(FatigueRotation):
    def __init__(self, port, rosters):
        super().__init__(port, rosters)
        players = port.m.s.players
        self.waves = {}
        self.backups = {}
        self.override_benched = set()
        self.original_ids = frozenset(self.starters.values())
        self.period_ms = port.config.period_seconds * 1000
        for team, roster in sorted(rosters.items()):
            # The engine also admits an eleventh field player at kickoff.
            # Coach windows apply to the ten ordered field starters.
            planned = [players[f'{team}:{a.source_id}'] for a in engine_order(roster)[:10]]
            waves = split_waves(planned, self.roster)
            self.waves[team] = tuple(tuple(p.id for p in wave) for wave in waves)
            for wave in waves:
                bench = [p for p in players.values() if p.team == team and p.role == 'field' and not p.active]
                for outgoing in wave:
                    backup, tier = select_substitute(outgoing, bench, self.roster)
                    if backup is not None:
                        self.backups[outgoing.id] = (backup.id, tier)
                        bench.remove(backup)

    def plan_record(self):
        return dict(waves=self.waves, backups=self.backups, rest_window_ms=REST_WINDOW_MS)

    def needs_rest(self, player):
        return player.fatigue <= REST_THRESHOLD or player.id in self.due

    def bench(self, team, role, reserved):
        engine = self.port.m.e
        return (p for p in engine.s.players.values() if p.team == team and p.role == role
                and not p.active and p.id not in self.original_ids and p.id not in reserved
                and engine.rb_can_enter(p))

    def rotate(self):
        # Most calls are during play. Check the restart before scanning players.
        port = self.port
        s = port.m.s
        restart = s.restart
        if (s.phase != port.types.Phase.DEAD or restart is None
                or restart.native_id == self.last_restart or restart.rs.get('formation')):
            return
        self.last_restart = restart.native_id
        wave = resting_wave(s.live_ms, self.period_ms, s.period)
        resting = set() if wave is None else {pid for waves in self.waves.values() for pid in waves[wave]}
        active = {(p.team, p.slot): p for p in s.players.values() if p.active}
        # Free planned backups before the next wave's outgoing changes. An
        # original returning after an override must meet the recovery threshold.
        for slot, starter in self.starters.items():
            outgoing, incoming = active.get(slot), s.players[starter]
            if (outgoing is None or incoming.active or starter in resting
                    or outgoing.role != 'field' or incoming.role != 'field'):
                continue
            overridden = starter in self.override_benched
            if incoming.fatigue <= REST_THRESHOLD or overridden and incoming.fatigue < RETURN_THRESHOLD:
                continue
            reason = 'override_return' if overridden else 'planned_return'
            if self.swap(outgoing, incoming, reason, 'starter_slot'):
                active[slot] = incoming
        reserved = {backup for pid in resting if s.players[pid].active
                    for backup, _ in (self.backups.get(pid, (None, None)),)}
        for slot, outgoing in active.items():
            plan = outgoing.id in resting
            override = self.needs_rest(outgoing)
            if not plan and not override:
                continue
            if outgoing.role == 'keeper':
                if (self.starters.get(slot) != outgoing.id
                        or self.regulation_ms[outgoing.id] < KEEPER_REGULATION_MIN_MS):
                    continue
            elif outgoing.role != 'field':
                continue
            backup_id, tier = self.backups.get(outgoing.id, (None, None)) if plan else (None, None)
            reserved.discard(backup_id)
            candidates = list(self.bench(outgoing.team, outgoing.role, reserved))
            incoming = next((p for p in candidates if not override and p.id == backup_id
                             and p.fatigue >= RETURN_THRESHOLD), None)
            if incoming is None:
                incoming, tier = self.choose(outgoing, candidates)
            if incoming is not None:
                self.swap(outgoing, incoming, 'energy_override' if override else 'planned_out', tier)

    def log_swap(self, outgoing, incoming, reason, tier):
        super().log_swap(outgoing, incoming, reason, tier, stamina=outgoing.a.endurance)
        if reason == 'energy_override' and outgoing.id in self.original_ids:
            self.override_benched.add(outgoing.id)
        self.override_benched.discard(incoming.id)
