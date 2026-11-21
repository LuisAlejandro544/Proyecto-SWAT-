# SettingsScreen.gd
# Pantalla dedicada de ajustes para comodidad móvil:
# sensibilidad de cámara táctil, multiplicador al apuntar (ADS), tamaño de joystick,
# inversión del eje Y, sprint automático y volumen maestro.

extends Control

@onready var slider_sens: HSlider = $CenterPanel/Card/VBox/SensRow/SensSlider
@onready var lbl_sens: Label = $CenterPanel/Card/VBox/SensRow/SensValue
@onready var slider_joy: HSlider = $CenterPanel/Card/VBox/JoyRow/JoySlider
@onready var lbl_joy: Label = $CenterPanel/Card/VBox/JoyRow/JoyValue
@onready var slider_vol: HSlider = $CenterPanel/Card/VBox/VolRow/VolSlider
@onready var lbl_vol: Label = $CenterPanel/Card/VBox/VolRow/VolValue
@onready var chk_invert_y: CheckButton = $CenterPanel/Card/VBox/InvertYCheck
@onready var chk_auto_sprint: CheckButton = $CenterPanel/Card/VBox/AutoSprintCheck
@onready var btn_back: Button = $CenterPanel/Card/VBox/ButtonsRow/BtnBack
@onready var btn_save: Button = $CenterPanel/Card/VBox/ButtonsRow/BtnSave


func _ready() -> void:
	slider_sens.value = GameSettings.look_sensitivity
	slider_joy.value = GameSettings.joystick_scale
	slider_vol.value = GameSettings.master_volume_db
	chk_invert_y.button_pressed = GameSettings.invert_y
	chk_auto_sprint.button_pressed = GameSettings.auto_sprint
	_refresh_labels()

	slider_sens.value_changed.connect(func(_v): _refresh_labels())
	slider_joy.value_changed.connect(func(_v): _refresh_labels())
	slider_vol.value_changed.connect(func(_v): _refresh_labels())

	btn_save.pressed.connect(func():
		GameSettings.look_sensitivity = slider_sens.value
		GameSettings.joystick_scale = slider_joy.value
		GameSettings.master_volume_db = slider_vol.value
		GameSettings.invert_y = chk_invert_y.button_pressed
		GameSettings.auto_sprint = chk_auto_sprint.button_pressed
		GameSettings.save_settings()
		get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn")
	)
	btn_back.pressed.connect(func():
		get_tree().change_scene_to_file("res://scenes/ui/MainMenu.tscn")
	)


func _refresh_labels() -> void:
	lbl_sens.text = "%.2f" % slider_sens.value
	lbl_joy.text = "%d%%" % int(roundf(slider_joy.value * 100.0))
	lbl_vol.text = "%d dB" % int(roundf(slider_vol.value))
