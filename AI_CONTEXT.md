# AI_CONTEXT — Contexto Técnico del Proyecto

Documento de referencia técnica rápida para que cualquier modelo o desarrollador entienda las decisiones arquitectónicas, contratos entre módulos y restricciones del proyecto sin necesidad de explorar todo el repositorio.

---

## 1. Naturaleza del Proyecto
- **Título**: *SWAT: Asalto al Hotel*
- **Plataforma objetivo**: **Android móvil exclusivamente** (distribución directa por APK / Uptodown, sin dependencia ni bloqueo a Google Play Services).
- **Nota sobre `src/` y `public/`**: Los archivos React/Vite en raíz (`src/`, `index.html`, `public/godot/`) pertenecen al entorno inicial de arranque del workspace. **El juego no se desarrolla para web**, todo el desarrollo jugable vive en `godot-project/` y los assets 3D en `blender-scripts/`.

---

## 2. Stack Tecnológico Exacto
- **Motor**: `Godot Engine 4.7.2-stable`
- **Renderizado**: `gl_compatibility` (tanto escritorio como móvil) para máxima compatibilidad en GPUs Android de gama baja/media.
- **Resolución base**: `1280x720` (`canvas_items`, aspecto `expand`, orientación horizontal móvil `window/handheld/orientation=0`).
- **Pipeline 3D**: `Blender 4.5.16 LTS` ejecutado en modo `--background` vía Python (`bpy`, `bmesh`, `mathutils`), exportando `.glb` (`export_yup=True`) y renders PNG Cycles CPU (`960x540`, 20 muestras + denoising).
- **Exportación Android (`export_presets.cfg`)**:
  - `gradle_build/use_gradle_build=false` (usa plantilla precompilada `android_debug.apk` de Godot + `apksigner`, compilación rápida en CI).
  - `gradle_build/export_format=0` (`.apk`).
  - `gradle_build/min_sdk=""` y `gradle_build/target_sdk=""` (hereda los niveles SDK de la plantilla precompilada de Godot al tener `use_gradle_build=false`).
  - `textures/vram_compression/import_etc2_astc=true` en `project.godot` (compresión de texturas requerida para Android).
  - Arquitecturas habilitadas: **`armeabi-v7a=true`** (32 bits) y **`arm64-v8a=true`** (64 bits).
  - Permisos: `permissions/internet=false`, `permissions/vibrate=true`.

---

## 3. Contratos Críticos Blender (`*.glb`) ↔ Godot (`*.gd`)

Los scripts de Godot buscan **nombres exactos de nodos hijos** dentro de los modelos `.glb` importados. **Nunca renombrar estos nodos en Blender sin actualizar su script en Godot:**

| Modelo GLB | Script Blender | Nodos Obligatorios Buscados por Godot | Script Godot Consumidor |
| :--- | :--- | :--- | :--- |
| `m4.glb` | `build_m4.py` | `M4_Body`, `M4_Bolt`, `M4_ChargingHandle`, `M4_Magazine`, `MuzzlePoint`, `EjectionPort` | `PlayerWeaponM4.gd` |
| `ak47.glb` | `build_ak47.py` | `AK47_Bolt`, `AK47_Magazine`, `MuzzlePoint`, `EjectionPort` | `TerroristAI.gd` |
| `hotel_door.glb` | `build_hotel_door.py` | `DoorFrame`, `DoorPivot`, `DoorLeaf` | `HotelDoor.gd` |
| `shell_casing.glb` | `build_shell_casing.py` | Malla única de vaina | `ShellCasing.tscn` / `PlayerWeaponM4.gd` / `TerroristAI.gd` |
| `terrorist_pill.glb` | `build_hotel_props.py` | Píldora táctica con chaleco y pasamontañas | `Terrorist.tscn` |

### Convención de Ejes Blender → Godot
En `blender-scripts/lib/mesh_utils.py`, la exportación usa `export_yup=True`:
- Blender `+X` → Godot `+X` (Derecha)
- Blender `+Y` → Godot `-Z` (Adelante)
- Blender `+Z` → Godot `+Y` (Arriba)

---

## 4. Arquitectura Modular en `godot-project/`

- **Autoloads globales (`project.godot`)**:
  - `GameSettings` (`scripts/autoload/GameSettings.gd`): persiste en `user://swat_hotel_settings.cfg` (`look_sensitivity`, `ads_sensitivity_multiplier`, `master_volume_db`, `invert_y`, `joystick_scale`, `auto_sprint`).
  - `AudioSynth` (`scripts/autoload/AudioSynth.gd`): genera `AudioStreamWAV` en memoria al arrancar (sin archivos de audio externos con derechos de autor).
- **Flujo de Escenas UI**:
  - `MainMenu.tscn` → `HotelMission01.tscn` (juego) / `SettingsScreen.tscn` (ajustes) / `ControlsGuideScreen.tscn` (guía).
  - La pausa y resultado (Victoria/Derrota) se manejan mediante paneles modales (`OverlayCanvas`) dentro de `HotelMissionManager.gd`.
- **Controles Táctiles Multi-Touch (`MobileHUD.gd` + `VirtualJoystick.gd`)**:
  - Cada componente táctil rastrea su propio `touch_index` (`InputEventScreenTouch` / `InputEventScreenDrag`) para evitar conflictos entre moverse con el pulgar izquierdo y apuntar/disparar con el pulgar derecho.
  - El botón de disparo (`FireButton`) reenvía eventos de arrastre hacia `PlayerController` para que el jugador pueda disparar y corregir puntería al mismo tiempo.

---

## 5. Pipeline CI/CD en `.github/workflows/`

- Todos los workflows son exclusivamente manuales (`on: workflow_dispatch:`).
- `build-android-debug.yml`:
  - Usa acciones compatibles con Node 24 (`actions/checkout@v7`, `actions/setup-java@v6`, `android-actions/setup-android@v4`, `actions/cache@v6`, `actions/upload-artifact@v7`).
  - Instala explícitamente `platform-tools`, `platforms;android-34` y `build-tools;34.0.0` (evitando el paquete eliminado `tools` que causaba fallo en `setup-android@v3`).
  - Configura `~/.config/godot/editor_settings-4.7.tres` con `android_sdk_path`, `java_sdk_path`, `debug_keystore`, `debug_keystore_user` y `debug_keystore_pass` antes de ejecutar `--export-debug "Android"`.
- `generate-blender-assets.yml`:
  - Instala dependencias X11/OpenGL mínimas para Blender headless, cachea Blender `4.5.16 LTS` en `/opt/blender`, genera `.glb` + `.png`, sube los `.png` como artefacto y hace commit automático de `.glb` modificados.
