# Pendientes de desarrollo

Backlog actualizado después de ATLAS v0.3.0.

## Decisión vigente

Antes de incorporar nuevos módulos se ejecutarán las pruebas funcionales e integradas de v0.3.0. El módulo de conocimiento operacional y gestión documental queda formalmente registrado, pero **no se desarrollará ni se mezclará con el despliegue actual** hasta cerrar esas pruebas.

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
5. Registrar defectos encontrados y resolver o aceptar formalmente los P0/P1.

## P1 — completar el núcleo operacional
1. Delegación temporal y reemplazante del aprobador.
2. Cierre mensual y reglas de corte.
3. Edición, clonación y vigencia integral de proyectos/tareas.
4. Planificación de capacidad y comparación plan/real.
5. Copiar semana, favoritos, recientes y fracciones de hora.
6. Tablero gerencial con privacidad y drill-down.
7. Notificaciones de semanas pendientes, observadas o vencidas.

## P2 — diferenciación
1. Módulo de conocimiento operacional y gestión documental, versión objetivo sugerida `v0.4.0`.
2. Textos y archivos vinculados con tareas, acciones, procesos, proyectos, servicios, actividades y unidades.
3. Versionamiento, flujo documental, búsqueda, permisos y auditoría.
4. Riesgo de dependencia por persona/tarea.
5. Evidencia económica de automatización y ahorro realizado.
6. Alertas de documentación vencida y tareas críticas sin procedimiento.

El requerimiento completo, sus controles de seguridad y sus criterios de aceptación están en `05_MODULO_CONOCIMIENTO.md`.

## Puerta de entrada para v0.4.0

El desarrollo del módulo de conocimiento solo debe iniciarse después de:

- Ejecutar la pauta funcional v0.3.0.
- Cerrar defectos P0.
- Evaluar defectos P1.
- Validar el flujo con USUARIO, JEFE y ADMIN.
- Confirmar almacenamiento, antivirus, extensiones y retención documental.

Ver archivos temáticos de esta carpeta.
