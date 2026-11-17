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
        row.update(id=str(n),role=role,height_m=2.39,mass_kg=226.,reach_m=3.05,acceleration=.7)
        rows.append(row)
    return {t:load_rows(rows,t) for t in ('A','B')}


def measure(p,carry_events,foul_events,arrow_attempts):
    e=p.m.e;ledger=e.possession_history+e.possession.ledger
    # A possession begins on a change of passive team, including an award;
    # a period's first passive team begins another possession. An attempt is
    # terminal when it is the final observed offensive ball action; a later
    # control or pass replaces it.
    timeline=[]
    for row in ledger:
        if row['event']=='passive_possession' or row['event']=='restart_awarded' and row.get('pp_changed'):
            timeline.append((row['t_ms'],0,'possession',row['team']))
    for row in e.log:
        if row['event']=='control':
            player=e.s.players.get(row['data']['player'])
            if player:timeline.append((row['t_ms'],1,'control',player.team))
    for row in e.rb_attempts:
        timeline.append((row['t_ms'],2,'attempt' if row['shot_attempt'] else 'pass',row['team']))
    timeline.extend((row['t_ms'],3,'attempt',row['team']) for row in carry_events)
    possessions=Counter();attempted=Counter();terminal=Counter();current=None;had=False;last=None
    for _,_,kind,team in sorted(timeline,key=lambda x:(x[0],x[1])):
        if kind=='possession':
            if current is not None:
                possessions[current]+=1;attempted[current]+=int(had);terminal[current]+=int(last=='attempt')
            current=team;had=False;last=None
        elif team==current:
            last=kind
            if kind=='attempt':had=True
    if current is not None:possessions[current]+=1;attempted[current]+=int(had);terminal[current]+=int(last=='attempt')
    calls=e.rb.calls
    scores={t:{'play':0,'penalty_awards':0} for t in ('A','B')}
    for row in e.log:
        if row['event'] in ('goal','foul_award'):
            d=row['data'];scores[d['team']]['play' if row['event']=='goal' else 'penalty_awards']+=d['points']
    # Attribute every released projectile to its Archer and its terminal engine
    # outcome. A legal release with no retained impact is reported explicitly.
    arrow_log={}
    for row in e.log:
        arrow=row['data'].get('arrow')
        if arrow is None:continue
        outcome={'freeze':'freeze','inert_impact':'inert_impact','arrow_ball':'ball_impact',
                 'arrow_stop':'stopped','arrow_geometry_impact':'geometry_impact'}.get(row['event'])
        if outcome:arrow_log.setdefault(arrow,[]).append(outcome)
    archer_outcomes={}
    for attempt in arrow_attempts:
        player=attempt['player'];counts=archer_outcomes.setdefault(player,Counter())
        if not attempt['legal']:
            counts[attempt['outcome']]+=1;continue
        outcomes=arrow_log.get(attempt['arrow'],())
        terminal=next((x for x in ('freeze','ball_impact','inert_impact','stopped') if x in outcomes),
                      'geometry_impact' if 'geometry_impact' in outcomes else 'released_no_impact')
        counts[terminal]+=1
    arrows={pid:dict(sorted(counts.items())) for pid,counts in sorted(archer_outcomes.items())}

    # Goal source: a goal is restart-adjacent only when the scoring team owns
    # the released restart possession and passive possession has not flipped.
    releases=[row for row in e.log if row['event']=='restart_release']
    passive=[row for row in ledger if row['event']=='passive_possession']
    goal_sources={t:Counter() for t in ('A','B')}
    for goal in (row for row in e.log if row['event']=='goal'):
        team=goal['data']['team'];prior=next((r for r in reversed(releases) if r['t_ms']<=goal['t_ms']),None)
        adjacent=False
        if prior and prior['data'].get('team')==team:
            adjacent=not any(row['t_ms']>prior['t_ms'] and row['t_ms']<=goal['t_ms'] and row['team']!=team for row in passive)
        goal_sources[team]['within_one_possession_of_restart' if adjacent else 'live_play_after_possession_change']+=1
        goal_sources[team]['points_within_one_possession_of_restart' if adjacent else 'points_live_play_after_possession_change']+=goal['data']['points']

    # Carry attempts begin on first controlled entry inside the 20 m scoring
    # zone. Classify the first terminating witness after that entry.
    carry_outcomes={t:Counter() for t in ('A','B')}
    terminal_events=[row for row in e.log if row['event'] in ('goal','c3_grounding','restart_awarded','control')]
    for n,attempt in enumerate(carry_events):
        stop=carry_events[n+1]['t_ms'] if n+1<len(carry_events) else float('inf')
        outcome='other_or_match_end'
        for row in terminal_events:
            if not attempt['t_ms']<=row['t_ms']<stop:continue
            data=row['data']
            if row['event']=='goal' and data.get('team')==attempt['team'] and data.get('method')=='carry':outcome='carry_goal';break
            if row['event']=='c3_grounding':outcome='grounding';break
            if row['event']=='restart_awarded':outcome='restart_or_turnover';break
            if row['event']=='control':
                player=e.s.players.get(data.get('player'))
                if player and player.team!=attempt['team']:outcome='lost_control';break
        carry_outcomes[attempt['team']][outcome]+=1

    foul_rows=[];dq_rows=[]
    for row in foul_events:
        item=dict(rule=row['rule'],offender=row['offender'],role=row['role'],team=row['team'],
                  award_value=row['award_value'],discipline=row['discipline'],dq=row['dq'])
        foul_rows.append(item)
        if row['dq']:dq_rows.append(item)
    return dict(possessions={t:dict(count=possessions[t],with_attempt=attempted[t],ending_in_attempt=terminal[t],share_ending_in_attempt=terminal[t]/possessions[t] if possessions[t] else None) for t in ('A','B')},
        points=scores,goals_by_source={t:dict(goal_sources[t]) for t in ('A','B')},
        carry_attempts={t:dict(attempts=e.rb_bands[t]['carry_attempts'],goals=e.rb_bands[t]['carry_goals'],outcomes=dict(carry_outcomes[t])) for t in ('A','B')},
        groundings=sum(r['event']=='c3_grounding' for r in e.log),
        restart_timeouts=sum(v.endswith('_timeout') for v in e.restart_results.values()),
        arrows_by_archer=arrows,
        arrows={t:dict(legal=sum(a['legal'] and a['team']==t for a in arrow_attempts),illegal=sum(not a['legal'] and a['team']==t for a in arrow_attempts),
                       legal_rate=sum(a['legal'] and a['team']==t for a in arrow_attempts)/sum(a['team']==t for a in arrow_attempts) if any(a['team']==t for a in arrow_attempts) else None) for t in ('A','B')},
        fouls=foul_rows,dq_events=dq_rows,
        dqs={t:sum(row['team']==t for row in dq_rows) for t in ('A','B')})


