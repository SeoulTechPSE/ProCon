```{=html}
<svg class="dchart" viewBox="0 0 1120 470" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Decision chart for choosing a stability-analysis technique">
  <defs>
    <marker id="dc-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#555"/>
    </marker>
    <filter id="dc-sh" x="-10%" y="-10%" width="130%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#333399" flood-opacity="0.18"/>
    </filter>
  </defs>
  <style>
    .dchart { width: 100%; height: auto; font-family: inherit; }
    .dchart text { font-family: inherit; fill: #222; }
    .dchart .lbl  { font-size: 21px; text-anchor: middle; dominant-baseline: middle; }
    .dchart .lblw { font-size: 21px; text-anchor: middle; dominant-baseline: middle; fill: #fff; font-weight: 600; }
    .dchart .yes  { font-size: 17px; fill: #2E7D32; font-weight: 700; }
    .dchart .no   { font-size: 17px; fill: #C00000; font-weight: 700; }
    .dchart .tag  { font-size: 16px; fill: #C00000; font-style: italic; }
    .dchart .edge { stroke: #555; stroke-width: 2; fill: none; marker-end: url(#dc-arr); }
    .dchart .box  { fill: #fff; stroke: #333399; stroke-width: 2; }
    .dchart .dec  { fill: #eef0fa; stroke: #333399; stroke-width: 2; }
    .dchart .meth { fill: #333399; stroke: none; }
    .dchart .out  { fill: #f4f4f4; stroke: #999; stroke-width: 1.6; stroke-dasharray: 6 4; }
  </style>

  <!-- edges (drawn first, under the nodes) -->
  <path class="edge" d="M160,100 L203,100"/>                       <!-- model -> linearize -->
  <path class="edge" d="M341,100 L384,100"/>                       <!-- linearize -> TF -->
  <path class="edge" d="M536,100 L579,100"/>                       <!-- TF -> dead time -->
  <path class="edge" d="M717,100 L760,100"/>                       <!-- dead time -> Routh -->
  <path class="edge" d="M912,100 L955,100"/>                       <!-- Routh -> root locus -->
  <path class="edge" d="M273,150 L273,255"/>                       <!-- linearize -> nonlinear -->
  <path class="edge" d="M649,150 L649,218"/>                       <!-- dead time -> Pade -->
  <path class="edge" d="M717,270 L837,270 L837,135"/>              <!-- Pade -> Routh -->
  <path class="edge" d="M649,320 L649,368"/>                       <!-- Pade -> s=jw -->

  <!-- edge labels -->
  <text class="yes" x="350" y="88">Yes</text>
  <text class="no"  x="283" y="200">No</text>
  <text class="no"  x="722" y="88">No</text>
  <text class="yes" x="659" y="190">Yes</text>
  <text class="yes" x="733" y="258">Yes</text>
  <text class="no"  x="659" y="350">No</text>

  <!-- nodes -->
  <g filter="url(#dc-sh)">
    <rect class="box" x="10"  y="67" width="150" height="66" rx="10"/>
    <polygon class="dec" points="205,100 273,50 341,100 273,150"/>
    <rect class="box" x="386" y="67" width="150" height="66" rx="10"/>
    <polygon class="dec" points="581,100 649,50 717,100 649,150"/>
    <rect class="meth" x="762" y="67" width="150" height="66" rx="10"/>
    <rect class="meth" x="957" y="67" width="150" height="66" rx="10"/>
    <rect class="out"  x="173" y="257" width="200" height="66" rx="10"/>
    <polygon class="dec" points="581,270 649,220 717,270 649,320"/>
    <rect class="meth" x="514" y="370" width="270" height="74" rx="10"/>
  </g>

  <text class="lbl" x="85"  y="88">Nonlinear</text>
  <text class="lbl" x="85"  y="113">process model</text>
  <text class="lbl" x="273" y="101">Linearize?</text>
  <text class="lbl" x="461" y="88">Transfer-</text>
  <text class="lbl" x="461" y="113">function model</text>
  <text class="lbl" x="649" y="89">Dead</text>
  <text class="lbl" x="649" y="112">time?</text>
  <text class="lblw" x="837" y="101">Routh array</text>
  <text class="lblw" x="1032" y="101">Root locus</text>
  <text class="lbl" x="273" y="279" style="fill:#666">Nonlinear tests</text>
  <text class="lbl" x="273" y="304" style="fill:#666;font-size:17px">(Lyapunov, Khalil 2001)</text>
  <text class="lbl" x="649" y="261">Padé</text>
  <text class="lbl" x="649" y="284">approx.?</text>
  <text class="lblw" x="649" y="394">Direct substitution s = jω</text>
  <text class="lblw" x="649" y="421" style="font-size:17px;font-weight:400">or frequency response (Ch. 5)</text>

  <!-- where each example sits -->
  <text class="tag" x="837"  y="50" text-anchor="middle">Ex 4.2, 4.3</text>
  <text class="tag" x="1032" y="50" text-anchor="middle">Ex 4.2B, 4.3B, 4.6–4.8</text>
  <text class="tag" x="795"  y="412">Ex 4.2A, 4.3A, 4.4</text>
  <text class="tag" x="733"  y="296">Ex 4.4 (Padé, with error)</text>
  <text class="lbl" x="1032" y="150" style="font-size:16px;fill:#333399">pole locations →</text>
  <text class="lbl" x="1032" y="171" style="font-size:16px;fill:#333399">dynamics &amp; design</text>
</svg>
```
