# ControlsGuideScreen.gd
# Pantalla separada con la guía visual de controles móviles para el agente SWAT.

extends Control

@onready var btn_back: Button = $CenterPanel/Card/VBox/BtnBack


func _ready() -> void:
	if btn_back:
		btn_back.pressed.connect(func():
			get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn")
		)
