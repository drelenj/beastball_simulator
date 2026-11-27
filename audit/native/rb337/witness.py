"""Observe fumble causes and evasion outcomes without changing the match."""
from bisect import bisect_right
from collections import Counter, defaultdict


def band(rating):
    if rating is None:
        return 'unknown'
    if rating < .60:
        return '<.60'
    if rating < .70:
        return '.60–.69'
    if rating < .80:
        return '.70–.79'
    return '≥.80'


class Witness:
    def __init__(self, driver, rosters):
        port, ledger = driver.port, driver.stats_ledger
        self.port = port
        engine, state = port.m.e, port.m.s
        self.handling = {f'{team}:{a.source_id}':dict(a.values)['ball_handling']
                         for team,roster in rosters.items() for a in roster.athletes}
        self.moves = defaultdict(Counter)
        self.dodges = {}
        self.blame = {}
        self.drops = []
        self.flight = None
        previous_emit, submit, step, possessions = engine.emit, port.submit, port.step, ledger.possessions

        def saved_possessions(scores, blame):
            result = possessions(scores,blame)
            self.blame = blame.copy()
            return result

        def observed_submit(intent):
            result = submit(intent)
            if result['status']=='accepted' and intent.kind=='carry' and intent.technique in ('juke','spin'):
                self.moves[intent.technique]['attempts'] += 1
                self.dodges.setdefault(intent.athlete,[]).append((intent.technique,state.live_ms+500))
            return result

        def observed_step():
            step()
            for player, moves in tuple(self.dodges.items()):
                if state.ball.carrier != player:
                    del self.dodges[player]
                    continue
                live = state.live_ms
                for technique,until in moves:
                    if live>=until:
                        self.moves[technique]['successes'] += 1
                self.dodges[player] = [(technique,until) for technique,until in moves if live<until]
                if not self.dodges[player]:
                    del self.dodges[player]

        def emit(event, rule, **data):
            now = state.now
            if event in ('release','restart_release'):
                kind = data.get('kind','pass' if event=='restart_release' else None)
                pid = data.get('player',data.get('taker'))
                self.flight = (pid,data.get('target'),[]) if kind=='pass' else None
                if kind=='loose' and data.get('forced'):
                    self.dodges.pop(pid,None)
            elif event=='handoff_fumble':
                self.dodges.pop(data['giver'],None)
            elif event=='touch' and self.flight and data.get('player')==self.flight[1]:
                self.flight[2].append(now)
            elif event=='control':
                receiver = data['player']
                if self.flight:
                    passer,target,touches = self.flight
                    if touches and receiver[0]!=passer[0]:
                        self.drops.append(dict(ms=now,player=target,touch_ms=touches[-1]))
                self.flight = None
            elif event in ('boundary','restart_awarded','period_end'):
                self.flight = None
                if event!='boundary':
                    self.dodges.clear()
            if event in ('truck','stiff_arm'):
                self.moves[event]['attempts'] += 1
            elif event=='truck_broken':
                self.moves['truck']['successes'] += 1
            elif event=='stiff_arm_effect' and data.get('impulse_Ns',0)>0:
                self.moves['stiff_arm']['successes'] += 1
            return previous_emit(event,rule,**data)

        ledger.possessions, port.submit, port.step, engine.emit = saved_possessions, observed_submit, observed_step, emit

    def result(self,box):
        log = self.port.m.e.log
        collisions, holds, losses = defaultdict(list), defaultdict(list), defaultdict(list)
        causes_at = {}
        for row in log:
            event,d,at = row['event'],row['data'],row['t_ms']
            if event=='c3_collision':
                for player in (d['a'],d['b']):
                    collisions[player].append(at)
            elif event=='c3_hold_end' and d.get('peak_grip',0)>0:
                holds[d['target']].append(at)
            elif event=='release' and d.get('kind')=='loose' and d.get('forced'):
                losses[d['player'],'fumble'].append((at,row['id'],'other'))
            elif event=='handoff_fumble':
                losses[d['giver'],'fumble'].append((at,row['id'],'handoff'))
            elif event=='strip':
                losses[d['target'],'strip'].append((at,row['id'],'strip attempt'))
                causes_at[at,d['target']] = ('strip attempt','strip event')
            elif event=='freeze' and d.get('was_carrier'):
                causes_at[at,d['player']] = ('other','freeze of carrier')
            elif event=='grounded':
                causes_at.setdefault((at,d['player']),('wrap/takedown','grounding'))
        loss_times = {key:[item[0] for item in rows] for key,rows in losses.items()}
        timeline = sorted(self.blame)
        fumbles, supplemental = [], []
        for pos,nxt in zip(box['possessions'],box['possessions'][1:]):
            reason = pos['end_reason']
            if reason=='fumble' or reason=='strip':
                index = bisect_right(timeline,nxt['start_ms'])-1
                at = timeline[index] if index>=0 else None
                entry = self.blame.get(at)
                pid = entry[0] if entry else None
                source = losses.get((pid,reason),())
                release_index = bisect_right(loss_times.get((pid,reason),()),at)-1 if at is not None else -1
                cause, detail, event_id, loss_ms = 'other', 'unlinked ledger attribution', None, None
                if release_index>=0 and source[release_index][0]>=pos['start_ms']:
                    loss_ms,event_id,cause = source[release_index]
                    detail = 'loss event'
                    if cause=='other':
                        cause,detail = causes_at.get((loss_ms,pid),('other','unresolved forced release'))
                        if detail=='unresolved forced release':
                            if any(-1<=loss_ms-t<=100 for t in holds[pid]):
                                cause,detail = 'wrap/takedown','grip ended near release'
                            elif any(-1<=loss_ms-t<=100 for t in collisions[pid]):
                                cause,detail = 'collision without grip','contact near release'
                datum = dict(team=pos['team'],player=pid,cause=cause,detail=detail,
                             witness_ms=at,loss_ms=loss_ms,event_id=event_id,
                             possession_start_ms=pos['start_ms'],possession_end_ms=nxt['start_ms'],
                             ball_handling=self.handling.get(pid),band=band(self.handling.get(pid)))
                (fumbles if reason=='fumble' else supplemental).append(datum)
        for drop in self.drops:
            pos = next((a for a,b in zip(box['possessions'],box['possessions'][1:])
                        if a['start_ms']<=drop['touch_ms']<=drop['ms']<=b['start_ms']<=drop['ms']+1000
                        and a['team']==drop['player'][0] and b['team']!=a['team']),None)
            if pos:
                supplemental.append(drop | dict(team=pos['team'],cause='reception drop',
                    band=band(self.handling.get(drop['player'])),ball_handling=self.handling.get(drop['player'])))
        return dict(fumbles=fumbles,supplemental_losses=supplemental,evasion=self.moves)
