# Release notes v0.3.0

Versión candidata para pruebas funcionales que implementa los seis frentes priorizados:

1. Sesiones y autenticación endurecidas.
2. HTTPS y configuración segura.
3. Errores correlacionados y auditoría confiable.
4. Autorización operacional por unidad.
5. Pruebas automatizadas y CI.
6. Flujo semanal de envío, revisión, aprobación, cierre y reapertura.

## Instalación
Aplicar `sql/60_SEGURIDAD_APROBACIONES_V0_3.sql` antes de iniciar el código. Validar con el script `61` y seguir `docs/ACTUALIZACION_V0_3_0.md`.

## Estado
Código listo para despliegue en ambiente de pruebas funcionales. No promover directamente a producción sin ejecutar la pauta `docs/PRUEBAS_FUNCIONALES_V0_3_0.md`.
