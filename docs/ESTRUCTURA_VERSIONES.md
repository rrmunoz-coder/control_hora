# Estándar de versionado ATLAS

## Convención

Se utilizará versionado semántico:

```text
MAJOR.MINOR.PATCH
```

Ejemplo:

```text
v0.1.0
```

## Estructura por versión

Cada versión debe incluir:

```text
README.md
VERSION.md
CHANGELOG.md
MANIFEST.md
docs/MANUAL_INSTALACION.md
docs/MANUAL_USO_ADMIN.md
docs/ARQUITECTURA.md
prompts/PROMPT_CONSTRUCCION_ATLAS.md
releases/vX.Y.Z/RELEASE_NOTES.md
releases/vX.Y.Z/CHECKSUMS.md
scripts/build_package.py
scripts/validar_higiene.py
```

## Criterio de versión

- `PATCH`: correcciones puntuales y hotfix.
- `MINOR`: nuevo módulo funcional compatible.
- `MAJOR`: cambio estructural o incompatible.

## Control de calidad previo a publicar

- Compilación Python.
- Validación SQL manual o por ambiente.
- Revisión de secretos.
- Limpieza de cachés.
- Actualización de changelog.
- Generación de checksum.
