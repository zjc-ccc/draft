extends Node3D
## 城市中心广场 glb 预览：火柴人第三人称视角（WASD 移动）
## 运行：godot --path . ；截图：godot --path . -- --shot

const MODEL_PATH := "res://assets/env_city_plaza.glb"


func _ready() -> void:
	_add_environment()
	_add_lights()
	_add_model()
	_add_player()
	_add_camera()
	_add_ui()
	if "--shot" in OS.get_cmdline_user_args():
		_capture()


func _add_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.68, 0.76, 0.88)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.80, 0.85, 0.95)
	env.ambient_light_energy = 0.60
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.ssao_enabled = false
	env.glow_enabled = true
	env.glow_intensity = 0.40
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	we.environment = env
	add_child(we)


func _add_lights() -> void:
	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(-38.0, 145.0, 0.0)
	sun.light_color = Color(1.0, 0.79, 0.60)
	sun.light_energy = 1.15
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 80.0
	add_child(sun)

	var fill := DirectionalLight3D.new()
	fill.name = "Fill"
	fill.rotation_degrees = Vector3(-32.0, -55.0, 0.0)
	fill.light_color = Color(0.70, 0.80, 1.0)
	fill.light_energy = 0.30
	fill.shadow_enabled = false
	add_child(fill)


func _add_model() -> void:
	if has_node("CityPlaza"):
		return
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("模型加载失败: " + MODEL_PATH)
		return
	var model: Node3D = packed.instantiate()
	model.name = "CityPlaza"
	add_child(model)


func _add_player() -> void:
	var player := Node3D.new()
	player.name = "Player"
	player.set_script(load("res://player.gd"))
	player.position = Vector3(3.9, 0.371, -4.6)   # 广场内、喷泉东南侧
	add_child(player)


func _add_camera() -> void:
	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.set_script(load("res://follow_camera.gd"))
	cam.set("target_path", NodePath("../Player"))
	add_child(cam)
	cam.current = true


func _add_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "UI"
	add_child(layer)
	var hint := Label.new()
	hint.text = "W / S  Move   ·   A / D  Turn   ·   Shift  Sprint"
	hint.position = Vector2(26, 20)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.9))
	hint.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.5))
	hint.add_theme_constant_override("outline_size", 4)
	hint.add_theme_font_size_override("font_size", 18)
	layer.add_child(hint)


func _capture() -> void:
	for i in 30:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("res://screenshot.png")
	print("SHOT_SAVED ", img.get_size())
	get_tree().quit()
