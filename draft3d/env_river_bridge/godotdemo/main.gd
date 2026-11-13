extends Node3D
## 跨河桥 glb 预览：火柴人第三人称视角（WASD 移动，可上桥行走）
## 运行：godot --path . ；截图：godot --path . -- --shot

const MODEL_PATH := "res://assets/env_river_bridge.glb"


func _ready() -> void:
	_add_environment()
	_add_lights()
	_add_model()
	_add_player()
	_add_camera()
	_add_delivery()
	_add_ui()
	if "--shot" in OS.get_cmdline_user_args():
		_capture()


func _add_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.70, 0.82)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.78, 0.83, 0.95)
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.ssao_enabled = false
	env.glow_enabled = true
	env.glow_intensity = 0.35
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	we.environment = env
	add_child(we)


func _add_lights() -> void:
	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(-40.0, 150.0, 0.0)
	sun.light_color = Color(1.0, 0.86, 0.70)
	sun.light_energy = 1.0
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 80.0
	add_child(sun)

	var fill := DirectionalLight3D.new()
	fill.name = "Fill"
	fill.rotation_degrees = Vector3(-35.0, -50.0, 0.0)
	fill.light_color = Color(0.72, 0.82, 1.0)
	fill.light_energy = 0.28
	fill.shadow_enabled = false
	add_child(fill)


func _add_model() -> void:
	if has_node("RiverBridge"):
		return
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("模型加载失败: " + MODEL_PATH)
		return
	var model: Node3D = packed.instantiate()
	model.name = "RiverBridge"
	add_child(model)


var _player: Node3D
var _cam: Camera3D
var _status: Label


func _add_player() -> void:
	_player = Node3D.new()
	_player.name = "Player"
	_player.set_script(load("res://player.gd"))
	_player.position = Vector3(0.0, 1.45, 3.60)   # 桥面靠北端，脚底贴桥面
	add_child(_player)


func _add_camera() -> void:
	_cam = Camera3D.new()
	_cam.name = "Camera3D"
	_cam.set_script(load("res://follow_camera.gd"))
	_cam.set("target_path", NodePath("../Player"))
	add_child(_cam)
	_cam.current = true


func _add_delivery() -> void:
	# 取餐 / 交付 / 计时 / 顾客，逻辑见 delivery.gd
	if has_node("Delivery"):
		return
	var d := Node3D.new()
	d.name = "Delivery"
	d.set_script(load("res://delivery.gd"))
	add_child(d)


func _add_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "UI"
	add_child(layer)
	var hint := Label.new()
	hint.text = "W / S  Move   ·   A / D  Turn   ·   Shift  Sprint   ·   Space  Jump   ·   F  取餐 / 交付   ·   E / 左键  Wave   ·   V  第一/第三人称"
	hint.position = Vector2(26, 20)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.86))
	hint.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.45))
	hint.add_theme_constant_override("outline_size", 4)
	hint.add_theme_font_size_override("font_size", 18)
	layer.add_child(hint)

	# 当前动作名与视角，用于确认输入是否真的进来了
	_status = Label.new()
	_status.text = "anim: -"
	_status.position = Vector2(26, 50)
	_status.add_theme_color_override("font_color", Color(1, 1, 1, 0.72))
	_status.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.45))
	_status.add_theme_constant_override("outline_size", 4)
	_status.add_theme_font_size_override("font_size", 16)
	layer.add_child(_status)


func _process(_delta: float) -> void:
	if _status == null:
		return
	var anim_text := "-"
	if _player:
		anim_text = str(_player.call("current_anim"))
	var view_text := "3P"
	if _cam:
		view_text = str(_cam.call("mode_text"))
	_status.text = "anim: %s    view: %s" % [anim_text, view_text]


func _capture() -> void:
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("res://screenshot.png")
	print("SHOT_SAVED ", img.get_size())
	get_tree().quit()
