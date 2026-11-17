import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
entries=[]
for p,Rs in [(20,[596,1012,1426,1842,2257,2673,3088,3502,3918,4331]),(21,[508,923,1338,1755,2171,2588,3003,3420,3835,4251])]:
    a,lab,st=load(p)
    dl=digitlike(st)
    for ci,R in enumerate(Rs):
        sel=[tuple(s) for s,d in zip(st,dl) if d and R-160<s[0]+s[2]<=R+8]
        L=lines_from(sel)
        L=[l for l in L if len(l)>=1]
        tops=[int(np.median([c[1] for c in l])) for l in L]
        used=set()
        for i,t in enumerate(tops):
            if i in used: continue
            j=[k for k,t2 in enumerate(tops) if 40<t2-t<58]
            if not j: continue
            j=j[0]; used|={i,j}
            entries.append(dict(page=p,col=ci,R=R,ytop=t,ybot=tops[j]))
print(len(entries))
pickle.dump(entries,open(sys.argv[1]+'/work/sl_entries.pkl','wb'))
