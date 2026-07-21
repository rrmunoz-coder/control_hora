# control_hora / ATLAS

ATLAS es el sistema web para transformar el registro semanal de trabajo en información accionable sobre capacidad, costo operativo y oportunidades de automatización.

## Versión vigente

- Versión: `v0.1.0`
- Fecha base: `2026-07-21`
- Estado: base técnica limpia para pruebas integrales
- Paquete instalable: `control_hora_v0.1.0_instalacion.zip`

## Objetivo

Implementar ATLAS como plataforma integral de gestión del equipo, centralizando el registro de trabajo, la estructura organizacional, los proyectos y servicios, las tareas y sus validaciones, e incorporando una visión financiero-operacional para fortalecer la toma de decisiones.

## Módulos incluidos

- Autenticación corporativa vía LDAP, con usuario local de contingencia.
- Administración de usuarios, roles y permisos.
- Administración de unidades organizacionales.
- Administración de proyectos, servicios y tareas.
- Imputación semanal de lunes a domingo.
- Imputación directa a proyectos mediante tarea técnica `PRYGEN_<ID_PROYECTO>` compatible con tablas comprimidas.
- Módulo base de costos, centros de costo, score y permisos.
- Servicio Windows para ejecución productiva.

## Estructura de versionado

Cada versión debe mantener la misma estructura:

```text
control_hora/
├── atlas/                  código Flask
├── sql/                    scripts Oracle por orden de ejecución
├── service/                scripts servicio Windows
├── tools/                  utilitarios técnicos
├── tests/                  pruebas básicas
├── docs/                   manuales y arquitectura
├── prompts/                prompt usado para construir la versión
├── releases/vX.Y.Z/        notas, checksums y control de paquete
├── scripts/                scripts de build/validación
├── VERSION.md
├── CHANGELOG.md
├── MANIFEST.md
└── README.md
```

## Seguridad

No se versiona `config.ini` real, credenciales, `.venv`, cachés Python, logs, respaldos temporales ni binarios de NSSM. La configuración real debe mantenerse localmente en el servidor.

## Instalación rápida

1. Descargar el paquete instalable de la versión.
2. Descomprimir en el servidor.
3. Copiar `config.ini.example` a `config.ini` y completar credenciales localmente.
4. Ejecutar SQL en el orden indicado en `docs/MANUAL_INSTALACION.md`.
5. Instalar o reiniciar el servicio Windows.
6. Validar acceso web y prueba funcional de imputación semanal.
