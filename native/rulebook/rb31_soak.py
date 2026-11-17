"""RB/3.1 match runner with read-only match measurement; outputs outside evidence tree."""
import argparse
import json
import time
import traceback
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from .config import RulebookConfigV3
from .port import RulebookPort
from native.nbl_roster import load_canon_nbl
from native.roster import RATINGS, load_rows
from native.run import run_match


def uniform_rosters():
    roles=['field']*18+['keeper']*2+['archer']*2
    rows=[]
    for n,role in enumerate(roles):
        row={key:.7 for key in RATINGS}
        row.update(id=str(n),role=role,height_m=2.55,mass_kg=230.,acceleration=.7)
        rows.append(row)
    return {t:load_rows(rows,t) for t in ('A','B')}


def measure(p,carry_events):
    e=p.m.e;ledger=e.possession_history+e.possession.ledger
    # A possession begins on a change of passive team, including an award;
    # a period's first passive team begins another possession. A completed
    # possession counts as having an attempt if any shot or zone-entry carry
    # attempt occurred during it. We do not infer intent from a pass.
    timeline=[]
    for row in ledger:
        if row['event']=='passive_possession' or row['event']=='restart_awarded' and row.get('pp_changed'):
            timeline.append((row['t_ms'],0,'possession',row['team']))
    for row in e.rb_attempts:
        if row['shot_attempt']:timeline.append((row['t_ms'],1,'attempt',row['team']))
    timeline.extend((t,1,'attempt',team) for t,team in carry_events)
    possessions=Counter();attempted=Counter();current=None;had=False
    for _,_,kind,team in sorted(timeline,key=lambda x:(x[0],x[1])):
        if kind=='possession':
            if current is not None:
                possessions[current]+=1;attempted[current]+=int(had)
            current=team;had=False
        elif team==current:had=True
    if current is not None:possessions[current]+=1;attempted[current]+=int(had)
    calls=e.rb.calls;discipline=[r for r in calls if r['kind']=='discipline']
    scores={t:{'play':0,'penalty_awards':0} for t in ('A','B')}
    for row in e.log:
        if row['event'] in ('goal','foul_award'):
            d=row['data'];scores[d['team']]['play' if row['event']=='goal' else 'penalty_awards']+=d['points']
    arrows={t:Counter(r['kind'] for r in calls if r.get('team')==t and r['kind'] in ('arrow_release','arrow_forfeited')) for t in ('A','B')}
    return dict(possessions={t:dict(count=possessions[t],with_attempt=attempted[t],share_with_attempt=attempted[t]/possessions[t] if possessions[t] else None) for t in ('A','B')},
        points=scores,carry_attempts={t:dict(attempts=e.rb_bands[t]['carry_attempts'],goals=e.rb_bands[t]['carry_goals']) for t in ('A','B')},
        groundings=sum(r['event']=='c3_grounding' for r in e.log),
        restart_timeouts=sum(v.endswith('_timeout') for v in e.restart_results.values()),
        arrows={t:dict(legal=arrows[t]['arrow_release'],illegal=arrows[t]['arrow_forfeited'],legal_rate=arrows[t]['arrow_release']/sum(arrows[t].values()) if sum(arrows[t].values()) else None) for t in ('A','B')},
        dqs={t:sum(bool(r['dq']) and e.s.players[r['player']].team==t for r in discipline) for t in ('A','B')})


def job(spec):
    block,seed,output=spec;started=time.monotonic();path=Path(output)/f'{block}-seed{seed:02}.json'
    try:
        rosters=uniform_rosters() if block=='control' else load_canon_nbl(('Garvian Guardians','Ala Apex'))
        cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
        p=RulebookPort(seed,cfg,rosters=rosters);carry=[];old=p.m.e.rb_carry_attempt
        def count_attempt(holder,*args,**kw):
            result=old(holder,*args,**kw)
            if result:carry.append((p.m.s.now,holder.team))
            return result
        p.m.e.rb_carry_attempt=count_attempt
        r,_=run_match(seed,cfg,rosters=rosters,port_factory=lambda *a,**k:p)
        # Rulebook report wrapper is not used because the port is instrumented.
        assert r['status']=='final' and r['restart_completion_ratio']==1.
        metrics=measure(p,carry)
        assert all(sum(metrics['points'][t].values())==r['score'][t] for t in ('A','B'))
        out=dict(block=block,seed=seed,status='passed',score=r['score'],live_ms=r['live_ms'],config_digest=cfg.digest,trace_hash=r['trace_hash'],state_hash=r['state_hash'],metrics=metrics,runtime_s=round(time.monotonic()-started,2),restart_completion_ratio=r['restart_completion_ratio'])
    except Exception as exc:
        out=dict(block=block,seed=seed,status='failed',error=repr(exc),traceback=traceback.format_exc(),runtime_s=round(time.monotonic()-started,2))
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--block',choices=('control','real'),required=True);ap.add_argument('--seeds',type=int,nargs='+',required=True);ap.add_argument('--out',required=True);ap.add_argument('--workers',type=int,default=2)
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(args.workers) as pool:
        futures=[pool.submit(job,(args.block,seed,str(out))) for seed in args.seeds]
        for future in as_completed(futures):print(json.dumps(future.result(),sort_keys=True),flush=True)


if __name__=='__main__':main()
