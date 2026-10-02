# El Niño

Aplicación web hecha con [Nuxt 4](https://nuxt.com/) y Vue. El proyecto usa Bun y define su versión en `mise.toml`.

## Requisitos

- [Git](https://git-scm.com/) para clonar el repositorio.
- [mise](https://mise.jdx.dev/getting-started) instalado.

## Puesta en marcha

Después de clonar el repositorio, abre una terminal en su carpeta raíz y ejecuta:

```sh
mise install
mise exec -- bun install
mise exec -- bun run dev
```

Abre [http://localhost:3000](http://localhost:3000) para ver la aplicación. mise instala la versión de Bun declarada en `mise.toml`; `mise exec` la usa sin requerir que actives mise en tu shell.

Si mise ya está activado en tu shell, puedes omitir `mise exec --` y ejecutar los comandos con Bun directamente, por ejemplo `bun install` y `bun run dev`.

## Comandos disponibles

Desde la raíz del proyecto:

| Comando | Uso |
| --- | --- |
| `bun run dev` | Inicia el servidor de desarrollo. |
| `bun run build` | Compila la aplicación para producción. |
| `bun run generate` | Genera una versión estática prerenderizada. |
| `bun run preview` | Previsualiza la compilación de producción; ejecuta antes `bun run build`. |

Si mise no está activado en tu shell, antepón `mise exec --` a cualquiera de estos comandos; por ejemplo: `mise exec -- bun run build`.

El código de la aplicación está en `app/`; la configuración de Nuxt está en `nuxt.config.ts`. Los scripts están definidos en `package.json` y las dependencias se registran en `bun.lock`.

## Pipeline de datos

Cada fuente es un notebook de [marimo](https://marimo.io) en `pipeline/` que descarga los datos, los valida según [`docs/protocolo-datos.md`](docs/protocolo-datos.md), los muestra y los publica en `data/<id>.json`. Desde la carpeta `pipeline/`:

| Comando | Uso |
| --- | --- |
| `uv run marimo edit noaa_cpc_oni.py` | Abre el notebook en el navegador para ver cada paso. Para publicar, pulsa el botón del final. |
| `uv run python noaa_cpc_oni.py` | Ejecuta el notebook sin interfaz: descarga, valida y publica. |
| `uv run pytest` | Ejecuta los tests. |

uv instala la versión de Python y las dependencias (marimo, polars y plotly) la primera vez. Si una descarga no pasa la validación, no se publica nada y el JSON anterior se conserva.

Más información: [documentación de Nuxt](https://nuxt.com/docs/getting-started/introduction) · [mise](https://mise.jdx.dev/).
