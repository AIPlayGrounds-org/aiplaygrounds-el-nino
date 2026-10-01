# ECMWF / Copernicus C3S — SEAS5

**ID:** `ecmwf-seas5`
**Bloque:** Pronósticos
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Sistema europeo de pronóstico estacional. Es candidato para mostrar una perspectiva de modelo independiente, siempre identificado como pronóstico y enlazado a su fuente.

## Identidad

| Campo | Valor |
|---|---|
| Institución | European Centre for Medium-Range Weather Forecasts (ECMWF), distribuido por Copernicus Climate Change Service |
| Producto / dataset | SEAS5; servicio/dataset exacto de descarga por confirmar. |
| Variable(s) | Campos estacionales, por confirmar para ENSO/Niño 3.4. |
| Unidad | Desconocido; revisé la página oficial y la documentación enlazada, pero no encontré este dato. |
| Tipo de dato | Pronóstico |
| Página oficial | https://cds.climate.copernicus.eu/ |
| Documentación técnica | Desconocido; intenté localizar un archivo o servicio de descarga en la página oficial y no quedó confirmado. |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Por confirmar para producto ENSO y conjunto de descarga. |
| Resolución espacial | Por confirmar. |
| Resolución temporal | Pronóstico estacional; resolución temporal del dataset seleccionado por confirmar. |
| Histórico disponible | Por confirmar. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Por confirmar; el sistema emite pronósticos en ciclos operativos. |
| Latencia | Por confirmar. |
| Último dato visto | No se obtuvo un valor; descarga no intentada porque requiere cuenta CDS. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Copernicus Climate Data Store/API |
| URL de descarga | No se confirmó endpoint exacto; consultar catálogo del CDS. |
| Formato | Por confirmar; normalmente depende de dataset solicitado. |
| Autenticación | Cuenta del Climate Data Store requerida; no se creó ninguna cuenta. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: fuente pendiente de acceso autenticado y selección de dataset. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; revisar la licencia del conjunto específico en CDS. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Acceso sujeto a cuenta y condiciones del dataset CDS. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Por confirmar según campo/dataset. |
| Umbrales oficiales | No aplica al pronóstico bruto; categorías deben venir de metodología documentada. |
| Notas metodológicas | La fuente se identifica en la lista de candidatas y en la documentación de herramientas del repo; no se verificó una descarga de SEAS5 en esta revisión. |

## Riesgos

- Cuenta de acceso requerida; se respetó la instrucción de no crearla.
- No se fijó el dataset concreto, variable, región ni licencia.

## Conclusión

Pendiente: reanudar en el catálogo CDS cuando el equipo decida el acceso y los campos necesarios; registrar usuario, frecuencia, cobertura, resolución y licencia del dataset concreto.

## Evidencia consultada

- [Climate Data Store Copernicus](https://cds.climate.copernicus.eu/)
