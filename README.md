# WawaPacha

Observatorio web para seguir las señales del Fenómeno El Niño en el Perú: temperatura del mar, lluvia, ríos, indicadores ENSO, pronósticos y alertas. Reúne fuentes peruanas e internacionales y muestra de cada dato su fuente, su fecha y si es observado, estimado o pronóstico.

Es un sitio estático ([Nuxt 4](https://nuxt.com/) con Bun) alimentado por un pipeline de datos en Python (uv), con [notebooks de marimo](https://marimo.io) para explorarlo. No tiene backend, cuentas ni API.

**Estado:** existe una sola página, el [ONI](docs/fuentes/noaa-cpc-oni.md) de NOAA desde 1950. El resto del alcance y las fechas están en [`docs/decisiones.md`](docs/decisiones.md).

## Puesta en marcha

Necesitas [Git](https://git-scm.com/) y [mise](https://mise.jdx.dev/getting-started). mise instala las versiones de Bun y uv que fija `mise.toml`.

```sh
mise install
mise exec -- bun install
mise exec -- bun run dev
```

Abre <http://localhost:3100>. Con mise activado en tu shell, omite `mise exec --`.

| Comando | Uso |
| --- | --- |
| `bun run dev` | Servidor de desarrollo. |
| `bun run generate` | Sitio estático en `.output/public`. |
| `bun run build` | Compilación de producción. |
| `bun run preview` | Previsualiza la compilación; ejecuta antes `bun run build`. |

## Pipeline

El paquete de `pipeline/` descarga, valida y publica `data/<id>.json`, una fuente a la vez. Los notebooks de `notebooks/` muestran cada paso sin publicar nada. Desde `pipeline/`:

| Comando | Uso |
| --- | --- |
| `uv run wawapacha-pipeline run noaa-cpc-oni` | Descarga, valida y publica el ONI. |
| `uv run marimo edit ../notebooks/noaa_cpc_oni.py` | Abre el notebook en el navegador, paso a paso. |
| `uv run pytest` | Tests. |

Si una descarga no pasa la validación, no se publica nada y se conserva el JSON anterior.

## Fuera de alcance

Cuentas y login, notificaciones, API pública, descargas propias, búsqueda global, nivel distrito, modelos o consensos propios y módulos sectoriales. La lista completa está en [`docs/producto.md`](docs/producto.md#8-fuera-de-alcance-por-ahora).

## Documentación

Empieza por el [índice de `docs/`](docs/README.md). Para trabajar en el repositorio, [`CONTRIBUTING.md`](CONTRIBUTING.md).
