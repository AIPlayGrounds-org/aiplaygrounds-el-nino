# Copernicus Marine — OSTIA

**ID:** `copernicus-ostia`
**Bloque:** SST
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Análisis diario de SST de nivel 4, sin huecos, con rejilla global de 0,05°. Es una alternativa de mayor resolución espacial a OISST.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Copernicus Marine Service; sistema OSTIA operado por Met Office (Reino Unido) |
| Producto / dataset | Global Ocean OSTIA Sea Surface Temperature and Sea Ice Analysis, SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001. |
| Variable(s) | Temperatura superficial fundacional del mar y fracción de hielo marino |
| Unidad | °C para SST |
| Tipo de dato | Análisis estimado con satélite e in situ |
| Página oficial | https://data.marine.copernicus.eu/?option=com_csw&product_id=SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001&view=details |
| Documentación técnica | https://data.marine.copernicus.eu/es/product/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/services |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Océano global |
| Resolución espacial | 0,05° × 0,05° (aprox. 6 km) |
| Resolución temporal | Diaria |
| Histórico disponible | El catálogo consultado muestra desde 2024-01-17; disponibilidad histórica exacta por confirmar. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Diaria; catálogo muestra actualización diaria a las 12:00. |
| Latencia | Por confirmar; el producto figura como casi en tiempo real. |
| Último dato visto | La página de servicios mostraba datos hasta 2026-09-09 al consultarla. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Copernicus Marine Toolbox/API, subconjuntos, ficheros y mapas |
| URL de descarga | Descarga programática mediante Copernicus Marine Toolbox; no se descargó en esta revisión. |
| Formato | NetCDF-3/NetCDF-4 |
| Autenticación | Cuenta Copernicus Marine; no se creó ninguna cuenta. |
| Tamaño aproximado | Desconocido; depende del área y periodo solicitados. |
| Script de prueba | No aplica: entrega v0.1 pendiente de acceso autenticado y prueba. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; la ficha del producto enlaza una licencia, pero no se revisaron sus condiciones. |
| Atribución obligatoria | Por confirmar; la ficha tiene sección de cita. |
| Restricciones | Requiere registro/cuenta para el acceso programático documentado. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a SST fundacional; confirmar si se usa otra variable/anomalía. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | El producto describe mapas diarios gap-free de SST fundacional; OSTIA combina satélite e in situ. No es idéntico a un producto de anomalía. |

## Cómo leer el dato

**Qué es un valor:** un mapa por día, con celdas de 0,05° (unos 5,5 km) y la **temperatura fundacional** del mar en °C. No trae anomalía.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente.

**Para interpretarlo bien:**

- La temperatura fundacional no incluye el calentamiento diurno de la superficie, así que no es exactamente comparable con OISST.
- Para mostrar anomalías habría que calcularlas con una climatología propia, documentada en la metodología. No se mezclaría con anomalías de otros productos.
- Su mayor resolución permite ver mejor la costa peruana que OISST.

**Conceptos:** [rejilla y resolución](../conceptos.md#rejilla-y-resolución) · [SST](../conceptos.md#temperatura-superficial-del-mar-sst) · [anomalía](../conceptos.md#anomalía) · [periodo base](../conceptos.md#periodo-base) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- El usuario indicó no crear cuentas; la cuenta de Copernicus Marine no se creó.
- La cobertura temporal publicada en metadatos puede variar entre vistas/servicios.

## Conclusión

Pendiente: es una alternativa viable por especificación y resolución, pero requiere cuenta y falta descargar datos, confirmar licencia/atribución y demostrar automatización.

## Evidencia consultada

- [Ficha del producto OSTIA](https://data.marine.copernicus.eu/?option=com_csw&product_id=SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001&view=details)
- [Servicios de acceso y metadatos OSTIA](https://data.marine.copernicus.eu/es/product/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/services)
