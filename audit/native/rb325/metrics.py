"""Scoring and pass witnesses shared by diagnosis and calibration."""
from collections import Counter

from native.rulebook.rb31_soak import measure


def observe_carries(port):
    engine = port.m.e
    rows = []
    original = engine.rb_carry_attempt

    def observed(holder, *args, **kwargs):
        attempted = original(holder, *args, **kwargs)
        if attempted:
            rows.append((engine.s.now, holder.team))
        return attempted

    engine.rb_carry_attempt = observed
    return rows


def add_metrics(result, port, carries=None):
    e = port.m.e
    if carries is None:
        carries = [(row['t_ms'], row['data']['team']) for row in e.log
               if row['event'] == 'carry_attempt' and 'team' in row['data']]
    result.update(measure(port, carries))
    shots = Counter(row['team'] for row in e.rb_attempts if row['shot_attempt'])
    passes = Counter()
    complete = Counter()
    pending = None
    for row in e.log:
        data, event = row['data'], row['event']
        if event == 'release':
            player = e.s.players.get(data.get('player'))
            pending = player.team if player and data.get('kind') == 'pass' else None
            if pending:
                passes[pending] += 1
        elif event == 'control' and pending:
            player = e.s.players.get(data.get('player'))
            if player and player.team == pending:
                complete[pending] += 1
            pending = None
        elif event in ('boundary', 'goal', 'restart_awarded', 'restart_release', 'period_end'):
            pending = None
    result['shots'] = {t: shots[t] for t in ('A','B')}
    result['open_passes'] = {t: {'released': passes[t], 'completed': complete[t],
                                 'rate': complete[t] / passes[t] if passes[t] else None} for t in ('A','B')}
