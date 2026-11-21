"""
mesh_utils.py
Utilidades compartidas de Blender (bpy) para construir modelos 3D estilizados/tácticos
y exportarlos en formato GLB listos para Godot 4.7.2.

Convención de ejes en Blender para exportar directo a Godot (export_yup=True):
  +X = Derecha
  +Y = Adelante (se convierte en -Z en Godot)
  +Z = Arriba   (se convierte en +Y en Godot)
"""

import math
import os
import bpy
import bmesh
from mathutils import Vector, Euler


def clear_scene():
    """Elimina todos los objetos, mallas, materiales y luces huérfanas de la escena."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block_collection in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.images,
    ):
        for item in list(block_collection):
            if item.users == 0:
                block_collection.remove(item)


def get_or_create_material(
    name: str,
    base_color: tuple,
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: tuple | None = None,
    emission_strength: float = 0.0,
):
    """Crea o reutiliza un material PBR Principled BSDF ligero para móviles y Godot."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base_color[:3], 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission_color is not None and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission_color[:3], 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def apply_material(obj, material):
    """Asigna un material a un objeto de malla."""
    if obj.type != 'MESH':
        return
    if len(obj.data.materials) == 0:
        obj.data.materials.append(material)
    else:
        obj.data.materials[0] = material


def add_bevel(obj, width: float = 0.002, segments: int = 2):
    """Agrega biselado suave para capturar reflejos en los bordes."""
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(30.0)
    return mod


def set_smooth_with_sharp_edges(obj, angle_deg: float = 38.0):
    """Suaviza caras curvas manteniendo aristas duras limpias mediante EdgeSplit."""
    if obj.type != 'MESH':
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
    mod.split_angle = math.radians(angle_deg)
    mod.use_edge_angle = True


def create_empty(name: str, location=(0.0, 0.0, 0.0), parent=None):
    """Crea un nodo Empty (marcador de punto o pivote para Godot)."""
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 0.03
    empty.location = Vector(location)
    bpy.context.collection.objects.link(empty)
    if parent is not None:
        empty.parent = parent
    return empty


def add_box(
    name: str,
    size=(0.1, 0.1, 0.1),
    location=(0.0, 0.0, 0.0),
    rotation_deg=(0.0, 0.0, 0.0),
    material=None,
    bevel: float = 0.002,
    parent=None,
):
    """Crea una caja dimensionada con bisel opcional."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rotation_deg), 'XYZ')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel > 0:
        add_bevel(obj, width=bevel, segments=2)
    set_smooth_with_sharp_edges(obj, 35.0)
    if material:
        apply_material(obj, material)
    if parent:
        obj.parent = parent
    return obj


def add_cylinder(
    name: str,
    radius: float = 0.02,
    depth: float = 0.1,
    vertices: int = 16,
    location=(0.0, 0.0, 0.0),
    rotation_deg=(0.0, 0.0, 0.0),
    material=None,
    bevel: float = 0.0,
    parent=None,
):
    """Crea un cilindro orientado y suavizado."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = Euler(tuple(math.radians(a) for a in rotation_deg), 'XYZ')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if bevel > 0:
        add_bevel(obj, width=bevel, segments=1)
    set_smooth_with_sharp_edges(obj, 42.0)
    if material:
        apply_material(obj, material)
    if parent:
        obj.parent = parent
    return obj


def add_extruded_profile(
    name: str,
    points_yz: list[tuple[float, float]],
    thickness_x: float,
    location=(0.0, 0.0, 0.0),
    material=None,
    bevel: float = 0.002,
    parent=None,
):
    """
    Construye una malla a partir de un perfil 2D (Y, Z) extruido simétricamente en X.
    Ideal para siluetas precisas de receptores, cargadores curvos y culatas.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    half_x = thickness_x * 0.5
    front_verts = [bm.verts.new((half_x, y, z)) for (y, z) in points_yz]
    back_verts = [bm.verts.new((-half_x, y, z)) for (y, z) in points_yz]

    bm.faces.new(front_verts)
    bm.faces.new(list(reversed(back_verts)))

    n = len(points_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([front_verts[i], front_verts[j], back_verts[j], back_verts[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj.location = Vector(location)
    if bevel > 0:
        add_bevel(obj, width=bevel, segments=2)
    set_smooth_with_sharp_edges(obj, 35.0)
    if material:
        apply_material(obj, material)
    if parent:
        obj.parent = parent
    return obj


def join_objects(objects: list, target_name: str, parent=None):
    """Une múltiples objetos de malla en uno solo aplicando sus modificadores."""
    valid = [o for o in objects if o is not None and o.type == 'MESH']
    if not valid:
        return None

    bpy.ops.object.select_all(action='DESELECT')
    for o in valid:
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for mod in list(o.modifiers):
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            except Exception:
                pass

    bpy.ops.object.select_all(action='DESELECT')
    for o in valid:
        o.select_set(True)
    bpy.context.view_layer.objects.active = valid[0]
    if len(valid) > 1:
        bpy.ops.object.join()

    result = bpy.context.active_object
    result.name = target_name
    if parent is not None:
        result.parent = parent
    return result


def export_hierarchy_glb(root_obj, output_path: str):
    """Selecciona el nodo raíz y todos sus hijos y los exporta como archivo .glb."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')

    def select_recursive(obj):
        obj.select_set(True)
        for child in obj.children:
            select_recursive(child)

    select_recursive(root_obj)
    bpy.context.view_layer.objects.active = root_obj

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT',
        export_normals=True,
    )
    print(f"[GLB Exported] {output_path}")
