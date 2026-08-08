/* ============================================================
   ATLAS S.2.0
   EXTRACCION COMPLETA DE MODELO ORACLE PARA GREENFIELD
   Compatible con DBeaver / Oracle

   Objetivo:
   - Inventariar el esquema ATLAS real.
   - Extraer DDL de tablas, índices, secuencias, triggers, vistas
     y packages.
   - Recuperar constraints, columnas y dependencias.
   - Extraer catálogos base necesarios para una instalación nueva.

   Ejecución recomendada en DBeaver:
   Execute SQL Script sobre el archivo completo.
   ============================================================ */


/* ============================================================
   01 - INVENTARIO DE OBJETOS ATLAS
   ============================================================ */

SELECT
    OBJECT_TYPE,
    OBJECT_NAME,
    STATUS,
    CREATED,
    LAST_DDL_TIME
FROM USER_OBJECTS
WHERE (
       OBJECT_NAME LIKE 'GT\_%' ESCAPE '\'
    OR OBJECT_NAME LIKE 'VW\_GT\_%' ESCAPE '\'
    OR OBJECT_NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
)
ORDER BY OBJECT_TYPE, OBJECT_NAME;


/* ============================================================
   02 - DDL DE TABLAS
   Incluye columnas y constraints embebidos por DBMS_METADATA.
   ============================================================ */

SELECT
    'TABLE' AS TIPO_OBJETO,
    TABLE_NAME AS NOMBRE_OBJETO,
    DBMS_METADATA.GET_DDL(
        'TABLE',
        TABLE_NAME,
        USER
    ) AS DDL
FROM USER_TABLES
WHERE TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
ORDER BY TABLE_NAME;


/* ============================================================
   03 - INDICES
   Excluye los índices gestionados directamente por PK/UNIQUE.
   ============================================================ */

SELECT
    'INDEX' AS TIPO_OBJETO,
    I.TABLE_NAME,
    I.INDEX_NAME AS NOMBRE_OBJETO,
    I.UNIQUENESS,
    DBMS_METADATA.GET_DDL(
        'INDEX',
        I.INDEX_NAME,
        USER
    ) AS DDL
FROM USER_INDEXES I
WHERE I.TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
  AND NOT EXISTS (
        SELECT 1
        FROM USER_CONSTRAINTS C
        WHERE C.INDEX_NAME = I.INDEX_NAME
          AND C.CONSTRAINT_TYPE IN ('P', 'U')
  )
ORDER BY I.TABLE_NAME, I.INDEX_NAME;


/* ============================================================
   04 - CONSTRAINTS
   P = PRIMARY KEY
   R = FOREIGN KEY
   U = UNIQUE
   C = CHECK / NOT NULL
   ============================================================ */

SELECT
    C.TABLE_NAME,
    C.CONSTRAINT_NAME,
    C.CONSTRAINT_TYPE,
    C.STATUS,
    C.R_CONSTRAINT_NAME,
    C.DELETE_RULE,
    C.SEARCH_CONDITION_VC
FROM USER_CONSTRAINTS C
WHERE C.TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
ORDER BY
    C.TABLE_NAME,
    C.CONSTRAINT_TYPE,
    C.CONSTRAINT_NAME;


/* ============================================================
   05 - COLUMNAS DE CONSTRAINTS
   Permite reconstruir PK, FK y UNIQUE en el orden correcto.
   ============================================================ */

SELECT
    CC.TABLE_NAME,
    CC.CONSTRAINT_NAME,
    CC.COLUMN_NAME,
    CC.POSITION
FROM USER_CONS_COLUMNS CC
WHERE CC.TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
ORDER BY
    CC.TABLE_NAME,
    CC.CONSTRAINT_NAME,
    CC.POSITION;


/* ============================================================
   06 - SECUENCIAS ATLAS
   ============================================================ */

SELECT
    'SEQUENCE' AS TIPO_OBJETO,
    SEQUENCE_NAME AS NOMBRE_OBJETO,
    DBMS_METADATA.GET_DDL(
        'SEQUENCE',
        SEQUENCE_NAME,
        USER
    ) AS DDL
FROM USER_SEQUENCES
WHERE (
       SEQUENCE_NAME LIKE 'GT\_%' ESCAPE '\'
    OR SEQUENCE_NAME LIKE 'SEQ\_GT\_%' ESCAPE '\'
)
ORDER BY SEQUENCE_NAME;


/* ============================================================
   07 - TRIGGERS SOBRE TABLAS ATLAS
   ============================================================ */

SELECT
    'TRIGGER' AS TIPO_OBJETO,
    TABLE_NAME,
    TRIGGER_NAME AS NOMBRE_OBJETO,
    STATUS,
    DBMS_METADATA.GET_DDL(
        'TRIGGER',
        TRIGGER_NAME,
        USER
    ) AS DDL
