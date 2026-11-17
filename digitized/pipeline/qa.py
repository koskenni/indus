import sys; sys.path.insert(0,'/tmp/claude-1000/-home-koskenni-ai-indus/9b5180f3-e622-40d5-aabe-c02d518af172/scratchpad/work')
from common import *
import pickle,os
OUT=sys.argv[1]; pages=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(22,79)
os.makedirs(OUT,exist_ok=True)
T=pickle.load(open(S+'/work/templates.pkl','rb'))
out,longrows,insc=pickle.load(open(S+'/work/assembled.pkl','rb'))
code2t={(t['rank'],t['code']):t for t in T}
byrow={}
for l in longrows: byrow.setdefault((l['pdf_page'],l['column']-1,l['y']),[]).append(l)
F=pickle.load(open(S+'/work/g_results.pkl','rb'))
SC=0.4
for p in pages:
    a=load(p)[0]
    for col in (0,1):
        keys=sorted([k for k in F if k[0]==p and k[1]==col],key=lambda k:k[2])
        if not keys: continue
        x0=0 if col==0 else a.shape[1]//2-60; x1=a.shape[1]//2+60 if col==0 else a.shape[1]
        strips=[]
        for k in keys:
            yt=k[2]
            orig=(1-a[max(0,yt-56):yt+130,x0:x1])*255
            if orig.shape[0]<186: orig=np.vstack([orig,np.full((186-orig.shape[0],orig.shape[1]),255,np.uint8)])
            rend=np.full_like(orig,255); lbl=np.full((44,orig.shape[1]),255,np.uint8)
            for l in byrow.get(k,[]):
                t=code2t[(l['sign'],l['variant_code'])]; im=t['img']; ty=t['top']+56; xx=l['x_left']-x0
                h,w=im.shape; h=min(h,186-ty); w=min(w,rend.shape[1]-xx)
                if h>0 and w>0 and xx>=0: rend[ty:ty+h,xx:xx+w]=np.minimum(rend[ty:ty+h,xx:xx+w],255-im[:h,:w]*255)
                if l['underlined']: rend[176:180,max(0,xx):max(0,xx)+t['w']:12]=0
                txt=f"{l['sign']}{'*' if l['underlined'] else ''}"
                cv2.putText(lbl,txt,(max(0,xx),30),cv2.FONT_HERSHEY_SIMPLEX,1.0,0,2)
                if l['low_confidence']: cv2.rectangle(rend,(max(0,xx-4),2),(xx+t['w']+4,184),0,4)
            strips.append(np.vstack([orig,rend,lbl,np.full((6,orig.shape[1]),0,np.uint8)]))
        M=np.vstack(strips); M=cv2.resize(M,None,fx=SC,fy=SC,interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(OUT,f'p{p:03d}_col{col+1}.png'),M)
