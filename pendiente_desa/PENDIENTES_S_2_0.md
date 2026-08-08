# Pendientes de desarrollo después de S.2.0

## Estado de S.2.0

La autenticación web LDAP, Oracle, CSRF/sesión y servicio Windows quedaron validados en el ambiente integrado. La release consolida el runtime que funciona; los siguientes puntos no deben confundirse con defectos del login ya resuelto.

## P0 — infraestructura y seguridad

1. **HTTPS frontal definitivo.** Actualmente existe un perfil de compatibilidad HTTP directo. Implementar proxy/terminador TLS, volver a `force_https=true` y `session_cookie_secure=true`.
2. **Renovar certificados LDAPS.** El ambiente necesita temporalmente `DEFAULT:@SECLEVEL=1` por certificados con clave legacy. Renovarlos y volver a `tls_ciphers=DEFAULT`.
3. **CA/ACL de servicio.** Confirmar que la CA corporativa y `config.ini` tengan ACL mínima para la cuenta de servicio.
4. **Privilegios Oracle.** Revisar permisos del usuario runtime y separar, si corresponde, cuenta de migración y cuenta de aplicación.
5. **Repositorio privado/protección de rama.** Mantener secretos fuera de Git y proteger `main`.
6. **Cookie propia.** Evaluar `SESSION_COOKIE_NAME=atlas_session` para reducir colisiones con otras aplicaciones Flask del mismo host.

## P1 — núcleo operacional

1. Delegación temporal/reemplazante de aprobador con vigencia y auditoría.
2. Cierre mensual y reglas de corte.
3. Plan de capacidad versus real, ausencias y sobreasignación.
4. Edición/clonación/vigencia integral de proyectos y tareas.
5. Copiar semana anterior, favoritos/recientes y fracciones de hora configurables.
6. Dashboard gerencial por unidad con privacidad y drill-down.
7. Notificaciones de semanas pendientes, observadas, rechazadas o vencidas.
8. Automatizar smoke test post-reinicio del servicio.

## P2 — diferenciación

1. Módulo de conocimiento operacional y gestión documental.
2. Riesgo de dependencia por persona/tarea.
3. Evidencia económica de automatización y ahorro realizado.
4. Alertas de documentación vencida y tareas críticas sin procedimiento.

## Puerta de entrada del módulo de conocimiento

No mezclar el módulo documental con estabilización S.2.0. Iniciar en rama independiente cuando no existan defectos P0, los P1 estén evaluados y se definan almacenamiento, antivirus, extensiones, tamaño máximo y retención.

Ver `05_MODULO_CONOCIMIENTO.md`.
