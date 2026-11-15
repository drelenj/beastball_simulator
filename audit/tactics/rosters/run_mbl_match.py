import sys, argparse
from pathlib import Path
import player_gen_v1 as G
MAP={'PDR':'passer','PFD':'passer','SCT':'receiver','STR':'forward','TRK':'runner','HNT':'safety','SEN':'backer','TRP':'corner','GRD':'lineman','KPR':'keeper','ARC':'archer'}
G._LOOKUP.update(MAP)
import pocket4_proto as P4
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--a',default='../Ala_Lady_Reds_input.csv');p.add_argument('--b',default='../Xenar_Dzaku_input.csv');p.add_argument('--seed',type=int,default=1);p.add_argument('--short',action='store_true');a=p.parse_args()
    P=P4.install(P4.load_pocket())
    over,extra,names=P4.make_rosters(G.read_csv(a.a),G.read_csv(a.b),a.seed)
    result,log,elapsed=P4.run(P,over,extra,names,seed=a.seed,short=a.short)
    print(P4.box(result,log,names));print('wall_seconds',round(elapsed,2))
