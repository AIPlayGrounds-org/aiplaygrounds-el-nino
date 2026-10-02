# SENAMHI — avisos meteorológicos

**ID:** `senamhi-avisos`
**Bloque:** Alertas
**Veredicto:** ✅ Automatizable
**Entrega propuesta:** v0.3
**Revisado:** 2026-10-01

## Qué es

Avisos preventivos oficiales que indican fenómenos meteorológicos severos, áreas potencialmente afectadas, periodo de vigencia y nivel de peligro. Se ajustan a la regla de WawaPacha de enlazar alertas oficiales.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Servicio Nacional de Meteorología e Hidrología del Perú (SENAMHI) |
| Producto / dataset | Avisos Meteorológicos a nivel nacional |
| Variable(s) | Fenómeno, zonas, fecha de emisión, inicio/fin, duración y nivel de peligro |
| Unidad | Categoría (amarillo/naranja/rojo), fechas y horas |
| Tipo de dato | Pronóstico/aviso preventivo |
| Página oficial | https://www.senamhi.gob.pe/?p=aviso-meteorologico |
| Documentación técnica | https://www.senamhi.gob.pe/?p=aviso-meteorologico |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú |
| Resolución espacial | Áreas descritas por aviso; los detalles incluyen regiones/localidades. |
| Resolución temporal | Por evento, duración en horas/días |
| Histórico disponible | La página actual lista avisos de 2021 a 2026. Los de 2003 a 2020 están en un archivo aparte: https://web2.senamhi.gob.pe/?p=avisos |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Por evento, con múltiples avisos y actualizaciones en días activos. |
| Latencia | No definido; emisión antes del periodo de vigencia. |
| Último dato visto | Aviso N.° 392 (precipitaciones en la sierra norte y costa norte), emitido el 2026-09-30, vigente del 2026-10-02 al 2026-10-04, nivel naranja. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | HTML con tabla de avisos y páginas de detalle |
| URL de descarga | https://www.senamhi.gob.pe/?p=aviso-meteorologico |
| Formato | HTML; la tabla muestra fenómeno, número, estado (emitido/vigente), emisión, inicio, fin, duración y nivel. |
| Autenticación | Ninguna observada |
| Tamaño aproximado | Unos 1,2 MB por descarga de la página completa (2026-10-01). |
| Script de prueba | No aplica: entrega v0.3; se confirma viabilidad a nivel de página, sin spike según guía. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se localizó licencia explícita de reutilización de avisos. |
| Atribución obligatoria | Por confirmar; atribuir a SENAMHI y enlazar el aviso original. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica. |
| Umbrales oficiales | El SENAMHI asigna los niveles del aviso; no reetiquetar. |
| Notas metodológicas | La página oficial describe avisos como pronósticos preventivos y expone una tabla HTML, además de páginas de detalle con vigencia y áreas. Automatización plausible por HTML, no API confirmada. |

## Cómo leer el dato

**Qué es un valor:** cada fila es un aviso con su fenómeno, número, estado, fecha de emisión, inicio y fin de vigencia, duración y nivel de peligro: amarillo, naranja o rojo, de menor a mayor.

**Ejemplo:** el aviso N.° 392 (precipitaciones en la sierra norte y costa norte) se emitió el 2026-09-30, rige del 2026-10-02 al 2026-10-04 y tiene nivel naranja.

**Para interpretarlo bien:**

- El estado indica si el aviso está **emitido** (publicado, aún no empieza) o **vigente** (en curso). En la consulta del 2026-10-01, los avisos sin estado eran los que ya habían terminado; hay que confirmarlo antes de automatizar, y nunca mostrarlos como activos.
- La numeración vuelve a empezar cada año: el número no basta para identificar un aviso, hace falta también el año.
- Algunos avisos actualizan o extienden otro anterior; el título lo indica (por ejemplo, «actualización del aviso N.° 265»).
- Un aviso meteorológico no implica que el fenómeno se deba a El Niño. No se atribuyen causas.

**Conceptos:** [aviso, alerta y emergencia](../conceptos.md#aviso-alerta-y-emergencia) · [tipos de dato](../conceptos.md#tipos-de-dato)

## Riesgos

- No confundir con `web2.senamhi.gob.pe/?p=avisos`: es un archivo histórico que termina en diciembre de 2020 y reinicia la numeración cada año, así que un número de aviso no basta para identificar su fecha.
- El HTML puede cambiar; validar que la tabla tenga las columnas esperadas.
- Nunca tratar aviso vencido como vigente; conservar estado y periodo original.
- No extraer ni crear un índice propio de riesgo.

## Conclusión

Automatizable a nivel de ficha de viabilidad: la lista HTML actual tiene campos estructurados, incluido el estado de cada aviso, y se actualiza (último aviso del 2026-09-30). Las páginas de detalle contienen el aviso oficial. Antes de producción, definir el enlace a cada aviso y la estrategia de caducidad; la interfaz debe mostrar fechas y enlazar a SENAMHI.

## Evidencia consultada

- [Avisos meteorológicos SENAMHI](https://www.senamhi.gob.pe/?p=aviso-meteorologico)
- [Archivo histórico de avisos 2003–2020](https://web2.senamhi.gob.pe/?p=avisos)
- [Ejemplo de detalle oficial de aviso](https://www.senamhi.gob.pe/servicios/?a=2026&b=27502&c=00&d=SENA&p=aviso-meteorologico-detalle)
