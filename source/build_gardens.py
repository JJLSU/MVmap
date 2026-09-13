import sys,json,importlib,math;sys.path.insert(0,'/home/claude/mv/work')
from georef import *
from geo import *
def cen(n):
    f=[f for f in LS['features'] if f['id'].endswith('/'+n)][0];cs=f['geometry']['coordinates'][0][:-1]
    m=[merc(*c) for c in cs];return (sum(a for a,b in m)/len(m),sum(b for a,b in m)/len(m))
FITS={
 'upper':fit_similarity([((945,172),(70.45,-66.1)),((2180,172),(117.2,-95.9)),((34,505),(27.5,-55.9))]),
 'lower':fit_similarity([((177,867),(-51.9,-172.6)),((2350,272),(46.4,-204.3))]),
 'fruit':fit_affine([((465,232),(-86.4,-209.6)),((470,1520),(-137.2,-289.3)),((2200,1515),(-33.3,-355.6)),((2200,240),(18.4,-275.3)),((1682,890),(-41.4,-294.3))]),
 'farm':fit_similarity([((398,132),(-333.8,-338.8)),((610,105),(-308.7,-352.3)),((600,285),(-325.3,-368.4)),((1590,145),(-198.2,-433.2))]),
}
GARDEN_IDS={'upper':'way/232717210','lower':'way/232717207','fruit':'way/232718129','farm':'way/232718134'}
GARDEN_NAMES={'upper':'Upper Garden','lower':'Lower Garden','fruit':'Fruit Garden & Nursery','farm':'Pioneer Farm'}
SRC='Google Maps 3D aerial imagery, manual interpretation (Sept 2026)'
feats=[];n=0
def ll(T,pts): return [[round(v,7) for v in unmerc(*T['fwd'](x,y))] for x,y in pts]
def px_m(T):  # metres per pixel (approx)
    a=T['fwd'](0,0);b=T['fwd'](100,0);return math.hypot(b[0]-a[0],b[1]-a[1])/100
for g in ['upper','lower','fruit']:
    m=importlib.import_module('trace_'+g);T=FITS[g];mpp=px_m(T)
    base=dict(garden=GARDEN_NAMES[g],garden_id=GARDEN_IDS[g],source=SRC,method='georeferenced aerial trace',surveyed=False,confidence='medium')
    def add(kind,geom,**props):
        global n;n+=1
        feats.append({'type':'Feature','id':f'aerial2026/{g}/{kind}/{n}','properties':{**base,'kind':kind,**props},'geometry':geom})
    add('enclosure',{'type':'Polygon','coordinates':[ll(T,m.enclosure+[m.enclosure[0]])]},name=GARDEN_NAMES[g]+' enclosure')
    for name,w,surf,routable,pts in m.walks:
        add('walk',{'type':'LineString','coordinates':ll(T,pts)},name=name,width_m=w,surface=surf,routable=routable,**({'casing':False} if 'forecourt' in name.lower() else {}))
    for name,kind,pts in m.areas:
        add('area',{'type':'Polygon','coordinates':[ll(T,pts+[pts[0]])]},name=name,area_type=kind)
    for name,pts in m.walls:
        add('wall',{'type':'LineString','coordinates':ll(T,pts)},name=name,material='brick')
    for f in getattr(m,'fences',[]):
        name,ft,pts=f;add('fence',{'type':'LineString','coordinates':ll(T,pts)},name=name,fence_type=ft)
    for name,pts in getattr(m,'hedges',[]):
        if len(pts)==1: add('hedge',{'type':'Point','coordinates':ll(T,pts)[0]},name=name)
        else: add('hedge',{'type':'LineString','coordinates':ll(T,pts)},name=name)
    for name,(x,y) in getattr(m,'gates',[]):
        add('gate',{'type':'Point','coordinates':ll(T,[(x,y)])[0]},name=name)
    for x,y,r in getattr(m,'trees',[]):
        add('tree',{'type':'Point','coordinates':ll(T,[(x,y)])[0]},name='canopy',crown_radius_m=round(r*mpp,1))
# Pioneer Farm: built in the OSM frame from the mapped lanes (aerial used for layout only)
import farm_build
from shapely.geometry import mapping
base=dict(garden='Pioneer Farm',garden_id='way/232718134',source='OpenStreetMap lanes + Google Maps 3D aerial layout interpretation (Sept 2026)',method='offset construction from mapped lanes',surveyed=False,confidence='low')
for kind,geom,props in farm_build.build():
    n+=1
    gj=mapping(geom)
    def conv(c):
        if isinstance(c[0],(int,float)): return [round(v,7) for v in unmerc(c[0],c[1])]
        return [conv(x) for x in c]
    gj={'type':gj['type'],'coordinates':conv(gj['coordinates'])}
    feats.append({'type':'Feature','id':f'aerial2026/farm/{kind}/{n}','properties':{**base,'kind':kind,**props},'geometry':gj})
fc={'type':'FeatureCollection','name':'Mount Vernon garden detail 2026','features':feats}
json.dump(fc,open('/home/claude/mv/dist/gardens-2026.geojson','w'),separators=(',',':'))
open('/home/claude/mv/dist/gardens.js','w').write('window.GARDENS='+json.dumps(fc,separators=(',',':'))+';\n')
import collections;print(len(feats),collections.Counter(f['properties']['kind'] for f in feats))
