import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle,re
R=pickle.load(open(S+'/work/c_rows3.pkl','rb'))
C=[r for r in R if r['hascode']]
C.sort(key=lambda r:(r['page'],r['col'],r['ytop']))
def parse(s):
    m=re.fullmatch(r'([1-9]\d{0,3})([A-F]?)',s)
    return (int(m.group(1)),m.group(2)) if m else None
nums=[r['num_s'].replace(' ','') for r in C]
P=[parse(s) for s in nums]
alph='0123456789ABCDEF'
def edits(s):
    c=set()
    for k in range(len(s)+1):
        for ch in alph: c.add(s[:k]+ch+s[k:])
    for k in range(len(s)):
        c.add(s[:k]+s[k+1:])
        for ch in alph: c.add(s[:k]+ch+s[k+1:])
    return [(parse(x),x) for x in c if parse(x)]
def nxt_ok(i,last):
    # smallest later parsed value > last, looking ahead up to 3 entries
    for j in range(i+1,min(i+4,len(P))):
        if P[j] and P[j]>last: return P[j]
    return None
changes=[];last=(0,'')
for i in range(len(P)):
    hi=nxt_ok(i,last)
    v=P[i]
    if v and v>last and (hi is None or v<hi):
        last=v; continue
    cands=[c for c in edits(nums[i]) if c[0]>last and (hi is None or c[0]<hi)]
    if not cands:
        changes.append((i,C[i]['page'],nums[i],None,0)); 
        if v and v>last: last=v
        continue
    # prefer substitution (same length), then closeness to last+1
    cands.sort(key=lambda c:(len(c[1])!=len(nums[i]), c[0][0]-last[0], c[0][1]))
    changes.append((i,C[i]['page'],nums[i],cands[0][1],len(cands)))
    nums[i]=cands[0][1]; P[i]=cands[0][0]; last=P[i]
OVR=[(33,'1264',5433,'1261'),(64,'39C',None,'3978')]
for i,r in enumerate(C):
    for p_,raw,y_,val in OVR:
        if r['page']==p_ and r['num_s'].replace(' ','')==raw and (y_ is None or abs(r['ytop']-y_)<15):
            nums[i]=val; P[i]=parse(val)
for c in changes: print(c)
cmap={'C':'0','D':'0','B':'8','A':'4','E':'6','F':'6'}
for r,s in zip(C,nums):
    r['num_fixed']=s; r['num_changed']=(s!=r['num_s'].replace(' ',''))
    r['code_fixed']=''.join(cmap.get(ch,ch) for ch in r['code_s'])
    r['code_ok']=bool(re.fullmatch(r'\d\d[ 0-9][ \d]\d',r['code_fixed']))
from collections import Counter
cc=Counter(nums); print('dups',[k for k,v in cc.items() if v>1])
print('bad codes',[(r['page'],r['num_fixed'],r['code_s']) for r in C if not r['code_ok']])
pickle.dump(R,open(S+'/work/c_rows4.pkl','wb'))
