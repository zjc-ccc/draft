extends Camera3D
## 第三人称越肩跟随（类似 PUBG）：相机位于火柴人左后上方；按 V 切换第一人称，可来回切

@export var target_path: NodePath = ^"../Player"
@export var shoulder_left := 0.28     # 相机向角色左侧偏移
@export var offset_back := 1.25       # 相机在身后多远
@export var offset_up := 0.80         # 相机相对脚底的高度（火柴人总高 0.583）
@export var aim_offset := Vector3(0.0, 0.10, -8.0)   # 瞄准点（角色局部坐标，-Z 为前）
@export var eye_height := 0.545       # 第一人称眼睛高度
@export var smooth := 14.0

var first_person := false
var _target: Node3D
var _head: Node3D


func _ready() -> void:
	near = 0.02             # 火柴人只有 0.583 高，近裁剪面要小
	far = 400.0
	fov = 52.0
	_target = get_node_or_null(target_path)
	if _target == null:
		push_error("跟随目标不存在: " + str(target_path))
		return
	_head = _find_head(_target.get_child(0))
	global_position = _want_position()
	_look_at_aim()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k: int = event.physical_keycode if event.physical_keycode != 0 else event.keycode
		if k == KEY_V or event.keycode == KEY_V:
			toggle_view()


func toggle_view() -> void:
	first_person = not first_person
	if _head:
		_head.visible = not first_person   # 第一人称隐藏头部，避免镜头被头球包住
	print("[camera] ", mode_text())


func mode_text() -> String:
	return "1P" if first_person else "3P"


func _process(delta: float) -> void:
	if _target == null:
		return
	global_position = global_position.lerp(_want_position(), 1.0 - exp(-smooth * delta))
	_look_at_aim()


func _want_position() -> Vector3:
	var b := _target.global_transform.basis
	if first_person:
		return _target.global_position + b * Vector3(0.0, eye_height, -0.02)
	# 角色正面是 -Z，所以 +basis.z 是身后；向左偏移走 -basis.x
	return _target.global_position + b.x * -shoulder_left + b.z * offset_back + Vector3.UP * offset_up


func _look_at_aim() -> void:
	var b := _target.global_transform.basis
	var dir := b * aim_offset
	if first_person:
		dir = b * Vector3(0.0, 0.0, -1.0)
		look_at(global_position + dir, Vector3.UP)
		return
	var up := Vector3.UP
	if absf(dir.normalized().dot(up)) > 0.99:
		up = Vector3.FORWARD
	look_at(global_position + dir, up)


func _find_head(n: Node) -> Node3D:
	for c in n.get_children():
		if c is MeshInstance3D and str(c.name).begins_with("Head"):
			return c
		if c is Node3D:
			var r := _find_head(c)
			if r:
				return r
	return null
