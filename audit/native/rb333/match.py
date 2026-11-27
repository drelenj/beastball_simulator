"""Run one named ladder arm and save one atomic self-contained result."""
import argparse
import gzip
import io
import json
import platform
import signal
from collections import Counter
from math import hypot, sin, atan2
from pathlib import Path
from time import process_time
from native.oracle.snapshot import Build
from native.rulebook.config import RulebookConfigV3
from native.nbl_roster import load_nbl_workbook
from native.rulebook.stats_ledger import write_csv
from audit.native.rb332.match import PAIRS, TRIAL_SCALE
from audit.native.rb332.witness import TrialWitness
from audit.native.rb331.events import analyze
from audit.native.rb331.summarize import diagnose

STAGES = (('frame_freshness','arrival_lane'),('movement_clock','mouth_boundary','braking'),
          ('keeper_interrupt','keeper_deadline','keeper_menu','keeper_settle'),
          ('cadence','field_interrupt','abort_wrap'),('pass_signal','pass_speed'),
          ('carry_seven','stretch_range','planning_speed'))
ARMS = ('RB332','A0','A1','A2','A3','A4','A5','A5prime')


TURNOVER_STAGES = (('projected_beliefs',),('sideline_held_ball','carrier_boundary'),
                   ('keeper_plant',),('takedown_gate',))
TURNOVER_ARMS = ('B1','B2','B3','B4')


SETS_ARMS = ('C0','C1','C2','T3','T4')
TRACTION = {'L0':1.,'L1':1.5,'L2':2.}
ARCHERY = {'R0':None,'R1':None,'R2':'match','R3':'period'}