def job(spec):
    block,seed,output=spec;started=time.monotonic();path=Path(output)/f'{block}-seed{seed:02}.json'
    try:
        rosters=uniform_rosters() if block=='control' else load_canon_nbl(('Garvian Guardians','Ala Apex'))
        cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
        p=RulebookPort(seed,cfg,rosters=rosters);carry=[];fouls=[];arrows=[];e=p.m.e
        old=e.rb_carry_attempt
        def count_attempt(holder,*args,**kw):
            result=old(holder,*args,**kw)
            if result:carry.append(dict(t_ms=p.m.s.now,team=holder.team,player=holder.id,x=holder.x,y=holder.y))
            return result
        e.rb_carry_attempt=count_attempt
        old_foul=e.foul
        def count_foul(actor,victim=None,reason='hold',*args,**kw):
            q=p.m.s.players[actor];before=dict(p.m.s.score);minor=q.minor_count;major=q.major_count;dq=q.disqualified
            result=old_foul(actor,victim,reason,*args,**kw)
            discipline='major' if q.major_count>major else 'minor' if q.minor_count>minor else 'warning_or_corrected'
            fouls.append(dict(t_ms=p.m.s.now,rule=reason,offender=actor,role=q.role,team=q.team,
                              award_value=sum(p.m.s.score[t]-before[t] for t in ('A','B')),
                              discipline=discipline,dq=bool(q.disqualified and not dq)))
            return result
        e.foul=count_foul
        old_arrow=e.shoot_arrow
        def count_arrow(pid,target,velocity,origin=None):
            before=len(e.rb.calls)
            result=old_arrow(pid,target,velocity,origin)
            q=p.m.s.players[pid];legal=bool(result)
            rulings=e.rb.calls[before:]
            ruling=next((row['kind'] for row in rulings if row['kind'].startswith('arrow_')),None)
            arrows.append(dict(t_ms=p.m.s.now,player=pid,team=q.team,legal=legal,
                               arrow=getattr(result,'id',None),outcome=ruling or 'rejected_before_ruling'))
            return result
        e.shoot_arrow=count_arrow
        r,_=run_match(seed,cfg,rosters=rosters,port_factory=lambda *a,**k:p,
                      progress=lambda row:print(json.dumps(dict(block=block,progress=True,**row),sort_keys=True),flush=True))
        # Rulebook report wrapper is not used because the port is instrumented.
        assert r['status']=='final' and r['restart_completion_ratio']==1.
        metrics=measure(p,carry,fouls,arrows)
        assert all(sum(metrics['points'][t].values())==r['score'][t] for t in ('A','B'))
        out=dict(block=block,seed=seed,status='passed',score=r['score'],live_ms=r['live_ms'],config_digest=cfg.digest,trace_hash=r['trace_hash'],state_hash=r['state_hash'],metrics=metrics,runtime_s=round(time.monotonic()-started,2),restart_completion_ratio=r['restart_completion_ratio'])
    except Exception as exc:
        out=dict(block=block,seed=seed,status='failed',error=repr(exc),traceback=traceback.format_exc(),runtime_s=round(time.monotonic()-started,2))
    path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--block',choices=('control','real'),required=True);ap.add_argument('--seeds',type=int,nargs='+',required=True);ap.add_argument('--out',required=True);ap.add_argument('--workers',type=int,default=2)
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    # Each build creates isolated physical-engine classes; retire the process
    # after a match so those classes and their state do not accumulate.
    with ProcessPoolExecutor(args.workers,max_tasks_per_child=1) as pool:
        futures=[pool.submit(job,(args.block,seed,str(out))) for seed in args.seeds]
        for future in as_completed(futures):print(json.dumps(future.result(),sort_keys=True),flush=True)


if __name__=='__main__':main()
