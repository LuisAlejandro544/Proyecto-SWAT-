# MobileHUD.gd
# Interfaz táctica ergonómica para móvil durante la misión en el hotel.
# Disposición tipo shooter táctico profesional en arco alrededor del pulgar derecho:
#   - DISPARAR (botón circular principal que permite apuntar simultáneamente)
#   - MIRA (ADS), RECARGAR, SALTAR y AGACHAR dispuestos en arco sin cubrir el arma
#   - Indicador de munición en esquina superior derecha, salud, objetivos y daño direccional.

extends CanvasLayer

signal pause_requested

@onready var joystick: Control = $TouchLayer/VirtualJoystick
@onready var look_pad: Control = $TouchLayer/LookPad
@onready var btn_fire: Control = $TouchLayer/RightControls/FireButton
@onready var btn_ads: Button = $TouchLayer/RightControls/AdsButton
@onready var btn_reload: Button = $TouchLayer/RightControls/ReloadButton
@onready var btn_crouch: Button = $TouchLayer/RightControls/CrouchButton
@onready var btn_jump: Button = $TouchLayer/RightControls/JumpButton
@onready var btn_door: Button = $TouchLayer/DoorInteractButton
@onready var btn_pause: Button = $TopBar/PauseButton

@onready var hp_bar: ProgressBar = $TopBar/HealthBox/HealthBar
@onready var hp_label: Label = $TopBar/HealthBox/HealthValue
@onready var enemies_label: Label = $TopBar/MissionStatus/EnemiesLabel
@onready var ammo_label: Label = $TouchLayer/AmmoPanel/AmmoVBox/AmmoLabel
@onready var reload_label: Label = $TouchLayer/AmmoPanel/AmmoVBox/ReloadHint
@onready var crosshair_root: Control = $CrosshairRoot
@onready var hitmarker: Control = $CrosshairRoot/Hitmarker
@onready var damage_vignette: ColorRect = $DamageVignette
@onready var edge_left: ColorRect = $DamageEdges/EdgeLeft
@onready var edge_right: ColorRect = $DamageEdges/EdgeRight
@onready var edge_top: ColorRect = $DamageEdges/EdgeTop
@onready var edge_bottom: ColorRect = $DamageEdges/EdgeBottom

