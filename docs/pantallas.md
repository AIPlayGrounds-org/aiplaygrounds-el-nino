# Pantallas de la v0.1

Qué se muestra en pantalla en la v0.1 ([D-002](decisiones.md#d-002--alcance-a-fin-de-mes-todas-las-fases-recortadas)) y qué dato alimenta cada parte. Las secciones de v0.2 en adelante (Territorio, Pronósticos por institución, Alertas, Histórico) se definen cuando llegue su fase.

La v0.1 es una sola página, `/`, que sigue respondiendo la pregunta que ya plantea la web del ONI: **¿llegó El Niño?** Cada panel responde una pregunta más concreta. Es una propuesta para el equipo: [D-007](decisiones.md#d-007--la-v01-es-una-página-hecha-de-paneles).

## Paneles

| # | Pregunta | Dato (ID de la ficha) | Campos que lee | Tipo | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | ¿Llegó El Niño? | [`noaa-cpc-oni`](fuentes/noaa-cpc-oni.md) | último `anomaly`, `season`, `end`; racha de trimestres ≥ +0,5 °C | observado | Existe |
| 2 | ¿Cómo está el mar frente al Perú? | [`noaa-cpc-nino-semanal`](fuentes/noaa-cpc-nino-semanal.md) | Niño 1+2: semana, `sst`, `anomaly`; serie de 12 meses | observado | Falta el pipeline |
| 3 | ¿Qué dice el estado oficial del Perú? | [`enfen-comunicado`](fuentes/enfen-comunicado.md) (carga manual) | nombre exacto del estado, número y fecha del comunicado, enlace | oficial (ver abajo) | Falta el pipeline |
| 4 | ¿Qué esperan los pronósticos? | [`noaa-cpc-outlook`](fuentes/noaa-cpc-outlook.md) | mes de emisión; por trimestre, % de cada categoría del RONI | pronóstico | Falta el pipeline |
| 5 | ¿Dónde está más caliente el mar? | [`noaa-oisst`](fuentes/noaa-oisst.md) | anomalía diaria por celda, fecha | observado | Falta un spike del mapa |
| 6 | Explora la serie histórica | `noaa-cpc-oni` | todos los registros | observado | Existe |
| 7 | Cómo lo hicimos | todos | bloque de procedencia de cada dato | — | Existe solo para el ONI |

El orden de la página es el de la tabla: primero la respuesta, después el contexto, al final la exploración y las fuentes.

## Lo que cada panel muestra

Toda parte de la página que muestra un dato responde las cinco preguntas de [`producto.md` §5](producto.md#5-reglas-para-cada-gráfico). Salen del bloque de procedencia del JSON, no se escriben a mano en la web:

| Pregunta | Campo |
| --- | --- |
| ¿Qué muestra y en qué unidad? | `variable`, `unit` |
| ¿Qué periodo cubre y cuál es su referencia? | primer y último registro, `reference_period` |
| ¿Observado, estimado o pronóstico? | `data_type` |
| ¿De dónde viene? | `source.institution`, `source.product`, `source.url` |
| ¿Cuándo se actualizó? | `ingestion_time` y la fecha del último registro |

Si el último registro es más viejo de lo que la fuente tarda en publicar, el panel avisa de su antigüedad y sigue mostrando el dato. Hoy lo hace solo el panel 1.

## Preguntas abiertas

1. **El tipo del estado de ENFEN.** `data_type` solo admite `observado`, `estimado` y `pronóstico` ([`datos.md`](datos.md)). El estado de ENFEN no es ninguno. Propuesta: añadir `oficial` al contrato en el PR que defina el esquema.
2. **Cómo mostrar el pronóstico.** CPC da nueve categorías por trimestre. Agruparlas en El Niño, neutral y La Niña es una suma nuestra, y los principios piden no inventar índices. Propuesta: mostrar las categorías de CPC tal cual, con la leyenda de sus rangos.
3. **El mapa.** No se sabe aún si cabe en la v0.1 sin MapLibre. Antes de decidir, un spike mide cuánto pesa una rejilla reducida a la región del Perú.
4. **Qué región Niño muestra el panel 2.** Propuesta: Niño 1+2 (frente al Perú) como serie principal y Niño 3.4 como referencia, con las otras dos regiones en el detalle técnico.
