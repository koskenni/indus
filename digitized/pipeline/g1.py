import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
G=pickle.load(open(S+'/work/sl_final.pkl','rb'))
DS=4; TOP=-56; H=168  # canvas rows relative to ytop: [-56,112)
CW=160
def clean(img):
    n,lab,st,_=cv2.connectedComponentsWithStats(img,connectivity=8)
    if n<=2: return img,(0,0)
    comps=list(range(1,n))
    # cluster by horizontal gap <= 45
    comps.sort(key=lambda i:st[i,0])
    groups=[]
    for i in comps:
        x,w=st[i,0],st[i,2]
        if groups and x<=groups[-1][1]+45: groups[-1][2].append(i); groups[-1][1]=max(groups[-1][1],x+w)
        else: groups.append([x,x+w,[i]])
    best=max(groups,key=lambda g:sum(st[i,4] for i in g[2]))
    keep=np.zeros(n,bool)
    for i in best[2]:
        keep[i]= st[i,4]>=40 or True
    # drop tiny isolated specks inside the group
    m=keep[lab]
    for i in best[2]:
        if st[i,4]<40:
            x,y,w,h,a=st[i]
            others=m.copy(); others[lab==i]=False
            if not others[max(0,y-20):y+h+20,max(0,x-20):x+w+20].any(): m[lab==i]=False
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
T=[]
for e in G:
    img,(dx,dy)=clean(e['img'])
    bb=e['bb']; top=bb[1]+dy-e['ytop']
    T.append(dict(rank=e['rank'],code=e['code'],ul=e['ul'],img=img,w=img.shape[1],h=img.shape[0],top=top,vec=canvas(img,top)))
pickle.dump(T,open(S+'/work/templates.pkl','wb'))
print(len(T), 'w range',min(t['w'] for t in T),max(t['w'] for t in T))
