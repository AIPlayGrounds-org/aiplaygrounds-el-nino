# Open-Meteo — GloFAS (caudal de ríos simulado)

**ID:** `open-meteo-glofas`
**Bloque:** Ríos
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.3
**Revisado:** 2026-10-01

## Qué es

Caudal diario de los ríos simulado por GloFAS, el sistema global de alerta de inundaciones de Copernicus, servido por la API gratuita de Open-Meteo. Incluye el pasado (desde 1984) y pronósticos de hasta unos 7 meses. Es la única fuente de caudales gratuita y sin cuenta encontrada mientras SENAMHI y ANA no confirmen el acceso a sus series observadas.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Open-Meteo (intermediario); datos de GloFAS, Copernicus Emergency Management Service |
| Producto / dataset | Flood API, GloFAS v4 (combinación continua de histórico y pronóstico) |
| Variable(s) | Caudal diario (`river_discharge`); para pronósticos, también media, mediana, máximo, mínimo y percentiles del conjunto |
| Unidad | m³/s |
| Tipo de dato | Estimado (simulación de un modelo hidrológico), y pronóstico para fechas futuras |
| Página oficial | https://open-meteo.com/en/docs/flood-api |
| Documentación técnica | https://open-meteo.com/en/docs/flood-api |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Global; se consulta por coordenadas |
| Resolución espacial | 0,05° (unos 5 km) |
| Resolución temporal | Diaria |
| Histórico disponible | Desde 1984 |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Diaria |
| Latencia | Sin retraso apreciable: el 2026-10-01 devolvía valores hasta la fecha actual y pronóstico para los días siguientes. |
| Último dato visto | 2026-10-01, con pronóstico hasta el 2026-10-07 (consulta de prueba). |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | API REST (HTTP GET), respuesta JSON |
| URL de descarga | `https://flood-api.open-meteo.com/v1/flood?latitude=-5.225&longitude=-80.675&daily=river_discharge&past_days=7&forecast_days=7` |
| Formato | JSON |
| Autenticación | Ninguna |
| Tamaño aproximado | Menos de 1 KB por punto; admite varios puntos por petición (143 en una prueba). |
| Script de prueba | Probado el 2026-10-01 con peticiones directas; sin notebook todavía. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | CC BY 4.0. Uso gratuito solo **no comercial**; las condiciones incluyen expresamente la investigación pública y el contenido educativo. |
| Atribución obligatoria | Enlace «Weather data by Open-Meteo.com» a https://open-meteo.com/, y crédito a GloFAS / Copernicus Emergency Management Service. |
| Restricciones | 600 llamadas por minuto, 5000 por hora, 10 000 por día y 300 000 por mes. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica. |
| Umbrales oficiales | Ninguno. Los niveles críticos de cada río los define SENAMHI o ANA; no se deducen alertas de este caudal simulado. |
| Notas metodológicas | El caudal sale de un modelo hidrológico alimentado con datos meteorológicos, no de una medición. Con 5 km de resolución, el punto pedido puede no caer sobre el cauce del modelo: hay que elegir cada punto buscando la celda con mayor caudal en los alrededores. |

## Cómo leer el dato

**Qué es un valor:** el caudal medio de un día, en m³/s, en la celda de la red de ríos de GloFAS más cercana al punto pedido.

**Ejemplo:** en el Niño Costero de 2017, la celda del río Piura en GloFAS (-5,225; -80,675) simula un máximo de unos **2600 m³/s el 10 de marzo**. Según la prensa de la época, el río real **superó los 3400 m³/s** a finales de marzo, con el desborde sobre la ciudad el **27 de marzo**. El modelo detecta una crecida grande, pero no acierta ni la magnitud ni el día del pico.

**Para interpretarlo bien:**

- Es una **simulación**: sirve para ver si un río va alto o bajo respecto a lo habitual, no para dar cifras exactas.
- El punto importa mucho. En las coordenadas de la ciudad de Piura (-5,19; -80,63), el modelo daba 2 m³/s en marzo de 2017, porque esa celda no está sobre el río en su red. Cada punto debe validarse con una crecida conocida antes de publicarse.
- Las fechas futuras son **pronóstico** y se muestran separadas de las pasadas.
- Nunca se presenta como el caudal oficial ni se deducen alertas de él.

**Conceptos:** [nivel y caudal](../conceptos.md#nivel-y-caudal) · [tipos de dato](../conceptos.md#tipos-de-dato) · [aviso, alerta y emergencia](../conceptos.md#aviso-alerta-y-emergencia) · [rejilla y resolución](../conceptos.md#rejilla-y-resolución)

## Riesgos

- Confundir caudal simulado con medido. La web debe etiquetarlo siempre como «estimado por modelo».
- Elegir mal la celda da valores absurdos sin ningún error visible.
- Open-Meteo es un intermediario: si cambia sus condiciones, la alternativa es GloFAS en Copernicus, que exige cuenta.

## Conclusión

Automatizable: API pública sin cuenta, probada con el río Piura. Es útil para la v0.3 mientras no haya caudales observados de SENAMHI o ANA, siempre como dato estimado y con cada punto validado contra crecidas conocidas. Cuando haya datos observados, estos tienen prioridad. Su incorporación requiere aprobar [D-005](../decisiones.md).

## Evidencia consultada

- [Documentación de la Flood API](https://open-meteo.com/en/docs/flood-api)
- [Condiciones de uso de Open-Meteo](https://open-meteo.com/en/terms)
- [Licencia y atribución de Open-Meteo](https://open-meteo.com/en/licence)
- [Desbordes del río Piura en marzo de 2017: más de 3400 m³/s (Mongabay)](https://es.mongabay.com/2017/03/dia-despues-las-consecuencias-los-desbordes-e-inundaciones-del-rio-piura/)
- [27 de marzo de 2017: el río Piura con más de 3000 m³/s (Noticias Piura 3.0)](https://noticiaspiura30.pe/27-de-marzo-del-2017-el-dia-en-que-el-rio-piura-arraso-con-todo-la-ciudad/)
- Pendiente: confirmar el caudal máximo oficial con la serie de SENAMHI cuando haya acceso.
