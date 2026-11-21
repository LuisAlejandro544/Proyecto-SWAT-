# HotelArchitecture.gd
# Coordina el horneado diferido del NavigationMesh sobre la arquitectura estática del
# Gran Hotel Corona importada desde Blender (res://assets/models/hotel_building.glb) y su
# mobiliario complementario dentro de NavigationRegion3D.
# Nota: Toda la geometría 3D, texturas PBR empaquetadas y colisionadores (-col) del hotel
# residen directamente en el modelo .glb generado por blender-scripts/models/build_hotel_building.py.

extends Node3D

@export var nav_region: NavigationRegion3D


func _ready() -> void:
	_bake_navigation_deferred()


func _bake_navigation_deferred() -> void:
	if nav_region == null:
		return
	call_deferred("_do_bake_nav")


func _do_bake_nav() -> void:
	if nav_region and nav_region.navigation_mesh:
		nav_region.bake_navigation_mesh(false)
