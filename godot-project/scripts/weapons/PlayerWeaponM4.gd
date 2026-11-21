# PlayerWeaponM4.gd
# Controlador completo de la carabina táctica M4 para el agente SWAT.
# Implementa las 5 animaciones solicitadas sobre la jerarquía real de m4.glb:
#   1. Animación de arma (respiración, balanceo al caminar/correr, lag de cámara y apuntado ADS)
#   2. Animación de disparo (retroceso del arma, retroceso del cerrojo M4_Bolt y elevación de cámara)
#   3. Animación de fogonazo (destello 3D en MuzzlePoint + luz puntual instantánea)
#   4. Animación de recarga (inclinación táctica, extracción/inserción de M4_Magazine y M4_ChargingHandle)
#   5. Animación de casquillos cayéndose (expulsión física de shell_casing.glb desde EjectionPort)

extends Node3D

signal ammo_changed(mag_ammo: int, reserve_ammo: int, is_reloading: bool)
signal shot_fired(hit_info: Dictionary)

@export_group("Estadísticas M4")
@export var mag_capacity: int = 30
@export var reserve_ammo: int = 150
@export var fire_rate_rps: float = 11.0
@export var base_damage: float = 34.0
@export var headshot_multiplier: float = 2.2
@export var reload_duration: float = 1.85

@export_group("Poses del Arma")
@export var hip_pos: Vector3 = Vector3(0.21, -0.20, -0.36)
@export var ads_pos: Vector3 = Vector3(0.0, -0.145, -0.26)
@export var sprint_rot_deg: Vector3 = Vector3(-10.0, 22.0, 8.0)

@export_group("Escenas")
@export var shell_casing_scene: PackedScene

@onready var m4_model: Node3D = $M4Model
@onready var muzzle_flash_root: Node3D = $MuzzleFlashRoot
@onready var muzzle_light: OmniLight3D = $MuzzleFlashRoot/MuzzleLight
@onready var flash_mesh_a: MeshInstance3D = $MuzzleFlashRoot/FlashStarA
@onready var flash_mesh_b: MeshInstance3D = $MuzzleFlashRoot/FlashStarB

var _bolt_node: Node3D
var _charging_handle_node: Node3D
var _magazine_node: Node3D
var _muzzle_point: Node3D
var _ejection_port: Node3D

var _bolt_rest_pos: Vector3 = Vector3.ZERO
var _ch_rest_pos: Vector3 = Vector3.ZERO
var _mag_rest_pos: Vector3 = Vector3.ZERO
var _mag_rest_rot: Vector3 = Vector3.ZERO

var current_ammo: int = 30
var is_reloading: bool = false
var is_ads: bool = false

var _fire_cooldown: float = 0.0
var _flash_timer: float = 0.0
var _bolt_kick: float = 0.0
var _recoil_offset: Vector3 = Vector3.ZERO
var _recoil_rot: Vector3 = Vector3.ZERO
var _sway_time: float = 0.0
var _look_sway: Vector2 = Vector2.ZERO

var _reload_elapsed: float = 0.0
var _reload_stage_flags: int = 0
var _rng := RandomNumberGenerator.new()

var player_body: CharacterBody3D
var aim_ray: RayCast3D
var camera_node: Camera3D


func _ready() -> void:
	_rng.randomize()
	current_ammo = mag_capacity
	_cache_m4_parts()
	_hide_muzzle_flash()
	position = hip_pos
	ammo_changed.emit(current_ammo, reserve_ammo, is_reloading)


func setup_references(p_body: CharacterBody3D, p_cam: Camera3D, p_ray: RayCast3D) -> void:
	player_body = p_body
	camera_node = p_cam
	aim_ray = p_ray


func _cache_m4_parts() -> void:
	if m4_model == null:
		return
	_bolt_node = m4_model.find_child("M4_Bolt", true, false) as Node3D
	_charging_handle_node = m4_model.find_child("M4_ChargingHandle", true, false) as Node3D
	_magazine_node = m4_model.find_child("M4_Magazine", true, false) as Node3D
	_muzzle_point = m4_model.find_child("MuzzlePoint", true, false) as Node3D
	_ejection_port = m4_model.find_child("EjectionPort", true, false) as Node3D

	if _bolt_node:
		_bolt_rest_pos = _bolt_node.position
	if _charging_handle_node:
		_ch_rest_pos = _charging_handle_node.position
	if _magazine_node:
		_mag_rest_pos = _magazine_node.position
		_mag_rest_rot = _magazine_node.rotation


