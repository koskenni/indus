import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
R=pickle.load(open(S+'/work/c_rows.pkl','rb'))
bad=[]
cur=None
for ri,r in enumerate(R):
    if not r['hascode']: continue
    if r['page']!=cur: a,lab,st=load(r['page']); cur=r['page']
    num,Rn=read_cells(a,lab,st,r['R'],r['ytop'],extra=PITCH)
    code,Rc=read_cells(a,lab,st,r["R"]+PITCH,r["ytop"]+48)
    r['numc']={k:v[:2] for k,v in num.items()}; r['codec']={k:v[:2] for k,v in code.items()}
    r['Rc']=Rc
    for line,dd in (('num',num),('code',code)):
        for k,(ch,d,img,_) in dd.items():
            if d>6.5: bad.append((d,ch,k,line,ri,img))
pickle.dump(R,open(S+'/work/c_rows2.pkl','wb'))
pickle.dump(bad,open(S+'/work/c_bad.pkl','wb'))
print(len(bad))
bad.sort(key=lambda b:-b[0])
cols=25;n=len(bad)
M=np.ones(((n//cols+1)*80,cols*50),np.uint8)*255
for i,b in enumerate(bad):
    y,x=(i//cols)*80,(i%cols)*50
    M[y+5:y+53,x:x+40]=255-center_norm(b[5])*255
    cv2.putText(M,f'{b[1]}{b[2]}{b[3][0]}',(x,y+72),cv2.FONT_HERSHEY_SIMPLEX,0.5,0,1)
cv2.imwrite(S+'/work/bad2.png',M)
