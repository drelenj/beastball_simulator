"""Full or bounded PRISM CORE match with raw rulebook metrics."""
import argparse
import json
from pathlib import Path
from time import process_time

from native.prism_lab import neutral_rosters
from native.nbl_roster import load_canon_nbl
from native.rulebook.port import RulebookPort
from native.rulebook.config import RulebookConfigV3
from native.run import run_match
from metrics import add_metrics, observe_carries

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--mode', choices=('off','core'), default='core')
parser.add_argument('--roster', choices=('control','neutral-real','real'), default='neutral-real')
parser.add_argument('--seed',type=int,default=1)
parser.add_argument('--steps', type=int)
parser.add_argument('--out', type=Path,required=True)
args=parser.parse_args()
rosters=load_canon_nbl(('Garvian Guardians','Ala Apex')) if args.roster == 'real' else neutral_rosters(args.roster == 'neutral-real')
config=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')),
                        individuation='individuation/2' if args.mode == 'core' else 'off')
start=process_time()
port=RulebookPort(args.seed,config,rosters=rosters)
carries=observe_carries(port)
result, port=run_match(args.seed,config,rosters=rosters,port_factory=lambda *a,**k:port,
                       max_steps=args.steps)
result['cpu_ms_per_step']=(process_time()-start)*1000/result['steps']
result.pop('prism_commits',None)
add_metrics(result,port,carries)
args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
