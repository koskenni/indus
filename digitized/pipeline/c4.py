import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
PR=167.3
def read_code_line(a,lab,st,R,y):
    G=line_glyphs(a,lab,st,R-5*PITCH-8,R+10,y-6,y+46)
    cells={}
    for g in G:
        if g[4].sum()<40: continue
        b=cv2.GaussianBlur(center_norm(g[4]).astype(np.float32),(0,0),2).ravel()
        d=np.linalg.norm(DTm()-b,axis=1); k=int(np.argmin(d))
        ci=int(round((R-g[1])/PITCH))
        cells[ci]=(k,d[k],g)
    return cells
def DTm():
    import common
    if common.DT is None: common.DT=np.load(S+'/work/digit_templates.npy')
    return common.DT
rows=[]; codes=[]
for p in range(22,79):
    a,lab,st=load(p)
    dl=digitlike(st)
    dig=st[dl]
    paired=[]
    for x,y,w,h,ar in dig:
        m=(np.abs(dig[:,1]-y-48)<9)&(np.abs(dig[:,0]-x)<14)
        if m.any(): paired.append((x+w,y))
    paired=np.array(paired)
    Rs=[]
    for lo,hi in [(1500,2700),(3700,4880)]:
        r=paired[(paired[:,0]>lo)&(paired[:,0]<hi),0]
        Rs.append(float(np.percentile(r,98)))
    for ci,R in enumerate(Rs):
        strip=a[:,int(R-4*PITCH-8):int(R+PITCH+12)]
        prof=strip.sum(1)>0
        bands=[];y=450
        while y<len(prof):
            if prof[y]:
                y0=y
                while y<len(prof) and (prof[y] or prof[y:y+6].any()): y+=1
                bands.append((y0,y))
            y+=1
        bands=[b for b in bands if b[1]-b[0]>=18]
        U=[]
        k=0
        while k<len(bands)-1:
            if 38<=bands[k+1][0]-bands[k][0]<=60 and bands[k][1]-bands[k][0]<=60:
                U.append(bands[k][0]); k+=2
            elif 72<=bands[k][1]-bands[k][0]<=105:
                U.append(bands[k][0]); k+=1
            else: k+=1
        if k==len(bands)-1 and 72<=bands[k][1]-bands[k][0]<=105: U.append(bands[k][0])
        U=np.array(U,float)
        xl=0 if ci==0 else Rs[0]+20
        xr=R-5*PITCH-30
        cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
        slots=[]
        for n,u in enumerate(U):
            slots.append((u,True))
            nxt=U[n+1] if n+1<len(U) else 6950
            y=u+PR
            while y<nxt-80:
                slots.append((y,False)); y+=PR
        # rows above the first code? (continuation from previous page not possible); ignore
        for yt,hascode in slots:
            yti=int(round(yt))
            idx=np.where((cx>xl)&(st[:,0]+st[:,2]<xr+20)&(cy>yt-60)&(cy<yt+128)&(st[:,4]>=12))[0]
            if len(idx)==0 and not hascode: continue
            rec=dict(page=p,col=ci,ytop=yti,R=R,xl=xl,xr=xr,comps=st[idx].copy(),idx=idx,hascode=hascode)
            if hascode:
                rec['num']=read_code_line(a,lab,st,R,yti)
                rec['code']=read_code_line(a,lab,st,R,yti+48)
            rows.append(rec)
        pitch=0;resid=np.zeros(1)
        print(p,ci,round(R),'pitch',round(pitch,2),'maxres',round(np.abs(resid).max(),1),'codes',len(U),flush=True)
pickle.dump(rows,open(S+'/work/c_rows.pkl','wb'))
