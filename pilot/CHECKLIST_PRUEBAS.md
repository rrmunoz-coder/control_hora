# Checklist de pruebas — ATLAS Conocimiento v0.4 piloto

Registra resultado como `OK`, `ERROR` o `NO PROBADO`.

## A. Aislamiento y regresión

| Prueba | Esperado | Resultado |
|---|---|---|
| `http://claroprod985:5050` abre | Producción normal | |
| `http://claroprod985:5051` abre | Piloto normal | |
| Login 5050 y 5051 simultáneos | No se pisan las sesiones | |
| Dashboard 5051 | Igual a ATLAS actual | |
| Tareas 5051 | Lista normal | |
| Proyectos 5051 | Lista normal | |
| Imputaciones 5051 | Operación/lectura normal | |

## B. ADMIN

| Prueba | Esperado | Resultado |
|---|---|---|
| Abrir Biblioteca de conocimiento | Acceso permitido | |
| Crear PROCEDIMIENTO INTERNO | Queda BORRADOR v1 | |
| Definir unidad y revisor | Guarda correctamente | |
| Editar borrador | Genera v2, conserva v1 | |
| Enviar a revisión | Estado EN_REVISION | |
| Publicar | Estado PUBLICADO | |
| Intentar editar PUBLICADO directamente | No ofrece edición | |
| Marcar requiere actualización | Estado REQUIERE_ACTUALIZACION | |
| Abrir nueva revisión | Vuelve a BORRADOR | |
| Marcar obsoleto | Estado OBSOLETO | |
| Buscar por título | Encuentra documento | |
| Filtrar por tipo/estado | Resultado coherente | |

## C. JEFE

Usa un JEFE asociado a una unidad y sus descendientes.

| Prueba | Esperado | Resultado |
|---|---|---|
| Ver documento de su unidad | Permitido | |
| Ver documento de unidad fuera de alcance | Denegado/no listado | |
| Revisar/publicar documento dentro de alcance | Permitido según flujo | |
| Crear documento en unidad accesible | Permitido | |
| Crear documento fuera de alcance manipulando ID | Backend debe rechazar | |

## D. USUARIO

| Prueba | Esperado | Resultado |
|---|---|---|
| Ver PUBLICADO + INTERNO de su unidad | Permitido | |
| Ver BORRADOR ajeno | No listado/denegado | |
| Ver RESTRINGIDO ajeno | No listado/denegado | |
| Ver CONFIDENCIAL ajeno | No listado/denegado | |
| Ver documento de otra unidad | Denegado | |
| Editar su propio BORRADOR | Permitido | |
| Editar su PUBLICADO directamente | Denegado | |

## E. Auditoría y datos

Después de crear/editar/cambiar estados, revisar:

```sql
SELECT ID_AUDITORIA, ID_USUARIO, MODULO, ENTIDAD, ID_ENTIDAD, ACCION, FECHA_EVENTO
FROM GT_AUDITORIA
WHERE MODULO = 'CONOCIMIENTO'
ORDER BY ID_AUDITORIA DESC;
```

Y versionado:

```sql
SELECT ID_CONOCIMIENTO, NUMERO_VERSION, TITULO, ESTADO_ORIGEN, MOTIVO_CAMBIO, FECHA_VERSION
FROM GT_CONOCIMIENTO_VERSION
ORDER BY ID_CONOCIMIENTO, NUMERO_VERSION;
```

Debe existir una fila de versión por cada creación/edición, sin sobrescribir versiones previas.

## F. Criterio de salida del piloto

No promover a `main` hasta tener:

- regresión 5050 sin impacto;
- ADMIN, JEFE y USUARIO aprobados;
- autorización horizontal probada;
- flujo y versionado aprobados;
- cero errores Oracle en el SQL 71;
- logs sin excepciones no controladas;
- CI del PR en verde.

Los adjuntos físicos siguen fuera de esta fase y no forman parte del criterio de aceptación actual.
