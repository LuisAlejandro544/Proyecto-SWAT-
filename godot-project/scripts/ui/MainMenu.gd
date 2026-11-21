# MainMenu.gd
# Pantalla principal del juego móvil SWAT: Asalto al Hotel.
# Navega hacia la Misión 1, la pantalla de Ajustes Táctiles o la Guía de Controles.

extends Control

@onready var btn_play: Button = $Layout/RightColumn/MissionCard/VBox/BtnStartMission
@onready var btn_controls: Button = $Layout/LeftColumn/MenuButtons/BtnControls
@onready var btn_settings: Button = $Layout/LeftColumn/MenuButtons/BtnSettings
@onready var btn_quit: Button = $Layout/LeftColumn/MenuButtons/BtnQuit


func _ready() -> void:
	if btn_play:
		btn_play.pressed.connect(func():
			get_tree().change_scene_to_file("res://scenes/levels/HotelMission01.tscn")
		)
	if btn_controls:
		btn_controls.pressed.connect(func():
			get_tree().change_scene_to_file("res://scenes/ui/ControlsGuideScreen.tscn")
		)
	if btn_settings:
		btn_settings.pressed.connect(func():
			get_tree().change_scene_to_file("res://scenes/ui/SettingsScreen.tscn")
		)
	if btn_quit:
		btn_quit.pressed.connect(func(): get_tree().quit())
