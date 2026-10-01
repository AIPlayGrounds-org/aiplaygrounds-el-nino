# ENFEN — comunicados oficiales

**ID:** `enfen-comunicado`
**Bloque:** Pronósticos
**Veredicto:** ✍️ Carga manual
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Publicaciones oficiales que informan el estado del sistema de alerta y resumen condiciones observadas y pronósticos para Niño 1+2 y Niño 3.4. WawaPacha puede enlazar el comunicado y mostrar su estado con revisión humana.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Comisión Multisectorial ENFEN |
| Producto / dataset | Comunicado Oficial ENFEN |
| Variable(s) | Estado del sistema de alerta, diagnóstico y pronósticos ENSO/El Niño Costero |
| Unidad | Categorías de alerta y magnitud; probabilidades cuando se publican. |
| Tipo de dato | Pronóstico y diagnóstico |
| Página oficial | https://enfen.imarpe.gob.pe/downloads/comunicados/ |
| Documentación técnica | https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú y regiones Niño 1+2 y 3.4 |
| Resolución espacial | Áreas y regiones descritas por comunicado; varía por edición. |
| Resolución temporal | Publicación por emisión, no serie regular de observaciones. |
| Histórico disponible | Archivo de comunicados con ediciones previas; extensión exacta no verificada. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Irregular, asociada a nuevas evaluaciones y comunicados; en el archivo consultado hubo publicaciones con intervalos de alrededor de dos semanas. |
| Latencia | Desconocido; depende de la fecha de emisión. |
| Último dato visto | Comunicado Oficial ENFEN N.° 16-2026, publicado el 14-09-2026; informa estado de alerta y pronóstico. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Página HTML y versión PDF enlazada |
| URL de descarga | https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/ |
| Formato | HTML/PDF |
| Autenticación | Ninguna observada |
| Tamaño aproximado | El archivo del comunicado 16-2026 figura con 905,10 KB en el archivo de descargas. |
| Script de prueba | No aplica: la propuesta es revisar y registrar manualmente cada nueva emisión. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se localizó licencia del contenido del comunicado. |
| Atribución obligatoria | Por confirmar; atribuir a ENFEN y enlazar la publicación original es una práctica recomendada, no una exigencia confirmada. |
| Restricciones | Por confirmar; no se encontró permiso de reutilización explícito. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica como boletín; las series y anomalías que incluya pueden tener sus propias referencias. |
| Umbrales oficiales | Usar las categorías declaradas por ENFEN en cada comunicado; no inferir umbrales. |
| Notas metodológicas | El archivo lista comunicados numerados y la página de cada uno expone texto y PDF. La emisión 16-2026 indica el estado de alerta en el HTML. |

## Cómo leer el dato

**Qué es un valor:** cada comunicado es un documento con tres partes: el **estado del sistema de alerta** (la categoría oficial vigente), un **diagnóstico** de las condiciones actuales y un **pronóstico**. WawaPacha toma el estado, la fecha de emisión y el enlace al original.

**Ejemplo:** el último comunicado consultado fue el N.° 17-2026, publicado el 28-09-2026; el anterior, el N.° 16-2026, el 14-09-2026. Su contenido no se transcribe aquí.

**Para interpretarlo bien:**

- El estado vale hasta el siguiente comunicado. Se publican aproximadamente cada dos semanas.
- Se copia el nombre exacto del estado que use ENFEN (por ejemplo, de vigilancia o de alerta ante El Niño Costero), sin resumirlo ni traducirlo a colores propios.
- Un estado de alerta de ENFEN no es un aviso meteorológico ni un reporte de emergencia.
- El pronóstico del comunicado es la opinión oficial peruana. No se promedia con el de NOAA ni con otros.

**Conceptos:** [aviso, alerta y emergencia](../conceptos.md#aviso-alerta-y-emergencia) · [El Niño Costero](../conceptos.md#el-niño-costero) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- Los comunicados son documentos editoriales y pueden cambiar de estructura.
- La extracción automática del estado y pronóstico no se probó; requiere revisión para evitar mostrar un estado desactualizado.

## Conclusión

Carga manual por publicación: una persona revisa la nueva emisión, captura estado/fecha, enlaza el original y confirma vigencia. Frecuencia según emisión; esfuerzo no cronometrado.

## Evidencia consultada

- [Archivo oficial de comunicados ENFEN](https://enfen.imarpe.gob.pe/downloads/comunicados/)
- [Comunicado Oficial ENFEN 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/)
