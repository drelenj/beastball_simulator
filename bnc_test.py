import sys, os, collections; sys.path.insert(0,'.')
import selfplay_v0 as SP, bounce_option_v0 as BN
w=SP._setup(); LOG=[]
_o=w['DS'].score
def _sc(log): LOG.extend(log); return _o(log)
w['DS'].score=_sc
g=dict(SP.BASE)
seed=int(os.environ.get('SEED','1'))
BN.reset()
for t in 'AB': BN.BG[t].update(dribble_rate=1.,skip_rate=1.,bounce_shot_rate=1.)
r=SP.game((g,g,seed,60))
print('seed',seed,'engine',r['engine'],'el',r['el'],'stats',BN.ST['stats'])
ev=collections.Counter(e['event'] for e in LOG)
print({k:v for k,v in ev.items() if 'dribble' in k or k in('foul','shot','goal')})
print('fouls',collections.Counter(e['data'].get('reason') for e in LOG if e['event']=='foul'))
print('shots',[ (e['data'].get('kind'),e['data'].get('result')) for e in LOG if e['event']=='shot'][:8])
d=[e for e in LOG if e['event']=='dribble'];print('first dribble',d[:1])
d=[e for e in LOG if e['event']=='dribble']
rp=[e for e in LOG if e['event']=='dribble_replayed']
print('dribbles',len(d),'replayed',len(rp),'self_recontact',sum(1 for e in LOG if 'recontact' in str(e['data'].get('reason',''))+e['event']))
for e in d:
    i=LOG.index(e); nxt=[f for f in LOG[i+1:i+80] if f['event'] in('control','possession_change','dribble_replayed','foul')][:2]
    print(e['data']['player'],[(f['event'],f['data'].get('player') or f['data'].get('reason')) for f in nxt])
