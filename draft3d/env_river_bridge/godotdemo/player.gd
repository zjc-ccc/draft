extends Node3D
## 火柴人第三人称控制：W/S 移动，A/D 转身，Shift 加速，Space 跳跃，F 挥手
## 身高 0.583 场景单位（马路 2.4 单位 = 7 m，即 1.7 m），活动范围限定在桥面

const MODEL_PATH := "res://assets/stickman_white.glb"
const GROUND_Y := 1.45           # 桥面高度
const WALK_SPEED := 0.48         # 场景单位/秒，约 1.4 m/s
const SPRINT_SPEED := 1.03       # 约 3.0 m/s
const TURN_SPEED := 2.2          # 弧度/秒
const HALF_X := 0.68             # 桥面半宽 0.85，留出栏杆边距
const HALF_Z := 4.15             # 桥面半长 4.36
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
	global_position.y = GROUND_Y

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
		elif k == KEY_F or k == KEY_E or event.keycode == KEY_F or event.keycode == KEY_E:
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
		global_position += -global_transform.basis.z * move * speed * delta

	if not _grounded:
		_vy -= GRAVITY * delta
		global_position.y += _vy * delta
		if global_position.y <= GROUND_Y:
			global_position.y = GROUND_Y
			_vy = 0.0
			_grounded = true
	else:
		global_position.y = GROUND_Y

	global_position.x = clampf(global_position.x, -HALF_X, HALF_X)
	global_position.z = clampf(global_position.z, -HALF_Z, HALF_Z)

	_update_anim(move, Input.is_key_pressed(KEY_SHIFT))


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
