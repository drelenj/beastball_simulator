import os,sys,json,collections
os.environ.update(CATCH_V2='1',HAND_FIGHT=os.environ.get('HF','1'),PRISM_KEEPER='1',KP_MINOBS='3')
import test_prism_install as T
seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
import tend_check as TC, pocket4_proto as X
P=X.install(X.load_pocket())
over,ex,names=X.make_rosters(TC.G.read_csv('Ala_Lady_Reds_input.csv'),TC.G.read_csv('Xenar_Dzaku_input.csv'),seed)
r,log,el=X.run(P,over,ex,names,off=(),seed=seed,short=True)
ev=collections.Counter(e['event'] for e in log)
print('score',r['score']); print({k:v for k,v in ev.items() if k in('foul','tackle_count','engagement','goal','ground','possession_change')})
fs=dict(X.S.fstats); print({k:v for k,v in fs.items() if k.startswith(('oa_','mate','seen_mate','hidden_mate','free_ball','call','pm_','zr_'))})
import gc
for o in gc.get_objects():
    if hasattr(o,'stats') and isinstance(getattr(o,'stats',None),dict) and any(k.startswith('hf_') for k in o.stats): print({k:v for k,v in o.stats.items() if k.startswith('hf_') or k in('field_jumps','hand_contests')}); break
