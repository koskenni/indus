import sys; sys.path.insert(0,'/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad/work')
from common import *
import pickle
from g1lib import canvas, TOP, H, DS, CW
T=pickle.load(open(S+'/work/templates.pkl','rb'))
TV=np.array([t['vec'].ravel() for t in T]); TN=(TV**2).sum(1)
TW=np.array([t['w'] for t in T]); TT=np.array([t['top'] for t in T]); TH=np.array([t['h'] for t in T])
# shifted template versions (by -1,+1 canvas columns)
def shift(v,s):
    v=v.reshape(H//DS,CW); o=np.zeros_like(v)
    if s>0: o[:,s:]=v[:,:-s]
    elif s<0: o[:,:s]=v[:,-s:]
    else: o=v
    return o.ravel()
TVs=[np.array([shift(v,s) for v in TV]) for s in (-1,0,1)]
GAP0=20
HATCH=[i for i,t in enumerate(T) if 395<=t['rank']<=399]
def heavy(v):
    return cv2.GaussianBlur(v.reshape(H//DS,CW),(0,0),2.5).ravel()
HV=np.array([heavy(TV[i]) for i in HATCH]); HN=(HV**2).sum(1)
def hatchlike(st,ids):
    n=0
    for i in ids:
        x,y,w,h,a=st[i]
        if w>12 and h>12 and abs(w-h)/max(w,h)<0.45 and a/(w*h)<0.2: n+=1
    return n>=4
def match_hatch(vec,w):
    v=heavy(vec.ravel()); vn=(v**2).sum()
    d=(HN+vn-2*HV@v)/(HN+vn+1e-6)
    d=d+0.3*np.abs(TW[HATCH]-w)/np.maximum(TW[HATCH],w)
    k=int(np.argmin(d)); return float(d[k]),HATCH[k]
def match(vec,w,top,h):
    v=vec.ravel(); vn=(v**2).sum()
    best=None
    ok=np.where((np.abs(TW-w)<=np.maximum(14,0.2*np.maximum(TW,w)))&(np.abs(TT-top)<=22)&(np.abs(TH-h)<=24))[0]
    if len(ok)==0: return 9.0,-1
    ds=[]
    for M in TVs:
        d=(TN[ok]+vn-2*M[ok]@v)/(TN[ok]+vn+1e-6)
        ds.append(d)
    d=np.min(ds,0)
    d=d+0.3*np.abs(TW[ok]-w)/np.maximum(TW[ok],w)
    k=int(np.argmin(d))
    return float(d[k]),int(ok[k])
def process_row(a,lab,st,rec):
    yt=rec['ytop']; idx=[i for i in rec['idx'] if st[i,4]>=25 or st[i,3]>=12]
    def blob(i):
        x,y,w,h,a=st[i]
        return a>=140 and a/(w*h)>0.5 and 0.4<=w/h<=2.5 and min(w,h)>=12
    def edge(i):
        x,y,w,h,a=st[i]
        return h>170 or (w<=8 and h>140)
    idx=[i for i in idx if not blob(i) and not edge(i)]
    ul=[i for i in idx if st[i,3]<=12 and st[i,2]>=6 and st[i,1]>=yt+86]
    rest=[i for i in idx if i not in ul and st[i,1]+st[i,3]>yt-45 and st[i,1]<yt+100]
    rest.sort(key=lambda i:st[i,0])
    cl=[]
    for i in rest:
        x,y,w,h,_=st[i]
        if cl and x<=cl[-1]['x1']+4: cl[-1]['ids'].append(i); cl[-1]['x1']=max(cl[-1]['x1'],x+w)
        else: cl.append(dict(x0=x,x1=x+w,ids=[i]))
    n=len(cl)
    if n==0: return [],ul
    gaps=[cl[k+1]['x0']-cl[k]['x1'] for k in range(n-1)]
    INF=1e9; best=[INF]*(n+1); back=[None]*(n+1); best[0]=0
    cache={}
    for j in range(1,n+1):
        for i in range(j-1,max(-1,j-9),-1):
            if i<j-1 and gaps[i]>42: break  # internal gap
            if cl[j-1]['x1']-cl[i]['x0']>590: break
            ids=sum((c['ids'] for c in cl[i:j]),[])
            img,bb=render(lab,st,ids)
            top=bb[1]-yt; w=bb[2]-bb[0]; h=bb[3]-bb[1]
            cv_=canvas(img,top)
            d,k=match(cv_,w,top,h)
            if hatchlike(st,ids):
                d2,k2=match_hatch(cv_,w)
                if d2<d: d,k=d2,k2
            pen=0
            for g in gaps[i:j-1]: pen+=0.012*max(0,g-GAP0)
            if i>0: pen+=0.012*max(0,GAP0-gaps[i-1])
            c=best[i]+d+pen+0.05
            if c<best[j]: best[j]=c; back[j]=(i,d,k,bb)
    segs=[];j=n
    while j>0:
        i,d,k,bb=back[j]; segs.append(dict(x0=bb[0],x1=bb[2],y0=bb[1],y1=bb[3],d=d,t=k)); j=i
    segs.reverse()
    return segs,[(st[i,0],st[i,0]+st[i,2]) for i in ul]
def process_page(p,rows):
    a,lab,st=load(p)
    out=[]
    for rec in rows:
        segs,ul=process_row(a,lab,st,rec)
        out.append((segs,ul))
    return out
