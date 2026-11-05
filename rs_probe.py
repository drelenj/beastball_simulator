import sys; ARGS=list(sys.argv)
import tend_check as T, pocket4_proto as X, collections, math
norm=lambda a,b:math.hypot(a,b)
P=X.install(X.load_pocket()); CO=P.CORE; Engine=CO.engine.Engine
rec=[]
o=Engine.restart_release
def rr(self,taker,velocity,target=None,method='hand'):
    s=self.s; r=s.restart
    rs=getattr(r,'rs',None) if r else None
    if rs and rs['kind']=='toss':
        t=s.players[taker]; opp=min((norm(q.x-r.x,q.y-r.y) for q in s.players.values() if q.team!=r.team and q.active and q.role!='archer'),default=99)
        rec.append(dict(kind='toss',thrower=taker,role=t.role,pos=(round(t.x,2),round(t.y,2)),spot=(round(r.x,1),round(r.y,1)),outside=not(0<=t.x<=100 and 0<=t.y<=100),nearest_opp=round(opp,2),dead_s=(s.now-r.created_at)/1000.,ready=(s.now-r.ready_at)/1000.))
    if rs and rs['kind'] in('scrim','snap40'):
        sg=s.attack_sign(r.team); att_ahead=0; def_behind=0; tack=None
        d=dict(kind=rs['kind'],count=s.tackle_count,pms=s.possession_ms,taker=taker,snapper=rs.get('snapper'),team=r.team)
        if rs['kind']=='scrim':
            for p in s.players.values():
                if not p.active or p.role!='field' or p.id==taker: continue
                ua=sg*(p.x-r.x)
                if p.team==r.team and ua>-.3: att_ahead+=1
                if p.team!=r.team and ua<.3 and p.id!=rs['tackler']: def_behind+=1
                if p.id==rs['tackler']: tack=(round(ua,2),round(p.y-r.y,2),p.posture)
            d.update(att_ahead=att_ahead,def_behind=def_behind,tackler=tack,nose=rs['nose'])
        else:
            bad=[p.id for p in s.players.values() if p.active and p.role=='field' and p.id!=taker and abs(p.x-s.ends[p.team])>40.3]
            d['over40']=bad; d['taker_pos']=(round(s.players[taker].x,1),round(s.players[taker].y,1))
        rec.append(d)
    return o(self,taker,velocity,target,method)
Engine.restart_release=rr
over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),int(ARGS[1]))
r,log,el=X.run(P,over,ex,names,off=(),seed=int(ARGS[1]),short=True)
print(r['score'])
for d in [x for x in rec if x['kind']=='toss'][:10]: print(d)
print('toss outside rate',sum(1 for x in rec if x['kind']=='toss' and x['outside']),'/',sum(1 for x in rec if x['kind']=='toss'),' field thrower',sum(1 for x in rec if x['kind']=='toss' and x['role']=='field'),' min nearest opp',min((x['nearest_opp'] for x in rec if x['kind']=='toss'),default=None))
#print('snapper==taker rate',sum(1 for d in rec if d['kind']=='scrim' and d['snapper']==d['taker']),'/',sum(1 for d in rec if d['kind']=='scrim'))
