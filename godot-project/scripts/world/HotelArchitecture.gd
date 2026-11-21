# HotelArchitecture.gd
# Construye la arquitectura sólida de los 2 pisos del Hotel (Planta Baja + Segundo Piso)
# con aberturas exactas para puertas animadas, escalera central transitable, barandal en mezanine,
# iluminación cálida de hotel y horneado del NavigationMesh para la IA terrorista.
#
# Distribución (en metros):
#   - Planta Baja (Y = 0.0):
#       * Vestíbulo principal amplio (X: -12 a +12, Z: -4 a +12)
#       * Pasillo trasero y 2 habitaciones con puertas animadas (101 y 102) en Z: -12 a -4
#       * Escalera central ancha desde Z = +2.5 (Y=0) hasta Z = -3.5 (Y=4.0)
#   - Segundo Piso (Y = 4.0):
#       * Balcón / Mezanine mirando al lobby (Z: -4 a +2)
#       * 3 habitaciones con puertas animadas (201, 202, 203) en Z: -12 a -4
#   - Techo alto a Y = 8.4 para sensación de hotel grande.

extends Node3D

@export var nav_region: NavigationRegion3D

var _mat_marble: StandardMaterial3D
var _mat_carpet: StandardMaterial3D
var _mat_wall: StandardMaterial3D
var _mat_wall_accent: StandardMaterial3D
var _mat_wood_trim: StandardMaterial3D
var _mat_ceiling: StandardMaterial3D
var _mat_brass: StandardMaterial3D


func _ready() -> void:
	_init_materials()
	_build_ground_floor()
	_build_second_floor()
	_build_staircase()
	_build_exterior_and_ceiling()
	_bake_navigation_deferred()


func _init_materials() -> void:
	_mat_marble = _make_mat(Color(0.79, 0.77, 0.73), 0.25, 0.05)
	_mat_carpet = _make_mat(Color(0.40, 0.11, 0.13), 0.88, 0.0)
	_mat_wall = _make_mat(Color(0.82, 0.78, 0.70), 0.75, 0.0)
	_mat_wall_accent = _make_mat(Color(0.24, 0.26, 0.30), 0.65, 0.05)
	_mat_wood_trim = _make_mat(Color(0.24, 0.12, 0.06), 0.50, 0.0)
	_mat_ceiling = _make_mat(Color(0.90, 0.88, 0.84), 0.85, 0.0)
	_mat_brass = _make_mat(Color(0.82, 0.65, 0.25), 0.25, 0.88)


