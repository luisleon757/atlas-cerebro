import numpy as np, trimesh, os
from manifold3d import Manifold, Mesh
os.makedirs('stl',exist_ok=True)
FN=96
def cyl(d,h,z=0,x=0,y=0,fn=FN): return Manifold.cylinder(h,d/2,d/2,fn).translate((x,y,z))
def box(a,b,c,x=0,y=0,z=0,center_xy=True): m=Manifold.cube((a,b,c)); return m.translate((x-(a/2 if center_xy else 0),y-(b/2 if center_xy else 0),z))
def hexp(af,h,z=0): r=af/np.sqrt(3); return Manifold.cylinder(h,r,r,6).translate((0,0,z))
def tm(m): g=m.to_mesh(); return trimesh.Trimesh(np.asarray(g.vert_properties)[:,:3],np.asarray(g.tri_verts))
S,H,T=180.0,45.0,1.6         # prisma: lado, alto, pared
BRG_D,BRG_H=22.4,7.0          # rodamiento 608 (22 x 7) con holgura
MAG_D,MAG_H=6.3,2.2           # imán 6 x 2 mm
ROD=8.6                       # varilla M8
HUB=58.0; REC_D,REC_H=44.0,9.0  # cubo central y hueco para el separador
# --- prisma ---
walls=box(S,S,H)-box(S-2*T,S-2*T,H+2,z=-1)
hub=cyl(HUB,REC_H+BRG_H+3)+cyl(BRG_D+7,H)
ribs=Manifold()
for a in range(0,360,45):
    L=(S/2-T)/ (np.cos(np.radians(a%90)) if a%90==0 else np.cos(np.radians(45)))
    r=box(L-HUB/2+1.5,3,12,center_xy=False,y=0).translate((HUB/2-1,-1.5,0)).rotate((0,0,a))
    ribs=ribs+r
# nervio superior para rigidez del borde
prism=walls+hub+ribs
cut=cyl(REC_D,REC_H,-1)+cyl(REC_D,1,0)   # hueco del separador (abierto abajo)
cut=cyl(REC_D,REC_H+1,-1)
cut=cut+cyl(BRG_D,BRG_H,REC_H)+cyl(ROD+0.6,H,0)+cyl(BRG_D,BRG_H+1,H-BRG_H)
for a in (0,90,180,270):
    x,y=15*np.cos(np.radians(a)),15*np.sin(np.radians(a)); cut=cut+cyl(MAG_D,MAG_H,REC_H,x,y)
prism=prism-cut
# --- separador ---
SP_D,SP_H=REC_D-3,REC_H-1
sep=cyl(SP_D,SP_H)+cyl(11.5,1.0,SP_H)
sep=sep-cyl(ROD,SP_H+3,-1)-hexp(13.4,6.6,-0.01)
for a in (0,180):
    x,y=15*np.cos(np.radians(a)),15*np.sin(np.radians(a)); sep=sep-cyl(MAG_D,MAG_H+0.01,SP_H-MAG_H,x,y)
# --- base: disco con columna y tuerca embebida, 4 agujeros para atornillar a una tabla ---
base=cyl(130,6)+cyl(34,24)
base=base-cyl(ROD,40,-1)-hexp(13.4,6.6,-0.01)-hexp(13.4,6.6,24-6.6+0.01)
for a in (45,135,225,315):
    x,y=50*np.cos(np.radians(a)),50*np.sin(np.radians(a)); base=base-cyl(4.5,10,-1,x,y)-cyl(9,3,3.01,x,y)
# --- tapa para el prisma de arriba ---
tapa=box(S,S,1.6)-cyl(ROD+1,5,-1)
out={'prisma':prism,'separador':sep,'base':base,'tapa':tapa}
for n,m in out.items():
    t=tm(m); t.export(f'stl/{n}.stl'); print(n,'estanco',t.is_watertight,'vol cm3',round(t.volume/1000,1),'medidas',t.extents.round(1))
# montaje de comprobación: base, y por nivel separador + prisma
asm=[tm(base)]; z=24+1.0
for i in range(4):
    asm.append(tm(sep.translate((0,0,z)))); asm.append(tm(prism.translate((0,0,z))))
    z+=H+1.5
asm.append(tm(tapa.translate((0,0,z-1.5))))
trimesh.util.concatenate(asm).export('stl/_montaje.glb')
print('alto total mm',round(z-1.5+1.6,1))
