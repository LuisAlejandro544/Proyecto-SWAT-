"""
build_hotel_door.py
Genera la puerta animable de las habitaciones del hotel (hotel_door.glb).
Estructura pensada para animación de apertura/cierre en Godot:
  - DoorFrame (marco fijo de madera oscura y placa numérica de latón)
  - DoorPivot (pivote ubicado exactamente en la bisagra izquierda x = -0.50)
    - DoorLeaf (hoja de puerta con paneles en relieve, mirilla y manija en ambos lados)
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
    join_objects,
    export_hierarchy_glb,
)


def build_hotel_door_model():
    """Construye una puerta de habitación de hotel estándar (ancho útil 1.0m, alto 2.2m)."""
    clear_scene()

    mat_wood_frame = get_or_create_material("Door_MahoganyDark", (0.18, 0.08, 0.045), metallic=0.0, roughness=0.52)
    mat_wood_leaf = get_or_create_material("Door_Walnut", (0.30, 0.14, 0.075), metallic=0.0, roughness=0.45)
    mat_wood_trim = get_or_create_material("Door_Trim", (0.24, 0.11, 0.055), metallic=0.0, roughness=0.42)
    mat_brass = get_or_create_material("Door_Brass", (0.82, 0.65, 0.25), metallic=0.92, roughness=0.24)
    mat_dark_metal = get_or_create_material("Door_DarkMetal", (0.12, 0.12, 0.14), metallic=0.7, roughness=0.4)

    root = create_empty("HotelDoor_Root", (0.0, 0.0, 0.0))

    # 1. Marco fijo de la puerta (abertura de 1.00m x 2.20m)
    frame_parts = [
        add_box("Frame_Left", (0.08, 0.16, 2.28), (-0.54, 0.0, 1.14), material=mat_wood_frame, bevel=0.004),
        add_box("Frame_Right", (0.08, 0.16, 2.28), (0.54, 0.0, 1.14), material=mat_wood_frame, bevel=0.004),
        add_box("Frame_Top", (1.16, 0.16, 0.08), (0.0, 0.0, 2.24), material=mat_wood_frame, bevel=0.004),
        add_box("Threshold", (1.02, 0.14, 0.015), (0.0, 0.0, 0.0075), material=mat_brass, bevel=0.002),
    ]
    join_objects(frame_parts, "DoorFrame", parent=root)

    # 2. Pivote de bisagra (en x = -0.50, y = 0.0, z = 0.0)
    # Al rotar DoorPivot en Y en Godot (rotación sobre eje vertical), la puerta abre suavemente.
    pivot = create_empty("DoorPivot", (-0.50, 0.0, 0.0), parent=root)

    leaf_parts = []
    # Hoja principal centrada en x = +0.50 respecto al pivote
    leaf_parts.append(add_box("Leaf_Core", (0.99, 0.055, 2.18), (0.50, 0.0, 1.10), material=mat_wood_leaf, bevel=0.003))

    # Molduras decorativas en ambas caras
    for side_y in (-0.030, 0.030):
        # Panel superior e inferior en relieve
        leaf_parts.append(add_box(f"PanelTop_{side_y}", (0.72, 0.012, 0.86), (0.50, side_y, 1.56), material=mat_wood_trim, bevel=0.003))
        leaf_parts.append(add_box(f"PanelBot_{side_y}", (0.72, 0.012, 0.68), (0.50, side_y, 0.54), material=mat_wood_trim, bevel=0.003))
        # Placa protectora metálica inferior (kickplate)
        leaf_parts.append(add_box(f"Kickplate_{side_y}", (0.92, 0.006, 0.18), (0.50, side_y * 1.02, 0.11), material=mat_brass, bevel=0.001))
        # Base de manija y picaporte de palanca en el lado derecho (x = 0.88)
        leaf_parts.append(add_box(f"HandlePlate_{side_y}", (0.055, 0.010, 0.18), (0.88, side_y * 1.05, 1.02), material=mat_brass, bevel=0.002))
        sign = 1.0 if side_y > 0 else -1.0
        leaf_parts.append(add_cylinder(f"HandleStem_{side_y}", 0.012, 0.045, 12, (0.88, side_y + sign * 0.025, 1.02), (90, 0, 0), material=mat_brass))
        leaf_parts.append(add_box(f"HandleLever_{side_y}", (0.125, 0.016, 0.020), (0.83, side_y + sign * 0.048, 1.02), material=mat_brass, bevel=0.003))

    # Mirilla central y placa dorada de número de habitación en lado exterior (-Y)
    leaf_parts.append(add_cylinder("Peephole", 0.012, 0.068, 12, (0.50, 0.0, 1.62), (90, 0, 0), material=mat_brass))
    leaf_parts.append(add_box("RoomPlaque", (0.14, 0.010, 0.065), (0.50, -0.036, 1.82), material=mat_brass, bevel=0.002))

    # Bisagras visibles en el lado del pivote
    for hz in (0.35, 1.10, 1.85):
        leaf_parts.append(add_cylinder(f"Hinge_{hz}", 0.012, 0.09, 10, (0.005, -0.028, hz), (0, 0, 0), material=mat_dark_metal))

    join_objects(leaf_parts, "DoorLeaf", parent=pivot)

    return root


if __name__ == "__main__":
    door_root = build_hotel_door_model()
    out_file = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "godot-project", "assets", "models", "hotel_door.glb"))
    export_hierarchy_glb(door_root, out_file)
