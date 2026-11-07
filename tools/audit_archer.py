"""HP-002 r3 instrument: Archer pathway.  Modes: b0 (B0 flags), shadow (PRISM=1, full PRISM stack), drive (PRISM=1 PRISM_DRIVE=1, full stack).
Reports: arrows, releases with a belief of the target, belief position error, aim divergence between the omniscient lead and the lead computed from the archer's belief (what the arrow would have been if it had been aimed from belief), and the score/log hash.
Read-only logging from S.prism_log; no behaviour change.   usage: python3 tools/audit_archer.py <seed> <out.json> <b0|shadow|drive>"""
import sys, os, json, hashlib, statistics
seed = int(sys.argv[1]); out = sys.argv[2]; mode = sys.argv[3]
if mode != 'b0':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1', PRISM='1')
    if mode == 'drive': os.environ['PRISM_DRIVE'] = '1'
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
P = X.install(X.load_pocket()); S = X.S
over, ex, names = X.make_rosters(seed=seed); res, log, el = X.run(P, over, ex, names, seed=seed, short=True)
rel = S.prism_log.get('release', []) if getattr(S, 'prism_log', None) else []
pe = [r['v']['lsq_.4']['pos_err'] for r in rel if r.get('v', {}).get('lsq_.4')]; ad = [r['v']['lsq_.4'].get('aim_divergence') for r in rel if r.get('v', {}).get('lsq_.4') and r['v']['lsq_.4'].get('aim_divergence') is not None]
q = lambda v, f: round(sorted(v)[int(f * (len(v) - 1))], 3) if v else None
arrows = sum(1 for e in log if 'arrow' in str(e).lower() and 'draw' not in str(e).lower()) if log else None
rep = dict(seed=seed, mode=mode, score=res['score'], n_log=len(log), log_hash=hashlib.sha256(json.dumps([str(e) for e in log]).encode()).hexdigest()[:16],
           releases_logged=len(rel), with_belief=len(pe), pos_err_median=q(pe, .5), pos_err_p90=q(pe, .9), aim_div_n=len(ad), aim_div_median=q(ad, .5), aim_div_p90=q(ad, .9),
           stats=dict(getattr(S, 'prism_stats', {}) or {}), arrow_stats=dict(getattr(S, 'arrow_stats', {}) or {}))
json.dump(rep, open(out, 'w'), indent=1, default=str); print(json.dumps(rep, default=str))
