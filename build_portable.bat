@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Build Portable - Hardness Mapper
REM  Genera un paquete portable con Python embebido
REM ============================================================

echo.
echo ============================================================
echo   BUILD PORTABLE - Hardness Mapper
echo ============================================================
echo.

REM Configuración
set PYTHON_VERSION=3.13.1
set PYTHON_EMBED_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip
set PYTHON_EMBED_ZIP=python-%PYTHON_VERSION%-embed-amd64.zip
set GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py

set BUILD_DIR=%~dp0build_portable
set INSTALLER_DIR=%~dp0installer
set PYTHON_DIR=%BUILD_DIR%\python
set APP_DIR=%BUILD_DIR%\app

REM Leer versión
set /p APP_VERSION=<"%~dp0version.txt"
echo Version de la aplicacion: %APP_VERSION%
echo.

REM ============================================================
REM  PASO 1: Limpiar carpetas de salida
REM ============================================================
echo [1/7] Limpiando carpetas de salida...

if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%"

if not exist "%INSTALLER_DIR%" (
    mkdir "%INSTALLER_DIR%"
)

echo       OK
echo.

REM ============================================================
REM  PASO 2: Descargar Python embebido
REM ============================================================
echo [2/7] Descargando Python %PYTHON_VERSION% embebido...

if not exist "%~dp0%PYTHON_EMBED_ZIP%" (
    echo       Descargando desde python.org...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_EMBED_URL%' -OutFile '%~dp0%PYTHON_EMBED_ZIP%'"
    if errorlevel 1 (
        echo ERROR: No se pudo descargar Python embebido
        exit /b 1
    )
) else (
    echo       Usando cache existente...
)
echo       OK
echo.

REM ============================================================
REM  PASO 3: Extraer Python embebido
REM ============================================================
echo [3/7] Extrayendo Python embebido...

mkdir "%PYTHON_DIR%"
powershell -Command "Expand-Archive -Path '%~dp0%PYTHON_EMBED_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force"
if errorlevel 1 (
    echo ERROR: No se pudo extraer Python embebido
    exit /b 1
)
echo       OK
echo.

REM ============================================================
REM  PASO 4: Instalar pip en Python embebido
REM ============================================================
echo [4/7] Instalando pip...

REM Descargar get-pip.py si no existe
if not exist "%~dp0get-pip.py" (
    echo       Descargando get-pip.py...
    powershell -Command "Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%~dp0get-pip.py'"
)

REM Modificar el archivo ._pth ANTES de instalar pip
REM Buscar el archivo ._pth (puede ser python313._pth, python312._pth, etc.)
for %%f in ("%PYTHON_DIR%\python*._pth") do (
    set PTH_FILE=%%f
)

echo       Configurando %PTH_FILE%...

REM Crear el contenido del archivo .pth
REM ../app permite encontrar los módulos de la aplicación
(
    echo python313.zip
    echo .
    echo ../app
    echo Lib\site-packages
    echo import site
) > "%PTH_FILE%"

REM Crear carpeta site-packages
mkdir "%PYTHON_DIR%\Lib\site-packages"

REM Instalar pip
"%PYTHON_DIR%\python.exe" "%~dp0get-pip.py" --no-warn-script-location
if errorlevel 1 (
    echo ERROR: No se pudo instalar pip
    exit /b 1
)
echo       OK
echo.

REM ============================================================
REM  PASO 5: Copiar código fuente
REM ============================================================
echo [5/7] Copiando codigo fuente...

mkdir "%APP_DIR%"

REM Copiar archivos principales
copy "%~dp0main.py" "%APP_DIR%\" >nul
copy "%~dp0config.ini" "%APP_DIR%\" >nul
copy "%~dp0dpg.ini" "%APP_DIR%\" >nul
copy "%~dp0user_preferences.json" "%APP_DIR%\" >nul
copy "%~dp0version.txt" "%APP_DIR%\" >nul

REM Copiar carpetas
xcopy "%~dp0callbacks" "%APP_DIR%\callbacks\" /E /I /Q >nul
xcopy "%~dp0config" "%APP_DIR%\config\" /E /I /Q >nul
xcopy "%~dp0interface" "%APP_DIR%\interface\" /E /I /Q >nul
xcopy "%~dp0fonts" "%APP_DIR%\fonts\" /E /I /Q >nul
xcopy "%~dp0icons" "%APP_DIR%\icons\" /E /I /Q >nul
xcopy "%~dp0resources" "%APP_DIR%\resources\" /E /I /Q >nul
for /d %%f in ("%~dp0projects\sample*") do (
    xcopy "%%f" "%APP_DIR%\projects\%%~nxf\" /E /I /Q >nul
)

REM Crear carpeta projects vacía
mkdir "%APP_DIR%\projects"

REM Eliminar __pycache__ de las carpetas copiadas
for /d /r "%APP_DIR%" %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)

echo       OK
echo.

REM ============================================================
REM  PASO 6: Instalar dependencias
REM ============================================================
echo [6/7] Instalando dependencias (esto puede tardar)...

"%PYTHON_DIR%\python.exe" -m pip install -r "%~dp0requirements.txt" --no-warn-script-location -q
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    exit /b 1
)
echo       OK
echo.

REM ============================================================
REM  PASO 7: Crear scripts y empaquetar
REM ============================================================
echo [7/7] Creando scripts y empaquetando...

REM Crear run.bat
(
    echo @echo off
    echo setlocal
    echo.
    echo REM Hardness Mapper - Launcher
    echo set PYDIR=%%~dp0python
    echo set PYTHON=%%PYDIR%%\python.exe
    echo set APPDIR=%%~dp0app
    echo.
    echo REM Agregar app al path de Python
    echo set PYTHONPATH=%%APPDIR%%
    echo.
    echo cd /d "%%APPDIR%%"
    echo "%%PYTHON%%" main.py
    echo.
    echo endlocal
) > "%BUILD_DIR%\run.bat"

REM Crear version.txt en la raíz del build
copy "%~dp0version.txt" "%BUILD_DIR%\" >nul

REM Empaquetar todo en ZIP
set ZIP_NAME=hardness-mapper-v%APP_VERSION%-portable.zip
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
echo   BUILD COMPLETADO
echo ============================================================
echo.
echo   Archivo generado:
echo   %INSTALLER_DIR%\%ZIP_NAME%
echo.
echo   Para distribuir:
echo   1. Copia la carpeta installer/ completa
echo   2. El cliente ejecuta install.bat
echo.
echo ============================================================

endlocal
pause
