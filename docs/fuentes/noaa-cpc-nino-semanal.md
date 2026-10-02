# NOAA CPC — índices semanales de las regiones Niño

**ID:** `noaa-cpc-nino-semanal`
**Bloque:** ENSO
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.1
**Revisado:** 2026-10-01

## Qué es

Serie semanal de temperatura superficial del mar (SST) y anomalía para Niño 1+2, 3, 3.4 y 4. Complementa el ONI mensual y permite mostrar el estado más reciente del Pacífico ecuatorial.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NOAA Climate Prediction Center (CPC) |
| Producto / dataset | Weekly SST indices, archivo wksst9120.for |
| Variable(s) | SST y anomalía de SST en las regiones Niño |
| Unidad | °C |
| Tipo de dato | Observado |
| Página oficial | https://www.cpc.ncep.noaa.gov/data/indices/ |
| Documentación técnica | https://www.cpc.ncep.noaa.gov/data/indices/Readme.index.shtml |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Regiones Niño del Pacífico ecuatorial |
| Resolución espacial | Un valor por región Niño: Niño 1+2, 3, 3.4 y 4 |
| Resolución temporal | Semanal |
| Histórico disponible | Desde la semana centrada en el 02-09-1981; 2352 semanas al 2026-10-01. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Semanal; CPC publica índices semanales |
| Latencia | Alrededor de una semana: el 2026-10-01 el último registro era la semana centrada en el 23SEP2026. |
| Último dato visto | 23SEP2026; Niño 1+2 +4,7 °C, Niño 3 +3,9 °C, Niño 3.4 +3,1 °C y Niño 4 +1,1 °C de anomalía. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTP, archivo de texto de columnas fijas |
| URL de descarga | https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for |
| Formato | Texto de ancho fijo con 4 líneas de cabecera; fecha (`02SEP1981`), SST y anomalía para cuatro regiones. Las anomalías negativas van pegadas a la SST (`20.6-0.1`), así que hay que leer por posición y no separar por espacios. |
| Autenticación | Ninguna observada |
| Tamaño aproximado | 145 KB (148.353 bytes el 2026-10-01); crece con cada semana. |
| Script de prueba | `spikes/noaa_cpc_nino_semanal.py` ✅ probado con `uv run`. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; la documentación de índices consultada no muestra una licencia específica. |
| Atribución obligatoria | Por confirmar; no encontré texto de atribución obligatorio. |
| Restricciones | Por confirmar; no encontré restricciones específicas del archivo. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | 1991–2020: CPC publica la serie semanal OISST.v2.1 con esa base en la página de índices, y el nombre del archivo (`wksst9120`) la indica. El archivo no lo declara en su cabecera. |
| Umbrales oficiales | No aplica a la serie observada; no asignar categorías propias. |
| Notas metodológicas | El archivo entrega promedios regionales, no una rejilla espacial. Se verificó su respuesta y se parsearon las cuatro parejas de valores SST/anomalía. |

## Riesgos

- El formato es texto de ancho fijo; conservar validaciones ante cambios de columnas.
- Cobertura regional agregada: no equivale a un mapa de SST.
- Su anomalía usa la base 1991–2020, distinta de la de OISST en PSL (1971–2000) y de la base móvil del ONI. No comparar ni restar anomalías de productos con bases distintas.

## Conclusión

Automatizable: descarga pública, archivo pequeño y valores interpretables. Aporta un producto de SST por región para la v0.1; no cubre un mapa de temperatura del mar.

## Evidencia consultada

- [Archivo semanal CPC](https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for)
- [Índices mensuales/semanales y preguntas frecuentes](https://www.cpc.ncep.noaa.gov/data/indices/Readme.index.shtml)
