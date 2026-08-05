# Calidad técnica y operación

## Realizado v0.3.0
- [x] Pruebas de configuración segura, sesiones, rutas y flujo.
- [x] Verificación estática de autorización por rutas.
- [x] CI para higiene, compilación y pytest.
- [x] Migración idempotente, validación y rollback lógico.
- [x] Logging rotativo y correlación de solicitud.
- [x] Paquete reproducible sin secretos ni residuos.

## Pendiente
- [ ] Refactorizar `costs/service.py` y dividir consultas/responsabilidades.
- [ ] Aumentar cobertura con integración de Oracle y LDAP simulados.
- [ ] Pruebas 200/302/403 por cada ruta y perfil.
- [ ] Tabla formal de versión de esquema y ejecutor de migraciones.
- [ ] Ensayar rollback por release en ambiente controlado.
- [ ] Logging JSON y envío a plataforma centralizada.
- [ ] Health checks de app, Oracle y LDAP sin revelar secretos.
- [ ] Métricas de pool, latencia, errores y disponibilidad.
- [ ] Backups y prueba de restauración.
- [ ] Separar configuración formal por ambiente.
- [ ] Eliminar archivos legacy del servidor después del respaldo.
