import sys; sys.path.insert(0,'/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad/work')
from g2 import *
F=pickle.load(open(S+'/work/g_results.pkl','rb'))
pages={}
nfix=0;ndrop=0;log=[]
for key,(segs,ul,left) in F.items():
    p,col,yt=key
    for s in segs:
        if not (0.3<s['d']<5): continue
        if p not in pages: pages[p]=load(p)
        a,lab,st=pages[p]
        cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
        ids=list(np.where((st[:,0]>=s['x0'])&(st[:,0]+st[:,2]<=s['x1'])&(st[:,1]>=s['y0'])&(st[:,1]+st[:,3]<=s['y1'])&(st[:,4]>=12))[0])
        if not ids: continue
        img,bb=render(lab,st,ids)
        top=bb[1]-yt; w=bb[2]-bb[0]; h=bb[3]-bb[1]
        v=canvas(img,top).ravel(); vn=(v**2).sum()
        best=(9,-1)
        # relaxed: try vertical shifts of the canvas too
        for dy in (-3,-2,-1,0,1,2,3):
            vv=np.roll(v.reshape(H//DS,CW),dy,axis=0).ravel()
            for M in TVs:
                d=(TN+vn-2*M@vv)/(TN+vn+1e-6)+0.3*np.abs(TW-w)/np.maximum(TW,w)
                k=int(np.argmin(d))
                if d[k]<best[0]: best=(float(d[k]),k)
        old=(s['d'],T[s['t']]['rank'] if s['t']>=0 else None)
        if best[0]<s['d']-0.03:
            s['d'],s['t']=best; nfix+=1
        if s['d']>0.6 and h<30:
            s['d']=9.5; ndrop+=1   # speck: excluded later (d>=5)
        log.append((key,old,(round(s['d'],3),T[s['t']]['rank'] if s['t']>=0 else None)))
pickle.dump(F,open(S+'/work/g_results.pkl','wb'))
print('rematched',nfix,'dropped specks',ndrop)
for l in log: 
    if l[1][1]!=l[2][1]: print(l)