func add_look_sway(delta_look: Vector2) -> void:
	_look_sway = (_look_sway + delta_look * 0.0022).clamp(Vector2(-0.025, -0.02), Vector2(0.025, 0.02))


func set_ads(enabled: bool) -> void:
	if is_reloading:
		is_ads = false
		return
	is_ads = enabled


func try_fire(wants_fire: bool) -> void:
	if not wants_fire or is_reloading or _fire_cooldown > 0.0:
		return
	if current_ammo <= 0:
		start_reload()
		return
	_execute_shot()


func start_reload() -> void:
	if is_reloading or current_ammo >= mag_capacity or reserve_ammo <= 0:
		return
	is_reloading = true
	is_ads = false
	_reload_elapsed = 0.0
	_reload_stage_flags = 0
	ammo_changed.emit(current_ammo, reserve_ammo, true)


func _process(delta: float) -> void:
	_fire_cooldown = maxf(0.0, _fire_cooldown - delta)

	# Temporizador del destello de fogonazo (3)
	if _flash_timer > 0.0:
		_flash_timer -= delta
		if _flash_timer <= 0.0:
			_hide_muzzle_flash()

	# Recuperación del retroceso del disparo (2) y del cerrojo
	_recoil_offset = _recoil_offset.lerp(Vector3.ZERO, minf(1.0, delta * 18.0))
	_recoil_rot = _recoil_rot.lerp(Vector3.ZERO, minf(1.0, delta * 16.0))
	_bolt_kick = lerpf(_bolt_kick, 0.0, minf(1.0, delta * 28.0))
	_look_sway = _look_sway.lerp(Vector2.ZERO, minf(1.0, delta * 10.0))

	if _bolt_node:
		# En Godot, atrás es +Z porque el modelo apunta hacia -Z
		_bolt_node.position = _bolt_rest_pos + Vector3(0.0, 0.0, _bolt_kick)

	# 1. Animación de movimiento del arma (respiración + caminar + ADS)
	var speed := 0.0
	var is_on_floor := true
	if player_body:
		var horiz := Vector2(player_body.velocity.x, player_body.velocity.z)
		speed = horiz.length()
		is_on_floor = player_body.is_on_floor()

	_sway_time += delta * (1.8 + speed * 1.65)
	var bob_amp := (0.0022 if is_ads else 0.0085) * clampf(speed / 4.5, 0.0, 1.3)
	if not is_on_floor:
		bob_amp *= 0.25
	var idle_amp := 0.0008 if is_ads else 0.0026

	var bob_offset := Vector3(
		cos(_sway_time * 0.5) * bob_amp + sin(Time.get_ticks_msec() * 0.0018) * idle_amp - _look_sway.x,
		absf(sin(_sway_time)) * bob_amp + cos(Time.get_ticks_msec() * 0.0024) * idle_amp + _look_sway.y,
		0.0
	)

	var target_base_pos := ads_pos if is_ads else hip_pos
	var target_rot := Vector3.ZERO

	# Inclinación al correr rápido cuando no se apunta
	if speed > 4.9 and not is_ads and not is_reloading:
		target_rot = Vector3(
			deg_to_rad(sprint_rot_deg.x),
			deg_to_rad(sprint_rot_deg.y),
			deg_to_rad(sprint_rot_deg.z)
		)
		target_base_pos += Vector3(-0.02, -0.025, 0.03)

	# 4. Animación de recarga por etapas sobre cargador y palanca de carga
	if is_reloading:
		_update_reload_animation(delta)
		return

	var final_pos := target_base_pos + bob_offset + _recoil_offset
	var final_rot := target_rot + _recoil_rot + Vector3(_look_sway.y * 1.4, -_look_sway.x * 1.8, -_look_sway.x * 1.2)

	position = position.lerp(final_pos, minf(1.0, delta * (16.0 if is_ads else 12.0)))
	rotation = rotation.lerp(final_rot, minf(1.0, delta * 14.0))


