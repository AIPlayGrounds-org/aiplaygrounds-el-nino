# WawaPacha

*Monitoreando el Fenómeno El Niño en el Perú*

Qué construimos y para quién. La arquitectura está en [`arquitectura.md`](arquitectura.md), las fases y el alcance en [`decisiones.md`](decisiones.md).

---

## 1. Qué es

Un observatorio web, científico y divulgativo, para seguir las señales del Fenómeno El Niño en el Perú. Reúne temperatura del mar, precipitación, ríos, indicadores ENSO, pronósticos y alertas de fuentes nacionales e internacionales. Siempre muestra de dónde viene cada dato y cuándo se actualizó.

Principio rector: **simple primero, técnico bajo demanda.**

Recorrido del usuario: observar → contextualizar → comparar → profundizar → consultar la fuente.

## 2. Para quién

| Público | Necesita |
|---|---|
| **Público general** | Entender en menos de un minuto qué pasa, qué destaca, dónde y si hay alertas. |
| **Estudiantes e investigadores** | Series históricas, unidades, referencias climatológicas, metodología y enlace a la fuente original. |

## 3. Principios

1. Claridad antes que densidad.
2. Rigor científico sin lenguaje innecesariamente complejo.
3. Fuente y fecha de actualización siempre visibles.
4. Separar claramente dato **observado**, **estimado** y **pronóstico**.
5. Una anomalía no es lo mismo que un peligro.
6. Usar los umbrales oficiales o científicos; no inventar umbrales propios.
7. No inferir causalidad.
8. Sin semáforo ni índice propio: cada señal se muestra por separado.

## 4. Secciones

| Sección | Contenido |
|---|---|
| **Dashboard** | Entrada principal: qué está pasando ahora, SST, ENSO, precipitación, ríos, pronósticos, alertas y novedades. Mapa secundario. |
| **Territorio** | Mapa protagonista por región y provincia, con una ficha breve de cada una: situación, alertas, indicadores, fecha y fuente. |
| **Histórico** | Series, anomalías y comparación con eventos: 1982–83, 1997–98 y 2017 (identificado como **Niño Costero**). |
| **Pronósticos** | Un gráfico por institución. Sin promedio ni consenso propio. |
| **Alertas** | Meteorológicas, hidrológicas y de aludes/aluviones (lagunas glaciares, zonas altoandinas). |
| **Aprende** | Guía divulgativa: qué es El Niño, ENSO, Niño Costero, anomalía, ONI, cómo leer un pronóstico… |
| **Metodología** | Fuentes, procesamiento, periodos base, limitaciones y control de calidad. |

## 5. Reglas para cada gráfico

Todo gráfico debe responder:

- ¿Qué muestra y en qué unidad?
- ¿Qué periodo cubre y cuál es su referencia histórica?
- ¿Es observado, estimado o pronóstico?
- ¿De dónde viene? (institución, producto y enlace)
- ¿Cuándo se actualizó?

Además:

- **Ver detalle técnico:** un desplegable bajo el gráfico con definición, resolución, periodo base y metodología.
- **Tendencias** con dirección y magnitud (`↑ +0,8 °C`), nunca solo la flecha.
- **Rango temporal global** (24 h · 7 d · 30 d · 12 m). Los indicadores con otra cadencia, como ENSO o los pronósticos, usan su propia ventana.
- **Si una fuente deja de actualizarse,** se muestra el último dato con su antigüedad. Nunca se oculta.
- **Estados vacíos y errores** con mensajes útiles, por ejemplo: "No fue posible actualizar los caudales; se muestra el dato del 20 de septiembre".

## 6. IA ("Qué está pasando ahora")

Un resumen automático en lenguaje divulgativo, generado a partir de datos ya normalizados, nunca de páginas web sueltas.

- **Puede:** seleccionar, ordenar, resumir y redactar.
- **No puede:** inferir causas, pronosticar, inventar alertas ni asignar niveles de riesgo.
- **Cada afirmación** debe enlazar a su fuente, variable, fecha y dato.

## 7. Fuentes potenciales

- **Perú:** SENAMHI, ENFEN, ANA, DHN, INDECI.
- **Internacionales:** NOAA, NASA, Copernicus, ECMWF.

La lista final depende del inventario de [fuentes](fuentes/README.md). No se ofrecen descargas propias: se enlaza siempre al dataset original.

## 8. Fuera de alcance (por ahora)

Cuentas y login, favoritos, notificaciones push, API pública, CSV/JSON propios, búsqueda global, nivel distrito, modelos predictivos propios, consenso de modelos. Tampoco módulos de agricultura, pesca, salud o infraestructura.

## 9. Requisitos transversales

- Responsive completo: diseñado para escritorio, usable en tablet y móvil.
- Modo claro y oscuro, con mapas y escalas legibles en ambos.
- Solo español al lanzar, con i18n preparada (inglés y quechua a futuro).
- Accesibilidad WCAG 2.1 AA.
- Páginas de Aprende, Histórico y Territorio indexables (SEO).
- Estética "científico moderno": limpia, con los gráficos como protagonistas. Sin gauges decorativos, 3D ni dashboards saturados.

## 10. Éxito

- **Público general:** en menos de un minuto entiende qué pasa, qué variables destacan, dónde y si hay alertas.
- **Usuario técnico:** puede identificar variable, unidad, fuente, referencia, metodología, fecha de actualización y enlace original.
