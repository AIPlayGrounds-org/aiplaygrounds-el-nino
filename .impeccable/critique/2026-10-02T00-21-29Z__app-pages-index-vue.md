---
target: página del ONI
total_score: 29
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 1
target_identity: "file:D:\\projects\\AI_Playground\\el_nino\\app\\pages\\index.vue"
target_fingerprint: "sha256:4bb1a840ff91c7c2f420cff1c4be9b21cfc7f3271dfa896e2fbebe9c56a73404"
target_path: "D:\\projects\\AI_Playground\\el_nino\\app\\pages\\index.vue"
timestamp: 2026-10-02T00-21-29Z
slug: app-pages-index-vue
---
# Crítica 2: página del ONI (app/pages/index.vue)

## Puntuación: 29/40 (Buena; antes 24/40)
| # | Heurística | Puntos | Problema que queda |
|---|---|---|---|
| 1 | Visibilidad del estado | 3 | Fuente lejos del titular en móvil; el gráfico no marca el último valor |
| 2 | Lenguaje del mundo real | 3 | Códigos MJJ/JJA; "(5 meses)" confunde |
| 3 | Control y libertad | 3 | Barra de zoom difícil con el dedo |
| 4 | Consistencia | 3 | +0,5 frente a +0,50; Temperatura frente a Temperatura del mar |
| 5 | Prevención de errores de lectura | 3 | El "no es una alerta" llega después de la cifra |
| 6 | Reconocer antes que recordar | 3 | Hay que traducir los códigos de trimestre |
| 7 | Flexibilidad y eficiencia | 2 | Sin cita fácil; tabla de 12 trimestres |
| 8 | Estética y minimalismo | 3 | Una sola tarjeta para todo |
| 9 | Recuperación de errores | 3 | Estados bien resueltos |
| 10 | Ayuda | 3 | Falta glosario |

## Especificidad
Texto propio de WawaPacha; composición intercambiable; nada visual dice Perú. Detector: 0 hallazgos. Navegador: sin desbordamiento a 390 px, 0 errores de consola, lang="es", títulos correctos, foco visible, botones de 44 px en táctil. Se descarta la afirmación de que falta role="img": el DOM lo tiene.

## Problemas prioritarios
- [P1] El estado no responde en llano a "¿hay El Niño?"; "(5 meses)" y "MJJ 2026" confunden. (clarify)
- [P2] La fuente no se ve junto al titular en móvil. (layout)
- [P2] El gráfico no marca el último valor; etiquetas de umbral pisadas y con 2 decimales frente a 1 de la leyenda. (polish)
- [P2] La barra de zoom en móvil estorba (28 px, asas de unos 10 px), redundante con los botones. (adapt)
- [P3] Una sola tarjeta, sin elemento visual del Perú (mapa de Niño 3.4, Niño 1+2 y costa). (bolder)

## Alertas por persona
- Casey: cifra antes del "no es una alerta"; captura reenviada sin fuente.
- Sam: base bien; barra sin teclado compensada por los botones.
- Periodista: fuente al final; sin cita; sin RONI.

## Observaciones menores
Años raros en el eje con "Todo"; interlineado irregular del titular; color de relleno fijo en el código.
