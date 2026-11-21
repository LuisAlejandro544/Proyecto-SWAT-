# AGENTS — Reglas Operativas para Agentes de IA

Directrices obligatorias que todo agente o colaborador automatizado debe cumplir antes de modificar archivos en este repositorio.

---

## 1. Filosofía y Alcance
- **Plataforma real**: Este proyecto construye un **juego 3D FPS móvil para Android** en **Godot 4.7.2-stable**. No implementes mecánicas del juego en la capa web (`src/`).
- **Usuario sin PC**: El desarrollador trabaja desde teléfono móvil y compila mediante **GitHub Actions manuales** (`workflow_dispatch`). Cualquier cambio debe poder compilarse en los runners `ubuntu-latest` de GitHub Actions sin pasos manuales de editor local.
- **Distribución APK externa**: El juego se distribuirá en **Uptodown / APK directo**, no mediante Play Store cerrado.
  - Mantén `gradle_build/export_format=0` (`.apk`).
  - Mantén activadas **ambas arquitecturas**: `armeabi-v7a=true` (32 bits) y `arm64-v8a=true` (64 bits).
  - No introduzcas dependencias que exijan Google Play Services obligatorio.

---

## 2. Reglas de Código y Modularidad
- **Sin atajos ni fallbacks falsos**: Si una funcionalidad depende de un modelo `.glb`, un nodo específico o un workflow, impleméntala completamente en ese sistema en lugar de esconder errores con reemplazos vacíos.
- **Modularidad estricta**: Mantén separados jugador (`scripts/player/`), armas (`scripts/weapons/`), IA (`scripts/ai/`), mundo (`scripts/world/`), autoloads (`scripts/autoload/`) e interfaz (`scripts/ui/`).
- **Comentarios explicativos**: Todos los archivos de script deben conservar o incluir una cabecera clara explicando qué lógica y responsabilidad contiene el archivo. Añade comentarios inline solo donde la lógica no sea obvia.
- **Diseño y UI intactos**: No modifiques estilos, iconos, disposición de pantallas ni lógica existente que funcione si el usuario no lo ha pedido explícitamente. Mantén pantallas separadas (`MainMenu`, `SettingsScreen`, `ControlsGuideScreen`) en lugar de amontonar todo en una sola vista.
- **Dependencias y licencias**:
  - Nunca agregues librerías o assets con licencias copyleft o que obliguen a liberar el código fuente o dar créditos obligatorios (ej. GPL/AGPL).
  - Evita usar nombres de marcas comerciales protegidas en nombres de archivos o identificadores que expongan al proyecto a reclamos legales.
- **Archivo `commit_message.txt`**: Si llega a existir en el repositorio, su contenido debe estar en **español** y no debe modificarse ni crearse salvo petición expresa del usuario.

---

## 3. Reglas Específicas de Godot y Blender
- **Generación local de modelos `.glb` con Blender**: Los agentes de IA **sí pueden y deben** descargar Blender `4.5.16 LTS` en `tools/blender/` (ignorado en `.gitignore`, sin subir binarios al repo) y ejecutar `./tools/blender/blender --background --python blender-scripts/generate_all.py` cuando creen o modifiquen scripts en `blender-scripts/`. De este modo, los `.glb` y sus `.glb.import` quedan listos y guardados en `godot-project/assets/models/` dentro del repositorio, sin depender de geometría procedural en GDScript ni obligar al usuario a esperar una ejecución manual previa en CI.
- **Sin arquitectura procedural en Godot**: Toda la arquitectura y mobiliario fijo del Gran Hotel vive en Blender (`blender-scripts/models/build_hotel_building.py` -> `hotel_building.glb` con sufijos `-col` para colisiones automáticas), manteniendo `HotelArchitecture.gd` únicamente para hornear el `NavigationRegion3D`.
- **Preservar contratos de nodos GLB**: Antes de editar `build_m4.py`, `build_ak47.py`, `build_hotel_door.py` o `build_hotel_building.py`, verifica en `AI_CONTEXT.md` los nombres de pivotes y puntos (`M4_Bolt`, `M4_Magazine`, `M4_ChargingHandle`, `MuzzlePoint`, `EjectionPort`, `DoorPivot`, `AK47_Bolt`, `AK47_Magazine`).
- **Las 5 animaciones del M4 son obligatorias**: Toda actualización al arma del jugador debe preservar: (1) idle/balanceo/ADS, (2) disparo/retroceso+cerrojo, (3) fogonazo 3D+luz, (4) recarga completa y (5) expulsión física de casquillos.
- **Rendimiento móvil**: No sobrecargues el hilo/frame principal con instancias infinitas (usa tiempos de vida finitos en casquillos/partículas, límite de voces de audio y materiales compatibles tanto con `mobile` Vulkan 1.1 como con `gl_compatibility` OpenGL ES 3.0).
- **Workflows manuales**: En `.github/workflows/`, conserva `on: workflow_dispatch:` sin triggers automáticos de `push` o `pull_request` salvo orden contraria del usuario.
- **Android SDK en CI**: No uses el paquete eliminado `tools` con `sdkmanager`; usa `android-actions/setup-android@v4` con paquetes explícitos (`platform-tools platforms;android-34 build-tools;34.0.0`).

---

## 4. Checklist Antes de Finalizar Cualquier Cambio
1. Verifica que las escenas y scripts de Godot arranquen sin errores en modo headless si el binario está disponible (`./tools/godot/Godot_v4.7.2-stable_linux.x86_64 --headless --path godot-project --quit-after 2`).
2. Si editaste `.github/workflows/*.yml`, valida la sintaxis YAML y que todas las acciones y URLs referenciadas existan realmente.
3. Si editaste `blender-scripts/`, verifica sintaxis Python, regenera los `.glb` con Blender en `tools/blender/` (e importa con Godot `--import --quit`) y comprueba consistencia de nombres de nodos exportados.
4. No leas ni modifiques archivos ajenos a la tarea solicitada.
