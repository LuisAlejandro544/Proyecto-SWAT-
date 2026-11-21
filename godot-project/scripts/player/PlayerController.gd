# PlayerController.gd
# Controlador en primera persona del agente SWAT ("píldora por defecto").
# Gestiona desplazamiento, agachado, salto, puntería táctil/ratón, retroceso de cámara,
# salud/blindaje, interacción con puertas del hotel y conexión con el arma M4.

extends CharacterBody3D

signal health_changed(hp: float, max_hp: float)
signal door_prompt_changed(visible: bool, text: String)
signal ads_changed(enabled: bool)
signal crouch_changed(enabled: bool)
signal damage_taken_from(attacker_pos: Vector3)
signal player_died

@export_group("Movimiento")
@export var walk_speed: float = 4.6
@export var sprint_speed: float = 6.4
@export var crouch_speed: float = 2.6
@export var jump_velocity: float = 4.4
@export var gravity_force: float = 14.0

@export_group("Salud SWAT")
@export var max_health: float = 100.0

@onready var head_pivot: Node3D = $HeadPivot
@onready var camera: Camera3D = $HeadPivot/Camera3D
@onready var weapon_m4: Node3D = $HeadPivot/Camera3D/WeaponM4
@onready var aim_ray: RayCast3D = $HeadPivot/Camera3D/AimRay
@onready var interact_ray: RayCast3D = $HeadPivot/Camera3D/InteractRay
@onready var collision_shape: CollisionShape3D = $CollisionShape3D
@onready var pill_mesh: MeshInstance3D = $PillMesh

var health: float = 100.0
var is_crouching: bool = false
var is_dead: bool = false

var _move_input: Vector2 = Vector2.ZERO
var _wants_fire: bool = false
var _wants_ads: bool = false

var _pitch_deg: float = 0.0
var _recoil_pitch: float = 0.0
var _recoil_yaw: float = 0.0
var _base_fov: float = 74.0
var _ads_fov: float = 54.0

var _current_door: Node = null


func _ready() -> void:
	add_to_group("player")
	health = max_health
	if weapon_m4 and weapon_m4.has_method("setup_references"):
		weapon_m4.setup_references(self, camera, aim_ray)
	health_changed.emit(health, max_health)


func set_touch_move_input(vec: Vector2) -> void:
	_move_input = vec


func add_look_delta(delta_pixels: Vector2) -> void:
	if is_dead:
		return
	var sens := GameSettings.look_sensitivity
	if _wants_ads:
		sens *= GameSettings.ads_sensitivity_multiplier
	var y_sign := 1.0 if GameSettings.invert_y else -1.0

	rotate_y(deg_to_rad(-delta_pixels.x * sens))
	_pitch_deg = clampf(_pitch_deg + delta_pixels.y * sens * y_sign, -78.0, 78.0)

	if weapon_m4 and weapon_m4.has_method("add_look_sway"):
		weapon_m4.add_look_sway(delta_pixels * sens)


func set_fire_pressed(pressed: bool) -> void:
	_wants_fire = pressed


func toggle_ads() -> void:
	set_ads(not _wants_ads)


func set_ads(enabled: bool) -> void:
	_wants_ads = enabled
	if weapon_m4 and weapon_m4.has_method("set_ads"):
		weapon_m4.set_ads(_wants_ads)
	ads_changed.emit(_wants_ads)


func toggle_crouch() -> void:
	is_crouching = not is_crouching
	crouch_changed.emit(is_crouching)


func trigger_jump() -> void:
	if is_dead:
		return
	if is_on_floor():
		if is_crouching:
			is_crouching = false
		velocity.y = jump_velocity


func trigger_reload() -> void:
	if is_dead or weapon_m4 == null:
		return
	if weapon_m4.has_method("start_reload"):
		weapon_m4.start_reload()


func interact_with_door() -> void:
	if is_dead or _current_door == null:
		return
	if _current_door.has_method("toggle_door"):
		_current_door.toggle_door()
		door_prompt_changed.emit(true, _current_door.get_prompt_text())


func apply_camera_recoil(pitch_kick: float, yaw_kick: float) -> void:
	_recoil_pitch += pitch_kick
	_recoil_yaw += yaw_kick