func _execute_shot() -> void:
	_fire_cooldown = 1.0 / fire_rate_rps
	current_ammo -= 1
	ammo_changed.emit(current_ammo, reserve_ammo, false)

	# Sonido de disparo
	AudioSynth.play_m4_shot()

	# 2. Retroceso del arma y ciclo del cerrojo
	var kick_scale := 0.55 if is_ads else 1.0
	_recoil_offset += Vector3(
		_rng.randf_range(-0.004, 0.004) * kick_scale,
		0.006 * kick_scale,
		0.042 * kick_scale
	)
	_recoil_rot += Vector3(
		deg_to_rad(_rng.randf_range(2.2, 3.6) * kick_scale),
		deg_to_rad(_rng.randf_range(-0.8, 0.8) * kick_scale),
		deg_to_rad(_rng.randf_range(-1.6, 1.6) * kick_scale)
	)
	_bolt_kick = 0.048

	if player_body and player_body.has_method("apply_camera_recoil"):
		player_body.apply_camera_recoil(
			_rng.randf_range(1.1, 1.65) * kick_scale,
			_rng.randf_range(-0.45, 0.45) * kick_scale
		)

	# 3. Fogonazo del cañón
	_trigger_muzzle_flash()

	# 5. Expulsión de casquillo físico
	_eject_shell_casing()

	# Detección de impacto con RayCast3D
	var hit_info := _perform_ballistic_raycast()
	shot_fired.emit(hit_info)

	if current_ammo == 0 and reserve_ammo > 0:
		# Recarga automática cómoda para móvil al vaciar cargador
		get_tree().create_timer(0.18).timeout.connect(func():
			if is_instance_valid(self) and current_ammo == 0 and not is_reloading:
				start_reload()
		)


func _trigger_muzzle_flash() -> void:
	if muzzle_flash_root == null:
		return
	if _muzzle_point:
		muzzle_flash_root.global_transform = _muzzle_point.global_transform
	muzzle_flash_root.visible = true
	muzzle_flash_root.rotation.z = _rng.randf_range(0.0, TAU)
	var s := _rng.randf_range(0.85, 1.35)
	muzzle_flash_root.scale = Vector3(s, s, s * _rng.randf_range(0.9, 1.4))
	if muzzle_light:
		muzzle_light.light_energy = _rng.randf_range(3.5, 5.2)
	_flash_timer = 0.048


func _hide_muzzle_flash() -> void:
	if muzzle_flash_root:
		muzzle_flash_root.visible = false
	if muzzle_light:
		muzzle_light.light_energy = 0.0


func _eject_shell_casing() -> void:
	if shell_casing_scene == null or _ejection_port == null:
		return
	var level_root := get_tree().current_scene
	if level_root == null:
		return

	var casing := shell_casing_scene.instantiate() as RigidBody3D
	if casing == null:
		return
	level_root.add_child(casing)
	casing.global_transform = _ejection_port.global_transform
	casing.rotate_object_local(Vector3.UP, _rng.randf_range(-0.2, 0.2))

	# Dirección de expulsión hacia la derecha y arriba de la cámara
	var right_dir := _ejection_port.global_transform.basis.x.normalized()
	var up_dir := _ejection_port.global_transform.basis.y.normalized()
	var back_dir := _ejection_port.global_transform.basis.z.normalized()

	var eject_vel := (
		right_dir * _rng.randf_range(2.2, 3.1)
		+ up_dir * _rng.randf_range(1.6, 2.4)
		+ back_dir * _rng.randf_range(0.3, 0.8)
	)
	if player_body:
		eject_vel += player_body.velocity * 0.45

	var spin := Vector3(
		_rng.randf_range(-28.0, 28.0),
		_rng.randf_range(-22.0, 22.0),
		_rng.randf_range(-30.0, 30.0)
	)
	if casing.has_method("launch"):
		casing.launch(eject_vel, spin)


