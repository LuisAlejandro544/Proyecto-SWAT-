# HotelMissionManager.gd
# Controla el flujo completo de la Misión 1 (Asalto al Hotel de 2 pisos):
#   - Conteo de terroristas restantes
#   - Conexión entre jugador, HUD móvil, modal de pausa y pantallas de Victoria/Derrota.

extends Node3D

@onready var player: CharacterBody3D = $PlayerSWAT
@onready var hud: CanvasLayer = $MobileHUD
@onready var pause_panel: Control = $OverlayCanvas/PausePanel
@onready var result_panel: Control = $OverlayCanvas/ResultPanel
@onready var result_title: Label = $OverlayCanvas/ResultPanel/Card/VBox/ResultTitle
@onready var result_desc: Label = $OverlayCanvas/ResultPanel/Card/VBox/ResultDesc
@onready var btn_resume: Button = $OverlayCanvas/PausePanel/Card/VBox/BtnResume
@onready var btn_pause_retry: Button = $OverlayCanvas/PausePanel/Card/VBox/BtnRetry
@onready var btn_pause_menu: Button = $OverlayCanvas/PausePanel/Card/VBox/BtnMenu
@onready var btn_result_retry: Button = $OverlayCanvas/ResultPanel/Card/VBox/BtnRetry
@onready var btn_result_menu: Button = $OverlayCanvas/ResultPanel/Card/VBox/BtnMenu

var _total_terrorists: int = 0
var _remaining_terrorists: int = 0
var _mission_finished: bool = false
var _start_time_msec: int = 0


func _ready() -> void:
	_start_time_msec = Time.get_ticks_msec()
	if pause_panel:
		pause_panel.visible = false
	if result_panel:
		result_panel.visible = false

	var weapon := player.get_node_or_null("HeadPivot/Camera3D/WeaponM4")
	if hud and player:
		hud.bind_player(player, weapon)
		hud.pause_requested.connect(_on_pause_requested)
	if player:
		player.player_died.connect(_on_player_died)

	var terrorists := get_tree().get_nodes_in_group("terrorists")
	_total_terrorists = terrorists.size()
	_remaining_terrorists = _total_terrorists
	for t in terrorists:
		if t.has_signal("terrorist_neutralized"):
			t.terrorist_neutralized.connect(_on_terrorist_neutralized)

	if hud:
		hud.set_remaining_terrorists(_remaining_terrorists, _total_terrorists)

	if btn_resume:
		btn_resume.pressed.connect(_close_pause)
	if btn_pause_retry:
		btn_pause_retry.pressed.connect(_restart_mission)
	if btn_pause_menu:
		btn_pause_menu.pressed.connect(_go_to_menu)
	if btn_result_retry:
		btn_result_retry.pressed.connect(_restart_mission)
	if btn_result_menu:
		btn_result_menu.pressed.connect(_go_to_menu)


func _on_terrorist_neutralized(_t: Node3D) -> void:
	if _mission_finished:
		return
	_remaining_terrorists = maxi(0, _remaining_terrorists - 1)
	if hud:
		hud.set_remaining_terrorists(_remaining_terrorists, _total_terrorists)

	if _remaining_terrorists == 0:
		_show_result(true)


func _on_player_died() -> void:
	if _mission_finished:
		return
	_show_result(false)


func _show_result(victory: bool) -> void:
	_mission_finished = true
	var elapsed_s := int((Time.get_ticks_msec() - _start_time_msec) / 1000.0)
	var mins := elapsed_s / 60
	var secs := elapsed_s % 60
	if result_panel:
		result_panel.visible = true
	if result_title:
		result_title.text = "HOTEL DESPEJADO" if victory else "AGENTE CAÍDO"
		result_title.modulate = Color(0.35, 0.95, 0.55) if victory else Color(1.0, 0.35, 0.30)
	if result_desc:
		if victory:
			result_desc.text = "Misión 1 completada. Todos los terroristas neutralizados.\nTiempo táctico: %02d:%02d" % [mins, secs]
		else:
			result_desc.text = "Fuiste superado por el fuego enemigo.\nObjetivos restantes: %d" % _remaining_terrorists


func _on_pause_requested() -> void:
	if _mission_finished:
		return
	get_tree().paused = true
	if pause_panel:
		pause_panel.visible = true


func _close_pause() -> void:
	get_tree().paused = false
	if pause_panel:
		pause_panel.visible = false


func _restart_mission() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


func _go_to_menu() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn")
