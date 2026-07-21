# Prompt de construcción ATLAS v0.1.0

Actúa como arquitecto senior y desarrollador full-stack de ATLAS, un sistema web interno para gestión de tiempo, capacidad, proyectos, servicios, tareas, costos y oportunidades de automatización.

## Contexto

- Plataforma: Flask + Oracle + LDAP + Windows Service.
- Base de datos: Oracle 12.2 / SCBILL.
- Entorno: Windows Server.
- Ejecución productiva: Waitress como servicio Windows.
- Restricción crítica: algunas tablas Oracle pueden estar comprimidas, por lo que no se deben agregar columnas físicas sin validar compatibilidad.

## Objetivo

Generar una versión limpia, instalable y versionada de ATLAS, sin secretos ni residuos locales, que permita:

- Autenticación LDAP.
- Administración de usuarios.
- Administración de unidades organizacionales.
- Administración de proyectos y servicios.
- Administración de tareas.
- Imputación semanal de lunes a domingo.
- Imputación directa a proyectos usando tarea técnica `PRYGEN_<ID_PROYECTO>`.
- Base de análisis financiero-operacional.

## Reglas técnicas

- No versionar `config.ini` real.
- No versionar `.venv`, cachés, logs ni respaldos.
- No incluir credenciales.
- Mantener `config.ini.example` con placeholders.
- Entregar SQL ordenado e idempotente cuando sea posible.
- Usar paquetes PL/SQL para reglas críticas.
- Mantener compatibilidad con tablas comprimidas.
- Generar manual de instalación, manual de uso, arquitectura, changelog y checksums.

## Resultado esperado

Un paquete de instalación y un repositorio con estructura estándar por versión, listo para pruebas integrales y evolución controlada.
