# ENFEN / IGP — Índice Costero El Niño (ICEN)

**ID:** `enfen-icen`
**Bloque:** ENSO
**Veredicto:** ⏳ Pendiente
**Entrega propuesta:** v0.1
**Revisado:** 2026-09-27

## Qué es

Índice de anomalía de SST en Niño 1+2 utilizado para describir las condiciones cálidas o frías costeras. Es la referencia nacional pertinente para el Niño Costero.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Comisión Multisectorial ENFEN; documentación consultada alojada en el portal de ENFEN/IMARPE |
| Producto / dataset | Índice Costero El Niño (ICEN); se documenta también ICEN temporal (ICENtmp). |
| Variable(s) | SST y anomalía en Niño 1+2 |
| Unidad | °C |
| Tipo de dato | Observado; ICENtmp puede incorporar observaciones semanales y pronósticos según informes ENFEN. |
| Página oficial | https://enfen.imarpe.gob.pe/ |
| Documentación técnica | https://enfen.imarpe.gob.pe/download/nota-tecnica-enfen-01-2024-definicion-operacional-de-los-eventos-el-nino-costero-y-la-nina-costera-en-el-peru/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Región Niño 1+2 frente a la costa de Perú |
| Resolución espacial | Un valor por región |
| Resolución temporal | Mensual; media corrida de tres meses según nota técnica consultada. |
| Histórico disponible | La página del IGP muestra una tabla numérica de valores de ICEN desde 1950; no se confirmó su última fila ni si sigue exactamente la metodología vigente. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | El índice es mensual; la frecuencia de actualización de la tabla y del enlace de descarga está por confirmar. |
| Latencia | Por confirmar; la página IGP y el destino de descarga de SIOFEN no se pudieron recuperar directamente en esta sesión. |
| Último dato visto | Por confirmar; el extracto indexado del IGP confirma valores numéricos, pero no pude verificar la última fila. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Tabla numérica HTML en IGP y página SIOFEN con sección «Descargar datos» |
| URL de descarga | La tabla está en https://met.igp.gob.pe/elnino/lista_eventos.html. SIOFEN anuncia «Descargar datos», pero no pude confirmar la URL ni el formato del archivo. |
| Formato | Tabla HTML de ICEN localizada en el índice del sitio del IGP; formato del archivo ofrecido por SIOFEN por confirmar. |
| Autenticación | No se confirmó un requisito de autenticación; la petición directa al IGP agotó el tiempo y SIOFEN devolvió 403 en esta sesión. |
| Tamaño aproximado | Por confirmar; no se recuperó el archivo de descarga. |
| Script de prueba | No creado: queda confirmar acceso directo y metodología/actualización antes de automatizar. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se localizó licencia de reutilización de la serie. |
| Atribución obligatoria | Por confirmar; no encontré una atribución exacta. |
| Restricciones | Por confirmar; no se encontró una declaración sobre redistribución. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | La página SIOFEN indica climatología 1991–2020 para la serie ICEN allí descrita; su relación con el índice operacional acordado en 2026 está por confirmar. |
| Umbrales oficiales | Por confirmar; la documentación 2024 revisa la definición operativa y ENFEN publicó una nota técnica posterior en 2026. |
| Notas metodológicas | SIOFEN describe una media móvil trimestral de anomalías mensuales de TSM en Niño 1+2 calculadas con ERSSTv5 y climatología 1991–2020. Un informe técnico de ENFEN describe ICENtmp como una estimación transitoria que sustituye faltantes mensuales con observaciones semanales y pronósticos consensuados. La relación con el índice operacional anunciado en abril de 2026 queda por confirmar. |

## Riesgos

- El IGP sí publica una tabla numérica de ICEN; la búsqueda localizó valores desde 1950. El acceso directo a la página agotó el tiempo en esta sesión.
- La página SIOFEN del ICEN muestra una sección «Descargar datos», pero el portal devolvió 403 y no se confirmó el destino, el formato ni la cobertura.
- Hay documentos de distintas versiones/metodologías; fijar versión antes de comparar histórico.
- Licencia y atribución sin confirmar.

## Conclusión

Pendiente: se confirmó que existe una tabla numérica de ICEN en la página del IGP y una sección de descarga en SIOFEN, pero no se verificó una descarga repetible, la última fecha ni la continuidad de metodología. Reintentar acceso a la tabla/archivo y confirmar licencia, atribución y frecuencia antes de asignar ✅. Si la página solo permite una tabla legible por personas, cargar cada actualización mensual con fecha, valor, categoría y enlace de origen, y revisar la transcripción por una segunda persona.

## Evidencia consultada

- [Portal ENFEN](https://enfen.imarpe.gob.pe/)
- [Índice Costero El Niño en SIOFEN](https://siofen.imarpe.gob.pe/nivel2/indice-costero-el-nino-icen)
- [Tabla de ICEN del IGP](https://met.igp.gob.pe/elnino/lista_eventos.html)
- [Nota técnica ENFEN sobre definición operacional y serie histórica](https://enfen.imarpe.gob.pe/download/nota-tecnica-enfen-01-2024-definicion-operacional-de-los-eventos-el-nino-costero-y-la-nina-costera-en-el-peru/)
- [Informe técnico ENFEN que describe ICENtmp](https://enfen.imarpe.gob.pe/download/informe-tecnico-2014-7/)
- [Nota de prensa ENFEN N.° 01-2026 sobre el índice operacional](https://enfen.imarpe.gob.pe/notas-tecnicas/)
