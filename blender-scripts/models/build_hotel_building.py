"""
build_hotel_building.py
Construye en Blender 4.5.16 LTS el edificio completo del Gran Hotel Corona (36m x 32m, 2 pisos,
altura 9.0m) con texturas PBR procedurales empaquetadas y colisionadores automáticos (-col) para Godot 4.7.2:
  - Planta Baja (Y=0.0): Atrium con cenefa de mármol oscuro/latón, entrada principal acristalada,
    recepción con casillero de llaves y carro de equipaje, Lounge Bar con taburetes,
    banco de ascensores de latón, Escalera Imperial y salas 101 (Conferencias), 102 (Seguridad), 103.
  - Segundo Piso (Y=4.0): Mezanine con balaustradas completas (incluyendo hueco de escalera),
    apliques de pared, cuadros enmarcados, ascensores y habitaciones 201, 202, 203 y Suite Presidencial 204.
  - Candelabro central de cristal de 3 niveles y techo artesonado con vigas de nogal.

Convención de coordenadas:
  Godot (gx, gy, gz) -> Blender (gx, -gz, gy)
  Tamaño Godot (sx, sy, sz) -> Blender (sx, sz, sy)
"""

import math
import os
import sys
import bpy

LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "lib"))
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

from mesh_utils import (
    clear_scene,
    get_or_create_material,
    get_or_create_textured_material,
    apply_box_uv_projection,
    create_empty,
    add_box,
    add_cylinder,
    join_objects,
)


def g2b(gx: float, gy: float, gz: float) -> tuple[float, float, float]:
    """Convierte coordenadas de mundo Godot (Y-up) a Blender (Z-up, export_yup=True)."""
    return (gx, -gz, gy)


def s2b(sx: float, sy: float, sz: float) -> tuple[float, float, float]:
    """Convierte dimensiones (ancho X, alto Y, fondo Z) de Godot a Blender."""
    return (sx, sz, sy)


# ------------------------------------------------------------------------------
# GENERADORES DE TEXTURAS PBR PROCEDURALES EMPAQUETADAS EN EL .GLB
# ------------------------------------------------------------------------------
def _gen_marble_pixels(base_col: tuple, vein_col: tuple, sz: int = 128) -> list[float]:
    pixels = [0.0] * (sz * sz * 4)
    idx = 0
    for y in range(sz):
        fy = y / float(sz)
        tile_y = 1.0 if (y % 64) > 1 else 0.72
        for x in range(sz):
            fx = x / float(sz)
            wave = math.sin((fx * 6.28318 + fy * 3.14159) * 2.0 + math.sin(fx * 12.5663) * 0.7)
            vein = pow(max(0.0, min(1.0, 1.0 - abs(wave))), 6.0) * 0.55
            tile_x = 1.0 if (x % 64) > 1 else 0.72
            tile = min(tile_x, tile_y)
            pixels[idx] = (base_col[0] + (vein_col[0] - base_col[0]) * vein) * tile
            pixels[idx + 1] = (base_col[1] + (vein_col[1] - base_col[1]) * vein) * tile
            pixels[idx + 2] = (base_col[2] + (vein_col[2] - base_col[2]) * vein) * tile
            pixels[idx + 3] = 1.0
            idx += 4
    return pixels


def _gen_carpet_pixels(base_col: tuple, pat_col: tuple, sz: int = 64) -> list[float]:
    pixels = [0.0] * (sz * sz * 4)
    idx = 0
    for y in range(sz):
        dy = abs((y % 16) - 7.5)
        for x in range(sz):
            dx = abs((x % 16) - 7.5)
            diamond = dx + dy
            is_pat = (5.8 < diamond < 7.4) or (dx < 1.2 and dy < 1.2)
            grain = ((x * 13 + y * 29) % 7) * 0.012
            c = pat_col if is_pat else base_col
            pixels[idx] = min(1.0, c[0] + grain)
            pixels[idx + 1] = min(1.0, c[1] + grain * 0.5)
            pixels[idx + 2] = min(1.0, c[2] + grain * 0.5)
            pixels[idx + 3] = 1.0
            idx += 4
    return pixels


def _gen_wallpaper_pixels(col_a: tuple, col_b: tuple, sz: int = 64) -> list[float]:
    pixels = [0.0] * (sz * sz * 4)
    idx = 0
    for y in range(sz):
        for x in range(sz):
            stripe = 0.5 + 0.5 * math.sin((x / 8.0) * math.tau)
            t = stripe * 0.45
            weave = 0.97 if ((x + y) % 4 == 0) else 1.0
            pixels[idx] = (col_a[0] + (col_b[0] - col_a[0]) * t) * weave
            pixels[idx + 1] = (col_a[1] + (col_b[1] - col_a[1]) * t) * weave
            pixels[idx + 2] = (col_a[2] + (col_b[2] - col_a[2]) * t) * weave
            pixels[idx + 3] = 1.0
            idx += 4
    return pixels


def _gen_wood_pixels(base_col: tuple, sz: int = 64) -> list[float]:
    pixels = [0.0] * (sz * sz * 4)
    idx = 0
    for y in range(sz):
        for x in range(sz):
            streak = 0.5 + 0.5 * math.sin(y * 0.45 + math.sin(x * 0.18) * 2.2)
            shade = 1.0 - 0.24 * (streak * 0.6)
            pixels[idx] = base_col[0] * shade
            pixels[idx + 1] = base_col[1] * shade
            pixels[idx + 2] = base_col[2] * shade
            pixels[idx + 3] = 1.0
            idx += 4
    return pixels


