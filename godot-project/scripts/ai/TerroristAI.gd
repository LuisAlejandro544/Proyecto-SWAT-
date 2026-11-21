# TerroristAI.gd
# Inteligencia artificial táctica para los terroristas armados con AK-47 dentro del hotel.
# Comportamiento realista:
#   - PATROL / GUARD: vigila habitaciones o pasillos y rota la mirada periódicamente.
#   - ALERT: investiga disparos cercanos o puertas abiertas por el agente SWAT.
#   - COMBAT: apunta, se desplaza lateralmente/busca cobertura con NavigationAgent3D y dispara ráfagas de AK-47
#             con fogonazo real, retroceso del cerrojo AK47_Bolt y expulsión física de casquillos.
#   - RELOADING: recarga su cargador curvo AK47_Magazine tras agotar munición.

extends CharacterBody3D

signal terrorist_neutralized(terrorist: Node3D)

enum State { GUARD, ALERT, COMBAT, RELOADING, NEUTRALIZED }

@export_group("Combate Terrorista")
@export var max_health: float = 100.0
@export var move_speed: float = 3.2
@export var detection_range: float = 28.0
@export var fov_degrees: float = 125.0
@export var ak_damage: float = 11.0
@export var ak_mag_size: int = 24
@export var patrol_points: Array[Vector3] = []

@export_group("Escenas")
@export var shell_casing_scene: PackedScene

@onready var nav_agent: NavigationAgent3D = $NavigationAgent3D
@onready var visual_root: Node3D = $VisualRoot
@onready var terrorist_model: Node3D = $VisualRoot/TerroristModel
@onready var ak_holder: Node3D = $VisualRoot/AKHolder
@onready var ak_model: Node3D = $VisualRoot/AKHolder/AK47Model
@onready var muzzle_flash: Node3D = $VisualRoot/AKHolder/MuzzleFlash
@onready var los_ray: RayCast3D = $LineOfSightRay
@onready var body_hitbox: Area3D = $BodyHitbox
@onready var head_hitbox: Area3D = $HeadHitbox

var state: State = State.GUARD
var health: float = 100.0
var _ammo: int = 24
var _player: CharacterBody3D
var _last_known_player_pos: Vector3 = Vector3.ZERO
var _patrol_index: int = 0

var _burst_shots_left: int = 0
var _fire_timer: float = 0.0
var _burst_cooldown: float = 0.6
var _flash_timer: float = 0.0
var _reload_timer: float = 0.0
var _strafe_dir: float = 1.0
var _strafe_timer: float = 1.2
var _guard_look_timer: float = 2.0
var _guard_yaw_target: float = 0.0

var _ak_bolt: Node3D
var _ak_mag: Node3D
var _ak_muzzle: Node3D
var _ak_ejection: Node3D
var _ak_bolt_rest: Vector3 = Vector3.ZERO
var _ak_mag_rest: Vector3 = Vector3.ZERO
var _ak_holder_rest: Vector3 = Vector3.ZERO
var _ak_recoil_z: float = 0.0

var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.randomize()
	add_to_group("terrorists")
	health = max_health
	_ammo = ak_mag_size
	_guard_yaw_target = rotation.y

	if body_hitbox:
		body_hitbox.set_meta("terrorist_owner", self)
		body_hitbox.set_meta("is_headshot", false)
	if head_hitbox:
		head_hitbox.set_meta("terrorist_owner", self)
		head_hitbox.set_meta("is_headshot", true)

	_cache_ak_parts()
	if muzzle_flash:
		muzzle_flash.visible = false

	call_deferred("_find_player")


func _find_player() -> void:
	_player = get_tree().get_first_node_in_group("player") as CharacterBody3D


func _cache_ak_parts() -> void:
	if ak_holder:
		_ak_holder_rest = ak_holder.position
	if ak_model:
		_ak_bolt = ak_model.find_child("AK47_Bolt", true, false) as Node3D
		_ak_mag = ak_model.find_child("AK47_Magazine", true, false) as Node3D
		_ak_muzzle = ak_model.find_child("MuzzlePoint", true, false) as Node3D
		_ak_ejection = ak_model.find_child("EjectionPort", true, false) as Node3D
		if _ak_bolt:
			_ak_bolt_rest = _ak_bolt.position
		if _ak_mag:
			_ak_mag_rest = _ak_mag.position


