const {chromium}=require('playwright'); const fs=require('fs'); const V=require('/tmp/claude-0/-home-claude-atlas-cerebro/02752242-dd27-5e6e-b4fe-2f40e2d19f44/scratchpad/render3d/bands.js');
const IMG={}; for(const b of [1,2,3,4]) for(const k of 'ABCD') IMG[b+k]='data:image/png;base64,'+fs.readFileSync('/tmp/claude-0/-home-claude-atlas-cerebro/02752242-dd27-5e6e-b4fe-2f40e2d19f44/scratchpad/render3d/outw/f'+b+k+'.png').toString('base64');
const strip=(b,k)=>'<img src="'+IMG[b+k]+'" style="width:180mm;height:45mm;display:block">';
const face=c=>'<div>'+[1,2,3,4].map(b=>'<img src="'+IMG[b+c[b-1]]+'" style="width:100%;display:block">').join('')+'</div>'; const R=require('./recetas.js');
const css=`@page{size:A4;margin:0} body{margin:0;font-family:'DejaVu Sans',Arial,sans-serif;color:#1d2430}
.pg{width:210mm;height:297mm;box-sizing:border-box;padding:12mm 15mm;page-break-after:always;position:relative}
h1{font-size:17pt;margin:0 0 2mm} h2{font-size:13pt;margin:0 0 1mm} p{font-size:9.5pt;margin:0 0 3mm;line-height:1.35}
.lab{font-size:8pt;color:#555;margin:4mm 0 1mm;display:flex;justify-content:space-between}
.cut{width:180mm;height:45mm;outline:0.2mm dashed #888;outline-offset:0}
.cut svg{display:block}
table{border-collapse:collapse;width:100%;font-size:9pt} td,th{border:0.2mm solid #bbb;padding:1.5mm 2mm;vertical-align:middle;text-align:left}
.th{width:30mm}`;
let html=`<style>${css}</style>`;
for(const b of [1,2,3,4]){
  html+=`<div class="pg"><h1>Franja ${b}: ${V[b].titulo}</h1><p>Recorta por la línea discontinua y pega cada tira en una cara del prisma ${b}, en el orden A, B, C, D (girando siempre hacia el mismo lado). Cada tira mide 180 × 45 mm. Imprime al 100 %, sin «ajustar a la página».</p>`;
  for(const k of 'ABCD') html+=`<div class="lab"><span><b>Prisma ${b} · Cara ${k}</b> · ${V[b][k].n}</span><span>✂</span></div><div class="cut">${strip(b,k)}</div>`;
  html+=`</div>`;
}
html+=`<div class="pg"><h1>Recetas de expresiones</h1><p>Gira cada prisma hasta la letra indicada (franja 1 arriba, franja 4 abajo). Fíjate en la <b>sonrisa falsa</b>: la boca sonríe pero los ojos y las mejillas no, igual que en una microexpresión que delata una emoción fingida. A la sonrisa real se le llama <i>sonrisa de Duchenne</i>.</p>
<table><tr><th class="th">Cara</th><th>Expresión</th><th style="white-space:nowrap">Prismas 1·2·3·4</th><th>Zona del cerebro implicada</th></tr>
${R.map(r=>`<tr><td><div style="width:30mm">${face(r.c)}</div></td><td><b>${r.e}</b></td><td style="font-size:13pt;letter-spacing:1mm;white-space:nowrap"><b>${r.c.split('').join(' ')}</b></td><td>${r.cer}</td></tr>`).join('')}</table>
<p style="margin-top:3mm">Con 4 prismas de 4 caras salen 4 × 4 × 4 × 4 = <b>256 combinaciones</b>. La mayoría no son expresiones «coherentes»; pregunta a tus compañeros cuáles reconocen. El desprecio (media sonrisa de un solo lado) no cabe en estas tiras porque es asimétrica.</p><p style="font-size:8pt;color:#666">Imágenes: cabeza 3D «facecap» (Face Cap, Bannaflak; ejemplos de three.js) con 52 formas de expresión basadas en el sistema FACS de Paul Ekman. Entre paréntesis, la unidad de acción (AU) de FACS. Las arrugas de cada músculo se han dibujado encima del render.</p></div>`;
(async()=>{const b=await chromium.launch(); const p=await b.newPage(); await p.setContent(html); await p.pdf({path:'laminas-microexpresiones-realistas.pdf',format:'A4',printBackground:true,preferCSSPageSize:true});
await p.setViewportSize({width:794,height:1123}); await p.screenshot({path:'pdfprev.png',fullPage:false}); await b.close();})();
