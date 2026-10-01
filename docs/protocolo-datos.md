# Protocolo de datos

Reglas que cumple todo dato de WawaPacha, desde que se descarga hasta que aparece en la web. Los conceptos (anomalía, periodo base…) se explican en [`conceptos.md`](conceptos.md).

## 1. Origen

- Solo se automatiza una fuente con ficha en `docs/fuentes/` y veredicto ✅.
- Se descarga de la URL que indica la ficha, nunca de copias o páginas intermedias.

## 2. Validación

Antes de publicar, cada descarga se comprueba. **Si algo falla, no se publica nada y se conserva el JSON anterior.** La web sigue mostrando el último dato válido con su fecha.

Cada fuente comprueba como mínimo:

| Comprobación | Por qué |
|---|---|
| El archivo tiene la estructura esperada (cabecera, columnas) | Detecta cambios de formato en la fuente. |
| Cada valor está dentro de un rango físicamente posible | Detecta errores de lectura y valores corruptos. |
| Las fechas van en orden, sin huecos ni duplicados | Detecta descargas cortadas o mal leídas. |

Los valores faltantes se guardan como `null`, nunca como `0` ni con el código especial de la fuente (por ejemplo, `-99.9`).

## 3. Transformación

- **No se modifican los valores de la fuente.** Solo se cambia su formato.
- Si la fuente publica la anomalía, se usa la suya; no se recalcula.
- Si hay que calcular algo (un promedio, una anomalía), el método y el periodo base se documentan en la ficha de la fuente.

## 4. Formato publicado

Un archivo JSON por fuente en `data/<id>.json`, con los metadatos de procedencia y los registros:

| Campo | Contenido |
|---|---|
| `id` | El ID de la ficha, por ejemplo `noaa-cpc-oni`. |
| `source` | Institución, producto y URL de descarga. |
| `variable`, `unit` | Qué se mide y en qué unidad. |
| `data_type` | `observado`, `estimado` o `pronóstico`. |
| `spatial_resolution`, `temporal_resolution` | Cobertura del dato. |
| `reference_period` | Periodo base de la anomalía, si aplica. |
| `ingestion_time` | Cuándo se descargó, en UTC (ISO 8601). |
| `processing_version` | Versión del código que lo generó. |
| `records` | Los datos. Cada registro indica el periodo que describe (`start`, `end`). |

Las fechas siempre en ISO 8601: `2026-08` para un mes, `2026-08-31` para un día.

## 5. Comparabilidad

- Nunca se mezclan en un mismo gráfico anomalías con periodos base distintos sin indicarlo.
- Nunca se mezclan datos observados, estimados y pronósticos sin distinguirlos.

## 6. Pruebas

Cada fuente tiene un test que usa una copia real del archivo original guardada en el repositorio. Así, si la fuente cambia de formato, el test sigue sirviendo de referencia.
