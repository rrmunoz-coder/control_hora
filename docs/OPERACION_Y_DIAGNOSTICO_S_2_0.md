# Operación y diagnóstico — ATLAS S.2.0

## Servicio

```cmd
sc query ATLAS_Web
service\status_service.cmd
service\diagnose_service.cmd
```

## Puerto

```cmd
netstat -ano | findstr :5050
```

Debe existir un único `TCP ... LISTENING`. Una entrada UDP 5050 de otro proceso no corresponde a Waitress.

## Python real

NSSM debe apuntar a `.venv\Scripts\python.exe`. En Windows, WMIC puede mostrar el Python base que creó el venv. Confirmar con:

```cmd
.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.prefix); print(sys.base_prefix)"
```

## Configuración efectiva

```cmd
.venv\Scripts\python.exe tools\diagnose_runtime.py
```

No imprime contraseñas ni `SECRET_KEY`.

## Logs

```cmd
powershell -NoProfile -Command "Get-Content 'logs\atlas.log' -Tail 50"
```

Errores relevantes:

- `CSRF session token is missing`: cookie de sesión no volvió con el POST.
- `LDAP no disponible`: revisar detalle TLS/conectividad.
- `EE certificate key too weak`: certificado LDAPS legacy; usar temporalmente `DEFAULT:@SECLEVEL=1` y gestionar renovación.

## CSRF

ATLAS genera el `csrf_token` en la sesión y el formulario de login incluye el campo oculto. Para aislar navegador de servidor se puede hacer un GET+POST manteniendo una sesión HTTP. Si PowerShell pasa CSRF y Chrome no, limpiar cookies del host o probar incógnito.

## Reinicio después de configuración

`config.ini` se carga al crear la aplicación. Cualquier cambio de LDAP, TLS, cookies, proxy o seguridad requiere reiniciar `ATLAS_Web`.
