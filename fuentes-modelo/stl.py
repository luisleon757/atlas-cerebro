import numpy as np, nibabel as nib, trimesh, os
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage import measure
D='dl/fs/'; OUT='stl/'; os.makedirs(OUT,exist_ok=True)
SCALE=0.5
DK={}
for k in [3,12,14,17,18,19,20,24,27,28,32]: DK[k]=0
for k in [8,22,25,29,31]: DK[k]=1
for k in [1,6,7,9,15,16,30,33,34]: DK[k]=2
for k in [5,11,13,21]: DK[k]=3
LOB=['frontal','parietal','temporal','occipital']
labels=np.loadtxt('dl/aparc_fsa5.csv',dtype=int)
gm=nib.load(D+'mni_icbm152_gm_tal_nlin_sym_09a_converted.nii.gz'); wm=nib.load(D+'mni_icbm152_wm_tal_nlin_sym_09a_converted.nii.gz')
A=gm.affine; vol=ndimage.gaussian_filter((gm.get_fdata()+wm.get_fdata())/255.0,0.8); mask=vol>0.45
x,y,z=[np.arange(n)+A[i,3] for i,n in enumerate(mask.shape)]
X,Y,Z=np.meshgrid(x,y,z,indexing='ij')
def largest(m,k=1):
    lab,n=ndimage.label(m)
    if n==0: return m
    sz=ndimage.sum(m,lab,range(1,n+1)); return np.isin(lab,np.argsort(sz)[::-1][:k]+1)
pieces={}
cortex=np.zeros(mask.shape,bool)
for hi,h in enumerate(['left','right']):
    g=nib.load(D+f'pial_{h}.gii.gz'); v=g.darrays[0].data.astype(float); f=g.darrays[1].data.astype(np.int64)
    lab=labels[hi*10242:(hi+1)*10242]; lab=np.where(lab>35,lab-35,lab)
    vr=np.array([DK.get(int(l),-1) for l in lab])
    pm=trimesh.Trimesh(v,f,process=False)
    shell=np.zeros(mask.shape,bool)
    pts,_=trimesh.sample.sample_surface(pm,1500000,seed=1)
    ii=np.round(pts-A[:3,3]).astype(int); ok=np.all((ii>=0)&(ii<np.array(mask.shape)),1); ii=ii[ok]
    shell[ii[:,0],ii[:,1],ii[:,2]]=True
    hemi=ndimage.binary_fill_holes(ndimage.binary_closing(shell,iterations=1))
    hemi=largest(hemi,1); cortex|=hemi
    tree=cKDTree(v[vr>=0]); vl=vr[vr>=0]
    idx=np.argwhere(hemi); P=idx+A[:3,3]
    _,nn=tree.query(P); L=vl[nn]
    side='izq' if h=='left' else 'der'
    for li,ln in enumerate(LOB):
        m=np.zeros(mask.shape,bool); s=idx[L==li]; m[s[:,0],s[:,1],s[:,2]]=True
        pieces[f'{ln}_{side}']=largest(m,1)
cdil=ndimage.binary_dilation(cortex,iterations=3)
rest=mask&~cdil&(Z<2)
stem_box=(np.abs(X)<=14)&(Y>=-44)&(Y<=-8)&(Z<=-2); stem_box&=~((Y<-32)&(np.abs(X)>10))
cereb=rest&~stem_box&(Y<-30); stem=rest&stem_box
core=largest(ndimage.binary_opening(cereb,iterations=4),1)
cereb=largest(ndimage.binary_closing(cereb&ndimage.binary_dilation(core,iterations=4),iterations=1),1)
stem=largest(ndimage.binary_opening(stem,iterations=2),1)
pieces['cerebelo']=cereb; pieces['tronco']=stem
allm=[]
for name,m in pieces.items():
    m=largest(ndimage.binary_fill_holes(m),1)
    field=ndimage.gaussian_filter(np.pad(m,3).astype(float),1.0)
    vv,ff,_,_=measure.marching_cubes(field,0.55)
    vv=vv-3+A[:3,3]
    tm=trimesh.Trimesh(vv,ff,process=True)
    if len(tm.split(only_watertight=False))>1: tm=max(tm.split(only_watertight=False),key=lambda t:len(t.faces))
    trimesh.smoothing.filter_taubin(tm,iterations=10)
    if len(tm.faces)>60000:
        t2=tm.simplify_quadric_decimation(face_count=60000)
        if t2.is_watertight: tm=t2
        else: print(name,'decimado no estanco, sin decimar',len(tm.faces))
    trimesh.repair.fix_normals(tm); trimesh.repair.fill_holes(tm)
    if tm.volume<0: tm.invert()
    tm.apply_scale(SCALE)
    asm=tm.copy(); allm.append((name,asm))
    print(name,'watertight',tm.is_watertight,'vol cm3',round(tm.volume/1000,1),'bbox mm',(tm.extents).round(1),'faces',len(tm.faces))
    pieces[name]=tm
np.save('stl/_names.npy',np.array(list(pieces)))
import pickle; pickle.dump({n:(t.vertices,t.faces) for n,t in pieces.items()},open('stl/_raw.pkl','wb'))
