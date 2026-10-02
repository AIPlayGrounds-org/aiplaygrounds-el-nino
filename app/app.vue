<script setup lang="ts">
// Serif de lectura con eje de tamaño óptico: fina para leer, pesada y apretada para el titular.
// Letra manuscrita solo para anotar los gráficos, como una nota al margen.
import '@fontsource-variable/source-serif-4/opsz.css'
import '@fontsource-variable/source-serif-4/opsz-italic.css'
import '@fontsource/patrick-hand/latin.css'
import '@fontsource/patrick-hand/latin-ext.css'
</script>

<template>
  <div>
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
    --notice-bg: #33280f;
    --notice-text: #f4dca5;
  }
}
html {
  -webkit-text-size-adjust: 100%;
}
body {
  margin: 0;
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
:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 3px;
}
</style>
