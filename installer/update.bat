@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Actualizador - Hardness Mapper
REM  Aplica una actualización de código fuente
REM ============================================================

echo.
echo ============================================================
echo   ACTUALIZADOR - Hardness Mapper
echo ============================================================
echo.

REM Buscar el archivo ZIP de actualización
set UPDATE_ZIP=
for %%f in ("%~dp0hardness-mapper-*-update.zip") do (
    set UPDATE_ZIP=%%f
    set UPDATE_NAME=%%~nxf
)

if not exist "%UPDATE_ZIP%" (
    echo ERROR: No se encontro el archivo de actualizacion
    echo        Asegurese de que el archivo hardness-mapper-*-update.zip
    echo        este en la misma carpeta que este actualizador.
    echo.
    pause
    exit /b 1
)

echo Archivo de actualizacion: %UPDATE_NAME%
echo.

REM ============================================================
REM  Buscar instalación existente
REM ============================================================
set INSTALL_DIR=

REM Primero buscar en la ubicación por defecto
if exist "%LOCALAPPDATA%\HardnessMapper\run.bat" (
    set INSTALL_DIR=%LOCALAPPDATA%\HardnessMapper
)

REM Si no, buscar archivo install_info.txt
if "%INSTALL_DIR%"=="" (
    if exist "%LOCALAPPDATA%\HardnessMapper\install_info.txt" (
        set INSTALL_DIR=%LOCALAPPDATA%\HardnessMapper
    )
)

if "%INSTALL_DIR%"=="" (
    echo No se encontro una instalacion existente.
    set /p INSTALL_DIR="Ingrese la ruta de instalacion: "
)

if not exist "%INSTALL_DIR%\run.bat" (
    echo ERROR: No se encontro una instalacion valida en:
    echo        %INSTALL_DIR%
    echo.
    pause
    exit /b 1
)

REM ============================================================
REM  Verificar versiones
REM ============================================================
set CURRENT_VERSION=desconocida
set NEW_VERSION=desconocida

if exist "%INSTALL_DIR%\app\version.txt" (
    set /p CURRENT_VERSION=<"%INSTALL_DIR%\app\version.txt"
)

REM Extraer version.txt del ZIP para verificar
powershell -Command "$zip = [System.IO.Compression.ZipFile]::OpenRead('%UPDATE_ZIP%'); $entry = $zip.Entries | Where-Object { $_.Name -eq 'version.txt' -and $_.FullName -notlike 'app/*' }; if ($entry) { $reader = [System.IO.StreamReader]::new($entry.Open()); $reader.ReadLine() | Out-File -FilePath '%TEMP%\new_version.txt' -NoNewline; $reader.Close() }; $zip.Dispose()"

if exist "%TEMP%\new_version.txt" (
    set /p NEW_VERSION=<"%TEMP%\new_version.txt"
    del "%TEMP%\new_version.txt"
)

echo Version instalada: %CURRENT_VERSION%
echo Version nueva:     %NEW_VERSION%
echo.

REM ============================================================
REM  Confirmar actualización
REM ============================================================
set /p CONFIRM="Desea continuar con la actualizacion? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Actualizacion cancelada.
    pause
    exit /b 0
)

echo.

REM ============================================================
REM  Crear backup
REM ============================================================
echo [1/3] Creando backup de la version actual...

set BACKUP_DIR=%INSTALL_DIR%\backup_%CURRENT_VERSION%
if exist "%BACKUP_DIR%" rmdir /s /q "%BACKUP_DIR%"
mkdir "%BACKUP_DIR%"

xcopy "%INSTALL_DIR%\app" "%BACKUP_DIR%\app\" /E /I /Q >nul
copy "%INSTALL_DIR%\version.txt" "%BACKUP_DIR%\" >nul 2>nul

echo       OK - Backup en: %BACKUP_DIR%
echo.

REM ============================================================
REM  Aplicar actualización
REM ============================================================
echo [2/3] Aplicando actualizacion...

REM Extraer a carpeta temporal
set TEMP_UPDATE=%TEMP%\hm_update_%RANDOM%
mkdir "%TEMP_UPDATE%"

powershell -Command "Expand-Archive -Path '%UPDATE_ZIP%' -DestinationPath '%TEMP_UPDATE%' -Force"
if errorlevel 1 (
    echo ERROR: No se pudo extraer el archivo de actualizacion
    rmdir /s /q "%TEMP_UPDATE%"
    pause
    exit /b 1
)

REM Eliminar carpeta app actual (excepto projects y user_preferences.json)
if exist "%INSTALL_DIR%\app\projects" (
    move "%INSTALL_DIR%\app\projects" "%TEMP%\hm_projects_%RANDOM%" >nul
)
if exist "%INSTALL_DIR%\app\user_preferences.json" (
    copy "%INSTALL_DIR%\app\user_preferences.json" "%TEMP%\hm_userprefs_%RANDOM%.json" >nul
)

rmdir /s /q "%INSTALL_DIR%\app"

REM Copiar nueva versión
xcopy "%TEMP_UPDATE%\app" "%INSTALL_DIR%\app\" /E /I /Q >nul
copy "%TEMP_UPDATE%\version.txt" "%INSTALL_DIR%\" >nul

REM Restaurar datos del usuario
if exist "%TEMP%\hm_projects_%RANDOM%" (
    move "%TEMP%\hm_projects_%RANDOM%" "%INSTALL_DIR%\app\projects" >nul
)
if exist "%TEMP%\hm_userprefs_%RANDOM%.json" (
    move "%TEMP%\hm_userprefs_%RANDOM%.json" "%INSTALL_DIR%\app\user_preferences.json" >nul
)

REM Limpiar
rmdir /s /q "%TEMP_UPDATE%"

echo       OK
echo.

REM ============================================================
REM  Verificar actualización
REM ============================================================
echo [3/3] Verificando actualizacion...

set /p INSTALLED_VERSION=<"%INSTALL_DIR%\app\version.txt"
echo       Version instalada: %INSTALLED_VERSION%
echo       OK
echo.

REM ============================================================
REM  COMPLETADO
REM ============================================================
echo ============================================================
echo   ACTUALIZACION COMPLETADA
echo ============================================================
echo.
echo   Version anterior: %CURRENT_VERSION%
echo   Version nueva:    %INSTALLED_VERSION%
echo.
echo   Backup guardado en:
echo   %BACKUP_DIR%
echo.
echo   Puede eliminar el backup manualmente si todo funciona bien.
echo.
echo ============================================================
echo.

set /p LAUNCH="Desea ejecutar la aplicacion ahora? (S/N): "
if /i "%LAUNCH%"=="S" (
    start "" "%INSTALL_DIR%\run.bat"
)

endlocal
pause
