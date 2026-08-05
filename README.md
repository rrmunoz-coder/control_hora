# ATLAS — Gestión de capacidad, costos y automatización

ATLAS es una aplicación web interna que transforma el registro semanal del trabajo en información de capacidad, costo operativo, trazabilidad y oportunidades de automatización.

## Versión

`v0.3.0` — candidato para pruebas funcionales controladas, 5 de agosto de 2026.

## Funcionalidad incluida

- Login corporativo LDAP y usuario local de contingencia.
- Sesiones revalidadas, revocables y con expiración.
- Bloqueo por intentos fallidos de usuario y dirección de origen.
- Usuarios, roles, jefaturas, unidades y permisos.
- Alcance operacional por unidad y descendientes.
- Proyectos/servicios y tareas.
- Planilla semanal de lunes a domingo y modalidades de día.
- Flujo de envío, observación, rechazo, aprobación, cierre y reapertura.
- Imputación directa a proyecto mediante tarea técnica `PRYGEN_<ID_PROYECTO>`.
- Dashboard personal.
- Costos por categoría, centro de costo y período.
- Mapeo tarea → actividad y actividad → centro de costo.
- Score de impacto, automatización, prioridad y eficiencia.
- Auditoría y ejecución productiva con Waitress como servicio Windows.

## Arquitectura

```text
Navegador HTTPS
  → proxy TLS confiable
  → Flask / Waitress
  → servicios Python y autorización backend
  → pool python-oracledb
  → packages, vistas y tablas Oracle
```

## Actualización desde v0.2.0

Aplicar primero:

```text
sql/60_SEGURIDAD_APROBACIONES_V0_3.sql
sql/61_VALIDAR_SEGURIDAD_APROBACIONES_V0_3.sql
```

Después actualizar `config.ini` usando `config.ini.example` y seguir `docs/ACTUALIZACION_V0_3_0.md`.

## Validación

```bash
python scripts/validar_higiene.py
python -m compileall -q atlas tests *.py tools
pytest -q
python scripts/build_package.py
```

## Documentos clave

- `docs/ACTUALIZACION_V0_3_0.md`
- `docs/PRUEBAS_FUNCIONALES_V0_3_0.md`
- `docs/ANALISIS_CODIGO_PRODUCCION_2026-08-05.md`
- `prompts/PROMPT_REGENERACION_ATLAS.md`
- `pendiente_desa/README.md`
- `SECURITY.md`

## Seguridad

El repositorio no debe contener secretos ni datos reales. `config.ini`, entornos, logs, respaldos y binarios externos están excluidos. Se recomienda mantener el repositorio privado o bajo una organización corporativa con acceso controlado y protección de rama.
