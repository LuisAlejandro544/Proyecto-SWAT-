"""
build_m4.py
Genera el modelo 3D de la carabina táctica M4A1 para el agente SWAT.
Incluye piezas separadas animables para Godot:
  - M4_Body (receptor, cañón, guardamanos con rieles Picatinny, culata, mira holográfica, empuñadura, linterna)
  - M4_Bolt (cerrojo metálico visible que retrocede en cada disparo)
  - M4_ChargingHandle (palanca de carga trasera para animación de recarga)
  - M4_Magazine (cargador curvo STANAG desmontable para recarga)
  - MuzzlePoint (punto exacto del fogonazo)
  - EjectionPort (ventana de expulsión de casquillos)
"""

import os
import sys
import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "lib"))
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from mesh_utils import (
    clear_scene,
    get_or_create_material,
    create_empty,
    add_box,
    add_cylinder,
    add_extruded_profile,
    join_objects,
    export_hierarchy_glb,
)


def build_m4_model():
    """Construye la jerarquía completa de la carabina M4 y devuelve el nodo raíz."""
    clear_scene()

    # Paleta táctica PBR
    mat_gunmetal = get_or_create_material("M4_Gunmetal", (0.11, 0.12, 0.135), metallic=0.78, roughness=0.38)
    mat_receiver = get_or_create_material("M4_Receiver", (0.075, 0.08, 0.09), metallic=0.65, roughness=0.42)
    mat_polymer = get_or_create_material("M4_Polymer", (0.045, 0.048, 0.052), metallic=0.05, roughness=0.68)
    mat_steel = get_or_create_material("M4_SteelBolt", (0.52, 0.54, 0.58), metallic=0.92, roughness=0.25)
    mat_optic_lens = get_or_create_material(
        "M4_OpticLens",
        (0.05, 0.16, 0.24),
        metallic=0.2,
        roughness=0.08,
        emission_color=(0.95, 0.15, 0.12),
        emission_strength=0.45,
    )
    mat_reticle = get_or_create_material(
        "M4_RedDot",
        (1.0, 0.15, 0.1),
        metallic=0.0,
        roughness=0.2,
        emission_color=(1.0, 0.12, 0.08),
        emission_strength=6.0,
    )
    mat_flashlight_lens = get_or_create_material(
        "M4_FlashlightLens",
        (0.85, 0.9, 0.95),
        metallic=0.1,
        roughness=0.1,
        emission_color=(0.95, 0.96, 1.0),
        emission_strength=1.5,
    )

    root = create_empty("M4_Root", (0.0, 0.0, 0.0))
    body_parts = []

    # 1. Receptor inferior y superior (Eje Y = adelante)
    lower_pts = [
        (-0.085, -0.025),
        (0.065, -0.025),
        (0.082, -0.048),
        (0.118, -0.048),
        (0.118, 0.018),
        (-0.085, 0.018),
    ]
    body_parts.append(add_extruded_profile("LowerReceiver", lower_pts, 0.034, material=mat_receiver, bevel=0.002))
    body_parts.append(add_box("UpperReceiver", (0.036, 0.205, 0.040), (0.0, 0.016, 0.036), material=mat_receiver, bevel=0.0025))
    # Deflector de casquillos en lado derecho
    body_parts.append(add_box("BrassDeflector", (0.012, 0.018, 0.018), (0.022, -0.015, 0.037), (0, 0, -20), material=mat_receiver, bevel=0.0015))
    # Guardamonte y gatillo
    body_parts.append(add_box("TriggerGuardBottom", (0.012, 0.056, 0.006), (0.0, -0.012, -0.044), material=mat_receiver, bevel=0.001))
    body_parts.append(add_box("TriggerGuardFront", (0.012, 0.008, 0.024), (0.0, 0.015, -0.034), (18, 0, 0), material=mat_receiver, bevel=0.001))
    body_parts.append(add_box("Trigger", (0.006, 0.008, 0.022), (0.0, -0.016, -0.030), (-22, 0, 0), material=mat_steel, bevel=0.001))

    # Empuñadura táctica (Pistol Grip)
    grip_pts = [
        (-0.072, -0.016),
        (-0.035, -0.016),
        (-0.062, -0.105),
        (-0.104, -0.102),
    ]
    body_parts.append(add_extruded_profile("PistolGrip", grip_pts, 0.029, material=mat_polymer, bevel=0.003))

    # 2. Tubo de culata y culata SOPMOD retráctil
    body_parts.append(add_cylinder("BufferTube", 0.0155, 0.175, 18, (0.0, -0.175, 0.028), (90, 0, 0), material=mat_gunmetal))
    stock_pts = [
        (-0.275, -0.052),
        (-0.145, -0.008),
        (-0.145, 0.048),
        (-0.275, 0.050),
    ]
    body_parts.append(add_extruded_profile("Buttstock", stock_pts, 0.040, material=mat_polymer, bevel=0.0035))
    body_parts.append(add_box("Buttpad", (0.042, 0.012, 0.104), (0.0, -0.280, 0.0), material=mat_polymer, bevel=0.003))
    # Apoyo lateral para mejilla (SOPMOD)
    body_parts.append(add_cylinder("StockCheekL", 0.014, 0.120, 14, (-0.019, -0.210, 0.028), (90, 0, 0), material=mat_polymer))
    body_parts.append(add_cylinder("StockCheekR", 0.014, 0.120, 14, (0.019, -0.210, 0.028), (90, 0, 0), material=mat_polymer))

    # 3. Guardamanos táctico (Quad-rail) y riel Picatinny superior
    body_parts.append(add_box("HandguardCore", (0.044, 0.215, 0.048), (0.0, 0.228, 0.032), material=mat_gunmetal, bevel=0.002))
    # Dientes del riel Picatinny superior (desde receptor hasta punta de guardamanos)
    for idx in range(22):
        y_pos = -0.065 + idx * 0.018
        body_parts.append(add_box(f"RailTop_{idx}", (0.021, 0.010, 0.007), (0.0, y_pos, 0.059), material=mat_gunmetal, bevel=0.0008))
    # Rieles laterales e inferior del guardamanos
    for idx in range(10):
        y_pos = 0.135 + idx * 0.019
        body_parts.append(add_box(f"RailBot_{idx}", (0.020, 0.010, 0.006), (0.0, y_pos, 0.006), material=mat_gunmetal, bevel=0.0008))
        body_parts.append(add_box(f"RailL_{idx}", (0.006, 0.010, 0.018), (-0.024, y_pos, 0.032), material=mat_gunmetal, bevel=0.0008))
        body_parts.append(add_box(f"RailR_{idx}", (0.006, 0.010, 0.018), (0.024, y_pos, 0.032), material=mat_gunmetal, bevel=0.0008))

    # 4. Empuñadura vertical delantera (Foregrip) y linterna táctica lateral
    body_parts.append(add_cylinder("Foregrip", 0.015, 0.088, 16, (0.0, 0.235, -0.040), (0, 0, 0), material=mat_polymer, bevel=0.002))
    body_parts.append(add_box("ForegripMount", (0.026, 0.034, 0.016), (0.0, 0.235, 0.001), material=mat_gunmetal, bevel=0.001))

    body_parts.append(add_cylinder("FlashlightBody", 0.013, 0.095, 16, (0.036, 0.265, 0.032), (90, 0, 0), material=mat_gunmetal))
    body_parts.append(add_cylinder("FlashlightHead", 0.016, 0.026, 16, (0.036, 0.315, 0.032), (90, 0, 0), material=mat_gunmetal))
    body_parts.append(add_cylinder("FlashlightLens", 0.013, 0.004, 16, (0.036, 0.328, 0.032), (90, 0, 0), material=mat_flashlight_lens))

    # 5. Cañón, bloque de gas (mira frontal A-frame) y apagallamas (flash hider)
    body_parts.append(add_cylinder("Barrel", 0.0105, 0.210, 18, (0.0, 0.380, 0.032), (90, 0, 0), material=mat_gunmetal))
    body_parts.append(add_box("GasBlockBase", (0.018, 0.034, 0.038), (0.0, 0.365, 0.046), material=mat_gunmetal, bevel=0.0015))
    body_parts.append(add_box("FrontSightPost", (0.008, 0.014, 0.028), (0.0, 0.370, 0.072), (10, 0, 0), material=mat_gunmetal, bevel=0.001))
    body_parts.append(add_cylinder("FlashHider", 0.013, 0.048, 12, (0.0, 0.485, 0.032), (90, 0, 0), material=mat_steel, bevel=0.001))

    # 6. Mira Holográfica / Red Dot sobre el riel superior
    body_parts.append(add_box("OpticBase", (0.032, 0.068, 0.014), (0.0, 0.020, 0.069), material=mat_gunmetal, bevel=0.0015))
    body_parts.append(add_box("OpticHoodTop", (0.034, 0.056, 0.006), (0.0, 0.022, 0.106), material=mat_receiver, bevel=0.0015))
    body_parts.append(add_box("OpticHoodL", (0.006, 0.056, 0.034), (-0.015, 0.022, 0.090), material=mat_receiver, bevel=0.001))
    body_parts.append(add_box("OpticHoodR", (0.006, 0.056, 0.034), (0.015, 0.022, 0.090), material=mat_receiver, bevel=0.001))
    body_parts.append(add_box("OpticGlass", (0.023, 0.003, 0.026), (0.0, 0.036, 0.090), material=mat_optic_lens, bevel=0.0))
    body_parts.append(add_box("OpticReticleDot", (0.0022, 0.0022, 0.0022), (0.0, 0.034, 0.090), material=mat_reticle, bevel=0.0))

    # Unir el cuerpo fijo en M4_Body
    join_objects(body_parts, "M4_Body", parent=root)

    # 7. PIEZAS ANIMABLES SEPARADAS
    # Cerrojo metálico (retrocede al disparar)
    bolt = add_box("M4_Bolt", (0.014, 0.052, 0.016), (0.013, 0.032, 0.036), material=mat_steel, bevel=0.001, parent=root)

    # Palanca de carga trasera (Charging Handle)
    ch_parts = [
        add_box("CH_Bar", (0.014, 0.032, 0.007), (0.0, -0.092, 0.052), material=mat_gunmetal, bevel=0.001),
        add_box("CH_T", (0.044, 0.012, 0.010), (0.0, -0.108, 0.052), material=mat_gunmetal, bevel=0.0015),
    ]
    join_objects(ch_parts, "M4_ChargingHandle", parent=root)

    # Cargador STANAG curvo (se extrae e inserta al recargar)
    mag_pts = [
        (0.068, -0.028),
        (0.114, -0.028),
        (0.122, -0.095),
        (0.136, -0.155),
        (0.090, -0.165),
        (0.074, -0.095),
    ]
    mag_parts = [add_extruded_profile("MagCore", mag_pts, 0.024, material=mat_polymer, bevel=0.002)]
    # Nervaduras del cargador
    for idx in range(4):
        z_r = -0.075 - idx * 0.020
        y_r = 0.095 + idx * 0.004
        mag_parts.append(add_box(f"MagRib_{idx}", (0.026, 0.036, 0.006), (0.0, y_r, z_r), (-10, 0, 0), material=mat_gunmetal, bevel=0.001))
    join_objects(mag_parts, "M4_Magazine", parent=root)

    # Marcadores de puntos de disparo y expulsión para Godot
    create_empty("MuzzlePoint", (0.0, 0.512, 0.032), parent=root)
    create_empty("EjectionPort", (0.022, 0.032, 0.038), parent=root)

    return root


if __name__ == "__main__":
    m4_root = build_m4_model()
    out_file = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "godot-project", "assets", "models", "m4.glb"))
    export_hierarchy_glb(m4_root, out_file)
