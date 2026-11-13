extends Node3D
## 火柴人第三人称控制：W/S 移动，A/D 转身，Shift 加速，Space 跳跃，E / 左键 挥手
## 取餐 / 交付由 delivery.gd 的 F 键处理
## 身高 0.583 场景单位（马路 2.4 单位 = 7 m，即 1.7 m）
## 无物理方案：按区域解析式计算地面高度，可走桥面 / 平台 / 楼梯 / 人行道 / 马路 / 绿化带

const MODEL_PATH := "res://assets/stickman_white.glb"
const DECK_Y := 1.45             # 桥面高度
const SIDEWALK_Y := 0.37         # 人行道顶面
const ROAD_Y := 0.304            # 柏油马路面
const PROMENADE_Y := 0.35        # 滨河步道
const BELT_Y := 0.40             # 绿化带草面
const BASE_HALF_X := 8.0         # 底座半宽 16 × 12（X 向沿马路延长）
const BASE_HALF_Z := 6.0
const SHOP_X0 := -7.30           # 外卖店实体范围（Blender -Y 端 → Godot +Z）
const SHOP_X1 := -4.50
const SHOP_Z0 := 5.06
const MAX_STEP := 0.22           # 可迈上的最大高差，挡住从马路直接跳上楼梯侧面
const WALK_SPEED := 0.48         # 场景单位/秒，约 1.4 m/s
const SPRINT_SPEED := 1.03       # 约 3.0 m/s
const TURN_SPEED := 2.2          # 弧度/秒
const JUMP_SPEED := 1.9          # 起跳初速，跳起约 0.39 单位
const GRAVITY := 4.6
const WAVE_FRAMES := 49          # wave 片段帧数（24 fps）
const ANIM_FPS := 24.0

var _model: Node3D
var _anim: AnimationPlayer
var _grounded := true
var _vy := 0.0
var _waving := false
var _wave_t := 0.0


func _ready() -> void:
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("火柴人加载失败: " + MODEL_PATH)
		return
	_model = packed.instantiate()
	add_child(_model)
	global_position.y = DECK_Y

	_anim = _model.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _anim == null:
		push_error("动画播放器缺失")
		return
	_setup_anims()
	if not _anim.has_animation("wave"):
		push_error("火柴人动画缺失，请重新导入 assets/stickman_white.glb，现有：" + str(_anim.get_animation_list()))
	_play("idle")


func _setup_anims() -> void:
	for name in ["idle", "walk", "run"]:
		var a := _anim.get_animation(name)
		if a:
			a.loop_mode = Animation.LOOP_LINEAR
	for name in ["jump", "wave"]:
		var a := _anim.get_animation(name)
		if a:
			a.loop_mode = Animation.LOOP_NONE


func _play(name: String) -> void:
	if _anim == null or not _anim.has_animation(name):
		return
	if _anim.current_animation == name:
		return
	_anim.play(name, 0.12)


func _unhandled_input(event: InputEvent) -> void:
	# 事件驱动的离散动作：比每帧轮询更可靠，也不受输入法拦截文本键影响
	if event is InputEventKey:
		if not event.pressed or event.echo:
			return
		var k: int = event.physical_keycode if event.physical_keycode != 0 else event.keycode
		if k == KEY_SPACE or event.keycode == KEY_SPACE:
			_try_jump()
		elif k == KEY_E or event.keycode == KEY_E:
			_try_wave()
	elif event is InputEventMouseButton:
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			_try_wave()


func _try_jump() -> void:
	if not _grounded or _anim == null:
		return
	_grounded = false
	_vy = JUMP_SPEED
	_waving = false
	_play("jump")
	print("[stickman] jump")


func _try_wave() -> void:
	if not _grounded or _waving or _anim == null:
		return
	_waving = true
	_wave_t = WAVE_FRAMES / ANIM_FPS
	_play("wave")
	print("[stickman] wave")


func current_anim() -> String:
	if _anim == null:
		return "无动画"
	return _anim.current_animation


