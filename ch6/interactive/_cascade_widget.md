```{=html}
<div id="csw" class="csw">
  <div class="csw-ctrl">
    <label>primary <i>K</i><sub>c</sub> = <b id="csw-kcv"></b><input id="csw-kc" type="range" min="0.2" max="12" step="0.1" value="3"></label>
    <label><i>τ</i><sub>I</sub>
      <select id="csw-ti"><option>0.05</option><option selected>0.5</option><option>5</option></select></label>
    <label>slave <i>K</i><sub>c2</sub> = <b id="csw-kc2v"></b><input id="csw-kc2" type="range" min="0" max="60" step="1" value="18"></label>
    <label><input type="radio" name="csw-in" value="L" checked> load step</label>
    <label><input type="radio" name="csw-in" value="R"> set-point step</label>
  </div>
  <div class="csw-read" id="csw-read"></div>
  <canvas id="csw-c" width="1100" height="400"></canvas>
</div>
<style>
.csw{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:17px;color:#222}
.csw-ctrl{display:flex;flex-wrap:wrap;gap:16px;align-items:center;margin-bottom:4px}
.csw-ctrl input[type=range]{width:170px;vertical-align:middle}
.csw select{font-size:15px}
.csw-read{font-family:ui-monospace,Menlo,monospace;font-size:15px;margin:2px 0 6px}
.csw-read .r{color:#C00000}.csw-read .n{color:#333399}
.csw canvas{border:1px solid #ddd;border-radius:4px;max-width:100%;height:auto;background:#fff}
</style>
<script>
(function(){
const $=id=>document.getElementById(id);
// Ex 6.1: Gv=0.5/(s+1), GL=0.75/(s+1), Gp=0.8/(2s+1); primary PI, slave P (Kc2)
function sim(Kc,tI,Kc2,cascade,input){
  const dt=0.004,T=30,n=Math.round(T/dt);let xv=0,xl=0,xp=0,I=0;const ys=[];
  const R=input==='R'?1:0,L=input==='L'?1:0;
  for(let k=0;k<=n;k++){
    const C=xp,e=R-C;const p=Kc*(e+I/tI);I+=e*dt;
    const a=xv+xl;const m=cascade?Kc2*(p-a):p;
    xv+=dt*(-xv+0.5*m);xl+=dt*(-xl+0.75*L);xp+=dt*(-xp+0.8*a)/2;
    ys.push(C);if(!isFinite(C)||Math.abs(C)>1e3)break;}
  return ys;
}
function stable(Kc,tI,Kc2,cascade){ // Routh on the characteristic polynomial
  let a;
  if(cascade){const tv=1/(1+0.5*Kc2),kv=0.5*Kc2/(1+0.5*Kc2),g=0.8*kv*Kc; // tI s(tv s+1)(2s+1)+g(tI s+1)
    a=[tI*2*tv,tI*(tv+2),tI+g*tI,g];
    if(Kc2===0)return{ok:false,txt:'K_c2 = 0: no slave action'};}
  else{const g=0.4*Kc;a=[2*tI,3*tI,tI+g*tI,g];}
  const ok=a.every(v=>v>0)&&a[1]*a[2]>a[0]*a[3];
  return{ok};
}
const cv=$('csw-c'),g=cv.getContext('2d');
function draw(){
  const Kc=+$('csw-kc').value,tI=+$('csw-ti').value,Kc2=+$('csw-kc2').value;
  const inp=document.querySelector('input[name=csw-in]:checked').value;
  $('csw-kcv').textContent=Kc.toFixed(1);$('csw-kc2v').textContent=Kc2;
  const yn=sim(Kc,tI,Kc2,false,inp),yc=sim(Kc,tI,Kc2,true,inp);
  const sn=stable(Kc,tI,Kc2,false),sc=stable(Kc,tI,Kc2,true);
  const pk=y=>Math.max(...y.map(Math.abs)).toFixed(3);
  $('csw-read').innerHTML=`<span class="r">single loop: ${sn.ok?'stable':'UNSTABLE'}${inp==='L'&&sn.ok?' · peak '+pk(yn):''}</span> &nbsp;&nbsp; `+
    `<span class="n">cascade: ${sc.ok?'stable':'UNSTABLE'}${inp==='L'&&sc.ok?' · peak '+pk(yc):''} · slave τ<sub>v</sub>* = ${(1/(1+0.5*Kc2)).toFixed(3)}, K<sub>v</sub>* = ${(0.5*Kc2/(1+0.5*Kc2)).toFixed(3)}</span>`;
  const W=cv.width,H=cv.height,x0=60,x1=W-14,y0=14,y1=H-40;
  let lo=inp==='L'?-0.2:-0.2,hi=inp==='L'?0.3:2.0;
  g.clearRect(0,0,W,H);
  const X=t=>x0+t/30*(x1-x0),Y=v=>y1-(v-lo)/(hi-lo)*(y1-y0);
  g.font='14px system-ui';g.fillStyle='#555';g.textAlign='right';
  const st=inp==='L'?0.1:0.5;for(let v=Math.ceil(lo/st)*st;v<=hi+1e-9;v+=st){g.strokeStyle='#eee';g.beginPath();g.moveTo(x0,Y(v));g.lineTo(x1,Y(v));g.stroke();g.fillText(v.toFixed(1),x0-6,Y(v)+4);}
  g.textAlign='center';for(let t=0;t<=30;t+=5){g.fillText(t,X(t),y1+18);}g.fillText('time',(x0+x1)/2,H-4);
  g.strokeStyle='#999';g.strokeRect(x0,y0,x1-x0,y1-y0);
  if(inp==='R'){g.setLineDash([5,4]);g.strokeStyle='#888';g.beginPath();g.moveTo(x0,Y(1));g.lineTo(x1,Y(1));g.stroke();g.setLineDash([]);}
  g.save();g.beginPath();g.rect(x0,y0,x1-x0,y1-y0);g.clip();
  const dt=0.004;[[yn,'#C00000'],[yc,'#333399']].forEach(([y,c])=>{g.strokeStyle=c;g.lineWidth=2.4;g.beginPath();
    y.forEach((v,i)=>{const px=X(i*dt),py=Y(Math.max(lo-1,Math.min(hi+1,v)));i?g.lineTo(px,py):g.moveTo(px,py);});g.stroke();});
  g.restore();
  g.textAlign='left';g.font='15px system-ui';g.fillStyle='#C00000';g.fillText('— single loop',x1-210,y0+22);g.fillStyle='#333399';g.fillText('— cascade',x1-210,y0+44);
}
['csw-kc','csw-ti','csw-kc2'].forEach(id=>$(id).addEventListener('input',draw));
document.querySelectorAll('input[name=csw-in]').forEach(r=>r.addEventListener('change',draw));
draw();
})();
</script>
```
