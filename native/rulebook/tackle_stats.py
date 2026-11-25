"""Count explicit drive commitments on witnessed carrier holds."""
from collections import defaultdict


class TackleWitness:
    def __init__(self, match):
        self.drives = {}
        contain = match.c3_contain

        def observe(defender, carrier):
            holding_up = contain(defender, carrier)
            if not holding_up:
                pair = defender.id, carrier.id
                hold = match.c3_holds.get(pair)
                intent = getattr(defender, 'native_intent', None)
                if hold is not None and intent is not None and intent.contact == 'takedown':
                    key = (*pair, round(hold['start'], 3))
                    self.drives.setdefault(key, match.s.now)
            return holding_up

        match.c3_contain = observe

    def totals(self, events):
        starts = set()
        ends = {}
        groundings = defaultdict(list)
        for row in events:
            event, data = row['event'], row['data']
            if event == 'c3_hold_start':
                starts.add((data['actor'], data['target'], data['start_ms']))
            elif event == 'c3_hold_end':
                ends[(data['actor'], data['target'], data['start_ms'])] = data
            elif event == 'tackle_count':
                groundings[data['actor'], data['target']].append(row['t_ms'])
        for actor, target, start in sorted(starts & self.drives.keys()):
            drive = max(start, self.drives[actor, target, start])
            closed = ends.get((actor, target, start))
            end = closed['end_ms'] if closed else float('inf')
            # Integration may probe a future hold and roll it back. Credit only
            # holds actually published by the kernel, during their live interval.
            if drive < end:
                made = (closed is not None and closed['cause'] == 'carrier_grounded'
                        and any(abs(at - end) <= 1 for at in groundings[actor, target]))
                yield actor, made
