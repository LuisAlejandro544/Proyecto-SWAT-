# ROADMAP — SWAT: Asalto al Hotel

Hoja de ruta evolutiva del proyecto móvil 3D FPS en **Godot 4.7.2-stable** + **Blender 4.5.16 LTS**.

---

## Fase 1 — Cimientos Técnicos, Misión 1 y Pipeline CI/CD (Estado Actual)

- [x] **Motor base**: Configuración de `Godot 4.7.2-stable` con renderizador `gl_compatibility` optimizado para móvil.
- [x] **Pipeline de assets procedurales**: Scripts Python en `blender-scripts/` para generar `.glb` y renders de estudio `.png` sin dependencias externas de pago ni copyright.
- [x] **Arma SWAT M4**: Jerarquía modular (`M4_Body`, `M4_Bolt`, `M4_ChargingHandle`, `M4_Magazine`, `MuzzlePoint`, `EjectionPort`) con las 5 animaciones completas (idle/sway/ADS, retroceso+cerrojo, fogonazo 3D+luz, recarga táctica, casquillos físicos).
- [x] **Hotel de 2 pisos (Misión 1)**: Geometría sólida construida en `HotelArchitecture.gd`, mobiliario táctico (`hotel_bed`, `hotel_desk`, `hotel_sofa`, `hotel_pillar`, `hotel_plant`), `NavigationRegion3D` y 5 puertas animadas (`HotelDoor.tscn`).
- [x] **IA Terrorista con AK-47**: Enemigos basados en cápsula táctica (`terrorist_pill.glb`) con estados `GUARD`, `ALERT`, `COMBAT`, `RELOADING`, `NEUTRALIZED` y arma AK-47 con fogonazo, cerrojo y casquillos.
- [x] **UI y UX Móvil**: Pantallas independientes (`MainMenu`, `SettingsScreen`, `ControlsGuideScreen`), `MobileHUD` ergonómico y `VirtualJoystick` multi-touch.
- [x] **Compilación APK Debug en GitHub Actions**: Workflow manual (`workflow_dispatch`) con caché de Godot, plantillas e importación `.godot`, generando APK dual **32 bits (`armeabi-v7a`) + 64 bits (`arm64-v8a`)** listo para instalación directa / Uptodown.

---

## Fase 2 — Pulido de Combate, Impactos y Sensación Táctica

- [ ] **Feedback balístico avanzado**:
  - Trazadores visibles de balas en ráfagas y chispas/polvo al impactar paredes, madera y metal.
  - Marcas temporales de impacto (decals) optimizadas por pooling para móvil.
  - Animación de muerte/caída física para los terroristas neutralizados.
- [ ] **Audio táctico ampliado**:
  - Pasos diferenciados por superficie (mármol en vestíbulo vs alfombra en pasillos/habitaciones).
  - Sonido de respiración con salud baja e indicación direccional de disparos recibidos.
- [ ] **Interacción táctica con el entorno**:
  - Opción de entreabrir/patear puertas (breach rápido) y cobertura destruible menor (plantas/macetas).

---

## Fase 3 — Modelado Detallado de Personajes y Nuevo Arsenal

- [ ] **Sustitución progresiva de la píldora base**:
  - Modelo humanoide estilizado del agente SWAT (brazos en primera persona con guantes tácticos visibles sosteniendo el M4).
  - Variantes visuales de terroristas generadas en Blender (chaleco, pasamontañas, casco ligero o bandolera) manteniendo la compatibilidad con el esqueleto/pivotes actuales.
- [ ] **Nuevas armas y equipamiento**:
  - Pistola táctica secundaria (cambio rápido cuando se vacía el cargador de la M4).
  - Granada aturdidora (Flashbang) para despejar habitaciones antes de entrar por la puerta.

---

## Fase 4 — Expansión de Misiones y Progresión Local

- [ ] **Selector de misiones independiente** (pantalla separada desde `MainMenu`):
  - **Misión 1**: Asalto al Hotel (Lobby + Piso 2).
  - **Misión 2**: Ala Ejecutiva / Azotea del Hotel con rehenes o desactivación de bomba.
  - **Misión 3**: Estacionamiento Subterráneo (combate a corta/media distancia con pilares y vehículos generados en Blender).
- [ ] **Sistema de calificación por misión**: Precisión, tiempo de despeje, daño recibido y rango táctico guardado localmente en `ConfigFile` (`user://`).

---

## Fase 5 — Optimización Móvil y Empaquetado Release

- [ ] **Perfilado en gama baja/media (32 y 64 bits)**:
  - Occlusion culling / frustum y LOD ligero en pasillos y habitaciones cerradas.
  - Pool reutilizable de casquillos (`ShellCasing`) y partículas para evitar picos de memoria en Android.
  - Selector de calidad gráfica en `SettingsScreen` (Sombras/Resolución/FPS límite 30-60).
- [ ] **Workflow de APK Release firmado**:
  - Firma con keystore de producción mediante GitHub Secrets manteniendo soporte dual `armeabi-v7a` + `arm64-v8a` para publicación en Uptodown y canales APK externos.
