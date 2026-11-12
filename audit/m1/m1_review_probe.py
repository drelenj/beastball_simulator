import sys, json, dataclasses, math
from b1.core import decide, AthleteView, BeliefState, Contact
from b1.runtime import PhysicalExecutionPort, CommandIngress, ObservationProjector
mode=sys.argv[1]; seed=int(sys.argv[2]) if len(sys.argv)>2 else 1
port=PhysicalExecutionPort(seed); s=port.m.s
if mode=='phys':
    a1=s.players['A1']; a0=s.players['A0']
    print(json.dumps({'A1_true':[a1.x,a1.y],'A1_active':a1.active,'n_active':sum(p.active for p in s.players.values()),
      'A0_ratings':{k:getattr(a0.a,k,None) for k in ('ball_handling','awareness','vision','decision_speed')},
      'A0_role':getattr(a0,'role',None),'prism_r':str(getattr(__import__('pocket4_proto').S,'prism_r',None))}))
if mode in('seed','moved'):
    eye=ObservationProjector(seed)
    bodies=[dict(id='A1',team='A',x=55.,y=50.,z=0.,h=2.5,r=.4,vx=0.,vy=0.)]
    for t in range(1000,1501,100): eye.capture(t,bodies)
    if mode=='moved':
        a=s.players['A0']; a.x,a.y=70.,20.; port.m.e.follow_carrier()
    s.now=1500
    view,belief=eye.deliver(1500)
    intent,dec=decide(view,belief)
    acc=CommandIngress(port).submit_batch([intent])[0][1]
    port.advance(2100)
    out=[e for e in port.records if e['kind']=='outcome']
    b=s.ball
    print(json.dumps({'seed':seed,'view_self':[view.x,view.y],'true_self':[s.players['A0'].x,s.players['A0'].y],
      'contacts':[(c.entity,round(c.x,2),round(c.y,2)) for c in view.contacts],'kind':intent.kind,
      'outcome':[(o['status'],o['time_ms'],[round(v,2) for v in o.get('ball_velocity',[])]) for o in out],
      'ball_end':[round(b.x,2),round(b.y,2),round(b.z,2)],'ball_mode':str(b.mode)}))
