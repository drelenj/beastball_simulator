"""SPRINT-45 authoritative possession / rules-state layer (pure; no simulator imports).

Implements the derived rules-state contract of
audit/HP-002_OWNER_DECISIONS_D1_RECORD.md section 3 (rows R-01..R-22) from
authoritative ball-contact facts only. It never reads athlete beliefs.
The tracker RECORDS violations (ZR-1, ZR-C, ZR-T) in its ledger; enforcing
the RST-1 restart is the caller's business.

PRIMITIVE notes (also listed in b1/sprint45/CANON_NOTES.md):
- PRIMITIVE: "touching the ball" is whatever the caller reports in `touching`
  and in 'touch' events; this module cannot check that source (D1 section 4.2).
- PRIMITIVE: ZR-C uses `holder_xy` (carrier body centre, G-6) when the caller
  supplies it, else the ball ground position as a proxy (flagged in the ledger).
- PRIMITIVE: ball_status loose_ground / loose_airborne are not distinguished
  (no height input); a loose ball is reported as 'loose_ground'.
"""
from dataclasses import dataclass
from math import hypot
from typing import Optional


class UnresolvedOutcome(Exception):
    """Raised for anything the decision record does not settle."""


@dataclass(frozen=True)
class RulesConfig:
    direct_possession_threshold_ms: int = 500     # P-1 (tested at 250/500/1000)
    keeper_zone_radius: float = 20.0              # G-5; inside = distance < R (G-3)
    zone_clock_limit_ms: int = 5000               # R-13
    ruleset: str = '1.0.2'
    goal_x: tuple = (('A', 0.0), ('B', 100.0))    # own-goal x per team; goal centre y = 50


@dataclass(frozen=True)
class PublicRulesState:
    ball_status: str
    direct_team: Optional[str]
    direct_holder: Optional[str]
    passive_team: Optional[str]
    contested: bool
    uncontested_ms: int
    team_control: Optional[str]
    last_toucher: Optional[str]
    zone_clock_ms: tuple
    zone_clock_running: tuple

    def phase(self, team):
        if self.passive_team is None:
            return 'none'
        return 'offense' if self.passive_team == team else 'defense'


