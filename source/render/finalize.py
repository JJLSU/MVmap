"""Grade, light sharpen, single WebP encode. finalize.py <png_root> <webp_out>"""
import sys,glob,os,numpy as np,cv2
from PIL import Image
sys.path.insert(0,'/home/claude/mv/work');from grade import grade
src,dst=sys.argv[1],sys.argv[2];n=0
for p in glob.glob(src+'/*/*/*.png'):
    a=grade(np.array(Image.open(p).convert('RGB')))
    b=cv2.GaussianBlur(a,(0,0),1.0);a=np.clip(a.astype(np.float32)+(a.astype(np.float32)-b.astype(np.float32))*0.35,0,255).astype(np.uint8)
    rel=os.path.relpath(p,src)[:-4]+'.webp';out=os.path.join(dst,rel);os.makedirs(os.path.dirname(out),exist_ok=True)
    Image.fromarray(a).save(out,'WEBP',quality=90,method=6);n+=1
print('finalized',n)
