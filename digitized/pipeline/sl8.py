import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
D=pickle.load(open(S+'/work/sl_entries2.pkl','rb'))
out=[]
for p,Rs in [(20,[596,1012,1426,1842,2257,2673,3088,3502,3918,4331]),(21,[508,923,1338,1755,2171,2588,3003,3420,3835,4251])]:
    a,lab,st=load(p)
    for ci,R in enumerate(Rs):
        det=[e for e in D if e['page']==p and e['col']==ci]
        # fit grid
        ys=np.array([e['ytop'] for e in det]); i=np.round((ys-ys[0])/167.3)
        A=np.vstack([i,np.ones_like(i)]).T; k,b=np.linalg.lstsq(A,ys,rcond=None)[0]
        b=b-round((b-603)/k)*k
        for r in range(35):
            yt=int(round(b+r*k)); yb=yt+48
            # refine: actual top of digits near yt
            box=a[yt-15:yt+30,R-110:R+8]
            if box.sum()<50: continue
            t,wt=read_number(a,lab,st,R,yt); c,wb=read_number(a,lab,st,R,yb)
            out.append(dict(page=p,col=ci,row=r,R=R,ytop=yt,ybot=yb,rank=int(t) if t else -1,code=int(c) if c else -1,w=max(wt,wb)))
prev=0
for e in out:
    if e['rank']<prev or e['rank']>prev+3 or e['w']>8: print(e['page'],e['col'],e['row'],e['rank'],e['code'],round(e['w'],1))
    prev=e['rank']
print(len(out))
pickle.dump(out,open(S+'/work/sl_grid.pkl','wb'))
