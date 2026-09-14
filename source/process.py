import sys,json,math,os,shutil;sys.path.insert(0,'/home/claude/mv/work')
from render import *
OUT=sys.argv[1] if len(sys.argv)>1 else '/home/claude/mv/work/tiles-out'
ZOOMS=[int(z) for z in sys.argv[2].split(',')] if len(sys.argv)>2 else [14,15,16,17,18,19]
GARDENS=sys.argv[3].split(',') if len(sys.argv)>3 else ['Upper Garden','Lower Garden','Fruit Garden & Nursery','Pioneer Farm']
os.makedirs(OUT,exist_ok=True)
pathTypes={'footway','path','pedestrian','steps','cycleway','bridleway','track','service','residential','living_street','unclassified'}
byid={f['id']:f for f in E['features']}
def geo_poly_px(coords,z,ox,oy):
    return Polygon([(u-ox,v-oy) for u,v in (to_pixel(c[0],c[1],z) for c in dens(coords))])
def geo_line_px(coords,z,ox,oy):
    return LineString([(u-ox,v-oy) for u,v in (to_pixel(c[0],c[1],z) for c in dens(coords))])
# trees near gardens for protection
trees=[]
for f in LS['features']:
    if f['properties']['kind']=='tree_candidate':trees.append((f['geometry']['coordinates'],f['properties'].get('crown_radius_m',3)))
for f in E['features']:
    if f['properties'].get('natural')=='tree' and f['geometry']['type']=='Point':trees.append((f['geometry']['coordinates'],3.5))
encl_geo={f['properties']['garden']:f for f in G['features'] if f['properties']['kind']=='enclosure'}
tiles_done={}
def tile_key(z,tx,ty):return f'{z}/{tx}/{ty}'
def load_tile(z,tx,ty):
    k=tile_key(z,tx,ty)
    if k in tiles_done:return tiles_done[k]
    p=tile_path(z,tx,ty)
    im=Image.open(p).convert('RGB') if os.path.exists(p) else Image.new('RGB',(TILE,TILE),(233,232,215))
    tiles_done[k]=im;return im
for z in ZOOMS:
    s=2**(z-17);ss=4 if z<=17 else (3 if z<=19 else 2)
    for garden in GARDENS:
        encl=encl_geo[garden];gid=encl['properties']['garden_id']
        # extent in tile px
        pts=[to_pixel(c[0],c[1],z) for c in encl['geometry']['coordinates'][0]]
        osm_poly=byid[gid]['geometry']['coordinates'][0]
        pts+= [to_pixel(c[0],c[1],z) for c in osm_poly]
        us=[p[0] for p in pts];vs=[p[1] for p in pts]
        pad=12*s+4
        for tx,ty in tiles_for_pixel_bbox(z,min(us)-pad,min(vs)-pad,max(us)+pad,max(vs)+pad):
            ox,oy=tx*TILE,ty*TILE
            if not os.path.exists(tile_path(z,tx,ty)) and tile_key(z,tx,ty) not in tiles_done:continue
            orig=load_tile(z,tx,ty)
            res=render_garden_tile(garden,z,tx,ty,orig,ss)
            # inpaint region: OSM garden polygon + superseded path strips, minus enclosure
            encl_px=geo_poly_px(encl['geometry']['coordinates'][0],z,ox,oy)
            regionB=[geo_poly_px(osm_poly,z,ox,oy).buffer(1.5*s)] if garden!='Pioneer Farm' else []
            for wid in G['superseded_ways']:
                f=byid.get(wid)
                if not f:continue
                lines=[f['geometry']['coordinates']] if f['geometry']['type']=='LineString' else f['geometry']['coordinates']
                for l in lines:regionB.append(geo_line_px(l,z,ox,oy).buffer(2.4*s+1.0))
            all_encl=unary_union([geo_poly_px(e['geometry']['coordinates'][0],z,ox,oy) for e in encl_geo.values()])
            B=unary_union(regionB).difference(all_encl.buffer(-0.5)) if regionB else None
            tilebox=box(0,0,TILE,TILE)
            if res is None and (B is None or not B.intersects(tilebox)):continue
            arr=np.array(orig).astype(np.float32)
            if B is not None and B.intersects(tilebox):
                bm=Image.new('L',(TILE,TILE),0);bd=ImageDraw.Draw(bm)
                geoms=B.geoms if B.geom_type=='MultiPolygon' else [B]
                for g in geoms:
                    if g.is_empty or not g.intersects(tilebox):continue
                    bd.polygon(list(g.exterior.coords),fill=255)
                    for ring in g.interiors:bd.polygon(list(ring.coords),fill=0)
                bmask=np.array(bm)
                if bmask.any():
                    src=np.array(orig)
                    inp=cv2.inpaint(cv2.cvtColor(src,cv2.COLOR_RGB2BGR),(bmask>0).astype(np.uint8),int(4*s)+3,cv2.INPAINT_TELEA)
                    inp=cv2.cvtColor(inp,cv2.COLOR_BGR2RGB).astype(np.float32)
                    a=(bmask/255.0)[:,:,None];arr=arr*(1-a)+inp*a
            if res is not None:
                new,alpha=res
                a=(np.array(alpha).astype(np.float32)/255.0)
                # tree protection: keep original pixels that differ from ring-median within discs
                prot=np.zeros((TILE,TILE),np.float32)
                orig_arr=np.array(orig).astype(np.float32)
                for (lon,lat),r in trees:
                    u,v=to_pixel(lon,lat,z);u-=ox;v-=oy
                    R=r*s;cu,cv_=u,v-0.8*R
                    if cu<-2*R or cv_<-2*R or cu>TILE+2*R or cv_>TILE+2*R:continue
                    if not encl_px.buffer(R*1.6).contains(Point(u,v)):continue
                    yy,xx=np.mgrid[0:TILE,0:TILE];dist=np.hypot(xx-cu,yy-cv_)
                    disc=dist<=R*1.45;ring=(dist>R*1.45)&(dist<=R*1.9)
                    if not ring.any():continue
                    med=np.median(orig_arr[ring],axis=0)
                    diff=np.linalg.norm(orig_arr-med,axis=2)
                    prot=np.maximum(prot,(disc&(diff>16)).astype(np.float32))
                if prot.any():
                    prot=cv2.GaussianBlur(prot,(0,0),0.7);prot=np.clip(prot*1.5,0,1)
                a=a*(1-prot)
                arr=arr*(1-a[:,:,None])+np.array(new).astype(np.float32)*a[:,:,None]
            im=Image.fromarray(np.clip(arr,0,255).astype(np.uint8))
            tiles_done[tile_key(z,tx,ty)]=im
# write out (processed tiles) and copy every untouched source tile so OUT is a complete pyramid
import glob,shutil
n=0
for src in glob.glob(ROOT+'/*/*/*.png')+glob.glob(ROOT+'/*/*/*.webp'):
    rel=os.path.relpath(src,ROOT);k=rel.rsplit('.',1)[0]
    if k in tiles_done:continue
    dst=os.path.join(OUT,k+'.png');os.makedirs(os.path.dirname(dst),exist_ok=True)
    Image.open(src).convert('RGB').save(dst,'PNG')
for k,im in tiles_done.items():
    p=os.path.join(OUT,k+'.png');os.makedirs(os.path.dirname(p),exist_ok=True);im.save(p,'PNG');n+=1
print('tiles written',n)
