"""
render_previews.py
Renderiza imágenes PNG de estudio de todos los assets generados en Blender para verificar
visualmente proporciones, materiales y detalles tanto localmente como en GitHub Actions.
"""

import math
import os
import sys
import bpy
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")
if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

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


def setup_studio_lighting_and_camera(target_pos: Vector, cam_pos: Vector, lens_mm: float = 48.0):
    """Configura iluminación de estudio de 3 puntos y cámara mirando al objetivo."""
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Fondo neutro oscuro para que destaquen los metales, maderas y latón
    if scene.world is None:
        scene.world = bpy.data.worlds.new("StudioWorld")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.09, 0.11, 0.14, 1.0)
        bg.inputs["Strength"].default_value = 0.7

    # Luz principal (Key), relleno (Fill) y contra (Rim)
    def add_area_light(name, loc, energy, size, color=(1.0, 1.0, 1.0)):
        light_data = bpy.data.lights.new(name=name, type='AREA')
        light_data.energy = energy
        light_data.size = size
        light_data.color = color
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        light_obj.location = Vector(loc)
        direction = target_pos - light_obj.location
        light_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.collection.objects.link(light_obj)

    span = max(0.3, (cam_pos - target_pos).length)
    add_area_light("KeyLight", target_pos + Vector((span * 0.9, span * 0.7, span * 0.9)), 28.0 * span * span, span * 0.8, (1.0, 0.97, 0.92))
    add_area_light("FillLight", target_pos + Vector((-span * 1.1, span * 0.4, span * 0.3)), 10.0 * span * span, span * 1.2, (0.78, 0.88, 1.0))
    add_area_light("RimLight", target_pos + Vector((-span * 0.4, -span * 1.0, span * 0.8)), 16.0 * span * span, span * 0.7, (1.0, 0.95, 0.88))

    cam_data = bpy.data.cameras.new("StudioCam")
    cam_data.lens = lens_mm
    cam_data.clip_start = 0.005
    cam_data.clip_end = 100.0
    cam_obj = bpy.data.objects.new("StudioCam", cam_data)
    cam_obj.location = cam_pos
    direction = target_pos - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj


def render_preview_png(output_path: str, target_pos: tuple, cam_pos: tuple, lens_mm: float = 48.0):
    """Renderiza la escena actual a un archivo PNG."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    setup_studio_lighting_and_camera(Vector(target_pos), Vector(cam_pos), lens_mm)
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"[PNG Preview] {output_path}")


def render_all_previews():
    """Genera los PNG de inspección para cada arma, casquillo, puerta y mobiliario."""
    previews_dir = os.path.join(SCRIPT_DIR, "previews")

    build_m4_model()
    render_preview_png(
        os.path.join(previews_dir, "m4_preview.png"),
        target_pos=(0.0, 0.11, -0.02),
        cam_pos=(0.95, 0.42, 0.25),
        lens_mm=44.0,
    )

    build_ak47_model()
    render_preview_png(
        os.path.join(previews_dir, "ak47_preview.png"),
        target_pos=(0.0, 0.11, -0.03),
        cam_pos=(1.02, 0.44, 0.24),
        lens_mm=44.0,
    )

    build_shell_casing_model()
    render_preview_png(
        os.path.join(previews_dir, "shell_casing_preview.png"),
        target_pos=(0.0, 0.0, 0.0),
        cam_pos=(0.068, 0.052, 0.036),
        lens_mm=50.0,
    )

    build_hotel_door_model()
    render_preview_png(
        os.path.join(previews_dir, "hotel_door_preview.png"),
        target_pos=(0.0, 0.0, 1.12),
        cam_pos=(1.85, -3.45, 1.45),
        lens_mm=38.0,
    )

    build_terrorist_pill()
    render_preview_png(
        os.path.join(previews_dir, "terrorist_pill_preview.png"),
        target_pos=(0.0, 0.0, 0.90),
        cam_pos=(1.75, 2.75, 1.38),
        lens_mm=42.0,
    )

    # Render combinado de mobiliario del hotel
    build_hotel_bed()
    render_preview_png(
        os.path.join(previews_dir, "hotel_bed_preview.png"),
        target_pos=(0.0, 0.0, 0.45),
        cam_pos=(2.10, 2.25, 1.45),
        lens_mm=40.0,
    )

    build_hotel_desk()
    render_preview_png(
        os.path.join(previews_dir, "hotel_desk_preview.png"),
        target_pos=(0.0, 0.0, 0.48),
        cam_pos=(1.85, 1.95, 1.25),
        lens_mm=42.0,
    )

    build_hotel_sofa()
    render_preview_png(
        os.path.join(previews_dir, "hotel_sofa_preview.png"),
        target_pos=(0.0, 0.0, 0.38),
        cam_pos=(1.95, 2.05, 1.18),
        lens_mm=42.0,
    )


if __name__ == "__main__":
    render_all_previews()
