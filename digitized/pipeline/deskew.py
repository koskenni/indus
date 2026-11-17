import numpy as np, cv2, sys, glob, os
from PIL import Image
S=sys.argv[1]; os.makedirs(f'{S}/desk',exist_ok=True)
def score(a,ang):
    h,w=a.shape
    M=cv2.getRotationMatrix2D((w/2,h/2),ang,1)
    r=cv2.warpAffine(a,M,(w,h),flags=cv2.INTER_NEAREST)
    p=r.sum(1).astype(float); return ((p[1:]-p[:-1])**2).sum()
for pg in range(1,60):
    a=(np.array(Image.open(f'{S}/pages/pg-{pg:03d}.png').convert('L'))<128).astype(np.uint8)
    small=cv2.resize(a,(a.shape[1]//4,a.shape[0]//4),interpolation=cv2.INTER_AREA)
    angs=np.arange(-1.5,1.51,0.05)
    sc=[score(small,t) for t in angs]; b=angs[int(np.argmax(sc))]
    angs2=np.arange(b-0.06,b+0.061,0.01); sc2=[score(small,t) for t in angs2]; b=angs2[int(np.argmax(sc2))]
    h,w=a.shape; M=cv2.getRotationMatrix2D((w/2,h/2),b,1)
    r=cv2.warpAffine(a*255,M,(w,h),flags=cv2.INTER_LINEAR)
    cv2.imwrite(f'{S}/desk/p{pg+19:03d}.png',255-((r>127)*255).astype(np.uint8))
    print(pg+19,round(b,2),flush=True)
