"""RB-3.13 extra metrics from raw logs (log-only): pass interceptions and distance, receiver second tackle after the snap,
arrows released/inert during holds, receiver freezes after the snap, wasted freezes. usage: extra.py <runs dir> """
import json, sys, math, statistics as st
def load(p): return json.load(open(p))['log']
def run(root):
    out = {}
    for name, b in (('real-seed01','real'),('real-seed03','real'),('real-seed05','real'),('control-seed01','control')):
        log = load(f'{root}/{b}/raw-{name}.json'); n = len(log)
        passes = icp = 0; dist_i = []; dist_c = []
        for q, r in enumerate(log):
            if r['event'] == 'release' and r['data']['kind'] == 'pass':
                passes += 1; team = r['data']['player'][0]; x0, y0 = r['ball'][0], r['ball'][1]
                for x in log[q+1:q+400]:
                    if x['event'] == 'control':
                        d = math.hypot(x['ball'][0]-x0, x['ball'][1]-y0)
                        if x['data']['player'][0] != team: icp += 1; dist_i.append(d)
                        else: dist_c.append(d)
                        break
                    if x['event'] in ('boundary', 'restart_awarded', 'goal'): break
        # holds
        form0 = {r['data'].get('restart_id') for r in log if r['event'] == 'scrimmage_formation'}
        rel = {r['data']['restart_id']: q for q, r in enumerate(log) if r['event'] == 'restart_release' and r['data'].get('restart_id') in form0}
        holds = [(rel[r['data']['restart_id']], q) for q, r in enumerate(log) if r['event'] == 'snap_hold_released' and r['data']['restart_id'] in rel and rel[r['data']['restart_id']] < q]
        arrows_in_hold = sum(1 for a, z in holds for x in log[a:z] if x['event'] in ('rb_arrow_release', 'arrow_release'))
        inert_hold = sum(1 for x in log if x['event'] == 'arrow_inert' and x['data'].get('reason') == 'snap_hold_release')
        # second tackle on receiver after snap
        form = {r['data'].get('restart_id'): r['data'] for r in log if r['event'] == 'scrimmage_formation'}
        sec = rec2 = 0; rfreeze = 0
        for q, r in enumerate(log):
            if r['event'] == 'restart_release':
                f = form.get(r['data'].get('restart_id'))
                if not f: continue
                tk = [x for x in log[q+1:q+300] if x['event'] == 'tackle_count']
                if len(tk) >= 2 or (tk and tk[0]['data'].get('count_to', 0) >= 2):
                    t2 = next((x for x in tk if x['data'].get('count_to') == 2), None)
                    if t2: sec += 1; rec2 += t2['data']['target'] == f['receiver']
                for x in log[q+1:q+300]:
                    if x['event'] == 'freeze' and x['data']['player'] == f['receiver']: rfreeze += 1; break
                    if x['event'] in ('restart_awarded', 'goal'): break
        fr = [x for x in log if x['event'] == 'freeze']; wasted = sum(1 for x in fr if not x['data'].get('was_carrier'))
        out[name] = dict(passes=passes, intercepted=icp, intercept_rate=round(icp / passes, 3) if passes else None,
                         median_intercept_m=round(st.median(dist_i), 2) if dist_i else None, median_complete_m=round(st.median(dist_c), 2) if dist_c else None,
                         second_tackles=sec, on_receiver=rec2, arrows_in_hold=arrows_in_hold, inert_hold=inert_hold, receiver_freezes_after_snap=rfreeze,
                         freezes=len(fr), wasted_freezes=wasted)
    return out
if __name__ == '__main__':
    for root in sys.argv[1:]:
        print('==', root)
        for k, v in run(root).items(): print(k, json.dumps(v))
