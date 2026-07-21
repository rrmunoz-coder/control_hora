# Manual de instalación ATLAS v0.1.0

## 1. Preparación

Servidor recomendado:

```text
Windows Server
Python 3.12 o superior
Oracle Instant Client
Acceso a Oracle SCBILL
Acceso LDAP corporativo
Puerto web autorizado, por defecto 5050
```

## 2. Despliegue de archivos

Descomprimir el paquete en:

```cmd
K:\@@@@@ATLAS
```

Crear configuración local:

```cmd
copy config.ini.example config.ini
```

Completar en `config.ini` los datos reales de Oracle, LDAP y secreto Flask. Ese archivo no debe versionarse.

## 3. Entorno Python

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Base de datos

Ejecutar los SQL en DBeaver conectado a `SCBILL`, usando:

```text
Ctrl+A
Ctrl+Enter
```

No agregar `/` al final si se ejecuta como sentencia completa en DBeaver.

Orden recomendado:

```text
sql/00_VALIDAR_INSTALACION.sql
sql/01_CREAR_USUARIO_ADMIN.sql
sql/20_VALIDAR_MANTENEDOR_USUARIOS.sql
sql/21_MODALIDADES_PLANILLA_SEMANAL.sql
sql/22A_PKG_GT_IMPUTACION_V2_SPEC.sql
sql/22B_PKG_GT_IMPUTACION_V2_BODY.sql
sql/23_VALIDAR_IMPUTACION_SEMANAL.sql
sql/24_AGREGAR_DESCANSO_SEMANAL.sql
sql/30_DDL_COSTOS_SCORE.sql
sql/31_CATALOGOS_PARAMETROS_SCORE.sql
sql/32A_PKG_GT_COSTOS_SPEC.sql
sql/32B_PKG_GT_COSTOS_BODY.sql
sql/33_VISTAS_COSTOS_SCORE.sql
sql/34_VALIDAR_MODULO_COSTOS.sql
sql/40_DDL_MANTENEDOR_UNIDADES.sql
sql/41A_PKG_GT_ORG_UNIDAD_SPEC.sql
sql/41B_PKG_GT_ORG_UNIDAD_BODY.sql
sql/42_VALIDAR_MANTENEDOR_UNIDADES.sql
sql/50_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
sql/51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
```

## 5. Servicio Windows

Instalar o reiniciar el servicio según corresponda:

```cmd
service\install_service.cmd
service\restart_service.cmd
```

## 6. Validación funcional mínima

- Login con usuario LDAP válido.
- Acceso con usuario administrador.
- Creación de unidad organizacional.
- Creación de proyecto o servicio.
- Creación de tarea.
- Imputación semanal a tarea.
- Imputación directa a proyecto.
- Revisión de historial.
