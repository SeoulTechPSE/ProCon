```{=html}
<div id="rgw" class="rgw">
  <div class="rgw-ctrl">
    <label><i>m</i><sub>1</sub> (pure A) = <b id="rgw-m1v"></b> g/s <input id="rgw-m1" type="range" min="-1" max="1.3" step="0.01" value="-1"></label>
    <label><i>m</i><sub>2</sub> (solvent) = <b id="rgw-m2v"></b> g/s <input id="rgw-m2" type="range" min="-1" max="1.3" step="0.01" value="1"></label>
  </div>
  <div class="rgw-out" id="rgw-out"></div>
</div>
<style>
.rgw{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;font-size:17px;color:#222;border:1px solid #ddd;border-radius:6px;padding:8px 12px;background:#fff}
.rgw-ctrl{display:flex;flex-wrap:wrap;gap:22px}
.rgw-ctrl input{width:200px;vertical-align:middle}
.rgw-out{display:flex;gap:28px;align-items:center;margin-top:6px;flex-wrap:wrap}
.rgw table{border-collapse:collapse;font-family:ui-monospace,Menlo,monospace;font-size:16px}
.rgw td,.rgw th{padding:3px 10px;text-align:right}
.rgw th{color:#333399;font-weight:600}
.rgw td.pick{background:#e6f2e8;color:#2E7D32;font-weight:700;border-radius:4px}
.rgw .pair{font-weight:600;color:#2E7D32}
</style>
<script>
(function(){
const $=id=>document.getElementById(id);
function upd(){
  const m1=10**(+$('rgw-m1').value),m2=10**(+$('rgw-m2').value),F=m1+m2,x=m1/F;
  $('rgw-m1v').textContent=m1.toFixed(2);$('rgw-m2v').textContent=m2.toFixed(2);
  const K=[[m2/F/F,-m1/F/F],[1,1]];const l=1-x;
  const diag=l>=0.5;
  const c=(v,p)=>`<td class="${p?'pick':''}">${v.toFixed(4)}</td>`;
  const e=v=>Math.abs(v)<1e-3||Math.abs(v)>=1e3?v.toExponential(2):v.toFixed(4);
  $('rgw-out').innerHTML=
   `<div><i>x</i> = ${x.toFixed(4)}, &nbsp;<i>F</i> = ${F.toFixed(2)} g/s</div>`+
   `<table><tr><th>K</th><th>m<sub>1</sub></th><th>m<sub>2</sub></th></tr>`+
   `<tr><th>x</th><td>${e(K[0][0])}</td><td>${e(K[0][1])}</td></tr><tr><th>F</th><td>1</td><td>1</td></tr></table>`+
   `<table><tr><th>Λ</th><th>m<sub>1</sub></th><th>m<sub>2</sub></th></tr>`+
   `<tr><th>x</th>${c(l,diag)}${c(x,!diag)}</tr><tr><th>F</th>${c(x,!diag)}${c(l,diag)}</tr></table>`+
   `<div class="pair">pair: ${diag?'x – m<sub>1</sub>, F – m<sub>2</sub>':'x – m<sub>2</sub>, F – m<sub>1</sub>'}${Math.abs(l-0.5)<0.1?' <span style="color:#C00000">(λ ≈ 0.5: strong interaction either way)</span>':''}</div>`;
}
['rgw-m1','rgw-m2'].forEach(id=>$(id).addEventListener('input',upd));upd();
})();
</script>
```
