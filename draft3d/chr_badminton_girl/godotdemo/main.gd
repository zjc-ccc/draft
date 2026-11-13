extends Node3D
## 羽毛球社团少女 glb 预览
## 运行：godot --path .    截图：godot --path . -- --shot

const MODEL_PATH := "res://assets/chr_badminton_girl.glb"


func _ready() -> void:
	_add_environment()
	_add_lights()
	_add_ground()
	_add_model()
	_add_camera()
	_add_ui()
	if "--shot" in OS.get_cmdline_user_args():
		_capture()


func _add_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.17, 0.18, 0.21)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.72, 0.78, 0.92)
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.ssao_enabled = false
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	we.environment = env
	add_child(we)


func _add_lights() -> void:
	var key := DirectionalLight3D.new()
	key.name = "Key"
	key.rotation_degrees = Vector3(-35.0, 155.0, 0.0)
	key.light_color = Color(1.0, 0.96, 0.92)
	key.light_energy = 1.25
	key.shadow_enabled = true
	add_child(key)

	var rim := DirectionalLight3D.new()
	rim.name = "Rim"
	rim.rotation_degrees = Vector3(-25.0, -20.0, 0.0)
	rim.light_color = Color(1.0, 0.88, 0.78)
	rim.light_energy = 0.55
	add_child(rim)

	var fill := DirectionalLight3D.new()
	fill.name = "Fill"
	fill.rotation_degrees = Vector3(-15.0, 40.0, 0.0)
	fill.light_color = Color(0.75, 0.84, 1.0)
	fill.light_energy = 0.35
	add_child(fill)


func _add_ground() -> void:
	var plane := MeshInstance3D.new()
	plane.name = "Ground"
	var mesh := PlaneMesh.new()
	mesh.size = Vector2(8.0, 8.0)
	plane.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.26, 0.27, 0.30)
	mat.roughness = 0.95
	plane.material_override = mat
	add_child(plane)


var anim_player: AnimationPlayer


func _add_model() -> void:
	var packed: PackedScene = load(MODEL_PATH)
	if packed == null:
		push_error("模型加载失败: " + MODEL_PATH)
		return
	var model: Node3D = packed.instantiate()
	model.name = "Character"
	add_child(model)
	for skel in _find_all(model, "Skeleton3D"):
		print("SKELETON bones = ", (skel as Skeleton3D).get_bone_count())
	var players := _find_all(model, "AnimationPlayer")
	if players.size() > 0:
		anim_player = players[0]
		print("ANIMATIONS = ", anim_player.get_animation_list())
		_play("idle")


func _play(anim: String) -> void:
	if anim_player == null:
		return
	if not anim_player.has_animation(anim):
		return
	anim_player.play(anim)
	anim_player.get_tree().root.title = "Badminton Girl - " + anim


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match (event as InputEventKey).keycode:
			KEY_1: _play("idle")
			KEY_2: _play("run")
			KEY_3: _play("jump")
			KEY_4: _play("wave")


func _find_all(node: Node, type_name: String) -> Array:
	var out: Array = []
	if node.is_class(type_name):
		out.append(node)
	for c in node.get_children():
		out.append_array(_find_all(c, type_name))
	return out


func _add_camera() -> void:
	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.set_script(load("res://orbit_camera.gd"))
	cam.set("target", Vector3(0.0, 0.85, 0.0))
	cam.set("distance", 3.0)
	add_child(cam)
	cam.current = true


func _add_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "UI"
	add_child(layer)
	var hint := Label.new()
	hint.text = "1 Idle  ·  2 Run  ·  3 Jump  ·  4 Wave     |     Drag  Orbit  ·  Wheel  Zoom"
	hint.position = Vector2(24, 18)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.85))
	hint.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.5))
	hint.add_theme_constant_override("outline_size", 4)
	hint.add_theme_font_size_override("font_size", 17)
	layer.add_child(hint)


func _capture() -> void:
	for i in 40:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("res://screenshot.png")
	print("SHOT_SAVED ", img.get_size())
	get_tree().quit()