func _make_mat(color: Color, rough: float, metal: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rough
	m.metallic = metal
	return m


func _add_block(box_name: String, size: Vector3, pos: Vector3, mat: Material, rot_deg: Vector3 = Vector3.ZERO) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = box_name
	body.position = pos
	body.rotation_degrees = rot_deg

	var mesh_inst := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	box.material = mat
	mesh_inst.mesh = box
	body.add_child(mesh_inst)

	var col := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = size
	col.shape = shape
	body.add_child(col)

	add_child(body)
	return body


func _add_wall_with_doorway(wall_name: String, width: float, height: float, thickness: float, center_pos: Vector3, door_local_x: float, mat: Material) -> void:
	# Abertura de puerta exacta de 1.02m de ancho x 2.24m de alto para hotel_door.glb
	var door_w := 1.02
	var door_h := 2.24
	var half_w := width * 0.5
	var left_edge := -half_w
	var right_edge := half_w
	var door_left := door_local_x - door_w * 0.5
	var door_right := door_local_x + door_w * 0.5

	var left_seg_w := door_left - left_edge
	if left_seg_w > 0.05:
		_add_block(wall_name + "_L", Vector3(left_seg_w, height, thickness),
			center_pos + Vector3((left_edge + door_left) * 0.5, height * 0.5, 0.0), mat)

	var right_seg_w := right_edge - door_right
	if right_seg_w > 0.05:
		_add_block(wall_name + "_R", Vector3(right_seg_w, height, thickness),
			center_pos + Vector3((door_right + right_edge) * 0.5, height * 0.5, 0.0), mat)

	var lintel_h := height - door_h
	if lintel_h > 0.05:
		_add_block(wall_name + "_Top", Vector3(door_w, lintel_h, thickness),
			center_pos + Vector3(door_local_x, door_h + lintel_h * 0.5, 0.0), mat)


func _build_ground_floor() -> void:
	# Suelo principal planta baja (24m x 24m)
	_add_block("Floor1_Slab", Vector3(24.0, 0.4, 24.0), Vector3(0.0, -0.2, 0.0), _mat_marble)
	# Alfombra roja del lobby
	_add_block("Lobby_Carpet", Vector3(6.0, 0.02, 11.0), Vector3(0.0, 0.01, 5.5), _mat_carpet)

	# Muro divisorio hacia las habitaciones de Planta Baja (Z = -4.0), con entrada central al pasillo y 2 habitaciones
	# Habitación 101 (X: -12 a -4, Z: -12 a -4) -> puerta en X = -8.0
	_add_wall_with_doorway("F1_Wall_101", 8.0, 4.0, 0.25, Vector3(-8.0, 0.0, -4.0), 0.0, _mat_wall)
	# Habitación 102 (X: +4 a +12, Z: -12 a -4) -> puerta en X = +8.0
	_add_wall_with_doorway("F1_Wall_102", 8.0, 4.0, 0.25, Vector3(8.0, 0.0, -4.0), 0.0, _mat_wall)

	# Paredes laterales de habitaciones 101 y 102
	_add_block("F1_Room101_Side", Vector3(0.25, 4.0, 8.0), Vector3(-4.0, 2.0, -8.0), _mat_wall)
	_add_block("F1_Room102_Side", Vector3(0.25, 4.0, 8.0), Vector3(4.0, 2.0, -8.0), _mat_wall)
	_add_block("F1_Carpet_101", Vector3(7.6, 0.02, 7.6), Vector3(-8.0, 0.01, -8.0), _mat_carpet)
	_add_block("F1_Carpet_102", Vector3(7.6, 0.02, 7.6), Vector3(8.0, 0.01, -8.0), _mat_carpet)


func _build_second_floor() -> void:
	# Segundo piso (Y = 4.0): cubre zona trasera y mezanine (Z: -12 a +1.5), dejando atrio abierto hacia el lobby (Z: +1.5 a +12)
	# Deja hueco central para la escalera (X: -2.0 a +2.0, Z: -3.5 a +1.5)
	_add_block("Floor2_Back", Vector3(24.0, 0.35, 8.5), Vector3(0.0, 3.825, -7.75), _mat_carpet)
	_add_block("Floor2_Mezz_Left", Vector3(10.0, 0.35, 5.0), Vector3(-7.0, 3.825, -1.0), _mat_marble)
	_add_block("Floor2_Mezz_Right", Vector3(10.0, 0.35, 5.0), Vector3(7.0, 3.825, -1.0), _mat_marble)

	# Barandales de protección del mezanine (altura ~1.05m para cubrir o disparar por encima)
	_add_block("Rail_Front_L", Vector3(10.0, 0.95, 0.14), Vector3(-7.0, 4.475, 1.43), _mat_wood_trim)
	_add_block("Rail_Front_R", Vector3(10.0, 0.95, 0.14), Vector3(7.0, 4.475, 1.43), _mat_wood_trim)
	_add_block("Rail_Top_L", Vector3(10.0, 0.08, 0.20), Vector3(-7.0, 4.98, 1.43), _mat_brass)
	_add_block("Rail_Top_R", Vector3(10.0, 0.08, 0.20), Vector3(7.0, 4.98, 1.43), _mat_brass)

	# 3 habitaciones en el Segundo Piso (Z = -4.0) -> 201 (X=-8), 202 (X=0), 203 (X=+8)
	_add_wall_with_doorway("F2_Wall_201", 8.0, 4.0, 0.25, Vector3(-8.0, 4.0, -4.0), 0.0, _mat_wall)
	_add_wall_with_doorway("F2_Wall_202", 8.0, 4.0, 0.25, Vector3(0.0, 4.0, -4.0), 0.0, _mat_wall)
	_add_wall_with_doorway("F2_Wall_203", 8.0, 4.0, 0.25, Vector3(8.0, 4.0, -4.0), 0.0, _mat_wall)

	_add_block("F2_Div_201_202", Vector3(0.25, 4.0, 8.0), Vector3(-4.0, 6.0, -8.0), _mat_wall)
	_add_block("F2_Div_202_203", Vector3(0.25, 4.0, 8.0), Vector3(4.0, 6.0, -8.0), _mat_wall)


func _build_staircase() -> void:
	# Rampa continua suave para subir sin tropiezos del Piso 1 (Z=+3.2, Y=0) al Piso 2 (Z=-3.5, Y=4.0)
	# Longitud horizontal = 6.7m, altura = 4.0m
	var dx := 0.0
	var length_z := 6.7
	var height_y := 4.0
	var diag := sqrt(length_z * length_z + height_y * height_y)
	var angle_deg := rad_to_deg(atan2(height_y, length_z))

	# Cuerpo sólido de la rampa inclinada
	_add_block(
		"GrandStair_Ramp",
		Vector3(3.8, 0.35, diag),
		Vector3(dx, 1.85, -0.15),
		_mat_carpet,
		Vector3(angle_deg, 0.0, 0.0)
	)
	# Zócalos laterales de la escalera
	_add_block("Stair_Wall_L", Vector3(0.20, 4.0, 6.8), Vector3(-2.0, 2.0, -0.15), _mat_wood_trim)
	_add_block("Stair_Wall_R", Vector3(0.20, 4.0, 6.8), Vector3(2.0, 2.0, -0.15), _mat_wood_trim)


func _build_exterior_and_ceiling() -> void:
	# Muros perimetrales de 2 pisos completos (8.4m de altura)
	_add_block("Ext_North", Vector3(24.4, 8.4, 0.4), Vector3(0.0, 4.2, -12.0), _mat_wall_accent)
	_add_block("Ext_South", Vector3(24.4, 8.4, 0.4), Vector3(0.0, 4.2, 12.0), _mat_wall_accent)
	_add_block("Ext_West", Vector3(0.4, 8.4, 24.4), Vector3(-12.0, 4.2, 0.0), _mat_wall_accent)
	_add_block("Ext_East", Vector3(0.4, 8.4, 24.4), Vector3(12.0, 4.2, 0.0), _mat_wall_accent)

	# Techo del hotel + tragaluz central simulado
	_add_block("Hotel_Ceiling", Vector3(24.4, 0.4, 24.4), Vector3(0.0, 8.4, 0.0), _mat_ceiling)


func _bake_navigation_deferred() -> void:
	if nav_region == null:
		return
	call_deferred("_do_bake_nav")


func _do_bake_nav() -> void:
	if nav_region and nav_region.navigation_mesh:
		nav_region.bake_navigation_mesh(false)
