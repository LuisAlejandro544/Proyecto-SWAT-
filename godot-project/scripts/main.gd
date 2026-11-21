# main.gd
# Lógica inicial de la escena Hello World en Godot 4.7.2-stable.
# Este script verifica que el motor arranque correctamente en WebAssembly y muestra el mensaje base.

extends Node3D

@onready var titulo_label: Label = $CanvasLayer/CenterContainer/VBoxContainer/TituloLabel
@onready var subtitulo_label: Label = $CanvasLayer/CenterContainer/VBoxContainer/SubtituloLabel

func _ready() -> void:
	# Configura los textos iniciales en pantalla al arrancar el motor.
	titulo_label.text = "Hello World"
	subtitulo_label.text = "Godot %s · Entorno Web listo" % Engine.get_version_info().string
	print("Hello World desde Godot ", Engine.get_version_info().string)
