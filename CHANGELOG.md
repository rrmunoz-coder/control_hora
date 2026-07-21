# Changelog

## v0.1.0 - 2026-07-21

### Incluye

- Base web Flask de ATLAS.
- Conexión Oracle con configuración externa.
- Autenticación LDAP y usuario local de contingencia.
- Administración de usuarios.
- Administración de unidades organizacionales.
- Administración de proyectos y tareas.
- Imputación semanal de lunes a domingo.
- Modalidades de día: presencial, remoto, vacaciones, compensatorio, permiso flexible, progresivos, licencia médica y descanso semanal.
- Imputación directa a proyectos mediante tarea técnica `PRYGEN_<ID_PROYECTO>`.
- Compatibilidad con tablas comprimidas Oracle: no se agrega columna física `ES_TAREA_PROYECTO`.
- Base de módulo de costos, centros de costo, score y permisos.
- Servicio Windows.
- Manuales, prompt de construcción y estructura estándar de versionado.

### Limpieza aplicada

- Excluido `.venv`.
- Excluidos `__pycache__` y `.pyc`.
- Excluidos logs, respaldos y archivos temporales.
- Excluido `config.ini` real.
- Excluidos paquetes históricos y binarios no necesarios.

### Nota técnica

La versión usa `PRYGEN_<ID_PROYECTO>` para representar proyectos en la planilla sin modificar la estructura de `GT_TAREA`, evitando el error `ORA-39726` en tablas comprimidas.
