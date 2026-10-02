# ENFEN — pronóstico

**ID:** `enfen-pronostico`
**Bloque:** Pronósticos
**Veredicto:** ❌ Descartar
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-26

## Qué es

Pronósticos peruanos para El Niño Costero y Niño 3.4 publicados dentro de comunicados oficiales ENFEN. El contenido está cubierto por la ficha de comunicados.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Comisión Multisectorial ENFEN |
| Producto / dataset | Pronóstico ENFEN difundido en Comunicados Oficiales |
| Variable(s) | Estado futuro y magnitud probable del fenómeno por región |
| Unidad | Categorías y probabilidades según comunicado. |
| Tipo de dato | Pronóstico |
| Página oficial | https://enfen.imarpe.gob.pe/downloads/comunicados/ |
| Documentación técnica | https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú; regiones Niño 1+2 y 3.4 según emisión |
| Resolución espacial | Por región descrita en el comunicado |
| Resolución temporal | Horizontes de meses, variables por emisión. |
| Histórico disponible | Archivo de comunicados; histórico de series no se investigó aquí. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Se publica con cada comunicado, no como producto independiente confirmado. |
| Latencia | Depende de emisión. |
| Último dato visto | Pronóstico incluido en el comunicado ENFEN N.° 16-2026, 14-09-2026. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTML y PDF dentro del comunicado |
| URL de descarga | No se localizó un archivo separado del comunicado. |
| Formato | HTML/PDF |
| Autenticación | Ninguna observada |
| Tamaño aproximado | Ver ficha `enfen-comunicado`; el tamaño varía por edición. |
| Script de prueba | No aplica: fuente duplicada. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; misma incertidumbre que en comunicados ENFEN. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Por confirmar según variable pronosticada. |
| Umbrales oficiales | Usar categorías explícitas de ENFEN en cada edición. |
| Notas metodológicas | La página y el comunicado 16-2026 contienen texto de estado y pronóstico; no se halló un producto de pronóstico separado. |

## Cómo leer el dato

**Qué es un valor:** el pronóstico ENFEN se publica dentro de cada comunicado oficial, con la magnitud esperada de El Niño Costero y del Pacífico central para los próximos meses.

**Ejemplo:** ver la ficha [`enfen-comunicado`](enfen-comunicado.md).

**Para interpretarlo bien:**

- Se lee en el comunicado, junto con su fecha de emisión. Un pronóstico de un comunicado antiguo ya no es el vigente.
- Si incluye probabilidades por magnitud, se leen como cualquier pronóstico probabilístico: no indican impactos concretos.

**Conceptos:** [pronóstico probabilístico](../conceptos.md#pronóstico-probabilístico) · [El Niño Costero](../conceptos.md#el-niño-costero) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- Duplicaría la ficha y captura manual de `enfen-comunicado`.
- El pronóstico cambia entre comunicados.

## Conclusión

Descartar como fuente independiente y mantener como campo/contenido de `enfen-comunicado`; así se evita duplicar la ingesta y conservar la fecha original de cada pronóstico.

## Evidencia consultada

- [Archivo de comunicados ENFEN](https://enfen.imarpe.gob.pe/downloads/comunicados/)
- [Comunicado Oficial ENFEN 16-2026](https://enfen.imarpe.gob.pe/download/comunicado-oficial-enfen-n-16-2026/)
