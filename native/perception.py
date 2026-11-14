"""Same cylinder visibility predicate, evaluated in one array per frame.
No world objects or hidden attributes: inputs are public geometry tuples.
"""
import math
import numpy as np


def visibility(viewers, endpoints, blockers):
    # viewer: id,x,y,eye_z,is_platform; endpoint: id,x,y,z
    # blocker: id,x,y,z_bottom,z_top,radius
    if not viewers or not endpoints:return np.empty((len(viewers),len(endpoints)),dtype=bool)
    v=np.array([x[1:4] for x in viewers],dtype=float)
    p=np.array([x[1:4] for x in endpoints],dtype=float)
    q=np.array([x[1:] for x in blockers],dtype=float)
    dx=p[None,:,0]-v[:,None,0];dy=p[None,:,1]-v[:,None,1]
    d=np.hypot(dx,dy);den=np.maximum(d*d,.01)
    qx=q[None,None,:,0]-v[:,None,None,0];qy=q[None,None,:,1]-v[:,None,None,1]
    f=(qx*dx[:,:,None]+qy*dy[:,:,None])/den[:,:,None]
    distance2=(qx-f*dx[:,:,None])**2+(qy-f*dy[:,:,None])**2
    height=v[:,None,None,2]+(p[None,:,None,2]-v[:,None,None,2])*f
    hit=(f>.03)&(f<.97)&(distance2<q[None,None,:,4]**2)&(height>=q[None,None,:,2])&(height<=q[None,None,:,3])
    vids=np.array([x[0] for x in viewers]);eids=np.array([x[0] for x in endpoints]);bids=np.array([x[0] for x in blockers])
    hit&=(bids[None,None,:]!=vids[:,None,None])&(bids[None,None,:]!=eids[None,:,None])
    visible=~np.any(hit,axis=2)
    visible|=(d<=2)
    visible|=np.array([x[4] for x in viewers])[:,None]
    return visible


def reference_visibility(viewers,endpoints,blockers):
    result=[]
    for pid,x,y,eye,platform in viewers:
        row=[]
        for eid,tx,ty,z in endpoints:
            dx,dy=tx-x,ty-y;d=math.hypot(dx,dy);blocked=False
            if not platform and d>2:
                for qid,qx,qy,qz,qtop,qr in blockers:
                    if qid in (pid,eid):continue
                    f=((qx-x)*dx+(qy-y)*dy)/max(d*d,.01)
                    if .03<f<.97 and (qx-x-f*dx)**2+(qy-y-f*dy)**2<qr*qr and qz<=eye+(z-eye)*f<=qtop:
                        blocked=True;break
            row.append(not blocked)
        result.append(row)
    return np.array(result,dtype=bool)
