"""Report fields (engine log only; no rule change). Rulebook ports only.

- carry_outcome: every carry attempt ends as goal, tackled, grounded, turnover or stopped_short.
- foul_award events carry origin_foul (reason, actor, victim) of the foul that produced them.
- rb_discipline rulings carry the offence reason that produced them (so every DQ has one).
- arrow_outcome: each arrow ends as hit (froze its target), hit_other (froze another
  player), inert (struck a player without a freeze), ball, or miss.
"""

OWN = ('carry_outcome', 'arrow_outcome')


def install(co, cfg):
    E = co.engine.Engine
    old_init, old_emit, old_foul, old_score = E.__init__, E.emit, E.foul, E.add_score
    old_carry, old_publish, old_impact = E.rb_carry_attempt, E.rb_publish, E.arrow_impact

    def init(self, *a, **kw):
        old_init(self, *a, **kw)
        self.rb_open_carry = None; self.rb_foul_context = None
    E.__init__ = init

    def close_carry(self, outcome, ended_by):
        c = self.rb_open_carry
        if c is None: return
        self.rb_open_carry = None
        old_emit(self, 'carry_outcome', 'RB-3.3-report', player=c['player'], team=c['team'], started_ms=c['t_ms'],
                 outcome=outcome, ended_by=ended_by)

    def emit(self, event, rule, **data):
        seq = old_emit(self, event, rule, **data)
        if event in OWN or getattr(self, 'rb_open_carry', None) is None and event != 'arrow_miss':
            return seq
        if event == 'arrow_miss':
            old_emit(self, 'arrow_outcome', 'RB-3.3-report', arrow=data.get('arrow'), outcome='miss')
            return seq
        c = self.rb_open_carry
        if event == 'goal':
            close_carry(self, 'goal' if data.get('method') == 'carry' and data.get('team') == c['team'] else 'stopped_short', 'goal')
        elif event == 'tackle_count' and data.get('target') == c['player']:
            close_carry(self, 'tackled', event)
        elif event == 'c3_grounding' and c['player'] in (data.get('player'), data.get('target')):
            close_carry(self, 'grounded', event)
        elif event in ('strip', 'boundary', 'possession') or event == 'restart_awarded' and data.get('team') != c['team']:
            close_carry(self, 'turnover', event)
        elif event in ('release', 'restart_awarded', 'period_end', 'freeze', 'discipline', 'rb_discipline'):
            if event != 'release' or data.get('player') == c['player'] or self.s.ball.carrier != c['player']:
                close_carry(self, 'stopped_short', event)
        return seq
    E.emit = emit

    def carry(self, holder, *a, **kw):
        result = old_carry(self, holder, *a, **kw)
        if result:
            close_carry(self, 'stopped_short', 'new_attempt')
            self.rb_open_carry = dict(player=holder.id, team=holder.team, t_ms=self.s.now)
        return result
    E.rb_carry_attempt = carry

    def foul(self, actor, victim=None, reason='hold', *a, **kw):
        previous = self.rb_foul_context
        self.rb_foul_context = dict(reason=reason, actor=actor, victim=victim, t_ms=self.s.now)
        try:
            return old_foul(self, actor, victim, reason, *a, **kw)
        finally:
            self.rb_foul_context = previous
    E.foul = foul

    def add_score(self, team, points, kind, **data):
        if kind in ('half_goal', 'full_goal_award') and self.rb_foul_context:
            data['origin_foul'] = dict(self.rb_foul_context)
        return old_score(self, team, points, kind, **data)
    E.add_score = add_score

    def publish(self, row):
        if row.get('kind') == 'discipline' and 'offence' not in row:
            row['offence'] = dict(self.rb_foul_context) if self.rb_foul_context else None
        return old_publish(self, row)
    E.rb_publish = publish

    def impact(self, arrow_id, target, panel=True, kind='player'):
        ar = next((a for a in self.s.arrows if a.id == arrow_id), None)
        before = sum(1 for r in self.log if r['event'] == 'freeze' and r['data'].get('arrow') == arrow_id)
        result = old_impact(self, arrow_id, target, panel, kind)
        froze = sum(1 for r in self.log[-8:] if r['event'] == 'freeze' and r['data'].get('arrow') == arrow_id) > 0 or before
        if kind == 'ball' or target == 'ball':
            outcome = 'ball'
        elif froze:
            outcome = 'hit' if ar is not None and target == ar.target else 'hit_other'
        else:
            outcome = 'inert'
        old_emit(self, 'arrow_outcome', 'RB-3.3-report', arrow=arrow_id, shooter=getattr(ar, 'shooter', None),
                 intended=getattr(ar, 'target', None), struck=target, outcome=outcome)
        return result
    E.arrow_impact = impact