FROM USER_TRIGGERS
WHERE TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
ORDER BY TABLE_NAME, TRIGGER_NAME;


/* ============================================================
   08 - VISTAS
   ============================================================ */

SELECT
    'VIEW' AS TIPO_OBJETO,
    VIEW_NAME AS NOMBRE_OBJETO,
    DBMS_METADATA.GET_DDL(
        'VIEW',
        VIEW_NAME,
        USER
    ) AS DDL
FROM USER_VIEWS
WHERE VIEW_NAME LIKE 'VW\_GT\_%' ESCAPE '\'
ORDER BY VIEW_NAME;


/* ============================================================
   09 - PACKAGE SPEC
   USER_OBJECTS informa PACKAGE;
   DBMS_METADATA requiere PACKAGE_SPEC.
   ============================================================ */

SELECT
    'PACKAGE_SPEC' AS TIPO_OBJETO,
    OBJECT_NAME AS NOMBRE_OBJETO,
    DBMS_METADATA.GET_DDL(
        'PACKAGE_SPEC',
        OBJECT_NAME,
        USER
    ) AS DDL
FROM USER_OBJECTS
WHERE OBJECT_TYPE = 'PACKAGE'
  AND OBJECT_NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
ORDER BY OBJECT_NAME;


/* ============================================================
   10 - PACKAGE BODY
   DBMS_METADATA requiere PACKAGE_BODY, no "PACKAGE BODY".
   ============================================================ */

SELECT
    'PACKAGE_BODY' AS TIPO_OBJETO,
    OBJECT_NAME AS NOMBRE_OBJETO,
    DBMS_METADATA.GET_DDL(
        'PACKAGE_BODY',
        OBJECT_NAME,
        USER
    ) AS DDL
FROM USER_OBJECTS
WHERE OBJECT_TYPE = 'PACKAGE BODY'
  AND OBJECT_NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
ORDER BY OBJECT_NAME;


/* ============================================================
   11 - DEPENDENCIAS ENTRE OBJETOS ATLAS
   Sirve para determinar el orden de creación.
   ============================================================ */

SELECT
    NAME AS OBJETO,
    TYPE AS TIPO_OBJETO,
    REFERENCED_NAME,
    REFERENCED_TYPE,
    REFERENCED_OWNER
FROM USER_DEPENDENCIES
WHERE (
       NAME LIKE 'GT\_%' ESCAPE '\'
    OR NAME LIKE 'VW\_GT\_%' ESCAPE '\'
    OR NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
)
AND (
       REFERENCED_NAME LIKE 'GT\_%' ESCAPE '\'
    OR REFERENCED_NAME LIKE 'VW\_GT\_%' ESCAPE '\'
    OR REFERENCED_NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
)
ORDER BY NAME, REFERENCED_NAME;


/* ============================================================
   12 - COLUMNAS DE TODAS LAS TABLAS
   Segunda validación independiente del DDL.
   ============================================================ */

SELECT
    TABLE_NAME,
    COLUMN_ID,
    COLUMN_NAME,
    DATA_TYPE,
    DATA_LENGTH,
    DATA_PRECISION,
    DATA_SCALE,
    NULLABLE,
    DATA_DEFAULT
FROM USER_TAB_COLUMNS
WHERE TABLE_NAME LIKE 'GT\_%' ESCAPE '\'
ORDER BY TABLE_NAME, COLUMN_ID;


/* ============================================================
   13 - CATALOGO: ROLES
   ============================================================ */

SELECT *
FROM GT_ROL;


/* ============================================================
   14 - CATALOGO: PERMISOS
   ============================================================ */

SELECT *
FROM GT_PERMISO;


/* ============================================================
   15 - CATALOGO: MODALIDADES DE DIA
   ============================================================ */

SELECT *
FROM GT_MODALIDAD_DIA;


/* ============================================================
   16 - CATALOGO: PARAMETROS
   ============================================================ */

SELECT *
FROM GT_PARAMETRO;


/* ============================================================
   17 - CATALOGO: PARAMETROS SCORE
   ============================================================ */

SELECT *
FROM GT_PARAMETRO_SCORE;


/* ============================================================
   18 - CATALOGO: CATEGORIAS DE COSTO
   ============================================================ */

SELECT *
FROM GT_CATEGORIA_COSTO;


/* ============================================================
   19 - RESUMEN FINAL
   ============================================================ */

SELECT
    OBJECT_TYPE,
    COUNT(*) AS CANTIDAD
FROM USER_OBJECTS
WHERE (
       OBJECT_NAME LIKE 'GT\_%' ESCAPE '\'
    OR OBJECT_NAME LIKE 'VW\_GT\_%' ESCAPE '\'
    OR OBJECT_NAME LIKE 'PKG\_GT\_%' ESCAPE '\'
)
GROUP BY OBJECT_TYPE
ORDER BY OBJECT_TYPE;
