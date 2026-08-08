# Seguridad

## Controles incorporados

ATLAS mantiene CSRF global, revalidación/revocación de sesión, timeout absoluto/inactividad, rate limiting por usuario/origen, autorización backend por unidad/rol, errores correlacionados, auditoría transaccional, CSP y validación de certificado LDAP.

## Perfil recomendado

Producción debe operar detrás de HTTPS con `force_https=true`, `session_cookie_secure=true`, proxy confiable correctamente configurado y `tls_ciphers=DEFAULT` para LDAP.

## Compatibilidad temporal S.2.0

El runtime validado requirió `DEFAULT:@SECLEVEL=1` porque el certificado LDAPS corporativo fue rechazado por OpenSSL con `EE certificate key too weak`. Se mantiene `validate_certificate=true` y `allow_legacy_ciphers=false`. Esta excepción debe retirarse cuando infraestructura renueve los certificados.

El perfil HTTP directo (`force_https=false`, cookie no Secure) existe solo para reproducir la instalación integrada actual mientras no exista terminación TLS. No debe considerarse el estado final de seguridad.

## Controles de despliegue

- Secreto Flask aleatorio >=32 bytes.
- `config.ini` fuera de Git y con ACL mínima.
- CA LDAP confiable y accesible por la cuenta del servicio.
- Usuario Oracle runtime con privilegios mínimos.
- Repositorio privado/protegido.
- Revisar `pendiente_desa/PENDIENTES_S_2_0.md`.
