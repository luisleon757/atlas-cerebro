const {chromium}=require('playwright'); const http=require('http'),fs=require('fs'),path=require('path'); const V=require('./bands.js');
const srv=http.createServer((q,s)=>{const f=path.join(__dirname,decodeURIComponent(q.url.split('?')[0])); fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end();} const t={'.js':'text/javascript','.wasm':'application/wasm','.html':'text/html'}[path.extname(f)]||'application/octet-stream'; s.writeHead(200,{'Content-Type':t}); s.end(d);});}).listen(8790);
// encuadre: px de referencia del render neutro de 1200 px (half=1.23012, cy=0.198358)
const half0=1.2301215992115877, cy0=0.19835790713208656, cx0=0.0005709;
const P0=+process.env.P0||360.5, K=+process.env.K||0.297;   // mm por px
const wy=px=>cy0+half0-px*(2*half0/1200);
const PXW=2126, PXH=531; fs.mkdirSync('out',{recursive:true});
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']}); const p=await b.newPage({viewport:{width:PXW,height:PXH}});
p.on('pageerror',e=>console.log('err',e.message));
await p.goto('http://localhost:8790/view.html'); await p.evaluate(()=>window.ready); await p.evaluate(([w,h])=>window.setSize(w,h),[PXW,PXH]);
for(const band of [1,2,3,4]) for(const k of 'ABCD'){
  const top=P0+(band-1)*45/K, bot=P0+band*45/K; const cy=(wy(top)+wy(bot))/2, half=(wy(top)-wy(bot))/2;
  const d=await p.evaluate(([s,cam])=>window.shot(s,cam),[V[band][k].s,{cx:cx0,cy,half,w2h:4}]);
  fs.writeFileSync(`out/f${band}${k}.png`,Buffer.from(d.split(',')[1],'base64')); }
await b.close(); srv.close(); console.log('ok');})();
