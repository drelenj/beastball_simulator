"""Exercise the production menus in controlled role and commitment scenarios."""
import argparse
from collections import Counter
from dataclasses import replace
import json
from math import log2
from pathlib import Path
from statistics import mean

from b1.emergence_intents import KeeperIntent
from native import cognition as C, prism_core as CORE, prism_lab as LAB
from sweep import DECISIONS


def evaluate(owner, level, seed):
    v,b,rival,rng = LAB.scene(seed,owner,level)
    v=replace(v,core_entropy=f'strategy/{seed}')
    base=C.ActionIntent('i','d',v.athlete,'carry',None,(92.,51.),None,None,v.delivered_ms)
    menu=CORE.Menu(v)
    if owner == 'playmaking':
        neutral=replace(v,registry_ratings=((owner,.7),))
        _, ref=C.decide(neutral,b)
        values={row[0]:row[2] for row in ref['core_menus'][0]['options']}
        offset=values['carry:']-values['shoot:']+rng.uniform(-.30,.30)
        v=replace(v,policy=replace(v.policy,bias_shoot=v.policy.bias_shoot+offset))
        _, record=C.decide(v,b)
        records=record['core_menus']
    elif owner == 'passing':
        opponent=replace(rival,x=85.,y=54. + rng.uniform(-.4,.4),vx=0.)
        base=replace(base,kind='pass',target='A1',aim=(93.,54.))
        CORE.passing(menu,v,base,(*b.tracks,opponent))
        records=menu.records
    elif owner == 'finishing':
        keeper=replace(b.tracks[1],y=50.+rng.uniform(-.12,.12))
        CORE.finish(menu,v,replace(base,kind='shoot',aim=(100.,50.)),(keeper,))
        records=menu.records
    elif owner == 'evasion':
        rival=replace(rival,x=v.x+2.4+rng.uniform(-.3,.3),y=v.y-.4)
        CORE.evade(menu,v,base,rival,False)
        records=menu.records
    elif owner == 'goalkeeping':
        v=replace(v,role='keeper',x=2.,y=50.,holds_ball=False)
        aux=KeeperIntent('i',v.athlete,'position',v.delivered_ms,'fixture',target=(2.2,50.))
        CORE.keeper_options(menu,v,replace(base,kind='keeper_control',auxiliary=aux))
        records=menu.records
    elif owner in ('defending','zone_coverage','takedown'):
        v=replace(v,holds_ball=False,x=17.,y=50.,own_balance_load=.5+rng.uniform(-.10,.10),
                  own_hold_target='B1' if owner=='takedown' else None,
                  signals=replace(v.signals,passive_team='B'))
        rival=replace(rival,x=19.2,y=50.,vx=5.+rng.uniform(-1.,1.))
        ball=replace(b.tracks[-1],x=rival.x,y=rival.y)
        belief=replace(b,tracks=(rival,ball))
        if owner == 'zone_coverage':
            # Choose a physically plausible decision boundary at the neutral
            # rating, then reuse the same search and scene for all levels.
            neutral=replace(v,registry_ratings=((owner,.7),))
            distances=tuple(range(4,27))
            def closeness(x):
                _, result=C.decide(replace(neutral,x=float(x)),belief)
                options=result['core_menus'][0]['options']
                area=next((o[2] for o in options if o[1]=='zone_coverage'),100.)
                man=max((o[2] for o in options if o[1]=='defending'),-100.)
                return abs(area-man),x
            v=replace(v,x=float(min(distances,key=closeness)))
        _, record=C.decide(v,belief)
        records=record['core_menus']
    elif owner in ('in_air_ball_pursuit','live_ball_pursuit'):
        v=replace(v,holds_ball=False,x=64.,y=46.)
        ball=b.tracks[-1]
        if owner=='live_ball_pursuit':
            v=replace(v,x=10.+rng.uniform(-1.,1.),y=48.)
            ball=replace(ball,vx=0.,vy=0.)
        belief=replace(b,tracks=(ball,),ball_course=replace(
                        b.ball_course,z=.8 if owner=='in_air_ball_pursuit' else .2,
                        vx=ball.vx,vy=ball.vy))
        _,record=C.decide(v,belief)
        records=record['core_menus']
    else:
        v=replace(v,role='archer',x=-5.,y=50.,holds_ball=False,arrows_loaded=15,hunt_cleared=True,
                  signals=replace(v.signals,passive_team='B',ball_status='carried'))
        o=replace(rival,x=62.,y=45.)
        other=replace(o,entity='B2',y=55.+rng.uniform(-.5,.5))
        _,record=C.decide(v,replace(b,tracks=(o,other,b.tracks[-1])))
        records=record['core_menus']
    stage=next((row for row in records if any(option[1]==owner for option in row['options'])),records[0])
    errors=[abs(o[3]-o[2]) for o in stage['options'] if o[1]==owner]
    return {'stage':stage['stage'],'choice':stage['choice'],'mean_abs_error':mean(errors) if errors else 0.,
            'options':stage['options']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path)
    args=parser.parse_args()
    data={}
    for owner in sorted(DECISIONS):
        neutral=[evaluate(owner,.7,seed) for seed in LAB.SEEDS]
        data[owner]=[]
        for level in LAB.LEVELS:
            trials=[evaluate(owner,level,seed) for seed in LAB.SEEDS]
            counts=Counter(t['choice'] for t in trials)
            data[owner].append(dict(level=level, counts=counts,
                choice_changes=sum(a['choice']!=b['choice'] for a,b in zip(trials,neutral)),
                choice_entropy_bits=-sum(n/20*log2(n/20) for n in counts.values()),
                mean_abs_error=mean(t['mean_abs_error'] for t in trials),trials=trials))
    args.out.write_text(json.dumps(data,sort_keys=True)+'\n')


if __name__=='__main__':
    main()
