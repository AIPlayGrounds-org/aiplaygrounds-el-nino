<script setup lang="ts">
import { messages } from '~/messages'
// Serif de lectura con eje de tamaño óptico: fina para leer, pesada y apretada para el titular.
// Letra manuscrita solo para anotar los gráficos, como una nota al margen.
import '@fontsource-variable/source-serif-4/opsz.css'
import '@fontsource-variable/source-serif-4/opsz-italic.css'
import '@fontsource/patrick-hand/latin.css'
import '@fontsource/patrick-hand/latin-ext.css'
</script>

<template>
  <div>
    <a class="skip-link" href="#main-content">{{ messages.page.skipLink }}</a>
    <NuxtRouteAnnouncer />
    <NuxtPage />
  </div>
</template>

<style>
/*
  Mundo visual: un ensayo visual con scroll.
  Papel blanco y tinta casi negra para leer. El mar tiene su color: petróleo profundo en la portada
  y el pie, verde agua claro en el mapa y en el rango normal; la costa, en arena.
  Un único realce cálido para El Niño y uno frío para La Niña, solo en datos.
  No hay rojo de alarma: una anomalía no es un peligro.
*/
:root {
  --paper: #ffffff;
  --text: #262626;
  --muted: #5e5e5e;
  --faint: #8c8c8c;
  --border: #e2e2e2;
  --land: #e6d8bb;
  --band: #e3f0ee;
  /* El mar: verde agua claro (mapa, rango normal) y petróleo profundo (portada y pie). */
  --sea: #e3f0ee;
  --sea-edge: #a9cdc8;
  --sand: #f5eddd;
  --deep: #0f3d46;
  --on-deep: #eef6f5;
  --on-deep-muted: #b2cfcc;
  --warm-on-deep: #ffa46d;
  --neutral-data: #a6a6a6;
  --warm: #d4581b;
  --warm-text: #ae4613;
  --warm-tint: #fbe9df;
  --cold: #2f6db3;
  --cold-text: #2a62a2;
  --accent: #17676b;
  --link: var(--accent);
  --focus: var(--accent);
  --chart-grid: #ececec;
  /* Rampa divergente del pronóstico: frío fuerte (1) a cálido fuerte (9), neutral en el centro (5). Cada paso tiene al menos 3:1 sobre el fondo. */
  --ramp-1: #0a3a78;
  --ramp-2: #1d5ba5;
  --ramp-3: #3a7dbf;
  --ramp-4: #5c92c8;
  --ramp-5: #8a8a8a;
  --ramp-6: #c9783c;
  --ramp-7: #b9622a;
  --ramp-8: #9c4818;
  --ramp-9: #6e300b;
  --notice-bg: #fff3d6;
  --notice-text: #5a3d07;
  /* Usados por los gráficos, que leen estas variables. */
  --bg: var(--paper);
  --surface: var(--paper);
  --fs-small: 0.875rem;
  --font: 'Source Serif 4 Variable', Georgia, 'Times New Roman', serif;
  --hand: 'Patrick Hand', 'Comic Sans MS', cursive;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #131313;
    --text: #ececec;
    --muted: #ababab;
    --faint: #7c7c7c;
    --border: #2d2d2d;
    --land: #3a3324;
    --band: #142a2d;
    --sea: #112629;
    --sea-edge: #2b555a;
    --sand: #1e1a13;
    --deep: #0a2a31;
    --on-deep: #e6f0ef;
    --on-deep-muted: #9fbfbc;
    --warm-on-deep: #f7a06a;
    --accent: #7cc9c7;
    --neutral-data: #707070;
    --warm: #f08a4b;
    --warm-text: #f59a62;
    --warm-tint: #3a2215;
    --cold: #74aaeb;
    --cold-text: #8ab8ee;
    --chart-grid: #232323;
    --ramp-1: #7db8ff;
    --ramp-2: #6ea3ea;
    --ramp-3: #6190d0;
    --ramp-4: #5683bd;
    --ramp-5: #777777;
    --ramp-6: #b9835f;
    --ramp-7: #d9894f;
    --ramp-8: #f09050;
    --ramp-9: #ffa468;
    --notice-bg: #33280f;
    --notice-text: #f4dca5;
  }
}
html {
  -webkit-text-size-adjust: 100%;
  overflow-x: clip;
}
body {
  margin: 0;
  overflow-x: clip;
  background: var(--paper);
  color: var(--text);
  font-family: var(--font);
  font-size: 1.125rem;
  font-optical-sizing: auto;
  line-height: 1.6;
}
a {
  color: var(--link);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.2em;
  text-decoration-color: color-mix(in srgb, currentColor 45%, transparent);
}
a:hover {
  text-decoration-color: currentColor;
  text-decoration-thickness: 2px;
}
::selection {
  background: color-mix(in srgb, var(--text) 16%, transparent);
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
:where(button, select, summary, a:not(.sr-only)) {
  min-height: 44px;
}
a:not(.sr-only) {
  display: inline-flex;
  align-items: center;
  padding-inline: 4px;
  margin-inline: -4px;
}
summary {
  align-items: center;
}
.skip-link {
  position: fixed;
  z-index: 10;
  top: 8px;
  left: 8px;
  padding: 8px 12px;
  transform: translateY(-150%);
  background: var(--text);
  color: var(--paper);
  text-decoration: none;
}
.skip-link:focus-visible {
  transform: translateY(0);
}
:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 3px;
}
</style>
