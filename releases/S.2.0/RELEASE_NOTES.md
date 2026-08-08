# ATLAS S.2.0 — Release Notes

Fecha: 2026-08-07

## Qué representa

Snapshot estable y completo de la aplicación que quedó operativa con login LDAP web, Oracle, CSRF/sesión y servicio Windows. Baseline funcional: v0.3.0.

## Correcciones consolidadas

- Compatibilidad temporal LDAPS `DEFAULT:@SECLEVEL=1` manteniendo validación de certificado.
- Reinicio/documentación de `ATLAS_Web` para recargar configuración.
- Diagnóstico correcto de venv: NSSM apunta a `.venv` aunque WMIC pueda mostrar el Python base.
- SQL 50/51 incorporados a la distribución principal.
- SQL 60 compatible con DBeaver sin `SET DEFINE OFF`.

## Instalación

Seguir `docs/INSTALACION_S_2_0.md` y no copiar `config.ini`, `.venv`, logs ni paquetes históricos desde producción.

## Deuda conocida

HTTPS frontal definitivo y renovación de certificados LDAPS para volver a `tls_ciphers=DEFAULT`.
