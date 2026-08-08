# ATLAS — Piloto de Conocimiento Operacional

## Objetivo

Probar el módulo de conocimiento v0.4 **sin reemplazar ni detener** el ATLAS productivo.

| Componente | Producción | Piloto |
|---|---|---|
| Código | `K:\@@@@@ATLAS` | `K:\@@@@@ATLAS_CONOCIMIENTO_TEST` |
| URL | `http://claroprod985:5050` | `http://claroprod985:5051` |
| Servicio | `ATLAS_Web` | `ATLAS_Conocimiento_Test` |
| Cookie | actual de producción | `atlas_knowledge_test_session` |
| Secret Flask | producción | nuevo y aleatorio |
| Runtime Python | venv productivo, proceso 5050 | mismo venv **solo como runtime**, proceso separado |
| Config | producción | copia aislada `config.ini` en carpeta piloto |

El piloto reutiliza el Python/paquetes del venv productivo porque el módulo no agrega dependencias. No modifica el venv ni el código de `K:\@@@@@ATLAS`.

## Qué sí toca Oracle

El piloto puede usar el mismo esquema Oracle. `sql/70_CONOCIMIENTO_V0_4.sql` agrega únicamente:

- `GT_CONOCIMIENTO`
- `GT_CONOCIMIENTO_RELACION`
- `GT_CONOCIMIENTO_VERSION`
- `GT_CONOCIMIENTO_ARCHIVO`
- cinco índices del módulo

La aplicación productiva 5050 no referencia esos objetos.

**Atención:** la autenticación piloto comparte las tablas de usuarios y rate-limit existentes. No hagas pruebas deliberadas con contraseñas incorrectas, porque los intentos fallidos podrían afectar el contador usado por producción.

## Instalación exacta

1. Extrae el paquete como `K:\@@@@@ATLAS_CONOCIMIENTO_TEST`.
2. Ejecuta `pilot\00_PRECHECK.cmd`.
3. Ejecuta `pilot\01_PREPARAR_PILOTO.cmd`. Se crea un `config.ini` piloto tomando Oracle/LDAP desde `K:\@@@@@ATLAS\config.ini`, pero cambia puerto, cookie y secreto. El módulo queda **apagado**.
4. En DBeaver, conectado al mismo esquema propietario de ATLAS, ejecuta **como SQL Script completo** `sql\70_CONOCIMIENTO_V0_4.sql`.
5. Ejecuta `sql\71_VALIDAR_CONOCIMIENTO_V0_4.sql`. Deben aparecer las cuatro tablas como `OK`, los cinco índices válidos y cero objetos/errores inválidos.
6. Ejecuta como Administrador `pilot\02_INSTALAR_SERVICIO_TEST.cmd`.
7. Abre `http://claroprod985:5051/login` y autentícate con una credencial válida. Verifica Dashboard/Tareas/Proyectos sin habilitar todavía conocimiento.
8. Confirma que `http://claroprod985:5050` sigue operativo normalmente.
9. Ejecuta `pilot\03_HABILITAR_CONOCIMIENTO.cmd`.
10. Entra en `http://claroprod985:5051/conocimiento` o usa la opción **Conocimiento** del menú.
11. Ejecuta el checklist `pilot\CHECKLIST_PRUEBAS.md`.

Si desde otro equipo no abre 5051 pero localmente sí, ejecuta como Administrador `pilot\06_ABRIR_FIREWALL_5051.cmd`.

## Diagnóstico

Ejecuta `pilot\05_STATUS_DIAGNOSTICO.cmd`. Comprueba servicio, listener TCP 5051, configuración no sensible y respuesta HTTP local.

Los logs del piloto son independientes:

- `logs\atlas_knowledge_test_stdout.log`
- `logs\atlas_knowledge_test_stderr.log`
- `logs\atlas.log`

## Deshabilitar sin desinstalar

`pilot\04_DESHABILITAR_CONOCIMIENTO.cmd` deja el módulo apagado y reinicia sólo `ATLAS_Conocimiento_Test`.

## Retirar el piloto

1. Ejecuta `pilot\04_DESHABILITAR_CONOCIMIENTO.cmd`.
2. Ejecuta como Administrador `pilot\07_DESINSTALAR_SERVICIO_TEST.cmd`.
3. Si quieres conservar los documentos piloto, **no ejecutes SQL 72**.
4. Si quieres borrar completamente las tablas/datos del módulo, ejecuta en DBeaver `sql\72_ROLLBACK_CONOCIMIENTO_V0_4.sql`. Es destructivo y sólo afecta los cuatro objetos del módulo.
5. Elimina `K:\@@@@@ATLAS_CONOCIMIENTO_TEST` cuando ya no sea necesario.

El servicio `ATLAS_Web`, el puerto 5050 y la carpeta productiva no deben detenerse ni modificarse en este procedimiento.
