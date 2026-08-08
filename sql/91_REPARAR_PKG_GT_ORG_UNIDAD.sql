CREATE OR REPLACE PACKAGE BODY PKG_GT_ORG_UNIDAD AS

    FUNCTION NORMALIZAR_CODIGO (
        P_CODIGO IN VARCHAR2
    ) RETURN VARCHAR2
    IS
        V_CODIGO VARCHAR2(50 CHAR);
    BEGIN
        V_CODIGO := UPPER(TRIM(P_CODIGO));

        IF V_CODIGO IS NULL
           OR LENGTH(V_CODIGO) > 50
           OR NOT REGEXP_LIKE(V_CODIGO, '^[A-Z0-9_.-]+$') THEN
            RAISE_APPLICATION_ERROR(
                -20011,
                'Código inválido. Use letras, números, punto, guion o guion bajo.'
            );
        END IF;

        RETURN V_CODIGO;
    END NORMALIZAR_CODIGO;


    FUNCTION NORMALIZAR_NOMBRE (
        P_NOMBRE IN VARCHAR2
    ) RETURN VARCHAR2
    IS
        V_NOMBRE VARCHAR2(150 CHAR);
    BEGIN
        V_NOMBRE := TRIM(P_NOMBRE);

        IF V_NOMBRE IS NULL OR LENGTH(V_NOMBRE) > 150 THEN
            RAISE_APPLICATION_ERROR(-20012, 'Nombre de unidad inválido.');
        END IF;

        RETURN V_NOMBRE;
    END NORMALIZAR_NOMBRE;


    FUNCTION NORMALIZAR_TIPO (
        P_TIPO_UNIDAD IN VARCHAR2
    ) RETURN VARCHAR2
    IS
        V_TIPO VARCHAR2(20 CHAR);
    BEGIN
        V_TIPO := UPPER(TRIM(P_TIPO_UNIDAD));

        IF V_TIPO IS NULL OR V_TIPO NOT IN ('GERENCIA','SUBGERENCIA','AREA','EQUIPO') THEN
            RAISE_APPLICATION_ERROR(-20013, 'Tipo de unidad inválido.');
        END IF;

        RETURN V_TIPO;
    END NORMALIZAR_TIPO;


    FUNCTION NORMALIZAR_ACTIVO (
        P_ACTIVO IN CHAR
    ) RETURN CHAR
    IS
        V_ACTIVO CHAR(1 CHAR);
    BEGIN
        V_ACTIVO := UPPER(TRIM(P_ACTIVO));

        IF V_ACTIVO IS NULL OR V_ACTIVO NOT IN ('S','N') THEN
            RAISE_APPLICATION_ERROR(-20014, 'Estado de unidad inválido.');
        END IF;

        RETURN V_ACTIVO;
    END NORMALIZAR_ACTIVO;


    FUNCTION JERARQUIA_VALIDA (
        P_TIPO_HIJO  IN VARCHAR2,
        P_TIPO_PADRE IN VARCHAR2
    ) RETURN BOOLEAN
    IS
    BEGIN
        RETURN
            (P_TIPO_HIJO = 'SUBGERENCIA' AND P_TIPO_PADRE = 'GERENCIA')
            OR
            (P_TIPO_HIJO = 'AREA' AND P_TIPO_PADRE IN ('GERENCIA','SUBGERENCIA'))
            OR
            (P_TIPO_HIJO = 'EQUIPO' AND P_TIPO_PADRE = 'AREA');
    END JERARQUIA_VALIDA;


    PROCEDURE VALIDAR_EXISTENCIA (
        P_ID_UNIDAD IN NUMBER
    )
    IS
        V_COUNT NUMBER;
    BEGIN
        SELECT COUNT(*)
          INTO V_COUNT
          FROM GT_ORG_UNIDAD
         WHERE ID_UNIDAD = P_ID_UNIDAD;

        IF V_COUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20010, 'La unidad no existe.');
        END IF;
    END VALIDAR_EXISTENCIA;


    PROCEDURE VALIDAR_CODIGO_UNICO (
        P_CODIGO    IN VARCHAR2,
        P_ID_EXCLUIR IN NUMBER DEFAULT NULL
    )
    IS
        V_COUNT NUMBER;
    BEGIN
        SELECT COUNT(*)
          INTO V_COUNT
          FROM GT_ORG_UNIDAD
         WHERE UPPER(CODIGO) = UPPER(P_CODIGO)
           AND (P_ID_EXCLUIR IS NULL OR ID_UNIDAD <> P_ID_EXCLUIR);

        IF V_COUNT > 0 THEN
            RAISE_APPLICATION_ERROR(-20001, 'El código de unidad ya existe.');
        END IF;
    END VALIDAR_CODIGO_UNICO;


    PROCEDURE VALIDAR_PADRE (
        P_TIPO_UNIDAD     IN VARCHAR2,
        P_ID_UNIDAD_PADRE IN NUMBER,
        P_ID_ACTUAL       IN NUMBER DEFAULT NULL
    )
    IS
        V_TIPO_PADRE   GT_ORG_UNIDAD.TIPO_UNIDAD%TYPE;
        V_ACTIVO_PADRE GT_ORG_UNIDAD.ACTIVO%TYPE;
        V_COUNT        NUMBER;
    BEGIN
        IF P_TIPO_UNIDAD = 'GERENCIA' THEN
            IF P_ID_UNIDAD_PADRE IS NOT NULL THEN
                RAISE_APPLICATION_ERROR(
                    -20005,
                    'Una Gerencia no puede tener unidad padre.'
                );
            END IF;
            RETURN;
        END IF;

        IF P_ID_UNIDAD_PADRE IS NULL THEN
            RAISE_APPLICATION_ERROR(
                -20005,
                'El tipo de unidad seleccionado requiere unidad padre.'
            );
        END IF;

        IF P_ID_ACTUAL IS NOT NULL AND P_ID_UNIDAD_PADRE = P_ID_ACTUAL THEN
            RAISE_APPLICATION_ERROR(-20003, 'Una unidad no puede ser su propio padre.');
        END IF;

        BEGIN
            SELECT TIPO_UNIDAD, ACTIVO
              INTO V_TIPO_PADRE, V_ACTIVO_PADRE
              FROM GT_ORG_UNIDAD
             WHERE ID_UNIDAD = P_ID_UNIDAD_PADRE;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                RAISE_APPLICATION_ERROR(-20002, 'La unidad padre no existe.');
        END;

        IF V_ACTIVO_PADRE <> 'S' THEN
            RAISE_APPLICATION_ERROR(-20008, 'La unidad padre está inactiva.');
        END IF;

        IF NOT JERARQUIA_VALIDA(P_TIPO_UNIDAD, V_TIPO_PADRE) THEN
            RAISE_APPLICATION_ERROR(-20005, 'Jerarquía organizacional inválida.');
        END IF;

        IF P_ID_ACTUAL IS NOT NULL THEN
            SELECT COUNT(*)
              INTO V_COUNT
              FROM (
                    SELECT ID_UNIDAD
                      FROM GT_ORG_UNIDAD
                     START WITH ID_UNIDAD = P_ID_ACTUAL
                    CONNECT BY NOCYCLE PRIOR ID_UNIDAD = ID_UNIDAD_PADRE
                   )
             WHERE ID_UNIDAD = P_ID_UNIDAD_PADRE;

            IF V_COUNT > 0 THEN
                RAISE_APPLICATION_ERROR(
                    -20004,
                    'La unidad padre seleccionada genera un ciclo.'
                );
            END IF;
        END IF;
    END VALIDAR_PADRE;


    PROCEDURE VALIDAR_HIJOS (
        P_ID_UNIDAD   IN NUMBER,
        P_NUEVO_TIPO  IN VARCHAR2
    )
    IS
        V_COUNT NUMBER;
    BEGIN
        SELECT COUNT(*)
          INTO V_COUNT
          FROM GT_ORG_UNIDAD H
         WHERE H.ID_UNIDAD_PADRE = P_ID_UNIDAD
           AND NOT (
                (H.TIPO_UNIDAD = 'SUBGERENCIA' AND P_NUEVO_TIPO = 'GERENCIA')
                OR
                (H.TIPO_UNIDAD = 'AREA' AND P_NUEVO_TIPO IN ('GERENCIA','SUBGERENCIA'))
                OR
                (H.TIPO_UNIDAD = 'EQUIPO' AND P_NUEVO_TIPO = 'AREA')
           );

        IF V_COUNT > 0 THEN
            RAISE_APPLICATION_ERROR(
                -20009,
                'El nuevo tipo no es compatible con las unidades hijas.'
            );
        END IF;
    END VALIDAR_HIJOS;


    FUNCTION CONTAR_ACTIVIDADES_ACTIVAS (
        P_ID_UNIDAD IN NUMBER
    ) RETURN NUMBER
    IS
        V_EXISTE NUMBER;
        V_COUNT  NUMBER := 0;
    BEGIN
        SELECT COUNT(*)
          INTO V_EXISTE
          FROM USER_TABLES
         WHERE TABLE_NAME = 'GT_ACTIVIDAD';

        IF V_EXISTE > 0 THEN
            EXECUTE IMMEDIATE
                'SELECT COUNT(*) FROM GT_ACTIVIDAD '
                || 'WHERE ID_UNIDAD_RESP = :1 AND ACTIVO = ''S'''
                INTO V_COUNT
                USING P_ID_UNIDAD;
        END IF;

        RETURN V_COUNT;
    END CONTAR_ACTIVIDADES_ACTIVAS;


    PROCEDURE CREAR (
        P_CODIGO          IN VARCHAR2,
        P_NOMBRE          IN VARCHAR2,
        P_TIPO_UNIDAD     IN VARCHAR2,
        P_ID_UNIDAD_PADRE IN NUMBER,
        P_ACTIVO          IN CHAR,
        P_ID_UNIDAD       OUT NUMBER
    )
    IS
        V_CODIGO VARCHAR2(50 CHAR);
        V_NOMBRE VARCHAR2(150 CHAR);
        V_TIPO   VARCHAR2(20 CHAR);
        V_ACTIVO CHAR(1 CHAR);
    BEGIN
        V_CODIGO := NORMALIZAR_CODIGO(P_CODIGO);
        V_NOMBRE := NORMALIZAR_NOMBRE(P_NOMBRE);
        V_TIPO := NORMALIZAR_TIPO(P_TIPO_UNIDAD);
        V_ACTIVO := NORMALIZAR_ACTIVO(P_ACTIVO);

        VALIDAR_CODIGO_UNICO(V_CODIGO);
        VALIDAR_PADRE(V_TIPO, P_ID_UNIDAD_PADRE);

        INSERT INTO GT_ORG_UNIDAD (
            ID_UNIDAD_PADRE,
            CODIGO,
            NOMBRE,
            TIPO_UNIDAD,
            ACTIVO,
            FECHA_ACTUALIZACION
        ) VALUES (
            P_ID_UNIDAD_PADRE,
            V_CODIGO,
            V_NOMBRE,
            V_TIPO,
            V_ACTIVO,
            SYSTIMESTAMP
        )
        RETURNING ID_UNIDAD INTO P_ID_UNIDAD;
    END CREAR;


    PROCEDURE ACTUALIZAR (
        P_ID_UNIDAD       IN NUMBER,
        P_CODIGO          IN VARCHAR2,
        P_NOMBRE          IN VARCHAR2,
        P_TIPO_UNIDAD     IN VARCHAR2,
        P_ID_UNIDAD_PADRE IN NUMBER
    )
    IS
        V_CODIGO VARCHAR2(50 CHAR);
        V_NOMBRE VARCHAR2(150 CHAR);
        V_TIPO   VARCHAR2(20 CHAR);
    BEGIN
        VALIDAR_EXISTENCIA(P_ID_UNIDAD);

        V_CODIGO := NORMALIZAR_CODIGO(P_CODIGO);
        V_NOMBRE := NORMALIZAR_NOMBRE(P_NOMBRE);
        V_TIPO := NORMALIZAR_TIPO(P_TIPO_UNIDAD);

        VALIDAR_CODIGO_UNICO(V_CODIGO, P_ID_UNIDAD);
        VALIDAR_PADRE(V_TIPO, P_ID_UNIDAD_PADRE, P_ID_UNIDAD);
        VALIDAR_HIJOS(P_ID_UNIDAD, V_TIPO);

        UPDATE GT_ORG_UNIDAD
           SET ID_UNIDAD_PADRE = P_ID_UNIDAD_PADRE,
               CODIGO = V_CODIGO,
               NOMBRE = V_NOMBRE,
               TIPO_UNIDAD = V_TIPO,
               FECHA_ACTUALIZACION = SYSTIMESTAMP
         WHERE ID_UNIDAD = P_ID_UNIDAD;
    END ACTUALIZAR;


    PROCEDURE CAMBIAR_ESTADO (
        P_ID_UNIDAD IN NUMBER,
        P_ACTIVO    IN CHAR
    )
    IS
        V_ACTIVO      CHAR(1 CHAR);
        V_ID_PADRE    NUMBER;
        V_PADRE_ACTIVO CHAR(1 CHAR);
        V_HIJOS       NUMBER;
        V_USUARIOS    NUMBER;
        V_PROYECTOS   NUMBER;
        V_TAREAS      NUMBER;
        V_ACTIVIDADES NUMBER;
    BEGIN
        VALIDAR_EXISTENCIA(P_ID_UNIDAD);
        V_ACTIVO := NORMALIZAR_ACTIVO(P_ACTIVO);

        SELECT ID_UNIDAD_PADRE
          INTO V_ID_PADRE
          FROM GT_ORG_UNIDAD
         WHERE ID_UNIDAD = P_ID_UNIDAD;

        IF V_ACTIVO = 'S' THEN
            IF V_ID_PADRE IS NOT NULL THEN
                SELECT ACTIVO
                  INTO V_PADRE_ACTIVO
                  FROM GT_ORG_UNIDAD
                 WHERE ID_UNIDAD = V_ID_PADRE;

                IF V_PADRE_ACTIVO <> 'S' THEN
                    RAISE_APPLICATION_ERROR(
                        -20008,
                        'No se puede activar bajo una unidad padre inactiva.'
                    );
                END IF;
            END IF;
        ELSE
            SELECT COUNT(*)
              INTO V_HIJOS
              FROM GT_ORG_UNIDAD
             WHERE ID_UNIDAD_PADRE = P_ID_UNIDAD
               AND ACTIVO = 'S';

            IF V_HIJOS > 0 THEN
                RAISE_APPLICATION_ERROR(
                    -20006,
                    'La unidad tiene hijos activos.'
                );
            END IF;

            SELECT COUNT(DISTINCT UU.ID_USUARIO)
              INTO V_USUARIOS
              FROM GT_USUARIO_UNIDAD UU
              JOIN GT_USUARIO U
                ON U.ID_USUARIO = UU.ID_USUARIO
             WHERE UU.ID_UNIDAD = P_ID_UNIDAD
               AND UU.ACTIVO = 'S'
               AND U.ACTIVO = 'S';

            SELECT COUNT(*)
              INTO V_PROYECTOS
              FROM GT_PROYECTO
             WHERE ID_UNIDAD_DUENA = P_ID_UNIDAD
               AND ACTIVO = 'S';

            SELECT COUNT(*)
              INTO V_TAREAS
              FROM GT_TAREA
             WHERE ID_UNIDAD_DUENA = P_ID_UNIDAD
               AND ACTIVO = 'S';

            V_ACTIVIDADES := CONTAR_ACTIVIDADES_ACTIVAS(P_ID_UNIDAD);

            IF V_USUARIOS + V_PROYECTOS + V_TAREAS + V_ACTIVIDADES > 0 THEN
                RAISE_APPLICATION_ERROR(
                    -20007,
                    'La unidad mantiene dependencias activas.'
                );
            END IF;
        END IF;

        UPDATE GT_ORG_UNIDAD
           SET ACTIVO = V_ACTIVO,
               FECHA_ACTUALIZACION = SYSTIMESTAMP
         WHERE ID_UNIDAD = P_ID_UNIDAD;
    END CAMBIAR_ESTADO;

END PKG_GT_ORG_UNIDAD;
