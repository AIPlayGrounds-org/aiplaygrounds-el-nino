---
name: WawaPacha
description: Monitoreando el Fenómeno El Niño en el Perú. Un ensayo visual con scroll donde una pregunta se responde paso a paso, entre una portada y un pie de mar profundo.
colors:
  paper: "#ffffff"
  text: "#262626"
  muted: "#5e5e5e"
  faint: "#8c8c8c"
  border: "#e2e2e2"
  land: "#e6d8bb"
  band: "#e3f0ee"
  sea: "#e3f0ee"
  sea-edge: "#a9cdc8"
  sand: "#f5eddd"
  deep: "#0f3d46"
  on-deep: "#eef6f5"
  on-deep-muted: "#b2cfcc"
  warm-on-deep: "#ffa46d"
  accent: "#17676b"
  chart-grid: "#ececec"
  neutral-data: "#a6a6a6"
  warm: "#d4581b"
  warm-text: "#ae4613"
  warm-tint: "#fbe9df"
  cold: "#2f6db3"
  cold-text: "#2a62a2"
  notice-bg: "#fff3d6"
  notice-text: "#5a3d07"
  paper-dark: "#131313"
  text-dark: "#ececec"
  muted-dark: "#ababab"
  faint-dark: "#7c7c7c"
  border-dark: "#2d2d2d"
  land-dark: "#3a3324"
  band-dark: "#142a2d"
  sea-dark: "#112629"
  sea-edge-dark: "#2b555a"
  sand-dark: "#1e1a13"
  deep-dark: "#0a2a31"
  on-deep-dark: "#e6f0ef"
  on-deep-muted-dark: "#9fbfbc"
  warm-on-deep-dark: "#f7a06a"
  accent-dark: "#7cc9c7"
  chart-grid-dark: "#232323"
  neutral-data-dark: "#707070"
  warm-dark: "#f08a4b"
  warm-text-dark: "#f59a62"
  warm-tint-dark: "#3a2215"
  cold-dark: "#74aaeb"
  cold-text-dark: "#8ab8ee"
  notice-bg-dark: "#33280f"
  notice-text-dark: "#f4dca5"
typography:
  display:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "clamp(3.25rem, 13vw, 6rem)"
    fontWeight: 900
    lineHeight: 0.92
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "clamp(1.6rem, 4vw, 2.2rem)"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  lede:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "clamp(1.2rem, 2.6vw, 1.4rem)"
    fontWeight: 400
    lineHeight: 1.45
  step:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "1.1875rem"
    fontWeight: 400
    lineHeight: 1.55
  body:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "0.875rem"
    fontWeight: 400
  data-label:
    fontFamily: "'Source Serif 4 Variable', Georgia, 'Times New Roman', serif"
    fontSize: "clamp(17px, 4.5vw, 24px)"
    fontWeight: 800
    fontFeature: "'tnum' 1"
  hand:
    fontFamily: "'Patrick Hand', 'Comic Sans MS', cursive"
    fontSize: "19px"
    fontWeight: 400
  wordmark:
    fontFamily: "'Patrick Hand', 'Comic Sans MS', cursive"
    fontSize: "1.5rem"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "0.02em"
rounded:
  none: "0"
  pill: "999px"
spacing:
  gutter: "16px"
  story-gap: "48px"
  reading-column: "38rem"
  step-card: "18px 20px"
  section: "clamp(64px, 10vw, 112px)"
components:
  button-range:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "36px"
  button-range-pressed:
    backgroundColor: "{colors.text}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "36px"
  step-card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.text}"
    rounded: "{rounded.none}"
    padding: "{spacing.step-card}"
    typography: "{typography.step}"
  notice:
    backgroundColor: "{colors.notice-bg}"
    textColor: "{colors.notice-text}"
    rounded: "{rounded.none}"
    padding: "12px 16px"
  link:
    textColor: "{colors.accent}"
  cover:
    backgroundColor: "{colors.deep}"
    textColor: "{colors.on-deep}"
  sand-section:
    backgroundColor: "{colors.sand}"
    textColor: "{colors.text}"
---

# Design System: WawaPacha

## Overview

**Creative North Star: "Ensayo visual con scroll"**

