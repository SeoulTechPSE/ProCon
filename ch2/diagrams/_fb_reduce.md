```{=html}
<svg class="bdia" viewBox="0 0 1000 250" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Block-diagram algebra: feedback, series and parallel">
  <defs>
    <marker id="fb_reduce-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>
    <filter id="fb_reduce-sh" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#333399" flood-opacity="0.16"/></filter>
  </defs>
  <style>.bdia{width:100%;height:auto;font-family:inherit} .bdia text{font-family:inherit}</style>
  <text x="10" y="16" font-size="15" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(a) negative feedback</text>
  <text x="22" y="68" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">R</text>
  <circle cx="70" cy="90" r="13" fill="#fff" stroke="#222" stroke-width="2"/>
  <text x="48" y="79" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <text x="87" y="119" font-size="19" font-weight="700" text-anchor="middle" fill="#222">−</text>
  <rect x="145.0" y="66.0" width="80" height="48" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="185" y="90" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G</text>
  <path d="M6,90 L57,90" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <path d="M83,90 L145.0,90" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="110" y="70" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">E</text>
  <path d="M225.0,90 L310,90" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="296" y="68" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">Y</text>
  <circle cx="270" cy="90" r="4" fill="#222"/>
  <rect x="145.0" y="148.0" width="80" height="44" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="185" y="170" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">H</text>
  <path d="M270,90 L270,170 L225.0,170" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <path d="M145.0,170 L70,170 L70,103" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="350" y="90" font-size="30" fill="#333399" text-anchor="middle" font-weight="400" dominant-baseline="central">⇒</text>
  <path d="M380,90 L412,90" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <rect x="412.0" y="65.0" width="136" height="50" rx="8" fill="#eef0fa" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="480" y="90" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="21" fill="#222" text-anchor="middle" dominant-baseline="central">G / (1 + GH)</text>
  <path d="M548,90 L585,90" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="480" y="160" font-size="15" fill="#333399" text-anchor="middle" font-weight="600" dominant-baseline="central">forward path / (1 + loop)</text>
  <line x1="620" y1="10" x2="620" y2="240" stroke="#ddd" stroke-width="1.5"/>
  <text x="640" y="16" font-size="15" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(b) series</text>
  <path d="M640,62 L668,62" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <rect x="669.0" y="41.0" width="62" height="42" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="700" y="62" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">1</tspan><tspan dy="-0.32em">​</tspan></text>
  <path d="M731,62 L768,62" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <rect x="769.0" y="41.0" width="62" height="42" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="800" y="62" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">2</tspan><tspan dy="-0.32em">​</tspan></text>
  <path d="M831,62 L862,62" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="880" y="62" font-size="24" fill="#444" text-anchor="middle" font-weight="400" dominant-baseline="central">=</text>
  <text x="940" y="62" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#333399" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">1</tspan><tspan dy="-0.32em">​</tspan>G<tspan dy="0.32em" font-size="72%">2</tspan><tspan dy="-0.32em">​</tspan></text>
  <text x="640" y="122" font-size="15" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(c) parallel</text>
  <path d="M640,190 L660,190" fill="none" stroke="#555" stroke-width="2"/>
  <circle cx="660" cy="190" r="4" fill="#222"/>
  <path d="M660,190 L660,162 L712,162" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <path d="M660,190 L660,218 L712,218" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <rect x="712.0" y="143.0" width="60" height="38" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="742" y="162" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">1</tspan><tspan dy="-0.32em">​</tspan></text>
  <rect x="712.0" y="199.0" width="60" height="38" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#fb_reduce-sh)"/>
  <text x="742" y="218" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">2</tspan><tspan dy="-0.32em">​</tspan></text>
  <circle cx="820" cy="190" r="13" fill="#fff" stroke="#222" stroke-width="2"/>
  <text x="837" y="172" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <text x="837" y="219" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <path d="M772,162 L820,162 L820,177" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <path d="M772,218 L820,218 L820,203" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <path d="M833,190 L862,190" fill="none" stroke="#555" stroke-width="2" marker-end="url(#fb_reduce-arr)"/>
  <text x="880" y="190" font-size="24" fill="#444" text-anchor="middle" font-weight="400" dominant-baseline="central">=</text>
  <text x="940" y="190" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#333399" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">1</tspan><tspan dy="-0.32em">​</tspan> + G<tspan dy="0.32em" font-size="72%">2</tspan><tspan dy="-0.32em">​</tspan></text>
</svg>
```
