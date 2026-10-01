# INAIGEM — glaciares, lagunas y aluviones

**ID:** `inaigem`
**Bloque:** Alertas
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.3
**Revisado:** 2026-09-26

## Qué es

Información sobre glaciares, lagunas de origen glaciar y peligros asociados. Puede aportar contexto para riesgos de aludes/aluviones, pero no se confirmó un flujo nacional de alertas vigentes.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Instituto Nacional de Investigación en Glaciares y Ecosistemas de Montaña (INAIGEM) |
| Producto / dataset | Geoportal, Inventario Nacional de Glaciares y Lagunas de Origen Glaciar, estudios de riesgo y monitoreo |
| Variable(s) | Geometría de glaciares/lagunas, características y clasificaciones de riesgo según dataset |
| Unidad | Área, altura y categorías dependen del producto; no se verificó tabla de datos. |
| Tipo de dato | Cartografía/estudio; tipo del feed de alerta no confirmado. |
| Página oficial | https://geoportal.inaigem.gob.pe/ |
| Documentación técnica | https://glaciares.inaigem.gob.pe/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Andes peruanos |
| Resolución espacial | Capas geográficas en geoportal; resolución varía por capa. |
| Resolución temporal | Inventarios/estudios por edición; monitoreo puntual en algunas lagunas. |
| Histórico disponible | Inventario Nacional 2023 disponible como catálogo; histórico sistemático por confirmar. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | No hay frecuencia nacional de alertas confirmada. |
| Latencia | Desconocido. |
| Último dato visto | Geoportal y catálogo de inventario consultados; no se obtuvo dato en tiempo real. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Geoportal interactivo, mapas e informes del repositorio |
| URL de descarga | No se confirmó descarga abierta de las capas desde el geoportal. |
| Formato | Visor web, mapas e informes PDF; formato vectorial descargable por confirmar. |
| Autenticación | Desconocido. |
| Tamaño aproximado | Desconocido. |
| Script de prueba | No aplica: entrega v0.3. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; revisar condiciones por mapa/dataset. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica. |
| Umbrales oficiales | Las clases de riesgo deben conservar su metodología y no combinarse en índice propio. |
| Notas metodológicas | La página del inventario describe glaciares y lagunas y ofrece memoria, mapas y visor. Repositorio y publicaciones describen monitoreo en ciertas lagunas, pero no una alerta pública homogénea nacional. |

## Cómo leer el dato

**Qué es un valor:** el inventario es un mapa de glaciares y lagunas de origen glaciar, con sus características (área, altura) y, en algunos estudios, una clasificación de su peligro. No es un dato que cambie cada día.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente. Se consultó el geoportal y el inventario de 2023.

**Para interpretarlo bien:**

- Una laguna clasificada como peligrosa en un estudio **no** significa que haya una alerta activa hoy.
- Las clases de peligro se muestran con la metodología del estudio que las define, sin combinarlas en un índice propio.
- Solo algunas lagunas tienen monitoreo continuo; la mayoría solo aparece en el inventario.

**Conceptos:** [aviso, alerta y emergencia](../conceptos.md#aviso-alerta-y-emergencia)

## Riesgos

- Inventario cartográfico estático no equivale a alerta activa.
- Cobertura y frecuencia dependen de cada laguna/proyecto.
- Falta verificar capas descargables y licencia.

## Conclusión

Pendiente: hay contenido oficial relevante e inventarios cartográficos, pero falta confirmar si existe un feed público y actualizado de alertas para integrar. Hasta entonces, enlazar estudios oficiales y no anunciar niveles de riesgo propios.

## Evidencia consultada

- [Geoportal INAIGEM](https://geoportal.inaigem.gob.pe/)
- [Inventario Nacional de Glaciares y Lagunas](https://glaciares.inaigem.gob.pe/)
- [Repositorio INAIGEM: monitoreo de lagunas](https://repositorio.inaigem.gob.pe/items/7a1ff38b-5bb2-4f9d-8ee4-242cacce17f8)
