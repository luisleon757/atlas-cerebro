// Genera las franjas de la cara (SVG en mm, 180 x 180, 4 franjas de 45 mm)
const SK='#f1c7a8', SK2='#e3ad8c', LN='#5a3b2e', HR='#3e2b20', W=180;
const base=()=>`
<rect x="0" y="0" width="180" height="180" fill="#fff"/>
<path d="M25 82 C18 24 58 1 90 1 C122 1 162 24 155 82 Z" fill="${HR}"/>
<path d="M28 70 Q20 62 22 78 Q24 100 34 104 Z" fill="${SK2}" stroke="${LN}" stroke-width="0.8"/>
<path d="M152 70 Q160 62 158 78 Q156 100 146 104 Z" fill="${SK2}" stroke="${LN}" stroke-width="0.8"/>
<path d="M90 8 C135 8 152 40 152 78 C152 125 128 176 90 176 C52 176 28 125 28 78 C28 40 45 8 90 8 Z" fill="${SK}" stroke="${LN}" stroke-width="0.9"/>
<path d="M29 64 C31 28 58 6 90 6 C122 6 149 28 151 64 C146 38 136 24 122 17 C106 21 86 19 68 13 C50 21 36 38 29 64 Z" fill="${HR}"/>
<path d="M88 78 C86 88 86 92 86 92" fill="none" stroke="${SK2}" stroke-width="0.9"/>
`;
const L=(d,w=0.9,c=LN)=>`<path d="${d}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round"/>`;
const brow=(d)=>`<path d="${d}" fill="none" stroke="${HR}" stroke-width="3.2" stroke-linecap="round"/>`;
// ojo genérico: centro cx, cy; apertura arriba/abajo; iris visible
function eye(cx,cy,up,dn,{lidTilt=0,iris=4.6,squint=0}={}){
  const w=12, l=cx-w, r=cx+w;
  const top=`M${l} ${cy} Q${cx} ${cy-up*2+lidTilt} ${r} ${cy}`, bot=`Q${cx} ${cy+dn*2} ${l} ${cy}`;
  const id='e'+cx+'_'+cy+'_'+up+'_'+dn;
  return `<clipPath id="${id}"><path d="${top} ${bot} Z"/></clipPath>
  <path d="${top} ${bot} Z" fill="#fff"/>
  <g clip-path="url(#${id})"><circle cx="${cx}" cy="${cy+(up>dn?0.6:0)}" r="${iris}" fill="#6b4b2c"/><circle cx="${cx}" cy="${cy+(up>dn?0.6:0)}" r="${iris*0.45}" fill="#1b120c"/><circle cx="${cx+1.4}" cy="${cy-1.4}" r="0.9" fill="#fff"/></g>
  ${L(top+' '+bot+' Z',0.9)}`;
}
const both=f=>f(64,1)+f(116,-1);
const V={
 1:{ titulo:'Frente y cejas', A:{n:'Neutra', s:both((x,s)=>brow(`M${x-11} 38 Q${x} 34 ${x+11} 38`))},
     B:{n:'Cejas levantadas', s:both((x,s)=>brow(`M${x-11} 31 Q${x} 24 ${x+11} 31`))+L('M64 22 Q90 18 116 22',0.7,SK2)+L('M68 26 Q90 22.5 112 26',0.7,SK2)},
     C:{n:'Cejas fruncidas', s:brow('M53 36 L76 42')+brow('M127 36 L104 42')+L('M87 33 L86.5 41',0.8,SK2)+L('M93 33 L93.5 41',0.8,SK2)},
     D:{n:'Cejas tristes', s:brow('M53 40 Q66 38 77 32')+brow('M127 40 Q114 38 103 32')+L('M80 24 Q90 21 100 24',0.7,SK2)+L('M83 28 Q90 26 97 28',0.6,SK2)} },
 2:{ titulo:'Ojos', A:{n:'Neutros', s:both((x)=>eye(x,64,3.2,2.6))},
     B:{n:'Muy abiertos', s:both((x)=>eye(x,63,5.6,4.2,{iris:4.2}))},
     C:{n:'Tensos / entornados', s:both((x)=>eye(x,65,1.6,1.4,{iris:4.6}))+both((x)=>L(`M${x-12} 61 Q${x} 59 ${x+12} 61`,0.6,SK2))},
     D:{n:'Ojos que sonríen', s:both((x)=>eye(x,64,2.6,0.6))+L('M44 60 L39 58 M44 64 L38 64 M44 68 L39 70',0.7,SK2)+L('M136 60 L141 58 M136 64 L142 64 M136 68 L141 70',0.7,SK2)+both((x)=>L(`M${x-10} 70 Q${x} 73 ${x+10} 70`,0.7,SK2))} },
 3:{ titulo:'Nariz y mejillas', A:{n:'Neutra', s:L('M86 92 C85 104 80 112 82 117 C85 120 88 118 90 119 C92 118 95 120 98 117 C100 112 95 104 94 92')},
     B:{n:'Nariz arrugada', s:L('M86 92 C85 103 79 110 81 115 C84 118 88 116 90 117 C92 116 96 118 99 115 C101 110 95 103 94 92')+L('M84 97 Q90 95 96 97 M83 101 Q90 99 97 101',0.7,SK2)+L('M79 116 C72 120 70 126 70 131',0.9,SK2)+L('M101 116 C108 120 110 126 110 131',0.9,SK2)},
     C:{n:'Mejillas levantadas', s:`<ellipse cx="58" cy="108" rx="13" ry="8" fill="#ec9c8c" opacity=".55"/><ellipse cx="122" cy="108" rx="13" ry="8" fill="#ec9c8c" opacity=".55"/>`+L('M86 92 C85 104 80 112 82 117 C85 120 88 118 90 119 C92 118 95 120 98 117 C100 112 95 104 94 92')+L('M78 117 C70 121 66 127 66 134',1,SK2)+L('M102 117 C110 121 114 127 114 134',1,SK2)},
     D:{n:'Aletas abiertas', s:L('M86 92 C85 104 78 111 79 117 C83 121 88 118 90 119 C92 118 97 121 101 117 C102 111 95 104 94 92')+`<ellipse cx="84" cy="117" rx="2.6" ry="1.4" fill="${LN}"/><ellipse cx="96" cy="117" rx="2.6" ry="1.4" fill="${LN}"/>`} },
 4:{ titulo:'Boca y barbilla', A:{n:'Sonrisa', s:`<path d="M70 146 Q90 166 110 146 Q90 156 70 146 Z" fill="#fff" stroke="${LN}" stroke-width="0.9"/>`+L('M70 146 Q90 166 110 146',1.1)+L('M68 144 Q70 146 71 148',0.7,SK2)+L('M112 144 Q110 146 109 148',0.7,SK2)},
     B:{n:'Comisuras hacia abajo', s:L('M72 156 Q90 146 108 156',1.3)+L('M84 166 Q90 168 96 166',0.6,SK2)},
     C:{n:'Labios apretados', s:L('M74 151 L106 151',1.6)+L('M74 151 Q73 150 72 149 M106 151 Q107 150 108 149',0.8)+L('M84 160 Q90 162 96 160',0.6,SK2)},
     D:{n:'Boca abierta', s:`<ellipse cx="90" cy="153" rx="9" ry="11" fill="#5b2a2a" stroke="${LN}" stroke-width="0.9"/><path d="M83 146 Q90 143 97 146 L97 147.5 Q90 145 83 147.5 Z" fill="#fff"/>`} },
};
const BAND={1:[0,45],2:[45,90],3:[90,135],4:[135,180]};
function strip(b,k){ const [y0]=BAND[b];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 ${y0} 180 45" width="180mm" height="45mm"><defs><clipPath id="c${b}${k}"><rect x="0" y="${y0}" width="180" height="45"/></clipPath></defs><g clip-path="url(#c${b}${k})">${base()}${V[b][k].s}</g></svg>`; }
function face(combo){ // combo like 'ADCA'
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180" width="100%">${[1,2,3,4].map(b=>{const [y0]=BAND[b];return `<svg x="0" y="${y0}" width="180" height="45" viewBox="0 ${y0} 180 45">${base()}${V[b][combo[b-1]].s}</svg>`}).join('')}</svg>`; }
module.exports={V,strip,face};
