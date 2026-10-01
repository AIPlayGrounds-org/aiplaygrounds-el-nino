# INDECI / COEN — emergencias y reportes

**ID:** `indeci-coen`
**Bloque:** Alertas
**Veredicto:** ✍️ Carga manual
**Entrega propuesta:** v0.3
**Revisado:** 2026-09-26

## Qué es

Reportes oficiales de emergencias y peligros difundidos por el Centro de Operaciones de Emergencia Nacional. Aportan seguimiento de eventos ya reportados, no un pronóstico meteorológico.

## Identidad

| Campo | Valor |
|---|---|
| Institución | Instituto Nacional de Defensa Civil (INDECI), Centro de Operaciones de Emergencia Nacional (COEN) |
| Producto / dataset | Emergencias COEN: reportes preliminares, complementarios e informes |
| Variable(s) | Evento, ubicación, cronología y afectaciones según informe |
| Unidad | Conteos/unidades por reporte; estructura variable. |
| Tipo de dato | Reporte observado |
| Página oficial | https://portal.indeci.gob.pe/emergencias/ |
| Documentación técnica | https://portal.indeci.gob.pe/coen/nosotros/ |

## Cobertura

| Campo | Valor |
|---|---|
| Cobertura espacial | Perú |
| Resolución espacial | Localidad/distrito/provincia según reporte |
| Resolución temporal | Eventos puntuales; actualización durante evolución de cada emergencia. |
| Histórico disponible | El archivo presenta decenas de miles de registros; cobertura histórica exacta por confirmar. |

## Frescura

| Campo | Valor |
|---|---|
| Frecuencia de publicación | Durante emergencias; la portada muestra muchos reportes por día. |
| Latencia | No fija; coordinación y reporte de autoridades. |
| Último dato visto | El archivo consultado listaba reportes del 2026-08-23; página dinámica, no verificada para 2026-09-26. |

## Acceso

| Campo | Valor |
|---|---|
| Tipo | Archivo HTML con descarga de reportes, generalmente PDF |
| URL de descarga | https://portal.indeci.gob.pe/emergencias/ |
| Formato | HTML/PDF |
| Autenticación | Ninguna observada |
| Tamaño aproximado | Varía por reporte; no medido. |
| Script de prueba | No aplica: entrega v0.3. |

## Uso

| Campo | Valor |
|---|---|
| Licencia | Por confirmar; no se localizó licencia de reutilización de los reportes. |
| Atribución obligatoria | Por confirmar; citar número, fecha y COEN/INDECI. |
| Restricciones | Por confirmar. |

## Ciencia

| Campo | Valor |
|---|---|
| Periodo base de la anomalía | No aplica. |
| Umbrales oficiales | No aplica; son reportes de eventos/emergencias. |
| Notas metodológicas | INDECI describe al COEN como órgano que monitorea, valida y comunica información oficial las 24 h. El archivo público lista reportes y enlaces de descarga; los documentos son narrativos y de actualización frecuente. |

## Riesgos

- El volumen es alto y el estado se actualiza por reporte complementario.
- No es un catálogo limpio de alertas; leer informes exige contexto.
- Mostrar sin selección podría saturar el módulo y confundir peligro con emergencia.

## Conclusión

Carga manual selectiva solo si el producto decide mostrar reportes de impacto: curar eventos relevantes, conservar número/fecha/enlace y revisar complementarios. Frecuencia durante eventos; esfuerzo no medido y probablemente alto. No usarlo como alerta predictiva.

## Evidencia consultada

- [Archivo de emergencias COEN](https://portal.indeci.gob.pe/emergencias/)
- [Descripción institucional del COEN](https://portal.indeci.gob.pe/coen/nosotros/)