def _init_hotel_materials() -> dict:
    mats = {}
    mats["marble_light"] = get_or_create_textured_material(
        "Hotel_Marble_Light",
        "tex_hotel_marble_light",
        _gen_marble_pixels((0.86, 0.84, 0.80), (0.58, 0.56, 0.54), 128),
        128,
        128,
        metallic=0.06,
        roughness=0.20,
    )
    mats["marble_dark"] = get_or_create_textured_material(
        "Hotel_Marble_Dark",
        "tex_hotel_marble_dark",
        _gen_marble_pixels((0.14, 0.15, 0.17), (0.45, 0.42, 0.36), 128),
        128,
        128,
        metallic=0.12,
        roughness=0.18,
    )
    mats["carpet_royal"] = get_or_create_textured_material(
        "Hotel_Carpet_Royal",
        "tex_hotel_carpet_royal",
        _gen_carpet_pixels((0.36, 0.08, 0.10), (0.68, 0.52, 0.22), 64),
        64,
        64,
        metallic=0.0,
        roughness=0.88,
    )
    mats["carpet_room"] = get_or_create_textured_material(
        "Hotel_Carpet_Room",
        "tex_hotel_carpet_room",
        _gen_carpet_pixels((0.18, 0.21, 0.28), (0.34, 0.38, 0.48), 64),
        64,
        64,
        metallic=0.0,
        roughness=0.88,
    )
    mats["wall_upper"] = get_or_create_textured_material(
        "Hotel_Wall_Upper",
        "tex_hotel_wallpaper",
        _gen_wallpaper_pixels((0.84, 0.79, 0.70), (0.76, 0.70, 0.60), 64),
        64,
        64,
        metallic=0.0,
        roughness=0.74,
    )
    mats["wood_walnut"] = get_or_create_textured_material(
        "Hotel_Wood_Walnut",
        "tex_hotel_wood_walnut",
        _gen_wood_pixels((0.24, 0.12, 0.06), 64),
        64,
        64,
        metallic=0.02,
        roughness=0.44,
    )
    mats["wood_mahogany"] = get_or_create_textured_material(
        "Hotel_Wood_Mahogany",
        "tex_hotel_wood_mahogany",
        _gen_wood_pixels((0.17, 0.075, 0.04), 64),
        64,
        64,
        metallic=0.04,
        roughness=0.40,
    )

    mats["wall_accent"] = get_or_create_material("Hotel_Wall_Accent", (0.20, 0.23, 0.28), metallic=0.06, roughness=0.65)
    mats["ceiling"] = get_or_create_material("Hotel_Ceiling_Plaster", (0.92, 0.89, 0.84), metallic=0.0, roughness=0.82)
    mats["brass"] = get_or_create_material("Hotel_Brass_Polished", (0.84, 0.66, 0.24), metallic=0.90, roughness=0.22)
    mats["chrome"] = get_or_create_material("Hotel_Chrome_Locker", (0.76, 0.79, 0.84), metallic=0.92, roughness=0.18)
    mats["leather"] = get_or_create_material("Hotel_Leather_Brown", (0.24, 0.12, 0.08), metallic=0.04, roughness=0.45)
    mats["curtain"] = get_or_create_material("Hotel_Velvet_Curtain", (0.52, 0.14, 0.16), metallic=0.0, roughness=0.85)
    mats["night_window"] = get_or_create_material(
        "Hotel_Night_Window",
        (0.08, 0.14, 0.26),
        metallic=0.10,
        roughness=0.15,
        emission_color=(0.16, 0.28, 0.52),
        emission_strength=0.85,
    )
    mats["warm_emissive"] = get_or_create_material(
        "Hotel_Warm_Emissive",
        (1.0, 0.90, 0.68),
        metallic=0.0,
        roughness=0.20,
        emission_color=(1.0, 0.85, 0.55),
        emission_strength=2.4,
    )
    mats["screen_cyan"] = get_or_create_material(
        "Hotel_Screen_Cyan",
        (0.12, 0.35, 0.52),
        metallic=0.10,
        roughness=0.15,
        emission_color=(0.22, 0.68, 0.95),
        emission_strength=1.35,
    )

    glass_mat = get_or_create_material("Hotel_Entrance_Glass", (0.55, 0.72, 0.84), metallic=0.20, roughness=0.08)
    bsdf = glass_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = 0.32
    mats["glass"] = glass_mat
    return mats


# ------------------------------------------------------------------------------
# UTILIDADES ARQUITECTÓNICAS EN ESPACIO GODOT -> BLENDER
# ------------------------------------------------------------------------------
def _gbox(
    bucket: list,
    name: str,
    gsize: tuple[float, float, float],
    gpos: tuple[float, float, float],
    material,
    grot_deg: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.0,
):
    """Crea una caja usando coordenadas y tamaño en sistema Godot dentro de Blender."""
    # Mapeo de rotación Godot Euler(rx, ry, rz) -> Blender Euler(rx, -rz, ry)
    brot = (grot_deg[0], -grot_deg[2], grot_deg[1])
    obj = add_box(
        name,
        size=s2b(*gsize),
        location=g2b(*gpos),
        rotation_deg=brot,
        material=material,
        bevel=bevel,
    )
    bucket.append(obj)
    return obj


def _gcyl(
    bucket: list,
    name: str,
    radius: float,
    height: float,
    gpos: tuple[float, float, float],
    material,
    vertices: int = 18,
    bevel: float = 0.0,
):
    """Crea un cilindro vertical en espacio Godot (eje +Y Godot = eje +Z Blender)."""
    obj = add_cylinder(
        name,
        radius=radius,
        depth=height,
        vertices=vertices,
        location=g2b(*gpos),
        rotation_deg=(0.0, 0.0, 0.0),
        material=material,
        bevel=bevel,
    )
    bucket.append(obj)
    return obj


