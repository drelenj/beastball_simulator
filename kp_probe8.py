import os,sys;sys.path.insert(0,'.')
import keeper_drill_v0 as K
a,r=K.one((40,67.1,0,1)); print(r and (r['goal'],r['touch'],r['flight']))
