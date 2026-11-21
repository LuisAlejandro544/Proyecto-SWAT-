# README_AI — Guía Rápida de Indexación para IAs

Guía directa para orientarse en segundos al retomar el repositorio, diagnosticar fallos o añadir nuevas funcionalidades.

---

## 1. Mapa de Entrada Rápida (Qué archivo tocar según la tarea)

| Objetivo | Archivo(s) Clave |
| :--- | :--- |
| Cambiar movimiento, agachado, salto o salud SWAT | `godot-project/scripts/player/PlayerController.gd` + `scenes/player/PlayerSWAT.tscn` |
| Ajustar animaciones, cadencia, retroceso o recarga del M4 | `godot-project/scripts/weapons/PlayerWeaponM4.gd` + `scenes/weapons/M4Rig.tscn` |
| Ajustar física o duración de casquillos | `godot-project/scripts/weapons/ShellCasing.gd` + `scenes/weapons/ShellCasing.tscn` |
| Modificar comportamiento, visión, cobertura o AK-47 de IA | `godot-project/scripts/ai/TerroristAI.gd` + `scenes/ai/Terrorist.tscn` |
| Cambiar distribución del hotel de 2 pisos o NavigationMesh | `godot-project/scripts/world/HotelArchitecture.gd` |
| Ajustar apertura/cierre de puertas de habitaciones | `godot-project/scripts/world/HotelDoor.gd` + `scenes/world/HotelDoor.tscn` |
| Ajustar conteo de enemigos, pausa o victoria/derrota | `godot-project/scripts/world/HotelMissionManager.gd` + `scenes/levels/HotelMission01.tscn` |
| Cambiar controles táctiles o joystick virtual | `godot-project/scripts/ui/MobileHUD.gd` + `VirtualJoystick.gd` + `scenes/ui/MobileHUD.tscn` |
| Cambiar menú principal, ajustes o guía de controles | `godot-project/scripts/ui/MainMenu.gd`, `SettingsScreen.gd`, `ControlsGuideScreen.gd` |
| Cambiar sonidos procedurales o persistencia de opciones | `godot-project/scripts/autoload/AudioSynth.gd`, `GameSettings.gd` |
| Modificar geometría o piezas animables de modelos 3D | `blender-scripts/models/build_*.py` + `blender-scripts/lib/mesh_utils.py` |
| Ajustar render de previsualizaciones PNG | `blender-scripts/render_previews.py` |
| Cambiar configuración APK (ABIs, SDK, paquete, firma) | `godot-project/export_presets.cfg` |
| Depurar o actualizar compilación APK Debug en CI | `.github/workflows/build-android-debug.yml` |
| Depurar o actualizar generación 3D en CI | `.github/workflows/generate-blender-assets.yml` |

---

## 2. Comandos de Validación Sin Interfaz Gráfica (Headless)

```bash
# 1. Validar que Godot 4.7.2-stable importa todos los recursos y arranca la escena principal sin errores
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --import --quit
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --quit-after 2

# 2. Validar carga directa de la Misión 1 y pantallas UI
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --quit-after 2 res://scenes/levels/HotelMission01.tscn
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --quit-after 2 res://scenes/ui/SettingsScreen.tscn

# 3. Validar sintaxis YAML de ambos workflows de GitHub Actions
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]; print('YAML OK')"

# 4. Validar sintaxis Python de todos los scripts de Blender
python3 -m py_compile blender-scripts/*.py blender-scripts/lib/*.py blender-scripts/models/*.py
```

*Nota*: Si ejecutas `--check-only --script ...` sobre un script individual de Godot sin cargar el proyecto completo, Godot puede reportar falsos positivos de `Identifier not found: AudioSynth / GameSettings` porque los autoloads solo se registran al cargar `project.godot` completo (como hace `--quit-after 2`).

---

## 3. Problemas Conocidos y Soluciones Aplicadas en CI

- **Fallo `sdkmanager tools` (`Failed to find package 'tools'`)**:
  - **Causa**: `android-actions/setup-android@v3` intentaba instalar el paquete obsoleto `tools` eliminado por Google en `cmdline-tools` modernos.
  - **Solución implementada**: Se actualizó a `android-actions/setup-android@v4` especificando `packages: 'platform-tools platforms;android-34 build-tools;34.0.0'`, junto con `actions/checkout@v7`, `actions/setup-java@v6`, `actions/cache@v6` y `actions/upload-artifact@v7` para ejecución nativa en Node 24.
- **Rutas de Android en Godot Headless**:
  - Godot `4.7.2-stable` lee `~/.config/godot/editor_settings-4.7.tres` para localizar `export/android/android_sdk_path`, `java_sdk_path` y `debug_keystore` antes de invocar `--export-debug "Android"`.
- **Regla de Keystore Debug en `export_presets.cfg`**:
  - Godot exige regla **todo o nada** para `keystore/debug`, `keystore/debug_user` y `keystore/debug_password`. Los tres deben quedar vacíos (`""`) en `export_presets.cfg` para delegar la firma al `debug.keystore` configurado en `editor_settings-4.7.tres` durante el CI.

---

## 4. Flujo Recomendado Para Cambios en Assets 3D
1. Edita el generador correspondiente en `blender-scripts/models/`.
2. Ejecuta manualmente en GitHub Actions **Generar Assets 3D en Blender (Manual)**.
3. Descarga y revisa el artefacto `blender-asset-previews-png` para comprobar proporciones, orientación y piezas separadas.
4. Ejecuta manualmente **Compilar APK Debug Android (Godot 4.7.2-stable)** para descargar e instalar el nuevo `.apk` en Android.
