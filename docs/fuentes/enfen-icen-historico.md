# ENFEN — ICEN histórico

**ID:** `enfen-icen-historico`
**Bloque:** Histórico
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.4
**Revisado:** 2026-09-27

## Qué es

Serie del Índice Costero El Niño para contextualizar episodios costeros históricos. La nota técnica de ENFEN presenta una figura que abarca 1950–2024.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Comisión Multisectorial ENFEN |
| Producto / dataset | ICEN histórico y cronología de eventos costeros |
| Variable(s) | ICEN mensual/anomalía SST en Niño 1+2 |
| Unidad | °C |
| Tipo de dato | Análisis observado/reconstruido; método por confirmar según versión. |
| Página oficial | https://enfen.imarpe.gob.pe/ |
| Documentación técnica | https://enfen.imarpe.gob.pe/download/nota-tecnica-enfen-01-2024-definicion-operacional-de-los-eventos-el-nino-costero-y-la-nina-costera-en-el-peru/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Región Niño 1+2 frente al Perú |
| Resolución espacial | Un índice por región |
| Resolución temporal | Mensual, promedios móviles descritos en metodología. |
| Histórico disponible | La página del IGP expone una tabla numérica de ICEN con valores desde 1950; el índice del sitio no permitió comprobar su última fila. La nota técnica ENFEN muestra una figura 1950–2024. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Histórico publicado en nota técnica; actualización futura por confirmar. |
| Latencia | No aplica a documento histórico. |
| Último dato visto | Por confirmar. Se verificó en el índice de la página del IGP que existe una tabla numérica desde 1950, pero no pude leer la última fila. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Tabla numérica HTML en la página del IGP; nota técnica y figura ENFEN como documentación |
| URL de descarga | https://met.igp.gob.pe/elnino/lista_eventos.html. SIOFEN también presenta «Descargar datos», pero no se verificó el destino ni su formato. |
| Formato | Tabla HTML numérica localizada por el índice del IGP; no se confirmó un archivo CSV/XLSX separado. |
| Autenticación | No se confirmó requisito; la consulta directa al IGP agotó el tiempo y la página SIOFEN devolvió 403 en esta sesión. |
| Tamaño aproximado | Por confirmar; la descarga no se pudo recuperar. |
| Script de prueba | No aplica: entrega v0.4. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; revisar licencia de documento y datos. |
| Atribución obligatoria | Por confirmar. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | Según versión de metodología del ICEN; confirmar cada base. |
| Umbrales oficiales | Categorías de eventos pueden cambiar al aplicar nueva metodología; consultar el documento vigente. |
| Notas metodológicas | La Nota Técnica 01-2024 indica que sustituye la definición anterior y presenta cronología 1950–2024. El IGP expone además una tabla numérica, pero su última fila y su correspondencia con la metodología descrita por SIOFEN deben confirmarse. |

## Riesgos

- La tabla numérica del IGP existe, pero su recuperación automatizada no quedó probada; no transcribir desde la figura ENFEN si se puede usar la tabla.
- SIOFEN describe ICEN mensual con ERSSTv5 y climatología 1991–2020; la equivalencia de la tabla histórica del IGP con esa metodología debe comprobarse.
- La metodología vigente puede revisar la cronología de eventos históricos; ENFEN publicó una nota sobre un índice operacional en abril de 2026.
- Puede duplicar al ICEN de v0.1.

## Conclusión

Pendiente: se encontró una tabla numérica histórica de ICEN en la página del IGP, además de la figura 1950–2024 de ENFEN; no se verificó una descarga repetible ni la equivalencia de metodología. Mantener el recurso pendiente hasta comprobar acceso y decidir si se conservará la serie del IGP o la serie histórica de ENFEN. Si solo quedara la figura/PDF para un periodo concreto, una persona podría digitalizar los puntos y otra revisarlos contra los ejes y valores publicados, registrando que son estimaciones.

## Evidencia consultada

- [Nota técnica ENFEN: definición operacional y serie 1950–2024](https://enfen.imarpe.gob.pe/download/nota-tecnica-enfen-01-2024-definicion-operacional-de-los-eventos-el-nino-costero-y-la-nina-costera-en-el-peru/)
- [Índice Costero El Niño en SIOFEN](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen)
- [Tabla numérica del ICEN en IGP](https://met.igp.gob.pe/elnino/lista_eventos.html)
- [Nota de prensa ENFEN N.° 01-2026 sobre el índice operacional](https://enfen.imarpe.gob.pe/notas-tecnicas/)