func on_gunshot_heard(origin: Vector3, radius: float) -> void:
	if state == State.NEUTRALIZED:
		return
	if global_position.distance_to(origin) <= radius and state == State.GUARD:
		_last_known_player_pos = origin
		state = State.ALERT
		if nav_agent:
			nav_agent.target_position = origin


func on_door_breached(door_pos: Vector3, radius: float) -> void:
	if state == State.NEUTRALIZED:
		return
	if global_position.distance_to(door_pos) <= radius:
		_last_known_player_pos = door_pos
		if state == State.GUARD:
			state = State.ALERT
			if nav_agent:
				nav_agent.target_position = door_pos


func apply_damage(amount: float, _hit_pos: Vector3, _is_headshot: bool) -> bool:
	if state == State.NEUTRALIZED:
		return false

	health -= amount
	# Al recibir daño, entra inmediatamente en combate hacia la posición del SWAT
	if _player:
		_last_known_player_pos = _player.global_position
		if state == State.GUARD or state == State.ALERT:
			state = State.COMBAT

	if health <= 0.0:
		_neutralize()
		return true
	return false


func _neutralize() -> void:
	state = State.NEUTRALIZED
	if muzzle_flash:
		muzzle_flash.visible = false
	if body_hitbox:
		body_hitbox.set_deferred("monitoring", false)
		body_hitbox.set_deferred("monitorable", false)
	if head_hitbox:
		head_hitbox.set_deferred("monitoring", false)
		head_hitbox.set_deferred("monitorable", false)
	collision_layer = 0
	collision_mask = 0

	# Animación de caída táctica de la píldora
	var tw := create_tween().set_ease(Tween.EASE_IN).set_trans(Tween.TRANS_QUAD)
	tw.tween_property(visual_root, "rotation_degrees:x", -88.0, 0.35)
	tw.parallel().tween_property(visual_root, "position:y", 0.25, 0.35)
	terrorist_neutralized.emit(self)


func _physics_process(delta: float) -> void:
	if state == State.NEUTRALIZED:
		return

	if not is_on_floor():
		velocity.y -= 14.0 * delta

	if _flash_timer > 0.0:
		_flash_timer -= delta
		if _flash_timer <= 0.0 and muzzle_flash:
			muzzle_flash.visible = false

	# Recuperación del retroceso del AK-47
	_ak_recoil_z = lerpf(_ak_recoil_z, 0.0, minf(1.0, delta * 18.0))
	if ak_holder:
		ak_holder.position = _ak_holder_rest + Vector3(0.0, 0.0, _ak_recoil_z)
	if _ak_bolt:
		_ak_bolt.position = _ak_bolt_rest + Vector3(0.0, 0.0, _ak_recoil_z * 1.4)

	var can_see_player := _check_player_visibility()
	if can_see_player and _player:
		_last_known_player_pos = _player.global_position
		if state == State.GUARD or state == State.ALERT:
			state = State.COMBAT
			get_tree().call_group("terrorists", "on_gunshot_heard", global_position, 10.0)

	match state:
		State.GUARD:
			_process_guard(delta)
		State.ALERT:
			_process_alert(delta)
		State.COMBAT:
			_process_combat(delta, can_see_player)
		State.RELOADING:
			_process_reload(delta)

	move_and_slide()
	if state == State.ALERT or state == State.COMBAT:
		_try_open_blocking_door()


