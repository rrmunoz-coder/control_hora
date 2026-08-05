# Análisis del código productivo — 2026-08-05

## Alcance verificable

Se analizaron estáticamente 29 archivos Python (4.018 líneas), 35 rutas Flask, 26 plantillas y 36 scripts SQL. El código Python compila. La prueba estructural existente pasa aislada. No se ejecutó contra Oracle o LDAP productivos.

## Funcionalidad real encontrada

1. Autenticación local y LDAP con bind directo, múltiples controladores, LDAPS/StartTLS y registro de éxitos/fallos.
2. Sesiones Flask con rol incorporado y decoradores de autenticación/autorización.
3. Administración de usuarios, jefaturas, roles, unidad principal y control LDAP.
4. Jerarquía organizacional con validaciones Oracle y desactivación controlada.
5. Proyectos/servicios y creación de tarea técnica `PRYGEN_<ID>` para imputación directa.
6. Tareas con clasificación OPEX/CAPEX, prioridad, responsable y estimación.
7. Planilla semanal de siete días, modalidades, comentarios y persistencia mediante `PKG_GT_IMPUTACION`.
8. Dashboard individual de horas, alertas y distribución OPEX/CAPEX.
9. Módulo financiero-operacional de actividades, centros, costos, mapeos, FTE, automatización, eficiencia y permisos.
10. Auditoría base y servicio Windows con Waitress/NSSM.

## Fortalezas

- Separación razonable por Blueprints y servicios.
- Consultas mayoritariamente parametrizadas.
- CSRF global con Flask-WTF.
- Autorización del módulo de costos en backend, no solo en la interfaz.
- Pool Oracle y transacciones controladas por context manager.
- Validaciones de jerarquía y reglas críticas reforzadas en Oracle.
- Modelo de costo/automatización claramente más avanzado que un timesheet básico.

## Hallazgos críticos y altos

### S1 — Sesiones no se invalidan al desactivar o cambiar un usuario
Los decoradores confían en `session['id_usuario']` y `session['rol_codigo']`. Una sesión ya emitida puede seguir vigente hasta cerrar el navegador aunque el usuario sea desactivado o cambie de rol. Se requiere revalidación periódica o versión de sesión en servidor.

### S2 — Intentos fallidos sin bloqueo ni rate limiting
El sistema incrementa `INTENTOS_FALLIDOS`, pero la autenticación no impide nuevos intentos al superar un umbral. Tampoco hay limitación por IP/usuario.

### S3 — Configuración TLS débil disponible como valor por defecto en código
`LDAP_TLS_CIPHERS` usa `DEFAULT:@SECLEVEL=0` cuando no se configura. Esto reduce la política criptográfica. Debe ser una excepción explícita y temporal, no un default.

### S4 — Despliegue HTTP y cookies inseguras posibles
La seguridad de la cookie depende de `config.ini`; la copia recibida tenía `session_cookie_secure` desactivado. Waitress no entrega TLS por sí solo. Debe existir proxy HTTPS o terminación TLS controlada.

### S5 — Secreto Flask productivo débil
La configuración recibida usa un secreto de longitud insuficiente para una política robusta. Debe rotarse por un valor aleatorio de al menos 32 bytes; no se versionó el valor.

### S6 — Errores técnicos expuestos en interfaz
Varias rutas muestran `flash(str(exc))`. Esto puede revelar nombres de tablas, packages, restricciones y datos técnicos de Oracle. Se requiere mensaje amigable al usuario y logging estructurado del detalle.

### S7 — Auditoría silenciosa y no transaccional
`record_event` captura toda excepción y la ignora. Una operación puede completarse sin evidencia de auditoría. Además, confía en `X-Forwarded-For` sin una lista de proxies confiables.

### S8 — Repositorio público
El repositorio actual es público. Aunque se excluyeron secretos, el código contiene lógica interna de capacidad, costos y automatización. Se recomienda migrarlo a privado antes de ampliar su uso.

## Hallazgos medios

- `JEFE` puede crear proyectos y tareas usando catálogos globales; no se verifica alcance por unidad.
- Todos los usuarios autenticados pueden listar proyectos y tareas globales.
- No existe cierre/aprobación/reapertura formal de semanas en la capa web actual.
- Horas limitadas a enteros; no admite 0,25 o 0,5 horas.
- No hay timeout de sesión, rotación de sesión por cambios de privilegio ni “remember me” gobernado.
- No se observan cabeceras CSP/HSTS/X-Content-Type-Options configuradas por la aplicación.
- Dependencias originales no estaban fijadas; se agregó baseline reproducible.
- `costs/service.py` tiene líneas de hasta 1.026 caracteres y funciones compactadas, dificultando revisión y pruebas.
- Los tests Python solo validaban existencia de tres archivos; la cobertura funcional es prácticamente nula.
- La distribución productiva incluía múltiples copias históricas, `.venv`, logs, ZIP, binarios y respaldos.

## Usabilidad observada

La planilla semanal tiene un flujo simple y adecuado para adopción. Las mejoras prioritarias son copiar semana anterior, favoritas/recientes, horas fraccionarias configurables, estado de semana y aprobación. Los mantenedores necesitan edición completa de proyectos/tareas, búsqueda global, filtros persistentes y mensajes de error no técnicos.

## Evaluación del módulo de conocimiento

Es relevante y diferenciador si se vincula a tareas, actividades, servicios, costos y riesgo de dependencia. No debe ser un wiki genérico. El MVP recomendado está definido en `pendiente_desa/05_MODULO_CONOCIMIENTO.md`.

## Dictamen

ATLAS ya es una aplicación funcional con una capa financiero-operacional diferenciadora. Su siguiente salto no depende de agregar muchas pantallas, sino de fortalecer seguridad, gobierno de sesiones, pruebas, aprobaciones y trazabilidad; luego incorporar conocimiento operacional vinculado al trabajo real.