La página es un ensayo visual al estilo The Pudding: una pregunta enorme («¿Llegó El Niño?») que se responde paso a paso mientras un gráfico fijo cambia de escena con cada párrafo. El lector no consulta un panel; lee una historia corta cuyos números salen de la serie de datos y se actualizan solos cada mes. Después de la historia, la página se vuelve una columna de lectura (qué significa para el Perú, explora tú mismo, cómo lo hicimos).

El material es papel blanco y tinta casi negra para leer, y el color del propio paisaje para dar atmósfera: la página abre y cierra sobre un campo de mar profundo (petróleo), el mapa pinta el océano en verde agua claro y la costa en arena, y la sección del Perú se apoya sobre arena, como el desierto costero. El verde agua claro también es «lo normal» en los gráficos (el rango neutral). Los colores de fase siguen siendo solo de datos: un naranja cálido para El Niño y un azul para La Niña; las franjas de temperatura de la portada son esos mismos colores aplicados a toda la serie. El único color de interfaz es el petróleo de los enlaces y el foco. No hay rojo de alarma. La voz tipográfica es una serif de lectura, Source Serif 4, con un titular enorme y pesado; sobre los gráficos, notas manuscritas en Patrick Hand, como anotaciones al margen de un cuaderno.

El sistema rechaza el panel de indicadores, la página de ficha técnica, las tarjetas y las sombras. La única caja de texto es la tarjeta de paso en móvil, que existe porque el texto pasa por encima del gráfico.

**Key Characteristics:**
- Una pregunta, un gráfico fijo y pasos de texto que cambian la escena al hacer scroll.
- Portada y pie sobre `--deep` (petróleo), abiertos y cerrados por las franjas de temperatura de toda la serie.
- Papel blanco y tinta para leer; mar en `--sea`, costa en `--land`, sección del Perú en `--sand`.
- `--warm` y `--cold` solo en datos; `--accent` (petróleo) solo en enlaces y foco.
- Source Serif 4 para leer y titular (titular a 900, hasta 6rem); Patrick Hand solo para anotar.
- Plano: sin sombras, sin radios salvo las píldoras del selector de periodo.
- Claro y oscuro con los mismos roles, por `prefers-color-scheme`.

## Colors

Papel blanco, tinta casi negra y grises neutros para leer; una familia de mar (petróleo profundo, verde agua claro) y una de costa (arena) para dar atmósfera y lugar; dos realces de fase, cálido y frío, reservados a los datos. Los tokens viven en `web/app/app.vue` como propiedades personalizadas en `:root` y se redefinen bajo `@media (prefers-color-scheme: dark)`; los valores `-dark` del frontmatter son esa redefinición. El gráfico de ECharts lee las mismas variables y las relee al cambiar el tema; el SVG de la historia las usa directamente.

### Primary (solo datos)
- **Naranja Niño** (`--warm`): fase cálida (anomalía ≥ +0,5 °C). Tramo cálido de la línea, punto del último dato, círculos de la racha, casillas llenas del contador, línea «tan alto como hoy», muestra de la leyenda y trazo de la caja Niño 3.4.
- **Naranja Niño para texto** (`--warm-text`): la versión más oscura (más clara en oscuro) que cumple contraste como texto. Cifra en la respuesta del primer viewport y en los pasos, etiqueta del último dato, anotaciones manuscritas cálidas.
- **Velo Niño** (`--warm-tint`): relleno de la caja Niño 3.4 y realce detrás de la cifra cálida en la respuesta.

### Secondary (solo datos)
- **Azul Niña** (`--cold`): fase fría (≤ −0,5 °C). Mismos usos que `--warm` en la línea, el punto, la racha y la leyenda.
- **Naranja sobre el mar** (`--warm-on-deep`): la cifra cálida cuando está sobre `--deep` (la respuesta de la portada).