func _process_guard(delta: float) -> void:
	if patrol_points.size() > 0:
		var target := patrol_points[_patrol_index]
		if nav_agent:
			nav_agent.target_position = target
			_move_along_nav(delta, move_speed * 0.55)
		if global_position.distance_to(target) < 1.0:
			_patrol_index = (_patrol_index + 1) % patrol_points.size()
	else:
		velocity.x = lerpf(velocity.x, 0.0, delta * 8.0)
		velocity.z = lerpf(velocity.z, 0.0, delta * 8.0)
		_guard_look_timer -= delta
		if _guard_look_timer <= 0.0:
			_guard_look_timer = _rng.randf_range(2.0, 4.2)
			_guard_yaw_target += _rng.randf_range(-1.1, 1.1)
		rotation.y = lerp_angle(rotation.y, _guard_yaw_target, delta * 2.5)


func _process_alert(delta: float) -> void:
	if nav_agent:
		nav_agent.target_position = _last_known_player_pos
		_move_along_nav(delta, move_speed * 0.85)
		if nav_agent.is_navigation_finished():
			_guard_look_timer -= delta
			rotation.y += delta * 1.6
			if _guard_look_timer <= -1.5:
				state = State.GUARD


func _process_combat(delta: float, can_see_player: bool) -> void:
	if _player == null or _player.get("is_dead"):
		state = State.GUARD
		return

	var to_player := _player.global_position - global_position
	var flat_dist := Vector2(to_player.x, to_player.z).length()
	var target_yaw := atan2(-to_player.x, -to_player.z)
	rotation.y = lerp_angle(rotation.y, target_yaw, minf(1.0, delta * 9.0))

	if can_see_player:
		# Desplazamiento lateral táctico mientras dispara (strafe)
		_strafe_timer -= delta
		if _strafe_timer <= 0.0:
			_strafe_timer = _rng.randf_range(0.9, 1.9)
			_strafe_dir = -_strafe_dir

		var right_vec := transform.basis.x
		var forward_vec := -transform.basis.z
		var desired_vel := right_vec * _strafe_dir * (move_speed * 0.65)
		if flat_dist > 11.0:
			desired_vel += forward_vec * (move_speed * 0.6)
		elif flat_dist < 4.5:
			desired_vel -= forward_vec * (move_speed * 0.5)

		velocity.x = lerpf(velocity.x, desired_vel.x, delta * 6.0)
		velocity.z = lerpf(velocity.z, desired_vel.z, delta * 6.0)

		_handle_ak_burst(delta)
	else:
		# Si perdió línea de visión, avanza hacia la última posición conocida
		if nav_agent:
			nav_agent.target_position = _last_known_player_pos
			_move_along_nav(delta, move_speed)


func _handle_ak_burst(delta: float) -> void:
	if _ammo <= 0:
		_start_ak_reload()
		return

	if _burst_shots_left > 0:
		_fire_timer -= delta
		if _fire_timer <= 0.0:
			_fire_ak_round()
			_burst_shots_left -= 1
			_fire_timer = 0.12
			if _burst_shots_left == 0:
				_burst_cooldown = _rng.randf_range(0.55, 1.15)
	else:
		_burst_cooldown -= delta
		if _burst_cooldown <= 0.0:
			_burst_shots_left = mini(_ammo, _rng.randi_range(3, 5))
			_fire_timer = 0.0


func _fire_ak_round() -> void:
	if _ammo <= 0 or _player == null:
		return
	_ammo -= 1
	_ak_recoil_z = 0.055

	AudioSynth.play_ak_shot_3d(global_position)

	if muzzle_flash and _ak_muzzle:
		muzzle_flash.global_transform = _ak_muzzle.global_transform
		muzzle_flash.visible = true
		muzzle_flash.rotation.z = _rng.randf_range(0.0, TAU)
		_flash_timer = 0.05

	_eject_ak_casing()

	# Comprobación de impacto con dispersión realista para dar margen táctico al jugador
	var aim_origin := global_position + Vector3(0.0, 1.42, 0.0)
	var player_target := _player.global_position + Vector3(0.0, 1.15, 0.0)
	var dir := (player_target - aim_origin).normalized()
	dir = (dir + Vector3(
		_rng.randf_range(-0.085, 0.085),
		_rng.randf_range(-0.06, 0.06),
		_rng.randf_range(-0.085, 0.085)
	)).normalized()

	var space_state := get_world_3d().direct_space_state
	var query := PhysicsRayQueryParameters3D.create(aim_origin, aim_origin + dir * 34.0, 1)
	query.exclude = [self]
	var hit := space_state.intersect_ray(query)
	if hit and hit.get("collider") == _player:
		if _player.has_method("apply_damage"):
			_player.apply_damage(ak_damage, global_position)


