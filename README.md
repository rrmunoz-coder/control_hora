# ATLAS — Gestión de capacidad, costos y automatización

ATLAS es una aplicación web interna en Flask/Oracle para registrar trabajo semanal, gestionar proyectos y tareas, aprobar semanas, controlar capacidad, costos y oportunidades de automatización.

## Versión

**ATLAS S.2.0 — 7 de agosto de 2026.**

Esta release es un snapshot consolidado del runtime validado y mantiene como baseline funcional la v0.3.0.

## Incluye

- Login corporativo LDAP y usuario local de contingencia.
- Sesiones revocables, timeout por inactividad y duración máxima.
- CSRF global y rate limiting de login por usuario/origen.
- Usuarios, roles, jefaturas, unidades y alcance por unidad.
- Proyectos/servicios, tareas e imputación semanal lunes-domingo.
- Imputación directa a proyecto mediante `PRYGEN_<ID_PROYECTO>`.
- Flujo semanal: `PENDIENTE`, `ENVIADO`, `OBSERVADO`, `RECHAZADO`, `APROBADO`, `CERRADO`, `REABIERTO`.
- Costos, centros de costo, actividades y score de automatización/eficiencia.
- Auditoría crítica y errores correlacionados.
- Waitress como WSGI y servicio Windows `ATLAS_Web` mediante NSSM.
- SQL Oracle, validaciones, rollback, pruebas, CI, manuales y prompt de reconstrucción.

## Instalación rápida

1. Descomprimir o clonar la release.
2. Crear `.venv` con Python 3.12 e instalar `requirements.txt`.
3. Copiar `config.ini.example` a `config.ini` o usar `config.compat-http-ldaps.example` como referencia si la infraestructura aún usa HTTP directo y certificados LDAP legacy.
4. Completar credenciales/DSN/CA/secreto Flask sin versionarlos.
5. Aplicar y validar SQL según `docs/INSTALACION_S_2_0.md` usando DBeaver.
6. Ejecutar:

```cmd
.venv\Scripts\python.exe scripts\validar_release.py
.venv\Scripts\python.exe scripts\validar_higiene.py
.venv\Scripts\python.exe -m compileall -q atlas tests *.py tools
.venv\Scripts\python.exe -m pytest -q
```

7. Probar Oracle y LDAP:

```cmd
.venv\Scripts\python.exe tools\test_oracle_connection.py
.venv\Scripts\python.exe tools\test_ldap_transport.py
.venv\Scripts\python.exe tools\test_ldap_bind.py
```

8. Copiar `nssm.exe` x64 a `service\` (no se versiona) e instalar `ATLAS_Web` como administrador:

```cmd
service\install_service.cmd
```

Manual completo: `docs/INSTALACION_S_2_0.md`.

## Configuración LDAP validada

La release mantiene validación de certificado (`validate_certificate=true`). En la infraestructura que presentó `EE certificate key too weak`, el perfil temporal validado usa:

```ini
tls_ciphers=DEFAULT:@SECLEVEL=1
allow_legacy_ciphers=false
```

No se utiliza `SECLEVEL=0`. La corrección definitiva es renovar los certificados LDAPS y volver a `tls_ciphers=DEFAULT`.

## Seguridad

`config.ini`, secretos, `.venv`, logs, ZIP históricos y binarios de terceros no forman parte del repositorio. El perfil HTTPS sigue siendo el objetivo productivo recomendado; el perfil HTTP directo existe solo para reproducir el runtime actualmente validado mientras se implementa TLS frontal.

## Documentos clave

- `docs/INSTALACION_S_2_0.md`
- `docs/OPERACION_Y_DIAGNOSTICO_S_2_0.md`
- `docs/PRUEBAS_S_2_0.md`
- `prompts/PROMPT_REGENERACION_ATLAS_S_2_0.md`
- `pendiente_desa/PENDIENTES_S_2_0.md`
- `releases/S.2.0/RELEASE_NOTES.md`
