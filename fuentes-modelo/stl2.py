import pickle, trimesh, numpy as np
raw=pickle.load(open('stl/_raw.pkl','rb'))
COL={'frontal':'#3d7bff','parietal':'#f2b705','temporal':'#19b37a','occipital':'#a05cf0','cerebelo':'#ff7a2f','tronco':'#e8436a'}
NUM={'frontal_izq':1,'parietal_izq':2,'temporal_izq':3,'occipital_izq':4,'frontal_der':5,'parietal_der':6,'temporal_der':7,'occipital_der':8,'cerebelo':9,'tronco':10}
sc=trimesh.Scene(); ex=trimesh.Scene()
allc=np.vstack([v for v,f in raw.values()]).mean(0)
for n,(v,f) in raw.items():
    t=trimesh.Trimesh(v,f,process=False); c=trimesh.visual.color.hex_to_rgba(COL[n.split('_')[0]])
    t.visual.face_colors=c
    sc.add_geometry(t.copy(),node_name=n)
    d=t.centroid-allc; d[2]*=0.6; e=t.copy(); e.apply_translation(d*0.6); ex.add_geometry(e,node_name=n)
    # orientación para imprimir: pose estable más probable, apoyada en z=0 y centrada
    p=t.copy(); tfs,probs=p.compute_stable_poses(n_samples=3,threshold=0.02)
    p.apply_transform(tfs[int(np.argmax(probs))])
    p.apply_translation([-p.bounds[:,0].mean()-0*0, -p.bounds[:,1].mean(), -p.bounds[0,2]])
    p.visual=trimesh.visual.ColorVisuals()
    fn=f'stl/{NUM[n]:02d}_{n}.stl'; p.export(fn)
    print(fn, p.extents.round(1), round(p.volume/1000,1),'cm3', 'wt',p.is_watertight)
sc.export('stl/montado.glb'); ex.export('stl/despiece.glb')
