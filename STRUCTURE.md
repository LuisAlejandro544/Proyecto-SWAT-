# STRUCTURE — Arquitectura y Mapa de Archivos

Descripción exacta del árbol de carpetas y la responsabilidad de cada archivo en el repositorio.

```text
/
├── .github/workflows/
│   ├── build-android-debug.yml        # CI manual (workflow_dispatch): descarga Godot 4.7.2, SDK Android y compila APK Debug 32/64-bit
│   └── generate-blender-assets.yml    # CI manual (workflow_dispatch): ejecuta Blender 4.5.16, genera .glb y sube previews .png
│
├── blender-scripts/                   # Pipeline procedural 3D en Python (bpy)
│   ├── generate_all.py                # Script maestro: construye todos los modelos GLB y llama a render_previews.py
│   ├── render_previews.py             # Configura iluminación de estudio Cycles CPU y renderiza PNGs en previews/
│   ├── lib/
│   │   └── mesh_utils.py              # Utilidades compartidas bpy/bmesh (materiales PBR, cajas, cilindros, exportación GLB Y-up)
│   ├── models/
│   │   ├── build_m4.py                # Carabina M4A1 con piezas separadas (M4_Body, M4_Bolt, M4_ChargingHandle, M4_Magazine, MuzzlePoint, EjectionPort)
│   │   ├── build_ak47.py              # Rifle AK-47 para IA con piezas animables equivalentes (AK47_Bolt, AK47_Magazine, MuzzlePoint, EjectionPort)
│   │   ├── build_shell_casing.py      # Casquillo/vaina metálica para expulsión física
│   │   ├── build_hotel_door.py        # Puerta animable con marco fijo (DoorFrame) y pivote de bisagra (DoorPivot/DoorLeaf)
│   │   └── build_hotel_props.py       # Mobiliario de hotel (cama, escritorio, sofá, pilar, planta) y píldora terrorista
│   └── previews/                      # Renders PNG de verificación visual (generados en CI, ignorados en git)
│
├── godot-project/                     # Proyecto principal del juego móvil en Godot 4.7.2-stable
│   ├── project.godot                  # Configuración global del motor, autoloads, pantalla horizontal móvil y GL Compatibility
│   ├── export_presets.cfg             # Preset "Android" APK (armeabi-v7a + arm64-v8a, min_sdk=24, target_sdk=34, sideload-ready)
│   ├── icon.svg                       # Icono vectorial del proyecto
│   ├── assets/models/                 # Modelos .glb exportados desde Blender e importados por Godot (.import)
│   │   ├── m4.glb
│   │   ├── ak47.glb
│   │   ├── shell_casing.glb
│   │   ├── hotel_door.glb
│   │   ├── hotel_bed.glb
│   │   ├── hotel_desk.glb
│   │   ├── hotel_sofa.glb
│   │   ├── hotel_pillar.glb
│   │   ├── hotel_plant.glb
│   │   └── terrorist_pill.glb
│   ├── scenes/
│   │   ├── main.tscn                  # Escena base inicial Hello World (heredada del bootstrap)
│   │   ├── ai/
│   │   │   └── Terrorist.tscn         # Escena del enemigo terrorista con NavigationAgent3D, pivote AK-47 y hitboxes
│   │   ├── levels/
│   │   │   └── HotelMission01.tscn    # Escena completa de la Misión 1 (hotel 2 pisos, iluminación, navegación, jugador y enemigos)
│   │   ├── player/
│   │   │   └── PlayerSWAT.tscn        # Escena del agente SWAT en primera persona (cuerpo cápsula + cámara + M4Rig)
│   │   ├── ui/
│   │   │   ├── MainMenu.tscn          # Pantalla principal con navegación a Misión 1, Controles, Ajustes y Salir
│   │   │   ├── SettingsScreen.tscn    # Pantalla dedicada de sensibilidad táctil, escala de joystick, eje Y, sprint y audio
│   │   │   ├── ControlsGuideScreen.tscn # Pantalla separada con la guía visual de controles móviles
│   │   │   └── MobileHUD.tscn         # HUD en partida (joystick, lookpad, disparo, ADS, recarga, agacharse, salto, puerta)
│   │   ├── weapons/
│   │   │   ├── M4Rig.tscn             # Escena rig de la carabina M4 instanciando m4.glb y nodo de fogonazo
│   │   │   └── ShellCasing.tscn       # RigidBody3D del casquillo expulsado con colisión y sonido de impacto
│   │   └── world/
│   │       └── HotelDoor.tscn         # Puerta interactiva con colisión dinámica y pivote de rotación
│   └── scripts/
│       ├── main.gd                    # Script de la escena inicial main.tscn
│       ├── autoload/
│       │   ├── AudioSynth.gd          # Síntesis procedural de audio en memoria (WAV para disparos, casquillos, recarga, puertas)
│       │   └── GameSettings.gd        # Persistencia en ConfigFile (user://swat_hotel_settings.cfg) y señal settings_changed
│       ├── ai/
│       │   └── TerroristAI.gd         # IA táctica de terroristas (GUARD, ALERT, COMBAT, RELOADING, NEUTRALIZED) + AK-47 animada
│       ├── player/
│       │   └── PlayerController.gd    # Movimiento FPS, agachado, salto, puntería, retroceso de cámara, salud y raycast de puertas
│       ├── ui/
│       │   ├── MainMenu.gd            # Navegación desde el menú principal hacia misión y pantallas secundarias
│       │   ├── SettingsScreen.gd      # Controladores de sliders/switches conectados a GameSettings
│       │   ├── ControlsGuideScreen.gd # Retorno desde guía de controles al menú principal
│       │   ├── MobileHUD.gd           # Coordinación multi-touch del HUD táctil, botón de disparo con aim simultáneo y feedback
│       │   └── VirtualJoystick.gd     # Joystick virtual izquierdo con seguimiento independiente por touch index
│       ├── weapons/
│       │   ├── PlayerWeaponM4.gd      # Lógica y las 5 animaciones solicitadas del M4 sobre los nodos de m4.glb
│       │   └── ShellCasing.gd         # Física de rebote, audio al primer impacto y autodestrucción temporal
│       └── world/
│           ├── HotelArchitecture.gd   # Construcción procedural de los 2 pisos del hotel, escaleras, aberturas y NavigationMesh
│           ├── HotelDoor.gd           # Animación suave de apertura/cierre alrededor de DoorPivot y alerta sonora a IA
│           └── HotelMissionManager.gd # Conteo de terroristas, pausa y pantallas de Victoria/Derrota
│
├── scripts/
│   └── export-godot.sh                # Script auxiliar heredado del bootstrap web (exporta preset "Web" a public/godot/)
│
├── src/ & public/                     # Contenedor web React/Vite inicial (el juego real se ejecuta en Android APK, no en web)
│   ├── App.tsx
│   ├── components/GodotViewport.tsx
│   └── utils/godotConfig.ts(.test.ts)
│
├── README.md                          # Documentación general del proyecto
├── ROADMAP.md                         # Plan de evolución por fases
├── STRUCTURE.md                       # Este archivo (arquitectura y árbol del repositorio)
├── AI_CONTEXT.md                      # Especificaciones técnicas críticas para LLMs
├── AGENTS.md                          # Reglas de comportamiento y desarrollo para agentes
└── README_AI.md                       # Referencia rápida operativa para IAs
```
