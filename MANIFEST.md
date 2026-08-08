# Manifiesto ATLAS S.2.0

## Fuente

Release consolidada a partir del snapshot de producción recibido el 7 de agosto de 2026 y de la línea vigente del repositorio ATLAS v0.3.0.

## Incluye

- Código Flask completo, plantillas, CSS, JavaScript y WSGI Waitress.
- Autenticación LOCAL/LDAP, CSRF, sesiones revocables y rate limiting.
- Administración de usuarios, unidades, proyectos, tareas y aprobaciones.
- Planilla semanal e imputación directa a proyectos V3.
- Módulo de costos y score.
- SQL Oracle de modelo, migraciones, paquetes, validaciones y rollback disponibles.
- Scripts `50/51` de imputación directa recuperados en la raíz `sql/`.
- Migración de seguridad v0.3 compatible con DBeaver.
- Servicio Windows `ATLAS_Web` mediante NSSM externo.
- Configuración segura de ejemplo y perfil de compatibilidad del runtime validado.
- Pruebas automáticas, CI, herramientas de diagnóstico, documentación, prompt y backlog.

## Excluye deliberadamente

- `config.ini` real.
- Contraseñas, secretos Flask, DSN reales y nombres internos de infraestructura.
- `.venv`, cachés y logs.
- Copias históricas, hotfix ZIP y respaldos locales.
- `nssm.exe`, DLL y otros binarios de terceros.
- Datos productivos o información personal real.

## Instalabilidad

La aplicación puede instalarse desde un clon limpio con Python 3.12. NSSM se provee como prerrequisito externo. La instalación sobre una base ATLAS existente está documentada de punta a punta. Para crear un esquema Oracle completamente nuevo, los scripts de `sql/modelo/` deben ser aprobados por DBA porque el modelo histórico aún conserva su marca de revisión; no se presenta ese modelo como DDL productivo certificado sin evidencia del esquema real.
