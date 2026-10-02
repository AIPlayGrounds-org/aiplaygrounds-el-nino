# ANA — Sistema Nacional de Información de Recursos Hídricos

**ID:** `ana-snirh`
**Bloque:** Ríos
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.3
**Revisado:** 2026-09-26

## Qué es

Portal de información hídrica y visores por cuencas. Es candidato para estaciones, caudales y contexto hidrológico, pero no se confirmó una serie numérica de caudales utilizable en esta revisión.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Autoridad Nacional del Agua (ANA), Sistema Nacional de Información de Recursos Hídricos (SNIRH) |
| Producto / dataset | Observatorio SNIRH y servicios geográficos |
| Variable(s) | Recursos hídricos; variable de serie temporal por confirmar. |
| Unidad | Por confirmar. |
| Tipo de dato | Observado; variable/producto concreto no confirmado. |
| Página oficial | https://snirh.ana.gob.pe/observatoriosnirh/Index.aspx?UH=2 |
| Documentación técnica | https://snirh.ana.gob.pe/observatoriosnirh/Index.aspx?UH=2 |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Cuencas/unidades hidrográficas de Perú |
| Resolución espacial | Capas de mapa por cuenca; resolución de estación/serie por confirmar. |
| Resolución temporal | Por confirmar. |
| Histórico disponible | Desconocido. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Desconocido. |
| Latencia | Desconocido. |
| Último dato visto | El visor presenta control “Datos Exportar”; no se exportó una serie en esta revisión. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Visor web y servicios GIS |
| URL de descarga | El portal tiene opción Datos Exportar; endpoint de observaciones de caudal no localizado. |
| Formato | Desconocido para datos temporales; un servicio GIS inspeccionado expone JSON de estaciones. |
| Autenticación | Ninguna observada para visor; exportación no probada. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.3. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; un servicio GIS usa texto de copyright SNIRH/PGIRH/ProGIRH. |
| Atribución obligatoria | Por confirmar; revisar atribución de cada capa. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a caudales sin anomalía definida. |
| Umbrales oficiales | Por confirmar por estación; no sustituir niveles críticos oficiales. |
| Notas metodológicas | El visor SNIRH muestra opción de exportar. El servicio ArcGIS consultado para estación de aforo del Mantaro describe 37 estaciones, pero los datos inspeccionados corresponden a puntos/atributos de estación, no a una serie observada de caudal. |

## Cómo leer el dato

**Qué es un valor:** si se confirma la descarga, una serie de caudal (m³/s) o nivel (m) por estación de aforo. Hoy solo se confirmó la lista de estaciones con sus atributos, no sus mediciones.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente.

**Para interpretarlo bien:**

- Se lee igual que los datos hidrológicos de SENAMHI: por estación y con los niveles críticos oficiales.
- Que una estación aparezca en el mapa no significa que sus datos sean públicos o estén actualizados.

**Conceptos:** [nivel y caudal](../conceptos.md#nivel-y-caudal) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- La presencia de capas/estaciones no prueba que la serie temporal de caudal sea pública.
- Se necesita confirmar servicio, periodo, unidades, latencia y licencias por capa.

## Conclusión

Pendiente: portal de exportación y metadatos geográficos existen, pero faltó confirmar descarga de los valores de caudal requeridos. No se enviaron consultas a ANA.

## Evidencia consultada

- [Visor por cuencas SNIRH](https://snirh.ana.gob.pe/observatoriosnirh/Index.aspx?UH=2)
- [Servicio ArcGIS SNIRH: estaciones de aforo Mantaro](https://geosnirh.ana.gob.pe/server/rest/services/OA_Mantaro/SW_Estaciones_Aforo/FeatureServer)
