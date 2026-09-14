"""Resample the Edition 17 renders into a lossless PNG tile pyramid, zooms 14-20 (core render feathered in from zoom 17)."""
from PIL import Image
import pathlib,json,math,sys
import numpy as np
Image.MAX_IMAGE_PIXELS=None
R=pathlib.Path('/home/claude/mv/render');m=json.load(open('/home/claude/mv/dist/baked/projection.json'))
out=pathlib.Path(sys.argv[1]);zooms=[int(z) for z in sys.argv[2].split(',')]
full=Image.open(R/'estate-render.png').convert('RGB');B=m['bake']['bounds']
core=None
if (R/'core-render.png').exists():
    core=Image.open(R/'core-render.png').convert('RGB');C=json.load(open(R/'core_bake.json'))['bounds']
count=0
for z in zooms:
 s=2**(z-17);lo=math.floor(B[0]*s/512);hi=math.ceil(B[2]*s/512);top=math.floor(-B[3]*s/512);bot=math.ceil(-B[1]*s/512)
 for x in range(lo,hi):
  for y in range(top,bot):
   bounds=[x*512/s,-(y+1)*512/s,(x+1)*512/s,-y*512/s]
   if z>=20 and core is not None:
    # zoom 20 only where the core render covers the tile; elsewhere the map reuses zoom 19
    if bounds[2]<=C[0] or bounds[0]>=C[2] or bounds[3]<=C[1] or bounds[1]>=C[3]:continue
   def sample(im,bb):
    sx=im.width/(bb[2]-bb[0]);sy=im.height/(bb[3]-bb[1]);return im.transform((512,512),Image.Transform.AFFINE,(sx/s,0,(bounds[0]-bb[0])*sx,0,sy/s,(bb[3]-bounds[3])*sy),Image.Resampling.BICUBIC,fillcolor=(225,224,200))
   tile=sample(full,B)
   if z>=17 and core is not None:
    ix0=max(bounds[0],C[0]);ix1=min(bounds[2],C[2]);iy0=max(bounds[1],C[1]);iy1=min(bounds[3],C[3])
    if ix1>ix0 and iy1>iy0:
     ct=sample(core,C)
     xx=bounds[0]+(np.arange(512)+.5)/s;yy=bounds[3]-(np.arange(512)+.5)/s
     edge=np.minimum(np.minimum((xx-C[0])[None,:],(C[2]-xx)[None,:]),np.minimum((yy-C[1])[:,None],(C[3]-yy)[:,None]))
     mask=Image.fromarray((np.clip(edge/12,0,1)*255).astype('uint8'));tile.paste(ct,(0,0),mask)
   p=out/str(z)/str(x);p.mkdir(parents=True,exist_ok=True);tile.save(p/(str(y)+'.png'));count+=1
print('tiles',count)
