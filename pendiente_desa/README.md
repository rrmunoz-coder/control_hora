# Pendientes de desarrollo

Backlog actualizado después de ATLAS v0.3.0.

## Realizado en v0.3.0
- Revalidación, expiración y revocación de sesiones.
- Bloqueo temporal por usuario y rate limit persistente por origen.
- Configuración segura de HTTPS, cookies, LDAP, proxy y cabeceras.
- Errores seguros con correlación y logging técnico.
- Auditoría transaccional para el flujo semanal.
- Alcance por unidad en dashboard, proyectos, tareas, imputación y aprobaciones.
- Pruebas automáticas, CI, migración, validación y rollback.
- Flujo semanal hasta cierre y reapertura.

## P0 — acciones de despliegue
1. Rotar el secreto real y configurar certificado HTTPS/CA LDAP.
2. Revisar privilegios del usuario Oracle de runtime.
3. Convertir el repositorio a privado y proteger `main`.
4. Ejecutar las pruebas funcionales v0.3.0 en ambiente integrado.

## P1 — completar el núcleo operacional
1. Delegación temporal y reemplazante del aprobador.
2. Cierre mensual y reglas de corte.
3. Edición, clonación y vigencia integral de proyectos/tareas.
4. Planificación de capacidad y comparación plan/real.
5. Copiar semana, favoritos, recientes y fracciones de hora.
6. Tablero gerencial con privacidad y drill-down.
7. Notificaciones de semanas pendientes, observadas o vencidas.

## P2 — diferenciación
1. Módulo de conocimiento operacional.
2. Riesgo de dependencia por persona/tarea.
3. Evidencia económica de automatización y ahorro realizado.
4. Alertas de documentación vencida y tareas críticas sin procedimiento.

Ver archivos temáticos de esta carpeta.
