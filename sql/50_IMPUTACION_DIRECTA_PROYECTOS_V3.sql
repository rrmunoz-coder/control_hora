/*
ATLAS - IMPUTACIÓN DIRECTA A PROYECTOS V3
COMPATIBLE CON GT_TAREA COMPRIMIDA / EXADATA
Oracle 12.2 - esquema SCBILL

CAUSA DE LA VERSIÓN ANTERIOR
----------------------------
GT_TAREA es una tabla comprimida. Oracle devuelve ORA-39726 cuando se intenta
agregar o eliminar columnas en este tipo de tabla.

SOLUCIÓN V3
-----------
No se modifica la estructura de GT_TAREA.
Cada proyecto se representa mediante una tarea técnica determinística:

    CODIGO = 'PRYGEN_' || ID_PROYECTO

La aplicación reconoce esa tarea como imputación directa al proyecto.

EJECUCIÓN EN DBEAVER
--------------------
1. Conectarse a SCBILL.
2. Abrir el archivo.
3. Ctrl+A.
4. Ctrl+Enter.
5. No agregar "/".
*/

DECLARE
    V_CONFLICTOS NUMBER;
    V_FILAS      NUMBER;
    V_FALTANTES  NUMBER;
BEGIN
    DBMS_OUTPUT.ENABLE(NULL);

    IF SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') <> 'SCBILL' THEN
        RAISE_APPLICATION_ERROR(
            -20090,
            'Conéctate al esquema SCBILL. Esquema actual: '
            || SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA')
        );
    END IF;

    /*
    Detecta si existe un código técnico reservado asociado a otro proyecto.
    En ese caso se cancela para no sobrescribir información.
    */
    SELECT COUNT(*)
      INTO V_CONFLICTOS
      FROM GT_TAREA T
     WHERE T.CODIGO LIKE 'PRYGEN\_%' ESCAPE '\'
       AND (
            T.ID_PROYECTO IS NULL
            OR T.CODIGO <> 'PRYGEN_' || TO_CHAR(T.ID_PROYECTO)
       );

    IF V_CONFLICTOS > 0 THEN
        RAISE_APPLICATION_ERROR(
            -20091,
            'Existen ' || V_CONFLICTOS
            || ' tareas con código PRYGEN_ que no coinciden con su proyecto. '
            || 'Revisar antes de continuar.'
        );
    END IF;

    /*
    Crea las tareas técnicas faltantes y sincroniza las existentes.
    MERGE es DML y sí está soportado sobre la tabla comprimida.
    */
    MERGE INTO GT_TAREA T
    USING (
        SELECT
            P.ID_PROYECTO,
            'PRYGEN_' || TO_CHAR(P.ID_PROYECTO) AS CODIGO_TAREA,
            SUBSTR('Proyecto · ' || P.NOMBRE, 1, 250) AS TITULO_TAREA,
            P.ID_UNIDAD_DUENA,
            P.CLASIFICACION_COSTO,
            P.FECHA_INICIO,
            P.FECHA_FIN,
            P.PERMITE_IMPUTACION,
            P.ACTIVO
        FROM GT_PROYECTO P
    ) P
       ON (
            T.ID_PROYECTO = P.ID_PROYECTO
            AND T.CODIGO = P.CODIGO_TAREA
       )
    WHEN MATCHED THEN
        UPDATE SET
            T.TITULO = P.TITULO_TAREA,
            T.DESCRIPCION =
                'Tarea técnica para imputación directa al proyecto.',
            T.ID_UNIDAD_DUENA = P.ID_UNIDAD_DUENA,
            T.CLASIFICACION_COSTO = P.CLASIFICACION_COSTO,
            T.FECHA_INICIO = P.FECHA_INICIO,
            T.FECHA_COMPROMISO = P.FECHA_FIN,
            T.PERMITE_IMPUTACION = P.PERMITE_IMPUTACION,
            T.ACTIVO = P.ACTIVO,
            T.FECHA_ACTUALIZACION = SYSTIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT (
            CODIGO,
            TITULO,
            DESCRIPCION,
            ID_PROYECTO,
            ID_UNIDAD_DUENA,
            CLASIFICACION_COSTO,
            ESTADO,
            PRIORIDAD,
            FECHA_INICIO,
            FECHA_COMPROMISO,
            HORAS_ESTIMADAS,
            PERMITE_IMPUTACION,
            ACTIVO
        )
        VALUES (
            P.CODIGO_TAREA,
            P.TITULO_TAREA,
            'Tarea técnica para imputación directa al proyecto.',
            P.ID_PROYECTO,
            P.ID_UNIDAD_DUENA,
            P.CLASIFICACION_COSTO,
            'EN_EJECUCION',
            'MEDIA',
            P.FECHA_INICIO,
            P.FECHA_FIN,
            NULL,
            P.PERMITE_IMPUTACION,
            P.ACTIVO
        );

    V_FILAS := SQL%ROWCOUNT;

    SELECT COUNT(*)
      INTO V_FALTANTES
      FROM GT_PROYECTO P
     WHERE NOT EXISTS (
            SELECT 1
            FROM GT_TAREA T
            WHERE T.ID_PROYECTO = P.ID_PROYECTO
              AND T.CODIGO = 'PRYGEN_' || TO_CHAR(P.ID_PROYECTO)
     );

    IF V_FALTANTES > 0 THEN
        RAISE_APPLICATION_ERROR(
            -20092,
            'Quedaron ' || V_FALTANTES
            || ' proyectos sin tarea técnica.'
        );
    END IF;

    COMMIT;

    DBMS_OUTPUT.PUT_LINE(
        'Tareas técnicas insertadas o sincronizadas: ' || V_FILAS
    );
    DBMS_OUTPUT.PUT_LINE(
        'Proyectos sin tarea técnica: ' || V_FALTANTES
    );
    DBMS_OUTPUT.PUT_LINE(
        'Instalación V3 terminada correctamente. COMMIT ejecutado.'
    );

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;

        DBMS_OUTPUT.PUT_LINE('ERROR: ' || SQLERRM);
        DBMS_OUTPUT.PUT_LINE(
            'ROLLBACK de los cambios DML ejecutado.'
        );

        RAISE;
END;
