# Arrugas por músculo: se dibujan como surcos (mapa de relieve) sobre cada tira renderizada
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
import os, sys
W,H=2126,531
def bez(p0,p1,p2,n=60):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2=map(np.array,(p0,p1,p2))
    return [tuple(v) for v in ((1-t)**2*p0+2*(1-t)*t*p1+t**2*p2)]
def mirror(c,cx=1063): return [(2*cx-x,y) for x,y in c]
def both(c,dy=0): return [c,[(x,y+dy) for x,y in mirror(c)]]
L={}  # (franja,variante) -> lista de (curva, fuerza, ancho px)
# Franja 1: frente y cejas
def wave(x0,x1,y,amp,n=80,ph=0):
    xs=np.linspace(x0,x1,n); return [(x, y+amp*np.sin((x-x0)/(x1-x0)*np.pi*2.2+ph)-28*np.sin((x-x0)/(x1-x0)*np.pi)) for x in xs]
L['1B']=[(wave(380,1750,32,5),0.9,8),(wave(470,1660,72,6,ph=1),0.85,8),(bez((860,118),(1063,100),(1270,118)),0.7,7)]
L['1C']=[(bez((1020,340),(1010,430),(995,531)),1.0,10),(bez((1108,340),(1118,430),(1133,531)),1.0,10),
         ]
L['1D']=[(bez((700,215-i*62),(1063,145-i*62),(1430,215-i*62)),0.9-0.15*i,8) for i in range(3)]+\
        [(bez((1030,360),(1035,430),(1028,531)),0.6,5),(bez((1098,360),(1094,430),(1100,531)),0.6,5)]
# Franja 2: ojos
L['2B']=[(c,0.5,5) for c in both(bez((330,95),(510,40),(720,95)),dy=40)]
L['2C']=[(c,0.7,4) for c in both(bez((320,250),(510,300),(720,250)),dy=40)]+[(c,0.5,4) for c in both(bez((350,290),(510,335),(690,290)),dy=40)]
crow=[]
for a,l in [(-30,120),(-8,140),(14,140),(36,110)]:
    r=np.radians(a); x0,y0=250,190
    crow.append(bez((x0,y0),(x0-l*0.5*np.cos(r),y0+l*0.5*np.sin(r)-6),(x0-l*np.cos(r),y0+l*np.sin(r))))
L['2D']=[(c,0.9,5) for c in crow]+[(c,0.9,5) for c in [[(2*1063-x+0,y+40) for x,y in c] for c in crow]]+\
        [(c,0.8,6) for c in both(bez((330,280),(510,340),(700,280)),dy=40)]+[(c,0.5,5) for c in both(bez((360,330),(510,380),(670,330)),dy=40)]
# Franja 3: nariz y mejillas
naso_up=bez((775,350),(700,430),(650,531))
L['3B']=[(c,1.0,5) for c in both(bez((900,40),(940,20),(985,40)))]+[(c,0.9,5) for c in both(bez((880,85),(930,60),(990,80)))]+\
        [(c,0.8,5) for c in both(bez((905,130),(945,115),(990,125)))]+[(c,0.9,13) for c in both(naso_up)]+[(c,0.5,4) for c in both(bez((990,10),(1063,0),(1136,10)))]
L['3C']=[(c,1.0,16) for c in both(naso_up)]
L['3D']=[(c,0.6,12) for c in both(naso_up)]+[(c,0.5,5) for c in both(bez((905,60),(945,40),(990,60)))]
# Franja 4: boca y barbilla
naso_lo=bez((650,0),(560,70),(470,150))
L['4A']=[(c,1.0,16) for c in both(naso_lo,dy=20)]+[(c,0.6,5) for c in both(bez((430,120),(420,160),(440,200)),dy=20)]
L['4B']=[(c,0.5,7) for c in both(bez((650,0),(590,80),(560,150)),dy=20)]+[(c,0.9,7) for c in both(bez((520,215),(540,300),(600,400)),dy=20)]+\
        [(bez((880,420),(1063,470),(1250,420)),0.8,6)]
L['4C']=[(c,0.4,6) for c in both(bez((650,0),(600,70),(580,140)),dy=20)]+[(bez((900,400),(1063,440),(1230,400)),0.7,6)]+\
        []
L['4D']=[(c,0.7,13) for c in both(bez((650,0),(590,90),(580,200)),dy=20)]
def stipple(seed=1):  # textura de «piel de naranja» de la barbilla (músculo mentoniano)
    rng=np.random.default_rng(seed); z=np.zeros((H,W)); 
    for _ in range(140):
        x=rng.normal(1063,110); y=rng.normal(470,35)
        if 0<y<H: z[int(y),int(np.clip(x,0,W-1))]=1
    return gaussian_filter(z,7)*25
def apply(img,lines,extra=None):
    W_,H_=W,H; dark=np.zeros((H,W)); sh=np.zeros((H,W)); lx,ly=-0.45,-0.9   # luz de arriba a la izquierda
    for c,f,w in lines:
        hm=Image.new('F',(W,H),0); ImageDraw.Draw(hm).line(c,fill=1.0,width=3,joint='curve')
        m=np.asarray(hm,float)
        crease=gaussian_filter(m,max(2.5,w*0.32)); crease=crease/(crease.max()+1e-9)*f          # pliegue fino y oscuro
        fold=gaussian_filter(m,w*2.4); fold=fold/(fold.max()+1e-9)*f                 # relieve ancho y suave
        gy,gx=np.gradient(-fold); dark+=crease*0.45+fold*0.30; sh+=(gx*lx+gy*ly)*w*2.4
    if extra is not None:
        gy,gx=np.gradient(-extra); dark+=extra*0.25; sh+=(gx*lx+gy*ly)*9
    a=np.asarray(img.convert('RGB'),float)
    out=a*(1-0.36*np.clip(dark,0,1.2))[...,None]*(1+0.40*np.clip(sh,-0.6,0.12))[...,None]
    return Image.fromarray(np.clip(out,0,255).astype(np.uint8))
os.makedirs('outw',exist_ok=True)
for b in '1234':
    for k in 'ABCD':
        im=Image.open(f'out/f{b}{k}.png')
        ex=stipple() if b+k in ('4B','4C') else None
        apply(im,L.get(b+k,[]),ex).save(f'outw/f{b}{k}.png')
print('ok')
