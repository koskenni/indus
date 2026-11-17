import sys; sys.path.insert(0,'/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad/work')
from g2 import *
from multiprocessing import Pool
R=pickle.load(open(S+'/work/c_rows4.pkl','rb'))
xl0={}
for r in R:
    if r['col']==0: xl0[r['page']]=r['R']
for r in R:
    if r['col']==1: r['xl']=xl0[r['page']]+PITCH+25
def rows_for(p):
    return sorted([r for r in R if r['page']==p],key=lambda r:(r['col'],r['ytop']))
def job(p):
    a,lab,st=load(p)
    cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
    out=[]; lastleft=None
    for rec in rows_for(p):
        yt=rec['ytop']
        if rec['hascode']:
            num,_=read_cells(a,lab,st,rec['R'],yt,extra=PITCH)
            code,_=read_cells(a,lab,st,rec['R']+PITCH,yt+48)
            xs=[v[3][0] for v in list(num.values())+list(code.values())]
            left=min(xs) if xs else rec['R']-5*PITCH
            lastleft=left
        else:
            left=lastleft if lastleft is not None else rec['R']-5*PITCH
        rec['codeleft']=left
        idx=np.where((cx>rec['xl'])&(st[:,0]+st[:,2]<left-6)&(cy>yt-60)&(cy<yt+128)&(st[:,4]>=12))[0]
        rec['idx']=idx
        segs,ul=process_row(a,lab,st,rec)
        out.append(((p,rec['col'],yt),segs,ul,left))
    return out
if __name__=='__main__':
    with Pool(8) as pool:
        res=pool.map(job,range(22,79))
    flat={k:(s,u,l) for page in res for k,s,u,l in page}
    pickle.dump(flat,open(S+'/work/g_results.pkl','wb'))
    ds=[s['d'] for v in flat.values() for s in v[0]]
    print(len(flat),'segments',len(ds),'d pct',np.percentile(ds,[50,90,95,98,99]).round(3),'>0.2:',sum(d>0.2 for d in ds))
