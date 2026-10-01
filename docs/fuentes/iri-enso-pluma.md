# IRI — pluma de pronóstico ENSO

**ID:** `iri-enso-pluma`
**Bloque:** Pronósticos
**Veredicto:** ✍️ Carga manual
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Gráfica y resumen mensual de pronósticos de modelos para SST en Niño 3.4. Sirve para mostrar el rango de modelos, conservando las salidas institucionales por separado.

## Identidad

| Campo | Valor |
|---|---|
| Institución | International Research Institute for Climate and Society (IRI), Columbia University; pronóstico CCSR/IRI |
| Producto / dataset | CCSR/IRI ENSO Predictions Plume y distribución probabilística |
| Variable(s) | Pronóstico de anomalía SST Niño 3.4 por modelo y temporada |
| Unidad | °C y probabilidades según gráfica |
| Tipo de dato | Pronóstico |
| Página oficial | https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/ |
| Documentación técnica | https://iri.columbia.edu/our-expertise/climate/enso/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Región Niño 3.4, 5°S–5°N y 120°–170°W |
| Resolución espacial | Un valor por región y modelo |
| Resolución temporal | Nueve temporadas móviles de tres meses |
| Histórico disponible | La página actual incluye una gráfica interactiva resumida de pronósticos previos; serie estructurada no disponible. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual; página indica publicación el día 19 o día hábil cercano. |
| Latencia | No aplica a publicación futura; pluma del 21-09-2026. |
| Último dato visto | Publicación 2026-09-21; el sitio describe 22 modelos, pero no expone un archivo de valores descargables. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Página HTML, gráficos e interacción web |
| URL de descarga | No se ofrece descarga de valores de pronóstico; la página dice expresamente que ya no proporcionan los datos. |
| Formato | HTML, imágenes/gráficos interactivos |
| Autenticación | Ninguna para ver la página |
| Tamaño aproximado | No aplica a valores; gráficos cargan desde el sitio de IRI. |
| Script de prueba | No aplica: no se distribuyen los valores de modelos. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Creative Commons Attribution 4.0 según aviso del sitio. |
| Atribución obligatoria | Se requiere atribución bajo CC BY 4.0; la página cita a ENSO Forecast Data © 2002–2026 IRI. |
| Restricciones | Aplican condiciones de atribución CC BY 4.0; la propia página solicita colaboración para acceso a datos que dejó de distribuir. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Los modelos usan periodos base distintos; IRI indica que no armoniza todas las anomalías y recomienda 1991–2020 o periodo cercano. |
| Umbrales oficiales | La página describe límites ENSO ±0,5 °C para su resumen probabilístico. |
| Notas metodológicas | Pluma de 22 modelos; el sitio avisa que algunos valores de la tabla pueden derivarse por promedio/interpolación temporal o lectura visual de mapas. No todos los modelos tienen igual habilidad. |

## Riesgos

- No se proporcionan los datos subyacentes, solo gráficos y explicaciones.
- Los periodos base varían entre modelos; no tratar pluma como una serie homogénea.
- Los resultados publicados pueden mantener la versión del pronóstico aunque cambien datos subyacentes.

## Conclusión

Carga manual solo como resumen institucional mensual y enlazando el gráfico original; no digitalizar ni reconstruir líneas de modelos sin permiso/acceso. Revisión una vez por publicación; tiempo de extracción no medido.

## Evidencia consultada

- [Pronóstico ENSO actual de IRI](https://iri.columbia.edu/our-expertise/climate/forecasts/enso/current/)
- [Recursos ENSO de IRI](https://iri.columbia.edu/our-expertise/climate/enso/)
