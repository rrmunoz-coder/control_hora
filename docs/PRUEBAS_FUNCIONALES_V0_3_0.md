# Pruebas funcionales ATLAS v0.3.0

## Prerrequisitos
- Migración `60` aplicada y validación `61` sin observaciones.
- HTTPS operativo.
- Tres usuarios de prueba: `USUARIO`, `JEFE` y `ADMIN`.
- Usuario y jefe vinculados a la misma unidad; otra unidad fuera de su alcance.
- Semana de prueba sin datos críticos.

## 1. Sesiones y autenticación
1. Ingresar con credenciales válidas y navegar normalmente.
2. Dejar vencer el tiempo de inactividad reducido en un ambiente de prueba y comprobar redirección al login.
3. Cambiar el rol o desactivar al usuario desde ADMIN; su próxima solicitud debe cerrar la sesión.
4. Fallar el login hasta el umbral por usuario; comprobar bloqueo temporal y reinicio administrativo.
5. Probar múltiples usuarios inválidos desde el mismo origen hasta el umbral IP; comprobar bloqueo en `GT_LOGIN_RATE_LIMIT`.
6. Verificar que una indisponibilidad LDAP no incremente intentos como contraseña incorrecta.

## 2. HTTPS y cabeceras
1. Acceder por HTTP y confirmar redirección 307 a HTTPS.
2. Revisar cookie de sesión: `Secure`, `HttpOnly` y `SameSite`.
3. Confirmar CSP, HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `X-Request-ID`.
4. Confirmar que planilla, gráfico OPEX/CAPEX y barras de costos se visualizan sin errores CSP.

## 3. Errores y auditoría
1. Provocar una validación funcional y comprobar un mensaje legible sin SQL/ORA técnico.
2. Provocar un error controlado de infraestructura y comprobar código de referencia.
3. Buscar el mismo código en `logs/atlas.log`.
4. Enviar y aprobar una semana; comprobar eventos en `GT_AUDITORIA`.
5. Simular fallo de auditoría en ambiente aislado; la acción de aprobación debe hacer rollback.

## 4. Autorización por unidad
1. Un USUARIO solo debe ver tareas de su unidad, asignadas o proyectos donde sea responsable.
2. Un JEFE debe ver su unidad y unidades descendientes, no unidades ajenas.
3. Alterar manualmente IDs de unidad/proyecto/tarea en POST; el backend debe responder 403 o rechazar la operación.
4. El JEFE solo debe revisar semanas de su equipo accesible.
5. ADMIN debe conservar alcance global.

## 5. Flujo semanal
1. Guardar una semana completa: estado `PENDIENTE`.
2. Enviarla: estado `ENVIADO`; edición bloqueada.
3. Observar con comentario: estado `OBSERVADO`; edición habilitada.
4. Corregir, guardar y reenviar.
5. Rechazar con motivo: estado `RECHAZADO`; edición habilitada.
6. Reenviar y aprobar: estado `APROBADO`; horas con estado `APROBADA`.
7. Como ADMIN, cerrar: estado `CERRADO`.
8. Reabrir con motivo: estado `REABIERTO`; edición habilitada.
9. Confirmar auditoría de `ENVIAR`, `OBSERVAR`, `RECHAZAR`, `APROBAR`, `CERRAR` y `REABRIR`.

## 6. Regresión
- Login local de contingencia.
- Login LDAP.
- Dashboard.
- Usuarios y unidades ADMIN.
- Creación de proyecto y tarea dentro de alcance.
- Imputación semanal lunes a domingo.
- Costos y permisos financieros.
- Inicio, detención y reinicio del servicio Windows.

## Criterio de aprobación
La versión puede promoverse cuando no existan defectos P0/P1, la migración y rollback hayan sido ensayados en ambiente controlado, y las evidencias de seguridad, autorización y flujo semanal estén archivadas.
