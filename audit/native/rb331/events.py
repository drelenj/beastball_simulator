"""Join diagnostic witnesses to adjudicated events outside the simulation."""
from bisect import bisect_left, bisect_right
from collections import defaultdict
from math import hypot

from native.rulebook.ball_material import params, path

INTERVAL_ENDS = {'boundary', 'restart_awarded', 'period_end', 'goal'}
ZONE_REASONS = {'ZR-C', 'ZR-T', 'ZR-1', 'zone_unmarked', 'zone_residence'}
MANEUVERS = {'juke', 'spin', 'hurdle', 'stiff_arm', 'truck'}


def shot_on_target(origin, velocity, gx, cfg, radius):
    forecast = path((*origin,*velocity), params(cfg), radius, 3., .010)
    plane = gx + (radius if gx == 100 else -radius)
    for p, q in zip(forecast, forecast[1:]):
        if min(p[1],q[1]) <= plane <= max(p[1],q[1]) and p[1] != q[1]:
            fraction = (plane-p[1])/(q[1]-p[1])
            y,z = (p[i]+fraction*(q[i]-p[i]) for i in (2,3))
            return hypot(y-50.,z)+radius <= cfg.goal_radius
    return False


def end_flight(flight, touches, won, witness):
    if not flight or flight['data'].get('kind') != 'shot' or flight['id'] not in witness.release:
        return None
    (origin,_,_,_,keeper,_), aim, _, gx = witness.release[flight['id']]
    velocity = flight['data']['velocity']
    cfg = witness.port.config
    distance = hypot(gx-origin[0], origin[1]-50.)
    band = next(points for upper,points in cfg.release_bands if upper is None or distance < upper)
    kid = keeper[0] if keeper else None
    on_target = won or shot_on_target(origin, velocity, gx, cfg, witness.port.m.s.ball.radius)
    return dict(t_ms=flight['t_ms'], release_id=flight['id'], shooter=flight['data']['player'], keeper=kid, band=band,
                distance=distance, aim_offset=abs(aim[1]-keeper[3]) if aim and keeper else None,
                on_target=on_target, goal=won, keeper_touch=kid in touches,
                save=on_target and kid in touches and not won)


def possession_at(possessions, starts, at):
    index = bisect_right(starts, at)-1
    return possessions[index] if index >= 0 else None


def flights_and_archers(log, possessions, witness):
    interceptions, shots = [], []
    flight, touches = None, set()
    arrow_poss, quota, epochs = {}, {}, []
    starts = [p['start_ms'] for p in possessions]
    for p in possessions:
        p.update(arrows=0, charged=0, hits=0, freezes=0, relevant_freezes=[])
    for row in log:
        at, event, data = row['t_ms'],row['event'],row['data']
        if event in ('touch','keeper_contact'):
            touches.add(data['player'])
        if event in ('control','release','restart_release','strip',*INTERVAL_ENDS):
            if event == 'control':
                pid = data['player']
                touches.add(pid)
                if flight:
                    origin = flight['data'].get('player',flight['data'].get('taker'))
                    if flight['data'].get('kind','pass') == 'pass' and origin.split(':')[0] != pid.split(':')[0]:
                        interceptions.append(witness.interception(flight,pid))
            finishing_goal = event == 'goal' and flight and data['team'] == flight['data'].get('player','').split(':')[0]
            record = end_flight(flight,touches,bool(finishing_goal),witness)
            if record:
                shots.append(record)
            flight = row if event in ('release','restart_release') else None
            touches = set()
        p = possession_at(possessions,starts,at)
        if event == 'rb_quota_reset':
            team = data['ruling']['archer_team']
            quota[team] = dict(team=team, start_ms=at, charged=0, peak=0, freezes=0)
            epochs.append(quota[team])
        elif event in ('rb_arrow_release','rb_arrow_forfeited'):
            team = data['ruling']['team']
            if team in quota:
                q = quota[team]
                q['charged'] += 1
                q['peak'] = max(q['peak'],q['charged'])
            if p and p['team'] != team:
                p['charged'] += 1
        elif event == 'arrow_release':
            team = data['player'].split(':')[0]
            if p and p['team'] != team:
                p['arrows'] += 1
            arrow_poss[data['arrow']] = (p if p and p['team']!=team else None, quota.get(team))
        elif event == 'arrow_inert' and data.get('refunded') and data.get('arrow') in arrow_poss:
            origin, q = arrow_poss[data['arrow']]
            if q:
                q['charged'] -= 1
            if origin:
                origin['charged'] -= 1
        elif event in ('arrow_geometry_impact','freeze') and data.get('arrow') in arrow_poss:
            origin,q = arrow_poss[data['arrow']]
            if q and event == 'freeze':
                q['freezes'] += 1
            if origin:
                if event == 'freeze':
                    origin['freezes'] += 1
                    intended = witness.freeze_targets.get(row['id']) == data['player']
                    if data.get('was_carrier') or intended:
                        origin['relevant_freezes'].append(at)
                elif data['target'] not in ('ball',None):
                    origin['hits'] += 1
    if flight:
        shot = end_flight(flight,touches,False,witness)
        if shot:
            shots.append(shot)
    for i,p in enumerate(possessions):
        end = possessions[i+1]['start_ms'] if i+1<len(possessions) else log[-1]['t_ms']
        turnover = p['end_reason'] not in ('score','own_goal','period_end','match_end') and (
            i+1<len(possessions) and p['team']!=possessions[i+1]['team'])
        p['turnover'] = turnover
        p['turnover_after_freeze'] = turnover and any(0 <= end-f <= 3000 for f in p['relevant_freezes'])
    return interceptions, shots, epochs


