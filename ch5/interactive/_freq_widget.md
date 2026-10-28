```{=html}
<div id="frw" class="frw">
  <div class="frw-ctrl">
    <label>System
      <select id="frw-sys">
        <option value="ex511">Ex 5.11 — P, 3(−2s+1)/[(10s+1)(5s+1)]</option>
        <option value="ex512">Ex 5.12 — PI (τ<sub>I</sub>=12.7), same plant</option>
        <option value="ex44">Ex 4.4 — P, 0.8e<sup>−2s</sup>/(5s+1)</option>
        <option value="ex42">Ex 4.2 — P, 1/[(s+1)(s+2)(s+3)]</option>
      </select>
    </label>
    <label class="frw-k">K<sub>c</sub> = <b id="frw-kval">1.00</b>
      <input id="frw-k" type="range" min="0" max="1000" value="300">
    </label>
    <span id="frw-status" class="frw-status"></span>
  </div>
  <div class="frw-read" id="frw-read"></div>
  <div class="frw-plots">
    <canvas id="frw-b" width="420" height="400"></canvas>
    <canvas id="frw-n" width="360" height="400"></canvas>
    <canvas id="frw-t" width="400" height="400"></canvas>
  </div>
</div>
<style>
.frw{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:18px;color:#222}
.frw-ctrl{display:flex;flex-wrap:wrap;gap:18px;align-items:center;margin-bottom:4px}
.frw select{font-size:16px;padding:2px 4px}
.frw-k{display:flex;align-items:center;gap:8px}
.frw-k input{width:260px}
.frw-status{font-weight:600;padding:2px 10px;border-radius:4px}
.frw-status.ok{background:#e6f2e8;color:#2E7D32}.frw-status.bad{background:#fbe9e9;color:#C00000}.frw-status.mar{background:#fff4e0;color:#b36b00}
.frw-read{font-family:ui-monospace,Menlo,monospace;font-size:15px;margin:2px 0 6px;color:#333}
.frw-read b.g{color:#C00000}.frw-read b.p{color:#2E7D32}
.frw-plots{display:flex;gap:10px;flex-wrap:wrap}
.frw canvas{border:1px solid #ddd;border-radius:4px;max-width:100%;height:auto;background:#fff}
</style>
<script>
(function(){
const SYS={
  ex511:{num:[-6,3],den:[50,15,1],delay:0,tI:0,kmax:3.5,kdef:1.5,tmax:100},
  ex512:{num:[-6,3],den:[50,15,1],delay:0,tI:12.699,kmax:2.5,kdef:1.136,tmax:120},
  ex44:{num:[0.8],den:[5,1],delay:2,tI:0,kmax:8,kdef:2.87,tmax:60},
  ex42:{num:[1],den:[1,6,11,6],delay:0,tI:0,kmax:80,kdef:30,tmax:12}
};
const $=id=>document.getElementById(id);
const W=Array.from({length:900},(_,i)=>Math.pow(10,-3+5*i/899));
function polyC(p,w){let re=0,im=0;for(const c of p){const r=re*0-im*w,i=re*w+im*0;re=r+c;im=i;}return[re,im];}
function L(S,k,w){ // complex loop gain Kc*C(jw)*G(jw)*e^{-jw theta}
  const [nr,ni]=polyC(S.num,w),[dr,di]=polyC(S.den,w),d=dr*dr+di*di;
  let re=(nr*dr+ni*di)/d, im=(ni*dr-nr*di)/d;
  if(S.tI){const cr=1,ci=-1/(S.tI*w);const r=re*cr-im*ci,i=re*ci+im*cr;re=r;im=i;}
  if(S.delay){const c=Math.cos(-w*S.delay),s=Math.sin(-w*S.delay);const r=re*c-im*s,i=re*s+im*c;re=r;im=i;}
  return[k*re,k*im];
}
function resp(S,k){const m=[],p=[],z=[];let prev=null,off=0;
  for(const w of W){const [r,i]=L(S,k,w);let a=Math.atan2(i,r)*180/Math.PI;
    if(prev!==null){while(a+off-prev>180)off-=360;while(a+off-prev<-180)off+=360;}
    a+=off;prev=a;m.push(Math.hypot(r,i));p.push(a);z.push([r,i]);}
  // first phase crossover of -180 (from above)
  let wc=null,gm=Infinity,wg=null,pm=Infinity;
  for(let j=1;j<W.length;j++){if(p[j-1]>-180&&p[j]<=-180){const f=(-180-p[j-1])/(p[j]-p[j-1]);
      wc=W[j-1]*Math.pow(W[j]/W[j-1],f);const mm=m[j-1]*Math.pow(m[j]/m[j-1],f);gm=1/mm;break;}}
  for(let j=1;j<W.length;j++){if(m[j-1]>=1&&m[j]<1){const f=Math.log(m[j-1])/Math.log(m[j-1]/m[j]);
      wg=W[j-1]*Math.pow(W[j]/W[j-1],f);const ph=p[j-1]+f*(p[j]-p[j-1]);pm=180+ph;break;}}
  return{m,p,z,wc,gm,wg,pm};
}
function step(S,k){ // unity-feedback set-point step, plant in controllable canonical form, delay buffer
  const a0=S.den[0],den=S.den.map(x=>x/a0),num=S.num.map(x=>x/a0),n=den.length-1;
  const b=new Array(n).fill(0);for(let j=0;j<num.length;j++)b[num.length-1-j]=num[j]; // b[0]=const coeff
  const T=S.tmax,h=T/12000,nd=Math.round(S.delay/h);let x=new Array(n).fill(0),xi=0;
  const ubuf=new Array(nd+1).fill(0);const ts=[],ys=[],us=[];
  const f=(x,u)=>{const dx=new Array(n);for(let i=0;i<n-1;i++)dx[i]=x[i+1];let s=u;for(let i=0;i<n;i++)s-=den[n-i]*x[i];dx[n-1]=s;return dx;};
  for(let st=0;st<=12000;st++){
    let y=0;for(let i=0;i<n;i++)y+=b[i]*x[i];
    const e=1-y;const u=k*(e+(S.tI?xi/S.tI:0));
    ts.push(st*h);ys.push(y);us.push(u);
    ubuf.push(u);const ud=ubuf.shift();
    const k1=f(x,ud),k2=f(x.map((v,i)=>v+h/2*k1[i]),ud),k3=f(x.map((v,i)=>v+h/2*k2[i]),ud),k4=f(x.map((v,i)=>v+h*k3[i]),ud);
    x=x.map((v,i)=>v+h/6*(k1[i]+2*k2[i]+2*k3[i]+k4[i]));xi+=h*e;
    if(Math.abs(y)>1e3)break;}
  return{ts,ys,us};
}
function frame(g,x0,y0,w,h){g.strokeStyle='#999';g.lineWidth=1;g.strokeRect(x0,y0,w,h);}
function txt(g,s,x,y,al,col,font){g.fillStyle=col||'#555';g.font=font||'12px system-ui';g.textAlign=al||'center';g.fillText(s,x,y);}
function drawBode(R){
  const c=$('frw-b'),g=c.getContext('2d'),Wd=c.width,H=c.height;g.clearRect(0,0,Wd,H);
  const x0=64,x1=Wd-10,lw0=-3,lw1=2,X=w=>x0+(Math.log10(w)-lw0)/(lw1-lw0)*(x1-x0);
  // magnitude panel
  const my0=12,my1=190;let lm=R.m.map(v=>Math.log10(Math.max(v,1e-6)));
  let mmax=Math.ceil(Math.max(...lm,0.5)),mmin=Math.floor(Math.max(Math.min(...lm,-1),mmax-6));
  const Ym=v=>my1-(Math.log10(Math.max(v,1e-9))-mmin)/(mmax-mmin)*(my1-my0);
  const pp0=225,pp1=H-40;let pmin=Math.min(...R.p),pmx=Math.max(...R.p,0);
  pmin=Math.max(-720,Math.floor(Math.min(pmin,-200)/90)*90);pmx=Math.ceil(pmx/90)*90;
  const Yp=v=>pp1-(Math.max(v,pmin)-pmin)/(pmx-pmin)*(pp1-pp0);
  g.save();
  for(let e=lw0;e<=lw1;e++){g.strokeStyle='#eee';g.beginPath();g.moveTo(X(10**e),my0);g.lineTo(X(10**e),my1);g.moveTo(X(10**e),pp0);g.lineTo(X(10**e),pp1);g.stroke();txt(g,'10^'+e,X(10**e),pp1+16);}
  for(let e=mmin;e<=mmax;e++){g.strokeStyle='#eee';g.beginPath();g.moveTo(x0,Ym(10**e));g.lineTo(x1,Ym(10**e));g.stroke();txt(g,(e===0?'1':'10^'+e),x0-4,Ym(10**e)+4,'right');}
  for(let v=pmin;v<=pmx;v+=90){g.strokeStyle='#eee';g.beginPath();g.moveTo(x0,Yp(v));g.lineTo(x1,Yp(v));g.stroke();txt(g,v,x0-4,Yp(v)+4,'right');}
  g.strokeStyle='#888';g.beginPath();g.moveTo(x0,Ym(1));g.lineTo(x1,Ym(1));g.stroke();
  g.strokeStyle='#C00000';g.setLineDash([5,4]);g.beginPath();g.moveTo(x0,Yp(-180));g.lineTo(x1,Yp(-180));g.stroke();g.setLineDash([]);
  frame(g,x0,my0,x1-x0,my1-my0);frame(g,x0,pp0,x1-x0,pp1-pp0);
  g.beginPath();g.rect(x0,my0,x1-x0,my1-my0);g.rect(x0,pp0,x1-x0,pp1-pp0);g.clip();
  g.strokeStyle='#333399';g.lineWidth=2;g.beginPath();W.forEach((w,i)=>{i?g.lineTo(X(w),Ym(R.m[i])):g.moveTo(X(w),Ym(R.m[i]));});g.stroke();
  g.beginPath();W.forEach((w,i)=>{i?g.lineTo(X(w),Yp(R.p[i])):g.moveTo(X(w),Yp(R.p[i]));});g.stroke();
  if(R.wc){g.strokeStyle='#C00000';g.lineWidth=2.2;g.beginPath();g.moveTo(X(R.wc),Ym(1));g.lineTo(X(R.wc),Ym(1/R.gm));g.stroke();
    g.fillStyle='#C00000';g.beginPath();g.arc(X(R.wc),Yp(-180),4,0,7);g.fill();}
  if(R.wg){g.strokeStyle='#2E7D32';g.lineWidth=2.2;g.beginPath();g.moveTo(X(R.wg),Yp(-180));g.lineTo(X(R.wg),Yp(-180+R.pm));g.stroke();
    g.fillStyle='#2E7D32';g.beginPath();g.arc(X(R.wg),Ym(1),4,0,7);g.fill();}
  g.restore();
  txt(g,'AR',16,(my0+my1)/2,'center','#555','13px system-ui');txt(g,'φ°',16,(pp0+pp1)/2,'center','#555','13px system-ui');
  txt(g,'ω (rad/time)',(x0+x1)/2,H-6);
}
function drawNyq(R){
  const c=$('frw-n'),g=c.getContext('2d'),Wd=c.width,H=c.height;g.clearRect(0,0,Wd,H);
  // square window centred near -0.5 that always shows -1; far excursions are clipped
  let hs=1.6;R.z.forEach(v=>{if(Math.hypot(v[0],v[1])<4)hs=Math.max(hs,Math.abs(v[0]+0.5)*1.05,Math.abs(v[1])*1.05);});
  hs=Math.min(hs,3.2);const xmin=-0.5-hs,xmax=-0.5+hs,ymin=-hs,ymax=hs;
  const pad=34,sx=(Wd-pad-10)/(xmax-xmin),sy=(H-pad-10)/(ymax-ymin),s=Math.min(sx,sy);
  const cx=pad+((Wd-pad-10)-(xmax-xmin)*s)/2,cy=10+((H-pad-10)-(ymax-ymin)*s)/2;
  const X=x=>cx+(x-xmin)*s,Y=y=>cy+(ymax-y)*s;
  g.strokeStyle='#ccc';g.beginPath();g.moveTo(X(xmin),Y(0));g.lineTo(X(xmax),Y(0));g.moveTo(X(0),Y(ymin));g.lineTo(X(0),Y(ymax));g.stroke();
  g.strokeStyle='#bbb';g.setLineDash([4,4]);g.beginPath();g.arc(X(0),Y(0),s,0,2*Math.PI);g.stroke();g.setLineDash([]);
  frame(g,X(xmin),Y(ymax),(xmax-xmin)*s,(ymax-ymin)*s);
  g.save();g.beginPath();g.rect(X(xmin),Y(ymax),(xmax-xmin)*s,(ymax-ymin)*s);g.clip();
  g.strokeStyle='rgba(51,51,153,0.35)';g.lineWidth=1.5;g.setLineDash([5,4]);g.beginPath();R.z.forEach((v,i)=>{i?g.lineTo(X(v[0]),Y(-v[1])):g.moveTo(X(v[0]),Y(-v[1]));});g.stroke();g.setLineDash([]);
  g.strokeStyle='#333399';g.lineWidth=2;g.beginPath();R.z.forEach((v,i)=>{i?g.lineTo(X(v[0]),Y(v[1])):g.moveTo(X(v[0]),Y(v[1]));});g.stroke();
  if(R.wc){g.fillStyle='#C00000';g.beginPath();g.arc(X(-1/R.gm),Y(0),4.5,0,7);g.fill();}
  g.restore();
  g.strokeStyle='#C00000';g.lineWidth=2.5;g.beginPath();g.moveTo(X(-1)-7,Y(0));g.lineTo(X(-1)+7,Y(0));g.moveTo(X(-1),Y(0)-7);g.lineTo(X(-1),Y(0)+7);g.stroke();
  txt(g,'−1',X(-1),Y(0)+20,'center','#C00000','13px system-ui');
  txt(g,'Re',Wd/2,H-8);txt(g,'Nyquist (ω>0 solid)',Wd/2,22,'center','#555','13px system-ui');
}
function drawStep(S,k){
  const c=$('frw-t'),g=c.getContext('2d'),Wd=c.width,H=c.height;g.clearRect(0,0,Wd,H);
  const {ts,ys}=step(S,k);const x0=44,x1=Wd-10,y0=12,y1=H-40;
  let lo=Math.min(0,...ys),hi=Math.max(1.2,...ys);lo=Math.max(lo,-1);hi=Math.min(hi,2.5);
  const X=t=>x0+t/S.tmax*(x1-x0),Y=v=>y1-(v-lo)/(hi-lo)*(y1-y0);
  for(let v=Math.ceil(lo*2)/2;v<=hi;v+=0.5){g.strokeStyle='#eee';g.beginPath();g.moveTo(x0,Y(v));g.lineTo(x1,Y(v));g.stroke();txt(g,v.toFixed(1),x0-4,Y(v)+4,'right');}
  for(let j=0;j<=4;j++){const t=S.tmax*j/4;txt(g,t.toFixed(0),X(t),y1+16);}
  frame(g,x0,y0,x1-x0,y1-y0);
  g.strokeStyle='#888';g.setLineDash([5,4]);g.beginPath();g.moveTo(x0,Y(1));g.lineTo(x1,Y(1));g.stroke();g.setLineDash([]);
  g.save();g.beginPath();g.rect(x0,y0,x1-x0,y1-y0);g.clip();
  const st=$('frw-status').className.includes('ok');g.strokeStyle=st?'#333399':'#C00000';g.lineWidth=2;g.beginPath();
  ts.forEach((t,i)=>{i?g.lineTo(X(t),Y(ys[i])):g.moveTo(X(t),Y(ys[i]));});g.stroke();g.restore();
  txt(g,'time',(x0+x1)/2,H-6);txt(g,'closed-loop set-point step',(x0+x1)/2+10,28,'center','#555','13px system-ui');
}
let S;
function draw(){
  const k=S.kmax*(+$('frw-k').value)/1000;$('frw-kval').textContent=k.toFixed(3);
  const R=resp(S,k);const st=$('frw-status');
  if(R.gm>1.02){st.textContent='STABLE';st.className='frw-status ok';}
  else if(R.gm>0.98){st.textContent='MARGINAL';st.className='frw-status mar';}
  else{st.textContent='UNSTABLE';st.className='frw-status bad';}
  const f=v=>isFinite(v)?v.toFixed(3):'∞';
  $('frw-read').innerHTML=`<b class="g">GM = ${f(R.gm)}</b> (ω<sub>c</sub> = ${R.wc?R.wc.toFixed(3):'—'}) &nbsp;&nbsp; <b class="p">PM = ${isFinite(R.pm)?R.pm.toFixed(1)+'°':'∞'}</b> (ω<sub>g</sub> = ${R.wg?R.wg.toFixed(3):'—'}) &nbsp;&nbsp; K<sub>cu</sub> = K<sub>c</sub>·GM = ${isFinite(R.gm)?(k*R.gm).toFixed(3):'∞'}`;
  drawBode(R);drawNyq(R);drawStep(S,k);
}
function load(){S=SYS[$('frw-sys').value];$('frw-k').value=Math.round(1000*S.kdef/S.kmax);draw();}
$('frw-sys').addEventListener('change',load);$('frw-k').addEventListener('input',draw);
load();
})();
</script>
```
