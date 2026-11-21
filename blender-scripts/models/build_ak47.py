"""
build_ak47.py
Genera el modelo 3D del rifle AK-47 para los enemigos terroristas.
Incluye detalles equivalentes al M4: madera laminada, receptor estampado,
cargador curvo ("banana") desmontable, cerrojo lateral y puntos de disparo/expulsión.
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


def build_ak47_model():
    """Construye la jerarquía completa del AK-47 y devuelve el nodo raíz."""
    clear_scene()

    mat_steel_dark = get_or_create_material("AK_SteelDark", (0.08, 0.085, 0.095), metallic=0.80, roughness=0.38)
    mat_steel_bright = get_or_create_material("AK_SteelBright", (0.58, 0.60, 0.63), metallic=0.92, roughness=0.26)
    mat_wood = get_or_create_material("AK_Wood", (0.38, 0.16, 0.065), metallic=0.0, roughness=0.52)
    mat_bakelite = get_or_create_material("AK_Bakelite", (0.28, 0.085, 0.04), metallic=0.05, roughness=0.45)

    root = create_empty("AK47_Root", (0.0, 0.0, 0.0))
    body_parts = []

    # 1. Receptor estampado y tapa superior (Dust Cover)
    body_parts.append(add_box("AK_Receiver", (0.036, 0.220, 0.044), (0.0, 0.015, 0.018), material=mat_steel_dark, bevel=0.002))
    dust_pts = [
        (-0.095, 0.036),
        (0.115, 0.036),
        (0.110, 0.056),
        (-0.090, 0.054),
    ]
    body_parts.append(add_extruded_profile("AK_DustCover", dust_pts, 0.032, material=mat_steel_dark, bevel=0.003))
    # Palanca selectora lateral
    body_parts.append(add_box("AK_Selector", (0.006, 0.068, 0.014), (0.020, -0.020, 0.022), (8, 0, 0), material=mat_steel_dark, bevel=0.001))

    # Guardamonte y gatillo
    body_parts.append(add_box("AK_TriggerGuard", (0.012, 0.052, 0.005), (0.0, -0.010, -0.034), material=mat_steel_dark, bevel=0.001))
    body_parts.append(add_box("AK_TriggerGuardFront", (0.012, 0.007, 0.030), (0.0, 0.016, -0.018), (15, 0, 0), material=mat_steel_dark, bevel=0.001))
    body_parts.append(add_box("AK_Trigger", (0.006, 0.007, 0.022), (0.0, -0.014, -0.018), (-24, 0, 0), material=mat_steel_bright, bevel=0.001))

    # Empuñadura de baquelita
    grip_pts = [
        (-0.070, -0.002),
        (-0.036, -0.002),
        (-0.068, -0.095),
        (-0.104, -0.090),
    ]
    body_parts.append(add_extruded_profile("AK_PistolGrip", grip_pts, 0.028, material=mat_bakelite, bevel=0.003))

    # 2. Culata clásica de madera inclinada
    stock_pts = [
        (-0.092, 0.034),
        (-0.092, -0.005),
        (-0.315, -0.068),
        (-0.315, 0.014),
    ]
    body_parts.append(add_extruded_profile("AK_Buttstock", stock_pts, 0.034, material=mat_wood, bevel=0.0035))
    body_parts.append(add_box("AK_Buttplate", (0.035, 0.008, 0.084), (0.0, -0.319, -0.027), material=mat_steel_dark, bevel=0.002))

    # 3. Guardamanos inferior y superior de madera
    hand_low_pts = [
        (0.125, -0.004),
        (0.275, 0.004),
        (0.275, 0.032),
        (0.125, 0.034),
    ]
    body_parts.append(add_extruded_profile("AK_HandguardLower", hand_low_pts, 0.042, material=mat_wood, bevel=0.004))
    body_parts.append(add_cylinder("AK_HandguardUpper", 0.017, 0.135, 16, (0.0, 0.200, 0.042), (90, 0, 0), material=mat_wood, bevel=0.0015))
    # Abrazadera metálica frontal
    body_parts.append(add_box("AK_HandguardRetainer", (0.043, 0.014, 0.042), (0.0, 0.278, 0.024), material=mat_steel_dark, bevel=0.0015))

    # 4. Bloque de mira trasera, tubo de gases, cañón, baqueta y freno de boca
    body_parts.append(add_box("AK_RearSightBlock", (0.026, 0.044, 0.024), (0.0, 0.118, 0.048), material=mat_steel_dark, bevel=0.0015))
    body_parts.append(add_cylinder("AK_GasTube", 0.011, 0.085, 14, (0.0, 0.305, 0.042), (90, 0, 0), material=mat_steel_dark))
    body_parts.append(add_box("AK_GasBlock", (0.022, 0.024, 0.036), (0.0, 0.345, 0.030), (-18, 0, 0), material=mat_steel_dark, bevel=0.0015))

    body_parts.append(add_cylinder("AK_Barrel", 0.010, 0.265, 18, (0.0, 0.390, 0.020), (90, 0, 0), material=mat_steel_dark))
    # Baqueta clásica debajo del cañón
    body_parts.append(add_cylinder("AK_CleaningRod", 0.0038, 0.230, 10, (0.0, 0.375, 0.005), (90, 0, 0), material=mat_steel_dark))

    # Mira delantera icónica con protectores laterales
    body_parts.append(add_box("AK_FrontSightBase", (0.020, 0.024, 0.030), (0.0, 0.488, 0.032), material=mat_steel_dark, bevel=0.001))
    body_parts.append(add_box("AK_FrontSightHoodL", (0.004, 0.014, 0.026), (-0.009, 0.488, 0.056), material=mat_steel_dark, bevel=0.001))
    body_parts.append(add_box("AK_FrontSightHoodR", (0.004, 0.014, 0.026), (0.009, 0.488, 0.056), material=mat_steel_dark, bevel=0.001))
    body_parts.append(add_cylinder("AK_FrontPin", 0.0018, 0.018, 8, (0.0, 0.488, 0.052), (0, 0, 0), material=mat_steel_dark))

    # Freno de boca inclinado clásico AKM
    body_parts.append(add_cylinder("AK_MuzzleBrake", 0.0125, 0.032, 16, (0.0, 0.530, 0.020), (90, 0, 0), material=mat_steel_dark, bevel=0.001))

    join_objects(body_parts, "AK47_Body", parent=root)

    # 5. PIEZAS ANIMABLES SEPARADAS
    # Cerrojo cromado lateral
    bolt_parts = [
        add_box("AK_BoltCarrier", (0.012, 0.068, 0.018), (0.015, 0.038, 0.032), material=mat_steel_bright, bevel=0.001),
        add_cylinder("AK_ChargingHandle", 0.006, 0.024, 12, (0.028, 0.058, 0.032), (0, 90, 0), material=mat_steel_bright),
    ]
    join_objects(bolt_parts, "AK47_Bolt", parent=root)

    # Cargador curvo metálico ("banana")
    mag_pts = [
        (0.066, -0.004),
        (0.114, -0.004),
        (0.125, -0.075),
        (0.148, -0.135),
        (0.180, -0.185),
        (0.136, -0.205),
        (0.100, -0.145),
        (0.076, -0.075),
    ]
    mag_parts = [add_extruded_profile("AK_MagCore", mag_pts, 0.025, material=mat_steel_dark, bevel=0.002)]
    join_objects(mag_parts, "AK47_Magazine", parent=root)

    create_empty("MuzzlePoint", (0.0, 0.550, 0.020), parent=root)
    create_empty("EjectionPort", (0.022, 0.042, 0.034), parent=root)

    return root


if __name__ == "__main__":
    ak_root = build_ak47_model()
    out_file = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "godot-project", "assets", "models", "ak47.glb"))
    export_hierarchy_glb(ak_root, out_file)