### Mar y costa (atmósfera)
- **Mar profundo** (`--deep`): fondo de la portada (cabecera, pregunta, respuesta) y del pie («Cómo lo hicimos»). Sobre él, texto `--on-deep` y secundarios `--on-deep-muted`; dentro de esas regiones se redefinen `--text`, `--muted`, `--link` y `--focus` para que los componentes funcionen sin código extra.
- **Verde agua** (`--sea`, igual a `--band`): el océano del mapa y el rango neutral de los dos gráficos. `--sea-edge` dibuja la línea de costa y el ecuador.
- **Arena** (`--sand`): fondo a sangre de «¿Y qué significa para el Perú?». **Costa** (`--land`): el continente en el mapa.
- **Petróleo** (`--accent` = `--link` = `--focus`): enlaces y anillo de foco. Es el único color de interfaz.
- **Franjas de temperatura** (`OniStripes`): cada trimestre de la serie es una franja coloreada por su anomalía en una escala divergente azul (−2,5) → gris verdoso (0) → naranja (+2,6). Es la única escala calculada en el componente (RGB interpolado) en lugar de leerse de una variable: es una escala de datos, no un rol.
- **Azul Niña para texto** (`--cold-text`): cifra fría en texto y anotaciones manuscritas frías.

### Neutral
- **Papel** (`--paper`): fondo de toda la página y del gráfico; trazo de separación alrededor del punto y de la etiqueta del último dato. Alias `--bg` y `--surface` (fondo del tooltip y de la etiqueta en ECharts).
- **Tinta** (`--text`): texto principal, flecha de distancia, guías de los picos, botón de periodo pulsado.
- **Gris de lectura** (`--muted`): firma, textos secundarios, «Cómo lo hicimos», rótulo «PERÚ», ejes y umbrales del gráfico de exploración, indicación para bajar.
- **Gris tenue** (`--faint`): umbrales discontinuos de la historia, borde de las casillas vacías del contador.
- **Regla** (`--border`): bordes de 1px de las tarjetas de paso, filas de tabla, borde superior de «Cómo lo hicimos», borde de los botones de periodo, línea del cero.
- **Rejilla** (`--chart-grid`): líneas de división de ambos gráficos.
- **Gris de dato neutral** (`--neutral-data`): la línea y el punto cuando el valor está en el rango neutral.
- **Aviso de antigüedad** (`--notice-bg` / `--notice-text`): solo para avisar que el dato o la revisión de la fuente es antiguo.

### Named Rules
**The Un Solo Acento Rule.** El único color de interfaz es el petróleo `--accent`, en enlaces y foco. Los botones son tinta y papel. Sobre `--deep`, los enlaces y el foco pasan a `--on-deep`.

**The Data Owns the Heat Rule.** `--warm`, `--cold`, `--neutral-data` y sus variantes `-text`, `-tint` y `-on-deep` colorean solo datos: la línea, los puntos, las cifras, las franjas, las anotaciones de umbral, la región donde se mide. Nunca un botón, un marco ni un fondo de sección.

**The El Mar Es Lo Normal Rule.** Lo normal se dice en el color del mar en calma: el rango neutral es `--band` (verde agua), el océano del mapa es `--sea`. El color de lugar (mar, arena, petróleo) da atmósfera y regiones; nunca codifica una fase.

**The Sin Rojo Rule.** No hay rojo de alarma. Una anomalía no es un peligro; las alertas son de ENFEN y SENAMHI.

## Typography

**Display Font:** Source Serif 4 Variable (con Georgia, 'Times New Roman', serif), con eje de tamaño óptico (`font-optical-sizing: auto`)
**Body Font:** Source Serif 4 Variable (variable `--font`)
**Annotation Font:** Patrick Hand (con 'Comic Sans MS', cursive), variable `--hand`

**Character:** Una serif de lectura que se aprieta y se vuelve negrísima en el titular y se abre para leer; al lado, una letra manuscrita que anota los gráficos como un lápiz al margen. Ambas autoalojadas con `@fontsource`.

