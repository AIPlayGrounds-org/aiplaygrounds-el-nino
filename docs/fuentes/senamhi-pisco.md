# SENAMHI — PISCO precipitación

**ID:** `senamhi-pisco`
**Bloque:** Precipitación
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.2
**Revisado:** 2026-09-26

## Qué es

Producto nacional gridded de precipitación del SENAMHI construido a partir de estimaciones satelitales y datos de estaciones. Aporta cobertura histórica y espacial sobre el Perú.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Servicio Nacional de Meteorología e Hidrología del Perú (SENAMHI) |
| Producto / dataset | PISCO precipitación; referencias revisadas describen PISCOp v2.1. |
| Variable(s) | Precipitación |
| Unidad | mm |
| Tipo de dato | Estimado |
| Página oficial | https://www.senamhi.gob.pe/?p=monitoreo-pronostico-sequias |
| Documentación técnica | https://www.senamhi.gob.pe/load/file/01403SENA-36.pdf |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú |
| Resolución espacial | Documentación consultada describe aproximadamente 0,1° (~5 km), según producto/versión. |
| Resolución temporal | Mensual en la versión descrita. |
| Histórico disponible | Desde 1981 para PISCOp mensual v2.1 según documento SENAMHI consultado. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual en el producto documentado. |
| Latencia | Desconocido; publicación del producto no confirmada. |
| Último dato visto | No se confirmó un archivo numérico descargable. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Página de monitoreo y documentos; descarga de datos crudos no localizada. |
| URL de descarga | Desconocido; intenté localizar un archivo o servicio de descarga en la página oficial y no quedó confirmado. |
| Formato | Raster/GeoTIFF mencionado en página SENAMHI; endpoint no confirmado. |
| Autenticación | Desconocido; la solicitud de información hidrometeorológica institucional requiere formulario. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.2. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se encontró licencia de uso del producto. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar; el servicio de información puede requerir solicitud/costo; monto no investigado. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a valores de precipitación; anomalías calculadas requieren metodología aparte. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | La documentación SENAMHI consultada describe PISCOp v2.1 a paso mensual desde 1981 y ~0,1°. No se confirmó vigencia de esa ficha para la publicación actual. |

## Riesgos

- No se localizó archivo de descarga pública actual.
- La documentación encontrada describe una versión específica y puede no corresponder al producto más nuevo.
- Licencia y condiciones de solicitud pendientes.

## Conclusión

Pendiente: la utilidad y características históricas están documentadas, pero falta confirmar dónde obtener los archivos, actualización, costo/condiciones y licencia. Consultar a SENAMHI después de que el equipo envíe los correos.

## Evidencia consultada

- [Monitoreo de sequías SENAMHI con información PISCO](https://www.senamhi.gob.pe/?p=monitoreo-pronostico-sequias)
- [Documento técnico SENAMHI sobre PISCO mensual](https://www.senamhi.gob.pe/load/file/01403SENA-36.pdf)
