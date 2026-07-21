# Arquitectura ATLAS

## Visión

ATLAS separa operación, seguridad, validación y analítica para sostener crecimiento sin depender de planillas.

```text
Navegador
  ↓
Flask / Waitress
  ↓
Servicios Python
  ↓
Packages Oracle
  ↓
Tablas ATLAS
```

## Capas

### Capa web

- Flask.
- Blueprints por módulo.
- Plantillas Jinja.
- Validaciones de experiencia usuario.

### Capa de negocio

- Servicios Python.
- Validación de formulario.
- Normalización de datos.
- Control de sesión y roles.

### Capa Oracle

- Tablas transaccionales.
- Packages PL/SQL.
- Vistas de consulta.
- Integridad referencial.

### Capa de análisis

- Costos por categoría.
- Distribución por centro de costo.
- Score de automatización.
- Eficiencia operativo-financiera.

## Modelo conceptual

```text
Unidad dueña
└── Proyecto o servicio
    └── Actividad
        └── Tarea
            └── Imputación semanal
```

El centro de costo es una dimensión financiera separada de la unidad dueña.

```text
Unidad dueña     = quién responde
Tarea ejecutada  = qué se hizo
Centro de costo  = dónde se carga el costo
```
