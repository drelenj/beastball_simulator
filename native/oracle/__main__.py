"""Run offline scenes, save regulation snapshots and verify exact resumes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from time import process_time

from .harness import Force, run
from .matches import match_build
from .rollout import grade, menus
from .scenes import scene
from .snapshot import Snapshot, capture, restore

FINGERPRINT = ('seed','score','steps','live_ms','config_digest','trace_hash','state_hash','status')


def fingerprint(result):
    return {key: result[key] for key in FINGERPRINT}


def exact_replays(args):
    output_dir = args.directory
    output_dir.mkdir(parents=True, exist_ok=True)
    start = process_time()
    build = match_build(args.seed,args.mode)
    driver = build.create()
    files = []
    for n in sorted(args.steps):
        driver.play(max_steps=n)
        if driver.steps != n or driver.final:
            raise ValueError(f'cannot capture step {n} after the match ends')
        path = output_dir / f'{args.mode}-{n}.snapshot.gz'
        capture(build,driver).save(path)
        files.append((n,path))
    driver.play()
    expected = fingerprint(driver.result())
    baseline_cpu_s = process_time() - start
    replays = []
    for n,path in files:
        command = [sys.executable,'-m','native.oracle','resume',str(path)]
        row = json.loads(subprocess.check_output(command, text=True))
        if row['fingerprint'] != expected:
            raise AssertionError((n,expected,row))
        replays.append({'capture_step':n,'snapshot_bytes':path.stat().st_size,**row})
    return {'mode':args.mode,'uninterrupted':expected,'uninterrupted_capture_cpu_s':baseline_cpu_s,
            'fresh_processes':replays}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command',required=True)
    replay = subs.add_parser('verify-replay')
    replay.add_argument('--mode',choices=('core','off'),required=True)
    replay.add_argument('--seed',type=int,default=1)
    replay.add_argument('--steps',type=int,nargs='+',default=(4_000,14_000,25_000))
    replay.add_argument('--directory',type=Path,required=True)
    replay.add_argument('--out',type=Path)
    resume = subs.add_parser('resume')
    resume.add_argument('snapshot',type=Path)
    prepare = subs.add_parser('prepare')
    prepare.add_argument('--scene',type=Path,required=True)
    prepare.add_argument('--athlete',required=True)
    prepare.add_argument('--stage',required=True)
    prepare.add_argument('--turn',type=int,default=1)
    prepare.add_argument('--max-steps',type=int,default=300)
    prepare.add_argument('--snapshot',type=Path,required=True)
    rollout = subs.add_parser('grade')
    rollout.add_argument('snapshot',type=Path)
    rollout.add_argument('--stage',required=True)
    rollout.add_argument('--samples',type=int,default=20)
    rollout.add_argument('--moment')
    rollout.add_argument('--out',type=Path)
    scenario = subs.add_parser('run')
    source = scenario.add_mutually_exclusive_group(required=True)
    source.add_argument('--scene',type=Path)
    source.add_argument('--snapshot',type=Path)
    scenario.add_argument('--team',choices=('A','B'))
    scenario.add_argument('--stop',default='possession')
    scenario.add_argument('--max-ms',type=int,default=30_000)
    scenario.add_argument('--seed',type=int)
    scenario.add_argument('--force',nargs=3,metavar=('ATHLETE','STAGE','INDEX'))
    scenario.add_argument('--decision')
    scenario.add_argument('--turn',type=int,default=1)
    scenario.add_argument('--out',type=Path)
    args = parser.parse_args()
    if args.command == 'verify-replay':
        result = exact_replays(args)
    elif args.command == 'resume':
        start = process_time()
        snapshot = Snapshot.load(args.snapshot)
        if snapshot.compact:
            raise ValueError('full match replay requires a full snapshot')
        driver, prepared = restore(snapshot,record=False)
        if prepared:
            driver.advance(prepared=prepared)
        driver.play()
        result = {'fingerprint':fingerprint(driver.result()),'cpu_s':process_time()-start}
    elif args.command == 'prepare':
        build,driver = scene(args.scene)
        seen = 0
        prepared = None

        def select(view,belief,remaining):
            nonlocal seen,prepared
            intent,record,candidates = menus(view,belief)
            if view.athlete == args.athlete and any(name == args.stage for name,_ in candidates):
                seen += 1
                if seen == args.turn:
                    prepared = capture(build,driver,prepared=(view,belief,remaining))
            return intent,record

        while prepared is None and not driver.final and driver.steps < args.max_steps:
            driver.advance(select)
        if prepared is None:
            raise ValueError('requested menu was not reached')
        prepared.save(args.snapshot)
        result = {'snapshot':str(args.snapshot),'stage':args.stage,'athlete':args.athlete,'turn':args.turn}
    elif args.command == 'grade':
        snapshot = Snapshot.load(args.snapshot)
        result = grade(snapshot,args.moment or snapshot.prefix_hash,args.stage,samples=args.samples)
    else:
        if args.scene:
            _,driver = scene(args.scene)
            prepared = None
        else:
            driver,prepared = restore(Snapshot.load(args.snapshot),record=False)
        force = Force(args.force[0],args.force[1],int(args.force[2]),args.decision,args.turn) if args.force else None
        result = run(driver,prepared=prepared,force=force,team=args.team,
                     stop=args.stop,max_ms=args.max_ms,seed=args.seed)
    output = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if getattr(args,'out',None):
        args.out.write_text(output)
    else:
        print(output,end='')


if __name__ == '__main__':
    main()
