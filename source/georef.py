import sys,json,math;sys.path.insert(0,'/home/claude/mv/work')
import numpy as np
from geo import merc,unmerc
def fit_similarity(cps):
    # cps: list of ((u,v),(x,y)) ; model x = a*u - b*v + tx ; y = b*u + a*v + ty  (with v flipped: use v'=-v)
    A=[];B=[]
    for (u,v),(x,y) in cps:
        vv=-v
        A.append([u,-vv,1,0]);B.append(x)
        A.append([vv,u,0,1]);B.append(y)
    A=np.array(A);B=np.array(B)
    p,res,rk,sv=np.linalg.lstsq(A,B,rcond=None)
    a,b,tx,ty=p
    s=math.hypot(a,b);th=math.degrees(math.atan2(b,a))
    def fwd(u,v):
        vv=-v;return (a*u-b*vv+tx, b*u+a*vv+ty)
    def inv(x,y):
        det=a*a+b*b
        u=( a*(x-tx)+b*(y-ty))/det
        vv=(-b*(x-tx)+a*(y-ty))/det
        return (u,-vv)
    resid=[(math.hypot(*(np.array(fwd(*uv))-np.array(xy)))) for uv,xy in cps]
    return dict(a=a,b=b,tx=tx,ty=ty,scale_m_per_px=s,theta_deg=th,resid_m=resid,fwd=fwd,inv=inv)
def fit_affine(cps):
    A=[];B=[]
    for (u,v),(x,y) in cps:
        A.append([u,v,1,0,0,0]);B.append(x)
        A.append([0,0,0,u,v,1]);B.append(y)
    A=np.array(A);B=np.array(B)
    p=np.linalg.lstsq(A,B,rcond=None)[0]
    M=np.array([[p[0],p[1]],[p[3],p[4]]]);t=np.array([p[2],p[5]])
    Mi=np.linalg.inv(M)
    fwd=lambda u,v: tuple(M@np.array([u,v])+t)
    inv=lambda x,y: tuple(Mi@(np.array([x,y])-t))
    resid=[math.hypot(*(np.array(fwd(*uv))-np.array(xy))) for uv,xy in cps]
    return dict(M=M.tolist(),t=t.tolist(),resid_m=resid,fwd=fwd,inv=inv)
def px_to_lonlat(T,u,v):
    return unmerc(*T['fwd'](u,v))
def fit_homography(cps):
    A=[]
    for (u,v),(x,y) in cps:
        A.append([u,v,1,0,0,0,-x*u,-x*v,-x])
        A.append([0,0,0,u,v,1,-y*u,-y*v,-y])
    A=np.array(A)
    U,S,Vt=np.linalg.svd(A);h=Vt[-1].reshape(3,3)
    Hi=np.linalg.inv(h)
    def fwd(u,v):
        p=h@np.array([u,v,1.0]);return (p[0]/p[2],p[1]/p[2])
    def inv(x,y):
        p=Hi@np.array([x,y,1.0]);return (p[0]/p[2],p[1]/p[2])
    resid=[math.hypot(*(np.array(fwd(*uv))-np.array(xy))) for uv,xy in cps]
    return dict(H=h.tolist(),resid_m=resid,fwd=fwd,inv=inv)