def index_events(log):
    by_player = defaultdict(list)
    for row in log:
        d = row['data']
        for p in {d.get(k) for k in ('actor','target','player','carrier','a','b','receiver','giver','credited')}:
            if isinstance(p,str) and p:
                by_player[p].append(row)
    for rows in by_player.values():
        rows.sort(key=lambda r:(r['t_ms'],r['id']))
    return by_player


def carry_outcomes(log, witness, by_player, shots):
    shot_by_release = {r['release_id']:r for r in shots}
    reports = []
    for c in witness.carries:
        if c['start_distance'] >= witness.port.config.zone_radius:
            continue
        c = dict(c)
        pid = c['player']
        closing = c.get('closing_id')
        if not closing:
            reports.append(c | dict(outcome='stopped_short'))
            continue
        row = log[closing-1]
        end, ended, data = row['t_ms'],row['event'],row['data']
        evidence = [r for r in log[max(0,closing-5):closing+10] if r['t_ms'] == end]
        reason = data.get('reason')
        shot = shot_by_release.get(closing)
        within_release_radius = shot and shot['distance'] < witness.port.config.carry_release_radius_m
        other_holder = data.get('player') if ended=='control' else None
        outcome = (
            'goal' if ended=='goal' and data.get('method')=='carry' and data.get('team')==c['team']
                      or within_release_radius and shot['goal'] else
            'tackle' if ended=='tackle_count' else
            'strip' if ended=='strip' or any(r['event']=='strip' and r['data'].get('target')==pid for r in evidence) else
            'freeze' if ended=='freeze' or any(r['event']=='freeze' and r['data'].get('player')==pid for r in evidence) else
            'out_of_bounds' if ended=='boundary' or reason=='out_of_bounds' else
            'zone_violation' if reason in ZONE_REASONS else
            'keeper' if other_holder and witness.port.m.s.players[other_holder].role=='keeper' else
            data['kind'] if ended=='release' and data.get('kind') in ('shot','pass') else
            'handoff' if other_holder and any(r['event']=='handoff_complete' and r['data'].get('giver')==pid for r in evidence) else
            'stopped_short'
        )
        stretch = [r for r in by_player[pid] if r['event'] in ('stretch_start','stretch_end','stretch_goal')
                   and c['start_ms'] <= r['t_ms'] <= end]
        c.update(outcome=outcome,end_ms=end,ended_by=ended,reason=reason,
                 shot_after_carry=('goal' if shot['goal'] else 'keeper_save' if shot['save'] else
                     'on_target_not_scored' if shot['on_target'] else 'off_target') if shot else None,
                 stretch=[dict(event=r['event'],t_ms=r['t_ms'],reason=r['data'].get('reason')) for r in stretch])
        reports.append(c)
    return reports