func _eject_ak_casing() -> void:
	if shell_casing_scene == null or _ak_ejection == null:
		return
	var level := get_tree().current_scene
	if level == null:
		return
	var casing := shell_casing_scene.instantiate() as RigidBody3D
	if casing == null:
		return
	level.add_child(casing)
	casing.global_transform = _ak_ejection.global_transform
	var right_dir := _ak_ejection.global_transform.basis.x.normalized()
	var up_dir := _ak_ejection.global_transform.basis.y.normalized()
	if casing.has_method("launch"):
		casing.launch(
			right_dir * _rng.randf_range(2.0, 2.8) + up_dir * _rng.randf_range(1.4, 2.0),
			Vector3(_rng.randf_range(-20, 20), _rng.randf_range(-20, 20), _rng.randf_range(-20, 20))
		)


func _start_ak_reload() -> void:
	state = State.RELOADING
	_reload_timer = 1.9
	velocity.x *= 0.3
	velocity.z *= 0.3
	if _ak_mag:
		var tw := create_tween()
		tw.tween_property(_ak_mag, "position:y", _ak_mag_rest.y - 0.16, 0.4)
		tw.tween_interval(0.9)
		tw.tween_property(_ak_mag, "position:y", _ak_mag_rest.y, 0.45)


func _process_reload(delta: float) -> void:
	velocity.x = lerpf(velocity.x, 0.0, delta * 6.0)
	velocity.z = lerpf(velocity.z, 0.0, delta * 6.0)
	_reload_timer -= delta
	if _reload_timer <= 0.0:
		_ammo = ak_mag_size
		state = State.COMBAT


func _move_along_nav(delta: float, spd: float) -> void:
	if nav_agent == null or nav_agent.is_navigation_finished():
		velocity.x = lerpf(velocity.x, 0.0, delta * 8.0)
		velocity.z = lerpf(velocity.z, 0.0, delta * 8.0)
		return
	var next_pos := nav_agent.get_next_path_position()
	var dir := next_pos - global_position
	dir.y = 0.0
	if dir.length() > 0.05:
		dir = dir.normalized()
		velocity.x = lerpf(velocity.x, dir.x * spd, delta * 8.0)
		velocity.z = lerpf(velocity.z, dir.z * spd, delta * 8.0)
		if state != State.COMBAT:
			rotation.y = lerp_angle(rotation.y, atan2(-dir.x, -dir.z), delta * 6.0)


func _try_open_blocking_door() -> void:
	for i in get_slide_collision_count():
		var col := get_slide_collision(i).get_collider()
		if col and col.has_meta("hotel_door_owner"):
			var door = col.get_meta("hotel_door_owner")
			if door and not door.get("is_open") and door.has_method("set_open"):
				door.set_open(true)


func _check_player_visibility() -> bool:
	if _player == null or _player.get("is_dead") or los_ray == null:
		return false
	var eye_pos := global_position + Vector3(0.0, 1.48, 0.0)
	var target_pos := _player.global_position + Vector3(0.0, 1.28, 0.0)
	var to_target := target_pos - eye_pos
	var dist := to_target.length()
	if dist > detection_range:
		return false

	# Cono de visión (si ya está en combate detecta 360°)
	if state != State.COMBAT:
		var forward := -transform.basis.z
		var angle_deg := rad_to_deg(forward.angle_to(to_target.normalized()))
		if angle_deg > fov_degrees * 0.5:
			return false

	los_ray.global_position = eye_pos
	los_ray.target_position = los_ray.to_local(target_pos)
	los_ray.force_raycast_update()
	if los_ray.is_colliding():
		return los_ray.get_collider() == _player
	return false
