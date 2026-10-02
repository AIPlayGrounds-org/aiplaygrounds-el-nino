# Inventario de fuentes

Tabla resumen de todas las fuentes candidatas. Cada fila enlaza a su ficha cuando existe. La plantilla está en [`_plantilla.md`](_plantilla.md) y el ejemplo de ficha completa, en [`noaa-cpc-oni.md`](noaa-cpc-oni.md).

**Veredictos:** ✅ Automatizable · ✍️ Carga manual · ❌ Descartar · ⏳ Pendiente

**Prioridad:** revisar primero las de la **v0.1**, que necesitan ficha completa y script de prueba. Para las demás basta con la ficha.

## v0.1 — ENSO, temperatura del mar y pronósticos

| ID | Fuente | Qué aporta | Veredicto | Notas |
|---|---|---|---|---|
| [`noaa-cpc-oni`](noaa-cpc-oni.md) | NOAA CPC — ONI | Índice ENSO de referencia (Niño 3.4, trimestral) | ✅ Automatizable | Spike probado; el ASCII llega a JJA 2026. Licencia y versión explícita del archivo por confirmar. |
| [`noaa-cpc-nino-semanal`](noaa-cpc-nino-semanal.md) | NOAA CPC — índices Niño semanales | SST y anomalía semanal de Niño 1+2, 3, 3.4 y 4 | ✅ Automatizable | Spike probado; serie desde 02SEP1981, última semana 23SEP2026. Son promedios regionales, no mapas. |
| [`enfen-icen`](enfen-icen.md) | ENFEN / IGP — ICEN | Índice Costero El Niño, el índice oficial peruano (Niño 1+2) | ⏳ Pendiente | El IGP expone tabla numérica desde 1950 y SIOFEN anuncia descarga; no se confirmó la última fila ni un acceso repetible al dato actual. |
| [`enfen-comunicado`](enfen-comunicado.md) | ENFEN — comunicado oficial | Estado del sistema de alerta (vigilancia, alerta de El Niño costero…) | ✍️ Carga manual | Texto HTML y PDF; capturar y revisar el estado en cada emisión. |
| [`noaa-oisst`](noaa-oisst.md) | NOAA — OISST v2.1 | Mapas diarios de SST y anomalía | ✅ Automatizable | Spike probado vía NOAA PSL NCSS: 177,4 KB para SST y anomalía de un recorte Niño 1+2; no descarga los archivos globales. Licencia formal por confirmar. |
| [`copernicus-ostia`](copernicus-ostia.md) | Copernicus Marine — OSTIA | Alternativa a OISST, mayor resolución | ⏳ Pendiente | Producto diario 0,05°; requiere cuenta y falta confirmar licencia y probar descarga. |
| [`dhn-boletines`](dhn-boletines.md) | DHN — boletines oceanográficos | Datos del mar peruano (costa) | ✍️ Carga manual | Archivo público de boletines PDF mensuales; requiere extraer y revisar cada edición. |
| [`iri-enso-pluma`](iri-enso-pluma.md) | IRI (Columbia) — pluma ENSO | Pronóstico de Niño 3.4 de muchos modelos | ✍️ Carga manual | Publica gráficos mensuales, pero indica que ya no entrega los datos subyacentes; CC BY 4.0. |
| [`noaa-cpc-outlook`](noaa-cpc-outlook.md) | NOAA CPC — ENSO Outlook | Probabilidades oficiales de El Niño / Neutral / La Niña | ✅ Automatizable | Spike probado con la tabla HTML mensual de probabilidades basada en RONI. |
| [`bom-enso`](bom-enso.md) | BoM (Australia) — ENSO Outlook | Pronóstico de otra institución | ❌ Descartar | La página oficial declara que ENSO Outlook ya no está disponible; alternativa: CPC o IRI. |
| [`ecmwf-seas5`](ecmwf-seas5.md) | ECMWF SEAS5 (Copernicus C3S) | Pronóstico estacional | ⏳ Pendiente | Requiere cuenta CDS; no se creó cuenta ni se confirmó el dataset/descarga. |
| [`enfen-pronostico`](enfen-pronostico.md) | ENFEN — pronóstico | Pronóstico oficial peruano | ❌ Descartar | El pronóstico está dentro del comunicado oficial; evitar una ingesta duplicada. |

