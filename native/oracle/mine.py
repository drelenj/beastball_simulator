"""Record Native decisions and sample exact prepared turns for the drill."""
import argparse
from collections import Counter
from dataclasses import asdict
import gzip
from hashlib import sha256
import json
from math import hypot
from pathlib import Path
from time import process_time
from contextlib import nullcontext

from native import cognition, cognition_rb3 as rb
from native.prism_core import Aim
from native.throw_speed import release_speed

from .matches import match_build
from .rollout import menus
from .snapshot import capture

CARRIER_BUCKETS = tuple(f'carrier/{distance}/{pressure}'
                        for distance in ('under20','20to40','over40')
                        for pressure in ('open','pressured'))
QUOTAS = dict.fromkeys(CARRIER_BUCKETS,10) | dict.fromkeys(('passing','finishing','takedown'),30)


def dump_json(data):
    return json.dumps(data,separators=(',',':'),sort_keys=True)


def knowledge(view, belief):
    return {
        'actor_xy':(view.x,view.y),'role':view.role,'has_ball':view.holds_ball,
        'attack_sign':view.attack_sign,'own_goal_x':view.own_goal_x,
        'signals':asdict(view.signals),'ball_course':asdict(belief.ball_course) if belief.ball_course else None,
        'observation_id':view.observation_id,'revision':belief.revision,'max_track_age_ms':belief.max_track_age_ms,
        'tracks':[(t.entity,t.team,t.role,t.x,t.y,t.vx,t.vy,t.captured_ms) for t in belief.tracks],
        'feedback':belief.own_feedback,'own_hold_target':view.own_hold_target,'own_held':view.own_held,
        'body':vars(view.body) if view.body else None,'own_balance_load':view.own_balance_load,
        'release_ms':getattr(view,'own_release_ms',None),'max_throw_speed':view.max_throw_speed,
        'messages':[repr(message) for message in belief.messages],
    }


def features(view, belief, options, stage):
    tracks = [t for t in belief.tracks if 0 <= view.delivered_ms-t.captured_ms <= belief.max_track_age_ms]
    rivals = [t for t in tracks if t.team not in (view.team,'ball') and t.role != 'archer']
    pressure = rb.is_pressured(view,rivals)
    distance = hypot(100.-view.own_goal_x-view.x,50.-view.y)
    keeper = next((t for t in rivals if t.role == 'keeper'),None)
    distance_band = 'under20' if distance < 20 else '20to40' if distance <= 40 else 'over40'
    values = []
    for option in options:
        intent = option.intent
        data = {'goal_distance_m':distance,'pressured':pressure,'field_x_m':view.x if view.attack_sign>0 else 100.-view.x,
                'field_y_m':view.y,'keeper_offset_m':abs(keeper.y-50.) if keeper else None}
        if intent.aim is not None:
            data['attempt_distance_m'] = hypot(intent.aim[0]-view.x,intent.aim[1]-view.y)
            data['lane_margin_m'] = rb.lane_margin(
                view,Aim(*intent.aim),rivals if intent.kind != 'shoot' else [t for t in rivals if t.role == 'field'],
                release_speed(data['attempt_distance_m'],view.max_throw_speed) if stage == 'carrier' and intent.kind == 'pass'
                else max(intent.speed,1.))
            if intent.kind == 'carry':
                data['free_run_m'] = rb.free_run_m(view,rivals,intent.aim)
        values.append(data)
    return f'carrier/{distance_band}/{"pressured" if pressure else "open"}', values


def winner(menu):
    return max(range(len(menu['options'])), key=lambda index: (menu['options'][index][3],-index))


def mine(seed, directory, *, quotas=None, journal=True):
    directory.mkdir(parents=True,exist_ok=True)
    snapshots = directory/'moments'
    snapshots.mkdir(exist_ok=True)
    build = match_build(seed)
    driver = build.create()
    counts = Counter()
    quotas = QUOTAS if quotas is None else quotas
    reservoirs = {group:[] for group in quotas}
    start = process_time()
    with (gzip.open(directory/f'decisions-{seed}.jsonl.gz','wt',compresslevel=3)
          if journal else nullcontext()) as log:
        def observer(view,belief,remaining):
            if view.holds_ball or view.own_hold_target:
                intent,record,options = menus(view,belief)
            else:
                intent,record = cognition.decide(view,belief)
                options = ()
            stages = record.get('core_menus',[])
            if log is not None:
                ratings = dict(view.registry_ratings)
                used_ratings = {option[1]:ratings.get(option[1],.70)
                                for stage in stages for option in stage['options']}
                log.write(dump_json({'decision':intent.decision_id,'athlete':view.athlete,'step':driver.steps,
                                     'team':view.team,'at_ms':view.delivered_ms,
                                     'agent':record.get('prism_agent'),'menus':stages,
                                     'ratings':used_ratings,'belief':knowledge(view,belief),
                                     'procedural_options':record.get('options',[]) if not stages else [],
                                     'chosen_kind':intent.kind})+'\n')
            prefix = []
            for stage, (name,opts) in zip(stages,options):
                index = winner(stage)
                if name in ('carrier','passing','finishing','takedown'):
                    ident = f'{seed}/{intent.decision_id}/{name}'
                    rank = sha256(ident.encode()).hexdigest()
                    if name == 'carrier':
                        group,_ = features(view,belief,(),name)
                    else:
                        group = name
                    counts[group] += 1
                    kept = reservoirs[group]
                    if len(kept) < quotas[group] or rank < kept[-1]['rank']:
                        _,measured = features(view,belief,opts,name)
                        filename = f'{rank}.snapshot.gz'
                        capture(build,driver,prepared=(view,belief,remaining),compact=True).save(snapshots/filename)
                        row = {'moment':ident,'rank':rank,'seed':seed,'step':driver.steps,'team':view.team,
                               'actor':view.athlete,'stage':name,'group':group,'prefix':list(prefix),
                               'menu':stage,'features':measured,'belief':knowledge(view,belief),'snapshot':f'moments/{filename}'}
                        kept.append(row)
                        kept.sort(key=lambda row:row['rank'])
                        if len(kept) > quotas[group]:
                            (directory/kept.pop()['snapshot']).unlink()
                prefix.append((name,index))
            return intent,record

        while not driver.final:
            driver.advance(observer)
    result = driver.result()
    output = {'seed':seed,'score':result['score'],'trace_hash':result['trace_hash'],
              'state_hash':result['state_hash'],'config_digest':result['config_digest'],
              'steps':result['steps'],'decisions':result['decisions_total'],'groups':dict(counts),
              'sample_candidates':[row for group in reservoirs.values() for row in group],
              'cpu_s':process_time()-start}
    (directory/f'mine-{seed}.json').write_text(json.dumps(output,sort_keys=True,indent=2)+'\n')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args()
    mine(args.seed,args.directory)


if __name__=='__main__':
    main()