def _add_wainscot_wall(
    col_bucket: list,
    trim_bucket: list,
    mats: dict,
    wall_name: str,
    width: float,
    height: float,
    thickness: float,
    gcenter: tuple[float, float, float],
    rot_y_deg: float = 0.0,
):
    cx, cy, cz = gcenter
    _gbox(
        col_bucket,
        wall_name,
        (width, height, thickness),
        (cx, cy + height * 0.5, cz),
        mats["wall_upper"],
        grot_deg=(0.0, rot_y_deg, 0.0),
        bevel=0.0,
    )

    rad = math.radians(rot_y_deg)
    # Godot Vector3.FORWARD = (0, 0, -1) rotado por rot_y_deg alrededor de Y -> (-sin(rad), 0, -cos(rad))
    nx, nz = -math.sin(rad), -math.cos(rad)
    offset = thickness * 0.5 + 0.015

    for sign in (-1.0, 1.0):
        ox = nx * offset * sign
        oz = nz * offset * sign
        _gbox(
            trim_bucket,
            f"{wall_name}_Wain_{int(sign)}",
            (width, 1.06, 0.03),
            (cx + ox, cy + 0.53, cz + oz),
            mats["wood_walnut"],
            grot_deg=(0.0, rot_y_deg, 0.0),
            bevel=0.004,
        )
        _gbox(
            trim_bucket,
            f"{wall_name}_Dado_{int(sign)}",
            (width, 0.07, 0.05),
            (cx + ox, cy + 1.09, cz + oz),
            mats["wood_mahogany"],
            grot_deg=(0.0, rot_y_deg, 0.0),
            bevel=0.005,
        )
        _gbox(
            trim_bucket,
            f"{wall_name}_Crown_{int(sign)}",
            (width, 0.12, 0.06),
            (cx + ox, cy + height - 0.06, cz + oz),
            mats["wood_walnut"],
            grot_deg=(0.0, rot_y_deg, 0.0),
            bevel=0.005,
        )


def _add_wall_with_doorway(
    col_bucket: list,
    trim_bucket: list,
    mats: dict,
    wall_name: str,
    width: float,
    height: float,
    thickness: float,
    gcenter: tuple[float, float, float],
    door_local_x: float = 0.0,
):
    door_w = 1.04
    door_h = 2.24
    left_edge = -width * 0.5
    right_edge = width * 0.5
    door_left = door_local_x - door_w * 0.5
    door_right = door_local_x + door_w * 0.5
    cx, cy, cz = gcenter

    left_seg_w = door_left - left_edge
    if left_seg_w > 0.05:
        _add_wainscot_wall(
            col_bucket,
            trim_bucket,
            mats,
            f"{wall_name}_L",
            left_seg_w,
            height,
            thickness,
            (cx + (left_edge + door_left) * 0.5, cy, cz),
        )

    right_seg_w = right_edge - door_right
    if right_seg_w > 0.05:
        _add_wainscot_wall(
            col_bucket,
            trim_bucket,
            mats,
            f"{wall_name}_R",
            right_seg_w,
            height,
            thickness,
            (cx + (door_right + right_edge) * 0.5, cy, cz),
        )

    lintel_h = height - door_h
    if lintel_h > 0.05:
        _gbox(
            col_bucket,
            f"{wall_name}_Top",
            (door_w, lintel_h, thickness),
            (cx + door_local_x, cy + door_h + lintel_h * 0.5, cz),
            mats["wall_upper"],
            bevel=0.0,
        )


def _add_balustrade(
    col_bucket: list,
    trim_bucket: list,
    mats: dict,
    b_name: str,
    length: float,
    gpos: tuple[float, float, float],
    along_z: bool = False,
):
    rot_y = 90.0 if along_z else 0.0
    px, py, pz = gpos
    _gbox(
        col_bucket,
        f"{b_name}_Col",
        (length, 1.02, 0.18),
        (px, py + 0.51, pz),
        mats["wood_walnut"],
        grot_deg=(0.0, rot_y, 0.0),
        bevel=0.006,
    )
    _gbox(
        trim_bucket,
        f"{b_name}_TopBrass",
        (length + 0.06, 0.07, 0.24),
        (px, py + 1.02, pz),
        mats["brass"],
        grot_deg=(0.0, rot_y, 0.0),
        bevel=0.008,
    )

    count = max(2, int(length / 2.2))
    for i in range(count + 1):
        t = -0.5 + i / float(count)
        ox, oz = (0.0, t * length) if along_z else (t * length, 0.0)
        _gbox(
            trim_bucket,
            f"{b_name}_Post_{i}",
            (0.16, 1.08, 0.16),
            (px + ox, py + 0.54, pz + oz),
            mats["wood_mahogany"],
            bevel=0.01,
        )


def _add_elevator_pair(
    solid_bucket: list,
    decor_bucket: list,
    mats: dict,
    e_name: str,
    gpos: tuple[float, float, float],
):
    bx, by, bz = gpos
    for idx in range(2):
        zc = bz + (idx * 2.4 - 1.2)
        _gbox(
            solid_bucket,
            f"{e_name}_Frame_{idx}",
            (0.14, 2.55, 1.75),
            (bx, by + 1.275, zc),
            mats["marble_dark"],
            bevel=0.008,
        )
        _gbox(
            decor_bucket,
            f"{e_name}_DoorL_{idx}",
            (0.06, 2.35, 0.72),
            (bx - 0.05, by + 1.175, zc - 0.37),
            mats["brass"],
            bevel=0.006,
        )
        _gbox(
            decor_bucket,
            f"{e_name}_DoorR_{idx}",
            (0.06, 2.35, 0.72),
            (bx - 0.05, by + 1.175, zc + 0.37),
            mats["brass"],
            bevel=0.006,
        )
        _gbox(
            decor_bucket,
            f"{e_name}_Ind_{idx}",
            (0.05, 0.16, 0.42),
            (bx - 0.06, by + 2.66, zc),
            mats["warm_emissive"],
            bevel=0.004,
        )


