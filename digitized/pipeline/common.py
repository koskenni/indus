import numpy as np, cv2
from PIL import Image
S='/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad'
PITCH=35.5
def load(p):
    a=(np.array(Image.open(f'{S}/desk/p{p:03d}.png').convert('L'))<128).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(a,connectivity=8)
    return a,lab,st[1:]
def digitlike(st):
    return (st[:,3]>=26)&(st[:,3]<=44)&(st[:,2]<=34)&(st[:,2]>=3)
def lines_from(comps,tol=12):
    comps=sorted(comps,key=lambda c:c[1]); L=[]
    for c in comps:
        if L and abs(c[1]-np.median([d[1] for d in L[-1]]))<tol: L[-1].append(c)
        else: L.append([c])
    return L
def cell_crop(a,R,ytop,k):
    x1=int(round(R-k*PITCH)); x0=int(round(R-(k+1)*PITCH))
    c=a[ytop-4:ytop+42, x0:x1+2]
    return c
def center_norm(c,W=40,H=48):
    out=np.zeros((H,W),np.uint8)
    ys,xs=np.nonzero(c)
    if len(ys)==0: return out
    c=c[ys.min():ys.max()+1, xs.min():xs.max()+1]
    h,w=c.shape; h=min(h,H); w=min(w,W)
    oy=(H-h)//2; ox=(W-w)//2
    out[oy:oy+h,ox:ox+w]=c[:h,:w]; return out

def line_glyphs(a,lab,st,x0,x1,y0,y1,minarea=8,gap=3):
    """components whose bbox center is inside the box; merged by x-overlap. returns list of (x0,x1,y0,y1,img)"""
    cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
    idx=np.where((cx>=x0)&(cx<x1)&(cy>=y0)&(cy<y1)&(st[:,4]>=minarea))[0]
    idx=sorted(idx,key=lambda i:st[i,0])
    groups=[]
    for i in idx:
        x,y,w,h,_=st[i]
        if groups and x<=groups[-1][1]+gap:
            g=groups[-1]; g[1]=max(g[1],x+w); g[2]=min(g[2],y); g[3]=max(g[3],y+h); g[4].append(i)
        else: groups.append([x,x+w,y,y+h,[i]])
    out=[]
    for gx0,gx1,gy0,gy1,ids in groups:
        sub=np.isin(lab[gy0:gy1,gx0:gx1],np.array(ids)+1).astype(np.uint8)
        out.append((gx0,gx1,gy0,gy1,sub))
    return out

DT=None
def read_number(a,lab,st,R,ytop,ncell=3,x0=None):
    global DT
    if DT is None: DT=np.load(S+'/work/digit_templates.npy')
    if x0 is None: x0=R-ncell*PITCH-6
    G=line_glyphs(a,lab,st,x0,R+10,ytop-6,ytop+46)
    s='';worst=0
    for g in G:
        if g[4].sum()<40: continue
        b=cv2.GaussianBlur(center_norm(g[4]).astype(np.float32),(0,0),2).ravel()
        d=np.linalg.norm(DT-b,axis=1); k=int(np.argmin(d))
        s+=str(k); worst=max(worst,d[k])
    return s,worst

def split_underline(st,idx):
    """idx: component indices. returns (glyph_idx, underline_idx)"""
    small=[i for i in idx if st[i,3]<=10 and 6<=st[i,2]<=45]
    ul=set()
    for i in small:
        same=[j for j in small if abs(st[j,1]-st[i,1])<=5]
        if len(same)>=3: ul|=set(same)
    if ul:
        yul=np.median([st[i,1] for i in ul])
        others=[i for i in idx if i not in ul]
        # underline must be below the glyph bulk
        if others and yul < np.median([st[i,1]+st[i,3] for i in others])-10: ul=set()
    return [i for i in idx if i not in ul],sorted(ul)
def render(lab,st,ids):
    x0=min(st[i,0] for i in ids); y0=min(st[i,1] for i in ids)
    x1=max(st[i,0]+st[i,2] for i in ids); y1=max(st[i,1]+st[i,3] for i in ids)
    sub=np.isin(lab[y0:y1,x0:x1],np.array(ids)+1).astype(np.uint8)
    return sub,(x0,y0,x1,y1)

