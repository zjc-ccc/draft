extends Node3D
## 送外卖玩法：外卖店取餐 → 过桥 → 送达对面顾客
## F 在取餐光圈取餐、在收货光圈交付；60 秒时限；金币 = 10 + 剩余秒
## 顾客用 stickman_white.glb 复刻，整身换色 + idle / wave

const MODEL_PATH := "res://assets/stickman_white.glb"
const PICK_POS := Vector3(-4.98, 0.37, 4.62)      # 取餐光圈
const DROP_POS := Vector3(5.55, 0.37, -4.86)      # 收货光圈
const INTERACT_RADIUS := 0.80
const TIME_LIMIT := 60.0
const RESULT_HOLD := 2.4
const TINT := Color(0.91, 0.47, 0.35)

enum State { WAITING, CARRYING, RESULT }

var state: int = State.WAITING
var coins := 0
var orders := 0
var time_left := 0.0

var _player: Node3D
var _customer: Node3D
var _cust_anim: AnimationPlayer
var _panel: Label
var _prompt: Label
var _toast: Label
var _toast_t := 0.0
var _result_t := 0.0


func _ready() -> void:
	_player = get_parent().get_node_or_null("Player")
	if _player == null:
		push_error("送外卖：找不到 Player")
	_build_ui()
	_spawn_customer()
	_refresh_panel()


# ---------------------------------------------------------------- UI
func _make_label(size: int) -> Label:
	var l := Label.new()
	l.add_theme_color_override("font_color", Color(1, 1, 1, 0.92))
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.55))
	l.add_theme_constant_override("outline_size", 5)
	l.add_theme_font_size_override("font_size", size)
	return l


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "DeliveryUI"
	add_child(layer)

	_panel = _make_label(18)
	_panel.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_panel.anchor_left = 1.0
	_panel.anchor_right = 1.0
	_panel.offset_left = -460.0
	_panel.offset_top = 52.0
	_panel.offset_right = -26.0
	_panel.offset_bottom = 78.0
	layer.add_child(_panel)

	_prompt = _make_label(24)
	_prompt.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_prompt.anchor_left = 0.5
	_prompt.anchor_right = 0.5
	_prompt.anchor_top = 1.0
	_prompt.anchor_bottom = 1.0
	_prompt.offset_left = -200.0
	_prompt.offset_right = 200.0
	_prompt.offset_top = -140.0
	_prompt.offset_bottom = -104.0
	_prompt.visible = false
	layer.add_child(_prompt)

	_toast = _make_label(30)
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast.anchor_left = 0.5
	_toast.anchor_right = 0.5
	_toast.anchor_top = 0.5
	_toast.anchor_bottom = 0.5
	_toast.offset_left = -260.0
	_toast.offset_right = 260.0
	_toast.offset_top = -120.0
	_toast.offset_bottom = -80.0
	_toast.visible = false
	layer.add_child(_toast)


func _toast_msg(text: String, color: Color) -> void:
	_toast.text = text
	_toast.add_theme_color_override("font_color", color)
	_toast.visible = true
	_toast_t = RESULT_HOLD


# ---------------------------------------------------------------- 顾客
func _spawn_customer() -> void:
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("顾客模型加载失败: " + MODEL_PATH)
		return
	_customer = packed.instantiate()
	_customer.name = "Customer"
	add_child(_customer)
	_customer.global_position = DROP_POS
	_customer.rotation.y = PI          # 角色正面 -Z，转 180° 面向 +Z（桥的方向）

	var tint := StandardMaterial3D.new()
	tint.albedo_color = TINT
	tint.roughness = 1.0
	for node in _customer.find_children("*", "MeshInstance3D", true, false):
		(node as MeshInstance3D).material_override = tint

	_cust_anim = _customer.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _cust_anim == null:
		push_error("顾客动画播放器缺失")
		return
	var idle := _cust_anim.get_animation("idle")
	if idle:
		idle.loop_mode = Animation.LOOP_LINEAR
	var wave := _cust_anim.get_animation("wave")
	if wave:
		wave.loop_mode = Animation.LOOP_NONE
	_cust_anim.play("idle")


# ---------------------------------------------------------------- 交互
func _near(pos: Vector3) -> bool:
	if _player == null:
		return false
	var p := _player.global_position
	return Vector2(p.x - pos.x, p.z - pos.z).length() <= INTERACT_RADIUS


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var k: int = event.physical_keycode if event.physical_keycode != 0 else event.keycode
		if k == KEY_F or event.keycode == KEY_F:
			_interact()


func _interact() -> void:
	if state == State.WAITING and _near(PICK_POS):
		state = State.CARRYING
		time_left = TIME_LIMIT
		_toast_msg("接到订单，送到河对岸的顾客手里", Color(1, 1, 1))
	elif state == State.CARRYING and _near(DROP_POS):
		_deliver()


func _deliver() -> void:
	var gain := 10 + int(ceilf(maxf(time_left, 0.0)))
	coins += gain
	orders += 1
	time_left = 0.0
	state = State.RESULT
	_result_t = RESULT_HOLD
	if _cust_anim:
		_cust_anim.play("wave", 0.15)
	_toast_msg("送达 +%d 金币" % gain, Color(0.62, 1.0, 0.72))


func _fail() -> void:
	time_left = 0.0
	state = State.RESULT
	_result_t = RESULT_HOLD
	_toast_msg("超时，订单取消", Color(1.0, 0.56, 0.5))


# ---------------------------------------------------------------- 主循环
func _process(delta: float) -> void:
	if _toast_t > 0.0:
		_toast_t -= delta
		if _toast_t <= 0.0:
			_toast.visible = false

	if state == State.CARRYING:
		time_left -= delta
		if time_left <= 0.0:
			_fail()
	elif state == State.RESULT:
		_result_t -= delta
		if _result_t <= 0.0:
			state = State.WAITING
			if _cust_anim:
				_cust_anim.play("idle", 0.2)

	_update_prompt()
	_refresh_panel()


func _update_prompt() -> void:
	var txt := ""
	if state == State.WAITING and _near(PICK_POS):
		txt = "F  取餐"
	elif state == State.CARRYING and _near(DROP_POS):
		txt = "F  交付"
	_prompt.text = txt
	_prompt.visible = txt != ""


func _refresh_panel() -> void:
	if state == State.CARRYING:
		_panel.text = "外卖送单   剩余 %4.1f s   已送 %d 单   金币 %d" % [
			maxf(time_left, 0.0), orders, coins]
	else:
		_panel.text = "外卖送单   已送 %d 单   金币 %d" % [orders, coins]
