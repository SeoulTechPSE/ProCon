```{=html}
<div id="clw" class="clw">
  <div class="clw-ctrl">
    <label>process <select id="clw-p">
      <option value="0" selected>0.8/(5s+1)  — Ex 2.6</option>
      <option value="1">1/[(2s+1)(4s+1)]  — Ex 2.2</option>
      <option value="2">1/s  — Ex 2.5</option>
      <option value="3">1/(s+1)³</option></select></label>
    <label>mode <select id="clw-m"><option>P</option><option selected>PI</option><option>PD</option><option>PID</option></select></label>
    <label>input <select id="clw-i"><option value="sp" selected>set-point step</option><option value="ld">load step</option></select></label>
    <label><input type="checkbox" id="clw-dm"> D on measurement</label>
  </div>
  <div class="clw-ctrl">
    <label><i>K</i><sub>c</sub> = <b id="clw-kv"></b><input id="clw-k" type="range" min="0" max="20" step="0.05" value="10"></label>
    <label><i>τ</i><sub>I</sub> = <b id="clw-iv"></b><input id="clw-ti" type="range" min="0.1" max="20" step="0.05" value="1"></label>
    <label><i>τ</i><sub>D</sub> = <b id="clw-dv"></b><input id="clw-td" type="range" min="0" max="3" step="0.01" value="0.5"></label>
  </div>
  <div class="clw-body">
    <canvas id="clw-cv" width="820" height="430"></canvas>
    <div id="clw-info" class="clw-info"></div>
  </div>
</div>
<style>
.clw{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:19px;color:#222}
.clw-ctrl{display:flex;flex-wrap:wrap;gap:18px;align-items:center;margin-bottom:6px}
.clw-ctrl input[type=range]{width:170px;vertical-align:middle}
.clw select{font-size:17px}
.clw-body{display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}
.clw canvas{border:1px solid #ddd;border-radius:4px;max-width:100%;height:auto;background:#fff}
.clw-info{font-size:18px;line-height:1.5;min-width:250px;max-width:300px}
.clw-info b{color:#333399}
.clw-info .bad{color:#C00000;font-weight:700}
.clw-info .ok{color:#2E7D32;font-weight:700}
</style>
<script>
(function(){
const $=id=>document.getElementById(id);
// plants: gain, first-order lags, integrator, horizon
const P=[{K:0.8,lags:[5],int:false,T:12},{K:1,lags:[2,4],int:false,T:40},{K:1,lags:[],int:true,T:20},{K:1,lags:[1,1,1],int:false,T:30}];
function sim(pl,Kc,tI,tD,useI,useD,load,dmeas){
  const n=6000,dt=pl.T/n,a=0.1,x=pl.lags.map(()=>0);let xi=0,I=0,df=0,prev=0;
  const y=new Float64Array(n+1),u=new Float64Array(n+1);
  for(let k=0;k<=n;k++){
    const yk=pl.int?(pl.lags.length?x[x.length-1]:xi):x[x.length-1];
    const r=load?0:1,e=r-yk;
    if(useI)I+=e*dt;
    let D=0;if(useD&&tD>0){const sig=dmeas?-yk:e;df+=dt*(tD*(sig-prev)/dt-df)/(a*tD);prev=sig;D=df;}
    let uk=Kc*(e+(useI?I/tI:0)+D);uk=Math.max(-1e6,Math.min(1e6,uk));
    y[k]=yk;u[k]=uk;
    let w=pl.K*(uk+(load?1:0));
    if(pl.int){xi+=dt*w;w=xi;}
    for(let j=0;j<pl.lags.length;j++){x[j]+=dt*(w-x[j])/pl.lags[j];w=x[j];}
  }
  return{y,u,dt};
}
const cv=$('clw-cv'),g=cv.getContext('2d');
function axes(x0,x1,y0,y1,lo,hi,T,lab,ticks){
  g.strokeStyle='#999';g.lineWidth=1;g.strokeRect(x0,y0,x1-x0,y1-y0);
  g.font='15px system-ui';g.fillStyle='#555';g.textAlign='right';
  const Y=v=>y1-(v-lo)/(hi-lo)*(y1-y0);
  ticks.forEach(v=>{g.strokeStyle='#eee';g.beginPath();g.moveTo(x0+1,Y(v));g.lineTo(x1-1,Y(v));g.stroke();g.fillText(v.toFixed(1),x0-5,Y(v)+4);});
  g.save();g.translate(14,(y0+y1)/2);g.rotate(-Math.PI/2);g.textAlign='center';g.fillText(lab,0,0);g.restore();
  return Y;
}
function curve(arr,dt,X,Y,lo,hi,col,w,dash){
  g.save();g.beginPath();g.rect(X(0),Y(hi),X(1e9)-X(0),Y(lo)-Y(hi));g.clip();
  g.strokeStyle=col;g.lineWidth=w;g.setLineDash(dash||[]);g.beginPath();
  for(let k=0;k<arr.length;k+=3){const v=Math.max(lo-10,Math.min(hi+10,arr[k]));k?g.lineTo(X(k*dt),Y(v)):g.moveTo(X(k*dt),Y(v));}
  g.stroke();g.restore();
}
function draw(){
  const pl=P[+$('clw-p').value],m=$('clw-m').value,ld=$('clw-i').value==='ld',dm=$('clw-dm').checked;
  const Kc=+$('clw-k').value,tI=+$('clw-ti').value,tD=+$('clw-td').value,useI=m.includes('I'),useD=m.includes('D');
  $('clw-kv').textContent=Kc.toFixed(2);$('clw-iv').textContent=useI?tI.toFixed(2):'—';$('clw-dv').textContent=useD?tD.toFixed(2):'—';
  $('clw-ti').disabled=!useI;$('clw-td').disabled=!useD;$('clw-dm').disabled=!useD;
  const {y,u,dt}=sim(pl,Kc,tI,tD,useI,useD,ld,dm);
  const W=cv.width,H=cv.height,x0=56,x1=W-14;g.clearRect(0,0,W,H);
  const X=t=>x0+Math.min(t,pl.T)/pl.T*(x1-x0);
  const lo=ld?-0.6:-0.1,hi=ld?(pl.int?2:1.2):1.8;
  const Y=axes(x0,x1,10,260,lo,hi,pl.T,'C(t)',ld?[-0.5,0,0.5,1,1.5,2].filter(v=>v<=hi):[0,0.5,1,1.5]);
  g.setLineDash([5,4]);g.strokeStyle='#999';g.beginPath();g.moveTo(x0,Y(ld?0:1));g.lineTo(x1,Y(ld?0:1));g.stroke();g.setLineDash([]);
  curve(y,dt,X,Y,lo,hi,'#333399',2.4);
  let umax=0;for(let k=0;k<u.length;k++)umax=Math.max(umax,Math.abs(u[k]));
  const ur=Math.min(Math.max(2,Math.ceil(umax)),30),Yu=axes(x0,x1,290,390,-ur,ur,pl.T,'p(t)',[-ur,0,ur]);
  curve(u,dt,X,Yu,-ur,ur,'#C00000',1.8);
  g.fillStyle='#555';g.textAlign='center';g.font='15px system-ui';
  const st=[1,2,5,10].find(v=>pl.T/v<=8);for(let t=0;t<=pl.T+1e-9;t+=st)g.fillText(t,X(t),406);
  g.fillText('time',(x0+x1)/2,H-3);
  // diagnostics
  const n=y.length,yf=y[n-1],ref=ld?0:1;let tail=0,M=0;for(let k=Math.floor(n*0.85);k<n;k++)tail=Math.max(tail,Math.abs(y[k]-yf));
  for(let k=0;k<n;k++)M=Math.max(M,Math.abs(y[k]));
  let pk=-1e9;for(let k=0;k<n;k++)pk=Math.max(pk,y[k]);
  let s='';
  if(!isFinite(M)||M>50||tail>0.05*Math.max(1,Math.abs(yf))&&M>3) s+='<span class="bad">unstable / not settled</span><br>';
  else{
    s+=`final value <b>${yf.toFixed(3)}</b><br>offset <i>r</i> − <i>C</i>(∞) = <b>${(ref-yf).toFixed(3)}</b> `+(Math.abs(ref-yf)<0.01?'<span class="ok">none</span>':'')+'<br>';
    if(!ld){s+=`peak <b>${pk.toFixed(3)}</b>`+(pk>1.001?` (overshoot ${((pk-yf)/yf*100).toFixed(0)}%)`:'')+'<br>';}
    else s+=`peak deviation <b>${pk.toFixed(3)}</b><br>`;
    if(tail>0.01)s+='<span class="bad">still oscillating at the end</span><br>';
  }
  s+=`max |<i>p</i>| = <b>${umax.toFixed(2)}</b><br><span style="color:#777;font-size:14px">load enters at the process input (<i>G<sub>L</sub></i> = <i>G<sub>p</sub></i>); derivative filter α = 0.1</span>`;
  $('clw-info').innerHTML=s;
}
['clw-p','clw-m','clw-i','clw-dm','clw-k','clw-ti','clw-td'].forEach(id=>$(id).addEventListener('input',draw));
draw();
})();
</script>
```