func _process(delta: float) -> void:
	var turn := 0.0
	if Input.is_key_pressed(KEY_A):
		turn += 1.0
	if Input.is_key_pressed(KEY_D):
		turn -= 1.0
	if turn != 0.0:
		rotate_y(turn * TURN_SPEED * delta)
		_waving = false

	var move := 0.0
	if Input.is_key_pressed(KEY_W):
		move += 1.0
	if Input.is_key_pressed(KEY_S):
		move -= 1.0
	if move != 0.0:
		_waving = false

	if _waving:
		_wave_t -= delta
		if _wave_t <= 0.0 or move != 0.0:
			_waving = false

	if move != 0.0:
		var speed := SPRINT_SPEED if Input.is_key_pressed(KEY_SHIFT) else WALK_SPEED
		_try_move(-global_transform.basis.z * move * speed * delta)

	var gy := _ground_at(global_position.x, global_position.z, global_position.y)
	if is_nan(gy):
		gy = DECK_Y          # 兜底：正常不会发生，移动已被 _can_stand 拦住
	if not _grounded:
		_vy -= GRAVITY * delta
		global_position.y += _vy * delta
		if global_position.y <= gy:
			global_position.y = gy
			_vy = 0.0
			_grounded = true
	else:
		# 贴地：楼梯是离散踏步，用平滑跟随消除 0.12 的台阶跳动
		global_position.y = lerpf(global_position.y, gy, 1.0 - exp(-18.0 * delta))
		if absf(global_position.y - gy) < 0.001:
			global_position.y = gy

	_update_anim(move, Input.is_key_pressed(KEY_SHIFT))


## 区域解析式地面高度：桥面 / 平台 / 楼梯 / 人行道 / 绿化带 / 马路 / 滨河步道
## 同一 XZ 可能有多层（桥面下方就是马路），按 ref_y 取最近的一层；河道返回 NAN
func _ground_at(x: float, z: float, ref_y: float = NAN) -> float:
	if absf(x) > BASE_HALF_X or absf(z) > BASE_HALF_Z:
		return NAN
	# 外卖店是实心店面（Blender y -6.00~-5.06 → Godot z 5.06~6.00），不可穿行
	if x >= SHOP_X0 and x <= SHOP_X1 and z >= SHOP_Z0:
		return NAN
	var ax := absf(x)
	var az := absf(z)
	var levels := []

	# 桥面（含两端平台，平台 1.70 × 1.10 挂在桥端）
	if ax <= 0.85 and (az <= 4.36 or (az >= 4.30 and az <= 5.40)):
		levels.append(DECK_Y)

	# 楼梯：Blender 的 +Y 端对应 Godot 的 -Z 端，两端分列左右（-Z 端向 +X，+Z 端向 -X）
	# 9 级 × 0.12 踢面，水平投影 2.25
	if az >= 4.36 and az <= 5.40 and ax > 0.85 and ax <= 3.10:
		if (x > 0.0) != (z > 0.0):
			var t := clampf((ax - 0.85) / 2.25, 0.0, 1.0)
			var idx := clampi(int(floor(t * 9.0)), 0, 8)
			levels.append(DECK_Y - 0.12 * float(idx + 1))

	# 地面分层
	if az >= 4.38 and az <= 5.38:
		levels.append(SIDEWALK_Y)      # 人行道
	elif az > 5.38:
		levels.append(BELT_Y)          # 绿化带
	elif az >= 1.98:
		levels.append(ROAD_Y)          # 柏油马路（桥下也可通行）
	elif az >= 1.40:
		levels.append(PROMENADE_Y)     # 滨河步道

	if levels.is_empty():
		return NAN
	if is_nan(ref_y):
		return levels.max()
	var best: float = levels[0]
	for h in levels:
		if absf(h - ref_y) < absf(best - ref_y):
			best = h
	return best


func _can_stand(p: Vector3) -> bool:
	var gy := _ground_at(p.x, p.z, global_position.y)
	if is_nan(gy):
		return false
	return absf(gy - global_position.y) <= MAX_STEP


func _try_move(dv: Vector3) -> void:
	var want := global_position + dv
	if _can_stand(want):
		global_position = want
		return
	# 轴向拆分：被挡住时沿墙滑动
	var dx := Vector3(dv.x, 0.0, 0.0)
	if absf(dx.x) > 0.00001 and _can_stand(global_position + dx):
		global_position += dx
		return
	var dz := Vector3(0.0, 0.0, dv.z)
	if absf(dz.z) > 0.00001 and _can_stand(global_position + dz):
		global_position += dz


func _update_anim(move: float, sprint: bool) -> void:
	if _anim == null:
		return
	if _waving:
		return
	if not _grounded:
		return
	if absf(move) > 0.01:
		_play("run" if sprint else "walk")
	else:
		_play("idle")
