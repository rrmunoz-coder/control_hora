# Módulo de conocimiento operacional y gestión documental

## Estado de la decisión

**Requerimiento aprobado conceptualmente, pero postergado.**

No se incorporará código de este módulo antes de completar las pruebas funcionales e integradas de ATLAS v0.3.0. Su desarrollo debe comenzar en una rama independiente después de cerrar los defectos P0/P1 detectados durante esas pruebas.

Versión objetivo sugerida: `v0.4.0`.

Rama sugerida: `feature/conocimiento-operacional`.

## Objetivo

Centralizar en ATLAS la documentación necesaria para ejecutar, controlar, mantener y transferir el trabajo del equipo. El módulo debe permitir registrar textos y archivos vinculados directamente con tareas, acciones, procesos, proyectos, servicios, actividades y unidades organizacionales.

No debe construirse como un wiki genérico aislado. El conocimiento debe quedar relacionado con el modelo operacional y con las personas responsables de mantenerlo.

## Casos de uso principales

- Documentar cómo se ejecuta una tarea.
- Mantener procedimientos e instructivos vigentes.
- Adjuntar archivos de apoyo, plantillas y evidencias.
- Registrar reglas de negocio y decisiones operacionales.
- Documentar incidentes, causas y soluciones.
- Relacionar un mismo documento con varias tareas, proyectos o procesos.
- Identificar tareas críticas sin documentación.
- Detectar concentración de conocimiento en una sola persona.
- Sustentar oportunidades de automatización con procedimientos estables.

## Entidades que podrán documentarse

- Unidad organizacional.
- Proyecto.
- Servicio.
- Proceso.
- Actividad.
- Acción.
- Tarea.

Un documento podrá relacionarse con una o varias entidades. No debe quedar limitado a una única tarea o proyecto.

## Tipos de conocimiento iniciales

- Procedimiento.
- Instructivo.
- Manual.
- Checklist o control.
- Regla de negocio.
- Decisión operacional.
- Incidente y solución.
- Script o herramienta documentada.
- Documento de proyecto.
- Plantilla.
- Evidencia o referencia.

## Contenido textual

Cada ficha deberá permitir, al menos:

- Título.
- Resumen.
- Contenido enriquecido sanitizado.
- Tipo documental.
- Etiquetas.
- Unidad dueña.
- Propietario del conocimiento.
- Revisor.
- Clasificación de acceso.
- Estado documental.
- Versión actual.
- Fecha de vigencia.
- Próxima fecha de revisión.
- Motivo del último cambio.
- Fecha y usuario de creación/modificación.

## Gestión de archivos

El módulo debe permitir adjuntar archivos a una ficha documental y conservar su historial.

### Tipos inicialmente permitidos

- PDF.
- DOCX.
- XLSX.
- PPTX.
- TXT.
- CSV.
- PNG, JPG y JPEG.

La aceptación de ZIP debe evaluarse posteriormente y mantenerse deshabilitada por defecto.

### Tipos prohibidos por defecto

- EXE, DLL y MSI.
- BAT, CMD y PS1.
- JS y otros ejecutables interpretados.
- Archivos con macros, salvo autorización y control específico.
- Claves privadas, secretos, contraseñas o configuraciones productivas.

### Controles obligatorios de carga

- Lista blanca de extensiones.
- Validación de MIME y firma real del archivo.
- Tamaño máximo configurable.
- Nombre físico aleatorio, separado del nombre original.
- Hash SHA-256.
- Prevención de path traversal.
- Escaneo antivirus o integración con la solución corporativa.
- Auditoría de carga, descarga, nueva versión y eliminación lógica.
- Descarga siempre a través de una ruta autenticada y autorizada.
- Encabezado `Content-Disposition: attachment` cuando corresponda.

## Almacenamiento propuesto

Para el MVP no se recomienda guardar todos los archivos como BLOB en Oracle.

- Oracle almacenará metadatos, relaciones, versiones y auditoría.
- Los archivos se almacenarán en una ruta Windows o recurso corporativo configurable.
- La ruta física nunca deberá exponerse al navegador.
- El nombre físico deberá ser interno y no predecible.

Configuración propuesta:

```ini
[features]
knowledge_enabled = false

[knowledge]
storage_path = K:\@@@@@ATLAS_DATA\conocimiento
max_file_mb = 25
allowed_extensions = pdf,docx,xlsx,pptx,txt,csv,png,jpg,jpeg
```

El módulo deberá poder desplegarse con `knowledge_enabled=false` y habilitarse inicialmente solo para un grupo piloto.

## Modelo de datos preliminar

### GT_CONOCIMIENTO

Cabecera de la ficha documental:

- ID_CONOCIMIENTO.
- TIPO.
- TITULO.
- RESUMEN.
- CONTENIDO.
- ESTADO.
- ID_UNIDAD_DUENA.
- ID_PROPIETARIO.
- ID_REVISOR.
- CLASIFICACION.
- VERSION_ACTUAL.
- FECHA_VIGENCIA.
- FECHA_PROX_REVISION.
- FECHA_CREACION.
- CREADO_POR.
- FECHA_MODIFICACION.
- MODIFICADO_POR.
- ACTIVO.

### GT_CONOCIMIENTO_RELACION

