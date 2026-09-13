import sys,json,math,os,random;sys.path.insert(0,'/home/claude/mv/work')
from tiles import *
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFilter
from shapely.geometry import Polygon,LineString,Point,MultiPolygon,box
from shapely.ops import unary_union
G=json.load(open('/home/claude/mv/dist/gardens-2026.geojson'))
random.seed(7)
def dens(coords,step=4.0):
    out=[]
    for i,c in enumerate(coords):
        if i:
            q=coords[i-1];x0,y0=merc(*q);x1,y1=merc(*c);n=max(1,int(math.hypot(x1-x0,y1-y0)/step))
            for j in range(1,n): out.append(unmerc(x0+(x1-x0)*j/n,y0+(y1-y0)*j/n))
        out.append(tuple(c))
    return out
def P(coords,z,ox,oy,SS):  # lon/lat -> canvas px
    return [((u-ox)*SS,(v-oy)*SS) for u,v in (to_pixel(c[0],c[1],z) for c in dens(coords))]
COL=dict(turf=(199,205,157),turf_dark=(186,196,146),gravel=(230,218,185),casing=(196,182,148),grass_walk=(204,213,155),
 bed_dark=(163,177,122),bed_light=(190,202,148),box=(118,146,94),parterre_ground=(222,211,178),parterre_green=(150,171,116),
 shrub_a=(168,184,136),shrub_b=(150,170,121),frame=(226,221,206),frame_edge=(150,140,120),crop=(206,188,146),crop_row=(190,171,130),
 cropg=(172,189,130),cropg_row=(152,172,112),ring=(176,156,124),wall=(168,138,114),wall_shadow=(120,96,78),fence=(104,86,62),hedge=(112,140,90))
def longest_edge_angle(pts):
    best=0;ang=0
    for i in range(1,len(pts)):
        (x0,y0),(x1,y1)=pts[i-1],pts[i];L=math.hypot(x1-x0,y1-y0)
        if L>best:best=L;ang=math.atan2(y1-y0,x1-x0)
    return ang
def stripes(canvas,poly_pts,pitch_px,c1,c2,angle,phase=0.0,width_frac=0.5):
    # fill polygon with alternating stripes perpendicular to `angle` direction? stripes run along direction perpendicular to longest edge => lines parallel to short axis
    W,H=canvas.size
    layer=Image.new('RGB',(W,H),c2);d=ImageDraw.Draw(layer)
    ux,uy=math.cos(angle),math.sin(angle)  # along longest edge
    xs=[p[0] for p in poly_pts];ys=[p[1] for p in poly_pts]
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2;R=math.hypot(max(xs)-min(xs),max(ys)-min(ys))/2+pitch_px
    n=int(2*R/pitch_px)+2
    for k in range(-n,n+1):
        t=(k+phase)*pitch_px;px=cx+ux*t;py=cy+uy*t
        # stripe line perpendicular to (ux,uy)
        d.line([(px-uy*R,py+ux*R),(px+uy*R,py-ux*R)],fill=c1,width=max(1,int(pitch_px*width_frac)))
    m=Image.new('L',(W,H),0);ImageDraw.Draw(m).polygon(poly_pts,fill=255)
    canvas.paste(layer,(0,0),m)
def fill_poly(canvas,pts,color,outline=None,width=1):
    ImageDraw.Draw(canvas).polygon(pts,fill=color,outline=outline,width=width)
def poly_inset(pts,d_px):
    try:
        p=Polygon(pts).buffer(-d_px,join_style=2)
        if p.is_empty:return None
        if p.geom_type=='MultiPolygon':p=max(p.geoms,key=lambda g:g.area)
        return list(p.exterior.coords)
    except Exception:return None
