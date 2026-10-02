# DHN — boletines oceanográficos

**ID:** `dhn-boletines`
**Bloque:** SST
**Veredicto:** ✍️ Carga manual
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Boletines de la Dirección de Hidrografía y Navegación sobre condiciones oceanográficas y meteorológicas en el Pacífico ecuatorial y el mar peruano. Aportan contexto local y observaciones descritas en documentos.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Dirección de Hidrografía y Navegación (DIHIDRONAV), Marina de Guerra del Perú |
| Producto / dataset | Boletín Oceanográfico Mensual / Boletín Océano Atmosférico Mensual |
| Variable(s) | SST, anomalías y condiciones oceánicas; variables concretas dependen del boletín. |
| Unidad | °C para SST; otros elementos varían. |
| Tipo de dato | Observado y análisis |
| Página oficial | https://www.dhn.mil.pe/portal/boletin-oceanografico-mensual |
| Documentación técnica | https://www.dhn.mil.pe/Archivos/Oceanografia/BOM/03-2025.pdf |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Pacífico ecuatorial y mar peruano |
| Resolución espacial | Mapas regionales y perfiles frente a estaciones/costa; resolución exacta depende del boletín. |
| Resolución temporal | Boletín mensual; algunos boletines oceanográficos son diarios. |
| Histórico disponible | El archivo web consultado incluye ediciones al menos desde 2022; cobertura completa desconocida. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Mensual para BOM; el portal tiene una colección separada de boletines diarios. |
| Latencia | No definida; publicación por edición. |
| Último dato visto | El índice consultado listaba BOM hasta julio de 2026. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Visor web con documentos PDF descargables |
| URL de descarga | https://www.dhn.mil.pe/portal/boletin-oceanografico-mensual |
| Formato | PDF |
| Autenticación | Ninguna observada |
| Tamaño aproximado | Por confirmar; varía por edición. |
| Script de prueba | No aplica: el contenido requiere revisión/extracción de documentos. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se encontró licencia en el índice de boletines. |
| Atribución obligatoria | Por confirmar; citar edición y enlace original como mínimo operativo. |
| Restricciones | Por confirmar; no se hallaron términos de redistribución. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Las anomalías se describen en cada publicación; periodo base por confirmar. |
| Umbrales oficiales | Por confirmar; no extraer categorías sin revisar metodología del producto. |
| Notas metodológicas | La colección enlaza ediciones por mes. La página identifica el producto como boletín mensual y un PDF consultado informa su alcance oceánico. |

## Cómo leer el dato

**Qué es un valor:** cada boletín es un PDF mensual con mapas, gráficos y textos sobre el mar peruano: temperatura, anomalías y otras variables, según la edición.

**Ejemplo:** Todavía no hay ejemplo: no se ha descargado ningún dato de esta fuente. El índice consultado listaba boletines hasta julio de 2026.

**Para interpretarlo bien:**

- Cada edición dice qué periodo, variable, unidad y periodo base usa. Hay que leerlos en el propio boletín antes de transcribir un valor.
- Los valores son análisis de la DHN. No se mezclan con los de NOAA sin explicar las diferencias de método.
- Por su frecuencia mensual, da contexto, no información para alertas.

**Conceptos:** [SST](../conceptos.md#temperatura-superficial-del-mar-sst) · [anomalía](../conceptos.md#anomalía) · [periodo base](../conceptos.md#periodo-base)

## Riesgos

- El PDF puede cambiar de diagramación o tratamiento de las figuras.
- Frecuencia adecuada para contexto mensual, no para alertas de vigencia diaria.

## Conclusión

Carga manual una vez por cada nueva edición mensual: revisar cifras, unidad y periodo, transcribir únicamente indicadores necesarios y enlazar el PDF. Tiempo de carga no medido; no usar como fuente de alertas en tiempo real.

## Evidencia consultada

- [Archivo de boletines oceanográficos mensuales](https://www.dhn.mil.pe/portal/boletin-oceanografico-mensual)
- [Ejemplo de boletín mensual DHN](https://www.dhn.mil.pe/Archivos/Oceanografia/BOM/03-2025.pdf)
