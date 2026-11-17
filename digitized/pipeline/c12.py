import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle,re
R=pickle.load(open(S+'/work/c_rows2.pkl','rb'))
def s_of(c,n=5,blank=' '):
    return ''.join(c[k][0] if k in c else blank for k in range(n-1,-1,-1))
C=[r for r in R if r['hascode']]
# reading order: page, col, y
C.sort(key=lambda r:(r['page'],r['col'],r['ytop']))
prev=None;issues=0
for r in C:
    num=s_of(r['numc']).strip(); code=s_of(r['codec'])
    r['num_s']=num; r['code_s']=code
    m=re.fullmatch(r'(\d{1,4})([A-F]?)',num)
    r['n']=(int(m.group(1)),m.group(2)) if m else None
    ok=True
    if not m: ok=False
    elif prev and prev[0] is not None:
        if r['n']<prev[0]: ok=False
    if not re.fullmatch(r'\d\d[ 0-9]\d\d',code): ok=False
    if not ok:
        issues+=1
        print(r['page'],r['col'],r['ytop'],repr(num),repr(code),'prev',prev[1] if prev else None)
    prev=(r['n'],num)
print('issues',issues,'of',len(C))
pickle.dump(R,open(S+'/work/c_rows3.pkl','wb'))
