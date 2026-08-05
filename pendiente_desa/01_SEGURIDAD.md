# Seguridad

## Realizado v0.3.0
- [x] Revalidar usuario activo, rol y versión de sesión.
- [x] Invalidar sesiones al desactivar o modificar usuario.
- [x] Timeout por inactividad y duración máxima.
- [x] Bloqueo temporal por usuario y dirección de origen.
- [x] Eliminar `SECLEVEL=0` como valor por defecto.
- [x] Validar secreto Flask mínimo de 32 bytes.
- [x] Soportar HTTPS forzado, cookies seguras y HSTS.
- [x] Incorporar CSP y cabeceras defensivas.
- [x] Sustituir exposición de excepciones por mensajes controlados.
- [x] Registrar fallos de auditoría y hacer atómicas las aprobaciones críticas.
- [x] Aceptar cabeceras de proxy únicamente cuando se configura ProxyFix.

## Pendiente de despliegue o gobierno
- [ ] Rotar el secreto Flask real en producción.
- [ ] Instalar y validar HTTPS y CA LDAP en infraestructura.
- [ ] Revisar privilegios Oracle y separar migraciones de runtime.
- [ ] Activar secret scanning, Dependabot y protección de rama.
- [ ] Revisar periódicamente retención de IP y auditoría.
- [ ] Ejecutar pentest y revisión de dependencias en ambiente corporativo.
