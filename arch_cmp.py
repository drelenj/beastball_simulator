import sys, collections; ARGS=list(sys.argv)
import tend_check as T
seeds=[int(x) for x in ARGS[1].split(',')]
for sd in seeds:
    for tag,off in (('fix',()),('orig',('archerfix',))):
        r,log,m,names=T.go(off,sd,True)
        c=collections.Counter((e['event'],e['data'].get('player','?')[0] if e['event']=='arrow_release' else '-') for e in log)
        fz=collections.Counter(e['data'].get('player','?')[0] for e in log if e['event']=='freeze')
        print(sd,tag,r['score'],'arrows A %d B %d'%(c[('arrow_release','A')],c[('arrow_release','B')]),'frozen A %d B %d'%(fz['A'],fz['B']),flush=True)
