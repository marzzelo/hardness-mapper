@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  Instalador - Hardness Mapper
REM  Instala la aplicación portable en el sistema del usuario
REM ============================================================

echo.
echo ============================================================
echo   INSTALADOR - Hardness Mapper
echo ============================================================
echo.

REM Configuración por defecto
set DEFAULT_INSTALL_DIR=%LOCALAPPDATA%\HardnessMapper
set ZIP_FILE=%~dp0hardness-mapper-*-portable.zip

REM Buscar el archivo ZIP portable
for %%f in ("%~dp0hardness-mapper-*-portable.zip") do (
    set ZIP_FILE=%%f
    set ZIP_NAME=%%~nxf
)

if not exist "%ZIP_FILE%" (
    echo ERROR: No se encontro el archivo portable ZIP
    echo        Asegurese de que el archivo hardness-mapper-*-portable.zip
    echo        este en la misma carpeta que este instalador.
    echo.
    pause
    exit /b 1
)

echo Archivo encontrado: %ZIP_NAME%
echo.

REM ============================================================
REM  Solicitar ruta de instalación
REM ============================================================
echo Ruta de instalacion por defecto:
echo   %DEFAULT_INSTALL_DIR%
echo.
set INSTALL_DIR=
set /p INSTALL_DIR="Presione ENTER para usar la ruta por defecto o escriba otra: "

if "!INSTALL_DIR!"=="" (
    set INSTALL_DIR=%DEFAULT_INSTALL_DIR%
)

echo.
echo Instalando en: %INSTALL_DIR%
echo.

REM ============================================================
REM  Verificar instalación existente
REM ============================================================
if exist "%INSTALL_DIR%\run.bat" (
    echo AVISO: Ya existe una instalacion en esta carpeta.
    set /p OVERWRITE="Desea sobrescribirla? (S/N): "
    if /i not "!OVERWRITE!"=="S" (
        echo Instalacion cancelada.
        pause
        exit /b 0
    )
    echo.
    echo Eliminando instalacion anterior...
    rmdir /s /q "%INSTALL_DIR%"
)

REM ============================================================
REM  Crear carpeta e instalar
REM ============================================================
echo [1/3] Creando carpeta de instalacion...
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ERROR: No se pudo crear la carpeta de instalacion
        pause
        exit /b 1
    )
)
echo       OK
echo.

echo [2/3] Extrayendo archivos (esto puede tardar)...
REM Usar Shell.Application para compatibilidad con PowerShell antiguo
powershell -Command "$shell = New-Object -ComObject Shell.Application; $zip = $shell.NameSpace('%ZIP_FILE%'); $dest = $shell.NameSpace('%INSTALL_DIR%'); $dest.CopyHere($zip.Items(), 16)"
if errorlevel 1 (
    echo ERROR: No se pudo extraer el archivo ZIP
    pause
    exit /b 1
)
echo       OK
echo.

REM ============================================================
REM  Crear accesos directos
REM ============================================================
echo [3/3] Creando accesos directos...

REM Crear acceso directo en el Escritorio
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_NAME=Hardness Mapper

REM Usar VBScript para crear accesos directos
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%DESKTOP%\%SHORTCUT_NAME%.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\run.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Hardness Mapper - Aplicacion de mapeo de dureza" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%INSTALL_DIR%\app\icons\icon.ico, 0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

REM Crear acceso directo en el Menú Inicio
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo sLinkFile = "%STARTMENU%\%SHORTCUT_NAME%.lnk" >> "%TEMP%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\CreateShortcut.vbs"
echo oLink.TargetPath = "%INSTALL_DIR%\run.bat" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%INSTALL_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Description = "Hardness Mapper - Aplicacion de mapeo de dureza" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.IconLocation = "%INSTALL_DIR%\app\icons\icon.ico, 0" >> "%TEMP%\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

echo       OK
echo.

REM ============================================================
REM  Guardar información de instalación
REM ============================================================
(
    echo install_path=%INSTALL_DIR%
    echo install_date=%DATE% %TIME%
) > "%INSTALL_DIR%\install_info.txt"

REM ============================================================
REM  COMPLETADO
REM ============================================================
echo ============================================================
echo   INSTALACION COMPLETADA
echo ============================================================
echo.
echo   La aplicacion se ha instalado en:
echo   %INSTALL_DIR%
echo.
echo   Se han creado accesos directos en:
echo   - Escritorio
echo   - Menu Inicio
echo.
echo   Para ejecutar la aplicacion, use el acceso directo
echo   o ejecute run.bat desde la carpeta de instalacion.
echo.
echo ============================================================
echo.

set /p LAUNCH="Desea ejecutar la aplicacion ahora? (S/N): "
if /i "%LAUNCH%"=="S" (
    start "" "%INSTALL_DIR%\run.bat"
)

endlocal
pause
