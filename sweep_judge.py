import subprocess, os, json
from concurrent.futures import ThreadPoolExecutor
env0 = dict(os.environ, PLAT='1', PLAT_H='15', PLAT_SET='5', RULESET='1.0.2', ARROW_V='250', QUIVER_POSS='1', PRISM='1', PRISM_DRIVE='1', PRISM_SOFT='1', PRISM_TRACKID='1')
seeds = ','.join(str(i) for i in range(1, 17))
cfgs = [('off', None)] + [(str(j), j) for j in (0.0, 1.0, 0.5, 0.25, 0.75)]
def go(c):
    tag, j = c
    r = {'anticipation': 0.0}; env = dict(env0, PRISM_JUDGE='0')
    if j is not None: r['judgment'] = j; env['PRISM_JUDGE'] = '1'
    subprocess.run(['python3', 'plat_study.py', f'jd_{tag}', seeds], env=dict(env, PRISM_RATINGS=json.dumps(r)), stdout=open(f'jd_{tag}.log', 'w'), stderr=subprocess.STDOUT)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, cfgs))
open('judge_done', 'w').write('x')
