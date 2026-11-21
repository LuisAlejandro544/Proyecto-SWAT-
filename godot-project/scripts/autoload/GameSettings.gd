# GameSettings.gd
# Autoload encargado de guardar y cargar las preferencias del jugador para móvil
# (sensibilidad táctil, volumen, inversión de eje Y, tamaño del joystick) usando ConfigFile.

extends Node

const SETTINGS_PATH := "user://swat_hotel_settings.cfg"

var look_sensitivity: float = 0.28
var ads_sensitivity_multiplier: float = 0.55
var master_volume_db: float = -4.0
var invert_y: bool = false
var joystick_scale: float = 1.0
var auto_sprint: bool = true

signal settings_changed


func _ready() -> void:
	load_settings()
	_apply_audio_volume()


func load_settings() -> void:
	var cfg := ConfigFile.new()
	if cfg.load(SETTINGS_PATH) != OK:
		return
	look_sensitivity = float(cfg.get_value("controls", "look_sensitivity", look_sensitivity))
	ads_sensitivity_multiplier = float(cfg.get_value("controls", "ads_sensitivity_multiplier", ads_sensitivity_multiplier))
	invert_y = bool(cfg.get_value("controls", "invert_y", invert_y))
	joystick_scale = float(cfg.get_value("controls", "joystick_scale", joystick_scale))
	auto_sprint = bool(cfg.get_value("controls", "auto_sprint", auto_sprint))
	master_volume_db = float(cfg.get_value("audio", "master_volume_db", master_volume_db))


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.set_value("controls", "look_sensitivity", look_sensitivity)
	cfg.set_value("controls", "ads_sensitivity_multiplier", ads_sensitivity_multiplier)
	cfg.set_value("controls", "invert_y", invert_y)
	cfg.set_value("controls", "joystick_scale", joystick_scale)
	cfg.set_value("controls", "auto_sprint", auto_sprint)
	cfg.set_value("audio", "master_volume_db", master_volume_db)
	cfg.save(SETTINGS_PATH)
	_apply_audio_volume()
	settings_changed.emit()


func _apply_audio_volume() -> void:
	var master_idx := AudioServer.get_bus_index("Master")
	if master_idx >= 0:
		AudioServer.set_bus_volume_db(master_idx, master_volume_db)