### Hierarchy
- **Display** (900, `clamp(3.25rem, 13vw, 6rem)`, 0.92, −0.03em, máximo 11ch, `text-wrap: balance`): la pregunta del primer viewport, centrada. Una por página.
- **Headline** (800, `clamp(1.6rem, 4vw, 2.2rem)`, 1.1, −0.02em): `h2` de las secciones tras la historia; en «Cómo lo hicimos» baja a 1.4rem.
- **Lede** (400, `clamp(1.2rem, 2.6vw, 1.4rem)`, 1.45, máximo 30rem): la respuesta corta. La primera frase va en bloque a 700; la cifra a 800 con cifras tabulares, en `--warm-text` sobre `--warm-tint` (o `--cold-text`).
- **Step** (400, 1.1875rem en escritorio, 1.125rem en móvil, 1.55): los párrafos de la historia; su énfasis `strong` a 650.
- **Body** (400, 1.125rem, 1.6): columna de lectura. «Cómo lo hicimos» baja a 1rem en `--muted`; el punto clave sube a 1.25rem / 1.45.
- **Label** (400, 0.875rem = `--fs-small`): leyenda, pie del gráfico, cabeceras de tabla (600), `dt` de metadatos.
- **Data label** (800, `clamp(17px, 4.5vw, 24px)`, cifras tabulares): la etiqueta del último dato en la historia, en el color de su fase, con un trazo de papel de 5px detrás.
- **Hand** (Patrick Hand, 19px; 21px para la ecuación de la anomalía; 16px para la subida en ≤559px): anotaciones sobre los gráficos.
- **Wordmark** (Patrick Hand, 1.5rem, 0.02em): WawaPacha centrado arriba. La indicación «Baja para entenderlo» y la firma final usan Patrick Hand a 1.25rem.
- **Rótulo de país** (650, 13px, mayúsculas, 0.12em, `--muted`): «PERÚ» en el mapa.
- **Ejes** (13px, cifras tabulares, `--muted`), con signo menos tipográfico (−).

### Named Rules
**The Mano Solo Anota Rule.** Patrick Hand solo aparece en anotaciones de los gráficos, el wordmark, la indicación para bajar, el contador «3 de 5» y la firma final. Nunca en un párrafo, un título ni un botón.

**The Titular Pesado Rule.** El titular es la única pieza a 900 y la única que llega a 6rem. Ningún otro texto compite con él.

**The Number Lives in the Sentence Rule.** La cifra va dentro de una frase en palabras, con cifras tabulares y el color de su fase; nunca como un indicador suelto en una caja.

## Layout

Una sola columna centrada de principio a fin, con 16px de margen lateral, salvo la historia en escritorio.

- **Primer viewport:** sobre `--deep` a sangre; el bloque ocupa `calc(100svh - 150px)` para que las franjas de temperatura (40px, con «1950» y «2026» a mano encima) cierren la portada dentro de la primera pantalla; centrado en ambos ejes y con texto centrado: pregunta, respuesta, firma en cursiva, aviso si lo hay y la indicación para bajar (48px por encima).
- **Historia (escritorio, ≥960px):** dos columnas, pasos de 300–380px a la izquierda y gráfico fijo (`position: sticky`, 100vh / 100svh) a la derecha, separados 48px, en un contenedor de 1280px con 32px de relleno. Pasos con 40vh de relleno arriba y 50vh abajo, 70vh entre pasos. La línea de lectura está al 55% de la altura de la ventana; el paso activo va a opacidad 1 y los demás a 0.3.
- **Historia (móvil, <960px):** el gráfico fijo ocupa toda la altura, pero se dibuja en el ~58% superior (el margen inferior del dibujo es el 42% de la altura); los pasos pasan por la franja inferior como tarjetas, con 70vh antes del primero y 75vh entre ellos. La línea de lectura está al 78% de la altura de la ventana; los pasos inactivos van a 0.55. En pantallas estrechas el mapa se acerca al Perú y Niño 3.4 sale por el borde oeste.
- **Columna de lectura:** máximo 38rem, para «¿Y qué significa para el Perú?», el texto de «Explora tú mismo», la tabla y «Cómo lo hicimos».
- **Gráfico de exploración:** máximo 960px; 360px de alto (300px a ≤599px); el marcador de posición reserva 410px / 360px para que la página no salte.
- **Ritmo:** `clamp(64px, 10vw, 112px)` antes de «Explora», `clamp(72px, 10vw, 120px)` antes de «Cómo lo hicimos»; 16px bajo cada `h2`, 18px entre párrafos, 24px antes de cada `<details>`. Metadatos en rejilla `auto-fit` de 150px mínimo; el detalle técnico a dos columnas (12rem / resto) desde 560px.

- **Regiones de color a sangre:** portada (`--deep`), «¿Y qué significa para el Perú?» (`--sand`, relleno `clamp(48px, 8vw, 88px)` arriba y `clamp(40px, 7vw, 72px)` abajo) y pie (`--deep`, abierto por franjas de 14px sin años). El texto dentro sigue en la columna de 38rem.

