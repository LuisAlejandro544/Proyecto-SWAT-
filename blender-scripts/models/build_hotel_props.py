"""
build_hotel_props.py
Genera el mobiliario táctico del hotel y el modelo base de terrorista ("píldora táctica")
en archivos GLB individuales listos para usarse como cobertura y decorado en los 2 pisos del hotel:
  - hotel_bed.glb
  - hotel_desk.glb
  - hotel_sofa.glb
  - hotel_pillar.glb
  - hotel_plant.glb
  - terrorist_pill.glb (cápsula con chaleco táctico, pasamontañas y soporte de arma)
"""

import math
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
    apply_material,
    add_bevel,
    set_smooth_with_sharp_edges,
    join_objects,
    export_hierarchy_glb,
)


def build_hotel_bed():
    """Cama doble de hotel con cabecero de madera, colchón, edredón y almohadas."""
    clear_scene()
    mat_wood = get_or_create_material("Hotel_DarkWood", (0.20, 0.10, 0.055), roughness=0.48)
    mat_sheet = get_or_create_material("Hotel_LinenWhite", (0.88, 0.87, 0.84), roughness=0.82)
    mat_duvet = get_or_create_material("Hotel_DuvetBurgundy", (0.42, 0.10, 0.12), roughness=0.78)
    mat_pillow = get_or_create_material("Hotel_PillowCream", (0.94, 0.92, 0.88), roughness=0.85)

    root = create_empty("HotelBed_Root", (0.0, 0.0, 0.0))
    parts = [
        add_box("BedBase", (1.60, 2.10, 0.24), (0.0, 0.0, 0.20), material=mat_wood, bevel=0.01),
        add_box("Headboard", (1.68, 0.10, 1.15), (0.0, -1.04, 0.575), material=mat_wood, bevel=0.015),
        add_box("Mattress", (1.52, 1.98, 0.24), (0.0, 0.02, 0.42), material=mat_sheet, bevel=0.03),
        add_box("Duvet", (1.56, 1.38, 0.25), (0.0, 0.34, 0.44), material=mat_duvet, bevel=0.04),
        add_box("PillowL", (0.58, 0.38, 0.14), (-0.38, -0.74, 0.59), (12, 0, 0), material=mat_pillow, bevel=0.04),
        add_box("PillowR", (0.58, 0.38, 0.14), (0.38, -0.74, 0.59), (12, 0, 0), material=mat_pillow, bevel=0.04),
    ]
    for sx in (-0.72, 0.72):
        for sy in (-0.96, 0.96):
            parts.append(add_cylinder(f"Leg_{sx}_{sy}", 0.035, 0.10, 10, (sx, sy, 0.05), material=mat_wood))
    join_objects(parts, "HotelBed_Mesh", parent=root)
    return root


def build_hotel_desk():
    """Escritorio / mostrador de recepción (cobertura sólida a altura de pecho/cintura)."""
    clear_scene()
    mat_wood = get_or_create_material("Desk_Walnut", (0.24, 0.12, 0.06), roughness=0.44)
    mat_top = get_or_create_material("Desk_MarbleTop", (0.76, 0.75, 0.72), roughness=0.28)
    mat_brass = get_or_create_material("Desk_Brass", (0.82, 0.64, 0.24), metallic=0.90, roughness=0.25)

    root = create_empty("HotelDesk_Root", (0.0, 0.0, 0.0))
    parts = [
        add_box("DeskTop", (1.80, 0.78, 0.07), (0.0, 0.0, 0.88), material=mat_top, bevel=0.01),
        add_box("FrontPanel", (1.72, 0.08, 0.85), (0.0, 0.33, 0.425), material=mat_wood, bevel=0.008),
        add_box("SideL", (0.08, 0.72, 0.85), (-0.82, 0.0, 0.425), material=mat_wood, bevel=0.008),
        add_box("SideR", (0.08, 0.72, 0.85), (0.82, 0.0, 0.425), material=mat_wood, bevel=0.008),
        add_box("DrawerBox", (0.56, 0.64, 0.76), (0.52, -0.02, 0.44), material=mat_wood, bevel=0.008),
        add_box("BrassTrim", (1.74, 0.02, 0.05), (0.0, 0.375, 0.10), material=mat_brass, bevel=0.003),
    ]
    for idx, z_d in enumerate((0.25, 0.47, 0.69)):
        parts.append(add_box(f"Handle_{idx}", (0.14, 0.02, 0.02), (0.52, -0.35, z_d), material=mat_brass, bevel=0.003))
    join_objects(parts, "HotelDesk_Mesh", parent=root)
    return root


