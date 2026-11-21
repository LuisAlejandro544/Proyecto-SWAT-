# SWAT: Asalto al Hotel

Juego táctico 3D en primera persona (FPS) diseñado específicamente para dispositivos móviles Android (arquitecturas de **32 bits `armeabi-v7a` y 64 bits `arm64-v8a`**), desarrollado en **Godot 4.7.2-stable** con todos los escenarios, armas y assets 3D generados en **Blender 4.5.16 LTS** mediante scripts de Python (`godot-project/assets/models/*.glb`).

---

## Características Principales

- **Objetivo de la Misión 1**: Despejar el **Gran Hotel Corona de 2 pisos** (`36m x 32m`, modelo `hotel_building.glb` generado en Blender con colisionadores `-col` integrados): gran atrium con candelabro de cristal y techo artesonado, recepción con casillero y carro de equipaje, lounge bar, banco de ascensores, escalera imperial con balaustradas y **7 salas/suites amuebladas** (`101–103` y `201–204`) defendidas por **10 terroristas**.
- **Gráficos Híbridos Vulkan 1.1 + OpenGL ES 3.0**: Configurado con renderizador `mobile` (**Vulkan 1.1**) en Android cuando el procesador lo soporta, con `fallback_to_opengl3=true` automático hacia **OpenGL ES 3.0** (`gl_compatibility`) en dispositivos antiguos, además de texturas PBR empaquetadas desde Blender, `ReflectionProbe`, tonemapping ACES y glow sutil.
- **Agente SWAT y Carabina M4 (`PlayerWeaponM4.gd` + `m4.glb`)**:
  1. **Animación de arma**: respiración, balanceo al caminar/esprintar, lag de cámara y transición suave a mira holográfica (ADS).
  2. **Animación de disparo**: retroceso del arma, retroceso mecánico de `M4_Bolt` y elevación controlada de cámara.
  3. **Animación de fogonazo**: destello 3D en `MuzzlePoint` acompañado de luz puntual instantánea.
  4. **Animación de recarga**: inclinación táctica, extracción/inserción de `M4_Magazine` y accionamiento de `M4_ChargingHandle`.
  5. **Expulsión física de casquillos**: spawn de `ShellCasing.tscn` (`shell_casing.glb`) con giro, rebote y sonido metálico desde `EjectionPort`.
- **IA Terrorista (`TerroristAI.gd` + `ak47.glb`)**:
  - Máquina de estados (`GUARD`, `ALERT`, `COMBAT`, `RELOADING`, `NEUTRALIZED`).
  - Navegación 3D sobre `NavigationRegion3D`, apertura de puertas cerradas en alerta/combate, capas de colisión dedicadas para hitboxes precisas, cobertura/desplazamiento lateral y ráfagas de AK-47 con fogonazo, cerrojo móvil (`AK47_Bolt`), recarga de cargador (`AK47_Magazine`) y casquillos físicos.
- **Interfaz Móvil Táctica (`MobileHUD.gd` + `VirtualJoystick.gd`)**:
  - Joystick izquierdo multi-touch centrado (`pivot_offset`), área derecha de puntería e **indicador direccional de daño**.
  - Botones circulares ergonómicos dispuestos en arco alrededor del pulgar derecho (`DISPARAR` con aim simultáneo, `MIRA`, `RECARGAR`, `AGACHAR` y `SALTAR`) sin tapar el arma, y panel de munición en esquina superior derecha.
  - Pantallas dedicadas e independientes: Menú Principal (`MainMenu`), Ajustes Táctiles (`SettingsScreen`) y Guía de Controles (`ControlsGuideScreen`).
- **Audio Procedural Sin Licencias Restrictivas (`AudioSynth.gd`)**:
  - Síntesis en tiempo de carga de disparos M4/AK-47, casquillos, clics mecánicos de recarga, puertas e impactos con límite de voces simultáneas para estabilidad móvil.
