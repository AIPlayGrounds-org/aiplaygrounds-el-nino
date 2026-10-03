# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Público general peruano.** Llega sobre todo desde el móvil, en tres
  situaciones: tras ver una noticia o un rumor sobre El Niño (redes, WhatsApp,
  TV) y querer comprobar qué pasa de verdad; preocupado por su zona (por
  ejemplo, la costa norte), para saber si hay alertas o lluvias donde vive; o
  por clase o trabajo. Necesita entender en menos de un minuto qué pasa, qué
  destaca, dónde y si hay alertas.
- **Estudiantes, docentes, periodistas e investigadores.** Necesitan datos
  fiables y citables: series históricas, unidades, periodo base, metodología y
  enlace a la fuente original.

## Product Purpose

Observatorio web, científico y divulgativo, para seguir las señales del Fenómeno
El Niño en el Perú: temperatura del mar, precipitación, ríos, indicadores ENSO,
pronósticos y alertas, de fuentes nacionales e internacionales.

Éxito: el público general entiende en menos de un minuto la situación; el
usuario técnico puede identificar variable, unidad, fuente, periodo base,
metodología, fecha de actualización y enlace original.

## Positioning

- **Todo en un solo lugar:** reúne fuentes peruanas (SENAMHI, ENFEN, ANA, DHN,
  INDECI) e internacionales (NOAA, Copernicus, NASA) que hoy están dispersas en
  PDFs, visores y archivos.
- **Explicado en simple:** traduce el dato técnico a lenguaje claro sin perder
  rigor; el detalle técnico está siempre disponible bajo demanda.
- **Transparente y neutral:** muestra siempre fuente y fecha, separa dato
  observado, estimado y pronóstico, y no inventa índices, semáforos, umbrales ni
  consensos propios.

## Operating Context

- Proyecto de un equipo de tres personas (áreas de Datos, Web y Contenido), con
  entrega de todas las fases recortadas al 2026-10-31 (ver `ROADMAP.md`).
- Los datos llegan como JSON en `data/`, publicados por el paquete de
  `pipeline/` (con notebooks de marimo en `notebooks/`); la web los lee en la
  compilación (`nuxt generate`) y se sirve como sitio estático.
- Algunos datos peruanos se cargan a mano (estado de ENFEN) y otros dependen de
  respuestas institucionales pendientes.

## Capabilities and Constraints

- Secciones previstas: Dashboard, Territorio, Histórico, Pronósticos, Alertas,
  Aprende y Metodología (`ROADMAP.md`). Hoy existe solo la página del ONI.
- Fuera de alcance: cuentas y login, favoritos, notificaciones, API pública,
  descargas propias, búsqueda global, nivel distrito, modelos o consensos
  propios, módulos sectoriales.
- Solo español al lanzar, con i18n preparada (inglés y quechua a futuro).
- Uso de fuentes gratuitas y, en el caso de Open-Meteo, solo no comercial.
- Terminología: ver `docs/concepts.md` (anomalía, periodo base, ONI/RONI/ICEN,
  aviso/alerta/emergencia…).

## Brand Commitments

- Nombre: **WawaPacha**, de origen quechua y ligado a El Niño y la tierra.
  **Abierto:** la traducción y explicación oficiales del nombre deben
  confirmarse con el equipo antes de publicarlas.
- Lema actual: «Monitoreando el Fenómeno El Niño en el Perú».
- No hay logo ni identidad visual definidos todavía.

## Evidence on Hand

- Datos reales: `data/noaa-cpc-oni.json` (ONI de NOAA CPC, 919 trimestres desde
  DJF 1950).
- Inventario de 27 fuentes con veredicto en `sources.toml`; glosario en
  `docs/concepts.md`; reglas de datos en `docs/data-contract.md`.
- No hay testimonios, usuarios, métricas de uso ni prensa: no deben inventarse.

## Product Principles

1. Simple primero, técnico bajo demanda.
2. Fuente y fecha siempre visibles; si una fuente deja de actualizarse, se
   muestra el último dato con su antigüedad, nunca se oculta.
3. Una anomalía no es lo mismo que un peligro: no inferir causas, riesgos ni
   alertas que la fuente oficial no haya dado.
4. Cada señal se muestra por separado, con los umbrales oficiales de cada
   institución.
5. Separar siempre dato observado, estimado y pronóstico.

## Accessibility & Inclusion

- WCAG 2.1 AA.
- Responsive completo: diseñado para escritorio y plenamente usable en móvil,
  que es por donde llega gran parte del público general.
- Modo claro y oscuro, con gráficos, mapas y escalas legibles en ambos.
- Páginas de Aprende, Histórico y Territorio indexables (SEO).
