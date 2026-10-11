import random, math
from PIL import Image, ImageDraw, ImageFont
random.seed(42)
W=H=1200
img=Image.new('RGB',(W,H),'#ffffff'); d=ImageDraw.Draw(img)
cols=['#3d7bff','#f2b705','#19b37a','#a05cf0','#ff7a2f','#e8436a','#16202b','#2d56c8']
for i in range(900):
    x,y=random.uniform(0,W),random.uniform(0,H); r=random.uniform(6,34); c=random.choice(cols)
    k=random.random()
    if k<0.35: d.ellipse([x-r,y-r,x+r,y+r],fill=c)
    elif k<0.7:
        a=random.uniform(0,6.28); d.polygon([(x+r*math.cos(a+j*2.094),y+r*math.sin(a+j*2.094)) for j in range(3)],fill=c)
    else:
        a=random.uniform(0,6.28); w=r*0.35
        d.line([(x-r*math.cos(a),y-r*math.sin(a)),(x+r*math.cos(a),y+r*math.sin(a))],fill=c,width=int(max(3,w)))
# central panel with brain
brain=Image.open('t/d1.png').crop((140,140,750,650)).convert('RGB')
bw=760; brain=brain.resize((bw,int(bw*brain.height/brain.width)))
px,py=(W-bw)//2,150
d.rounded_rectangle([px-20,py-20,px+bw+20,py+brain.height+20],radius=40,fill='#ffffff',outline='#16202b',width=8)
img.paste(brain,(px,py))
# title band
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',78)
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',40)
d.rounded_rectangle([90,880,W-90,1110],radius=36,fill='#16202b')
d.text((W/2,955),'ATLAS DEL CEREBRO',font=f,fill='#ffffff',anchor='mm')
d.text((W/2,1045),'Apunta la cámara aquí',font=f2,fill='#f2b705',anchor='mm')
d.rectangle([0,0,W-1,H-1],outline='#16202b',width=14)
img.save('tarjeta.png')
img.save('tarjeta.pdf',resolution=150)
print('ok')
