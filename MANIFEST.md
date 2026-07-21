# Manifiesto de versión v0.1.0

## Contenido esperado del paquete limpio

```text
atlas/                  aplicación Flask
sql/                    scripts Oracle
service/                scripts de servicio Windows
tools/                  utilitarios técnicos
tests/                  pruebas base
docs/                   documentación funcional/técnica
prompts/                prompt de construcción
releases/v0.1.0/        notas y checksums
scripts/                build y validaciones
config.ini.example      configuración ejemplo sin secretos
requirements.txt        dependencias Python
run_dev.cmd             ejecución local
run_prod.cmd            ejecución productiva
wsgi.py                 entrada WSGI
service_entry.py        entrada servicio Windows
README.md               resumen del proyecto
VERSION.md              versión vigente
CHANGELOG.md            historial de cambios
```

## Exclusiones obligatorias

```text
config.ini              configuración real del servidor
.venv/                  entorno virtual
__pycache__/            caché Python
*.pyc                   bytecode Python
*.log                   logs
*_old/                  respaldos antiguos
_backup*/              respaldos temporales
*.zip históricos        parches previos no vigentes
nssm.exe                binario externo
```

## Regla de oro

El repositorio debe contener código, SQL, documentación, prompts y scripts reproducibles. No debe contener secretos, credenciales, binarios externos ni residuos de pruebas locales.
