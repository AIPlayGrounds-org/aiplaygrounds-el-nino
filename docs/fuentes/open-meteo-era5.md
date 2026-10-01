# Open-Meteo — ERA5 (lluvia por punto)

**ID:** `open-meteo-era5`
**Bloque:** Precipitación
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.2
**Revisado:** 2026-10-01

## Qué es

Lluvia diaria en cualquier punto del Perú, calculada por el reanálisis ERA5 de Copernicus y servida por la API gratuita de Open-Meteo. Permite mostrar la lluvia por región o provincia sin procesar rejillas ni crear cuentas.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Open-Meteo (intermediario); datos de ERA5, de Copernicus Climate Change Service (C3S) / ECMWF |
| Producto / dataset | Historical Weather API, modelo `era5` |
| Variable(s) | Precipitación diaria acumulada (`precipitation_sum`) |
| Unidad | mm |
| Tipo de dato | Estimado (reanálisis) |
| Página oficial | https://open-meteo.com/en/docs/historical-weather-api |
| Documentación técnica | https://open-meteo.com/en/docs/historical-weather-api |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Global; se consulta por coordenadas (una o varias por petición) |
| Resolución espacial | 0,25° (unos 28 km) |
| Resolución temporal | Diaria (también horaria) |
| Histórico disponible | Desde 1940 |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Diaria |
| Latencia | Unos 7 días: el 2026-10-01 el último día con dato era el 2026-09-24. Los días sin dato vienen como `null`. |
| Último dato visto | 2026-09-24 (Piura) |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | API REST (HTTP GET), respuesta JSON |
| URL de descarga | `https://archive-api.open-meteo.com/v1/archive?latitude=-5.19&longitude=-80.63&start_date=2026-09-01&end_date=2026-09-30&daily=precipitation_sum&models=era5` |
| Formato | JSON |
| Autenticación | Ninguna |
| Tamaño aproximado | Menos de 1 KB por punto y mes; respuesta en menos de 1 s (prueba del 2026-10-01). |
| Script de prueba | Probado el 2026-10-01 con peticiones directas; sin notebook todavía. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | CC BY 4.0. Uso gratuito solo **no comercial**; las condiciones incluyen expresamente la investigación pública y el contenido educativo. |
| Atribución obligatoria | Enlace «Weather data by Open-Meteo.com» a https://open-meteo.com/, y crédito a ERA5 / Copernicus Climate Change Service como fuente de los datos. |
| Restricciones | 600 llamadas por minuto, 5000 por hora, 10 000 por día y 300 000 por mes. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica: la API entrega lluvia, no anomalías. Si se calcula una anomalía, documentar el periodo base aquí. |
| Umbrales oficiales | No aplica. |
| Notas metodológicas | Siempre pedir `models=era5`. La opción por defecto (`best_match`) mezcla ERA5 con otros modelos (IFS desde 2017), y la propia documentación recomienda usar solo ERA5 para series largas y coherentes. |

## Cómo leer el dato

**Qué es un valor:** la lluvia total de un día en la celda de 0,25° que contiene el punto pedido, en mm.

**Ejemplo:** en Piura (-5,19; -80,63), ERA5 da 631 mm en marzo de 2017, con un máximo de 92 mm el 5 de marzo, durante el Niño Costero.

**Para interpretarlo bien:**

- Es un **reanálisis**: un modelo que combina observaciones de todo el mundo. No es la lluvia medida en una estación.
- Una celda de 28 km promedia la lluvia de una zona amplia; los aguaceros muy locales quedan suavizados.
- Los últimos días llegan con unos 7 días de retraso; hasta entonces son `null`, nunca cero.
- La API devuelve las coordenadas de la celda usada, que no coinciden exactamente con las pedidas.

**Conceptos:** [precipitación](../conceptos.md#precipitación) · [rejilla y resolución](../conceptos.md#rejilla-y-resolución) · [tipos de dato](../conceptos.md#tipos-de-dato) · [latencia y revisiones](../conceptos.md#latencia-y-revisiones)

## Riesgos

- Open-Meteo es un intermediario: si cambia sus condiciones o su API, hay que volver a la fuente original (Copernicus CDS, que exige cuenta).
- La opción por defecto mezcla modelos; olvidar `models=era5` cambiaría la serie sin aviso.
- El uso gratuito es solo no comercial. Si WawaPacha cambiara de naturaleza, habría que revisar la licencia.

## Conclusión

Automatizable: API pública sin cuenta, probada con datos de Piura. Es la vía más simple para mostrar la lluvia por región en la v0.2. Complementa a CHIRPS (mayor resolución, pero exige procesar rejillas) y no sustituye a las estaciones de SENAMHI cuando estén disponibles. Su incorporación requiere aprobar [D-005](../decisiones.md).

## Evidencia consultada

- [Documentación de la Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Condiciones de uso de Open-Meteo](https://open-meteo.com/en/terms)
- [Licencia y atribución de Open-Meteo](https://open-meteo.com/en/licence)