def tackle_outcomes(log, witness, by_player):
    threshold = witness.port.m.assume['tackle_grip_threshold']
    by_time = {pid:[r['t_ms'] for r in rows] for pid,rows in by_player.items()}
    decisions = {pid:[i.decided_ms for i in intents] for pid,intents in witness.admissions.items()}
    whistles = [r for r in log if r['event'] in ('period_end','restart_awarded')]
    whistle_times = [r['t_ms'] for r in whistles]
    completed = []
    for pid, intents in witness.admissions.items():
        index = 0
        while index < len(intents):
            intent = intents[index]
            index += 1
            if intent.contact != 'takedown' or not intent.target:
                continue
            target = intent.target
            start = intent.decided_ms
            expiry = witness.port.prism_decision_interval_ms(pid,intent)
            last = intent
            held_at_admission = witness.committing_grip.get(intent.intent_id, 0.)
            while index < len(intents):
                following = intents[index]
                if (following.contact != 'takedown' or following.target != target or
                        following.decided_ms > last.decided_ms + expiry + witness.port.config.dt_ms):
                    break
                last = following
                held_at_admission = max(held_at_admission, witness.committing_grip.get(last.intent_id,0.))
                index += 1
            stop = last.decided_ms + expiry
            if index < len(intents):
                stop = min(stop,intents[index].decided_ms)
            w = bisect_right(whistle_times,start)
            if w < len(whistles):
                stop = min(stop,whistle_times[w])
            rows,times = by_player[pid],by_time.get(pid,())
            segment = rows[bisect_left(times,start):bisect_right(times,stop)]
            collision = any(r['event']=='c3_collision' and target in (r['data'].get('a'),r['data'].get('b')) for r in segment)
            holds = [r for r in segment if r['event'] in ('c3_hold_end','c3_hold_start')
                     and (r['data']['actor'],r['data']['target'])==(pid,target)]
            grounding = next((r for r in segment if r['event']=='tackle_count'
                             and (r['data'].get('actor'),r['data'].get('target'))==(pid,target)), None)
            times=by_time.get(target,())
            carrier_rows=by_player[target][bisect_left(times,start):bisect_right(times,stop)]
            release = next((r for r in carrier_rows if r['event']=='release' and r['data'].get('player')==target
                            and not r['data'].get('forced')), None)
            grip_lost = next((r for r in holds if r['event']=='c3_hold_end'
                              and r['data']['peak_grip'] >= threshold and r['data']['cause'] not in
                              ('carrier_grounded','control_lost','play_stopped')), None)
            maneuver = next((r for r in carrier_rows if r['data'].get('carrier')==target and r['data'].get('target')==pid
                             and (r['event']=='truck_broken' or r['event']=='stiff_arm_effect'
                                  and r['data']['grip_before']>0 and r['data']['grip_after']==0)), None)
            active_grip = held_at_admission >= threshold or any(
                r['event']=='c3_hold_end' and r['data']['peak_grip']>=threshold for r in holds)
            if grounding:
                outcome, end = 'takedown', grounding['t_ms']
            elif maneuver:
                outcome,end = 'maneuver',maneuver['t_ms']
            elif release and (not grip_lost or release['t_ms'] <= grip_lost['t_ms']):
                outcome,end = 'released_first',release['t_ms']
            elif grip_lost:
                outcome,end = 'grip_lost',grip_lost['t_ms']
            elif active_grip:
                outcome,end = 'grip_unresolved',stop
            elif holds or collision or held_at_admission:
                outcome,end = 'contact_without_confirmed_grip',stop
            else:
                outcome,end = 'no_contact',stop
            turns = decisions.get(target,())
            moves = sorted({(i.technique or i.kind) for i in witness.admissions.get(target,())[
                            bisect_left(turns,start-500):bisect_right(turns,end)]
                            if (i.technique or i.kind) in MANEUVERS})
            actual_carrier, gap = witness.commit_target.get(intent.intent_id,(False,None))
            completed.append(dict(player=pid,target=target,start_ms=start,end_ms=end,outcome=outcome,
                targeted_actual_carrier=actual_carrier, distance_at_commit=gap,
                maneuver=maneuver['event'] if maneuver else None, nearby_maneuvers=moves,
                tackling=witness.skills[pid]['tackling'],evasion=witness.skills[target]['evasion'],
                strength=witness.skills[target]['strength'],balance=witness.skills[target]['balance']))
    return completed


def analyze(witness, box):
    log = witness.port.m.e.log
    positions = index_events(log)
    interceptions, shots, epochs = flights_and_archers(log,box['possessions'],witness)
    return dict(interceptions=interceptions,shots=shots,quota_epochs=epochs,
                carries=carry_outcomes(log,witness,positions,shots),
                tackles=tackle_outcomes(log,witness,positions),
                stretches=[dict(t_ms=r['t_ms'],event=r['event'],**r['data']) for r in log if r['event'].startswith('stretch_')])
