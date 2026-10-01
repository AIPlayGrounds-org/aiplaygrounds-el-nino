# NASA GPM — IMERG

**ID:** `nasa-imerg`
**Bloque:** Precipitación
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.2
**Revisado:** 2026-09-26

## Qué es

Estimaciones satelitales globales de precipitación, con productos tempranos de baja latencia y una versión final calibrada con pluviómetros. Es candidato para seguimiento casi en tiempo real.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NASA Global Precipitation Measurement (GPM) |
| Producto / dataset | Integrated Multi-satellitE Retrievals for GPM (IMERG), versión 07 |
| Variable(s) | Precipitación estimada |
| Unidad | mm acumulados o mm/h; depende de producto. |
| Tipo de dato | Estimado |
| Página oficial | https://gpm.nasa.gov/data/imerg |
| Documentación técnica | https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Global |
| Resolución espacial | 0,1° × 0,1° |
| Resolución temporal | Campos nativos cada media hora; existen agregados diarios y mensuales. |
| Histórico disponible | Continuidad de TRMM/GPM desde 1998 según página GPM. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Cada media hora para productos operativos. |
| Latencia | Early ~4 h; Late ~14 h; Final ~3,5 meses después del mes, según documentación IMERG V07 consultada. |
| Último dato visto | No se obtuvo archivo; requiere registro gratuito en NASA/PPS. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTPS/FTP de NASA PPS y otras rutas de archivo |
| URL de descarga | https://jsimpsonhttps.pps.eosdis.nasa.gov/imerg/gis/early/ |
| Formato | HDF5, GeoTIFF, NetCDF y otros según producto. |
| Autenticación | Registro de usuario gratuito obligatorio para acceso de datos PPS; no se creó cuenta. |
| Tamaño aproximado | Desconocido; depende de la resolución y duración. |
| Script de prueba | No aplica: entrega v0.2, ficha de viabilidad solamente. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar para reutilización/publicación; revisar términos del producto. |
| Atribución obligatoria | Por confirmar; el producto ofrece documentación técnica y referencias. |
| Restricciones | Acceso a PPS requiere registro; no se creó cuenta. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a acumulación de precipitación; la calibración de productos varía. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | IMERG combina sensores satelitales y procesamiento para estimaciones medio-horarias. En terreno montañoso, la precipitación es menos segura según descripción GPM. |

## Riesgos

- Acceso a descargas PPS requiere registro gratuito; se respetó la instrucción de no crearlo.
- Elegir Early/Late para baja latencia o Final para análisis; no mezclar sin etiquetado.

## Conclusión

Pendiente de prueba de acceso porque requiere registro no creado en esta revisión. La ficha confirma resolución, frecuencia y latencias publicadas; para retomar, registrar cuenta con autorización del equipo y verificar licencia/cita.

## Evidencia consultada

- [IMERG — acceso y documentación](https://gpm.nasa.gov/data/imerg)
- [Documentación técnica IMERG V07](https://gpm.nasa.gov/resources/documents/imerg-v07-technical-documentation)
