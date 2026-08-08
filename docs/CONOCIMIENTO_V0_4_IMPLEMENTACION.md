# ATLAS v0.4.0 — Implementación del módulo de conocimiento

## Estado

**EN DESARROLLO** en la rama `feature/conocimiento-operacional`.

El desarrollo parte del requerimiento aprobado en `pendiente_desa/05_MODULO_CONOCIMIENTO.md` y se mantiene detrás de `features.knowledge_enabled=false` por defecto. No debe habilitarse en producción hasta aplicar/validar la migración Oracle y completar las pruebas de autorización, flujo y archivos.

## Fase 1 implementada

- Modelo Oracle: `GT_CONOCIMIENTO`, `GT_CONOCIMIENTO_RELACION`, `GT_CONOCIMIENTO_VERSION`, `GT_CONOCIMIENTO_ARCHIVO`.
- Constraints, FKs e índices de soporte.
- Feature flag y configuración de almacenamiento/archivos.
- Blueprint `/conocimiento`.
- Biblioteca con búsqueda por título, resumen y etiquetas, filtro por tipo y estado.
- Creación de borradores.
- Edición con nueva versión inmutable en cada guardado.
- Estados: `BORRADOR`, `EN_REVISION`, `PUBLICADO`, `REQUIERE_ACTUALIZACION`, `OBSOLETO`.
- Autorización backend por rol, unidad, propietario y revisor.
- Auditoría transaccional de altas, actualizaciones y cambios de estado.
- Pantallas iniciales de biblioteca, ficha, edición e historial.
- SQL de instalación, validación y rollback.

## Reglas de acceso iniciales

- `ADMIN`: acceso global.
- `JEFE`: acceso documental dentro de su alcance de unidades.
- Propietario/revisor: acceso directo al documento correspondiente.
- Usuario: documentos `INTERNO` publicados o que requieren actualización dentro de sus unidades.
- `RESTRINGIDO` y `CONFIDENCIAL`: no se exponen a usuarios generales en esta primera fase.

## Decisiones de seguridad

- El contenido de la fase 1 se trata como texto plano y Jinja lo escapa al renderizar. El editor enriquecido sanitizado no se habilita todavía.
- `config.ini` y la ruta física de documentos permanecen fuera de Git.
- La tabla de archivos existe, pero la carga física se habilitará solo después de incorporar validación de firma/MIME, hash SHA-256 y scanner antivirus corporativo.
- No se sirve directamente la carpeta de almacenamiento desde Flask ni desde el servidor web.
- Las relaciones polimórficas se almacenan como tipo + ID; la exposición de rutas para vincular entidades se hará cuando exista validación backend específica por cada entidad.

## Fase 2 inmediata

1. Adjuntos seguros: PDF, DOCX, XLSX, PPTX, TXT, CSV, PNG/JPG/JPEG.
2. Validación de extensión + firma real/MIME y tamaño.
3. SHA-256, UUID físico, ruta relativa y descarga autenticada.
4. Integración antivirus corporativa obligatoria antes de habilitar uploads.
5. Vinculación UI/backend a unidad, proyecto, tarea y actividad; posteriormente proceso/acción/servicio según modelo real.
6. Búsqueda por relaciones operacionales.
7. Indicadores de documentación vencida, tareas críticas sin procedimiento y concentración de conocimiento.
8. Pruebas automatizadas de autorización horizontal, flujo, versiones y archivos.
9. Enlace del módulo en la navegación principal cuando el feature flag esté activo.

## Despliegue de desarrollo

1. Ejecutar `sql/70_CONOCIMIENTO_V0_4.sql`.
2. Ejecutar `sql/71_VALIDAR_CONOCIMIENTO_V0_4.sql`.
3. Configurar `[features]` y `[knowledge]` en `config.ini`.
4. Mantener `knowledge_enabled=false` hasta finalizar pruebas.
5. Para un ambiente piloto controlado, cambiar a `knowledge_enabled=true` y reiniciar `ATLAS_Web`.

El rollback `sql/72_ROLLBACK_CONOCIMIENTO_V0_4.sql` es destructivo y solo debe utilizarse en desarrollo/pruebas.