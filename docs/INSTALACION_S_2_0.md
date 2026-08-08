# Instalación completa — ATLAS S.2.0

## 1. Objetivo

Este documento permite desplegar la misma línea de aplicación que fue validada con Oracle, sesión/CSRF, servicio Windows y login LDAP. No requiere recordar los hotfix históricos: todo lo necesario para el runtime está consolidado en esta release.

## 2. Requisitos

- Windows Server 2016 o superior.
- Python 3.12.x de 64 bits.
- Acceso al esquema Oracle propietario de ATLAS.
- Oracle Instant Client si `thick_mode=true`.
- Conectividad a LDAP/LDAPS corporativo.
- Certificado/CA corporativa accesible por la cuenta del servicio.
- NSSM x64 disponible como `service\nssm.exe` o en `PATH`.
- DBeaver para aplicar SQL Oracle.
- Puerto 5050 autorizado o el puerto definido en `config.ini`.

## 3. Copia limpia

No copiar desde producción los siguientes elementos:

```text
config.ini
.venv\
logs\
__pycache__\
*.zip históricos
nssm.exe desde el repositorio
respaldos/hotfix antiguos
```

Desplegar el repositorio en una ruta estable, por ejemplo:

```text
K:\@@@@@ATLAS
```

## 4. Entorno virtual

Desde CMD:

```cmd
cd /d K:\@@@@@ATLAS
I:\python\python.exe -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`I:\python\python.exe` es solo un ejemplo del Python base. Si se usa otra ruta, reemplazarla. El servicio siempre debe apuntar a `.venv\Scripts\python.exe`.

Validar:

```cmd
.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)"
```

`sys.executable` y `sys.prefix` deben apuntar al `.venv`. WMIC puede mostrar el ejecutable base del venv; eso por sí solo no indica un error.

## 5. Configuración

### Perfil recomendado: HTTPS

```cmd
copy config.ini.example config.ini
```

Completar Oracle, LDAP, CA y `secret_key`.

Generar secreto:

```cmd
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

### Perfil compatible con el runtime validado

Si todavía se publica por HTTP directo y LDAPS presenta certificados legacy:

```cmd
copy config.compat-http-ldaps.example config.ini
```

El perfil contiene:

```ini
session_cookie_secure=false
force_https=false
trust_proxy_headers=false
tls_ciphers=DEFAULT:@SECLEVEL=1
validate_certificate=true
allow_legacy_ciphers=false
```

`SECLEVEL=1` es una compatibilidad temporal. No deshabilita la validación del certificado. La meta es renovar los certificados LDAP y volver a `DEFAULT`, además de publicar ATLAS por HTTPS.

No versionar `config.ini`.

## 6. Base de datos — actualización de una instalación ATLAS existente

Ejecutar con el esquema propietario en DBeaver. Hacer respaldo/restore point según política corporativa.

### 6.1 Diagnóstico

Ejecutar consultas de validación existentes antes de modificar.

### 6.2 Imputación directa a proyectos V3

Ejecutar, si aún no están aplicados:

```text
sql/50_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
sql/51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
```

El resultado esperado es:

```text
PROYECTOS_SIN_TAREA_TECNICA = 0
CONFLICTOS_CODIGO_PRYGEN = 0
```

### 6.3 Seguridad y aprobaciones v0.3

Ejecutar:

```text
sql/60_SEGURIDAD_APROBACIONES_V0_3.sql
sql/61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql
```

El script 60 de S.2.0 no contiene `SET DEFINE OFF`, que no es SQL Oracle y provoca ORA-00922 en DBeaver.

En DBeaver utilizar **Execute SQL Script** para el archivo 60, porque contiene varios bloques PL/SQL separados por `/`.

Validaciones importantes del 61:

- `SESSION_VERSION` existe.
- `BLOQUEADO_HASTA` existe.
- `GT_LOGIN_RATE_LIMIT` existe.
- restricciones de estados/auditoría válidas.
- `IX_GT_VAL_ESTADO_ENVIO` válido.
- `ORIGENES_BLOQUEADOS=0` es normal cuando no hay IP bloqueada.

## 7. Base de datos — módulos de una instalación existente incompleta

Aplicar únicamente los módulos faltantes, en este orden lógico:

