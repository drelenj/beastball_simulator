"""PROVISIONAL (owner canon ruling 17 Nov 2026): period starts by coin flip.

Replaces the opening Hunt at every period start, rulebook ports only.
- One seeded coin flip at the start of the match (own RNG stream, driven by the
  match seed) decides the first offence. The winner starts periods 1 and 4 on
  offence; the loser starts periods 2 and 3.
- Each start is the same restart as after a score: snap40 at the offence's own
  40, y = 50 (same snap window, offside rules and Keeper snap).
- If overtime is needed, a second flip from the same stream decides the first
  overtime period. Later overtime periods alternate the starting team
  (PLACEHOLDER, see QUESTIONS_FOR_OWNER.md Q-RB33-1).
- hunt_cleared becomes true when the first snap of the period is released.
The Hunt code itself is kept (E.rb_open_hunt) but no longer used at period starts.
"""
import random
from b1.possession import PossessionTracker, RulesConfig

COIN_STREAM = 'beastball/rb/period-start-coin/{seed}'


def coin(rng):
    return 'A' if rng.random() < .5 else 'B'


def offence_for(period, first_winner, ot_winner):
    """Starting offence for a period. Pure; used by the engine and by tests."""
    loser = 'B' if first_winner == 'A' else 'A'
    if period in (1, 4):
        return first_winner
    if period in (2, 3):
        return loser
    if ot_winner is None:
        raise ValueError('overtime flip not taken')
    other = 'B' if ot_winner == 'A' else 'A'
    return ot_winner if (period - 5) % 2 == 0 else other


def install(co, cfg):
    E, T = co.engine.Engine, co.types
    P = T.Phase
    old_init, old_hunt, old_timers, old_restart = E.__init__, E.begin_hunt, E.resolve_timers, E.restart_release

    def init(self, *a, **kw):
        old_init(self, *a, **kw)
        seed = self.config.get('seed') if isinstance(self.config, dict) else None
        if seed is None:
            raise RuntimeError('period-start coin flip needs the match seed')
        self.rb_coin = random.Random(COIN_STREAM.format(seed=seed))
        self.rb_flip = dict(first=None, overtime=None)
        self.rb_period_start_open = False
    E.__init__ = init

    E.rb_open_hunt = old_hunt          # kept for any other use; not used at period starts

    def period_start(self):
        s = self.s
        if self.rb_flip['first'] is None:
            self.rb_flip['first'] = coin(self.rb_coin)
            self.emit('coin_flip', 'RB-3.3', purpose='first_offence', winner=self.rb_flip['first'], period=s.period)
        if s.period > cfg.periods and self.rb_flip['overtime'] is None:
            self.rb_flip['overtime'] = coin(self.rb_coin)
            self.emit('coin_flip', 'RB-3.3', purpose='first_overtime', winner=self.rb_flip['overtime'], period=s.period)
        team = offence_for(s.period, self.rb_flip['first'], self.rb_flip['overtime'])
        # Period reset formerly done by begin_hunt, without the Hunt itself.
        self.close_restart('period_end')
        s.restart = s.recovery = s.reconstruction = None
        s.owner = None; s.possession_ms = cfg.play_clock_ms; s.tackle_count = 0
        s.opening_contestants = (); s.opening_touched = False; s.opening_deadline = None
        self.hunt_claims = {}; self.hunt_cleared = False; self.dribbles.clear()
        self.possession_history.extend(self.possession.ledger)
        self.possession = PossessionTracker(RulesConfig(cfg.direct_ms, cfg.zone_radius, goal_x=tuple(s.ends.items())))
        self.freezes.clear()
        for q in s.quivers.values():
            q.allocation = cfg.arrows; q.spent = 0; q.loaded = cfg.arrows
        self.rb_hunt_running = False
        self.emit('period_start', 'RB-3.3', period=s.period, offence=team)
        self.award(team, s.ends[team] + s.attack_sign(team) * 40, 50, 'period_start', fresh=True, normalize=False)
        self.rb_period_start_open = True
    E.begin_hunt = period_start

    def timers(self):
        # No Hunt: the hunt-clear test (ball 5 m from centre) must not fire before the snap.
        if self.rb_period_start_open and not self.hunt_cleared:
            self.hunt_cleared = True
            try:
                return old_timers(self)
            finally:
                if self.rb_period_start_open:
                    self.hunt_cleared = False
        return old_timers(self)
    E.resolve_timers = timers

    def restart_release(self, pid, velocity, *a, **kw):
        # The first snap of the period, including a retake of it (offside, snap timeout).
        opening = self.rb_period_start_open
        ok = old_restart(self, pid, velocity, *a, **kw)
        if ok and opening:
            self.rb_period_start_open = False
            self.hunt_cleared = True
            self.emit('hunt_cleared', 'RB-3.3', by='period_start_snap')
        return ok
    E.restart_release = restart_release
