# Seguridad

- [ ] Revalidar usuario activo, rol y permisos en cada solicitud o mediante caché corto/versionado.
- [ ] Invalidar todas las sesiones cuando se desactiva un usuario o cambia su rol.
- [ ] Configurar timeout por inactividad y duración máxima.
- [ ] Implementar rate limiting y bloqueo temporal por usuario/IP.
- [ ] Eliminar cipher débil como default; documentar excepción temporal.
- [ ] Rotar el secreto Flask productivo.
- [ ] Publicar con HTTPS y HSTS.
- [ ] Incorporar CSP y cabeceras defensivas.
- [ ] Sustituir exposición de excepciones por códigos/mensajes controlados.
- [ ] Registrar fallos de auditoría y definir cuándo una operación debe abortar.
- [ ] Validar proxies confiables antes de usar `X-Forwarded-For`.
- [ ] Revisar privilegios Oracle y separar usuario de migraciones del usuario de runtime.
- [ ] Activar secret scanning, Dependabot y protección de rama.
