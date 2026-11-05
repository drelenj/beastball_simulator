import subprocess, os, json, sys
from concurrent.futures import ThreadPoolExecutor
env0 = dict(os.environ, PLAT='1', PLAT_H='15', PLAT_SET='5', RULESET='1.0.2', ARROW_V='250', QUIVER_POSS='1', PRISM='1', PRISM_DRIVE='1', PRISM_SOFT='1', PRISM_TRACKID='1')
cfgs = [('base', {})] + [(f'{r}_{v}', {r: v}) for r in ('vision', 'awareness', 'clarity', 'reaction', 'focus') for v in (0.1, 0.9)]
cfgs = [c for c in cfgs if c[0] != 'base']
def go(c):
    tag, r = c
    subprocess.run(['python3', 'plat_study.py', 'sw_' + tag, '1,2,3,4,5,6,7,8,9,10'], env=dict(env0, PRISM_RATINGS=json.dumps(r)), stdout=open(f'sw_{tag}.log', 'w'), stderr=subprocess.STDOUT)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, cfgs))
open('sweep_done2', 'w').write('x')
