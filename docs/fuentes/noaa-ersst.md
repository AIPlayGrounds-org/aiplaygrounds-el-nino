# NOAA NCEI — ERSST v5

**ID:** `noaa-ersst`
**Bloque:** Histórico
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.4
**Revisado:** 2026-10-01

## Qué es

Análisis mensual global de SST en rejilla de 2° con reconstrucción estadística para completar cobertura. Útil como base histórica para comparar episodios del Pacífico.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NOAA National Centers for Environmental Information (NCEI) |
| Producto / dataset | Extended Reconstructed Sea Surface Temperature, versión 5 (ERSSTv5) |
| Variable(s) | SST y anomalía SST |
| Unidad | °C |
| Tipo de dato | Análisis reconstruido |
| Página oficial | https://www.ncei.noaa.gov/products/extended-reconstructed-sst |
| Documentación técnica | https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00927 |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Global, incluido el Pacífico ecuatorial |
| Resolución espacial | 2° × 2° |
| Resolución temporal | Mensual |
| Histórico disponible | Desde enero de 1854 hasta el presente. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual |
| Latencia | Alrededor de un mes: el 2026-10-01 el último archivo disponible era el de agosto de 2026. |
| Último dato visto | Archivo `ersst.v5.202608.nc` (agosto de 2026) listado en el servidor de NCEI; no se leyeron sus valores. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTP/FTP, NetCDF y ASCII; ERDDAP disponible |
| URL de descarga | https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/netcdf/ (un archivo NetCDF global por mes, `ersst.v5.AAAAMM.nc`). Alternativa con recorte en servidor: https://coastwatch.pfeg.noaa.gov/erddap/griddap/nceiErsstv5.html |
| Formato | NetCDF y ASCII; ERDDAP exporta subset en CSV/NetCDF. |
| Autenticación | Ninguna indicada en página de datos |
| Tamaño aproximado | Desconocido; depende de recorte/periodo. |
| Script de prueba | No aplica: entrega v0.4, solo ficha según guía. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Metadatos del ERDDAP NCEI: sin restricciones de acceso/uso, con descargo de responsabilidad; se permite usar y redistribuir gratis. |
| Atribución obligatoria | Citar Huang et al. (2017), NOAA NCEI y DOI 10.7289/V5T72FNM según la ficha del dataset. |
| Restricciones | El metadato advierte que puede contener inexactitudes y excluye garantías/uso legal. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Anomalías del dataset con climatología 1971–2000. |
| Umbrales oficiales | No aplica al producto SST bruto; umbrales ENSO requieren metodología separada. |
| Notas metodológicas | ERSSTv5 deriva de ICOADS, se produce en 2° y aumenta la completitud espacial mediante reconstrucción estadística. NOAA indica mayor fiabilidad después de la década de 1940. |

## Cómo leer el dato

**Qué es un valor:** un mapa por mes, desde enero de 1854. Cada celda de 2° (unos 220 km) tiene la temperatura media del mar del mes (°C) y su anomalía (°C, base 1971–2000).

**Ejemplo:** el último archivo disponible el 2026-10-01 era el de agosto de 2026 (`ersst.v5.202608.nc`). Sus valores no se leyeron.

**Para interpretarlo bien:**

- Es una **reconstrucción**: rellena con métodos estadísticos las zonas sin mediciones. Antes de la década de 1940 hay muchas menos mediciones y más incertidumbre.
- Sus celdas son muy grandes: no muestra detalles de la costa peruana. Sirve para comparar eventos a escala del Pacífico, no para mapas locales.
- El ONI se calcula a partir de ERSST, pero con su propio método y periodo base. Una anomalía de ERSST no es un valor del ONI.

**Conceptos:** [rejilla y resolución](../conceptos.md#rejilla-y-resolución) · [SST](../conceptos.md#temperatura-superficial-del-mar-sst) · [anomalía](../conceptos.md#anomalía) · [periodo base](../conceptos.md#periodo-base) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- Resolución de 2° es gruesa para costa y mapa local.
- La serie temprana tiene mayor incertidumbre; revisar notas y versión antes de interpretar extremos.
- Las versiones y revisiones deben etiquetarse.
- El ERDDAP de CoastWatch no respondió el 2026-10-01 (tiempo agotado); el servidor directo de NCEI sí. No depender de una sola vía de acceso.

## Conclusión

Automatizable como producto histórico v0.4: descarga pública en NetCDF/ASCII y ERDDAP permite recortar. No sustituye a SST costera fina ni al ONI oficial.

## Evidencia consultada

- [Página de ERSSTv5 de NOAA NCEI](https://www.ncei.noaa.gov/products/extended-reconstructed-sst)
- [Metadatos, acceso y cita del dataset](https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ncdc%3AC00927)
- [ERDDAP NOAA ERSSTv5](https://coastwatch.pfeg.noaa.gov/erddap/griddap/nceiErsstv5.html)
