import sys,glob,os
import numpy as np
from PIL import Image
def grade(arr,contrast=1.22,sat=1.18,gamma=1.22,tint=(0.96,1.0,1.03)):
    a=arr.astype(np.float32)/255.0
    a=np.clip(a,0,1)**gamma
    lum=(0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2])[...,None]
    a=lum+(a-lum)*sat
    a=0.5+(a-0.5)*contrast
    a=a*np.array(tint,dtype=np.float32)
    return np.clip(a*255,0,255).astype(np.uint8)
def hexgrade(h):
    c=np.array([[[int(h[1:3],16),int(h[3:5],16),int(h[5:7],16)]]],dtype=np.uint8);g=grade(c)[0,0];return '#%02x%02x%02x'%tuple(int(v) for v in g)
if __name__=='__main__':
    src=sys.argv[1];dst=sys.argv[2];n=0
    for p in glob.glob(src+'/*/*/*.webp'):
        rel=os.path.relpath(p,src);out=os.path.join(dst,rel);os.makedirs(os.path.dirname(out),exist_ok=True)
        Image.fromarray(grade(np.array(Image.open(p).convert('RGB')))).save(out,'WEBP',quality=88,method=6);n+=1
    print('graded',n)
    for h in ['#e2d8b4','#bfae86','#cbd69f','#b7c48c','#b08f78','#6e5642','#6b573f','#5a4631','#5e4a35','#6f8a5a','#c5a284','#b69b78','#9b8873','#e9e8d7']:
        print(h,'->',hexgrade(h))
