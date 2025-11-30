# Sistema de Distribución Portable - Hardness Mapper

Este documento describe el sistema de distribución portable para Hardness Mapper.

## Estructura de Archivos

```
hardness-mapper/
├── build_portable.bat      # Genera el instalador completo
├── build_update.bat        # Genera paquete de actualización (solo código)
├── version.txt             # Versión actual de la aplicación
├── installer/
│   ├── install.bat         # Instalador para el cliente
│   ├── update.bat          # Actualizador para el cliente
│   └── check_updates.bat   # Verificador de actualizaciones online
```

## Para el Desarrollador

### Generar Instalador Completo

```batch
build_portable.bat
```

Este script:
1. Descarga Python 3.13 embebido (si no está en caché)
2. Extrae Python y configura el archivo `.pth`
3. Instala pip en el Python embebido
4. Copia el código fuente de la aplicación
5. Instala las dependencias desde `requirements.txt`
6. Crea `run.bat` para lanzar la aplicación
7. Empaqueta todo en `dist/hardness-mapper-vX.X.X-portable.zip`

**Salida:** `dist/hardness-mapper-v1.0.0-portable.zip` (~100-200 MB)

### Generar Paquete de Actualización

```batch
build_update.bat
```

Este script solo empaqueta el código fuente (sin Python ni dependencias).

**Salida:** `dist/hardness-mapper-v1.0.0-update.zip` (~pocos MB)

### Proceso de Release

1. Actualizar `version.txt` con la nueva versión
2. Ejecutar `build_portable.bat` para instalador completo
3. Ejecutar `build_update.bat` para paquete de actualización
4. Distribuir los archivos:
   - Para nuevos usuarios: ZIP portable + `install.bat`
   - Para usuarios existentes: ZIP update + `update.bat`

## Para el Cliente

### Instalación Nueva

1. Obtener el archivo `hardness-mapper-vX.X.X-portable.zip`
2. Colocar junto a `install.bat`
3. Ejecutar `install.bat`
4. Seguir las instrucciones en pantalla

**Ubicación por defecto:** `%LOCALAPPDATA%\HardnessMapper`

### Actualización

1. Obtener el archivo `hardness-mapper-vX.X.X-update.zip`
2. Colocar junto a `update.bat`
3. Ejecutar `update.bat`
4. Seguir las instrucciones en pantalla

El actualizador:
- Crea un backup de la versión anterior
- Preserva los proyectos del usuario (`projects/`)
- Preserva las preferencias del usuario (`user_preferences.json`)

### Verificar Actualizaciones

Ejecutar `check_updates.bat` para verificar si hay nuevas versiones disponibles.

> **Nota:** Requiere configurar la URL del servidor en el script.

## Estructura del Paquete Portable

```
hardness-mapper-portable/
├── python/                     # Python 3.13 embebido
│   ├── python.exe
│   ├── python313.dll
│   ├── python313._pth          # Configurado para site-packages
│   ├── Lib/
│   │   └── site-packages/      # Dependencias instaladas
│   └── ...
├── app/                        # Código de la aplicación
│   ├── main.py
│   ├── version.txt
│   ├── callbacks/
│   ├── config/
│   ├── interface/
│   ├── fonts/
│   ├── icons/
│   ├── resources/
│   └── projects/               # Proyectos del usuario
├── run.bat                     # Lanzador de la aplicación
└── version.txt                 # Versión instalada
```

## Notas Técnicas

### Python Embeddable

El paquete Python Windows Embeddable no incluye pip por defecto. El script `build_portable.bat`:

1. Descarga `get-pip.py` para instalar pip
2. Modifica `python313._pth` para habilitar `site-packages`:

```
python313.zip
.
Lib\site-packages
import site
```

### Dependencias

Las siguientes dependencias se instalan automáticamente:
- dearpygui
- reportlab
- pillow
- rich
- matplotlib
- scipy
- numpy
- plotly
- kaleido

### Versionado

El archivo `version.txt` controla la versión de la aplicación:
- Usar formato semántico: `MAJOR.MINOR.PATCH`
- Actualizar antes de cada release
- El instalador y actualizador leen esta versión automáticamente

## Solución de Problemas

### Error: "No se pudo descargar Python embebido"
- Verificar conexión a internet
- El archivo se descarga de python.org

### Error: "No se pudieron instalar las dependencias"
- Verificar que `requirements.txt` exista
- Algunas dependencias pueden requerir conexión a internet

### La aplicación no inicia
- Verificar que `run.bat` esté en la carpeta correcta
- Ejecutar desde cmd para ver mensajes de error
