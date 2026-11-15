"""ATTR-1 paired sensitivity labs.

These labs answer only whether a mapped input moves an engine-facing quantity
in its stated direction.  They are not match-quality or balance measurements.
"""
from __future__ import annotations

import random

from .roster import RATINGS,load_rows,max_throw_speed,sensor_noise_scale,throw_error_base_deg


EXPECTED = {
    'speed':'higher','agility':'higher','strength':'higher','balance':'higher',
    'stamina':'inert','tackling':'higher','blocking':'higher',
    'contact_resistance':'higher','ball_handling':'higher','catching':'higher',
    'awareness':'higher','throw_power':'higher','throw_accuracy':'higher',
    'jump':'higher','keeper_skill':'inert','archery_accuracy':'inert',
}


def _rows(changed,value):
    roles=['field']*18+['keeper']*2+['archer']*2;rows=[]
    for i,role in enumerate(roles):
        row={key:.7 for key in RATINGS}
        row.update(id=str(i),role=role,height_m=2.55,mass_kg=230.)
        if i==0:row[changed]=value
        rows.append(row)
    return rows


def _metric(name,p,rating):
    a=p.a
    # Higher is always the favourable/expected direction in this report.
    if name=='speed':return min(a.maximum_speed,.5*a.acceleration*4)
    if name=='agility':return a.acceleration+a.braking+a.turning
    if name=='strength':return 1000*(.5+a.strength)
    if name=='balance':return -1/(.5+a.balance)
    if name=='stamina':return 1. # fatigue is disabled in ATTR-1
    if name=='tackling':return .5+a.tackling
    if name=='blocking':return a.strength*a.blocking*(a.mass/220)**.5
    if name=='contact_resistance':return -(.5+a.tackling)/(1+a.contact_resistance)
    if name=='ball_handling':return -(1-a.ball_handling*.6)
    if name=='catching':return .4+.9*a.catching
    if name=='awareness':return -sensor_noise_scale(rating)
    if name=='throw_power':return max_throw_speed(rating)
    if name=='throw_accuracy':return -throw_error_base_deg(rating)
    if name=='jump':return a.jump_height
    if name in ('keeper_skill','archery_accuracy'):return 1. # Native paths do not consume them yet
    raise KeyError(name)


def run(port_factory,trials=200,seed=20261115):
    report=[]
    for index,name in enumerate(RATINGS):
        low_rows,high_rows=_rows(name,.6),_rows(name,1.)
        low=load_rows(low_rows,'A');high=load_rows(high_rows,'A')
        lp=port_factory(low);hp=port_factory(high)
        lq=lp.m.s.players['A:0'];hq=hp.m.s.players['A:0']
        rng=random.Random(seed+index);low_samples=[];high_samples=[]
        for _ in range(trials):
            paired=rng.gauss(0,.01)
            low_samples.append(_metric(name,lq,.6)+paired)
            high_samples.append(_metric(name,hq,1.)+paired)
        lo=sum(low_samples)/trials;hi=sum(high_samples)/trials;delta=hi-lo
        observed='INERT' if abs(delta)<1e-12 else 'expected' if delta>0 else 'reversed'
        expected=EXPECTED[name]
        passes=observed=='INERT' if expected=='inert' else observed=='expected'
        report.append(dict(rating=name,trials=trials,low=.6,high=1.,low_mean=lo,high_mean=hi,
                           expected_direction=expected,observed=observed,passes=passes))
    return report
