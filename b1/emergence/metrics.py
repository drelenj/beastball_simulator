"""EMERGENCE-1 descriptive match metrics. Read-only on the port; no RNG; never
influences a match. PRIMITIVE: positions are sampled once per 1000 ms of live play
from authoritative state (this is measurement, not cognition)."""
from collections import Counter
from math import hypot

TEAMS = ('A', 'B')
BINS = ('<8', '8-16', '16-24', '>=24')


def _r(v):
    return None if v is None else round(float(v), 3)


def _mean(xs):
    return _r(sum(xs) / len(xs)) if xs else None


class MetricsCollector:
    def __init__(self, sample_ms=1000):
        self.sample_ms, self.next_ms, self.samples = sample_ms, None, 0
        self.acc = {t: {k: [] for k in ('width', 'depth', 'centroid_ball_dist', 'mean_x_attack', 'spread_nn')} for t in TEAMS}
        self.poss = Counter()
        self.kinds = {t: Counter() for t in TEAMS}
        self.press = {t: [] for t in TEAMS}

    # ---- hooks -------------------------------------------------------------
    def on_decision(self, port, view, intent):
        try:
            t = view.team
            self.kinds[t][intent.kind] += 1
            if intent.kind == 'press' and intent.aim is not None:
                self.press[t].append(hypot(intent.aim[0] - view.x, intent.aim[1] - view.y))
        except Exception:
            pass

    def on_step(self, port):
        try:
            s = port.m.s
            if getattr(s.phase, 'value', s.phase) != 'live':
                return
            if self.next_ms is not None and s.now < self.next_ms:
                return
            self.next_ms = s.now + self.sample_ms
            self.samples += 1
            self.poss[port.rules.public().passive_team or 'none'] += 1
            b = s.ball
            for t in TEAMS:
                f = [(p.x, p.y) for p in s.players.values() if p.active and p.team == t and p.role == 'field']
                if len(f) < 2:
                    continue
                xs, ys = [q[0] for q in f], [q[1] for q in f]
                cx, cy = sum(xs) / len(f), sum(ys) / len(f)
                a = self.acc[t]
                a['width'].append(max(ys) - min(ys))
                a['depth'].append(max(xs) - min(xs))
                a['centroid_ball_dist'].append(hypot(cx - b.x, cy - b.y))
                a['mean_x_attack'].append(abs(cx - s.ends[t]))
                a['spread_nn'].append(sum(min(hypot(q[0] - o[0], q[1] - o[1]) for j, o in enumerate(f) if j != i)
                                          for i, q in enumerate(f)) / len(f))
        except Exception:
            pass

    # ---- result ------------------------------------------------------------
    def finalize(self, port):
        errors = []

        def safe(name, fn):
            try:
                return fn()
            except Exception:
                errors.append(name)
                return None

        s, log = port.m.s, port.m.e.log
        team = lambda pid: s.players[pid].team
        by = lambda ev: [r for r in log if r.get('event') == ev]
        out = {}
        for t in TEAMS:
            o = {k: _mean(v) for k, v in self.acc[t].items()}
            o['possession_share'] = _r(self.poss[t] / self.samples) if self.samples else None
            cmd_team = lambda cid: team(cid.split('/')[2])

            def passes():
                st = Counter(x.status.split(':')[0] for x in port.outcomes
                             if x.command_id and x.status.startswith('pass_') and cmd_team(x.command_id) == t)
                return {'pass_completed': st['pass_completed'] + st['pass_completed_other'],
                        'pass_intercepted': st['pass_intercepted'], 'pass_out': st['pass_dead']}

            def releases():
                rr = [x for x in port.release_records if x.get('status') == 'released' and cmd_team(x['command_id']) == t]
                ln = [hypot(x['semantic_aim'][0] - x['release_origin'][0], x['semantic_aim'][1] - x['release_origin'][1]) for x in rr]
                hist = dict.fromkeys(BINS, 0)
                for d in ln:
                    hist[BINS[0] if d < 8 else BINS[1] if d < 16 else BINS[2] if d < 24 else BINS[3]] += 1
                net = Counter(f"{s.players[x['command_id'].split('/')[2]].slot}>{s.players[x['target']].slot}" for x in rr)
                return {'pass_released': len(rr), 'pass_len_mean': _mean(ln), 'pass_len_hist': hist,
                        'pass_network': dict(sorted(net.items(), key=lambda kv: (-kv[1], kv[0]))[:12])}

            o.update(safe(t + '.passes', passes) or {'pass_completed': None, 'pass_intercepted': None, 'pass_out': None})
            o.update(safe(t + '.releases', releases) or {'pass_released': None, 'pass_len_mean': None, 'pass_len_hist': None, 'pass_network': None})
            o['press_dist_mean'] = _mean(self.press[t])
            o['decisions_by_kind'] = dict(sorted(self.kinds[t].items()))
            o['shots'] = safe(t + '.shots', lambda: sum(1 for r in by('release') if r['data'].get('kind') == 'shot' and team(r['data']['player']) == t))

            def goals():
                g = [r['data'] for r in by('goal') if r['data'].get('team') == t]
                return dict(sorted(Counter(str(d.get('method')) for d in g).items())), sum(int(d.get('points') or 0) for d in g)

            g = safe(t + '.goals', goals)
            o['goals'], o['points'] = g if g else (None, None)
            o['arrows'] = safe(t + '.arrows', lambda: sum(1 for r in by('arrow_release') if team(r['data']['player']) == t))
            o['freezes_caused'] = safe(t + '.freezes', lambda: sum(1 for r in by('freeze') if team(r['data']['player']) != t))
            o['turnovers_lost'] = safe(t + '.turnovers', lambda: sum(1 for r in by('possession_change')
                                                                      if r['data'].get('previous') == t and r['data'].get('team') != t))
            out[t] = o
        ra = by('restart_awarded')
        out['match'] = {
            'samples': self.samples,
            'possession_none_share': _r(self.poss['none'] / self.samples) if self.samples else None,
            'restarts_by_reason': safe('restarts', lambda: dict(sorted(Counter(str(r['data'].get('reason')) for r in ra).items()))),
            'stoppages': len(ra),
            'fouls_by_reason': safe('fouls', lambda: dict(Counter(str(r['data'].get('reason')) for r in by('foul')).most_common(8))),
            'zone_violations': safe('zone', lambda: dict(sorted(Counter(str(e.get('violation')) for e in port.rules.ledger
                                                                         if e.get('event') == 'violation').items()))),
            'release_records_capped': len(port.release_records) >= 400,
            'metric_errors': errors,
        }
        return out
