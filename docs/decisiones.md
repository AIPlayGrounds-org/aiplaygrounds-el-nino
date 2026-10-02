# Registro de decisiones

Cada decisión del proyecto queda aquí con su fecha, qué se decidió y por qué. Las decisiones nuevas se proponen en un PR para que el equipo las revise antes de aceptarlas.

**Estados:** 🟡 Propuesta · ✅ Aceptada · ❌ Rechazada · 🔁 Reemplazada

---

## D-001 — Primera meta: el ONI de punta a punta

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta
- **Plazo:** 2026-10-09 (ver [D-002](#d-002--alcance-a-fin-de-mes-todas-las-fases-recortadas))

### Qué

La primera entrega es una página web que muestra el **Índice Oceánico El Niño (ONI)** de NOAA desde 1950 en un gráfico. Junto al gráfico se ve:

- la fuente (institución, producto y enlace al original);
- la unidad (°C de anomalía);
- la fecha de la última actualización;
- que es un dato **observado**.

### Por qué

- Es el índice de referencia de El Niño a nivel mundial.
- Se obtiene de un archivo de texto público, sin cuentas ni permisos.
- Obliga a recorrer todo el camino (obtener, limpiar, guardar y mostrar el dato). Ese recorrido servirá de molde para las fuentes siguientes.

### Fuera de esta meta

Otros índices (incluido el ICEN peruano), mapas, pronósticos, alertas, resumen con IA y el resto de secciones de [`producto.md`](producto.md). Se abordan después, una por una.

### Terminado cuando

- [x] Existe un documento con las reglas de calidad y procesamiento de datos.
- [x] Un script descarga el ONI, lo valida y lo guarda como JSON, con un test.
- [x] La web muestra el gráfico con fuente, unidad, fecha y tipo de dato.
- [x] El trabajo está en `main` mediante un PR revisado.

---

## D-002 — Alcance a fin de mes: todas las fases, recortadas

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta
- **Plazo:** 2026-10-31

### Qué

Las cuatro fases del plan inicial (`wawapacha.md` §11, en el historial de git) se publican antes del 31 de octubre, pero cada una **solo con las fuentes que ya se pueden obtener sin depender de una institución**. El veredicto de cada fuente está en [`fuentes/`](fuentes/README.md).

| Fase | Entra | Queda para después |
|---|---|---|
| **v0.1** ENSO y mar | ONI, índices Niño semanales, mapa OISST, probabilidades NOAA CPC, estado ENFEN (carga manual) | ICEN, OSTIA, ECMWF SEAS5 |
| **v0.2** Lluvia y territorio | CHIRPS, límites de regiones y provincias INEI | PISCO, estaciones SENAMHI, IMERG |
| **v0.3** Ríos y alertas | Avisos SENAMHI, enlaces a las alertas oficiales | Caudales ANA y SENAMHI, alertas ANA, INAIGEM |
| **v0.4** Histórico | ONI y ERSST con los eventos 1982–83, 1997–98 y 2017 | ICEN histórico |

### Por qué

El plazo es fijo. Las fuentes que quedan fuera necesitan respuesta de una institución, una cuenta aún no aprobada o una licencia sin confirmar, y nada de eso depende del equipo.

### Condiciones

- Los correos a IGP/ENFEN, SENAMHI, ANA, DHN e INAIGEM se envían en la primera semana, para que las respuestas lleguen a tiempo para una fase posterior.
- No se publica una fuente sin su texto de atribución y sus condiciones de uso revisadas.
- Lo que no entre en esta tabla no bloquea el plazo.

---

## D-003 — Reparto del equipo

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta

Tres personas trabajando en paralelo, cada una responsable de un área:

| Área | Responsable | Qué hace |
|---|---|---|
| **Datos** | _por definir_ | Protocolo de datos, scripts por fuente, tests y JSON publicados. |
| **Web** | _por definir_ | Páginas, gráficos, mapas y despliegue. |
| **Contenido** | _por definir_ | Textos de Aprende y Metodología, carga manual de ENFEN, correos a instituciones y licencias. |

Datos y web se comunican solo a través del formato de los JSON. Web puede avanzar con datos de prueba mientras Datos termina cada fuente.

---

## D-004 — El pipeline se escribe en notebooks de marimo

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta

### Qué

Cada fuente es un notebook de [marimo](https://marimo.io) en `pipeline/` que hace todo el recorrido: descargar, validar, mostrar y publicar. Tablas con **polars** y gráficos con **plotly**. El mismo archivo se abre en el navegador para revisar cada paso (`marimo edit`) y se ejecuta sin interfaz en producción (`python <notebook>.py`).

### Por qué

Transparencia: cualquiera del equipo ve qué hace el código y su resultado en cada paso. Un notebook de marimo es un archivo `.py` normal: se versiona bien en Git, se prueba con pytest y se ejecuta en GitHub Actions.

Cambia lo propuesto en `wawapacha.md` §10 (hoy en [`arquitectura.md`](arquitectura.md)): en lugar de «un script Python por fuente» con pandas, cada fuente es un notebook de marimo con polars. xarray se añadirá cuando lleguen las fuentes en rejilla que lo necesiten.

---

## D-005 — APIs gratuitas para lluvia y ríos

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta

### Qué

Añadir al alcance de [D-002](#d-002--alcance-a-fin-de-mes-todas-las-fases-recortadas) dos fuentes servidas por la API gratuita de Open-Meteo:

| Fase | Fuente | Qué aporta |
|---|---|---|
| **v0.2** | [`open-meteo-era5`](fuentes/open-meteo-era5.md) | Lluvia diaria por región (reanálisis ERA5). |
| **v0.3** | [`open-meteo-glofas`](fuentes/open-meteo-glofas.md) | Caudal de ríos **simulado** (GloFAS), mientras no haya caudales observados de SENAMHI o ANA. |

Para OISST (v0.1) se usa el ERDDAP de NCEI, que entrega CSV recortado en el servidor (ver [`noaa-oisst`](fuentes/noaa-oisst.md)).

### Por qué

Son gratuitas, no exigen cuenta y se probaron con datos reales de Piura. Cubren la lluvia por región sin procesar rejillas y son la única vía encontrada para mostrar ríos en la v0.3 sin esperar a las instituciones.

### Condiciones

- Uso solo no comercial, con la atribución que exige CC BY 4.0: «Weather data by Open-Meteo.com» y el crédito a Copernicus (ERA5 o GloFAS).
- El caudal de GloFAS se muestra siempre como **estimado por modelo**, nunca como dato oficial ni como base para alertas.
- Cada punto de río se valida contra una crecida conocida antes de publicarse.
- Cuando SENAMHI o ANA den acceso a datos observados, estos tienen prioridad.
