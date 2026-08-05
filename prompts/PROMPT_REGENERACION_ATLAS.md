# PROMPT MAESTRO — REGENERAR Y EVOLUCIONAR ATLAS

## Rol
Actúa como arquitecto senior, desarrollador full-stack, especialista Oracle y revisor de seguridad. Debes generar código completo, ejecutable, probado y documentado; no entregues pseudocódigo ni omitas archivos esenciales.

## Producto
ATLAS es un sistema web interno para transformar el registro de trabajo en capacidad, costo, eficiencia, riesgo operacional y oportunidades de automatización.

## Stack obligatorio
- Python 3.12+.
- Flask 3, Flask-WTF y Jinja.
- Oracle 12c/compatible mediante `python-oracledb`.
- LDAP corporativo con `ldap3` por LDAPS o StartTLS.
- Waitress como servidor WSGI.
- Windows Service mediante NSSM externo, sin versionar binarios.
- JavaScript y CSS sin framework obligatorio.

## Arquitectura actual que debes preservar
- Application factory `create_app`.
- Blueprints: auth, dashboard, users, units, projects, tasks, time_entries y costs.
- Servicios Python por dominio.
- Pool Oracle y transacciones explícitas.
- Packages PL/SQL para reglas críticas.
- CSRF global.
- `config.ini` externo y `config.ini.example` sanitizado.

## Modelo funcional
- Unidad organizacional: dueño/responsable.
- Proyecto o servicio: agrupador del trabajo.
- Tarea: unidad imputable.
- Imputación: usuario, tarea, fecha, horas, comentario y estado.
- Centro de costo: dimensión financiera independiente.
- Actividad: agrupación operacional para costos y automatización.
- Mapeos: tarea→actividad y actividad→centro de costo, con porcentaje y vigencia.
- Categoría de costo, tarifa mensual y costo hora.
- Score: impacto, automatización, eficiencia, prioridad, esfuerzo y ahorro potencial.

## Reglas que no debes romper
1. La semana se maneja de lunes a domingo.
2. Los proyectos pueden imputarse directamente mediante una tarea técnica `PRYGEN_<ID_PROYECTO>`; no agregar una columna física `ES_TAREA_PROYECTO` sin validar compresión Oracle.
3. Las tablas pueden estar comprimidas; evitar ALTER incompatibles y entregar migración/rollback.
4. No eliminar físicamente registros con historial; usar vigencia/estado.
5. Todas las consultas con datos del usuario deben usar binds Oracle.
6. La autorización siempre se valida en backend.
7. No versionar secretos, binarios, logs, `.venv`, copias históricas ni datos reales.

## Seguridad obligatoria en la regeneración
- HTTPS y cookies `Secure`, `HttpOnly`, `SameSite`.
- Secreto Flask aleatorio de 32 bytes o más.
- Rotación de ID de sesión después del login.
- Timeout absoluto e inactividad.
- Revalidar en servidor que el usuario siga activo y que su rol/permisos no hayan cambiado.
- Bloqueo progresivo/rate limiting de login con auditoría.
- LDAP con validación de certificado; no usar `DEFAULT:@SECLEVEL=0` por defecto.
- Mensajes amigables al usuario y logs técnicos estructurados sin contraseñas.
- Auditoría confiable; no ignorar fallos críticos silenciosamente.
- Cabeceras CSP, HSTS, X-Content-Type-Options, Referrer-Policy y frame-ancestors.
- Privilegios Oracle mínimos.
- Protección contra IDOR y autorización por unidad/proyecto.

## Evolución funcional prioritaria
1. Flujo de semana: borrador, enviada, observada, corregida, aprobada, cerrada y reapertura auditada.
2. Capacidad planificada versus real, ausencias y sobreasignación.
3. Edición y vigencia de proyectos/tareas, no solo creación.
4. Copiar semana anterior, tareas favoritas/recientes y horas fraccionarias configurables.
5. Dashboard de gestión por unidad con drill-down y privacidad.
6. Conocimiento operacional vinculado a tarea/actividad/servicio.

## Módulo de conocimiento operacional
Implementar un MVP, no un wiki genérico:
- Tipos: procedimiento, checklist/control, incidente-solución, script/herramienta y regla de negocio.
- Campos: título, resumen, contenido, dueño, revisor, criticidad, estado, versión, vigencia, próxima revisión, etiquetas y relaciones.
- Relacionar con unidad, proyecto/servicio, tarea y actividad.
- Estados: borrador, revisión, publicado, requiere actualización y obsoleto.
- Versiones publicadas inmutables, historial y permisos heredables.
- Buscador que respete permisos.
- Métricas: tareas críticas sin documentación, conocimiento concentrado en una persona, artículos vencidos y candidatos a automatización.

## Calidad de código
- PEP 8, type hints y funciones pequeñas.
- Separar SQL largo en repositorios/servicios legibles.
- No compactar múltiples sentencias en una línea.
- Pruebas unitarias y de integración con mocks para Oracle/LDAP.
- Pruebas de autorización por cada ruta.
- Fixtures sin datos personales.
- Logging estructurado.
- Dependencias fijadas y CI.

## Entregables obligatorios
1. Árbol completo del repositorio.
2. Todos los archivos fuente, plantillas, CSS, JS y SQL.
3. Migraciones numeradas y rollback.
4. `config.ini.example` sin valores reales.
5. `requirements.txt` y dependencias de desarrollo.
6. Pruebas ejecutables.
7. Manual de instalación, uso, seguridad y operación.
8. `CHANGELOG`, `VERSION`, release notes y checksum.
9. Script de higiene y empaquetado.
10. Carpeta `pendiente_desa` actualizada, marcando realizado, pendiente y descartado.

## Criterios de aceptación
- `python -m compileall` sin errores.
- `pytest` exitoso.
- Ninguna ruta privada sin decorador de seguridad.
- Ningún formulario POST sin CSRF.
- Ninguna consulta construida desde entrada del usuario sin whitelist/binds.
- Ningún secreto o dato real en el repositorio.
- Aplicación instalable desde un clon limpio.
- Migraciones repetibles o con detección de estado.
- Rollback documentado.

## Forma de trabajo
Primero analiza el repositorio existente y presenta un plan de cambios. Luego genera una versión completa en una rama nueva. Conserva compatibilidad de datos y no inventes tablas o reglas sin documentar la decisión. Toda modificación funcional debe incluir prueba, migración si corresponde y actualización del changelog.