func _update_reload_animation(delta: float) -> void:
	_reload_elapsed += delta
	var t := clampf(_reload_elapsed / reload_duration, 0.0, 1.0)

	# Pose general del rifle durante la recarga (inclinación táctica lateral)
	var tilt_weight := sin(t * PI)
	var reload_pos := hip_pos + Vector3(-0.04 * tilt_weight, -0.045 * tilt_weight, 0.04 * tilt_weight)
	var reload_rot := Vector3(
		deg_to_rad(14.0 * tilt_weight),
		deg_to_rad(28.0 * tilt_weight),
		deg_to_rad(-24.0 * tilt_weight)
	)
	position = position.lerp(reload_pos, minf(1.0, delta * 14.0))
	rotation = rotation.lerp(reload_rot, minf(1.0, delta * 14.0))

	# Etapa 1 (0.00 -> 0.35): Extraer cargador vacío hacia abajo
	if t < 0.35:
		var p := t / 0.35
		if (_reload_stage_flags & 1) == 0:
			_reload_stage_flags |= 1
			AudioSynth.play_mag_out()
		if _magazine_node:
			_magazine_node.position = _mag_rest_pos + Vector3(0.0, -0.22 * p, 0.02 * p)
			_magazine_node.rotation = _mag_rest_rot + Vector3(deg_to_rad(-18.0 * p), 0.0, 0.0)
			_magazine_node.visible = p < 0.92
	# Etapa 2 (0.35 -> 0.65): Insertar cargador lleno nuevo
	elif t < 0.65:
		var p := (t - 0.35) / 0.30
		if _magazine_node:
			_magazine_node.visible = true
			var ease_p := 1.0 - pow(1.0 - p, 2.0)
			_magazine_node.position = _mag_rest_pos + Vector3(0.0, -0.22 * (1.0 - ease_p), 0.02 * (1.0 - ease_p))
			_magazine_node.rotation = _mag_rest_rot + Vector3(deg_to_rad(-18.0 * (1.0 - ease_p)), 0.0, 0.0)
		if p > 0.85 and (_reload_stage_flags & 2) == 0:
			_reload_stage_flags |= 2
			AudioSynth.play_mag_in()
	# Etapa 3 (0.65 -> 0.92): Tirar de la palanca de carga trasera (Charging Handle)
	elif t < 0.92:
		if _magazine_node:
			_magazine_node.position = _mag_rest_pos
			_magazine_node.rotation = _mag_rest_rot
		var p := (t - 0.65) / 0.27
		if p > 0.1 and (_reload_stage_flags & 4) == 0:
			_reload_stage_flags |= 4
			AudioSynth.play_bolt_rack()
		var pull := sin(p * PI)
		if _charging_handle_node:
			_charging_handle_node.position = _ch_rest_pos + Vector3(0.0, 0.0, 0.072 * pull)
		if _bolt_node:
			_bolt_node.position = _bolt_rest_pos + Vector3(0.0, 0.0, 0.055 * pull)
	else:
		if _charging_handle_node:
			_charging_handle_node.position = _ch_rest_pos
		if _bolt_node:
			_bolt_node.position = _bolt_rest_pos

	if t >= 1.0:
		_finish_reload()


func _finish_reload() -> void:
	is_reloading = false
	if _magazine_node:
		_magazine_node.visible = true
		_magazine_node.position = _mag_rest_pos
		_magazine_node.rotation = _mag_rest_rot
	if _charging_handle_node:
		_charging_handle_node.position = _ch_rest_pos
	if _bolt_node:
		_bolt_node.position = _bolt_rest_pos

	var needed := mag_capacity - current_ammo
	var loaded := mini(needed, reserve_ammo)
	current_ammo += loaded
	reserve_ammo -= loaded
	ammo_changed.emit(current_ammo, reserve_ammo, false)


func _perform_ballistic_raycast() -> Dictionary:
	var result := {"hit": false, "enemy": false, "headshot": false, "killed": false}
	if aim_ray == null:
		return result

	# Dispersión leve si dispara sin apuntar (ADS es muy preciso)
	var spread_deg := 0.25 if is_ads else 1.45
	aim_ray.rotation_degrees = Vector3(
		_rng.randf_range(-spread_deg, spread_deg),
		_rng.randf_range(-spread_deg, spread_deg),
		0.0
	)
	aim_ray.force_raycast_update()

	if not aim_ray.is_colliding():
		return result

	result.hit = true
	var collider := aim_ray.get_collider()
	var hit_pos := aim_ray.get_collision_point()
	var hit_normal := aim_ray.get_collision_normal()

	# Detectar impacto sobre hitbox de terrorista
	if collider and collider.has_meta("terrorist_owner"):
		var terrorist = collider.get_meta("terrorist_owner")
		var is_head := bool(collider.get_meta("is_headshot", false))
		var dmg := base_damage * (headshot_multiplier if is_head else 1.0)
		result.enemy = true
		result.headshot = is_head
		if terrorist and terrorist.has_method("apply_damage"):
			result.killed = terrorist.apply_damage(dmg, hit_pos, is_head)
		AudioSynth.play_hitmarker(is_head)
		_spawn_impact_spark(hit_pos, hit_normal, Color(0.95, 0.2, 0.15))
	else:
		_spawn_impact_spark(hit_pos, hit_normal, Color(1.0, 0.85, 0.45))

	# Alertar a terroristas cercanos por el sonido del disparo
	if player_body:
		get_tree().call_group("terrorists", "on_gunshot_heard", player_body.global_position, 24.0)

	return result


func _spawn_impact_spark(pos: Vector3, normal: Vector3, color: Color) -> void:
	var level := get_tree().current_scene
	if level == null:
		return
	var spark := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.055, 0.055, 0.055)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = color
	box.material = mat
	spark.mesh = box
	level.add_child(spark)
	spark.global_position = pos + normal * 0.03
	var tw := spark.create_tween()
	tw.tween_property(spark, "scale", Vector3.ZERO, 0.18)
	tw.tween_callback(spark.queue_free)
