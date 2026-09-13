import sys
from PIL import Image,ImageDraw,ImageFont
src,out=sys.argv[1],sys.argv[2]
x0,y0,x1,y1=[int(v) for v in sys.argv[3:7]]   # crop box in source px
scale=float(sys.argv[7]); step=int(sys.argv[8])
im=Image.open(src).convert('RGB').crop((x0,y0,x1,y1))
im=im.resize((int(im.width*scale),int(im.height*scale)),Image.LANCZOS)
d=ImageDraw.Draw(im)
font=ImageFont.load_default(size=max(10,int(11*max(1,scale))))
sx=(x0//step+1)*step
for gx in range(sx,x1,step):
    X=(gx-x0)*scale
    d.line([(X,0),(X,im.height)],fill=(255,255,0) if gx%(step*5)==0 else (255,255,255),width=1)
    d.text((X+2,2),str(gx),fill=(255,255,0),font=font)
sy=(y0//step+1)*step
for gy in range(sy,y1,step):
    Y=(gy-y0)*scale
    d.line([(0,Y),(im.width,Y)],fill=(255,255,0) if gy%(step*5)==0 else (255,255,255),width=1)
    d.text((2,Y+2),str(gy),fill=(255,255,0),font=font)
im.save(out)
print(im.size)
