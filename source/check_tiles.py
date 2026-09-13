import sys,json;sys.path.insert(0,'/home/claude/mv/work')
from tiles import *
from PIL import ImageDraw
G=json.load(open('/home/claude/mv/dist/gardens-2026.geojson'))
E=json.load(open('/home/claude/mv/dist/estate.geojson'))
z=19
boxes={'upper':(-77.08745,38.70840,-77.08590,38.70945),'lower':(-77.08830,38.70745,-77.08680,38.70845),'fruit':(-77.08925,38.70640,-77.08715,38.70800),'farm':(-77.09140,38.70480,-77.08880,38.70670)}
name=sys.argv[1];x0,y0,x1,y1=boxes[name]
u0,v0=to_pixel(x0,y1,z);u1,v1=to_pixel(x1,y0,z)
im,X0,Y0=mosaic(z,u0,v0,u1,v1)
S=3
im=im.resize((im.width*S,im.height*S),Image.BILINEAR);d=ImageDraw.Draw(im)
def P(c):u,v=to_pixel(c[0],c[1],z);return ((u-X0)*S,(v-Y0)*S)
# OSM footways and barriers for reference
for f in E['features']:
    p=f['properties'];g=f['geometry']
    if g['type'] not in('LineString','MultiLineString'):continue
    lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
    if p.get('highway'):
        for l in lines:d.line([P(c) for c in l],fill=(160,60,0),width=2)
    elif p.get('barrier'):
        for l in lines:d.line([P(c) for c in l],fill=(90,90,90),width=2)
for f in G['features']:
    p=f['properties'];g=f['geometry'];k=p['kind']
    if g['type']=='LineString':
        pts=[P(c) for c in g['coordinates']]
        col={'walk':(0,110,255) if p.get('surface')=='gravel' else (0,200,90),'wall':(255,0,0),'fence':(255,255,255),'hedge':(0,90,0)}.get(k,(255,0,255))
        d.line(pts,fill=col,width=3 if k!='hedge' else 2)
    elif g['type']=='Polygon':
        pts=[P(c) for c in g['coordinates'][0]]
        col=(255,255,0) if k=='area' else (255,0,255)
        d.line(pts,fill=col,width=2)
    elif g['type']=='Point' and k in('gate','tree'):
        u,v=P(g['coordinates']);r=8 if k=='gate' else p.get('crown_radius_m',3)*4*S
        d.ellipse([u-r,v-r,u+r,v+r],outline=(255,0,255) if k=='gate' else (0,255,255),width=2)
im=im.crop((int((u0-X0)*S),int((v0-Y0)*S),int((u1-X0)*S),int((v1-Y0)*S)))
im.save(f'checktile-{name}.png');print(im.size)
