# NOAA NCEI — OISST v2.1

**ID:** `noaa-oisst`
**Bloque:** SST
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.1
**Revisado:** 2026-10-01

## Qué es

Análisis diario de SST y anomalía en una rejilla global de 0,25°. Serviría para mapas y series espaciales de la temperatura superficial del mar.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NOAA National Centers for Environmental Information (NCEI) |
| Producto / dataset | Daily Optimum Interpolation Sea Surface Temperature (OISST/DOISST), versión 2.1. Los metadatos de PSL indican datos satelitales AVHRR+VIIRS. |
| Variable(s) | SST, anomalía SST, error analítico, concentración de hielo |
| Unidad | °C para SST/anomalía |
| Tipo de dato | Análisis estimado a partir de satélite y observaciones in situ |
| Página oficial | https://www.ncei.noaa.gov/products/optimum-interpolation-sst |
| Documentación técnica | https://upwell.pfeg.noaa.gov/erddap/info/ncdcOisst21Agg/index.html |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Global, incluye Perú y el Pacífico ecuatorial |
| Resolución espacial | 0,25° × 0,25° |
| Resolución temporal | Diaria |
| Histórico disponible | Desde 1981-09-01. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Archivo preliminar diario; el archivo final se publica aproximadamente dos semanas después del preliminar, según metadatos ERDDAP. |
| Latencia | La versión preliminar se describe con un día de latencia y la final alrededor de dos semanas después. |
| Último dato visto | 2026-09-25; media del recorte Niño 1+2: SST 25,64 °C y anomalía +4,93 °C. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | THREDDS NetCDF Subset Service (NCSS) de NOAA PSL |
| URL de descarga | `https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.oisst.v2.highres/`; el spike solicita `sst.day.mean.<año>.nc` y `sst.day.anom.<año>.nc`. |
| Formato | NetCDF por HTTP, recortado en servidor por variable, fecha y caja espacial. |
| Autenticación | Ninguna indicada en el catálogo consultado. |
| Tamaño aproximado | La prueba descargó 177,4 KB para dos recortes de 15 días y 10° × 10°; la salida contiene solo las celdas seleccionadas. |
| Script de prueba | `spikes/noaa_oisst.py`, probado con `uv run` el 2026-09-27. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Los metadatos de ERDDAP dicen que los datos pueden usarse y redistribuirse gratis, con descargo de responsabilidad; no nombran una licencia formal. |
| Atribución obligatoria | Por confirmar; el conjunto incluye referencias y DOI, pero no se confirmó una frase obligatoria. |
| Restricciones | Metadatos señalan que los datos no están destinados a uso legal y que no se garantiza exactitud/completitud. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | 1971–2000 (climatología OI.v2), según los metadatos de ERDDAP y de los archivos `sst.day.anom` de PSL. |
| Umbrales oficiales | No aplica; no asignar umbrales propios. |
| Notas metodológicas | Producto Level 4: integra observaciones satelitales (AVHRR y VIIRS) e in situ, interpoladas para generar una rejilla espacialmente completa. Los datos de menos de 15 días pueden revisarse. |

## Riesgos

- El ERDDAP de CoastWatch y el catálogo/NCSS de NCEI agotaron el tiempo en esta sesión. NOAA PSL respondió al NCSS con dos recortes NetCDF; la prueba actualizó el dictamen de acceso.
- El spike usa la última quincena y toma la última fecha común. La serie anual de PSL se actualiza con retraso respecto al día actual.
- La anomalía usa la base 1971–2000, distinta de los índices semanales CPC y de las probabilidades CPC (1991–2020) y del ONI (base móvil). No comparar ni mezclar anomalías con bases distintas.
- El spike calcula medias de la caja Niño 1+2, excluyendo celdas sin valor; para producción habría que definir si se requieren medias, puntos o mapas.

## Conclusión

Automatizable: NOAA PSL entregó SST y anomalía como NetCDF para Niño 1+2; el spike leyó la fecha 2026-09-25 y valores en °C sin descargar archivos globales. La licencia con nombre y la atribución siguen por confirmar.

## Evidencia consultada

- [Producto NOAA OISST](https://www.ncei.noaa.gov/products/optimum-interpolation-sst)
- [Metadatos y acceso ERDDAP NOAA](https://upwell.pfeg.noaa.gov/erddap/info/ncdcOisst21Agg/index.html)
- [Catálogo OISST diario de NOAA PSL](https://psl.noaa.gov/thredds/catalog/Datasets/noaa.oisst.v2.highres/catalog.html)
- [Servicio NCSS de la serie SST diaria de NOAA PSL](https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.oisst.v2.highres/sst.day.mean.2026.nc/dataset.html)
- [Metadatos de la anomalía diaria de NOAA PSL](https://psl.noaa.gov/thredds/dodsC/Datasets/noaa.oisst.v2.highres/sst.day.anom.2026.nc.das)
