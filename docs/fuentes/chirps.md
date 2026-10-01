# UCSB CHC — CHIRPS

**ID:** `chirps`
**Bloque:** Precipitación
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.2
**Revisado:** 2026-09-26

## Qué es

Estimaciones de precipitación derivadas de satélite y estaciones. La versión 3 ofrece rejillas cuasiglobales con varios formatos y escalas temporales para análisis de lluvia en Perú.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Climate Hazards Center (CHC), University of California Santa Barbara |
| Producto / dataset | CHIRPS v3 (CHC Infrared Precipitation with Stations) |
| Variable(s) | Precipitación |
| Unidad | mm por intervalo; confirmar variable y escala de cada archivo. |
| Tipo de dato | Estimado |
| Página oficial | https://chc.ucsb.edu/data/chirps3 |
| Documentación técnica | https://data.chc.ucsb.edu/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Dominio cuasiglobal; existe subdominio América Latina |
| Resolución espacial | 0,05° para productos CHIRPS; confirmar en archivo que se elija. |
| Resolución temporal | Pentadal, mensual, anual y productos diarios derivados. |
| Histórico disponible | Más de 40 años según descripción CHIRPS v3. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Los archivos se publican por periodo y acumulación; periodicidad exacta por producto por confirmar. |
| Latencia | Por confirmar para la versión/archivo seleccionado. |
| Último dato visto | Desconocido; no se descargó una escena durante esta revisión. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTP/FTP/RSYNC con índices públicos |
| URL de descarga | https://data.chc.ucsb.edu/ |
| Formato | GeoTIFF, NetCDF, BIL y COG; hay productos diarios/pentadales/mensuales. |
| Autenticación | No se observó autenticación en el repositorio público. |
| Tamaño aproximado | Desconocido; depende de resolución, dominio y periodo. |
| Script de prueba | No aplica: entrega v0.2, ficha de viabilidad solamente. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; se revisó la página del producto y repositorio, sin confirmar una licencia de reutilización concreta. |
| Atribución obligatoria | Por confirmar; consultar cita sugerida del producto antes de publicar. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica: precipitación acumulada/estimada, no anomalía salvo transformación posterior documentada. |
| Umbrales oficiales | No aplica; no definir umbrales de impacto propios. |
| Notas metodológicas | CHIRPS v3 se basa fundamentalmente en pentadas y meses. Sus productos diarios se derivan repartiendo totales con IMERG Late V07 o ERA5, según el tipo de producto. |

## Cómo leer el dato

**Qué es un valor:** lluvia acumulada en milímetros en cada celda de 0,05° (unos 5,5 km), para un periodo: pentada, mes o año. Hay productos diarios derivados.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente.

**Para interpretarlo bien:**

- Es un dato **estimado** a partir de satélites y estaciones, no una medición directa en cada celda.
- Siempre se indica el periodo de acumulación: una pentada y un mes no se comparan.
- Los productos diarios reparten los totales con otros datos (IMERG o ERA5): el valor de un día concreto es menos fiable que el de la pentada.
- En zonas de montaña, como los Andes, las estimaciones de lluvia por satélite tienen más error.

**Conceptos:** [precipitación](../conceptos.md#precipitación) · [rejilla y resolución](../conceptos.md#rejilla-y-resolución) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- Distinguir diaria satelital (`sat`) de diaria reanálisis (`rnl`) y de pentad/mensual.
- La versión v3 y archivos pueden tener propiedades distintas a CHIRPS v2.
- Licencia y cita pendientes de confirmación.

## Conclusión

Automatizable para v0.2: el repositorio oficial expone archivos de rejilla y formatos estándar. Elegir versión/escala temporal, verificar licencia y hacer una descarga de prueba antes de integrarlo.

## Evidencia consultada

- [CHIRPS v3 — página del producto](https://chc.ucsb.edu/data/chirps3)
- [Repositorio de datos CHC](https://data.chc.ucsb.edu/)
