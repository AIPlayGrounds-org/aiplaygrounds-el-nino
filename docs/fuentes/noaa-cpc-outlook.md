# NOAA CPC — probabilidades oficiales ENSO

**ID:** `noaa-cpc-outlook`
**Bloque:** Pronósticos
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.1
**Revisado:** 2026-10-01

## Qué es

Tabla de probabilidades oficiales por temporada para categorías de intensidad ENSO, calculadas con RONI. Aporta una previsión institucional legible y comparable mes a mes.

## Identidad

| Campo | Valor |
|---|---|
| Institución | NOAA Climate Prediction Center (CPC) |
| Producto / dataset | Official NOAA CPC ENSO Strength Probabilities |
| Variable(s) | Probabilidad de categorías de intensidad para temporadas ENSO |
| Unidad | % |
| Tipo de dato | Pronóstico |
| Página oficial | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/strengths/ |
| Documentación técnica | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Niño 3.4, Pacífico ecuatorial central |
| Resolución espacial | Un valor por categoría de intensidad y temporada |
| Resolución temporal | Nueve temporadas móviles de tres meses |
| Histórico disponible | Archivo de ediciones anteriores por confirmar. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual; CPC indica actualización el segundo jueves asociado al diagnóstico ENSO. |
| Latencia | Publicación mensual; no se declara una latencia desde el origen. |
| Último dato visto | Emisión September 2026; primera temporada de la tabla ASO; script volvió a leer probabilidades porcentuales el 2026-09-27. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTTP, tabla HTML |
| URL de descarga | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/strengths/ |
| Formato | HTML con tabla de porcentajes |
| Autenticación | Ninguna observada |
| Tamaño aproximado | 30,5 KB medidos; descarga en 1,0 s durante la prueba. |
| Script de prueba | `spikes/noaa_cpc_outlook.py` ✅ probado con `uv run`. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se encontró una licencia explícita en la página del producto. |
| Atribución obligatoria | Por confirmar; CPC identifica el pronóstico como oficial, sin texto exacto de atribución localizado. |
| Restricciones | Por confirmar; no se hallaron restricciones específicas de reutilización. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Desviaciones RONI con climatología 1991–2020 según página de probabilidades. |
| Umbrales oficiales | La página muestra límites de intensidad en °C; leerlos de la tabla/metodología, no construir umbrales propios. |
| Notas metodológicas | La probabilidad oficial la determina un equipo de aproximadamente diez pronosticadores a partir de observaciones y modelos. Es una síntesis institucional, no el resultado de un solo modelo. |

## Cómo leer el dato

**Qué es un valor:** para cada uno de los próximos nueve trimestres, el porcentaje de probabilidad de nueve categorías del RONI: cuatro de La Niña (de ≤ −2,0 °C a −0,5 °C), una neutral (entre −0,5 y +0,5 °C) y cuatro de El Niño (débil, moderado, fuerte y muy fuerte, de +0,5 °C a ≥ +2,0 °C). Cada fila suma 100 %.

**Ejemplo:** en la emisión de septiembre de 2026, el trimestre OND 2026 tenía 98 % en la categoría ≥ +2,0 °C y 2 % en la de +1,5 a +2,0 °C. Para AMJ 2027 el reparto era 55 % neutral, 35 % El Niño débil, 8 % moderado y 2 % La Niña débil.

**Para interpretarlo bien:**

- Es la probabilidad de la **intensidad** del índice, no de sus impactos. NOAA aclara que un El Niño fuerte no garantiza impactos fuertes en un lugar concreto.
- Se basa en el RONI, no en el ONI. No se dibuja como continuación de la serie ONI sin explicarlo.
- Cambia cada mes: siempre se muestra con su mes de emisión.

**Conceptos:** [pronóstico probabilístico](../conceptos.md#pronóstico-probabilístico) · [ONI, RONI e ICEN](../conceptos.md#índices-enso-oni-roni-e-icen) · [periodo base](../conceptos.md#periodo-base) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- La tabla y su encabezado pueden cambiar; el script valida que encuentre filas y porcentajes.
- El HTML contiene un comentario oculto con una emisión antigua (`Issued April 2026`). Leer la fecha de emisión del texto visible, nunca del primer «Issued» que aparezca en el código.
- Las probabilidades se verifican con RONI (base 1991–2020), no con el ONI. No mezclarlas con la serie ONI en un mismo gráfico sin explicarlo.
- Las probabilidades se actualizan mensualmente y no son pronósticos de impacto local.

## Conclusión

Automatizable: tabla HTML pública, pequeña y extraíble; spike obtiene la emisión y porcentajes. Usar como un pronóstico institucional independiente, explicar que se basa en RONI y no inferir impacto peruano.

## Evidencia consultada

- [Probabilidades oficiales NOAA CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/strengths/)
- [Información de monitoreo ENSO CPC](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/roni/)
