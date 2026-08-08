# Modelo Oracle productivo — ATLAS S.2.0

Extracción DBeaver recibida el 7 de agosto de 2026 y generada con `sql/90_EXTRACCION_VALIDACION_MODELO_PRODUCTIVO_S_2_0.sql`.

## Inventario confirmado

| Objeto | Cantidad |
|---|---:|
| Tablas `GT_*` | 30 |
| Columnas | 310 |
| CHECK / NOT NULL | 311 |
| Primary keys | 30 |
| Foreign keys | 50 |
| Unique constraints | 20 |
| Vistas `VW_GT_*` | 9 |
| Package specs | 3 |
| Package bodies | 3 |
| Índices explícitos adicionales | 27 |
| Secuencias explícitas | 0 |
| Triggers | 0 |

La extracción de índices devolvió 29 filas adicionales a PK/UNIQUE. Dos corresponden a índices internos `SYS_IL...` creados por Oracle para los CLOB `DATOS_ANTERIORES` y `DATOS_NUEVOS` de `GT_AUDITORIA`; no deben recrearse manualmente. Los 27 restantes sí son índices explícitos del modelo.

25 de las 30 tablas utilizan columnas `IDENTITY`; por eso no existen secuencias ATLAS explícitas que deban instalarse. Oracle administra las secuencias internas `ISEQ$$_...`.

## Catálogos base capturados

- `GT_ROL`: 4 registros.
- `GT_PERMISO`: 2 registros.
- `GT_MODALIDAD_DIA`: 12 registros.
- `GT_PARAMETRO`: 3 registros.
- `GT_PARAMETRO_SCORE`: 18 registros.
- `GT_CATEGORIA_COSTO`: 5 registros.

Los IDs identity de esos catálogos no deben forzarse en una instalación nueva. ATLAS resuelve roles, permisos y categorías mediante códigos; los IDs se generan nuevamente en el esquema greenfield.

## Comparación con el código versionado

Las 9 vistas productivas son semánticamente iguales a las definiciones vigentes del repositorio. `PKG_GT_COSTOS` y `PKG_GT_IMPUTACION` también coinciden con su código versionado.

### `PKG_GT_ORG_UNIDAD`: evidencia final

Durante el análisis inicial de la extracción se interpretó erróneamente que el body productivo validaba `V_ACTIVO NOT IN ('S','U')`. La verificación directa posterior contra `USER_SOURCE`, que constituye la evidencia autoritativa del código almacenado en Oracle, confirmó que el body usa correctamente:

```sql
IF V_ACTIVO IS NULL OR V_ACTIVO NOT IN ('S','N') THEN
```

Esto es coherente con la restricción de `GT_ORG_UNIDAD.ACTIVO`, que acepta `S/N`.

Por tanto, **no existe un drift funcional S/U en el estado productivo confirmado** y no debe mantenerse como pendiente.

## Incidente de mantenimiento del 7 de agosto de 2026

Durante las verificaciones del package, el `PACKAGE BODY` quedó temporalmente `INVALID`. La evidencia observada fue:

- `PACKAGE`: `VALID`.
- `PACKAGE BODY`: `INVALID`.
- `USER_ERRORS`: `PLS-00103`, símbolo `end-of-file`, línea 190 posición 22.
- El síntoma es consistente con un body truncado/incompleto.

Se restauró el body completo desde la copia conocida incluida en el snapshot productivo `@@@@@ATLAS.zip`. El archivo restaurado contiene 405 líneas, valida `S/N` y termina en `END PKG_GT_ORG_UNIDAD;`.

Después de la restauración se confirmó:

- `PKG_GT_ORG_UNIDAD / PACKAGE`: `VALID`.
- `PKG_GT_ORG_UNIDAD / PACKAGE BODY`: `VALID`.
- `LAST_DDL_TIME` del body: 2026-08-07 22:50:15 hora local observada en DBeaver.

El artefacto de recuperación quedó versionado como `sql/91_REPARAR_PKG_GT_ORG_UNIDAD.sql`.

## Conclusión

La evidencia recibida permite cerrar el modelo Oracle greenfield de S.2.0. El baseline reproducible queda fijado en 30 tablas, 9 vistas, 3 packages y los catálogos indicados.

El estado final confirmado de `PKG_GT_ORG_UNIDAD` es válido y utiliza `S/N`. Para futuras intervenciones sobre este package debe utilizarse el artefacto completo versionado y validar inmediatamente `USER_OBJECTS` y `USER_ERRORS`.