# NOAA CPC — Oceanic Niño Index (ONI)

**ID:** `noaa-cpc-oni`
**Bloque:** ENSO
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-27

## Qué es

El índice de referencia internacional para declarar un episodio El Niño o La Niña. Es la anomalía de la temperatura del mar en la región Niño 3.4 (Pacífico central), promediada en trimestres móviles. En WawaPacha va en el bloque ENSO del Dashboard y es la base de la comparación histórica.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NOAA Climate Prediction Center (CPC) |
| Producto / dataset | Oceanic Niño Index (ONI), archivo ASCII de CPC. CPC mantiene tablas históricas v5 (ERSSTv5) y v6 (ERSSTv6); el archivo no declara versión. Su valor JJA 2026 coincide con la tabla v6 consultada. |
| Variable(s) | Temperatura superficial del mar en Niño 3.4 y su anomalía |
| Unidad | °C |
| Tipo de dato | Observado |
| Página oficial | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/ |
| Documentación técnica | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_change.shtml |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Región Niño 3.4 (5°N–5°S, 170°W–120°W) |
| Resolución espacial | Un valor por región |
| Resolución temporal | Trimestral móvil (DJF, JFM, FMA…) |
| Histórico disponible | Desde DJF 1950 (919 registros el 2026-09-26) |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual; la página CPC indica que actualiza la tabla a más tardar el día 5 de cada mes. |
| Latencia | No hay latencia fija documentada. La página v5 indica que los valores ONI recientes pueden cambiar hasta dos meses tras su primera publicación. |
| Último dato visto | JJA 2026: anomalía +1,80 °C |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTP, archivo de texto |
| URL de descarga | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt |
| Formato | Texto en columnas: `SEAS YR TOTAL ANOM` |
| Autenticación | Ninguna |
| Tamaño aproximado | 22,5 KB medidos; descarga en 1,7 s durante la prueba del 2026-09-26. |
| Script de prueba | `spikes/noaa_cpc_oni.py` ✅ probado con `uv run` el 2026-09-27. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se encontró una licencia específica para el archivo ASCII de ONI. |
| Atribución obligatoria | Por confirmar; no se encontró una frase de atribución obligatoria. |
| Restricciones | Por confirmar; no se encontró declaración de reutilización específica para el archivo. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Periodos centrados de 30 años, actualizados cada cinco años; cada tramo histórico usa una base móvil. |
| Umbrales oficiales | CPC marca periodos cálidos/fríos cuando ONI alcanza ±0,5 °C durante al menos cinco temporadas consecutivas y solapadas. |
| Notas metodológicas | ONI es la media móvil de tres meses de anomalías SST en Niño 3.4. CPC declara que RONI se usa para el monitoreo y pronóstico ENSO oficiales; ONI sigue disponible como serie histórica. El archivo ASCII no incluye etiqueta de versión. |

## Riesgos

- El formato del archivo es texto en columnas y el archivo no declara versión.
- Las páginas oficiales CPC consultadas muestran v5 y v6; el valor JJA 2026 del archivo coincide con v6, pero debe confirmarse si CPC pretende mantener esa equivalencia.
- Los valores recientes pueden revisarse; CPC indica que las últimas cifras ONI son estimaciones.

## Conclusión

Automatizable: el archivo público se descargó y el spike interpretó 919 registros desde DJF 1950. La respuesta contenía JJA 2026 con anomalía +1,80 °C. La base temporal y el criterio ±0,5 °C durante cinco temporadas solapadas se confirmaron en las páginas CPC; quedan por confirmar la licencia y el versionado explícito del ASCII.

## Evidencia consultada

- [ONI v6 — página CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/)
- [ONI v5 — página CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v5/)
- [Cambios en la base del ONI](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_change.shtml)
- [Archivo ASCII descargado](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt)