**The Una Columna Rule.** Fuera de la historia, todo es una columna de lectura de 38rem; las secciones se separan por espacio y por regiones de color a sangre, no por cajas. No hay rejillas de tarjetas.

## Elevation & Depth

Plano. No hay `box-shadow` de elevación en ningún elemento. La profundidad la dan la superposición del texto sobre el gráfico fijo (en móvil, tarjetas de papel al 94% con borde de 1px) y la opacidad de los pasos inactivos. El único `box-shadow` del código dibuja la banda gris detrás de la muestra neutral de la leyenda; no es elevación.

### Named Rules
**The Papel Plano Rule.** Sin sombras, sin desenfoques, sin capas flotantes. Lo que debe destacar se dice con tinta, peso o color de dato.

## Shapes

Esquinas rectas en todo (radio 0): tarjetas de paso, aviso, casillas del contador (22px, borde de 2px), caja Niño 3.4. Las únicas formas redondas son funcionales: los puntos de datos (9px en la escena inicial, 6px después; 7px de radio para la racha; 3.5px para los trimestres «tan alto como hoy») y las píldoras del selector de periodo (999px), el único control redondeado.

Las líneas hablan por su trazo: la serie a 1.75px en gris y 2.25px en los tramos de fase; umbrales discontinuos `4 4`; ecuador `3 5`; flecha de distancia discontinua `5 4` con punta en ambos extremos; línea «tan alto como hoy» punteada `2 4`.

## Components

### Buttons (selector de periodo)
Píldoras discretas; la elegida, en tinta.
- **Forma:** píldora (999px), borde de 1px `--border`, alto mínimo 36px (44px con puntero grueso), relleno 0 16px (0 18px táctil), 0.9375rem, separadas 6px.
- **Reposo:** fondo `--paper`, texto `--text`.
- **Hover:** el borde pasa a `--text`, transición de 0.15s `ease-out`.
- **Pulsado** (`aria-pressed="true"`): fondo y borde `--text`, texto `--paper`, peso 650.
- **Foco:** anillo global de 2px `--focus` separado 3px.
- Grupo con `role="group"`; opciones «10 años / 30 años / Todo». En pantallas ≤599px empieza en 10 años.

### Tarjeta de paso (solo móvil)
La única caja de texto del sistema, y solo porque el texto pasa sobre el gráfico. Fondo `--paper` al 94% (`color-mix`), borde de 1px `--border`, relleno 18px 20px, esquinas rectas. En escritorio desaparece: el párrafo va sin fondo ni borde. Cambio de opacidad en 0.3s `ease-out`.

### Links
Petróleo (`--link` = `--accent`; `--on-deep` sobre el mar profundo) con subrayado de 1px al 45% del color del enlace, separado 0.2em. Al pasar el ratón el subrayado toma el color pleno y engrosa a 2px. Los externos abren en pestaña nueva y lo anuncian con texto solo para lectores de pantalla. Las listas de enlaces van a peso 600 sin viñetas.

### Notice (aviso de antigüedad)
Fondo `--notice-bg`, texto `--notice-text`, relleno 12px 16px, 1rem, esquinas rectas, sin borde, `role="status"`. Solo aparece cuando el dato tiene ≥3 meses o la revisión de la fuente ≥40 días.

### Navigation (cabecera)
Solo el wordmark WawaPacha en Patrick Hand, centrado sobre la portada de mar profundo, con 18px de relleno superior. No hay menú ni regla.

### OniStripes (franjas de temperatura)
Un SVG a todo el ancho con una franja por trimestre, coloreada por su anomalía (ver Colors). Decorativo (`aria-hidden`): la historia y la tabla dan los datos. 40px con los años extremos a mano al pie de la portada; 14px sin años al inicio del pie.