Relación muchos-a-muchos con el modelo operacional:

- ID_RELACION.
- ID_CONOCIMIENTO.
- TIPO_ENTIDAD.
- ID_ENTIDAD.
- ACTIVO.

Valores iniciales de `TIPO_ENTIDAD`:

- UNIDAD.
- PROYECTO.
- SERVICIO.
- PROCESO.
- ACTIVIDAD.
- ACCION.
- TAREA.

### GT_CONOCIMIENTO_ARCHIVO

Metadatos y control de archivos:

- ID_ARCHIVO.
- ID_CONOCIMIENTO.
- NOMBRE_ORIGINAL.
- NOMBRE_FISICO.
- EXTENSION.
- MIME_TYPE.
- TAMANO_BYTES.
- HASH_SHA256.
- RUTA_RELATIVA.
- VERSION.
- FECHA_CARGA.
- CARGADO_POR.
- ACTIVO.

### GT_CONOCIMIENTO_VERSION

Historial inmutable del contenido textual:

- ID_VERSION.
- ID_CONOCIMIENTO.
- NUMERO_VERSION.
- TITULO.
- RESUMEN.
- CONTENIDO.
- MOTIVO_CAMBIO.
- FECHA_VERSION.
- CREADO_POR.

## Flujo documental

```text
BORRADOR
  → EN_REVISION
  → PUBLICADO
      → REQUIERE_ACTUALIZACION
      → OBSOLETO
```

Reglas mínimas:

- Solo una versión publicada podrá considerarse oficial.
- Una versión publicada no deberá sobrescribirse; cualquier cambio crea una nueva versión.
- Los borradores serán visibles para autor, revisor, administradores y usuarios expresamente habilitados.
- Los documentos obsoletos conservarán historia y relaciones, pero se distinguirán claramente de los vigentes.
- La eliminación será lógica.

## Permisos

- ADMIN: administración global.
- JEFE: administración dentro de su unidad y descendientes autorizados.
- Propietario: edición de borradores y creación de nuevas versiones.
- Revisor: aprobación o devolución documental.
- Usuario: lectura y descarga según alcance y clasificación.

Clasificaciones iniciales:

- INTERNO.
- RESTRINGIDO.
- CONFIDENCIAL.

Los permisos deben validarse siempre en backend, incluyendo descarga de archivos y manipulación directa de identificadores.

## Integración con ATLAS

Cada tarea, proyecto, servicio, proceso o actividad deberá mostrar una sección de documentación relacionada.

Acciones iniciales:

- Crear documento.
- Vincular documento existente.
- Adjuntar archivo.
- Ver y descargar.
- Crear nueva versión.
- Enviar a revisión.
- Publicar.
- Marcar para actualización.
- Marcar obsoleto.

La planilla semanal podrá mostrar enlaces a procedimientos publicados de la tarea seleccionada, sin bloquear inicialmente la imputación si no existe documentación.

## Búsqueda

El MVP debe incluir búsqueda por:

- Texto de título y resumen.
- Tipo documental.
- Etiquetas.
- Unidad.
- Proyecto o servicio.
- Proceso, actividad, acción o tarea.
- Propietario.
- Estado y vigencia.

La indexación semántica y la IA quedan fuera del MVP.

## Indicadores diferenciadores

- Tareas críticas sin procedimiento publicado.
- Documentos vencidos o próximos a revisión.
- Procesos con alto consumo de horas y documentación inexistente.
- Tareas ejecutadas por una sola persona y sin respaldo documental.
- Procedimientos estables asociados a tareas de alto costo como candidatos a automatización.
- Documentación con alta consulta o descarga.

## Criterios de aceptación del MVP

- Crear una ficha con texto y relaciones operacionales.
- Adjuntar y descargar un archivo permitido con autorización backend.
- Rechazar archivos prohibidos, alterados o demasiado grandes.
- Mantener versiones de texto y archivos sin sobrescribir historia.
- Ejecutar el flujo borrador, revisión, publicación y obsolescencia.
- Buscar documentación por texto y entidad relacionada.
- Restringir lectura y descarga según rol, unidad y clasificación.
- Auditar todas las operaciones relevantes.
- Operar detrás del feature flag sin afectar los módulos actuales.
- Contar con migración, validación, rollback y pruebas automatizadas.

## Fuera del alcance inicial

- IA generativa o chat con documentos.
- OCR.
- Edición colaborativa simultánea.
- Firma electrónica.
- Ejecución de scripts desde ATLAS.
- Almacenamiento de secretos.
- Integración SharePoint/Drive.
- Flujos regulatorios complejos.
- Indexación vectorial o semántica.

## Condición para iniciar el desarrollo

El desarrollo solo comenzará cuando se cumpla lo siguiente:

1. Pruebas funcionales de v0.3.0 ejecutadas en ambiente integrado.
2. Sin defectos abiertos P0.
3. Defectos P1 evaluados y con decisión de corrección o aceptación.
4. Validación del flujo semanal con perfiles USUARIO, JEFE y ADMIN.
5. Confirmación de la ruta de almacenamiento y del control antivirus corporativo.
6. Definición de extensiones, tamaño máximo y política de retención.

Hasta entonces, este archivo constituye el requerimiento funcional y técnico de referencia, sin modificar el código productivo de ATLAS.