CT=None
def classify_char(img):
    global CT
    import pickle
    if CT is None: CT=pickle.load(open(S+'/work/char_templates.pkl','rb'))
    b=cv2.GaussianBlur(center_norm(img).astype(np.float32),(0,0),2).ravel()
    best=min(CT.items(),key=lambda kv:np.linalg.norm(kv[1]-b))
    return best[0],float(np.linalg.norm(best[1]-b))
def read_cells(a,lab,st,R,y,ncell=5):
    """assign components in a code line to grid cells right-aligned at R. returns {cell:(char,dist,img,(x0,x1))}, refined R"""
    cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
    sel=np.where((cx>R-ncell*PITCH-20)&(cx<R+15)&(cy>y-4)&(cy<y+44)&(st[:,4]>=6)&(st[:,3]<=50))[0]
    if len(sel)==0: return {},R
    # refine R using big pieces
    big=[i for i in sel if st[i,3]>=25]
    if big:
        offs=[]
        for i in big:
            c=cx[i]; k=np.floor((R-c)/PITCH); offs.append(c+(k+0.5)*PITCH)
        Rr=float(np.median(offs))
        if abs(Rr-R)<15: R=Rr
    cells={}
    for i in sel:
        k=int(np.floor((R-cx[i])/PITCH))
        if 0<=k<ncell: cells.setdefault(k,[]).append(i)
    out={}
    for k,ids in cells.items():
        if sum(st[i,4] for i in ids)<35: continue
        img,bb=render(lab,st,ids)
        ch,d=classify_char(img)
        out[k]=(ch,d,img,(bb[0],bb[2]))
    return out,R

def read_cells(a,lab,st,R,y,ncell=5,extra=0):
    cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
    sel=np.where((cx>R-ncell*PITCH-25)&(cx<R+15+extra)&(cy>y-4)&(cy<y+44)&(st[:,4]>=6)&(st[:,3]<=50))[0]
    sel=sorted(sel,key=lambda i:st[i,0])
    groups=[]
    for i in sel:
        x,yy,w,h,_=st[i]
        if groups and x<=groups[-1]['x1']+2:
            g=groups[-1]; g['x1']=max(g['x1'],x+w); g['ids'].append(i)
        else: groups.append(dict(x0=x,x1=x+w,ids=[i]))
    for g in groups:
        g['area']=sum(st[i,4] for i in g['ids'])
        g['h']=max(st[i,1]+st[i,3] for i in g['ids'])-min(st[i,1] for i in g['ids'])
    # merge fragments
    changed=True
    while changed and len(groups)>1:
        changed=False
        for j,g in enumerate(groups):
            if g['h']<27 or g['x1']-g['x0']<8 and g['h']<34:
                cands=[(max(0,g['x0']-o['x1'],o['x0']-g['x1']),k) for k,o in enumerate(groups) if k!=j]
                dist,k=min(cands)
                o=groups[k]
                if dist<=12 and (max(o['x1'],g['x1'])-min(o['x0'],g['x0']))<=34:
                    o['ids']+=g['ids']; o['x0']=min(o['x0'],g['x0']); o['x1']=max(o['x1'],g['x1']); o['area']+=g['area']
                    o['h']=max(st[i,1]+st[i,3] for i in o['ids'])-min(st[i,1] for i in o['ids'])
                    groups.pop(j); changed=True; break
    out={}
    groups=[g for g in groups if g['area']>=35 and g['h']>=20]
    if not groups: return {},R
    # refine R from right edge of rightmost wide group centers
    centers=np.array([(g['x0']+g['x1'])/2 for g in groups])
    tall=[c for g,c in zip(groups,centers) if g['h']>=25]
    if tall: R=max(tall)+PITCH/2
    for g,c in zip(groups,centers):
        k=int(np.floor((R-c)/PITCH))
        if not 0<=k<ncell: continue
        img,bb=render(lab,st,g['ids'])
        ch,d=classify_char(img)
        if k in out:  # collision
            out[k]=(out[k][0]+ch,max(d,out[k][1]),img,(bb[0],bb[2]))
        else: out[k]=(ch,d,img,(bb[0],bb[2]))
    return out,R
