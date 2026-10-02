# SENAMHI — estaciones hidrológicas

**ID:** `senamhi-hidro`
**Bloque:** Ríos
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.3
**Revisado:** 2026-09-26

## Qué es

Registros de nivel y/o caudal en estaciones hidrológicas. Aportarían observaciones de ríos para la sección de condiciones actuales.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Servicio Nacional de Meteorología e Hidrología del Perú (SENAMHI) |
| Producto / dataset | Monitoreo Hidrológico a nivel nacional / red de monitoreo hidrológico |
| Variable(s) | Nivel y/o caudal de ríos |
| Unidad | Nivel: unidad por confirmar por estación; caudal: m³/s cuando publicado. |
| Tipo de dato | Observado |
| Página oficial | https://www.senamhi.gob.pe/?p=monitoreo-hidrologico-2 |
| Documentación técnica | https://www.senamhi.gob.pe/?p=informacion-hidrologica-diaria |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú; estaciones hidrológicas nacionales |
| Resolución espacial | Punto de estación |
| Resolución temporal | Observaciones por estación; frecuencia de registro por confirmar. |
| Histórico disponible | Desconocido; la página de monitoreo no confirma un archivo histórico descargable. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Por confirmar; hay reportes hidrológicos diarios por estación. |
| Latencia | Desconocido. |
| Último dato visto | No se descargó dato de estación en esta revisión. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Página/visor web y solicitud de datos |
| URL de descarga | Desconocido; intenté localizar un archivo o servicio de descarga en la página oficial y no quedó confirmado. |
| Formato | HTML/visor; reportes diarios. Archivo estructurado no verificado. |
| Autenticación | Desconocido; solicitudes de información pasan por servicio SENAMHI. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.3. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar; servicio de solicitud de datos puede tener condiciones/costo. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica a observación de nivel/caudal. |
| Umbrales oficiales | Usar solo niveles críticos publicados oficialmente; no establecerlos en esta ficha. |
| Notas metodológicas | La página oficial confirma que el monitoreo hidrológico presenta niveles y/o caudales de la red SENAMHI. Otra página explica que los reportes diarios se emiten por estación e incluyen hidrogramas y niveles críticos. |

## Cómo leer el dato

**Qué es un valor:** una medición por estación de río: el **nivel** del agua (en metros) y, cuando existe, el **caudal** (en m³/s). Los reportes diarios incluyen un hidrograma, es decir, un gráfico de su evolución.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente.

**Para interpretarlo bien:**

- Cada estación tiene sus propios niveles críticos oficiales. Un mismo valor puede ser normal en un río y peligroso en otro.
- No se infiere una alerta a partir del nivel: solo se muestran las que publica la autoridad.
- Un dato de estación representa ese punto del río, no toda la cuenca.

**Conceptos:** [nivel y caudal](../conceptos.md#nivel-y-caudal) · [aviso, alerta y emergencia](../conceptos.md#aviso-alerta-y-emergencia) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- No se probó descarga automatizada de valores ni formato de serie.
- La cobertura no es completa: número de estaciones activas y variables cambian; no verificado.
- No publicar alertas inferidas a partir de datos sin validación.

## Conclusión

Pendiente: la variable y portal de monitoreo están confirmados, pero no se verificó acceso estructurado, histórico, frecuencia por estación, licencia ni costo/condiciones. Solicitar información después del envío institucional previsto.

## Evidencia consultada

- [Monitoreo hidrológico SENAMHI](https://www.senamhi.gob.pe/?p=monitoreo-hidrologico-2)
- [Información hidrológica diaria SENAMHI](https://web2.senamhi.gob.pe/?p=informacion-hidrologica-diaria)
