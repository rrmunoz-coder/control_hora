# ATLAS — Gestión de capacidad, costos y automatización

ATLAS es una aplicación web interna que transforma el registro semanal del trabajo en información de capacidad, costo operativo y oportunidades de automatización.

## Versión

`v0.2.0` — baseline sanitizado del código productivo recibido el 5 de agosto de 2026.

## Funcionalidad incluida

- Login corporativo LDAP y usuario local de contingencia.
- Usuarios, roles, jefaturas, unidades y permisos.
- Proyectos/servicios y tareas.
- Planilla semanal de lunes a domingo y modalidades de día.
- Imputación directa a proyecto mediante tarea técnica `PRYGEN_<ID_PROYECTO>`.
- Dashboard personal.
- Costos por categoría, centro de costo y período.
- Mapeo tarea → actividad y actividad → centro de costo.
- Score de impacto, automatización, prioridad y eficiencia.
- Auditoría base y ejecución productiva con Waitress como servicio Windows.

## Arquitectura

```text
Navegador
  → Flask / Jinja / JavaScript
  → servicios Python
  → pool python-oracledb
  → packages, vistas y tablas Oracle
```

## Instalación resumida

1. Instalar Python 3.12 o compatible y Oracle Instant Client cuando se use Thick mode.
2. Crear entorno: `python -m venv .venv`.
3. Instalar: `pip install -r requirements.txt`.
4. Copiar `config.ini.example` como `config.ini` y completar valores locales.
5. Ejecutar los SQL de `sql/` según la instalación requerida.
6. Validar con `python -m compileall -q atlas *.py tools` y `pytest -q`.
7. Ejecutar `run_dev.cmd` para prueba o instalar el servicio desde `service/install_service.cmd`.

`nssm.exe` no se versiona: debe descargarse desde su fuente oficial o estar disponible en PATH.

## Seguridad

El repositorio no debe contener secretos ni datos reales. Antes de publicar una versión, ejecutar:

```bash
python scripts/validar_higiene.py
pytest -q
python scripts/build_package.py
```

## Documentos clave

- `docs/ANALISIS_CODIGO_PRODUCCION_2026-08-05.md`
- `prompts/PROMPT_REGENERACION_ATLAS.md`
- `pendiente_desa/README.md`
- `SECURITY.md`

## Advertencia de exposición

Este sistema contiene lógica operacional interna. Aunque el contenido está sanitizado, se recomienda mantener el repositorio **privado** o bajo una organización corporativa con acceso controlado.
