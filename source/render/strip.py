import bpy,sys,time,json;sys.path.insert(0,'/home/claude/mv/render')
from setup_core import *
which,i,n=sys.argv[-3],int(sys.argv[-2]),int(sys.argv[-1])
bpy.ops.wm.open_mainfile(filepath='/home/claude/mv/blend14/Mount-Vernon-Edition14-Master.blend')
s=bpy.context.scene;hide_stray()
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.cycles.samples=48;s.cycles.adaptive_min_samples=12
if which=='core':
    b=setup_core(s,6144);json.dump({'bounds':b,'width':s.render.resolution_x,'height':s.render.resolution_y},open('/home/claude/mv/render/core_bake.json','w'))
H=s.render.resolution_y
# strip i of n, top to bottom in image space; border coords are 0..1 from the bottom
y1=1-i/n;y0=1-(i+1)/n
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=y0;s.render.border_max_y=y1
s.render.filepath=f'/home/claude/mv/render/strips/{which}-{i:02d}.png'
t=time.time();bpy.ops.render.render(write_still=True);print('STRIP DONE',which,i,n,'seconds',round(time.time()-t),'res',s.render.resolution_x,H)
