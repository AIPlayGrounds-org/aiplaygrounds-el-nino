# SENAMHI — estaciones meteorológicas

**ID:** `senamhi-estaciones`
**Bloque:** Precipitación
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.2
**Revisado:** 2026-09-26

## Qué es

Observaciones de estaciones meteorológicas convencionales y automáticas. Aportarían registros puntuales de lluvia y otras variables para contraste con productos de rejilla.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Servicio Nacional de Meteorología e Hidrología del Perú (SENAMHI) |
| Producto / dataset | Datos Hidrometeorológicos a Nivel Nacional — estaciones meteorológicas |
| Variable(s) | Variables por estación; lluvia, temperatura y otras según disponibilidad. |
| Unidad | Unidades por variable/estación; no se confirmaron en una exportación. |
| Tipo de dato | Observado |
| Página oficial | https://www.senamhi.gob.pe/servicios/?p=estaciones |
| Documentación técnica | https://www.senamhi.gob.pe/mapas/descarga-datos/pdf/tutorial-para-la-descarga-de-datos.pdf |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú; estaciones por departamento |
| Resolución espacial | Punto de estación |
| Resolución temporal | Desconocido; depende de la estación y variable. |
| Histórico disponible | No confirmado; el formulario de solicitud ofrece consulta de información histórica. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Por confirmar por estación/variable. |
| Latencia | Desconocido. |
| Último dato visto | No se descargó serie; el portal muestra visores incrustados. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Visor web y solicitud de información/descarga |
| URL de descarga | https://www.senamhi.gob.pe/site/descarga-datos/map_hist_data.php |
| Formato | Desconocido; el tutorial describe una opción de descarga y el visor incluye iframe. |
| Autenticación | El formulario de solicitud solicita identificación y finalidad; no se creó solicitud. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.2. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se localizaron condiciones de reutilización. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | El formulario de información hidrometeorológica solicita datos de identificación y contempla comprobante de pago; tarifa/condiciones exactas por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a observación directa. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | SENAMHI publica página de estaciones y un tutorial de descarga; también dispone un servicio de solicitud de información. No se verificó que la descarga disponible hoy cubra automáticamente una serie abierta. |

## Riesgos

- El visor de estaciones no se probó para obtener una serie numérica.
- La solicitud puede implicar datos personales y pago; no se envió ni creó solicitud.
- Cobertura temporal y actualización difieren por estación.

## Conclusión

Pendiente: existen estaciones y una ruta oficial de consulta/descarga, pero faltan prueba de exportación, condiciones, licencia y cobertura de lluvia. No se enviaron solicitudes.

## Evidencia consultada

- [Datos hidrometeorológicos SENAMHI](https://www.senamhi.gob.pe/servicios/?p=estaciones)
- [Mapa de descarga de datos SENAMHI](https://www.senamhi.gob.pe/site/descarga-datos/map_hist_data.php)
- [Tutorial oficial de descarga](https://www.senamhi.gob.pe/mapas/descarga-datos/pdf/tutorial-para-la-descarga-de-datos.pdf)
