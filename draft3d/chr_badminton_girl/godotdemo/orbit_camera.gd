extends Camera3D
## 简单的环绕相机：左键拖拽旋转，滚轮缩放

var target := Vector3(0.0, 0.85, 0.0)
var distance := 3.0
var yaw := 20.0
var pitch := -8.0

var _dragging := false


func _ready() -> void:
	_update_transform()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_LEFT:
			_dragging = mb.pressed
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = clampf(distance - 0.2, 1.0, 8.0)
			_update_transform()
		elif mb.pressed and mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = clampf(distance + 0.2, 1.0, 8.0)
			_update_transform()
	elif event is InputEventMouseMotion and _dragging:
		var mm := event as InputEventMouseMotion
		yaw -= mm.relative.x * 0.3
		pitch = clampf(pitch - mm.relative.y * 0.25, -70.0, 35.0)
		_update_transform()


func _update_transform() -> void:
	var yr := deg_to_rad(yaw)
	var pr := deg_to_rad(pitch)
	var offset := Vector3(
		cos(pr) * sin(yr),
		-sin(pr),
		cos(pr) * cos(yr)
	) * distance
	position = target + offset
	look_at(target, Vector3.UP)
