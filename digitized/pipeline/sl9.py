import sys; sys.path.insert(0,sys.argv[1]+'/work')
from common import *
import pickle
G=pickle.load(open(S+'/work/sl_grid.pkl','rb'))
fix={(21,1,2):(223,None),(21,4,21):(300,None),(21,4,22):(None,333),(21,5,22):(319,None),(20,2,22):(55,None)}
for e in G:
    k=(e['page'],e['col'],e['row'])
    if k in fix:
        r,c=fix[k]
        if r: e['rank']=r
        if c: e['code']=c
cache={}
Rs={20:[596,1012,1426,1842,2257,2673,3088,3502,3918,4331],21:[508,923,1338,1755,2171,2588,3003,3420,3835,4251]}
for e in G:
    p=e['page']
    if p not in cache: cache[p]=load(p)
    a,lab,st=cache[p]
    R=e['R']; xr=Rs[p][e['col']+1]-125 if e['col']<9 else 4880
    yc=e['ytop']+24
    cx=st[:,0]+st[:,2]/2; cy=st[:,1]+st[:,3]/2
    idx=list(np.where((st[:,0]>R+12)&(cx<xr)&(cy>yc-84)&(cy<yc+84)&(st[:,4]>=10))[0])
    g,u=split_underline(st,idx)
    e['ul']=len(u)>0
    if g:
        img,bb=render(lab,st,g); e['img']=img; e['bb']=bb
    else: e['img']=None
    e['ulw']=(min(st[i,0] for i in u),max(st[i,0]+st[i,2] for i in u)) if u else None
print(len(G),'noimg',[ (e['rank'],e['code']) for e in G if e['img'] is None])
print('ranks',sorted(set(range(1,402))-set(e['rank'] for e in G)))
print('ul',sum(e['ul'] for e in G))
hs=[e['img'].shape for e in G if e['img'] is not None]; print('max h,w',max(h for h,w in hs),max(w for h,w in hs))
pickle.dump(G,open(S+'/work/sl_final.pkl','wb'))
# montage
cell=230
cols=20; rows=(len(G)+cols-1)//cols
M=np.ones((rows*cell,cols*cell),np.uint8)*255
for i,e in enumerate(G):
    y,x=(i//cols)*cell,(i%cols)*cell
    if e['img'] is not None:
        im=e['img'][:190,:220]; h,w=im.shape
        M[y+30:y+30+h,x+5:x+5+w]=255-im*255
    cv2.putText(M,f"{e['rank']}/{e['code']}{'_' if e['ul'] else ''}",(x+5,y+22),cv2.FONT_HERSHEY_SIMPLEX,0.7,0,2)
cv2.imwrite(S+'/work/slmont.png',M)
for k in range(0,rows,12): cv2.imwrite(S+f'/work/slmont{k//12}.png',cv2.resize(M[k*cell:(k+12)*cell],None,fx=0.5,fy=0.5,interpolation=cv2.INTER_AREA))