### OniStory (componente distintivo)
La historia con scroll: un SVG fijo con dos escenas (mapa y gráfico) que se funden en 0.6s `ease-out`, y diez pasos de texto.
- **Escena del mapa:** océano `--sea`, tierra `--land` con costa de 1.5px `--sea-edge`, ecuador discontinuo en `--sea-edge`, caja Niño 3.4 en `--warm-tint` con trazo de 2.5 `--warm`, flecha de distancia en tinta y anotaciones manuscritas.
- **Escena del gráfico:** banda neutral, umbrales, serie gris con tramos de fase recortados por los umbrales, punto del último dato con borde de papel y etiqueta de dato; anotaciones manuscritas que aparecen por paso (umbrales, subida del último año, racha, picos, «tan alto como hoy») y un contador de cinco casillas cuadradas con «3 de 5» a mano.
- **Movimiento:** al cambiar de paso, el dominio del gráfico se interpola en 1.1s con salida cuártica (`1 − (1 − k)⁴`); bajo `prefers-reduced-motion: reduce` el cambio es instantáneo y las transiciones de opacidad se quitan.
- **Texto:** cada número del texto sale de la serie (último valor, racha, picos, porcentaje, subida); la única cifra fija es `DISTANCE_KM` («más de 4000 km»), documentada en el código.

### OniChart (explora tú mismo)
Gráfico de línea de ECharts teñido con los tokens: línea de 1.5px coloreada por fase con los umbrales oficiales (±0,5 °C), rango neutral sombreado en `--band`, umbrales discontinuos `--muted` con etiqueta de un decimal, rejilla `--chart-grid`, ejes en `--muted` con signo menos tipográfico. El último dato es un punto de 9px con borde de 2px de papel y una etiqueta a la derecha en su color de fase. Leyenda HTML debajo con muestras de 16 × 3px. Debajo, una tabla de los últimos 12 trimestres dentro de un `<details>`.

### Disclosure (`<details>`)
`<summary>` a 650, ancho ajustado al texto, con el marcador del navegador. Contiene la tabla alternativa y el detalle técnico.

### Data table
0.95rem, filas con regla inferior de 1px `--border`, celdas `8px 14px 8px 0`, cabecera en `--muted` 600 a `--fs-small`, números alineados a la derecha con cifras tabulares, desplazamiento horizontal con barra fina.

## Do's and Don'ts

### Do:
- **Do** contar con una pregunta y pasos: un gráfico fijo que cambia de escena por paso, con el paso activo a opacidad 1 y los demás a 0.3 (escritorio) o 0.55 (móvil).
- **Do** generar cada número del texto a partir de la serie; si una cifra debe ser fija, nómbrala como constante y documenta de dónde sale, como `DISTANCE_KM`.
- **Do** reservar `--warm`, `--cold`, `--neutral-data` y sus variantes `-text` y `-tint` para datos, con los umbrales oficiales (±0,5 °C) como corte; usar `--warm-text` y `--cold-text` cuando el dato es texto.
- **Do** decir lo normal con el mar en calma: `--band` para el rango neutral, `--sea` para el océano, `--land` para la costa, `--faint` para umbrales y guías.
- **Do** abrir y cerrar la página sobre `--deep`, y redefinir dentro de esa región `--text`, `--muted`, `--link` y `--focus` en vez de colorear componente por componente.
- **Do** escribir enlaces en petróleo `--accent`, con el foco del mismo color.
- **Do** usar Patrick Hand solo para anotar gráficos, el wordmark, la indicación para bajar y la firma.
- **Do** interpolar los cambios de escena (1.1s, salida cuártica) y hacerlos instantáneos bajo `prefers-reduced-motion`.
- **Do** mantener la columna de lectura en 38rem y el titular en 900 con interlineado apretado (0.92), hasta 6rem.
- **Do** pedir colores por variable de rol para que claro y oscuro funcionen solos; un componente en canvas debe leer las variables y releerlas al cambiar `prefers-color-scheme`.

### Don't:
- **Don't** añadir otro color de interfaz: el petróleo de enlaces y foco es el único; los botones son tinta y papel.
- **Don't** usar el color de lugar (mar, arena, petróleo) para codificar una fase, ni los colores de fase para pintar una región.
- **Don't** usar rojo de alarma para una anomalía.
- **Don't** usar tarjetas fuera de la tarjeta de paso en móvil, ni sombras de elevación.
- **Don't** redondear controles salvo las píldoras del selector de periodo.
- **Don't** poner Patrick Hand en párrafos, títulos ni botones.
- **Don't** convertir la página en un panel de indicadores ni en una ficha técnica: la cifra vive en una frase.
- **Don't** escribir hex directos en componentes; siempre la variable de rol.
