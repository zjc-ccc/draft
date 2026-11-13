extends Node3D
## 火柴人第三人称控制：W/S 前后移动，A/D 左右转身，Shift 加速
## 火柴人高 0.0646 场景单位（跑道 7.6 单位 = 200 m，即 1.7 m）

const MODEL_PATH := "res://assets/stickman_white.glb"
const GROUND_Y := 0.312          # 跑道面 0.312、草皮 0.308，取高的以免陷进跑道
const WALK_SPEED := 0.22         # 场景单位/秒，约 5.8 m/s
const SPRINT_SPEED := 0.42       # 约 11 m/s
const TURN_SPEED := 2.2          # 弧度/秒
const HALF_BOUND := 5.35         # 底座半宽 6.0，留一点边

var _model: Node3D


func _ready() -> void:
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("火柴人加载失败: " + MODEL_PATH)
		return
	_model = packed.instantiate()
	# glb 中脚掌朝 -Z，正好是 Godot 的前方，不需要额外旋转
	add_child(_model)
	global_position.y = GROUND_Y


func _process(delta: float) -> void:
	var turn := 0.0
	if Input.is_key_pressed(KEY_A):
		turn += 1.0
	if Input.is_key_pressed(KEY_D):
		turn -= 1.0
	if turn != 0.0:
		rotate_y(turn * TURN_SPEED * delta)

	var move := 0.0
	if Input.is_key_pressed(KEY_W):
		move += 1.0
	if Input.is_key_pressed(KEY_S):
		move -= 1.0
	if move != 0.0:
		var speed := SPRINT_SPEED if Input.is_key_pressed(KEY_SHIFT) else WALK_SPEED
		global_position += -global_transform.basis.z * move * speed * delta
		global_position.x = clampf(global_position.x, -HALF_BOUND, HALF_BOUND)
		global_position.z = clampf(global_position.z, -HALF_BOUND, HALF_BOUND)
		global_position.y = GROUND_Y
