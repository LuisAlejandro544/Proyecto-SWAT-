# ShellCasing.gd
# Controla el casquillo metálico (protección del proyectil) expulsado tras cada disparo.
# Aplica físicas de rebote, giro en el aire, sonido metálico al chocar con el suelo
# y auto-eliminación para mantener fluido el rendimiento en móvil.

extends RigidBody3D

@export var lifetime_sec: float = 3.8

var _played_clink: bool = false


func _ready() -> void:
	contact_monitor = true
	max_contacts_reported = 2
	body_entered.connect(_on_body_entered)
	var timer := get_tree().create_timer(lifetime_sec)
	timer.timeout.connect(queue_free)


func launch(initial_velocity: Vector3, spin_velocity: Vector3) -> void:
	linear_velocity = initial_velocity
	angular_velocity = spin_velocity


func _on_body_entered(_body: Node) -> void:
	if _played_clink:
		return
	_played_clink = true
	AudioSynth.play_shell_clink_3d(global_position)
