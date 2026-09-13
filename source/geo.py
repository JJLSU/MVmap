import json,math
R=6378137
P=json.load(open('/home/claude/mv/dist/baked/projection.json'))
c=P['cos_lat'];ox,oy=P['mercator_origin']
def merc(lon,lat):
    return ((lon*math.pi/180*R-ox)*c,(R*math.log(math.tan(math.pi/4+lat*math.pi/360))-oy)*c)
def unmerc(x,y):
    lon=(x/c+ox)/R*180/math.pi
    lat=(2*math.atan(math.exp((y/c+oy)/R))-math.pi/2)*180/math.pi
    return lon,lat
E=json.load(open('/home/claude/mv/dist/estate.geojson'))
LS=json.load(open('/home/claude/mv/dist/landscape-2025.geojson'))
by={f['id']:f for f in E['features']}
def coords_iter(g):
    t=g['type'];cs=g['coordinates']
    if t=='Point': yield [cs]
    elif t in('LineString',): yield cs
    elif t=='Polygon':
        for r in cs: yield r
    elif t=='MultiLineString':
        for r in cs: yield r
    elif t=='MultiPolygon':
        for p in cs:
            for r in p: yield r
def bbox_of(g):
    xs=[];ys=[]
    for r in coords_iter(g):
        for x,y in r: xs.append(x);ys.append(y)
    return min(xs),min(ys),max(xs),max(ys)
