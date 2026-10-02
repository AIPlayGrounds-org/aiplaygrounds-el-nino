<template>
  <div>
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </div>
</template>

<style>
/*
  Colores por rol. Cálido y frío son tonos sobrios a propósito: una anomalía no es un peligro,
  y el rojo de alarma queda reservado para las alertas oficiales cuando se muestren.
*/
:root {
  --bg: #f6f7f8;
  --surface: #ffffff;
  --inset: #f0f3f5;
  --text: #1b1f24;
  --muted: #545c66;
  --border: #dde2e7;
  --link: #1d5a9e;
  --focus: #1d5a9e;
  --warm: #9f4a1c;
  --cold: #255c8f;
  --neutral-data: #8a9099;
  --chart-grid: #e8ebee;
  --notice-bg: #fbf3e2;
  --notice-text: #5c4210;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111417;
    --surface: #191d22;
    --inset: #20252b;
    --text: #e7eaee;
    --muted: #a9b0ba;
    --border: #2d333b;
    --link: #8dbbec;
    --focus: #8dbbec;
    --warm: #f0a070;
    --cold: #8fbce8;
    --neutral-data: #8e959f;
    --chart-grid: #262c33;
    --notice-bg: #2e2717;
    --notice-text: #f1d9a6;
  }
}
html {
  -webkit-text-size-adjust: 100%;
}
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.4;
}
a {
  color: var(--link);
  text-underline-offset: 0.18em;
}
::selection {
  background: color-mix(in srgb, var(--link) 25%, transparent);
}
:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 3px;
  border-radius: 3px;
}
</style>
