extends Camera3D
# 简易轨道相机：右键拖动旋转，滚轮缩放，围绕水面中心观察。

@export var target := Vector3(0.0, -0.25, 0.0)
@export var distance := 9.5
@export_range(1.0, 89.0) var elevation := 16.0
@export var yaw := 24.0
@export var min_distance := 2.5
@export var max_distance := 24.0

var _dragging := false


func _ready() -> void:
	_update_view()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_RIGHT or mb.button_index == MOUSE_BUTTON_LEFT:
			_dragging = mb.pressed
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = clampf(distance * 0.92, min_distance, max_distance)
			_update_view()
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = clampf(distance * 1.08, min_distance, max_distance)
			_update_view()
	elif event is InputEventMouseMotion and _dragging:
		var mm := event as InputEventMouseMotion
		yaw -= mm.relative.x * 0.25
		elevation = clampf(elevation + mm.relative.y * 0.20, 2.0, 89.0)
		_update_view()


func _update_view() -> void:
	var y := deg_to_rad(yaw)
	var e := deg_to_rad(elevation)
	var offset := Vector3(cos(e) * sin(y), sin(e), cos(e) * cos(y)) * distance
	global_position = target + offset
	look_at(target, Vector3.UP)
