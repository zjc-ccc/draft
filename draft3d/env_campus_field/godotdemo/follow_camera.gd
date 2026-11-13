extends Camera3D
## 第三人称跟随相机：固定在火柴人的右后上方，始终看向头部

@export var target_path: NodePath = ^"../Player"
@export var offset_right := 0.050
@export var offset_back := 0.115
@export var offset_up := 0.085
@export var look_height := 0.050
@export var smooth := 14.0

var _target: Node3D


func _ready() -> void:
	near = 0.002            # 火柴人只有 0.065 高，近裁剪面要很小
	far = 400.0
	fov = 52.0
	_target = get_node_or_null(target_path)
	if _target == null:
		push_error("跟随目标不存在: " + str(target_path))
		return
	global_position = _want_position()
	_look_at_target()


func _process(delta: float) -> void:
	if _target == null:
		return
	global_position = global_position.lerp(_want_position(), 1.0 - exp(-smooth * delta))
	_look_at_target()


func _want_position() -> Vector3:
	var b := _target.global_transform.basis
	return _target.global_position + b.x * offset_right - b.z * offset_back + Vector3.UP * offset_up


func _look_at_target() -> void:
	look_at(_target.global_position + Vector3.UP * look_height, Vector3.UP)
