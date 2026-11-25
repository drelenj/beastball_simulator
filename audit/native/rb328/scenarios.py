"""Print the RB-3.28 held-sprint, recovery and technique scenarios as JSON."""
import json

from native.rulebook.fatigue_rotation import (REST_THRESHOLD, parameters, reserve_after,
                                               technique)


if __name__ == '__main__':
    sprint_times = (0, 30, 60, 90)
    recovery_times = (0, 30, 60, 90, 120)
    out = {'constants': parameters(), 'held_sprint': {}, 'standing_recovery': {},
           'bench_recovery': {t: reserve_after(.6, 0., 0., t, bench=True) for t in recovery_times},
           'technique_at_reserve_0.60': {r: technique(r, .60) for r in (.50, .95)}}
    for rating in (.60, .70, .85, 1.):
        loss = 1 - reserve_after(1., rating, 1., 1.)
        out['held_sprint'][rating] = {
            'reserve': {t: reserve_after(1., rating, 1., t) for t in sprint_times},
            'seconds_to_0.60': (1 - REST_THRESHOLD) / loss,
        }
        out['standing_recovery'][rating] = {
            t: reserve_after(.60, rating, 0., t) for t in recovery_times}
    print(json.dumps(out, indent=2, sort_keys=True))