def _add_painting(
    decor_bucket: list,
    mats: dict,
    p_name: str,
    gpos: tuple[float, float, float],
    rot_y_deg: float,
    w: float,
    h: float,
    art_color: tuple[float, float, float],
):
    art_mat = get_or_create_material(f"Hotel_Art_{p_name}", art_color, metallic=0.05, roughness=0.55)
    px, py, pz = gpos
    _gbox(
        decor_bucket,
        f"{p_name}_Frame",
        (w + 0.12, h + 0.12, 0.04),
        (px, py, pz),
        mats["brass"],
        grot_deg=(0.0, rot_y_deg, 0.0),
        bevel=0.008,
    )
    rad = math.radians(rot_y_deg)
    # Vector3.BACK (0,0,+1) rotado por rot_y_deg -> (sin(rad), 0, cos(rad))
    fx, fz = math.sin(rad) * 0.015, math.cos(rad) * 0.015
    _gbox(
        decor_bucket,
        f"{p_name}_Canvas",
        (w, h, 0.025),
        (px + fx, py, pz + fz),
        art_mat,
        grot_deg=(0.0, rot_y_deg, 0.0),
        bevel=0.002,
    )


def _add_wall_sconce(
    decor_bucket: list,
    mats: dict,
    s_name: str,
    gpos: tuple[float, float, float],
    rot_y_deg: float,
):
    px, py, pz = gpos
    _gbox(
        decor_bucket,
        f"{s_name}_Base",
        (0.14, 0.22, 0.04),
        (px, py, pz),
        mats["brass"],
        grot_deg=(0.0, rot_y_deg, 0.0),
        bevel=0.005,
    )
    rad = math.radians(rot_y_deg)
    fx, fz = math.sin(rad) * 0.11, math.cos(rad) * 0.11
    _gbox(
        decor_bucket,
        f"{s_name}_Shade",
        (0.16, 0.20, 0.12),
        (px + fx, py + 0.05, pz + fz),
        mats["warm_emissive"],
        grot_deg=(0.0, rot_y_deg, 0.0),
        bevel=0.008,
    )


def _add_hotel_room_furniture(
    solid_bucket: list,
    decor_bucket: list,
    mats: dict,
    room_id: str,
    cx: float,
    fy: float,
):
    _gbox(solid_bucket, f"{room_id}_NightstandL", (0.52, 0.56, 0.48), (cx - 1.35, fy + 0.28, -14.8), mats["wood_walnut"], bevel=0.008)
    _gbox(solid_bucket, f"{room_id}_NightstandR", (0.52, 0.56, 0.48), (cx + 1.35, fy + 0.28, -14.8), mats["wood_walnut"], bevel=0.008)
    _gcyl(decor_bucket, f"{room_id}_LampL", 0.13, 0.24, (cx - 1.35, fy + 0.72, -14.8), mats["warm_emissive"], vertices=16, bevel=0.004)
    _gcyl(decor_bucket, f"{room_id}_LampR", 0.13, 0.24, (cx + 1.35, fy + 0.72, -14.8), mats["warm_emissive"], vertices=16, bevel=0.004)

    _gbox(solid_bucket, f"{room_id}_Wardrobe", (1.45, 2.15, 0.68), (cx + 2.8, fy + 1.075, -14.9), mats["wood_mahogany"], bevel=0.01)
    _gbox(decor_bucket, f"{room_id}_TV", (1.55, 0.88, 0.08), (cx, fy + 1.65, -6.02), mats["marble_dark"], bevel=0.008)
    _add_painting(decor_bucket, mats, f"{room_id}_BedArt", (cx, fy + 2.1, -15.72), 0.0, 1.8, 0.95, (0.28, 0.36, 0.48))


def _finalize_group(objects: list, target_name: str, parent, uv_scale: float = 0.48):
    if not objects:
        return None
    joined = join_objects(objects, target_name, parent=parent)
    if joined is not None:
        bpy.context.view_layer.update()
        apply_box_uv_projection(joined, uv_scale=uv_scale)
    return joined