def run(arm, seed, book, pair=0, *, diagnostics=False, turnover_diagnostics=False, max_steps=None):
    archer_arm = arm if arm in ARCHERY else None
    if archer_arm:
        arm = 'L0'
    traction_arm = arm if arm in TRACTION else None
    if traction_arm:
        arm = 'T3'
    sets_arm = arm if arm in SETS_ARMS else None
    if sets_arm:
        arm = 'B4'
    turnover_arm = arm if arm in TURNOVER_ARMS else None
    if turnover_arm:
        arm = 'A6'
    switches = tuple(k for stage in STAGES[:ARMS.index('A5' if arm == 'A6' else arm)] for k in stage)
    if arm == 'A6':
        switches = tuple('carry_value' if k == 'carry_seven' else k for k in switches)
    if arm=='A5prime':
        switches+=('fast_cadence',)
    if turnover_arm:
        switches += tuple(k for stage in TURNOVER_STAGES[:TURNOVER_ARMS.index(turnover_arm)+1] for k in stage)
    if sets_arm:
        switches = tuple(s for s in switches if s!='keeper_plant')+('boundary_cross_y','endline_held_ball','active_reflex_observers')
        if sets_arm!='C0':
            switches+=('universal_set_speed',)
        if sets_arm not in ('C0','C1'):
            switches+=('universal_unset',)
    trial_limit = {'T3':3,'T4':4}.get(sets_arm)
    tackle_config = {'tackles_per_possession': trial_limit or 2}
    if traction_arm:
        tackle_config['traction_scale'] = TRACTION[traction_arm]
    if archer_arm and archer_arm != 'R0':
        tackle_config.update(archer_cycle=True, archer_budget=ARCHERY[archer_arm])
    rosters=load_nbl_workbook(book,PAIRS[pair],technical='explicit')
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in 'AB'),
        rb322_technical_source='explicit',individuation='individuation/2',fatigue_rotation=True,
        rotation_rhythm='PLANNED',planned_rate_scale=TRIAL_SCALE,rb332_pass_clearance=True,
        rb332_boundary_guard=True,rb332_fresh_takedown=True,rb332_carry_finish=arm in ('RB332','A5','A5prime','A6'),
        **({'rb333':switches} if switches else {}),**tackle_config)
    start=process_time()
    driver=Build(seed,cfg,rosters).create(record=False)
    driver.enable_stats()
    witness=TrialWitness(driver.port,rosters,True)
    diagnostic = None
    if diagnostics:
        from audit.native.rb334.witness import Diagnostics
        diagnostic = Diagnostics(driver, witness)
    turnover = None
    if turnover_arm or turnover_diagnostics:
        from audit.native.rb335.witness import Witness
        turnover = Witness(driver)
    sets = None
    if sets_arm:
        from audit.native.rb336.witness import Witness as SetWitness
        sets = SetWitness(driver)
    traction = None
    if traction_arm:
        from audit.native.rb337.witness import Witness as TractionWitness
        traction = TractionWitness(driver,rosters)
    archer = None
    if archer_arm:
        from audit.native.rb338.witness import Witness as ArcherWitness
        archer = ArcherWitness(driver)
    samples=Counter()
    def sample(_signal,frame):
        samples[f'{Path(frame.f_code.co_filename).name}/{frame.f_code.co_name}']+=1
    if arm in ('A5','A5prime','A6'):
        previous=signal.signal(signal.SIGPROF,sample)
        signal.setitimer(signal.ITIMER_PROF,.05,.05)
    try:
        archer.play(driver,max_steps) if archer else driver.play(max_steps)
    finally:
        if arm in ('A5','A5prime','A6'):
            signal.setitimer(signal.ITIMER_PROF,0)
            signal.signal(signal.SIGPROF,previous)
    cpu=process_time()-start
    result=driver.result()
    box=result['box_score']
    observed=analyze(witness,box)
    bounds,keepers=witness.detail(observed['shots'])
    for event in bounds:
        event['ball_z']=driver.port.m.e.log[event['event_id']-1]['ball'][2]
    passes=[]
    for rid,(snapshot,aim,_,_) in witness.release.items():
        row=driver.port.m.e.log[rid-1]
        d=row['data']
        if d.get('kind','pass')!='pass' or not aim or 'velocity' not in d:
            continue
        vx,vy,vz=d['velocity']
        dx,dy=aim[0]-snapshot[0][0],aim[1]-snapshot[0][1]
        passes.append(dict(id=rid,speed=hypot(vx,vy,vz),lateral_miss_m=abs(sin(atan2(vy,vx)-atan2(dy,dx)))*hypot(dx,dy)))
    output=io.StringIO()
    write_csv(box,output)
    extra = diagnostic.result(observed) if diagnostic else {}
    if turnover:
        extra['rb335'] = turnover.result()
    if sets:
        extra['rb336'] = sets.result()
    if traction:
        extra['rb337'] = traction.result(box)
    if archer:
        extra['rb338'] = archer.result(bounds)
    return dict(**extra,arm=archer_arm or traction_arm or sets_arm or turnover_arm or arm,seed=seed,pair=pair,python=platform.python_version(),cpu_s=cpu,
        **{k:result[k] for k in ('score','config_digest','trace_hash','state_hash','invariants','status','restart_completion_ratio')},
        box=box,box_csv=output.getvalue(),diagnosis=diagnose([dict(team_lines=box['teams'],possessions=box['possessions'],diagnosis=observed)]),
        cpu_profile=samples.most_common(20),passes=passes,boundary=bounds,keeper=keepers,ratings={p:s['catching'] for p,s in witness.skills.items()},
        strength={p:s['strength'] for p,s in witness.skills.items()},events=result['engine_events'],
        unset=sum(hypot(b.vx,b.vy)>driver.port.m.assume['keeper_set_mps'] for b,*_ in witness.keeper.values()))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('arm',choices=(*ARMS,'A6',*TURNOVER_ARMS,*SETS_ARMS,*TRACTION,*ARCHERY))
    p.add_argument('book',type=Path)
    p.add_argument('out',type=Path)
    p.add_argument('--seed',type=int,default=1)
    p.add_argument('--max-steps',type=int)
    p.add_argument('--pair',type=int,default=0)
    p.add_argument('--diagnostics', action='store_true')
    p.add_argument('--turnover-diagnostics',action='store_true')
    a=p.parse_args()
    result=run(a.arm,a.seed,a.book,a.pair,
               diagnostics=a.diagnostics or (a.arm == 'A6' and not a.turnover_diagnostics),
               turnover_diagnostics=a.turnover_diagnostics,max_steps=a.max_steps)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    tmp=a.out.with_suffix('.tmp')
    tmp.write_bytes(gzip.compress(json.dumps(result,ensure_ascii=False).encode(),mtime=0))
    tmp.replace(a.out)
    print(a.arm,result['score'],result['trace_hash'],flush=True)

if __name__=='__main__':
    main()
