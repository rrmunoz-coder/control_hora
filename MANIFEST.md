# Manifiesto v0.2.0

Incluye código fuente productivo sanitizado, pruebas, configuración de ejemplo, documentación técnica, prompt regenerador y backlog priorizado.

## Contenido esperado

```text
atlas/                  aplicación Flask por dominio
sql/                    DDL, packages, vistas, validaciones y rollback
service/                instalación y operación como servicio Windows
tools/                  utilitarios técnicos
tests/                  pruebas de estructura, higiene y autorización
docs/                   arquitectura, instalación y análisis
prompts/                prompt maestro para regenerar/evolucionar
pendiente_desa/          backlog por seguridad, función, UX y calidad
scripts/                validación y empaquetado
config.ini.example      configuración sanitizada
requirements*.txt       dependencias productivas y de desarrollo
```

## Exclusiones obligatorias

- `config.ini` real y cualquier secreto.
- `.venv`, cachés y logs.
- Copias históricas, respaldos y hotfix empaquetados.
- `nssm.exe`, DLL, instaladores y ZIP de terceros.
- Datos productivos o fixtures con información personal real.

## Regla de publicación

Una entrega solo se considera válida después de ejecutar higiene, compilación y pruebas. El paquete completo v0.2.0 debe coincidir con el checksum publicado en `releases/v0.2.0`.
