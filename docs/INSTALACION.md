# Instalación y actualización

## Requisitos
- Windows Server.
- Python 3.12 o compatible.
- Oracle Client cuando se usa Thick mode.
- Acceso Oracle y LDAP.
- Proxy o terminador TLS para HTTPS.
- NSSM x64 instalado externamente.

## Instalación nueva
1. Copiar el repositorio o paquete de la versión.
2. Crear `.venv` e instalar `requirements.txt`.
3. Crear `config.ini` desde el ejemplo y restringir sus permisos.
4. Ejecutar el modelo y catálogos Oracle según el orden documentado.
5. Ejecutar la migración vigente de seguridad/aprobaciones si el modelo base no la incorpora.
6. Probar Oracle, LDAP, HTTPS y cabeceras.
7. Instalar o reiniciar el servicio.

## Actualización v0.2.0 → v0.3.0
Seguir `docs/ACTUALIZACION_V0_3_0.md`. La migración `sql/60_SEGURIDAD_APROBACIONES_V0_3.sql` debe aplicarse antes de iniciar el código v0.3.0.

## Validación técnica
```cmd
python scripts\validar_higiene.py
python -m compileall -q atlas tests run_dev.py run_prod.py service_entry.py
pytest -q
python scripts\build_package.py
```

## Regla de actualización
Nunca reemplazar producción directamente desde un ZIP histórico. Cada despliegue debe corresponder a un commit/tag, incluir migraciones identificables, evidencia de pruebas y rollback documentado.