func apply_damage(amount: float, attacker_pos: Vector3 = Vector3.ZERO) -> void:
	if is_dead:
		return
	health = maxf(0.0, health - amount)
	health_changed.emit(health, max_health)
	if attacker_pos != Vector3.ZERO:
		damage_taken_from.emit(attacker_pos)
	if health <= 0.0:
		is_dead = true
		_wants_fire = false
		player_died.emit()


func _unhandled_input(event: InputEvent) -> void:
	if is_dead:
		return
	# Respaldo opcional para pruebas rápidas con teclado/ratón si se abre fuera de móvil
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		add_look_delta(event.relative * 0.6)
	elif event.is_action_pressed("ui_accept") and is_on_floor():
		trigger_jump()


func _physics_process(delta: float) -> void:
	if is_dead:
		return

	# Lectura opcional de teclado WASD combinada con joystick táctil
	var key_vec := Vector2.ZERO
	if Input.is_key_pressed(KEY_A):
		key_vec.x -= 1.0
	if Input.is_key_pressed(KEY_D):
		key_vec.x += 1.0
	if Input.is_key_pressed(KEY_W):
		key_vec.y -= 1.0
	if Input.is_key_pressed(KEY_S):
		key_vec.y += 1.0

	var combined_input := _move_input if _move_input.length_squared() > 0.01 else key_vec
	if combined_input.length() > 1.0:
		combined_input = combined_input.normalized()

	# Altura suave al agacharse (píldora estándar 1.8m vs agachada 1.15m)
	var target_head_y := 1.05 if is_crouching else 1.56
	if head_pivot:
		head_pivot.position.y = lerpf(head_pivot.position.y, target_head_y, minf(1.0, delta * 12.0))
	if collision_shape and collision_shape.shape is CapsuleShape3D:
		var cap := collision_shape.shape as CapsuleShape3D
		cap.height = lerpf(cap.height, 1.25 if is_crouching else 1.80, minf(1.0, delta * 12.0))
		collision_shape.position.y = cap.height * 0.5

	# Gravedad y desplazamiento horizontal
	if not is_on_floor():
		velocity.y -= gravity_force * delta

	var forward := -transform.basis.z
	var right := transform.basis.x
	var move_dir := (right * combined_input.x - forward * combined_input.y)
	if move_dir.length() > 0.001:
		move_dir = move_dir.normalized()

	var speed := walk_speed
	if is_crouching:
		speed = crouch_speed
	elif GameSettings.auto_sprint and combined_input.y < -0.78 and not _wants_ads and not _wants_fire:
		speed = sprint_speed

	var mag := clampf(combined_input.length(), 0.0, 1.0)
	velocity.x = lerpf(velocity.x, move_dir.x * speed * mag, minf(1.0, delta * 12.0))
	velocity.z = lerpf(velocity.z, move_dir.z * speed * mag, minf(1.0, delta * 12.0))

	move_and_slide()

	# Recuperación de retroceso y FOV suave para ADS
	_recoil_pitch = lerpf(_recoil_pitch, 0.0, minf(1.0, delta * 10.0))
	_recoil_yaw = lerpf(_recoil_yaw, 0.0, minf(1.0, delta * 10.0))
	if head_pivot:
		head_pivot.rotation.x = deg_to_rad(clampf(_pitch_deg + _recoil_pitch, -82.0, 82.0))
		head_pivot.rotation.y = deg_to_rad(_recoil_yaw)
	if camera:
		var target_fov := _ads_fov if _wants_ads else _base_fov
		camera.fov = lerpf(camera.fov, target_fov, minf(1.0, delta * 12.0))

	# Disparo continuo del M4 mientras se mantiene el botón
	if weapon_m4 and weapon_m4.has_method("try_fire"):
		weapon_m4.try_fire(_wants_fire)

	_update_door_detection()


func _update_door_detection() -> void:
	var detected_door: Node = null
	if interact_ray:
		interact_ray.force_raycast_update()
		if interact_ray.is_colliding():
			var col := interact_ray.get_collider()
			if col and col.has_meta("hotel_door_owner"):
				detected_door = col.get_meta("hotel_door_owner")

	if detected_door != _current_door:
		_current_door = detected_door
		if _current_door:
			door_prompt_changed.emit(true, _current_door.get_prompt_text())
		else:
			door_prompt_changed.emit(false, "")
