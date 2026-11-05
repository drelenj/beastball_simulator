import subprocess, os, json
from concurrent.futures import ThreadPoolExecutor
env0 = dict(os.environ, PLAT='1', PLAT_H='15', PLAT_SET='5', RULESET='1.0.2', ARROW_V='250', QUIVER_POSS='1', PRISM_SOFT='1', PRISM_TRACKID='1')
seeds = ','.join(str(i) for i in range(1, 9))
cfgs = [('off', None)] + [('neutral', {})] + [(f'{r}_{v}', {r: v}) for r in ('vision', 'awareness', 'clarity', 'reaction', 'focus') for v in (0.1, 0.9)]
def go(c):
    tag, r = c; env = dict(env0, PRISM_FIELD='0' if r is None else '1', PRISM_FIELD_RATINGS=json.dumps(r or {}))
    subprocess.run(['python3', 'plat_study.py', f'fs_{tag}', seeds], env=env, stdout=open(f'fs_{tag}.log', 'w'), stderr=subprocess.STDOUT)
with ThreadPoolExecutor(2) as ex: list(ex.map(go, cfgs))
open('field_done', 'w').write('x')
