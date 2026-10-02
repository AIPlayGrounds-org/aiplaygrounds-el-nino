---
target: página del ONI
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
target_identity: "file:D:\\projects\\AI_Playground\\el_nino\\app\\pages\\index.vue"
target_fingerprint: "sha256:e07fa06707b0b6584e8a7bfda0781d8cf1c4cc8baf4aa195022f0d3b4c552039"
target_path: "D:\\projects\\AI_Playground\\el_nino\\app\\pages\\index.vue"
timestamp: 2026-10-02T00-03-01Z
slug: app-pages-index-vue
closed: true
---
# Crítica: página del ONI (app/pages/index.vue)

## Puntuación (24/40, Aceptable)
| # | Heurística | Puntos | Problema principal |
|---|---|---|---|
| 1 | Visibilidad del estado | 2 | "Actualizado" es la fecha de descarga, no la del dato; sin antigüedad |
| 2 | Lenguaje del mundo real | 2 | Jerga sin explicar; sin conexión con el Perú |
| 3 | Control y libertad | 3 | Sin restablecer ni rangos rápidos |
| 4 | Consistencia | 3 | Tooltip blanco en modo oscuro |
| 5 | Prevención de errores | 3 | El rojo sugiere "peligro" |
| 6 | Reconocer antes que recordar | 3 | Colores de la línea sin explicar |
| 7 | Flexibilidad y eficiencia | 2 | Sin cita sugerida ni temperatura absoluta en el tooltip |
| 8 | Estética y minimalismo | 3 | Jerarquía plana tras la cifra |
| 9 | Recuperación de errores | 1 | Sin estados vacío, de error ni de dato desactualizado |
| 10 | Ayuda y documentación | 2 | Sin glosario; nota del RONI escondida |

## Especificidad
Contenido propio de WawaPacha; forma de tarjeta de dashboard genérica. Falta contexto peruano (ICEN, ENFEN, distancia de Niño 3.4 a la costa, unos 4400 km). Detector: 0 hallazgos, en modo degradado (sin contraste ni selectores). Confirmado: falta lang="es" y alternativa en texto del gráfico.

## Problemas prioritarios
- [P1] Gráfico no accesible y poco legible en modo oscuro: lang, aria/role, colores de ECharts por variables CSS, tabla alternativa. (harden, colorize)
- [P1] Falta contexto peruano y "una anomalía no es un peligro": bloque "¿Qué significa para el Perú?", enlace a ENFEN, nota del RONI visible, color cálido sin rojo de error. (clarify)
- [P1] Sin estados vacío/error/desactualizado; estado no simétrico para La Niña; fecha del dato frente a fecha de revisión. (harden)
- [P2] Móvil 360 px: área del gráfico, etiquetas cortadas, zoom táctil frente a scroll, rangos rápidos, .tech en una columna. (adapt)
- [P2] Jerarquía y tipografía genéricas: estado destacado, mini-leyenda de colores, marca, números tabulares. (typeset)

## Alertas por persona
- Casey (móvil): se va con miedo tras el rojo; el gráfico roba el scroll; nada sobre Piura.
- Sam (lector de pantalla): gráfico invisible; voz en inglés por falta de lang.
- Periodista: sin fecha de publicación NOAA ni cita; nota del RONI escondida; sin ICEN.

## Observaciones menores
Sin meta description ni Open Graph; sin tendencia (↑ respecto al trimestre anterior); "trimestres seguidos" se solapan; enlace a .txt crudo; formatAnomaly duplicado.

## Preguntas
1. ¿Primer dato: ONI o estado oficial de ENFEN?
2. ¿Qué color queda para una alerta oficial si el rojo ya está ocupado?
3. ¿Qué ve el usuario si NOAA deja de publicar 4 meses?
