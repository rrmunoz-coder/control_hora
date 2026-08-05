# Manifiesto v0.3.0

Incluye:
- Código Flask, plantillas, CSS y JavaScript.
- Autenticación local/LDAP, control de sesión y límite de intentos.
- Autorización operacional por unidad.
- Flujo semanal y módulo de aprobaciones.
- Módulos de usuarios, unidades, proyectos, tareas, costos y dashboard.
- Migración, validación y rollback de v0.3.0.
- Pruebas automáticas, CI, documentación, prompt regenerador y backlog.

Excluye expresamente:
- `config.ini` real y secretos.
- `.venv`, cachés, logs y resultados locales de pruebas.
- Copias históricas, respaldos y hotfix empaquetados.
- `nssm.exe`, DLL, ejecutables y ZIP de terceros.
- Datos productivos o archivos con información personal real.

La migración v0.3.0 debe ejecutarse antes de iniciar esta versión de la aplicación.
