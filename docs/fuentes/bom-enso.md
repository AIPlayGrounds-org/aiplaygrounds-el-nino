# BoM — ENSO Outlook

**ID:** `bom-enso`
**Bloque:** Pronósticos
**Veredicto:** ❌ Descartar
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Producto australiano de monitoreo/alerta ENSO que figuraba como pronóstico alternativo. La página del producto declara que ENSO Outlook ya no está disponible.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Bureau of Meteorology (BoM), Australia |
| Producto / dataset | ENSO Outlook (producto retirado de la página activa) |
| Variable(s) | Estado/alerta ENSO; variables de la edición histórica no revisadas. |
| Unidad | Desconocido; revisé la página oficial y la documentación enlazada, pero no encontré este dato. |
| Tipo de dato | Pronóstico |
| Página oficial | https://www.bom.gov.au/climate/enso/outlook/ |
| Documentación técnica | https://www.bom.gov.au/climate/enso/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Pacífico tropical; extensión exacta de ediciones históricas por confirmar. |
| Resolución espacial | Por confirmar. |
| Resolución temporal | Por confirmar. |
| Histórico disponible | La página activa conserva una sección de historial; extensión no medida. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | El producto ya no se publica en la página consultada. |
| Latencia | No aplica al producto retirado. |
| Último dato visto | Desconocido; página indica que ENSO Outlook ya no está disponible. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Página web de producto retirado |
| URL de descarga | No se encontró un canal actual de descarga para ENSO Outlook. |
| Formato | HTML histórico; producto vigente desconocido. |
| Autenticación | Ninguna para ver página |
| Tamaño aproximado | No aplica. |
| Script de prueba | No aplica: producto no disponible. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar para ediciones archivadas. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Producto actual no disponible. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Desconocido; no se encontró metodología vigente del producto retirado. |
| Umbrales oficiales | No aplica a producto disponible; no se verificaron umbrales históricos. |
| Notas metodológicas | La página oficial avisa que el producto ENSO Outlook dejó de estar disponible y remite a páginas de monitoreo/gestión climática del hemisferio sur. |

## Cómo leer el dato

**Qué es un valor:** producto retirado: no hay datos vigentes que leer.

**Ejemplo:** ninguno. La página oficial dice «The ENSO Outlook is no longer available».

**Para interpretarlo bien:**

- Si aparece una referencia antigua a un estado del sistema australiano (por ejemplo, «El Niño Watch» o «El Niño Alert»), corresponde a este producto y ya no se actualiza.

**Conceptos:** [pronóstico probabilístico](../conceptos.md#pronóstico-probabilístico)

## Riesgos

- La página activa dice expresamente que el producto dejó de estar disponible.
- Una petición automatizada recibió HTTP 403 en comprobación previa del repo.

## Conclusión

Descartar este producto como fuente vigente de pronóstico; sustituir por NOAA CPC o IRI. La página australiana de monitoreo del hemisferio sur puede revisarse por separado si el equipo busca un producto actual.

## Evidencia consultada

- [Página oficial BoM ENSO Outlook](https://www.bom.gov.au/climate/enso/outlook/)
- [Monitoreo del hemisferio sur BoM](https://www.bom.gov.au/climate/enso/)
