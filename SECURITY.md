# Seguridad

## Reporte
No publicar vulnerabilidades ni secretos en issues públicos. Usar un canal privado del responsable del repositorio.

## Controles mínimos de despliegue
- HTTPS obligatorio.
- `session_cookie_secure=true`.
- Certificado LDAP validado.
- Secreto Flask aleatorio de al menos 32 bytes.
- Usuario Oracle con privilegios mínimos.
- `config.ini` fuera del repositorio y ACL restringida.
- Repositorio privado y protección de rama.

## Riesgos conocidos
Consultar `pendiente_desa/01_SEGURIDAD.md` y el análisis técnico de `docs/`.
