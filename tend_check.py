import sys; sys.argv=['x']; sys.path.insert(0,'.')
import pocket4_proto as X, player_gen_v1 as G
G._LOOKUP.update({'PDR':'passer','PFD':'passer','SCT':'receiver','STR':'forward','TRK':'runner','HNT':'safety','SEN':'backer','TRP':'corner','GRD':'lineman','KPR':'keeper','ARC':'archer'})
def go(off=(), seed=1, short=True):
    P=X.install(X.load_pocket()); over,ex,names=X.make_rosters(G.read_csv('Ala_Lady_Reds_input.csv'),G.read_csv('Xenar_Dzaku_input.csv'),seed)
    r,log,el=X.run(P,over,ex,names,off=off,seed=seed,short=short); return r,log,X.S.last,names
def table(m):
    out={}
    for (pos,st),a in sorted(m.p4.pos_acc.items()):
        out.setdefault(pos,{})[st]=(round(a[1]/a[0],1),round(a[2]/a[0],1),round(a[3]/a[0],1))
    return out
if __name__=='__main__':
    for off in ((),('tendencies',)):
        r,log,m,names=go(off,1,True); print('OFF' if off else 'ON ',r['score'],'inj',m.p4.stats['injuries'])
        for pos,d in table(m).items(): print(' ',pos,{k:v for k,v in d.items()})