class PossessionTracker:
    def __init__(self, config=RulesConfig()):
        self.cfg = config
        self.goal = dict(config.goal_x)
        self.teams = tuple(t for t, _ in config.goal_x)
        if len(self.teams) != 2:
            raise UnresolvedOutcome('exactly two teams are defined by the record')
        self.ledger = []
        self.now = None
        self.live = True
        self.ball_status = 'loose_ground'           # R-01: opening, no possession
        self.ball_xy = (50.0, 50.0)
        self.dp_team = self.dp_holder = self.pp = self.tc = self.last_toucher = None
        self.contested = False
        self.unc_team = None
        self.unc_start = None
        self.zone_start = {t: None for t in self.teams}     # None = not running
        self.zone_violated = {t: False for t in self.teams}
        self.passing = None                                  # deliberate pass under watch for ZR-T
        self.carry_inside = None                             # carrier inside own zone at last step
        self._step = []

    # ------------------------------------------------------------ geometry (G-1..G-6)
    def other(self, team):
        return self.teams[1] if team == self.teams[0] else self.teams[0]

    def in_zone(self, team, xy):
        return hypot(xy[0] - self.goal[team], xy[1] - 50.0) < self.cfg.keeper_zone_radius

    # ------------------------------------------------------------ ledger
    def _log(self, row, event, **data):
        e = {'t_ms': self.now, 'row': row, 'event': event}
        e.update(data)
        self.ledger.append(e)
        self._step.append(e)

    def _reset_clocks(self, trigger, team=None, stop=False):
        """R-14 (A5): zone clock to 0. stop=True also stops it until it may run again."""
        for t in ((team,) if team else self.teams):
            if self.zone_start[t] is not None:
                self._log('R-14', 'zone_clock_reset', team=t, trigger=trigger,
                          clock_ms=self.now - self.zone_start[t])
                self.zone_start[t] = None if stop else self.now
            self.zone_violated[t] = False

    def _uncontested_ms(self):
        return 0 if self.unc_start is None else self.now - self.unc_start

    def _defender_touch(self, player, team):
        """R-08 / U4-06: TC ends, zone clock resets, PP unchanged."""
        if self.passing:
            self.passing['defender_touched'] = True
        if self.tc is not None or self.zone_start[self.pp] is not None:
            self._log('R-08', 'defender_touch', player=player, team=team, passive_team=self.pp)
        self.tc = None
        self._reset_clocks('defender_touch', self.pp)

    def _teammate_first_touch(self, player, team, contested):
        """R-12 / U4-01..03: ZR-T on a teammate's first touch of a deliberate pass."""
        p = self.passing
        if p is None or team != p['team'] or player == p['passer']:
            return
        self.passing = None
        if contested:
            self._log('R-22', 'same_instant_touch_no_ZR-T', player=player, team=team)
            return
        if p['was_outside'] and not p['defender_touched'] and self.in_zone(team, self.ball_xy):
            self._log('R-12', 'violation', violation='ZR-T', team=team, player=player,
                      restart='RST-1', awarded_to=self.other(team))

    # ------------------------------------------------------------ main step
    def step(self, now_ms, touching, ball_xy, events=(), holder_xy=None):
        if self.now is not None and now_ms < self.now:
            raise ValueError('time went backwards')
        self.now = now_ms
        self.ball_xy = (float(ball_xy[0]), float(ball_xy[1]))
        self._step = []
        touch_teams = set(touching.values())
        event_touches = []
        for ev in events:
            kind = ev['kind']
            if kind == 'touch':
                event_touches.append((ev['player'], ev['team']))
                touch_teams.add(ev['team'])
            elif kind == 'pass_release':                       # R-06
                self.dp_team = self.dp_holder = None
                self.unc_team = self.unc_start = None
                self.tc = ev['team']
                self.last_toucher = ev['player']
                self.ball_status = 'pass_in_flight'
                self.passing = {'team': ev['team'], 'passer': ev['player'], 'defender_touched': False,
                                'was_outside': not self.in_zone(ev['team'], self.ball_xy)}   # U4-04
                self._log('R-06', 'pass_release', player=ev['player'], team=ev['team'], passive_team=self.pp)
            elif kind == 'shot_release':                       # R-07
                self.dp_team = self.dp_holder = None
                self.unc_team = self.unc_start = None
                self.tc = None
                self.passing = None
                self.last_toucher = ev['player']
                self.ball_status = 'shot_in_flight'
                self._log('R-07', 'shot_release', player=ev['player'], team=ev['team'], passive_team=self.pp)
            elif kind == 'loose':                              # R-09 (U4-05 forced release)
                self.dp_team = self.dp_holder = self.tc = None
                self.unc_team = self.unc_start = None
                self.passing = None
                self.ball_status = 'loose_ground'
                self._log('R-09', 'loose', passive_team=self.pp)
            elif kind == 'out_of_play':                        # R-18 (+ dead ball R-20)
                self.live = False
                self.dp_team = self.dp_holder = self.tc = None
                self.unc_team = self.unc_start = None
                self.passing = None
                self.contested = False
                self.ball_status = 'out_of_play'
                self._log('R-18', 'out_of_play', passive_team=self.pp)
                self._reset_clocks('dead_ball', stop=True)
            elif kind == 'dead':                               # R-20 / U4-10
                self.live = False
                self.dp_team = self.dp_holder = self.tc = None
                self.unc_team = self.unc_start = None
                self.passing = None
                self.contested = False
                self.ball_status = 'restart_pending'
                self._log('R-20', 'dead', passive_team=self.pp)
                self._reset_clocks('dead_ball', stop=True)
            elif kind == 'restart_awarded':                    # R-18 / R-19 / P-3
                team = ev['team']
                changed = self.pp != team
                self.live = False
                self.pp = team
                self.dp_team = self.dp_holder = None
                self.unc_team = self.unc_start = None
                self.passing = None
                self.contested = False
                self.tc = team                                 # P-4: carried / deliberate pass sub-state
                self.ball_status = 'restart_pending'
                self._log('R-19' if ev.get('rst1') else 'R-18', 'restart_awarded', team=team, pp_changed=changed)
                self._reset_clocks('restart', stop=True)
            elif kind == 'restart_release':
                self.live = True
                self.ball_status = 'pass_in_flight'
                self._log('R-14', 'restart_release', team=ev['team'])
                self._reset_clocks('restart', stop=True)
            elif kind == 'live':
                self.live = True
                if self.ball_status in ('restart_pending', 'out_of_play'):
                    self.ball_status = 'loose_ground'
            else:
                raise UnresolvedOutcome('unknown rules event: %r' % (kind,))

        both = len(touch_teams) >= 2
        for player, team in event_touches:
            self.last_toucher = player
            if both:
                continue
            if self.pp is not None and team != self.pp:
                self._defender_touch(player, team)
            else:
                self._teammate_first_touch(player, team, False)

        if both:                                               # R-04 / R-22 / C-1 / C-3
            if not self.contested:
                self._log('R-22' if event_touches else 'R-04', 'contested', players=sorted(touching),
                          passive_team=self.pp)
                if self.passing:
                    self.passing = None                        # U4-12: counted as a defender touch
                self.tc = None
                if self.pp is not None:
                    self._reset_clocks('defender_touch', self.pp)
            self.contested = True
            self.dp_team = self.dp_holder = None
            self.unc_team = self.unc_start = None
            self.ball_status = 'loose_ground'
            if touching:
                self.last_toucher = sorted(touching)[0]
        elif touching:
            team = next(iter(touch_teams & set(touching.values())))
            holder = sorted(touching)[0]
            self.last_toucher = holder
            if self.contested:                                 # R-05
                self.contested = False
                self.unc_team = self.unc_start = None
                self._log('R-05', 'contest_ended', team=team)
            if self.unc_team != team:                          # R-02: timer starts at 0
                self.unc_team, self.unc_start = team, now_ms
                self._log('R-02', 'secured', team=team, player=holder, passive_team=self.pp)
                if self.pp is not None and team != self.pp:
                    self._defender_touch(holder, team)
                else:
                    self._teammate_first_touch(holder, team, False)
            if self.dp_team != team and self._uncontested_ms() >= self.cfg.direct_possession_threshold_ms:
                self.dp_team = team                            # R-03
                self._log('R-03', 'direct_possession', team=team, player=holder,
                          uncontested_ms=self._uncontested_ms())
                self.passing = None
                self.carry_inside = None
                if self.pp != team:                            # R-10 / first possession (P-3)
                    self._log('R-10' if self.pp is not None else 'R-03', 'passive_possession',
                              team=team, previous=self.pp)
                    self.pp = team
                    self._reset_clocks('passive_possession_change', stop=True)
            if self.dp_team == team:
                self.dp_holder = holder
                self.tc = team
                self.ball_status = 'carried'
                pos = holder_xy if holder_xy is not None else self.ball_xy
                inside = self.in_zone(team, pos)
                if self.carry_inside is False and inside:      # R-11 / ZR-C
                    self._log('R-11', 'violation', violation='ZR-C', team=team, player=holder,
                              restart='RST-1', awarded_to=self.other(team),
                              primitive_ball_proxy=holder_xy is None)
                self.carry_inside = inside
        else:
            if self.contested:
                self.contested = False
                self._log('R-05', 'contest_ended', team=None)
            self.unc_team = self.unc_start = None
            if self.dp_team is not None:                       # control ended without a release event
                self.dp_team = self.dp_holder = self.tc = None
                self.ball_status = 'loose_ground'
                self._log('R-09', 'loose', passive_team=self.pp, inferred=True)

        if self.passing and not self.in_zone(self.passing['team'], self.ball_xy):
            self.passing['was_outside'] = True                 # U4-03: left the zone after release

        for t in self.teams:                                   # R-13 / R-14 zone clock
            should = self.live and self.pp == t and self.in_zone(t, self.ball_xy)   # G-2, U4-11
            if should and self.zone_start[t] is None:
                self.zone_start[t] = now_ms
                self.zone_violated[t] = False
            elif not should and self.zone_start[t] is not None:
                self._reset_clocks('ball_left_zone' if self.live and self.pp == t else 'not_running', t, stop=True)
            if (self.zone_start[t] is not None and not self.zone_violated[t]
                    and now_ms - self.zone_start[t] >= self.cfg.zone_clock_limit_ms):
                self.zone_violated[t] = True
                self._log('R-13', 'violation', violation='ZR-1', team=t, restart='RST-1',
                          awarded_to=self.other(t), clock_ms=now_ms - self.zone_start[t])
        return list(self._step)

    # ------------------------------------------------------------ queries
    def public(self):
        now = self.now or 0
        return PublicRulesState(
            self.ball_status, self.dp_team, self.dp_holder, self.pp, self.contested,
            self._uncontested_ms() if self.now is not None else 0, self.tc, self.last_toucher,
            tuple((t, 0 if self.zone_start[t] is None else now - self.zone_start[t]) for t in self.teams),
            tuple((t, self.zone_start[t] is not None) for t in self.teams))

    def keeper_protected(self, keeper_team, keeper_xy):
        """R-15 / R-16, KP-13(a), KP-14: no opponent-initiated contact only while the
        Keeper's team has passive possession and he is inside his own zone right now."""
        return self.pp == keeper_team and self.in_zone(keeper_team, keeper_xy)

    def freeze_legal(self, target_team, target_role, target_xy):
        """R-17 (ruleset 1.0.2): any eligible player is freezable; a Keeper inside his
        own zone is never frozen (KP-13(b)); R-01: empty target set before first possession."""
        if self.cfg.ruleset != '1.0.2':
            raise UnresolvedOutcome('freeze eligibility is only settled for ruleset 1.0.2 in B1')
        if target_role not in ('field', 'keeper'):
            raise UnresolvedOutcome('freeze eligibility of role %r is not in the decision record' % (target_role,))
        if self.pp is None:
            return False
        return not (target_role == 'keeper' and self.in_zone(target_team, target_xy))