def build_hotel_sofa():
    """Sofá de lobby elegante para cobertura táctica en el vestíbulo."""
    clear_scene()
    mat_leather = get_or_create_material("Sofa_Leather", (0.28, 0.14, 0.09), roughness=0.45)
    mat_wood = get_or_create_material("Sofa_Wood", (0.15, 0.07, 0.04), roughness=0.5)

    root = create_empty("HotelSofa_Root", (0.0, 0.0, 0.0))
    parts = [
        add_box("Base", (1.90, 0.86, 0.22), (0.0, 0.0, 0.18), material=mat_leather, bevel=0.03),
        add_box("Backrest", (1.90, 0.22, 0.62), (0.0, -0.32, 0.56), (-10, 0, 0), material=mat_leather, bevel=0.04),
        add_box("ArmL", (0.20, 0.86, 0.42), (-0.85, 0.0, 0.42), material=mat_leather, bevel=0.035),
        add_box("ArmR", (0.20, 0.86, 0.42), (0.85, 0.0, 0.42), material=mat_leather, bevel=0.035),
        add_box("CushionL", (0.74, 0.64, 0.14), (-0.38, 0.06, 0.34), material=mat_leather, bevel=0.035),
        add_box("CushionR", (0.74, 0.64, 0.14), (0.38, 0.06, 0.34), material=mat_leather, bevel=0.035),
    ]
    for sx in (-0.84, 0.84):
        for sy in (-0.34, 0.34):
            parts.append(add_cylinder(f"SofaLeg_{sx}_{sy}", 0.03, 0.08, 10, (sx, sy, 0.04), material=mat_wood))
    join_objects(parts, "HotelSofa_Mesh", parent=root)
    return root


def build_hotel_pillar():
    """Columna de mármol y latón para el vestíbulo de 2 pisos del hotel."""
    clear_scene()
    mat_marble = get_or_create_material("Pillar_Marble", (0.84, 0.82, 0.78), roughness=0.25)
    mat_brass = get_or_create_material("Pillar_Brass", (0.82, 0.65, 0.25), metallic=0.9, roughness=0.24)

    root = create_empty("HotelPillar_Root", (0.0, 0.0, 0.0))
    parts = [
        add_box("PlinthBase", (0.86, 0.86, 0.28), (0.0, 0.0, 0.14), material=mat_marble, bevel=0.015),
        add_box("PlinthTrim", (0.78, 0.78, 0.08), (0.0, 0.0, 0.32), material=mat_brass, bevel=0.01),
        add_cylinder("Shaft", 0.30, 3.30, 20, (0.0, 0.0, 2.00), material=mat_marble),
        add_box("CapTrim", (0.78, 0.78, 0.08), (0.0, 0.0, 3.68), material=mat_brass, bevel=0.01),
        add_box("Capital", (0.88, 0.88, 0.24), (0.0, 0.0, 3.84), material=mat_marble, bevel=0.015),
    ]
    join_objects(parts, "HotelPillar_Mesh", parent=root)
    return root


def build_hotel_plant():
    """Maceta decorativa con hojas estilizadas para pasillos y lobby."""
    clear_scene()
    mat_pot = get_or_create_material("Plant_Ceramic", (0.62, 0.30, 0.18), roughness=0.42)
    mat_soil = get_or_create_material("Plant_Soil", (0.14, 0.09, 0.06), roughness=0.95)
    mat_leaf = get_or_create_material("Plant_Leaf", (0.14, 0.42, 0.16), roughness=0.55)

    root = create_empty("HotelPlant_Root", (0.0, 0.0, 0.0))
    parts = [
        add_cylinder("Pot", 0.24, 0.46, 16, (0.0, 0.0, 0.23), material=mat_pot, bevel=0.01),
        add_cylinder("Soil", 0.21, 0.04, 14, (0.0, 0.0, 0.44), material=mat_soil),
    ]
    for i in range(7):
        ang = i * (360.0 / 7.0)
        rad = math.radians(ang)
        x_off = math.sin(rad) * 0.12
        y_off = math.cos(rad) * 0.12
        parts.append(
            add_box(
                f"Leaf_{i}",
                (0.11, 0.42, 0.018),
                (x_off, y_off, 0.74 + (i % 2) * 0.08),
                (38 + (i % 3) * 8, 0, -ang),
                material=mat_leaf,
                bevel=0.005,
            )
        )
    join_objects(parts, "HotelPlant_Mesh", parent=root)
    return root


