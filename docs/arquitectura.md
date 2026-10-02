# Arquitectura

Un sitio estático y un pipeline de datos. No hay backend.

```text
fuente pública
  → pipeline/<id>.py   descarga, valida, publica
  → data/<id>.json     datos y procedencia
  → nuxt generate      lee data/ al compilar
  → GitHub Pages
```

Datos y web solo se comunican por el formato de los JSON ([`datos.md`](datos.md)). Quien trabaja en la web puede usar datos de prueba con ese formato mientras el pipeline termina una fuente.

## Piezas

| Pieza | Dónde | Qué hace |
| --- | --- | --- |
| Pipeline | [`pipeline/`](../pipeline/) | Un notebook de marimo por fuente. Descarga, valida y escribe `data/<id>.json` ([D-004](decisiones.md#d-004--el-pipeline-se-escribe-en-notebooks-de-marimo)). Python con uv, tablas con polars. |
| Datos publicados | [`data/`](../data/) | Un JSON por fuente. Si una descarga falla la validación, se conserva el anterior. |
| Tipos del formato | [`app/types/dataset.ts`](../app/types/dataset.ts) | La forma de esos JSON en TypeScript. |
| Web | [`app/`](../app/) | Nuxt 4 y Vue con Bun. Gráficos con ECharts (`vue-echarts`). |
| Despliegue | [`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml) | `nuxt generate` y publicación en GitHub Pages en cada push a `main`. |
| Comprobaciones | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) | Tests del pipeline y compilación de la web en cada PR. |

Las versiones de Bun y uv las fija [`mise.toml`](../mise.toml).

## Decisiones que sostienen el diseño

- **Sin backend.** No hay cuentas, API pública ni descargas propias. Si hiciera falta, se añade PostGIS o una API sin cambiar el formato de los datos.
- **Una fuente que falla no oculta su dato.** Se conserva el JSON anterior con su fecha de ingesta y la web avisa de su antigüedad. Hoy lo hace la página del ONI ([`app/pages/index.vue`](../app/pages/index.vue)).
- **Dashboard con orden fijo al inicio.** Ordenar por anomalía estadística exige comparar de forma justa variables muy distintas (SST, caudal, lluvia). Queda para después.
- **Alertas enlazadas a la fuente oficial.** Mostrar una alerta caducada, o no mostrar una nueva, puede llevar a malas decisiones. No se reproducen en un mapa propio hasta tener una ingesta fiable.
- **Resumen con IA revisado por una persona.** Los primeros resúmenes de "Qué está pasando ahora" se revisan antes de publicarse. Las reglas están en [`producto.md` §6](producto.md#6-ia-qué-está-pasando-ahora).

## Pendiente

Estas piezas se propusieron y todavía no existen:

- Actualización programada de los datos (GitHub Actions con cron, una fuente a la vez).
- Mapas (MapLibre GL JS).
- Estilos con Tailwind. La web usa hoy sus propias hojas de estilo; la guía visual está en [`DESIGN.md`](../DESIGN.md).