## v0.2 — Precipitación y territorio

| ID | Fuente | Qué aporta | Veredicto | Notas |
|---|---|---|---|---|
| [`chirps`](chirps.md) | UCSB CHC — CHIRPS | Precipitación estimada diaria/pentadal, con histórico largo | ✅ Automatizable | Repositorio oficial público y formatos estándar; verificar licencia y producto/versionado elegidos. |
| [`nasa-imerg`](nasa-imerg.md) | NASA — GPM IMERG | Precipitación casi en tiempo real | ⏳ Pendiente | Registro gratuito PPS requerido; no se creó cuenta. |
| [`senamhi-pisco`](senamhi-pisco.md) | SENAMHI — PISCO | Precipitación en rejilla para Perú | ⏳ Pendiente | Resolución e histórico documentados; no se confirmó una descarga actual ni sus condiciones. |
| [`senamhi-estaciones`](senamhi-estaciones.md) | SENAMHI — estaciones meteorológicas | Lluvia observada por estación | ⏳ Pendiente | Hay visor y solicitud de información; no se verificó una exportación repetible ni licencia. |
| [`limites-inei-ign`](limites-inei-ign.md) | INEI / IGN — límites administrativos | Regiones y provincias | ⏳ Pendiente | IDE INEI ofrece capas GPKG actualizadas a 2023; falta descargar y comprobar atributos en QGIS. |

## v0.3 — Ríos y alertas

| ID | Fuente | Qué aporta | Veredicto | Notas |
|---|---|---|---|---|
| [`senamhi-hidro`](senamhi-hidro.md) | SENAMHI — estaciones hidrológicas | Nivel y caudal de ríos | ⏳ Pendiente | Página y reportes por estación identificados; no se probó descarga de series. |
| [`ana-snirh`](ana-snirh.md) | ANA — SNIRH | Recursos hídricos, caudales | ⏳ Pendiente | Visor ofrece exportación, pero no se confirmó la serie temporal de caudales. |
| [`senamhi-avisos`](senamhi-avisos.md) | SENAMHI — avisos meteorológicos | Alertas de lluvia intensa y otros eventos | ✅ Automatizable | Listado HTML actualizado (último aviso del 2026-09-30) con campos, estado y enlaces de detalle. Usar `www.senamhi.gob.pe`, no el archivo histórico de `web2`. |
| [`indeci-coen`](indeci-coen.md) | INDECI / COEN | Emergencias y reportes | ✍️ Carga manual | Archivo público de reportes, mayormente PDF; curar solo eventos relevantes. |
| [`ana-alertas`](ana-alertas.md) | ANA — alertas hidrológicas | Riesgo de desborde | ⏳ Pendiente | No se localizó un producto nacional de alertas ni feed estructurado. |
| [`inaigem`](inaigem.md) | INAIGEM | Lagunas glaciares, aludes y aluviones | ⏳ Pendiente | Geoportal e inventario confirmados; no se verificó un feed público de alertas vigentes. |

## v0.4 — Histórico

| ID | Fuente | Qué aporta | Veredicto | Notas |
|---|---|---|---|---|
| [`noaa-ersst`](noaa-ersst.md) | NOAA — ERSST v5 | SST histórica mensual para comparar eventos | ✅ Automatizable | ERDDAP/NetCDF/ASCII; 2°, mensual desde 1854; revisar la resolución temprana. |
| [`enfen-icen-historico`](enfen-icen-historico.md) | ENFEN — ICEN histórico | Eventos costeros (1982–83, 1997–98, 2017) | ⏳ Pendiente | Además de la figura ENFEN 1950–2024, el IGP publica tabla numérica desde 1950; falta verificar descarga, última fecha y equivalencia metodológica. |

## Fuentes nuevas

Si encuentras una fuente que no está en la lista, añade una fila en el bloque que corresponda con veredicto ⏳ y avisa en el issue de la épica.
