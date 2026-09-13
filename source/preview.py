import sys,os;sys.path.insert(0,'/home/claude/mv/work')
import tiles as T
from tiles import *
from PIL import Image
name=sys.argv[1];outdir=sys.argv[2];z=int(sys.argv[3]);S=float(sys.argv[4]) if len(sys.argv)>4 else 3
boxes={'upper':(-77.08745,38.70840,-77.08590,38.70945),'lower':(-77.08830,38.70745,-77.08680,38.70845),'fruit':(-77.08925,38.70640,-77.08715,38.70800),'farm':(-77.09140,38.70480,-77.08880,38.70670),'core':(-77.0900,38.7064,-77.0848,38.7101)}
x0,y0,x1,y1=boxes[name]
u0,v0=to_pixel(x0,y1,z);u1,v1=to_pixel(x1,y0,z)
tl=tiles_for_pixel_bbox(z,u0,v0,u1,v1);X0=min(t[0] for t in tl)*TILE;Y0=min(t[1] for t in tl)*TILE
W=(max(t[0] for t in tl)-min(t[0] for t in tl)+1)*TILE;H=(max(t[1] for t in tl)-min(t[1] for t in tl)+1)*TILE
im=Image.new('RGB',(W,H),(233,232,215))
for tx,ty in tl:
    p=f'{outdir}/{z}/{tx}/{ty}.webp'
    if not os.path.exists(p):p=tile_path(z,tx,ty)
    if os.path.exists(p):im.paste(Image.open(p).convert('RGB'),(tx*TILE-X0,ty*TILE-Y0))
im=im.crop((int(u0-X0),int(v0-Y0),int(u1-X0),int(v1-Y0)))
im=im.resize((int(im.width*S),int(im.height*S)),Image.BILINEAR);im.save(f'preview-{name}-z{z}.png');print(im.size)
