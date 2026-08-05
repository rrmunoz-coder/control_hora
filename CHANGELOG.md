# Changelog

## v0.3.0 — 2026-08-05

### Seguridad y autenticación
- Revalidación periódica del usuario, rol, estado y versión de sesión.
- Revocación inmediata de sesiones al modificar o desactivar una cuenta.
- Timeout por inactividad y duración máxima absoluta.
- Bloqueo temporal por usuario y límite persistente por dirección de origen.
- Secreto Flask mínimo de 32 bytes y validación de configuración al iniciar.
- LDAP con certificado validado y rechazo de `SECLEVEL=0` salvo excepción explícita.
- HTTPS forzado, cookies `Secure`/`HttpOnly`/`SameSite`, HSTS y ProxyFix controlado.
- CSP sin scripts, JSON ni estilos inline en las plantillas entregadas.

### Errores y auditoría
- Mensajes funcionales seguros y código de correlación para soporte.
- Detalle técnico solo en logs rotativos.
- `X-Request-ID` externo aceptado únicamente detrás de proxy confiable.
- Auditoría de envío, aprobación, observación, rechazo, cierre y reapertura dentro de la misma transacción de negocio.

### Autorización
- Alcance de unidades y descendientes para jefaturas.
- Validación backend al crear proyectos y tareas.
- Catálogos, dashboard e imputación filtrados por unidad, responsabilidad o asignación.
- Revisión de semanas restringida al equipo accesible del jefe; ADMIN mantiene alcance global.

### Flujo semanal
- Estados: `PENDIENTE`, `ENVIADO`, `OBSERVADO`, `RECHAZADO`, `APROBADO`, `CERRADO` y `REABIERTO`.
- Envío de semana con bloqueo de edición.
- Aprobación, observación y rechazo por jefe o administrador autorizado.
- Cierre y reapertura administrativa con motivo y auditoría.
- Semanas observadas, rechazadas o reabiertas vuelven a edición y pueden reenviarse.

### Calidad
- Migración idempotente `60_SEGURIDAD_APROBACIONES_V0_3.sql`.
- Validación SQL y rollback lógico seguro.
- Pruebas de configuración, sesiones, rutas, CSP, migración, flujo y alcance.
- CI actualizado para compilar, validar higiene y ejecutar `pytest`.

## v0.2.0 — 2026-08-05

### Incorporado
- Código Flask productivo y plantillas web.
- Autenticación local y LDAP.
- Administración de usuarios, roles, jefaturas y unidades.
- Proyectos, tareas e imputación semanal de siete días.
- Costos, centros de costo, score de automatización, eficiencia y permisos.
- Scripts Oracle, utilitarios y servicio Windows mediante NSSM externo.
- Pruebas estáticas, CI y validación de higiene.
- Prompt integral para regeneración en otra IA.
- Carpeta `pendiente_desa` con backlog priorizado.

### Seguridad e higiene
- Excluidos `config.ini`, `.venv`, logs, cachés, respaldos, ZIP y ejecutables.
- Configuración de ejemplo reemplazada por valores genéricos.
- Dependencias directas fijadas según el entorno productivo recibido.

## v0.1.0 — 2026-07-21
- Base documental inicial y estándar de versionado.
