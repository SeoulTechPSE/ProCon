```{=html}
<svg class="dchart" viewBox="0 0 1120 440" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Decision chart for choosing a frequency-domain stability test">
  <defs>
    <marker id="dc5-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#555"/>
    </marker>
    <filter id="dc5-sh" x="-10%" y="-10%" width="130%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#333399" flood-opacity="0.18"/>
    </filter>
  </defs>
  <style>
    .dchart { width: 100%; height: auto; font-family: inherit; }
    .dchart text { font-family: inherit; fill: #222; }
    .dchart .lbl  { font-size: 21px; text-anchor: middle; dominant-baseline: middle; }
    .dchart .lblw { font-size: 21px; text-anchor: middle; dominant-baseline: middle; fill: #fff; font-weight: 600; }
    .dchart .sub  { font-size: 17px; text-anchor: middle; dominant-baseline: middle; fill: #fff; font-weight: 400; }
    .dchart .yes  { font-size: 17px; fill: #2E7D32; font-weight: 700; }
    .dchart .no   { font-size: 17px; fill: #C00000; font-weight: 700; }
    .dchart .tag  { font-size: 16px; fill: #C00000; font-style: italic; }
    .dchart .note { font-size: 16px; fill: #333399; }
    .dchart .edge { stroke: #555; stroke-width: 2; fill: none; marker-end: url(#dc5-arr); }
    .dchart .box  { fill: #fff; stroke: #333399; stroke-width: 2; }
    .dchart .dec  { fill: #eef0fa; stroke: #333399; stroke-width: 2; }
    .dchart .meth { fill: #333399; stroke: none; }
  </style>

  <!-- edges -->
  <path class="edge" d="M160,100 L203,100"/>                    <!-- G_OL -> OL stable? -->
  <path class="edge" d="M375,100 L438,100"/>                    <!-- OL stable -> single crossing -->
  <path class="edge" d="M630,100 L673,100"/>                    <!-- single crossing -> Bode -->
  <path class="edge" d="M855,100 L898,100"/>                    <!-- Bode -> margins -->
  <path class="edge" d="M290,150 L290,266"/>                    <!-- OL stable (No) -> Nyquist -->
  <path class="edge" d="M535,150 L535,266"/>                    <!-- single crossing (No) -> Nyquist -->
  <path class="edge" d="M630,306 L1000,306 L1000,135"/>         <!-- Nyquist -> margins -->

  <!-- edge labels -->
  <text class="yes" x="388" y="88">Yes</text>
  <text class="yes" x="633" y="88">Yes</text>
  <text class="no"  x="300" y="212">No</text>
  <text class="no"  x="545" y="212">No</text>
  <text class="note" x="815" y="296" text-anchor="middle">GM, PM = distance of the curve from −1</text>

  <!-- nodes -->
  <g filter="url(#dc5-sh)">
    <rect class="box" x="10" y="67" width="150" height="66" rx="10"/>
    <polygon class="dec" points="205,100 290,50 375,100 290,150"/>
    <polygon class="dec" points="440,100 535,50 630,100 535,150"/>
    <rect class="meth" x="675" y="64" width="180" height="72" rx="10"/>
    <rect class="meth" x="900" y="64" width="200" height="72" rx="10"/>
    <rect class="meth" x="240" y="268" width="390" height="76" rx="10"/>
  </g>

  <text class="lbl" x="85"  y="88">Open loop</text>
  <text class="lbl" x="85"  y="113">G<tspan baseline-shift="sub" font-size="15">OL</tspan>(jω)</text>
  <text class="lbl" x="290" y="89" style="font-size:19px">Open-loop</text>
  <text class="lbl" x="290" y="112" style="font-size:19px">stable?</text>
  <text class="lbl" x="535" y="89" style="font-size:19px">One −180°</text>
  <text class="lbl" x="535" y="112" style="font-size:19px">crossing?</text>
  <text class="lblw" x="765" y="88">Bode criterion</text>
  <text class="sub"  x="765" y="114">|G<tspan baseline-shift="sub" font-size="13">OL</tspan>(jω<tspan baseline-shift="sub" font-size="13">c</tspan>)| &lt; 1</text>
  <text class="lblw" x="1000" y="88">GM, PM</text>
  <text class="sub"  x="1000" y="114">→ choose K<tspan baseline-shift="sub" font-size="13">c</tspan></text>
  <text class="lblw" x="435" y="292">Nyquist criterion</text>
  <text class="sub"  x="435" y="320">Z = N + P = 0  (count encirclements of −1)</text>

  <!-- where each example sits -->
  <text class="tag" x="765"  y="46" text-anchor="middle">Ex 5.11, Ex 4.4 revisited</text>
  <text class="tag" x="1000" y="46" text-anchor="middle">Ex 5.12, 5.13</text>
  <text class="tag" x="435"  y="370" text-anchor="middle">Ex 5.14: open-loop unstable process</text>
  <text class="note" x="290" y="182" text-anchor="end" style="font-size:14px;fill:#666">P ≠ 0</text>
  <text class="note" x="525" y="182" text-anchor="end" style="font-size:14px;fill:#666">several ω<tspan baseline-shift="sub" font-size="11">c</tspan>, ω<tspan baseline-shift="sub" font-size="11">g</tspan></text>
  <text class="note" x="560" y="410" text-anchor="middle" style="fill:#666">(a single pole at the origin is allowed in “open-loop stable”)</text>
</svg>
```
