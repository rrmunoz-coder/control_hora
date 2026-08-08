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

La extracción de índices devolvió 29 filas adicionales a PK/UNIQUE. Dos corresponden a índices internos `SYS_IL...` creados por Oracle para los CLOB `DATOS_ANTERIORES` y `DATOS_NUEVOS` de `GT_AUDITORIA`; por eso no deben recrearse manualmente. Los 27 restantes sí son índices explícitos del modelo.

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

Se detectó un drift en el body productivo de `PKG_GT_ORG_UNIDAD`:

```sql
-- Producción extraída
V_ACTIVO NOT IN ('S','U')

-- Código versionado correcto
V_ACTIVO NOT IN ('S','N')
```

La propia tabla `GT_ORG_UNIDAD` restringe `ACTIVO` a `('S','N')`; por tanto, `U` no es un estado válido. El greenfield debe usar el body versionado con `S/N` y no reproducir este defecto de producción.

## Conclusión

La evidencia recibida permite cerrar el modelo Oracle greenfield de S.2.0. El baseline reproducible queda fijado en 30 tablas, 9 vistas, 3 packages y los catálogos indicados, usando el DDL productivo real salvo la corrección documentada de `PKG_GT_ORG_UNIDAD`.
