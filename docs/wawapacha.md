# WawaPacha

*Monitoreando el Fenómeno El Niño en el Perú*

Este documento resume qué queremos construir y cómo proponemos hacerlo. La parte de producto está acordada. La parte técnica son **propuestas para discutir en equipo**.

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

La lista final depende del inventario de fuentes (ver §11). No se ofrecen descargas propias: se enlaza siempre al dataset original.

## 8. Fuera de alcance (por ahora)

Cuentas y login, favoritos, notificaciones push, API pública, CSV/JSON propios, búsqueda global, nivel distrito, modelos predictivos propios, consenso de modelos. Tampoco módulos de agricultura, pesca, salud o infraestructura.

## 9. Requisitos transversales

- Responsive completo: diseñado para escritorio, usable en tablet y móvil.
- Modo claro y oscuro, con mapas y escalas legibles en ambos.
- Solo español al lanzar, con i18n preparada (inglés y quechua a futuro).
- Accesibilidad WCAG 2.1 AA.
- Páginas de Aprende, Histórico y Territorio indexables (SEO).
- Estética "científico moderno": limpia, con los gráficos como protagonistas. Sin gauges decorativos, 3D ni dashboards saturados.

---

## 10. Arquitectura técnica (propuesta)

### Stack

| Capa | Propuesta | Por qué |
|---|---|---|
| **Frontend** | Nuxt 4 + Vue + TypeScript, con Bun | El repositorio ya está en Nuxt. Cubre SSR/SSG, SEO, routing e i18n. El informe sugería Next.js, pero como recomendación, no como decisión. |
| **Estilos** | Tailwind CSS | |
| **Gráficos** | Apache ECharts (`vue-echarts`) | Series temporales, anomalías y buen rendimiento. |
| **Mapas** | MapLibre GL JS | Abierto, con GeoJSON, capas, polígonos y puntos. |
| **Ingesta de datos** | Scripts en Python (pandas, xarray) | Es el ecosistema científico para datos climáticos. |
| **Automatización** | GitHub Actions (cron) | Cada fuente con su propia frecuencia. |
| **Hosting** | Estático (Cloudflare Pages o Netlify) | Coste casi nulo y sin servidores que mantener. |

### Sitio estático con pipeline de datos, sin backend propio al inicio

El informe propone FastAPI, PostgreSQL/PostGIS y un sistema de colas. Como no hay cuentas, API pública ni descargas, basta con:

```text
GitHub Actions (cron por fuente)
  → un script Python por fuente (adaptador)
  → JSON normalizados con metadatos de procedencia
  → nuxt generate → hosting estático
```

- **Si una fuente falla,** el JSON anterior se mantiene con su fecha. Así se cumple la regla de "mostrar el último dato con su antigüedad" sin trabajo extra.
- **Quien hace datos y quien hace frontend no se bloquean.** El frontend puede avanzar con datos de prueba que sigan el mismo formato.
- **Si más adelante hace falta,** se añade PostGIS o una API sin cambiar el formato de los datos.

### Contrato de datos

Cada fuente tiene su propio adaptador, que descarga, valida, normaliza y guarda. Cada registro lleva sus metadatos de procedencia:

```text
source               institución (p. ej. NOAA)
dataset / product    producto concreto
variable             variable física
observation_time     fecha del dato
ingestion_time       cuándo lo descargamos
unit                 unidad
data_type            observado | estimado | pronóstico
spatial_resolution
temporal_resolution
reference_period     periodo base de la anomalía
source_url           enlace al original
processing_version   versión del adaptador
```

Estos campos alimentan directamente lo que se muestra junto a cada gráfico: fuente, fecha, tipo de dato y detalle técnico.

### Otras decisiones propuestas

- **Dashboard con orden fijo al inicio.** Ordenar por anomalía estadística exige comparar de forma justa variables muy distintas (SST, caudal, lluvia), lo que es un problema en sí mismo. Queda para más adelante.
- **Alertas enlazadas a la fuente oficial en la primera versión.** Mostrar una alerta caducada, o no mostrar una nueva, puede llevar a malas decisiones. Al principio se enlaza a la fuente oficial con su fecha visible y un aviso legal. No se reproducen en un mapa propio hasta tener una ingesta fiable.
- **Resumen con IA revisado por una persona al principio.** Los primeros resúmenes de "Qué está pasando ahora" pasan por revisión humana antes de publicarse.

## 11. Plan por fases (propuesta)

En lugar de lanzar las siete secciones a la vez, proponemos publicar pronto y crecer por partes:

| Entrega | Contenido |
|---|---|
| **Fase 0 — Inventario de fuentes** | Para cada fuente: variable, formato, forma de acceso, licencia, frecuencia, latencia y estabilidad. Nos lo repartimos. |
| **v0.1 — Estado actual** | Dashboard con ENSO (Niño 1+2, Niño 3.4, ONI), SST, estado oficial de ENFEN y 1 o 2 pronósticos. Metodología básica y 2 o 3 páginas de Aprende. |
| **v0.2** | Precipitación + Territorio (regiones y provincias). |
| **v0.3** | Ríos + Alertas. |
| **v0.4** | Histórico (1982–83, 1997–98, 2017). |
| **Después** | Novedades, resumen con IA y ordenación dinámica del Dashboard. |

**La Fase 0 va primero porque decide todo lo demás.** Las fuentes internacionales (índices de NOAA, SST satelital, precipitación CHIRPS, pronósticos ENSO del IRI) suelen ser fáciles de descargar. Varias fuentes peruanas publican en PDF, comunicados o visores web, sin una API estable. Hay que comprobarlo fuente por fuente. Algunos datos, como el estado oficial de ENFEN, quizá convenga cargarlos a mano.

## 12. Éxito

- **Público general:** en menos de un minuto entiende qué pasa, qué variables destacan, dónde y si hay alertas.
- **Usuario técnico:** puede identificar variable, unidad, fuente, referencia, metodología, fecha de actualización y enlace original.

## 13. Para decidir juntos

- ¿Aceptamos la arquitectura propuesta (Nuxt + sitio estático + pipeline en Python)?
- ¿Aceptamos el plan por fases y el alcance de la v0.1?
- ¿Quién se encarga de cada área: datos, visualización, contenido e infraestructura?
- ¿Tenemos una fecha objetivo para publicar la v0.1?
