import numpy as np, cv2
DS=4; TOP=-56; H=168  # canvas rows relative to ytop: [-56,112)
CW=160
def clean(img):
    n,lab,st,_=cv2.connectedComponentsWithStats(img,connectivity=8)
    if n<=2: return img,(0,0)
    big=np.argmax(st[1:,4])+1
    keep=np.zeros(n,bool); keep[0]=False
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a>=60: keep[i]=True; continue
        # small: keep if near other ink
        others=(lab>0)&(lab!=i)
        y0,y1,x0,x1=max(0,y-20),y+h+20,max(0,x-20),x+w+20
        keep[i]=others[y0:y1,x0:x1].any()
    m=keep[lab]
    ys,xs=np.nonzero(m)
    out=m[ys.min():ys.max()+1,xs.min():xs.max()+1].astype(np.uint8)
    return out,(xs.min(),ys.min())
def canvas(img,ytop_rel):
    """img binary at full res; ytop_rel = img top y minus row ytop"""
    h,w=img.shape
    C=np.zeros((H,max(w,8)),np.float32)
    y0=ytop_rel-TOP
    a0=max(0,-y0); b0=min(h,H-y0)
    if b0>a0: C[y0+a0:y0+b0,:w]=img[a0:b0]
    small=cv2.resize(C,(int(np.ceil(C.shape[1]/DS)),H//DS),interpolation=cv2.INTER_AREA)
    out=np.zeros((H//DS,CW),np.float32)
    ww=min(CW,small.shape[1]); out[:,:ww]=small[:,:ww]
    out=cv2.GaussianBlur(out,(0,0),1.0)
    return out