var _player: CharacterBody3D
var _weapon: Node3D
var _look_touch_idx: int = -1
var _fire_touch_idx: int = -1
var _hitmarker_timer: float = 0.0
var _damage_flash: float = 0.0
var _edge_flash := {"left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0}
var _last_hp: float = 100.0


func bind_player(player: CharacterBody3D, weapon: Node3D) -> void:
	_player = player
	_weapon = weapon
	_last_hp = player.max_health

	if joystick and joystick.has_signal("move_vector_changed"):
		joystick.move_vector_changed.connect(_player.set_touch_move_input)

	_player.health_changed.connect(_on_health_changed)
	_player.door_prompt_changed.connect(_on_door_prompt_changed)
	if _player.has_signal("ads_changed"):
		_player.ads_changed.connect(_on_ads_changed)
	if _player.has_signal("crouch_changed"):
		_player.crouch_changed.connect(_on_crouch_changed)
	if _player.has_signal("damage_taken_from"):
		_player.damage_taken_from.connect(_on_damage_taken_from)
	if _weapon:
		_weapon.ammo_changed.connect(_on_ammo_changed)
		_weapon.shot_fired.connect(_on_shot_fired)

	_on_health_changed(_player.health, _player.max_health)


func set_remaining_terrorists(remaining: int, total: int) -> void:
	if enemies_label:
		enemies_label.text = "OBJETIVOS: %d / %d" % [remaining, total]


func _ready() -> void:
	if btn_door:
		btn_door.visible = false
		btn_door.pressed.connect(func():
			if _player:
				_player.interact_with_door()
		)
	if btn_ads:
		btn_ads.pressed.connect(func():
			if _player:
				_player.toggle_ads()
		)
	if btn_reload:
		btn_reload.pressed.connect(func():
			if _player:
				_player.trigger_reload()
		)
	if btn_crouch:
		btn_crouch.pressed.connect(func():
			if _player:
				_player.toggle_crouch()
		)
	if btn_jump:
		btn_jump.pressed.connect(func():
			if _player:
				_player.trigger_jump()
		)
	if btn_pause:
		btn_pause.pressed.connect(func(): pause_requested.emit())

	if look_pad:
		look_pad.gui_input.connect(_on_look_pad_input)
	if btn_fire:
		btn_fire.gui_input.connect(_on_fire_button_input)
	if hitmarker:
		hitmarker.visible = false
	if damage_vignette:
		damage_vignette.modulate.a = 0.0


func _process(delta: float) -> void:
	if _hitmarker_timer > 0.0:
		_hitmarker_timer -= delta
		if _hitmarker_timer <= 0.0 and hitmarker:
			hitmarker.visible = false

	if _damage_flash > 0.0:
		_damage_flash = maxf(0.0, _damage_flash - delta * 2.2)
		if damage_vignette:
			damage_vignette.modulate.a = _damage_flash

	for dir_key in _edge_flash.keys():
		if _edge_flash[dir_key] > 0.0:
			_edge_flash[dir_key] = maxf(0.0, _edge_flash[dir_key] - delta * 1.8)

	if edge_left:
		edge_left.modulate.a = _edge_flash["left"]
	if edge_right:
		edge_right.modulate.a = _edge_flash["right"]
	if edge_top:
		edge_top.modulate.a = _edge_flash["top"]
	if edge_bottom:
		edge_bottom.modulate.a = _edge_flash["bottom"]


func _on_look_pad_input(event: InputEvent) -> void:
	if _player == null:
		return
	if event is InputEventScreenTouch:
		var t := event as InputEventScreenTouch
		if t.pressed and _look_touch_idx == -1:
			_look_touch_idx = t.index
		elif not t.pressed and t.index == _look_touch_idx:
			_look_touch_idx = -1
	elif event is InputEventScreenDrag:
		var d := event as InputEventScreenDrag
		if d.index == _look_touch_idx:
			_player.add_look_delta(d.relative)


func _on_fire_button_input(event: InputEvent) -> void:
	if _player == null:
		return
	# Permite disparar Y seguir moviendo la mira deslizando el mismo pulgar sobre DISPARAR
	if event is InputEventScreenTouch:
		var t := event as InputEventScreenTouch
		if t.pressed and _fire_touch_idx == -1:
			_fire_touch_idx = t.index
			_player.set_fire_pressed(true)
			btn_fire.modulate = Color(1.0, 0.72, 0.65, 1.0)
			get_viewport().set_input_as_handled()
		elif not t.pressed and t.index == _fire_touch_idx:
			_fire_touch_idx = -1
			_player.set_fire_pressed(false)
			btn_fire.modulate = Color.WHITE
			get_viewport().set_input_as_handled()
	elif event is InputEventScreenDrag:
		var d := event as InputEventScreenDrag
		if d.index == _fire_touch_idx:
			_player.add_look_delta(d.relative)
			get_viewport().set_input_as_handled()
	elif event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_LEFT:
			_player.set_fire_pressed(mb.pressed)
			btn_fire.modulate = Color(1.0, 0.72, 0.65, 1.0) if mb.pressed else Color.WHITE


func _on_health_changed(hp: float, max_hp: float) -> void:
	if hp < _last_hp:
		_damage_flash = 0.55
	_last_hp = hp
	if hp_bar:
		hp_bar.max_value = max_hp
		hp_bar.value = hp
	if hp_label:
		hp_label.text = "%d HP" % int(ceilf(hp))


func _on_damage_taken_from(attacker_pos: Vector3) -> void:
	if _player == null:
		return
	var to_attacker := attacker_pos - _player.global_position
	to_attacker.y = 0.0
	if to_attacker.length_squared() < 0.001:
		return
	var dir := to_attacker.normalized()
	var forward := (-_player.global_transform.basis.z)
	forward.y = 0.0
	forward = forward.normalized()
	var right := _player.global_transform.basis.x
	right.y = 0.0
	right = right.normalized()

	var f_dot := forward.dot(dir)
	var r_dot := right.dot(dir)
	if absf(r_dot) > absf(f_dot):
		if r_dot > 0.0:
			_edge_flash["right"] = 0.95
		else:
			_edge_flash["left"] = 0.95
	else:
		if f_dot > 0.0:
			_edge_flash["top"] = 0.95
		else:
			_edge_flash["bottom"] = 0.95


func _on_ads_changed(enabled: bool) -> void:
	if btn_ads:
		btn_ads.modulate = Color(0.55, 0.88, 1.0, 1.0) if enabled else Color.WHITE
	if crosshair_root:
		crosshair_root.scale = Vector2(0.75, 0.75) if enabled else Vector2.ONE


func _on_crouch_changed(enabled: bool) -> void:
	if btn_crouch:
		btn_crouch.modulate = Color(1.0, 0.82, 0.40, 1.0) if enabled else Color.WHITE


func _on_ammo_changed(mag_ammo: int, reserve: int, is_reloading: bool) -> void:
	if ammo_label:
		ammo_label.text = "%02d / %03d" % [mag_ammo, reserve]
	if reload_label:
		reload_label.text = "RECARGANDO M4..." if is_reloading else "M4A1 · 5.56mm"


func _on_door_prompt_changed(is_visible_prompt: bool, prompt_text: String) -> void:
	if btn_door:
		btn_door.visible = is_visible_prompt
		btn_door.text = prompt_text


func _on_shot_fired(hit_info: Dictionary) -> void:
	if hit_info.get("enemy", false) and hitmarker:
		hitmarker.visible = true
		hitmarker.modulate = Color(1.0, 0.22, 0.18, 1.0) if hit_info.get("headshot", false) else Color.WHITE
		_hitmarker_timer = 0.14
