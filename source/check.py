import sys,importlib
from PIL import Image,ImageDraw
g=sys.argv[1];scale=float(sys.argv[2]) if len(sys.argv)>2 else 0.6
m=importlib.import_module('trace_'+g)
im=Image.open(f'../ref/{g}.png').convert('RGB')
d=ImageDraw.Draw(im)
S=lambda pts:[(x,y) for x,y in pts]
for name,kind,pts in m.areas:
    col={'gravel':(255,230,120),'parterre':(255,120,255),'turf':(120,255,120),'vegetable':(255,255,0),'shrubbery':(0,255,200),'cold_frame':(0,200,255),'orchard':(200,255,150),'crop':(255,180,80),'grass_walk':(160,255,120)}.get(kind,(255,255,255))
    d.polygon(S(pts),outline=col,width=3)
for name,w,surf,r,pts in m.walks:
    d.line(S(pts),fill=(0,120,255) if surf=='gravel' else (0,220,80),width=4)
for name,pts in m.walls: d.line(S(pts),fill=(255,0,0),width=4)
for name,pts in getattr(m,'hedges',[]): d.line(S(pts),fill=(0,90,0),width=2)
for f in getattr(m,'fences',[]):
    name,ft,pts=f[0],f[1],f[2]; d.line(S(pts),fill=(255,255,255),width=3)
for name,(x,y) in getattr(m,'gates',[]): d.ellipse([x-12,y-12,x+12,y+12],outline=(255,0,255),width=3)
for x,y,r in getattr(m,'trees',[]): d.ellipse([x-r,y-r,x+r,y+r],outline=(0,255,255),width=2)
im=im.resize((int(im.width*scale),int(im.height*scale)),Image.LANCZOS);im.save(f'check-{g}.png');print(im.size)
