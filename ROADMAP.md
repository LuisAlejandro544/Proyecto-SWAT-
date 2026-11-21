# ROADMAP — SWAT: Asalto al Hotel

Hoja de ruta evolutiva del proyecto móvil 3D FPS en **Godot 4.7.2-stable** + **Blender 4.5.16 LTS**.

---

## Fase 1 — Cimientos Técnicos, Gran Hotel y Pipeline CI/CD (Estado Actual)

- [x] **Motor base y renderizado híbrido**: Configuración de `Godot 4.7.2-stable` con renderizador `mobile` (**Vulkan 1.1**) en Android y `fallback_to_opengl3=true` automático a **OpenGL ES 3.0** (`gl_compatibility`) para procesadores sin Vulkan, más ACES tonemap, glow sutil y `ReflectionProbe`.
- [x] **Pipeline de assets en Blender 4.5.16 LTS**: Scripts Python en `blender-scripts/` para generar todos los `.glb` (incluyendo el Gran Hotel completo en `hotel_building.glb` con texturas PBR empaquetadas y colisionadores `-col`) y renders de estudio `.png` sin dependencias externas de pago ni copyright.
- [x] **Arma SWAT M4**: Jerarquía modular (`M4_Body`, `M4_Bolt`, `M4_ChargingHandle`, `M4_Magazine`, `MuzzlePoint`, `EjectionPort`) con las 5 animaciones completas (idle/sway/ADS, retroceso+cerrojo, fogonazo 3D+luz, recarga táctica, casquillos físicos).
- [x] **Gran Hotel de 2 pisos (`36m x 32m`, Misión 1 en `hotel_building.glb`)**: Gran lobby con candelabro y techo artesonado, mármol con cenefas, lounge bar, recepción con casillero y carro de equipaje, ascensores, escalera imperial con balaustradas completas, `NavigationRegion3D` y 7 habitaciones/suites amuebladas (`101–103` y `201–204`) con puertas animadas (`HotelDoor.tscn`).
- [x] **IA Terrorista con AK-47 (10 objetivos)**: Enemigos basados en cápsula táctica (`terrorist_pill.glb`) con estados `GUARD`, `ALERT`, `COMBAT`, `RELOADING`, `NEUTRALIZED`, apertura de puertas bloqueantes, capas de hitbox precisas y AK-47 animado.
- [x] **UI y UX Móvil Ergonómica**: Pantallas independientes (`MainMenu`, `SettingsScreen`, `ControlsGuideScreen`), `MobileHUD` con arco circular de botones tipo shooter móvil profesional, indicador direccional de daño y `VirtualJoystick` multi-touch centrado.
- [x] **Compilación APK Debug en GitHub Actions**: Workflow manual (`workflow_dispatch`) con caché de Godot, plantillas e importación `.godot`, generando APK dual **32 bits (`armeabi-v7a`) + 64 bits (`arm64-v8a`)** listo para instalación directa / Uptodown.

---

## Fase 2 — Pulido de Combate, Impactos y Sensación Táctica

- [x] **Indicador direccional de daño**: Señalización en bordes de pantalla según dirección del fuego recibido.
- [ ] **Feedback balístico avanzado**:
  - Trazadores visibles de balas en ráfagas y chispas/polvo al impactar paredes, madera y metal.
  - Marcas temporales de impacto (decals) optimizadas por pooling para móvil.
  - Animación de muerte/caída física para los terroristas neutralizados.
- [ ] **Audio táctico ampliado**:
  - Pasos diferenciados por superficie (mármol en vestíbulo vs alfombra en pasillos/habitaciones).
  - Sonido de respiración con salud baja.
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
