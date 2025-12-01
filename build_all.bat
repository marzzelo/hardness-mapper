REM Builds bortable and updater versions of Hardness Mapper
@echo off
call build_portable.bat
if errorlevel 1 (
    echo ERROR: Fallo al construir la version portable
    exit /b 1
)
call build_update.bat
if errorlevel 1 (
    echo ERROR: Fallo al construir la version updater
    exit /b 1
)
echo ============================================================
echo   BUILD COMPLETADO: Versiones portable y updater creadas
echo ============================================================
echo.
echo   Archivos generados:
echo   - Portable: installer\hardness-mapper-v%APP_VERSION%-portable.zip
echo   - Updater: installer\hardness-mapper-v%APP_VERSION%-updater.zip
echo.echo ============================================================
exit /b 0


