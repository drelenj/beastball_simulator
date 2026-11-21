"""RB-3.20 comparison metrics from raw logs (log-only). usage: metrics.py label=dir ... (dir holds real/ control/ with raw-*.json[.gz]).
Possession end causes use the RB-3.11 offense_diagnosis classification (the lead's HP-002 RB-3.19 review numbers)."""
import sys, json, gzip, os, statistics as st, collections, math, tempfile, shutil
sys.path.insert(0, os.path.dirname(__file__))
from offense_diagnosis import Match, q1_q2
import stages

RUNS = [('real', 1), ('real', 3), ('real', 5), ('control', 1)]


def gz_root(root):
    """offense_diagnosis reads raw-*.json.gz: mirror the directory with gz files."""
    tmp = tempfile.mkdtemp()
    for b in ('real', 'control'):
        os.makedirs(f'{tmp}/{b}', exist_ok=True)
        for f in os.listdir(f'{root}/{b}') if os.path.isdir(f'{root}/{b}') else ():
            src = f'{root}/{b}/{f}'
            if f.startswith('raw-') and f.endswith('.json'):
                with open(src, 'rb') as i, gzip.open(f'{tmp}/{b}/{f}.gz', 'wb') as o: shutil.copyfileobj(i, o)
            else:
                shutil.copy(src, f'{tmp}/{b}/{f}')
    return tmp


def missed_exit(log):
    """Missed open-play passes that leave the field untouched: distance from release to the exit point and time."""
    d = []; t = []
    for i, r in enumerate(log):
        if r['event'] == 'release' and (r.get('data') or {}).get('kind') == 'pass':
            x0, y0 = r['ball'][0], r['ball'][1]
            for x in log[i + 1:i + 400]:
                if x['event'] in ('control', 'touch', 'restart_awarded', 'goal'): break
                if x['event'] == 'boundary':
                    c = x['data'].get('crossing') or [x['ball'][0], x['ball'][1]]
                    d.append(math.hypot(c[0] - x0, c[1] - y0)); t.append((x['live_ms'] - r['live_ms']) / 1000.); break
    return d, t


def run(root):
    g = gz_root(root); out = {}
    real_scores = []; causes = collections.Counter(); n_poss = 0; ex_d = []; ex_t = []
    for b, s in RUNS:
        if not os.path.exists(f'{g}/{b}/raw-{b}-seed{s:02d}.json.gz'): continue
        m = Match(g, '/nonexistent', b, s); P = q1_q2(m)
        row = stages.one(root, b, f'{b}-seed{s:02d}')
        res = m.res
        d, t = missed_exit(m.log)
        out[m.name] = dict(score=res['score'], trace_hash=res['trace_hash'], state_hash=res['state_hash'], steps=res.get('steps'),
                           possessions_per_team=round(len(P) / 2, 1), handoffs=row['actions'].get('handoff_complete', 0),
                           missed=row['missed'], missed_recovered=row['missed_recovered_by_passer_team'], passes=row['passes'],
                           missed_exit_median_m=round(st.median(d), 1) if d else None, missed_exit_median_s=round(st.median(t), 2) if t else None,
                           missed_exits=len(d), boundaries=row['boundaries'], boundary_after=row['boundary_after'], points_by_method=row['points_by_method'],
                           actions=row['actions'])
        if b == 'real':
            real_scores += list(res['score'].values()); n_poss += len(P); causes.update(p['cause'] for p in P); ex_d += d; ex_t += t
    summary = dict(real_median_team_score=st.median(real_scores) if real_scores else None, real_scores=real_scores,
                   real_possessions_per_team=round(n_poss / 6, 1),
                   real_end_causes_pct={k: round(v / n_poss * 100, 1) for k, v in causes.most_common()},
                   real_missed_exit_median_m=round(st.median(ex_d), 1) if ex_d else None, real_missed_exit_median_s=round(st.median(ex_t), 2) if ex_t else None)
    shutil.rmtree(g)
    return summary, out


if __name__ == '__main__':
    allout = {}
    for arg in sys.argv[1:]:
        lab, root = arg.split('=')
        summary, per = run(root); allout[lab] = dict(summary=summary, per_match=per)
        print('==', lab, json.dumps(summary))
        for k, v in per.items(): print('  ', k, json.dumps(v, sort_keys=True))
    if os.environ.get('OUT'): json.dump(allout, open(os.environ['OUT'], 'w'), indent=1, sort_keys=True)
