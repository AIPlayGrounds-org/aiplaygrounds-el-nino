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

Otros índices (incluido el ICEN peruano), mapas, pronósticos, alertas, resumen con IA y el resto de secciones de [`wawapacha.md`](wawapacha.md). Se abordan después, una por una.

### Terminado cuando

- [ ] Existe un documento con las reglas de calidad y procesamiento de datos.
- [ ] Un script descarga el ONI, lo valida y lo guarda como JSON, con un test.
- [ ] La web muestra el gráfico con fuente, unidad, fecha y tipo de dato.
- [ ] El trabajo está en `main` mediante un PR revisado.

---

## D-002 — Alcance a fin de mes: todas las fases, recortadas

- **Fecha:** 2026-10-01
- **Estado:** 🟡 Propuesta
- **Plazo:** 2026-10-31

### Qué

Las cuatro fases de [`wawapacha.md` §11](wawapacha.md#11-plan-por-fases-propuesta) se publican antes del 31 de octubre, pero cada una **solo con las fuentes que ya se pueden obtener sin depender de una institución**. El veredicto de cada fuente está en [`fuentes/`](fuentes/README.md).

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
