import sys; sys.path.insert(0,'/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad/work')
from common import *
import pickle,csv,os
OUT=sys.argv[1]
T=pickle.load(open(S+'/work/templates.pkl','rb'))
F=pickle.load(open(S+'/work/g_results.pkl','rb'))
R=pickle.load(open(S+'/work/c_rows4.pkl','rb'))
TV=np.array([t['vec'].ravel() for t in T])
twin={}
for i,t in enumerate(T):
    for flag in (False,True):
        c=[j for j,u in enumerate(T) if u['rank']==t['rank'] and u['ul']==flag]
        twin[(i,flag)]=min(c,key=lambda j:np.linalg.norm(TV[j]-TV[i])) if c else None
BOUND=115; LOWC=0.3
rows=sorted(R,key=lambda r:(r['page'],r['col'],r['ytop']))
insc=[]
for r in rows:
    if r['hascode']: insc.append(dict(head=r,rows=[r]))
    elif insc and insc[-1]['head']['page']==r['page'] and insc[-1]['head']['col']==r['col']:
        insc[-1]['rows'].append(r)
out=[];longrows=[]
for I in insc:
    h=I['head']; code=h['code_fixed']
    tokens=[]  # reading order
    for li,r in enumerate(I['rows']):
        segs,ul,left=F[(r['page'],r['col'],r['ytop'])]
        segs=[s for s in segs if s['d']<5 and s['x1']>=160]
        segs=sorted(segs,key=lambda s:s['x0'])
        while len(segs)>1 and segs[1]['x0']-segs[0]['x1']>300: segs=segs[1:]
        if not segs: continue
        if tokens: tokens.append('/')
        segs=sorted(segs,key=lambda s:-s['x1'])
        prev=None
        for s in segs:
            if prev is not None and prev['x0']-s['x1']>BOUND: tokens.append('/')
            w=s['x1']-s['x0']
            cov=np.zeros(w,bool)
            for u0,u1 in ul:
                a0=max(u0,s['x0'])-s['x0']; a1=min(u1,s['x1'])-s['x0']
                if a1>a0: cov[a0:a1]=True
            isul=cov.mean()>=0.3 if w>0 else False
            j=twin[(s['t'],isul)]
            tt=T[j] if j is not None else T[s['t']]
            tokens.append(dict(rank=tt['rank'],code=tt['code'],ul=isul,d=s['d'],x0=s['x0'],x1=s['x1'],ytop=r['ytop'],page=r['page'],col=r['col']))
            prev=s
    # strip leading/trailing boundaries
    while tokens and tokens[0]=='/': tokens.pop(0)
    while tokens and tokens[-1]=='/': tokens.pop()
    signs=[t for t in tokens if t!='/']
    text=' '.join('/' if t=='/' else f"{t['rank']}{'*' if t['ul'] else ''}" for t in tokens)
    var=' '.join('/' if t=='/' else f"{t['rank']}.{t['code']}" for t in tokens)
    low=[str(k+1) for k,t in enumerate(signs) if t['d']>LOWC]
    m=__import__('re').fullmatch(r'(\d+)([A-F]?)',h['num_fixed'])
    rec=dict(inscription=h['num_fixed'],number=int(m.group(1)),suffix=m.group(2),
             type_code=code[0:2],lines_code=code[2].strip(),icon_code=code[3:5].strip(),
             n_signs=len(signs),text=text,text_variants=var,low_confidence_positions=','.join(low),
             max_match_distance=round(max([t['d'] for t in signs]),3) if signs else '',
             printed_page=h['page']-1,pdf_page=h['page'],column=h['col']+1,list_lines=len(I['rows']),
             number_corrected=int(h['num_changed']))
    out.append(rec)
    pos=0; seg_no=1
    for t in tokens:
        if t=='/': seg_no+=1; continue
        pos+=1
        longrows.append(dict(inscription=h['num_fixed'],position=pos,segment=seg_no,sign=t['rank'],variant_code=t['code'],
            underlined=int(t['ul']),match_distance=round(t['d'],3),low_confidence=int(t['d']>LOWC),
            pdf_page=t['page'],column=t['col']+1,y=t['ytop'],x_left=t['x0'],x_right=t['x1']))
os.makedirs(OUT,exist_ok=True)
def wr(name,L):
    with open(os.path.join(OUT,name),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(L[0].keys()),delimiter='\t'); w.writeheader(); w.writerows(L)
wr('corpus_inscriptions.tsv',out); wr('corpus_signs_long.tsv',longrows)
G=pickle.load(open(S+'/work/sl_final.pkl','rb'))
wr('sign_list.tsv',[dict(sign=e['rank'],variant_code=e['code'],underlined=int(e['ul']),pdf_page=e['page'],column=e['col']+1,row=e['row']+1) for e in sorted(G,key=lambda e:(e['rank'],e['page'],e['col'],e['row']))])
pickle.dump((out,longrows,insc),open(S+'/work/assembled.pkl','wb'))
import collections
print('inscriptions',len(out),'sign tokens',len(longrows),'empty',sum(1 for o in out if o['n_signs']==0))
print('low-conf tokens',sum(l['low_confidence'] for l in longrows),'inscriptions with any',sum(1 for o in out if o['low_confidence_positions']))
print('underlined',sum(l['underlined'] for l in longrows))
print('distinct signs used',len(set(l['sign'] for l in longrows)))
print(collections.Counter(l['sign'] for l in longrows).most_common(12))