def build_terrorist_pill():
    """
    Construye el cuerpo cápsula ('píldora táctica') del enemigo terrorista con chaleco,
    cartucheras y pasamontañas/visor para distinguirlo claramente mientras sostiene el AK-47.
    """
    clear_scene()
    mat_suit = get_or_create_material("Terrorist_Suit", (0.20, 0.21, 0.18), roughness=0.72)
    mat_vest = get_or_create_material("Terrorist_Vest", (0.11, 0.11, 0.12), roughness=0.62)
    mat_mask = get_or_create_material("Terrorist_Mask", (0.06, 0.06, 0.07), roughness=0.75)
    mat_visor = get_or_create_material(
        "Terrorist_Goggles",
        (0.45, 0.12, 0.06),
        metallic=0.35,
        roughness=0.18,
        emission_color=(0.75, 0.18, 0.08),
        emission_strength=0.45,
    )
    mat_skin = get_or_create_material("Terrorist_EyesArea", (0.58, 0.42, 0.34), roughness=0.65)

    root = create_empty("TerroristPill_Root", (0.0, 0.0, 0.0))

    # Cápsula base (altura total ~1.80m, apoyada en Z=0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.32, location=(0.0, 0.0, 0.32))
    cap_bot = bpy.context.active_object
    apply_material(cap_bot, mat_suit)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.32, location=(0.0, 0.0, 1.46))
    cap_top = bpy.context.active_object
    apply_material(cap_top, mat_mask)

    parts = [
        cap_bot,
        cap_top,
        add_cylinder("TorsoPill", 0.32, 1.14, 20, (0.0, 0.0, 0.89), material=mat_suit),
        # Chaleco táctico y portacargadores
        add_cylinder("TacticalVest", 0.345, 0.56, 20, (0.0, 0.0, 1.05), material=mat_vest, bevel=0.01),
        add_box("MagPouchL", (0.11, 0.09, 0.18), (-0.12, 0.32, 0.94), material=mat_vest, bevel=0.008),
        add_box("MagPouchC", (0.11, 0.09, 0.18), (0.0, 0.33, 0.94), material=mat_vest, bevel=0.008),
        add_box("MagPouchR", (0.11, 0.09, 0.18), (0.12, 0.32, 0.94), material=mat_vest, bevel=0.008),
        # Cinta roja/bandana y visor frontal para lectura clara de dirección (+Y adelante)
        add_cylinder("HeadBand", 0.328, 0.08, 20, (0.0, 0.0, 1.56), material=mat_visor),
        add_box("FaceOpening", (0.24, 0.12, 0.08), (0.0, 0.25, 1.48), material=mat_skin, bevel=0.01),
        add_box("Goggles", (0.26, 0.10, 0.075), (0.0, 0.29, 1.50), material=mat_visor, bevel=0.012),
    ]
    join_objects(parts, "TerroristPill_Body", parent=root)

    # Punto de montaje del AK-47 en el lado derecho del torso apuntando hacia adelante (+Y)
    create_empty("WeaponMount", (0.26, 0.24, 1.12), parent=root)

    return root


if __name__ == "__main__":
    out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "godot-project", "assets", "models"))
    export_hierarchy_glb(build_hotel_bed(), os.path.join(out_dir, "hotel_bed.glb"))
    export_hierarchy_glb(build_hotel_desk(), os.path.join(out_dir, "hotel_desk.glb"))
    export_hierarchy_glb(build_hotel_sofa(), os.path.join(out_dir, "hotel_sofa.glb"))
    export_hierarchy_glb(build_hotel_pillar(), os.path.join(out_dir, "hotel_pillar.glb"))
    export_hierarchy_glb(build_hotel_plant(), os.path.join(out_dir, "hotel_plant.glb"))
    export_hierarchy_glb(build_terrorist_pill(), os.path.join(out_dir, "terrorist_pill.glb"))
