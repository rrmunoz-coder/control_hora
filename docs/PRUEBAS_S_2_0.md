# Pruebas de aceptación — ATLAS S.2.0

## Técnicas

```cmd
.venv\Scripts\python.exe scripts\validar_release.py
.venv\Scripts\python.exe scripts\validar_higiene.py
.venv\Scripts\python.exe -m compileall -q atlas tests *.py tools
.venv\Scripts\python.exe -m pytest -q
```

## Integración

1. `tools\test_oracle_connection.py` → `Conexion Oracle: OK`.
2. `tools\test_ldap_transport.py` → TCP/TLS OK para al menos un controlador.
3. `tools\test_ldap_bind.py` → `STATUS = SUCCESS`.
4. `service\diagnose_service.cmd` → servicio `RUNNING`, `.venv`, entry point correcto y puerto escuchando.
5. Login web LDAP → dashboard.

## Funcionales mínimas

- ADMIN accede a mantenedores.
- JEFE solo accede al alcance de su unidad/descendientes.
- USUARIO ve e imputa únicamente opciones autorizadas.
- Guardar semana lunes-domingo.
- Enviar semana y bloquear edición.
- Observar/rechazar y devolver a edición.
- Aprobar/cerrar y reabrir con auditoría.
- Imputar a proyecto mediante tarea `PRYGEN_<ID>`.
- Costos y dashboard cargan sin excepciones.

## Base de datos

- `sql/51_VALIDAR_IMPUTACION_DIRECTA_PROYECTOS_V3.sql`: faltantes/conflictos en 0.
- `sql/61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql`: estructuras válidas; `ORIGENES_BLOQUEADOS=0` es esperado sin bloqueos.