```text
20_VALIDAR_MANTENEDOR_USUARIOS.sql
21_MODALIDADES_PLANILLA_SEMANAL.sql
22A_PKG_GT_IMPUTACION_V2_SPEC.sql
22B_PKG_GT_IMPUTACION_V2_BODY.sql
23_VALIDAR_IMPUTACION_SEMANAL.sql
24_AGREGAR_DESCANSO_SEMANAL.sql
30_DDL_COSTOS_SCORE.sql
31_CATALOGOS_PARAMETROS_SCORE.sql
32A_PKG_GT_COSTOS_SPEC.sql
32B_PKG_GT_COSTOS_BODY.sql
33_VISTAS_COSTOS_SCORE.sql
34_VALIDAR_MODULO_COSTOS.sql
40_DDL_MANTENEDOR_UNIDADES.sql
41A_PKG_GT_ORG_UNIDAD_SPEC.sql
41B_PKG_GT_ORG_UNIDAD_BODY.sql
42_VALIDAR_MANTENEDOR_UNIDADES.sql
50_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql
60_SEGURIDAD_APROBACIONES_V0_3.sql
61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql
```

No ejecutar scripts DDL ya aplicados sin revisar primero su idempotencia. Los scripts `sql/modelo/` siguen siendo referencia histórica y no se certifican aquí como creación productiva desde cero sin una comparación contra el esquema real.

## 8. Validación técnica antes de servicio

```cmd
.venv\Scripts\python.exe scripts\validar_release.py
.venv\Scripts\python.exe scripts\validar_higiene.py
.venv\Scripts\python.exe -m compileall -q atlas tests *.py tools
.venv\Scripts\python.exe -m pytest -q
```

Luego:

```cmd
.venv\Scripts\python.exe tools\diagnose_runtime.py
.venv\Scripts\python.exe tools\test_oracle_connection.py
.venv\Scripts\python.exe tools\test_ldap_transport.py
.venv\Scripts\python.exe tools\test_ldap_bind.py
```

La prueba de bind solicita la clave con `getpass`; no la muestra ni la registra.

## 9. Servicio Windows `ATLAS_Web`

Copiar NSSM x64 a:

```text
K:\@@@@@ATLAS\service\nssm.exe
```

Abrir CMD como Administrador:

```cmd
cd /d K:\@@@@@ATLAS
service\install_service.cmd
```

La configuración esperada de NSSM es:

```text
Application   K:\@@@@@ATLAS\.venv\Scripts\python.exe
AppParameters K:\@@@@@ATLAS\service_entry.py
AppDirectory  K:\@@@@@ATLAS
Service       ATLAS_Web
```

Revisar:

```cmd
service\diagnose_service.cmd
```

## 10. Prueba web

1. Abrir una ventana privada/incógnito para evitar cookies de sesiones históricas.
2. Abrir la URL del servidor y puerto configurado.
3. Iniciar sesión con un usuario ATLAS inscrito en `GT_USUARIO_AUTH` con `TIPO_AUTENTICACION='LDAP'`.
4. Verificar acceso al dashboard y rol esperado.
5. Revisar `logs\atlas.log` si aparece un código de incidente.

## 11. Validación LDAP esperada

Si el transporte falla con:

```text
CERTIFICATE_VERIFY_FAILED ... EE certificate key too weak
```

usar temporalmente `DEFAULT:@SECLEVEL=1`. Si `tools\test_ldap_bind.py` devuelve `SUCCESS` pero la web falla, reiniciar `ATLAS_Web` para que el proceso recargue `config.ini`.

## 12. Rollback

- Mantener copia del directorio de la versión anterior sin `config.ini` expuesto.
- Conservar el `config.ini` de forma segura fuera del paquete.
- Antes de rollback DB revisar `sql/62_ROLLBACK_SEGURIDAD_APROBACIONES_V0_3.sql` y los rollback específicos; no ejecutar rollback destructivo después de uso real sin evaluar datos/auditoría.
- Para rollback de aplicación, detener `ATLAS_Web`, restaurar código compatible con el esquema y reiniciar.

## 13. Criterio de instalación terminada

La instalación se considera completa cuando:

- release/higiene/compile/pytest pasan;
- Oracle responde;
- transporte LDAP responde;
- bind LDAP real devuelve `SUCCESS`;
- `ATLAS_Web` está `RUNNING`;
- TCP 5050 (o puerto configurado) está `LISTENING`;
- login web LDAP entra correctamente;
- usuario/rol/unidad se cargan sin error;
- no hay errores P0 en `logs\atlas.log`.