def build_hotel_building():
    """Construye el Gran Hotel Corona completo en Blender y devuelve HotelBuilding_Root."""
    clear_scene()
    mats = _init_hotel_materials()
    root = create_empty("HotelBuilding_Root")

    floor1_col = []
    floor2_col = []
    stair_col = []
    balustrade_col = []
    walls_col = []
    glass_col = []
    furniture_col = []

    carpets_vis = []
    trim_vis = []
    decor_vis = []

    # --------------------------------------------------------------------------
    # 1. PLANTA BAJA (Y = 0.0)
    # --------------------------------------------------------------------------
    _gbox(floor1_col, "Floor1_Slab", (36.0, 0.4, 32.0), (0.0, -0.2, 0.0), mats["marble_light"], bevel=0.0)

    _gbox(carpets_vis, "Lobby_Inlay_N", (16.0, 0.014, 0.55), (0.0, 0.007, 4.4), mats["marble_dark"], bevel=0.003)
    _gbox(carpets_vis, "Lobby_Inlay_S", (16.0, 0.014, 0.55), (0.0, 0.007, 14.4), mats["marble_dark"], bevel=0.003)
    _gbox(carpets_vis, "Lobby_Inlay_W", (0.55, 0.014, 10.5), (-8.0, 0.007, 9.4), mats["marble_dark"], bevel=0.003)
    _gbox(carpets_vis, "Lobby_Inlay_E", (0.55, 0.014, 10.5), (8.0, 0.007, 9.4), mats["marble_dark"], bevel=0.003)
    _gbox(carpets_vis, "Lobby_Brass_Center", (6.2, 0.016, 6.2), (0.0, 0.008, 9.4), mats["brass"], grot_deg=(0.0, 45.0, 0.0), bevel=0.004)

    _gbox(carpets_vis, "Lobby_Runner", (4.2, 0.022, 11.2), (0.0, 0.011, 9.6), mats["carpet_royal"], bevel=0.004)
    _gbox(carpets_vis, "F1_Corridor_Runner", (34.6, 0.022, 2.2), (0.0, 0.011, -4.3), mats["carpet_royal"], bevel=0.004)

    _gbox(carpets_vis, "F1_Carpet_101", (10.8, 0.02, 9.0), (-12.0, 0.01, -10.9), mats["carpet_room"], bevel=0.003)
    _gbox(carpets_vis, "F1_Carpet_102", (10.8, 0.02, 9.0), (0.0, 0.01, -10.9), mats["carpet_room"], bevel=0.003)
    _gbox(carpets_vis, "F1_Carpet_103", (10.8, 0.02, 9.0), (12.0, 0.01, -10.9), mats["carpet_royal"], bevel=0.003)

    _add_wall_with_doorway(walls_col, trim_vis, mats, "F1_Wall_101", 12.0, 4.0, 0.26, (-12.0, 0.0, -5.8), 0.0)
    _add_wall_with_doorway(walls_col, trim_vis, mats, "F1_Wall_102", 12.0, 4.0, 0.26, (0.0, 0.0, -5.8), 0.0)
    _add_wall_with_doorway(walls_col, trim_vis, mats, "F1_Wall_103", 12.0, 4.0, 0.26, (12.0, 0.0, -5.8), 0.0)

    _add_wainscot_wall(walls_col, trim_vis, mats, "F1_Div_101_102", 10.2, 4.0, 0.26, (-6.0, 0.0, -10.9), 90.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "F1_Div_102_103", 10.2, 4.0, 0.26, (6.0, 0.0, -10.9), 90.0)

    # --------------------------------------------------------------------------
    # 2. SEGUNDO PISO / MEZANINE (Y = 4.0)
    # --------------------------------------------------------------------------
    _gbox(floor2_col, "Floor2_Back", (36.0, 0.35, 13.2), (0.0, 3.825, -9.4), mats["carpet_royal"], bevel=0.0)
    _gbox(floor2_col, "Floor2_Mezz_L", (15.6, 0.35, 6.0), (-10.2, 3.825, 0.2), mats["marble_light"], bevel=0.0)
    _gbox(floor2_col, "Floor2_Mezz_R", (15.6, 0.35, 6.0), (10.2, 3.825, 0.2), mats["marble_light"], bevel=0.0)

    _gbox(carpets_vis, "F2_Corridor_Runner", (34.6, 0.02, 2.2), (0.0, 4.01, -4.3), mats["carpet_royal"], bevel=0.004)
    for i in range(4):
        rx = -13.5 + i * 9.0
        _gbox(carpets_vis, f"F2_RoomCarpet_{i}", (7.8, 0.02, 9.0), (rx, 4.01, -10.9), mats["carpet_room"], bevel=0.003)

    _add_balustrade(balustrade_col, trim_vis, mats, "Rail_Front_L", 15.6, (-10.2, 4.0, 3.12), along_z=False)
    _add_balustrade(balustrade_col, trim_vis, mats, "Rail_Front_R", 15.6, (10.2, 4.0, 3.12), along_z=False)
    _add_balustrade(balustrade_col, trim_vis, mats, "Rail_StairGap_L", 6.0, (-2.45, 4.0, 0.2), along_z=True)
    _add_balustrade(balustrade_col, trim_vis, mats, "Rail_StairGap_R", 6.0, (2.45, 4.0, 0.2), along_z=True)

    _add_wall_with_doorway(walls_col, trim_vis, mats, "F2_Wall_201", 9.0, 4.8, 0.26, (-13.5, 4.0, -5.8), 0.0)
    _add_wall_with_doorway(walls_col, trim_vis, mats, "F2_Wall_202", 9.0, 4.8, 0.26, (-4.5, 4.0, -5.8), 0.0)
    _add_wall_with_doorway(walls_col, trim_vis, mats, "F2_Wall_203", 9.0, 4.8, 0.26, (4.5, 4.0, -5.8), 0.0)
    _add_wall_with_doorway(walls_col, trim_vis, mats, "F2_Wall_204", 9.0, 4.8, 0.26, (13.5, 4.0, -5.8), 0.0)

    _add_wainscot_wall(walls_col, trim_vis, mats, "F2_Div_201_202", 10.2, 4.8, 0.26, (-9.0, 4.0, -10.9), 90.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "F2_Div_202_203", 10.2, 4.8, 0.26, (0.0, 4.0, -10.9), 90.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "F2_Div_203_204", 10.2, 4.8, 0.26, (9.0, 4.0, -10.9), 90.0)

    # --------------------------------------------------------------------------
    # 3. ESCALERA IMPERIAL CENTRAL
    # --------------------------------------------------------------------------
    length_z = 7.0
    height_y = 4.0
    diag = math.sqrt(length_z * length_z + height_y * height_y)
    angle_rad = math.atan2(height_y, length_z)
    angle_deg = math.degrees(angle_rad)
    center_y = 2.0 - 0.175 * math.cos(angle_rad)

    _gbox(
        stair_col,
        "GrandStair_Ramp",
        (4.6, 0.35, diag),
        (0.0, center_y, 0.7),
        mats["carpet_royal"],
        grot_deg=(angle_deg, 0.0, 0.0),
        bevel=0.0,
    )

    step_count = 16
    for i in range(step_count):
        frac = (i + 0.5) / float(step_count)
        sz = 4.0 + (-2.6 - 4.0) * frac
        sy = 0.12 + (3.88 - 0.12) * frac
        _gbox(trim_vis, f"StairNose_{i}", (4.5, 0.06, 0.14), (0.0, sy, sz), mats["brass"], bevel=0.005)

    _gbox(stair_col, "Stair_Wall_L", (0.24, 4.0, 7.1), (-2.42, 2.0, 0.7), mats["wood_walnut"], bevel=0.008)
    _gbox(stair_col, "Stair_Wall_R", (0.24, 4.0, 7.1), (2.42, 2.0, 0.7), mats["wood_walnut"], bevel=0.008)
    _gbox(trim_vis, "Stair_Handrail_L", (0.10, 0.10, diag), (-2.30, center_y + 0.98, 0.7), mats["brass"], grot_deg=(angle_deg, 0.0, 0.0), bevel=0.008)
    _gbox(trim_vis, "Stair_Handrail_R", (0.10, 0.10, diag), (2.30, center_y + 0.98, 0.7), mats["brass"], grot_deg=(angle_deg, 0.0, 0.0), bevel=0.008)

    # --------------------------------------------------------------------------
    # 4. DECORACIÓN DE GRAN HOTEL (CANDELABRO, ENTRADA, RECEPCIÓN, BAR, ASCENSORES, ARTE)
    # --------------------------------------------------------------------------
    _gcyl(decor_vis, "Chandelier_Rod", 0.05, 2.1, (0.0, 7.9, 8.4), mats["brass"], vertices=16)
    for tier_idx in range(3):
        ty = 6.7 + tier_idx * 0.42
        tr = 1.45 - tier_idx * 0.36
        _gcyl(decor_vis, f"Chandelier_Ring_{tier_idx}", tr, 0.09, (0.0, ty, 8.4), mats["brass"], vertices=24, bevel=0.004)
        bulbs = 8 - tier_idx * 2
        for b in range(bulbs):
            ang = b * (math.tau / float(bulbs))
            bx = math.cos(ang) * tr
            bz = 8.4 + math.sin(ang) * tr
            _gbox(decor_vis, f"Chand_Crystal_{tier_idx}_{b}", (0.10, 0.24, 0.10), (bx, ty - 0.14, bz), mats["warm_emissive"], bevel=0.008)

    # Entrada Principal Acristalada al Sur (Z = +15.8)
    _gbox(furniture_col, "Ent_DoorFrame_L", (0.18, 3.8, 0.35), (-2.6, 1.9, 15.8), mats["brass"], bevel=0.008)
    _gbox(furniture_col, "Ent_DoorFrame_R", (0.18, 3.8, 0.35), (2.6, 1.9, 15.8), mats["brass"], bevel=0.008)
    _gbox(glass_col, "Ent_Glass_L", (2.4, 3.6, 0.08), (-1.3, 1.8, 15.8), mats["glass"], bevel=0.0)
    _gbox(glass_col, "Ent_Glass_R", (2.4, 3.6, 0.08), (1.3, 1.8, 15.8), mats["glass"], bevel=0.0)
    _gbox(decor_vis, "Ent_Handle_L", (0.06, 0.85, 0.14), (-0.35, 1.25, 15.65), mats["brass"], bevel=0.008)
    _gbox(decor_vis, "Ent_Handle_R", (0.06, 0.85, 0.14), (0.35, 1.25, 15.65), mats["brass"], bevel=0.008)

    # Ventanales nocturnos con cortinas en el muro Sur
    for wx in (-12.5, -7.2, 7.2, 12.5):
        _gbox(decor_vis, f"LobbyWin_{int(wx)}", (3.2, 4.4, 0.08), (wx, 3.0, 15.72), mats["night_window"], bevel=0.004)
        _gbox(trim_vis, f"LobbyWinFrame_{int(wx)}", (3.4, 0.14, 0.14), (wx, 5.25, 15.70), mats["brass"], bevel=0.008)
        _gbox(trim_vis, f"CurtainL_{int(wx)}", (0.48, 4.6, 0.18), (wx - 1.5, 3.0, 15.62), mats["curtain"], bevel=0.01)
        _gbox(trim_vis, f"CurtainR_{int(wx)}", (0.48, 4.6, 0.18), (wx + 1.5, 3.0, 15.62), mats["curtain"], bevel=0.01)

    # Zona de Recepción (Ala Este)
    _gbox(furniture_col, "Rec_WallPanel", (0.18, 3.6, 7.4), (17.7, 1.8, 8.8), mats["wood_mahogany"], bevel=0.01)
    _gbox(decor_vis, "Rec_SignBar", (0.08, 0.34, 2.8), (17.56, 2.95, 8.8), mats["warm_emissive"], bevel=0.006)
    for row in range(3):
        for col in range(6):
            _gbox(
                decor_vis,
                f"KeyCubby_{row}_{col}",
                (0.12, 0.24, 0.32),
                (17.56, 1.55 + row * 0.34, 7.6 + col * 0.48),
                mats["brass"],
                bevel=0.005,
            )

    _gbox(furniture_col, "Rec_ExtraCounter", (0.85, 1.02, 4.6), (13.5, 0.51, 9.2), mats["wood_walnut"], bevel=0.01)
    _gbox(furniture_col, "Rec_CounterMarble", (0.96, 0.08, 4.7), (13.5, 1.05, 9.2), mats["marble_light"], bevel=0.008)
    for mz in (7.8, 10.2):
        _gbox(decor_vis, f"Rec_Monitor_{int(mz * 10)}", (0.06, 0.34, 0.54), (13.6, 1.28, mz), mats["screen_cyan"], grot_deg=(0.0, 12.0, 0.0), bevel=0.004)

    _gbox(furniture_col, "LuggageCart_Base", (0.95, 0.14, 1.35), (10.8, 0.14, 13.0), mats["brass"], bevel=0.008)
    _gbox(decor_vis, "LuggageCart_Arch", (0.06, 1.55, 0.06), (10.8, 0.92, 12.4), mats["brass"], bevel=0.005)
    _gbox(decor_vis, "LuggageCart_Arch2", (0.06, 1.55, 0.06), (10.8, 0.92, 13.6), mats["brass"], bevel=0.005)
    _gbox(decor_vis, "LuggageCart_Top", (0.06, 0.06, 1.24), (10.8, 1.70, 13.0), mats["brass"], bevel=0.005)
    _gbox(furniture_col, "Suitcase_1", (0.56, 0.42, 0.72), (10.8, 0.42, 12.9), mats["leather"], bevel=0.012)
    _gbox(furniture_col, "Suitcase_2", (0.44, 0.30, 0.54), (10.8, 0.78, 13.0), mats["wall_accent"], bevel=0.012)

    # Zona Lounge & Café Bar (Ala Oeste)
    _gbox(furniture_col, "Bar_Counter", (1.1, 1.05, 6.2), (-14.6, 0.525, 8.6), mats["wood_mahogany"], bevel=0.01)
    _gbox(furniture_col, "Bar_Top", (1.22, 0.08, 6.35), (-14.6, 1.08, 8.6), mats["marble_dark"], bevel=0.008)
    _gbox(furniture_col, "Bar_BackShelf", (0.38, 2.6, 5.8), (-17.55, 1.65, 8.6), mats["wood_walnut"], bevel=0.01)
    _gbox(decor_vis, "Bar_BackGlow", (0.04, 1.8, 5.4), (-17.36, 1.85, 8.6), mats["warm_emissive"], bevel=0.004)
    for bz in (6.4, 8.0, 9.6, 11.2):
        _gcyl(decor_vis, f"Barstool_Leg_{int(bz * 10)}", 0.05, 0.72, (-13.5, 0.36, bz), mats["brass"], vertices=14)
        _gcyl(decor_vis, f"Barstool_Seat_{int(bz * 10)}", 0.22, 0.10, (-13.5, 0.74, bz), mats["leather"], vertices=18, bevel=0.008)

    for tbl in ((-10.4, 0.0, 11.8), (-10.4, 0.0, 5.8), (9.4, 0.0, 11.0)):
        tx, ty, tz = tbl
        _gbox(furniture_col, f"CoffeeTable_{int(tx)}_{int(tz)}", (1.25, 0.44, 0.85), (tx, ty + 0.22, tz), mats["wood_walnut"], bevel=0.008)
        _gbox(decor_vis, f"TableTop_{int(tx)}_{int(tz)}", (1.32, 0.05, 0.90), (tx, ty + 0.46, tz), mats["marble_light"], bevel=0.006)
        _gcyl(decor_vis, f"LampShade_{int(tx)}_{int(tz)}", 0.14, 0.22, (tx, ty + 0.72, tz), mats["warm_emissive"], vertices=16)

    # Ascensores en Planta Baja y Piso 2
    _add_elevator_pair(furniture_col, decor_vis, mats, "Elev_F1", (17.68, 0.0, -0.4))
    _add_elevator_pair(furniture_col, decor_vis, mats, "Elev_F2", (17.68, 4.0, -0.4))

    # Cuadros enmarcados y apliques cálidos
    _add_painting(decor_vis, mats, "Art_Lobby_W", (-17.70, 2.35, 13.0), 90.0, 1.8, 1.15, (0.18, 0.34, 0.48))
    _add_painting(decor_vis, mats, "Art_Lobby_E", (17.70, 2.35, 13.5), -90.0, 1.8, 1.15, (0.55, 0.28, 0.16))
    _add_painting(decor_vis, mats, "Art_Mezz_W", (-17.70, 6.2, 0.4), 90.0, 2.2, 1.25, (0.24, 0.42, 0.30))
    _add_painting(decor_vis, mats, "Art_Mezz_E", (17.70, 6.2, -4.2), -90.0, 1.8, 1.1, (0.48, 0.36, 0.18))
    _add_painting(decor_vis, mats, "Art_F2_Hall1", (-9.0, 6.2, -5.62), 0.0, 1.6, 1.0, (0.32, 0.22, 0.42))
    _add_painting(decor_vis, mats, "Art_F2_Hall2", (9.0, 6.2, -5.62), 0.0, 1.6, 1.0, (0.16, 0.38, 0.44))

    for sx in (-15.0, -6.5, 6.5, 15.0):
        _add_wall_sconce(decor_vis, mats, f"Sconce_F1_{int(sx)}", (sx, 2.25, -5.64), 0.0)
        _add_wall_sconce(decor_vis, mats, f"Sconce_F2_{int(sx)}", (sx, 6.25, -5.64), 0.0)

    # --------------------------------------------------------------------------
    # 5. INTERIORES DE HABITACIONES (101-103 y 201-204)
    # --------------------------------------------------------------------------
    # 101: Salón Ejecutivo / Conferencias
    _gbox(furniture_col, "Conf_Table", (4.6, 0.78, 1.8), (-12.0, 0.39, -11.2), mats["wood_mahogany"], bevel=0.01)
    _gbox(decor_vis, "Conf_TableTop", (4.75, 0.06, 1.92), (-12.0, 0.80, -11.2), mats["wood_walnut"], bevel=0.008)
    for cx in (-13.6, -12.0, -10.4):
        _gbox(furniture_col, f"Conf_ChairN_{int(cx * 10)}", (0.56, 0.92, 0.56), (cx, 0.46, -12.45), mats["leather"], bevel=0.012)
        _gbox(furniture_col, f"Conf_ChairS_{int(cx * 10)}", (0.56, 0.92, 0.56), (cx, 0.46, -9.95), mats["leather"], bevel=0.012)
    _gbox(decor_vis, "Conf_Screen", (3.2, 1.55, 0.08), (-12.0, 2.1, -15.72), mats["screen_cyan"], bevel=0.006)

    # 102: Sala de Seguridad y Control
    _gbox(decor_vis, "Sec_MonitorWall", (3.6, 1.4, 0.12), (0.0, 1.85, -14.8), mats["marble_dark"], bevel=0.008)
    for mx in (-1.1, 0.0, 1.1):
        _gbox(decor_vis, f"Sec_Screen_{int(mx * 10)}", (0.92, 0.65, 0.06), (mx, 1.88, -14.72), mats["screen_cyan"], bevel=0.004)
    _gbox(furniture_col, "Sec_Lockers", (2.4, 2.2, 0.72), (-4.2, 1.1, -14.9), mats["chrome"], bevel=0.008)
    _gbox(furniture_col, "Sec_ServerRack", (1.1, 2.2, 0.9), (4.6, 1.1, -14.8), mats["wall_accent"], bevel=0.008)

    # 103 y 201-204 Habitaciones
    _add_hotel_room_furniture(furniture_col, decor_vis, mats, "R103", 12.0, 0.0)
    _add_hotel_room_furniture(furniture_col, decor_vis, mats, "R201", -13.5, 4.0)
    _add_hotel_room_furniture(furniture_col, decor_vis, mats, "R202", -4.5, 4.0)
    _add_hotel_room_furniture(furniture_col, decor_vis, mats, "R203", 4.5, 4.0)
    _add_hotel_room_furniture(furniture_col, decor_vis, mats, "R204", 13.5, 4.0)

    _gbox(furniture_col, "Suite204_CoffeeTbl", (1.1, 0.42, 0.75), (11.4, 4.21, -9.2), mats["marble_dark"], bevel=0.008)
    _gbox(furniture_col, "Suite204_MiniBar", (1.6, 0.95, 0.55), (16.8, 4.475, -9.0), mats["wood_mahogany"], bevel=0.008)

    # --------------------------------------------------------------------------
    # 6. MUROS EXTERIORES Y TECHO ARTESONADO
    # --------------------------------------------------------------------------
    _add_wainscot_wall(walls_col, trim_vis, mats, "Ext_North", 36.0, 9.0, 0.4, (0.0, 0.0, -16.0), 0.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "Ext_West", 32.0, 9.0, 0.4, (-18.0, 0.0, 0.0), 90.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "Ext_East", 32.0, 9.0, 0.4, (18.0, 0.0, 0.0), 90.0)

    _add_wainscot_wall(walls_col, trim_vis, mats, "Ext_South_L", 15.4, 9.0, 0.4, (-10.3, 0.0, 16.0), 0.0)
    _add_wainscot_wall(walls_col, trim_vis, mats, "Ext_South_R", 15.4, 9.0, 0.4, (10.3, 0.0, 16.0), 0.0)
    _gbox(walls_col, "Ext_South_Top", (5.4, 5.2, 0.4), (0.0, 6.4, 16.0), mats["wall_upper"], bevel=0.0)

    _gbox(walls_col, "Hotel_Ceiling", (36.4, 0.4, 32.4), (0.0, 9.0, 0.0), mats["ceiling"], bevel=0.0)
    for bx in (-12.0, -4.0, 4.0, 12.0):
        _gbox(trim_vis, f"CeilingBeam_Z_{int(bx)}", (0.45, 0.34, 31.6), (bx, 8.68, 0.0), mats["wood_walnut"], bevel=0.008)
    for bz in (-10.0, -2.0, 6.0, 13.0):
        _gbox(trim_vis, f"CeilingBeam_X_{int(bz)}", (35.6, 0.34, 0.45), (0.0, 8.68, bz), mats["wood_walnut"], bevel=0.008)

    # --------------------------------------------------------------------------
    # 7. UNIR POR ZONAS Y APLICAR UV CÚBICAS (CON SUFIJO -col PARA COLISIONADORES GODOT)
    # --------------------------------------------------------------------------
    _finalize_group(floor1_col, "Hotel_Floor1-col", root, uv_scale=0.45)
    _finalize_group(floor2_col, "Hotel_Floor2-col", root, uv_scale=0.55)
    _finalize_group(stair_col, "Hotel_Staircase-col", root, uv_scale=0.65)
    _finalize_group(balustrade_col, "Hotel_Balustrades-col", root, uv_scale=0.60)
    _finalize_group(walls_col, "Hotel_Walls-col", root, uv_scale=0.55)
    _finalize_group(glass_col, "Hotel_GlassEntrance-col", root, uv_scale=0.50)
    _finalize_group(furniture_col, "Hotel_FixedFurniture-col", root, uv_scale=0.60)

    _finalize_group(carpets_vis, "Hotel_CarpetsAndInlays", root, uv_scale=0.70)
    _finalize_group(trim_vis, "Hotel_MoldingsAndTrim", root, uv_scale=0.60)
    _finalize_group(decor_vis, "Hotel_DecorAndArt", root, uv_scale=0.60)

    return root
