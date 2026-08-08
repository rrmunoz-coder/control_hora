# PROMPT MAESTRO — REGENERAR ATLAS S.2.0 COMPLETO

Actúa como arquitecto senior, desarrollador full-stack Python/Flask, especialista Oracle y revisor de seguridad. Debes reconstruir ATLAS como una aplicación ejecutable e instalable, no como pseudocódigo.

## Fuente de verdad

La línea funcional a preservar es **ATLAS S.2.0 (baseline v0.3.0)**. No elimines controles existentes para simplificar.

## Stack obligatorio

- Python 3.12.x.
- Flask 3.1, Flask-WTF, Jinja.
- Oracle 12c+ mediante `python-oracledb`.
- LDAP con `ldap3`, LDAPS o StartTLS y validación de certificado.
- Waitress.
- Windows Service `ATLAS_Web` mediante NSSM externo.
- HTML/CSS/JS sin depender de frameworks externos para la funcionalidad base.

## Arquitectura obligatoria

- Application factory `create_app`.
- Blueprints: auth, dashboard, users, units, projects, tasks, time_entries, approvals, costs.
- Servicios Python por dominio.
- Pool Oracle y binds en todas las entradas del usuario.
- Packages PL/SQL para reglas críticas existentes.
- Configuración externa `config.ini`.
- Logs rotativos y códigos de incidente.

## Funcionalidad que no se puede perder

1. Login LOCAL de contingencia y LDAP corporativo.
2. Usuarios/roles/jefaturas/unidades.
3. Alcance por unidad/descendientes/responsabilidad/asignación.
4. Proyectos y tareas.
5. Semana lunes-domingo y modalidades de día.
6. Imputación directa a proyecto usando tarea técnica `PRYGEN_<ID_PROYECTO>`; no agregar columna física incompatible con tablas comprimidas.
7. Flujo `PENDIENTE`, `ENVIADO`, `OBSERVADO`, `RECHAZADO`, `APROBADO`, `CERRADO`, `REABIERTO`.
8. Bloqueo de edición según estado.
9. Costos, centros de costo, actividades, mapeos y score.
10. Auditoría de acciones críticas.

## Seguridad obligatoria

- CSRF global en POST.
- `SECRET_KEY` aleatorio >=32 bytes.
- Cookie HttpOnly/SameSite; Secure cuando HTTPS esté activo.
- Timeout absoluto e inactividad.
- `SESSION_VERSION` para revocación/revalidación.
- Rate limit persistente por usuario e IP.
- LDAP con `validate_certificate=true`.
- Perfil seguro por defecto: `tls_ciphers=DEFAULT`.
- Compatibilidad temporal admitida: `DEFAULT:@SECLEVEL=1` cuando el certificado corporativo legacy lo exija, sin desactivar validación. No usar `SECLEVEL=0` salvo contingencia formal explícita y controlada.
- Cabeceras CSP/HSTS/X-Content-Type-Options/Referrer-Policy/frame-ancestors.
- Backend authorization contra IDOR.
- No exponer errores Oracle/LDAP al usuario.
- No registrar contraseñas.

## Base de datos

Conservar scripts/migraciones actuales y obligatoriamente incluir en `sql/`:

- `50_IMPUTACION_DIRECTA_PROYECTOS_V3.sql`
- `51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql`
- `60_SEGURIDAD_APROBACIONES_V0_3.sql` compatible con DBeaver, sin `SET DEFINE OFF`.
- `61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql`
- `62_ROLLBACK_SEGURIDAD_APROBACIONES_V0_3.sql`

No ejecutar automáticamente DDL destructivo. Tablas Oracle pueden estar comprimidas.

## Servicio Windows

NSSM debe configurar:

- Application: `<APP>\.venv\Scripts\python.exe`
- AppParameters: `<APP>\service_entry.py`
- AppDirectory: `<APP>`
- Servicio: `ATLAS_Web`
- Reinicio automático y logs rotativos.

No confundir `sys.base_prefix` o la imagen reportada por WMIC con el Python efectivo del venv; validar `sys.executable` y `sys.prefix`.

## Pruebas obligatorias

- higiene de repositorio;
- validación de release;
- compileall;
- pytest;
- autorización por rutas;
- sesión/revocación;
- CSRF;
- Oracle connection;
- LDAP transport;
- bind LDAP directo con `getpass`;
- servicio Windows y puerto;
- login web end-to-end.

## Entregables

Repositorio completo con código, plantillas, estáticos, SQL, requirements fijados, `config.ini.example`, perfil compat sanitizado, pruebas, CI, servicio, manual de instalación, operación/diagnóstico, changelog, versión, manifiesto, release notes/checksum, prompt y backlog.

Excluir secretos, `config.ini`, `.venv`, logs, binarios, ZIP históricos y datos reales.

## Pendientes que NO deben implementarse silenciosamente

HTTPS frontal definitivo, renovación de certificados LDAP, delegación de aprobador, capacidad plan/real, mejoras de planilla, dashboard gerencial y módulo de conocimiento. Cualquier evolución requiere migración/prueba/documentación y no debe romper S.2.0.