- **Distribución APK Directa**:
  - Configurado para exportación directa como `.apk` (no `.aab` exclusivo de tienda), compatible con **Uptodown** e instalación directa en Android `7.0+` (`min_sdk = 24`, `target_sdk = 34`).

---

## Requisitos Previos

- **En la nube (flujo principal sin PC)**: Cuenta de GitHub con GitHub Actions habilitado para ejecutar manualmente los workflows.
- **En entorno local (opcional)**:
  - `Godot 4.7.2-stable` (`tools/godot/Godot_v4.7.2-stable_linux.x86_64`)
  - `Blender 4.5.16 LTS` (para regenerar `.glb` y `.png` localmente)
  - `Java JDK 17` y `Android SDK` (`platform-tools`, `platforms;android-34`, `build-tools;34.0.0`) para exportar APK

---

## Flujos Manuales en GitHub Actions

Ambos workflows se activan **únicamente de forma manual** (`workflow_dispatch`) desde la pestaña **Actions** del repositorio:

### 1. Generar Assets 3D y Previsualizaciones PNG
- **Workflow**: `.github/workflows/generate-blender-assets.yml`
- **Qué hace**:
  1. Instala/restaura desde caché **Blender 4.5.16 LTS**.
  2. Ejecuta `blender-scripts/generate_all.py` en modo `--background`.
  3. Exporta todos los modelos `.glb` hacia `godot-project/assets/models/`.
  4. Renderiza capturas de estudio en `blender-scripts/previews/*.png` y las sube como artefacto `blender-asset-previews-png`.
  5. Guarda en el repositorio los `.glb` actualizados si hubo cambios.

### 2. Compilar APK Debug Android (32 y 64 bits)
- **Workflow**: `.github/workflows/build-android-debug.yml`
- **Qué hace**:
  1. Configura **Temurin JDK 17** y **Android SDK** (`android-actions/setup-android@v4` con `platform-tools`, `platforms;android-34`, `build-tools;34.0.0`).
  2. Descarga y cachea **Godot 4.7.2-stable** y sus plantillas de exportación Android.
  3. Cachea la carpeta de recursos importados `godot-project/.godot`.
  4. Genera `debug.keystore` y registra las rutas de SDK/JDK en `editor_settings-4.7.tres`.
  5. Compila por separado los presets `"Android arm64-v8a"` (64 bits -> `build/android/swat_asalto_al_hotel_arm64-v8a_debug.apk`) y `"Android armeabi-v7a"` (32 bits -> `build/android/swat_asalto_al_hotel_armeabi-v7a_debug.apk`).
  6. Verifica la firma de ambos APKs con `apksigner` y los sube como artefactos separados (`swat-asalto-al-hotel-arm64-v8a-debug-apk` y `swat-asalto-al-hotel-armeabi-v7a-debug-apk`).

---

## Comandos Útiles (CLI)

```bash
# Validar importación headless del proyecto Godot
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --import --quit

# Exportar APK Debug localmente (requiere export_templates, JDK 17 y Android SDK configurados)
mkdir -p build/android
./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --verbose --path godot-project --export-debug "Android" "../build/android/swat_asalto_al_hotel_debug.apk"

# Regenerar modelos GLB y previews PNG localmente con Blender
blender --background --python blender-scripts/generate_all.py

# Validación del entorno auxiliar TypeScript/Web
npm run lint
npm run build
```

---

## Documentación Relacionada

- [`STRUCTURE.md`](./STRUCTURE.md) — Árbol de archivos y responsabilidades de cada módulo.
- [`ROADMAP.md`](./ROADMAP.md) — Hoja de ruta de desarrollo por fases.
- [`AI_CONTEXT.md`](./AI_CONTEXT.md) — Contexto técnico, convenciones de nodos GLB y restricciones.
- [`AGENTS.md`](./AGENTS.md) — Reglas obligatorias para agentes de IA que modifiquen el repo.
- [`README_AI.md`](./README_AI.md) — Guía rápida de arranque y verificación para IAs.
