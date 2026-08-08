# Oracle greenfield — ATLAS S.2.0

Fuente de verdad: extracción real del esquema productivo `SCBILL`, recibida el 7 de agosto de 2026.

## Baseline confirmado

- 30 tablas `GT_*` y 310 columnas.
- 311 CHECK/NOT NULL, 30 PK, 50 FK y 20 UNIQUE.
- 9 vistas `VW_GT_*`.
- 3 package specs y 3 package bodies.
- 27 índices explícitos adicionales; los 2 `SYS_IL...` observados son internos de los CLOB de `GT_AUDITORIA`.
- Sin secuencias ATLAS explícitas ni triggers; 25 tablas usan `IDENTITY`.
- Catálogos base capturados: roles, permisos, modalidades, parámetros, parámetros de score y categorías de costo.

## Drift detectado

El body productivo de `PKG_GT_ORG_UNIDAD` contiene `V_ACTIVO NOT IN ('S','U')`, mientras que la tabla admite únicamente `S/N` y el código versionado correcto contiene `('S','N')`. Una instalación nueva no debe reproducir el valor `U`.

## Validación

Después de instalar el modelo ejecutar en DBeaver:

`01_VALIDAR_ATLAS_GREENFIELD_S_2_0.sql`

El validador controla cantidades de objetos/constraints/índices, catálogos, objetos inválidos, errores de compilación y bloqueos de login.

La evidencia detallada está en `docs/MODELO_ORACLE_PRODUCTIVO_S_2_0.md`.
