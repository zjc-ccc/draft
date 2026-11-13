extends Node3D
## 火柴人第三人称控制：W/S 前后移动，A/D 左右转身，Shift 加速
## 火柴人高 0.0646 场景单位（1.7 m）；地面高度按城市分区解析求出

const MODEL_PATH := "res://assets/stickman_white.glb"
const WALK_SPEED := 0.22         # 场景单位/秒
const SPRINT_SPEED := 0.42
const TURN_SPEED := 2.2          # 弧度/秒
const HALF_BOUND := 5.75         # 底座半宽 6.0

# 城市地面（Godot 坐标：z = -Blender y）
const ROAD_X := 1.10             # 南北向道路半宽
const ROAD_Z := 1.30             # 东西向道路半宽
const H_ROAD := 0.304            # 车行道
const H_PAVE := 0.358            # 人行道 / 街区地坪
const H_PLAZA := 0.371           # 广场圆形铺装
const PLAZA_C := Vector2(3.35, -3.40)
const PLAZA_R := 1.44

var _model: Node3D


func _ready() -> void:
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("火柴人加载失败: " + MODEL_PATH)
		return
	_model = packed.instantiate()
	# glb 中脚掌朝 -Z，正好是 Godot 的前方，不需要额外旋转
	add_child(_model)
	global_position.y = ground_height(global_position.x, global_position.z)


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
		global_position.y = ground_height(global_position.x, global_position.z)


func ground_height(x: float, z: float) -> float:
	if absf(x) <= ROAD_X or absf(z) <= ROAD_Z:
		return H_ROAD
	if Vector2(x, z).distance_to(PLAZA_C) <= PLAZA_R:
		return H_PLAZA
	return H_PAVE
