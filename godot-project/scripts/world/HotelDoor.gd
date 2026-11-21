# HotelDoor.gd
# Controla las puertas animables de las habitaciones del hotel.
# Busca el nodo DoorPivot del modelo hotel_door.glb y anima suavemente su apertura/cierre
# alrededor de la bisagra, actualizando colisiones y alertando a terroristas cercanos al abrirse.

extends Node3D

@export var open_angle_deg: float = 95.0
@export var animation_duration: float = 0.42
@export var room_label: String = "Habitación"

@onready var door_model: Node3D = $DoorModel
@onready var leaf_collider: StaticBody3D = $DoorPivotProxy/LeafCollider
@onready var pivot_proxy: Node3D = $DoorPivotProxy

var _model_pivot: Node3D
var is_open: bool = false
var _tween: Tween


func _ready() -> void:
	add_to_group("hotel_doors")
	if door_model:
		_model_pivot = door_model.find_child("DoorPivot", true, false) as Node3D
	if leaf_collider:
		leaf_collider.set_meta("hotel_door_owner", self)


func get_prompt_text() -> String:
	return ("Cerrar " if is_open else "Abrir ") + room_label


func toggle_door() -> void:
	set_open(not is_open)


func set_open(open_state: bool) -> void:
	if is_open == open_state:
		return
	is_open = open_state
	AudioSynth.play_door_3d(global_position)

	var target_rad := deg_to_rad(open_angle_deg if is_open else 0.0)
	if _tween and _tween.is_valid():
		_tween.kill()
	_tween = create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)

	if _model_pivot:
		_tween.parallel().tween_property(_model_pivot, "rotation:y", target_rad, animation_duration)
	if pivot_proxy:
		_tween.parallel().tween_property(pivot_proxy, "rotation:y", target_rad, animation_duration)

	if is_open:
		get_tree().call_group("terrorists", "on_door_breached", global_position, 11.0)
