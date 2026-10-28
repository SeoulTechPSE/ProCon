```{=html}
<svg class="bdia" viewBox="0 0 1000 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Smith predictor">
  <defs>
    <marker id="smith-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>
    <filter id="smith-sh" x="-10%" y="-10%" width="130%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#333399" flood-opacity="0.16"/></filter>
  </defs>
  <style>.bdia{width:100%;height:auto;font-family:inherit} .bdia text{font-family:inherit}</style>
  <text x="20" y="18" font-size="16" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(a) feedback with dead time</text>
  <text x="20" y="48" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">R</text>
  <circle cx="70" cy="70" r="13" fill="#fff" stroke="#222" stroke-width="2"/>
  <text x="48" y="59" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <text x="87" y="99" font-size="19" font-weight="700" text-anchor="middle" fill="#222">−</text>
  <rect x="125.0" y="45.0" width="110" height="50" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="180" y="70" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">c</tspan><tspan dy="-0.32em">​</tspan>(s)</text>
  <rect x="285.0" y="45.0" width="150" height="50" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="360" y="70" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G(s)e<tspan dy="-0.45em" font-size="72%">−θs</tspan><tspan dy="0.45em">​</tspan></text>
  <path d="M6,70 L57,70" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M83,70 L125.0,70" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M235.0,70 L285.0,70" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M435.0,70 L520,70" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="508" y="48" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">Y</text>
  <circle cx="480" cy="70" r="4" fill="#222"/>
  <path d="M480,70 L480,118 L70,118 L70,83" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="560" y="70" font-size="16" fill="#333399" text-anchor="start" font-weight="400" dominant-baseline="central">1 + G<tspan dy="0.32em" font-size="72%">c</tspan><tspan dy="-0.32em">​</tspan>Ge<tspan dy="-0.45em" font-size="72%">−θs</tspan><tspan dy="0.45em">​</tspan> = 0: delay in the loop</text>
  <text x="20" y="160" font-size="16" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(b) Smith predictor (dead-time compensator)</text>
  <text x="20" y="278" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">R</text>
  <circle cx="70" cy="300" r="13" fill="#fff" stroke="#222" stroke-width="2"/>
  <text x="48" y="289" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <text x="87" y="282" font-size="19" font-weight="700" text-anchor="middle" fill="#222">−</text>
  <text x="87" y="329" font-size="19" font-weight="700" text-anchor="middle" fill="#222">−</text>
  <rect x="145.0" y="275.0" width="110" height="50" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="200" y="300" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">c</tspan><tspan dy="-0.32em">​</tspan>(s)</text>
  <rect x="345.0" y="275.0" width="150" height="50" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="420" y="300" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G(s)e<tspan dy="-0.45em" font-size="72%">−θs</tspan><tspan dy="0.45em">​</tspan></text>
  <rect x="135.0" y="185.0" width="210" height="50" rx="8" fill="#fff4f4" stroke="#C00000" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="240" y="210" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G(s)(1 − e<tspan dy="-0.45em" font-size="72%">−θs</tspan><tspan dy="0.45em">​</tspan>)</text>
  <path d="M6,300 L57,300" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M83,300 L145.0,300" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="110" y="280" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">E</text>
  <path d="M255.0,300 L345.0,300" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M495.0,300 L600,300" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="588" y="278" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">Y</text>
  <circle cx="300" cy="300" r="4" fill="#222"/>
  <circle cx="300" cy="300" r="4" fill="#222"/>
  <path d="M300,300 L300,248" fill="none" stroke="#555" stroke-width="2"/>
  <path d="M300,248 L390,248 L390,210 L345.0,210" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M135.0,210 L70,210 L70,287" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <circle cx="550" cy="300" r="4" fill="#222"/>
  <path d="M550,300 L550,360 L70,360 L70,313" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="625" y="160" font-size="16" fill="#C00000" text-anchor="start" font-weight="700" dominant-baseline="central">(c) equivalent loop</text>
  <text x="625" y="228" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">R</text>
  <circle cx="665" cy="250" r="13" fill="#fff" stroke="#222" stroke-width="2"/>
  <text x="643" y="239" font-size="19" font-weight="700" text-anchor="middle" fill="#222">+</text>
  <text x="682" y="279" font-size="19" font-weight="700" text-anchor="middle" fill="#222">−</text>
  <rect x="710.0" y="227.0" width="70" height="46" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="745" y="250" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G<tspan dy="0.32em" font-size="72%">c</tspan><tspan dy="-0.32em">​</tspan></text>
  <rect x="805.0" y="227.0" width="60" height="46" rx="8" fill="#fff" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="835" y="250" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">G</text>
  <rect x="890.0" y="227.0" width="80" height="46" rx="8" fill="#eef0fa" stroke="#333399" stroke-width="2" filter="url(#smith-sh)"/>
  <text x="930" y="250" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="24" fill="#222" text-anchor="middle" dominant-baseline="central">e<tspan dy="-0.45em" font-size="72%">−θs</tspan><tspan dy="0.45em">​</tspan></text>
  <path d="M613,250 L652,250" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M678,250 L710.0,250" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M780.0,250 L805.0,250" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M865.0,250 L890.0,250" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <path d="M970.0,250 L993,250" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="981" y="226" font-family="'Times New Roman', 'STIX Two Text', serif" font-style="italic" font-size="22" fill="#222" text-anchor="middle" dominant-baseline="central">Y</text>
  <circle cx="879" cy="250" r="4" fill="#222"/>
  <path d="M879,250 L879,300 L665,300 L665,263" fill="none" stroke="#555" stroke-width="2" marker-end="url(#smith-arr)"/>
  <text x="805" y="330" font-size="15" fill="#2E7D32" text-anchor="middle" font-weight="400" dominant-baseline="central">delay moved outside the loop</text>
  <text x="805" y="352" font-size="15" fill="#2E7D32" text-anchor="middle" font-weight="400" dominant-baseline="central">char. eq.  1 + G<tspan dy="0.32em" font-size="72%">c</tspan><tspan dy="-0.32em">​</tspan>G = 0</text>
</svg>
```
