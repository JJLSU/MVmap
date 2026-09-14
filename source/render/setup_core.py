import bpy,json,math,sys,time
from mathutils import Vector
m=json.load(open('/home/claude/mv/blend/dist/baked/projection.json'))
def xy(lon,lat):return ((math.radians(lon)*6378137-m['mercator_origin'][0])*m['cos_lat'],(6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))-m['mercator_origin'][1])*m['cos_lat'])
def setup_core(scene,width):
    x0,y0=xy(-77.0901,38.7063);x1,y1=xy(-77.0846,38.7101);bounds=[x0,m['alpha']*y0-5,x1,m['alpha']*y1+28];w=bounds[2]-bounds[0];h=bounds[3]-bounds[1]
    target=Vector(((x0+x1)/2,(bounds[1]+bounds[3])/2/m['alpha'],0))
    cam=scene.camera;cam.location=target+Vector((0,-m['beta']*2500,m['alpha']*2500));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=w
    scene.render.resolution_x=width;scene.render.resolution_y=round(width*h/w);scene.render.resolution_percentage=100
    return bounds
def hide_stray():
    n=0
    for o in bpy.data.objects:
        if 'way/1028542424' in o.name: o.hide_render=True;n+=1
    return n
