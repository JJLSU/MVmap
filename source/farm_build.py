import sys;sys.path.insert(0,'/home/claude/mv/work')
from geo import *
from shapely.geometry import LineString,Polygon,Point,MultiLineString
from shapely.ops import unary_union,substring
import shapely
def line(i,rev=False):
    cs=[merc(*c) for c in by[i]['geometry']['coordinates']]
    return LineString(cs[::-1] if rev else cs)
axis=line('way/232727016',rev=True)          # west junction -> east pen gate
north=LineString(list(line('way/232726968',rev=True).coords)+list(line('way/232726933',rev=True).coords)[1:])  # barn -> east
south=line('way/232726959',rev=True)          # west junction -> east/river
L=axis.length
def slab(t0,t1,w=80):
    a=substring(axis,t0*L,t1*L)
    return a.buffer(w,cap_style=2)
def side_region(side):
    # region between the lane fence offset and the outer lane, on one side of the axis
    off=axis.parallel_offset(4.5,side)
    outer=(north if side=='left' else south)
    big=axis.buffer(60,cap_style=2)
    half=shapely.ops.split(big,axis)
    # choose half containing a point offset on that side
    probe=axis.interpolate(0.5,normalized=True)
    p2=axis.parallel_offset(10,side).interpolate(0.5,normalized=True)
    for g in half.geoms:
        if g.contains(p2): halfpoly=g;break
    # clip away lane corridor and outside the outer lane
    corridor=axis.buffer(4.5,cap_style=2)
    outer_clip=outer.buffer(3.0)
    # region beyond outer lane: split halfpoly by outer line and keep side containing p2
    region=halfpoly.difference(corridor).difference(outer_clip)
    parts=shapely.ops.split(region,outer) if False else region
    if region.geom_type=='MultiPolygon':
        region=[g for g in region.geoms if g.contains(p2) or g.distance(p2)<1][0]
    return region
FIELDS=[('Pioneer Farm field 1','crop','left',0.10,0.28),('Pioneer Farm field 2','crop_green','left',0.32,0.52),('Pioneer Farm field 3','crop','left',0.55,0.80),('Pioneer Farm kitchen garden','vegetable','left',0.83,0.98),
        ('Pioneer Farm field 4','crop','right',0.075,0.26),('Pioneer Farm field 5','crop','right',0.30,0.485),('Pioneer Farm field 6','crop','right',0.52,0.71),('Pioneer Farm field 8','crop','right',0.76,0.97)]
def build():
    out=[]  # (kind, geom(shapely), props)
    regions={'left':side_region('left'),'right':side_region('right')}
    for name,kind,side,t0,t1 in FIELDS:
        poly=regions[side].intersection(slab(t0,t1))
        # keep fields from getting too deep: clip to 24 m from axis
        poly=poly.intersection(axis.buffer(26,cap_style=2))
        if poly.geom_type=='MultiPolygon': poly=max(poly.geoms,key=lambda g:g.area)
        out.append(('area',poly.simplify(0.3),dict(name=name,area_type=kind)))
    # worm fences along the lane
    for side,nm in [('left','Field lane north worm fence'),('right','Field lane south worm fence')]:
        f=substring(axis,0.05*L,0.985*L).parallel_offset(4.0,side)
        out.append(('fence',f,dict(name=nm,fence_type='worm')))
    # outer worm fences: hull edge of each side region at 26 m or the lane clip
    for side,nm in [('left','North fields outer worm fence'),('right','South fields outer worm fence')]:
        reg=regions[side].intersection(axis.buffer(26,cap_style=2)).intersection(slab(0.06,0.985))
        if reg.geom_type=='MultiPolygon': reg=max(reg.geoms,key=lambda g:g.area)
        ring=LineString(reg.exterior.coords)
        # take the part of the ring farther than 6 m from the axis (the outer edge)
        outer=ring.difference(axis.buffer(6.5))
        if outer.geom_type=='MultiLineString': outer=max(outer.geoms,key=lambda g:g.length)
        out.append(('fence',outer.simplify(0.3),dict(name=nm,fence_type='worm')))
    enclosure=unary_union([regions['left'],regions['right'],axis.buffer(4.5,cap_style=2)]).intersection(axis.buffer(27,cap_style=2)).intersection(slab(0.03,1.0))
    if enclosure.geom_type=='MultiPolygon': enclosure=max(enclosure.geoms,key=lambda g:g.area)
    out.append(('enclosure',enclosure.simplify(0.3),dict(name='Pioneer Farm enclosure')))
    out.append(('walk',axis,dict(name='Pioneer Farm field lane',width_m=3.2,surface='gravel',routable=False,osm_id='way/232727016')))
    return out
if __name__=='__main__':
    for k,g,p in build(): print(k,p.get('name'),g.geom_type,round(g.area) if g.geom_type=='Polygon' else round(g.length))
