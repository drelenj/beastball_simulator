import subprocess, os, json
from concurrent.futures import ThreadPoolExecutor
env0 = dict(os.environ, PLAT='1', PLAT_H='15', PLAT_SET='5', RULESET='1.0.2', ARROW_V='250', QUIVER_POSS='1', PRISM='1', PRISM_DRIVE='1', PRISM_SOFT='1', PRISM_TRACKID='1')
seeds = ','.join(str(i) for i in range(1, 17))
def go(n):
    subprocess.run(['python3', 'plat_study.py', f'an_{n}', seeds], env=dict(env0, PRISM_RATINGS=json.dumps({'anticipation': n})), stdout=open(f'an_{n}.log', 'w'), stderr=subprocess.STDOUT)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, [0.0, 1.0, 0.5, 0.25, 0.75]))
open('antic_done', 'w').write('x')
