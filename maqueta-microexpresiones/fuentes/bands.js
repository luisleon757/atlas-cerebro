// Variantes por franja (blendshapes ARKit ≈ unidades de acción FACS)
const two=(n,v)=>({[n+'_L']:v,[n+'_R']:v});
module.exports={
 1:{titulo:'Frente y cejas', A:{n:'Neutra',s:{}}, B:{n:'Cejas levantadas (AU1+2)',s:{browInnerUp:1,...two('browOuterUp',1)}},
    C:{n:'Cejas fruncidas (AU4)',s:two('browDown',1)}, D:{n:'Cejas tristes (AU1+4)',s:{browInnerUp:1,...two('browDown',0.35)}}},
 2:{titulo:'Ojos', A:{n:'Neutros',s:{}}, B:{n:'Muy abiertos (AU5)',s:two('eyeWide',1)},
    C:{n:'Tensos (AU7)',s:{...two('eyeSquint',1),...two('eyeBlink',0.2)}}, D:{n:'Ojos que sonríen (AU6)',s:{...two('eyeSquint',0.6),...two('cheekSquint',1),...two('eyeBlink',0.15)}}},
 3:{titulo:'Nariz y mejillas', A:{n:'Neutra',s:{}}, B:{n:'Nariz arrugada (AU9)',s:two('noseSneer',1)},
    C:{n:'Mejillas levantadas (AU6)',s:{...two('cheekSquint',1)}}, D:{n:'Nariz tensa',s:two('noseSneer',0.4)}},
 4:{titulo:'Boca y barbilla', A:{n:'Sonrisa (AU12)',s:{...two('mouthSmile',1),jawOpen:0.05}}, B:{n:'Comisuras abajo (AU15)',s:{...two('mouthFrown',1),mouthShrugLower:0.5}},
    C:{n:'Labios apretados (AU24)',s:{...two('mouthPress',0.8),mouthRollUpper:0.3,mouthRollLower:0.3,...two('mouthFrown',0.3)}}, D:{n:'Boca abierta (AU26)',s:{jawOpen:0.3,mouthFunnel:0.25}}},
};