def worm(coords_px,panel_px,amp_px):
    out=[];side=1
    for i in range(1,len(coords_px)):
        (ax,ay),(bx,by)=coords_px[i-1],coords_px[i];L=math.hypot(bx-ax,by-ay)
        if L==0:continue
        n=max(1,round(L/panel_px));dx,dy=(bx-ax)/L,(by-ay)/L
        if not out:out.append((ax,ay))
        for j in range(n):
            t=(j+.5)/n;mx,my=ax+(bx-ax)*t,ay+(by-ay)*t;out.append((mx-dy*amp_px*side,my+dx*amp_px*side));side=-side
        out.append((bx,by))
    return out
def cloud(W,H,amp,seed):
    rs=np.random.RandomState(seed);small=rs.rand(max(2,H//48)+2,max(2,W//48)+2).astype(np.float32)
    big=cv2.resize(small,(W,H),interpolation=cv2.INTER_CUBIC);big=cv2.GaussianBlur(big,(0,0),max(1,W/60))
    return (big-big.mean())*amp*2
SPRITES=[{'img':Image.open('/home/claude/mv/work/sprite0.png').convert('RGBA'),'r_m':4.3},{'img':Image.open('/home/claude/mv/work/sprite1.png').convert('RGBA'),'r_m':3.91}]
def render_garden_tile(garden,z,tx,ty,orig,ss):
    """returns (new RGB PIL image for the tile, alpha mask L) or None"""
    s=2**(z-17)  # px per metre
    ox,oy=tx*TILE,ty*TILE
    W=H=TILE*ss
    feats=[f for f in G['features'] if f['properties']['garden']==garden]
    encl=[f for f in feats if f['properties']['kind']=='enclosure'][0]
    encl_px=P(encl['geometry']['coordinates'][0],z,ox,oy,ss)
    epoly=Polygon(encl_px)
    if not epoly.intersects(box(-40,-40,W+40,H+40)):return None
    canvas=orig.resize((W,H),Image.BILINEAR)
    d=ImageDraw.Draw(canvas)
    # 1. base turf with cloud variation
    base=np.zeros((H,W,3),np.float32);base[:]=COL['turf'];cl=cloud(W,H,7,hash((garden,z,tx,ty))%1000)
    for k in range(3):base[:,:,k]+=cl
    turf=Image.fromarray(np.clip(base,0,255).astype(np.uint8))
    m=Image.new('L',(W,H),0);ImageDraw.Draw(m).polygon(encl_px,fill=255)
    canvas.paste(turf,(0,0),m)
    # 2. areas
    areas=[f for f in feats if f['properties']['kind']=='area']
    order={'turf':0,'grass_walk':1,'orchard':1,'gravel':1,'vegetable':2,'crop':2,'crop_green':2,'parterre':2,'shrubbery':2,'cold_frame':3}
    for f in sorted(areas,key=lambda f:order.get(f['properties']['area_type'],2)):
        t=f['properties']['area_type'];pts=P(f['geometry']['coordinates'][0],z,ox,oy,ss)
        if not Polygon(pts).intersects(box(-2,-2,W+2,H+2)):continue
        ang=longest_edge_angle(pts)
        if t=='turf':fill_poly(canvas,pts,COL['turf'])
        elif t=='grass_walk':fill_poly(canvas,pts,COL['grass_walk'])
        elif t=='gravel':fill_poly(canvas,pts,COL['gravel'])
        elif t=='orchard':
            fill_poly(canvas,pts,(203,209,160))
            # tree rings on a grid aligned with the polygon
            poly=Polygon(pts);cx,cy=poly.centroid.x,poly.centroid.y;ux,uy=math.cos(ang),math.sin(ang);sp=8.6*s*ss;R=1.25*s*ss
            n=int(poly.length/sp)+3
            for i in range(-n,n+1):
                for j in range(-n,n+1):
                    px=cx+ux*i*sp-uy*j*sp;py=cy+uy*i*sp+ux*j*sp
                    if poly.buffer(-2.5*s*ss).contains(Point(px,py)):
                        d.ellipse([px-R,py-R,px+R,py+R],fill=COL['ring'])
        elif t in('vegetable','crop','crop_green'):
            boxed=garden in('Upper Garden','Lower Garden') and t=='vegetable'
            inner=poly_inset(pts,0.55*s*ss) if boxed else pts
            if boxed:fill_poly(canvas,pts,COL['box'])
            if inner is None:inner=pts
            if t=='vegetable':stripes(canvas,inner,1.3*s*ss,COL['bed_dark'],COL['bed_light'],ang,width_frac=.55)
            elif t=='crop':stripes(canvas,inner,0.9*s*ss,COL['crop_row'],COL['crop'],ang+math.pi/2,width_frac=.3)
            else:stripes(canvas,inner,0.9*s*ss,COL['cropg_row'],COL['cropg'],ang+math.pi/2,width_frac=.35)
        elif t=='parterre':
            fill_poly(canvas,pts,COL['box']);inner=poly_inset(pts,0.6*s*ss) or pts
            fill_poly(canvas,inner,COL['parterre_ground'])
            poly=Polygon(inner);minx,miny,maxx,maxy=poly.bounds;cx,cy=poly.centroid.x,poly.centroid.y
            # box-work: quartered scroll pattern -> four lobes + central diamond, rotated with the bed
            ux,uy=math.cos(ang),math.sin(ang);L=Polygon(pts).length/2  # approx half perimeter
            # bed half sizes along/across
            proj=[( (x-cx)*ux+(y-cy)*uy, -(x-cx)*uy+(y-cy)*ux) for x,y in inner]
            ha=max(abs(a) for a,b in proj);hb=max(abs(b) for a,b in proj)
            def T(a,b):return (cx+a*ux-b*uy,cy+a*uy+b*ux)
            g=COL['parterre_green']
            for sa in(-1,1):
                for sb in(-1,1):
                    ca,cb=sa*ha*0.5,sb*hb*0.45;r=min(ha,hb)*0.36
                    q=[T(ca+r*math.cos(k/12*2*math.pi)*1.15,cb+r*math.sin(k/12*2*math.pi)*0.8) for k in range(12)]
                    d.polygon(q,fill=g)
            r=min(ha,hb)*0.45
            d.polygon([T(r*1.6,0),T(0,r*0.9),T(-r*1.6,0),T(0,-r*0.9)],fill=g)
            r2=min(ha,hb)*0.14;d.ellipse([cx-r2,cy-r2,cx+r2,cy+r2],fill=COL['parterre_ground'])
        elif t=='shrubbery':
            fill_poly(canvas,pts,COL['turf_dark']);poly=Polygon(pts);minx,miny,maxx,maxy=poly.bounds
            rs=random.Random(11)
            for k in range(int(poly.area/(9*s*s*ss*ss))+6):
                for _ in range(20):
                    px=rs.uniform(minx,maxx);py=rs.uniform(miny,maxy)
                    if poly.buffer(-1.0*s*ss).contains(Point(px,py)):break
                else:continue
                r=rs.uniform(1.6,3.2)*s*ss;c=COL['shrub_a'] if rs.random()<.5 else COL['shrub_b']
                d.ellipse([px-r,py-r*.8,px+r,py+r*.8],fill=c)
        elif t=='cold_frame':
            fill_poly(canvas,pts,COL['gravel']);poly=Polygon(pts);cx,cy=poly.centroid.x,poly.centroid.y;ux,uy=math.cos(ang),math.sin(ang)
            proj=[((x-cx)*ux+(y-cy)*uy,-(x-cx)*uy+(y-cy)*ux) for x,y in pts];ha=max(abs(a) for a,b in proj);hb=max(abs(b) for a,b in proj)
            def T(a,b):return (cx+a*ux-b*uy,cy+a*uy+b*ux)
            for k in range(4):
                a0=-ha+ha*2*(k+0.1)/4;a1=-ha+ha*2*(k+0.9)/4
                d.polygon([T(a0,-hb*.7),T(a1,-hb*.7),T(a1,hb*.7),T(a0,hb*.7)],fill=COL['frame'],outline=COL['frame_edge'],width=max(1,int(.12*s*ss)))
    # 3. walks: casings then fills
    walks=[f for f in feats if f['properties']['kind']=='walk']
    for f in walks:
        if f['properties'].get('casing') is False:continue
        pts=P(f['geometry']['coordinates'],z,ox,oy,ss);w=f['properties']['width_m']
        d.line(pts,fill=COL['casing'],width=max(1,int((w+0.5)*s*ss)),joint='curve')
    for f in walks:
        pts=P(f['geometry']['coordinates'],z,ox,oy,ss);w=f['properties']['width_m'];grass=f['properties'].get('surface')=='grass'
        d.line(pts,fill=COL['grass_walk'] if grass else COL['gravel'],width=max(1,int(w*s*ss)),joint='curve')
    # 4. hedges
    for f in feats:
        if f['properties']['kind']=='hedge' and f['geometry']['type']=='LineString':
            pts=P(f['geometry']['coordinates'],z,ox,oy,ss);d.line(pts,fill=COL['hedge'],width=max(1,int(.6*s*ss)),joint='curve')
    # 5. walls (with oblique shadow) and fences
    for f in feats:
        k=f['properties']['kind']
        if k=='wall':
            pts=P(f['geometry']['coordinates'],z,ox,oy,ss);w=max(1,int(.6*s*ss))
            d.line([(x,y+w*.9) for x,y in pts],fill=COL['wall_shadow'],width=w,joint='curve');d.line(pts,fill=COL['wall'],width=w,joint='curve')
        elif k=='fence':
            pts=P(f['geometry']['coordinates'],z,ox,oy,ss)
            if f['properties'].get('fence_type')=='worm':
                d.line(worm(pts,3.3*s*ss,1.0*s*ss),fill=COL['fence'],width=max(1,int(.22*s*ss)))
            else:
                d.line(pts,fill=COL['fence'],width=max(1,int(.16*s*ss)),joint='curve')
                # posts
                pp=max(1,int(.38*s*ss))
                for i in range(1,len(pts)):
                    (ax,ay),(bx,by)=pts[i-1],pts[i];L=math.hypot(bx-ax,by-ay);n=int(L/(3.0*s*ss))
                    for j in range(n+1):
                        t=j/max(1,n) if n else 0;px=ax+(bx-ax)*t;py=ay+(by-ay)*t;d.ellipse([px-pp,py-pp,px+pp,py+pp],fill=COL['fence'])
    # 6. trees traced from the aerial, drawn with canopy sprites cut from the existing bake
    for i,f in enumerate([f for f in feats if f['properties']['kind']=='tree']):
        lon,lat=f['geometry']['coordinates'];r=f['properties'].get('crown_radius_m',3.5)
        u,v=to_pixel(lon,lat,z);u=(u-ox)*ss;v=(v-oy)*ss;R=r*s*ss
        if u<-3*R or v<-3*R or u>W+3*R or v>H+3*R:continue
        sp=SPRITES[i%len(SPRITES)];scale=R/(sp['r_m']*4)
        im=sp['img'];sz=(max(2,int(im.width*scale)),max(2,int(im.height*scale)))
        im=im.resize(sz,Image.LANCZOS)
        canvas.paste(im,(int(u-sz[0]/2),int(v-0.8*R-sz[1]/2)),im)
    # alpha mask = enclosure, feathered
    alpha=Image.new('L',(W,H),0);ad=ImageDraw.Draw(alpha);ad.polygon(encl_px,fill=255)
    # walks, walls and fences are also blended in where they run outside the enclosure (gates, approaches)
    for f in feats:
        k=f['properties']['kind']
        if f['geometry']['type']!='LineString' or k not in('walk','wall','fence'):continue
        pts=P(f['geometry']['coordinates'],z,ox,oy,ss)
        wm=(f['properties']['width_m']+0.9) if k=='walk' else (1.0 if k=='wall' else 2.6 if f['properties'].get('fence_type')=='worm' else 0.9)
        ad.line(pts,fill=255,width=max(2,int(wm*s*ss)),joint='curve')
    out=canvas.resize((TILE,TILE),Image.LANCZOS);alpha=alpha.resize((TILE,TILE),Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
    return out,alpha
