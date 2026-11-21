"""
build_shell_casing.py
Genera el modelo 3D de un casquillo/vaina metálica (protección del proyectil)
que sale expulsado al disparar el M4 y la AK-47, cayendo con físicas al suelo.
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
    add_cylinder,
    join_objects,
    export_hierarchy_glb,
)


def build_shell_casing_model():
    """Construye un casquillo de latón 5.56mm escalado para lectura visual clara en cámara FPS."""
    clear_scene()

    mat_brass = get_or_create_material("Shell_Brass", (0.86, 0.66, 0.24), metallic=0.94, roughness=0.22)
    mat_primer = get_or_create_material("Shell_Primer", (0.72, 0.45, 0.32), metallic=0.90, roughness=0.30)
    mat_hollow = get_or_create_material("Shell_Hollow", (0.04, 0.04, 0.04), metallic=0.2, roughness=0.8)

    root = create_empty("ShellCasing_Root", (0.0, 0.0, 0.0))
    parts = []

    # Base / reborde (rim) y ranura extractora
    parts.append(add_cylinder("Rim", 0.0072, 0.003, 14, (0.0, -0.022, 0.0), (90, 0, 0), material=mat_brass))
    parts.append(add_cylinder("Primer", 0.0032, 0.0035, 12, (0.0, -0.0222, 0.0), (90, 0, 0), material=mat_primer))
    parts.append(add_cylinder("Groove", 0.0056, 0.003, 14, (0.0, -0.019, 0.0), (90, 0, 0), material=mat_brass))
    # Cuerpo principal del casquillo
    parts.append(add_cylinder("Body", 0.0070, 0.028, 16, (0.0, -0.0035, 0.0), (90, 0, 0), material=mat_brass))
    # Cuello estrecho hacia la boca
    parts.append(add_cylinder("Neck", 0.0046, 0.011, 16, (0.0, 0.0155, 0.0), (90, 0, 0), material=mat_brass))
    # Interior oscuro en la punta (boca abierta donde estaba la bala)
    parts.append(add_cylinder("MouthHollow", 0.0036, 0.002, 14, (0.0, 0.0205, 0.0), (90, 0, 0), material=mat_hollow))

    join_objects(parts, "ShellCasing_Mesh", parent=root)
    return root


if __name__ == "__main__":
    shell_root = build_shell_casing_model()
    out_file = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "godot-project", "assets", "models", "shell_casing.glb"))
    export_hierarchy_glb(shell_root, out_file)
