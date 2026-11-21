# VirtualJoystick.gd
# Joystick táctil ergonómico para el pulgar izquierdo en dispositivos móviles.
# Soporta seguimiento independiente por índice táctil (finger index) para no interferir
# con la puntería ni el disparo del pulgar derecho.

extends Control

signal move_vector_changed(vector: Vector2)

@export var max_radius: float = 78.0
@export var deadzone: float = 0.12

@onready var base_ring: Panel = $BaseRing
@onready var knob: Panel = $BaseRing/Knob

var _active_touch_idx: int = -1
var _center_pos: Vector2 = Vector2.ZERO
var _current_vec: Vector2 = Vector2.ZERO


func _ready() -> void:
	_apply_scale_from_settings()
	GameSettings.settings_changed.connect(_apply_scale_from_settings)
	call_deferred("_recalc_center")


func _apply_scale_from_settings() -> void:
	scale = Vector2.ONE * GameSettings.joystick_scale


func _recalc_center() -> void:
	pivot_offset = size * 0.5
	if base_ring:
		_center_pos = base_ring.position + base_ring.size * 0.5
		_reset_knob()


func _reset_knob() -> void:
	_current_vec = Vector2.ZERO
	if knob and base_ring:
		knob.position = (base_ring.size - knob.size) * 0.5
	move_vector_changed.emit(Vector2.ZERO)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var touch := event as InputEventScreenTouch
		if touch.pressed and _active_touch_idx == -1:
			_active_touch_idx = touch.index
			_update_knob(touch.position)
			accept_event()
		elif not touch.pressed and touch.index == _active_touch_idx:
			_active_touch_idx = -1
			_reset_knob()
			accept_event()
	elif event is InputEventScreenDrag:
		var drag := event as InputEventScreenDrag
		if drag.index == _active_touch_idx:
			_update_knob(drag.position)
			accept_event()
	elif event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_LEFT:
			if mb.pressed and _active_touch_idx == -1:
				_active_touch_idx = 999
				_update_knob(mb.position)
				accept_event()
			elif not mb.pressed and _active_touch_idx == 999:
				_active_touch_idx = -1
				_reset_knob()
				accept_event()
	elif event is InputEventMouseMotion and _active_touch_idx == 999:
		_update_knob((event as InputEventMouseMotion).position)
		accept_event()


func _update_knob(local_pos: Vector2) -> void:
	var offset := local_pos - _center_pos
	var dist := offset.length()
	if dist > max_radius:
		offset = offset.normalized() * max_radius

	if knob and base_ring:
		knob.position = (base_ring.size - knob.size) * 0.5 + offset

	var norm := offset / max_radius
	if norm.length() < deadzone:
		_current_vec = Vector2.ZERO
	else:
		_current_vec = norm
	move_vector_changed.emit(_current_vec)
