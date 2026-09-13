import sys,json;sys.path.insert(0,'/home/claude/mv/work')
from geo import *
from shapely.geometry import LineString,Polygon,Point,shape,MultiLineString
from shapely.ops import unary_union,linemerge,nearest_points
G=json.load(open('/home/claude/mv/dist/gardens-2026.geojson'))
pathTypes={'footway','path','pedestrian','steps','cycleway','bridleway','track','service','residential','living_street','unclassified'}
def M(coords): return [merc(*c) for c in coords]
def U(coords): return [[round(v,7) for v in unmerc(*c)] for c in coords]
enclosures={f['properties']['garden']:Polygon(M(f['geometry']['coordinates'][0])) for f in G['features'] if f['properties']['kind']=='enclosure'}
encl_union=unary_union(list(enclosures.values()))
# --- superseded OSM ways: highway lines mostly inside an enclosure (except farm), barriers mostly within 6 m of an enclosure edge
superseded_ways=[];superseded_barriers=[]
non_farm=unary_union([g for n,g in enclosures.items() if n!='Pioneer Farm'])
for f in E['features']:
    p=f['properties'];g=f['geometry']
    if g['type'] not in('LineString','MultiLineString'):continue
    lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
    geom=unary_union([LineString(M(l)) for l in lines])
    if geom.length==0:continue
    if p.get('highway') in pathTypes:
        inside=geom.intersection(non_farm.buffer(1.5)).length/geom.length
        if inside>0.5: superseded_ways.append(f['id'])
    elif p.get('barrier'):
        near=geom.intersection(non_farm.buffer(7)).length/geom.length
        if near>0.6: superseded_barriers.append(f['id'])
print('superseded ways',superseded_ways);print('superseded barriers',superseded_barriers)
# --- OSM graph nodes that remain
nodes=[]
for f in E['features']:
    p=f['properties'];g=f['geometry']
    if p.get('highway') in pathTypes and g['type'] in('LineString','MultiLineString') and f['id'] not in superseded_ways and p.get('access') not in('no','private') and p.get('foot') not in('no','private') and not p.get('construction'):
        lines=[g['coordinates']] if g['type']=='LineString' else g['coordinates']
        for l in lines: nodes.extend([tuple(c) for c in l])
nodes=list(set(nodes));node_pts=[(Point(merc(*c)),c) for c in nodes]
# --- node the walk network (routable walks only) per garden
routing=[];connectors=[]
walks=[f for f in G['features'] if f['kind' if False else 'properties']['kind']=='walk' and f['properties'].get('routable')]
lines=[LineString(M(f['geometry']['coordinates'])) for f in walks]
# snap walk endpoints onto nearby other walks (T-junctions) before noding
coords=[list(l.coords) for l in lines]
for i,l in enumerate(lines):
    for pt in (l.coords[0],l.coords[-1]):
        P=Point(pt)
        for j,l2 in enumerate(lines):
            if i==j:continue
            d=l2.distance(P)
            if 0<d<1.2:
                # insert projected point into l2's coordinate list
                proj=l2.interpolate(l2.project(P));c2=coords[j]
                # find segment
                best=None;bd=1e9
                for k in range(1,len(c2)):
                    seg=LineString([c2[k-1],c2[k]]);dd=seg.distance(proj)
                    if dd<bd:bd=dd;best=k
                c2.insert(best,(proj.x,proj.y))
                # also move the endpoint exactly onto proj
                ci=coords[i];idx=0 if pt==l.coords[0] else len(ci)-1;ci[idx]=(proj.x,proj.y)
lines=[LineString(c) for c in coords]
noded=unary_union(lines)
segs=list(noded.geoms) if noded.geom_type=='MultiLineString' else [noded]
for s in segs:
    cs=list(s.coords)
    for i in range(1,len(cs)): routing.append(U([cs[i-1],cs[i]]))
# endpoints (degree-1 nodes) -> connect to nearest OSM node within 18 m
from collections import Counter
deg=Counter()
for s in segs:
    cs=list(s.coords);deg[cs[0]]+=1;deg[cs[-1]]+=1
for pt,dgr in deg.items():
    if dgr!=1:continue
    P=Point(pt);best=None;bd=1e9
    for np_,c in node_pts:
        d=P.distance(np_)
        if d<bd: bd=d;best=c
    print('dangling',[round(v,1) for v in pt],'nearest OSM node',round(bd,1))
    if bd<=18:
        a=U([pt])[0]
        connectors.append([a,[best[0],best[1]]])
# gate connectors: nearest walk vertex <-> nearest OSM node
walk_vertices=set()
for s_ in segs:
    for c in s_.coords: walk_vertices.add(c)
walk_vertices=list(walk_vertices)
for f in G['features']:
    if f['properties']['kind']!='gate':continue
    gp=Point(merc(*f['geometry']['coordinates']))
    wv=min(walk_vertices,key=lambda c:gp.distance(Point(c)))
    best=None;bd=1e9
    for np_,c in node_pts:
        d=gp.distance(np_)
        if d<bd:bd=d;best=c
    print('gate',f['properties']['name'],'walk vertex',round(gp.distance(Point(wv)),1),'osm node',round(bd,1))
    if bd<=40 and gp.distance(Point(wv))<8:
        a=U([wv])[0];pair=[a,[best[0],best[1]]]
        if pair not in connectors: connectors.append(pair)
print('routing segments',len(routing),'connectors',len(connectors))
out={'type':'FeatureCollection','name':G['name'],'features':G['features'],'superseded_ways':superseded_ways,'superseded_barriers':superseded_barriers,'routing_segments':routing,'connectors':connectors}
open('/home/claude/mv/dist/gardens.js','w').write('window.GARDENS='+json.dumps(out,separators=(',',':'))+';\n')
json.dump(out,open('/home/claude/mv/dist/gardens-2026.geojson','w'),separators=(',',':'))
