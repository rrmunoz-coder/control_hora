# Actualización ATLAS v0.3.0

## Orden obligatorio
1. Respaldar código, `config.ini` y objetos Oracle ATLAS.
2. Detener el servicio ATLAS.
3. Aplicar `sql/60_SEGURIDAD_APROBACIONES_V0_3.sql` como propietario de los objetos.
4. Ejecutar `sql/61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql` y guardar evidencia.
5. Copiar la versión v0.3.0 sin reemplazar el `config.ini` productivo.
6. Incorporar al `config.ini` las nuevas claves de `[security]` usando `config.ini.example` como guía.
7. Rotar `flask.secret_key` y configurar HTTPS/CA LDAP.
8. Instalar dependencias, ejecutar pruebas y reiniciar el servicio.
9. Ejecutar la pauta funcional de esta versión.

## Nuevas claves
```ini
[security]
force_https = true
trust_proxy_headers = true
trusted_proxy_hops = 1
session_idle_minutes = 30
session_absolute_minutes = 720
session_validation_seconds = 120
max_failed_logins = 5
max_failed_logins_ip = 20
login_rate_window_minutes = 15
login_lock_minutes = 15
hsts_seconds = 31536000
```

## Consideraciones
- Con `force_https=true`, una prueba directa por HTTP será redirigida a HTTPS.
- `trust_proxy_headers=true` solo debe usarse cuando el servidor reciba tráfico exclusivamente desde el proxy definido.
- La cuenta LDAP debe validar el certificado mediante la CA corporativa.
- La migración crea `GT_LOGIN_RATE_LIMIT` y amplía los estados y acciones de auditoría.
- v0.3.0 no debe iniciarse antes de aplicar la migración.

## Rollback
1. Detener ATLAS.
2. Ejecutar `sql/62_ROLLBACK_SEGURIDAD_APROBACIONES_V0_3.sql`.
3. Restaurar el código/tag v0.2.0 y su configuración compatible.
4. Reiniciar y validar login/imputación.

El rollback se detendrá si existen semanas `CERRADO` o eventos `CERRAR`, para evitar pérdida semántica. Las columnas de sesión y la tabla de rate limit permanecen porque son compatibles hacia atrás y eliminarlas físicamente agrega riesgo.
