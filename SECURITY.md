# Seguridad

## Reporte
No publicar vulnerabilidades, credenciales ni configuración interna en issues públicos. Utilizar un canal privado del responsable del repositorio.

## Controles incorporados en v0.3.0
- Revocación y revalidación de sesiones.
- Timeout absoluto y por inactividad.
- Bloqueo temporal por usuario y dirección de origen.
- Configuración segura validada al arrancar.
- LDAP con verificación de certificado.
- HTTPS forzado y cookies seguras.
- CSP, HSTS y cabeceras defensivas.
- CSRF global.
- Errores con correlación sin exposición de Oracle.
- Auditoría transaccional para el flujo semanal.
- Autorización backend por unidad y rol.

## Controles obligatorios de despliegue
- Rotar el secreto Flask productivo por uno aleatorio de 32 bytes o más.
- Instalar certificado HTTPS y publicar detrás de un proxy confiable.
- Configurar la CA corporativa de LDAP.
- Mantener `config.ini` fuera del repositorio y con ACL restringida.
- Aplicar `sql/60_SEGURIDAD_APROBACIONES_V0_3.sql` antes del reinicio.
- Usar un usuario Oracle de runtime con privilegios mínimos.
- Mantener el repositorio privado y proteger `main`.

## Riesgo residual
Las pruebas automáticas no sustituyen las pruebas integradas contra Oracle, LDAP, proxy TLS y servicio Windows del ambiente objetivo. Consultar `docs/PRUEBAS_FUNCIONALES_V0_3_0.md`.
