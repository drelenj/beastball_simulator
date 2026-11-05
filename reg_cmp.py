import sys, json; ARGS=list(sys.argv)
import tend_check as T
import pocket4_proto as X
seed=int(ARGS[1]); off=('tendencies',) if ARGS[2]=='off' else ()
r,log,m,names=T.go(off,seed,False)
st=m.p4.stats
print("score",r["score"],flush=True)
res=dict(seed=seed,mode=ARGS[2],score=r['score'],inj=st.get('injuries'),tab=T.table(m))
# shot/pass/goal by position if stats exist
for k in ('shots','goals','passes','carries'):
    if k in st: res[k]=st[k] if not isinstance(st[k],dict) else {str(a):b for a,b in st[k].items()}
json.dump(res,open('reg_%s_%s.json'%(ARGS[2],seed),'w'),default=str)
print(res['mode'],seed,res['score'],res['inj'])
