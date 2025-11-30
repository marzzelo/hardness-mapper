@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Build Update - Hardness Mapper
REM  Genera un paquete de actualización (solo código fuente)
REM ============================================================

echo.
echo ============================================================
echo   BUILD UPDATE - Hardness Mapper
echo ============================================================
echo.

set BUILD_DIR=%~dp0build_update
set INSTALLER_DIR=%~dp0installer
set APP_DIR=%BUILD_DIR%\app

REM Leer versión
set /p APP_VERSION=<"%~dp0version.txt"
echo Version de la aplicacion: %APP_VERSION%
echo.

REM ============================================================
REM  PASO 1: Limpiar carpeta de salida
REM ============================================================
echo [1/3] Limpiando carpetas...

if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%"
mkdir "%APP_DIR%"

if not exist "%INSTALLER_DIR%" (
    mkdir "%INSTALLER_DIR%"
)

echo       OK
echo.

REM ============================================================
REM  PASO 2: Copiar código fuente
REM ============================================================
echo [2/3] Copiando codigo fuente...

REM Copiar archivos principales
copy "%~dp0main.py" "%APP_DIR%\" >nul
copy "%~dp0config.ini" "%APP_DIR%\" >nul
copy "%~dp0dpg.ini" "%APP_DIR%\" >nul
copy "%~dp0version.txt" "%APP_DIR%\" >nul

REM Copiar carpetas (sin user_preferences.json para no sobrescribir config del usuario)
xcopy "%~dp0callbacks" "%APP_DIR%\callbacks\" /E /I /Q >nul
xcopy "%~dp0config" "%APP_DIR%\config\" /E /I /Q >nul
xcopy "%~dp0interface" "%APP_DIR%\interface\" /E /I /Q >nul
xcopy "%~dp0fonts" "%APP_DIR%\fonts\" /E /I /Q >nul
xcopy "%~dp0icons" "%APP_DIR%\icons\" /E /I /Q >nul
xcopy "%~dp0resources" "%APP_DIR%\resources\" /E /I /Q >nul
for /d %%f in ("%~dp0projects\sample*") do (
    xcopy "%%f" "%APP_DIR%\projects\%%~nxf\" /E /I /Q >nul
)

REM Eliminar __pycache__ de las carpetas copiadas
for /d /r "%APP_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)

REM Copiar version.txt a la raíz del update
copy "%~dp0version.txt" "%BUILD_DIR%\" >nul

echo       OK
echo.

REM ============================================================
REM  PASO 3: Empaquetar
REM ============================================================
echo [3/3] Empaquetando...

set ZIP_NAME=hardness-mapper-v%APP_VERSION%-update.zip
if exist "%INSTALLER_DIR%\%ZIP_NAME%" del "%INSTALLER_DIR%\%ZIP_NAME%"

powershell -Command "Compress-Archive -Path '%BUILD_DIR%\*' -DestinationPath '%INSTALLER_DIR%\%ZIP_NAME%' -Force"
if errorlevel 1 (
    echo ERROR: No se pudo crear el ZIP
    exit /b 1
)

echo       OK
echo.

REM ============================================================
REM  COMPLETADO
REM ============================================================
echo ============================================================
echo   UPDATE BUILD COMPLETADO
echo ============================================================
echo.
echo   Archivo generado:
echo   %INSTALLER_DIR%\%ZIP_NAME%
echo.
echo   Este paquete solo contiene el codigo fuente.
echo   El cliente debe usar update.bat para aplicarlo.
echo.
echo ============================================================

REM Limpiar carpeta temporal
rmdir /s /q "%BUILD_DIR%"

endlocal
pause
