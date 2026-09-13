import sys,json,math,os;sys.path.insert(0,'/home/claude/mv/work')
from geo import *
import numpy as np
from PIL import Image
P=json.load(open('/home/claude/mv/dist/baked/projection.json'))
d=P['dem'];A=P['alpha'];B=P['beta']
H=np.array(d['heights'],dtype=float)
def elevation(x,y):
    u=max(0,min(d['nx']-1.00001,(x-d['x0'])/d['dx']));v=max(0,min(d['ny']-1.00001,(y-d['y0'])/d['dy']))
    i=int(u);j=int(v);u-=i;v-=j
    h00=H[j][i];h10=H[j][i+1];h01=H[j+1][i];h11=H[j+1][i+1]
    return h00+(h10-h00)*u+(h11-h10)*v if v<u else h00+(h11-h01)*u+(h01-h00)*v
def project(lon,lat):
    x,y=merc(lon,lat);return (x,A*y+B*elevation(x,y))
def unproject(px,py):
    y=py/A
    for _ in range(12): y=(py-B*elevation(px,y))/A
    return unmerc(px,y)
def to_pixel(lon,lat,z):
    x,y=project(lon,lat);s=2**(z-17);return (x*s,-y*s)
def from_pixel(u,v,z):
    s=2**(z-17);return unproject(u/s,-v/s)
TILE=512;ROOT='/home/claude/mv/dist/baked/tiles'
def tile_path(z,tx,ty): return f'{ROOT}/{z}/{tx}/{ty}.webp'
def tiles_for_pixel_bbox(z,u0,v0,u1,v1):
    return [(tx,ty) for tx in range(math.floor(u0/TILE),math.floor(u1/TILE)+1) for ty in range(math.floor(v0/TILE),math.floor(v1/TILE)+1)]
def mosaic(z,u0,v0,u1,v1):
    tl=tiles_for_pixel_bbox(z,u0,v0,u1,v1)
    txs=[t[0] for t in tl];tys=[t[1] for t in tl]
    X0=min(txs)*TILE;Y0=min(tys)*TILE
    W=(max(txs)-min(txs)+1)*TILE;Hh=(max(tys)-min(tys)+1)*TILE
    im=Image.new('RGB',(W,Hh),(233,232,215))
    for tx,ty in tl:
        p=tile_path(z,tx,ty)
        if os.path.exists(p): im.paste(Image.open(p).convert('RGB'),(tx*TILE-X0,ty*TILE-Y0))
    return im,X0,Y0
