"""
generate_all.py
Script maestro para ejecutar desde Blender (--background --python blender-scripts/generate_all.py).
1. Genera y exporta todos los modelos .glb hacia godot-project/assets/models/.
2. Renderiza las previsualizaciones PNG hacia blender-scripts/previews/.
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")
LIB_DIR = os.path.join(SCRIPT_DIR, "lib")

for p in (SCRIPT_DIR, MODELS_DIR, LIB_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from mesh_utils import export_hierarchy_glb
from build_m4 import build_m4_model
from build_ak47 import build_ak47_model
from build_shell_casing import build_shell_casing_model
from build_hotel_door import build_hotel_door_model
from build_hotel_props import (
    build_hotel_bed,
    build_hotel_desk,
    build_hotel_sofa,
    build_hotel_pillar,
    build_hotel_plant,
    build_terrorist_pill,
)
from build_hotel_building import build_hotel_building
from render_previews import render_all_previews


def main():
    out_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "godot-project", "assets", "models"))
    os.makedirs(out_dir, exist_ok=True)

    builders = [
        ("m4.glb", build_m4_model),
        ("ak47.glb", build_ak47_model),
        ("shell_casing.glb", build_shell_casing_model),
        ("hotel_door.glb", build_hotel_door_model),
        ("hotel_bed.glb", build_hotel_bed),
        ("hotel_desk.glb", build_hotel_desk),
        ("hotel_sofa.glb", build_hotel_sofa),
        ("hotel_pillar.glb", build_hotel_pillar),
        ("hotel_plant.glb", build_hotel_plant),
        ("terrorist_pill.glb", build_terrorist_pill),
        ("hotel_building.glb", build_hotel_building),
    ]

    for filename, builder in builders:
        root_obj = builder()
        export_hierarchy_glb(root_obj, os.path.join(out_dir, filename))

    render_all_previews()
    print("Todos los modelos GLB y previsualizaciones PNG fueron generados correctamente.")


if __name__ == "__main__":
    main()
