# INEI / IGN — límites administrativos

**ID:** `limites-inei-ign`
**Bloque:** Territorio
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.2
**Revisado:** 2026-09-26

## Qué es

Capas geográficas de límites administrativos con nombres y códigos para regiones y provincias. Son la base del mapa territorial de WawaPacha.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Instituto Nacional de Estadística e Informática (INEI); candidato alternativo Instituto Geográfico Nacional (IGN) |
| Producto / dataset | Capas cartográficas de límites departamental y provincial |
| Variable(s) | Geometría, código y nombre de unidad administrativa |
| Unidad | No aplica a geometría |
| Tipo de dato | Cartografía de referencia |
| Página oficial | https://ide.inei.gob.pe/ |
| Documentación técnica | https://ide.inei.gob.pe/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú |
| Resolución espacial | Polígonos por departamento/provincia; escala/resolución por confirmar. |
| Resolución temporal | Versión cartográfica; no es serie temporal. |
| Histórico disponible | La página de descarga consultada identifica límites actualizados a 2023. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Actualización cuando el proveedor actualiza la cartografía; frecuencia no indicada. |
| Latencia | No aplica. |
| Último dato visto | Capas departamental, provincial y distrital actualizadas a 2023 según portal IDE INEI. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Portal de datos espaciales; descarga GPKG y servicios vectoriales según portal. |
| URL de descarga | https://ide.inei.gob.pe/ (sección descarga de capas; archivo no descargado). |
| Formato | GeoPackage (GPKG) según descripción del portal; otros formatos/servicios por confirmar. |
| Autenticación | No se observó requisito en página pública; acceso a fichero no probado. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.2; falta descargar y abrir la capa en QGIS. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; metadatos/licencia de cada capa deben revisarse antes de republicar. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | El portal IDE INEI ofrece capas vectoriales departamental/provincial/distrital, con GPKG, y advierte que la información puede tener inconsistencias. El paso requerido de descarga y validación en QGIS no pudo completarse: QGIS no está disponible en este entorno. |

## Cómo leer el dato

**Qué es un valor:** no son datos de clima: son polígonos con el contorno de cada departamento y provincia, con su nombre y su código **UBIGEO** de INEI (dos dígitos para el departamento, cuatro para la provincia y seis para el distrito).

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente. Falta abrir la capa en QGIS.

**Para interpretarlo bien:**

- Sirven para dibujar el mapa de Territorio y para ubicar cada dato en su región o provincia.
- Para unir datos de distintas fuentes se usa el código UBIGEO, no el nombre, porque los nombres pueden escribirse distinto.
- Los límites censales de INEI y los límites legales del IGN pueden no coincidir. Se usa uno solo, decidido por el equipo.

**Conceptos:** [rejilla y resolución](../conceptos.md#rejilla-y-resolución)

## Riesgos

- No se descargó archivo ni se comprobaron códigos/nombres de regiones y provincias dentro de la capa.
- El IGN puede tener límites o definiciones jurisdiccionales con otra condición legal; no mezclarlos con límites censales sin decisión del equipo.
- Falta revisar licencia y escala cartográfica.

## Conclusión

Pendiente por no completar la verificación exigida: el portal oficial parece ofrecer la capa adecuada y actualizada a 2023, pero no se descargó ni abrió en QGIS para comprobar atributos. Reanudar cuando QGIS esté disponible.

## Evidencia consultada

- [Portal de datos espaciales IDE INEI](https://ide.inei.gob.pe/)
