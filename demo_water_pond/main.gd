extends Node3D
# 水面 demo 场景：运行时搭建天空/太阳/水池/水面/相机/参数面板。

const WATER_SHADER := preload("res://water/realistic_water.gdshader")
const ORBIT_CAMERA := preload("res://water/orbit_camera.gd")
const PARAM_PANEL := preload("res://ui/parameter_panel.gd")

const WATER_SIZE := 10.0
const POND_DEPTH := 1.5
const RIM_WIDTH := 0.8

var water_material: ShaderMaterial
var sun: DirectionalLight3D


func _ready() -> void:
	_build_environment()
	_build_pond()
	_build_water()
	_build_camera()
	_build_ui()


func _build_environment() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color("#2f6ea8")
	sky_mat.sky_horizon_color = Color("#cfe0ea")
	sky_mat.sky_curve = 0.18
	sky_mat.ground_bottom_color = Color("#26303a")
	sky_mat.ground_horizon_color = Color("#8e9ba4")
	sky_mat.sun_angle_max = 12.0
	sky_mat.sun_curve = 0.12

	var sky := Sky.new()
	sky.sky_material = sky_mat
	sky.radiance_size = Sky.RADIANCE_SIZE_256

	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.9
	env.tonemap_mode = Environment.TONE_MAPPER_ACES
	env.tonemap_exposure = 1.0
	env.glow_enabled = true
	env.glow_intensity = 0.2
	env.glow_bloom = 0.02
	env.glow_hdr_threshold = 1.1

	var world_env := WorldEnvironment.new()
	world_env.name = "WorldEnvironment"
	world_env.environment = env
	add_child(world_env)

	sun = DirectionalLight3D.new()
	sun.name = "Sun"
	sun.rotation_degrees = Vector3(-42.0, 138.0, 0.0)
	sun.light_color = Color(1.0, 0.95, 0.86)
	sun.light_energy = 1.6
	sun.shadow_enabled = true
	sun.shadow_blur = 1.5
	add_child(sun)


func _build_pond() -> void:
	var pond := Node3D.new()
	pond.name = "Pond"
	add_child(pond)

	var stone := StandardMaterial3D.new()
	stone.albedo_color = Color("#7d858a")
	stone.roughness = 0.85

	var gravel := StandardMaterial3D.new()
	gravel.albedo_color = Color("#55625f")
	gravel.roughness = 0.95

	# 外围地面
	var ground := MeshInstance3D.new()
	var ground_mesh := PlaneMesh.new()
	ground_mesh.size = Vector2(40, 40)
	ground.mesh = ground_mesh
	ground.position = Vector3(0, -POND_DEPTH - 0.06, 0)
	var ground_mat := StandardMaterial3D.new()
	ground_mat.albedo_color = Color("#4a5348")
	ground_mat.roughness = 1.0
	ground.material_override = ground_mat
	pond.add_child(ground)

	# 池底
	var floor_mi := MeshInstance3D.new()
	floor_mi.name = "Floor"
	var floor_mesh := PlaneMesh.new()
	floor_mesh.size = Vector2(WATER_SIZE, WATER_SIZE)
	floor_mesh.subdivide_width = 12
	floor_mesh.subdivide_depth = 12
	floor_mi.mesh = floor_mesh
	floor_mi.position = Vector3(0, -POND_DEPTH, 0)
	floor_mi.material_override = gravel
	pond.add_child(floor_mi)

	# 四边石沿
	var rim_h := POND_DEPTH + 0.15
	var half := WATER_SIZE * 0.5 + RIM_WIDTH * 0.5
	var rim_top_y := -rim_h * 0.5 + 0.06
	var long_side := WATER_SIZE + RIM_WIDTH * 2.0
	var rim_specs := [
		[Vector3(long_side, rim_h, RIM_WIDTH), Vector3(half, rim_top_y, 0)],
		[Vector3(long_side, rim_h, RIM_WIDTH), Vector3(-half, rim_top_y, 0)],
		[Vector3(RIM_WIDTH, rim_h, long_side), Vector3(0, rim_top_y, half)],
		[Vector3(RIM_WIDTH, rim_h, long_side), Vector3(0, rim_top_y, -half)],
	]
	for spec in rim_specs:
		var rim := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = spec[0]
		rim.mesh = box
		rim.position = spec[1]
		rim.material_override = stone
		pond.add_child(rim)

	# 池底石块（用来观察折射与水体吸收）
	var rock_specs := [
		[Vector3(-2.4, -1.18, 1.6), Vector3(1.35, 0.75, 1.1), Color("#6b7a72")],
		[Vector3(1.9, -1.2, 2.4), Vector3(1.0, 0.6, 0.9), Color("#7d6f5f")],
		[Vector3(0.4, -1.05, -1.2), Vector3(1.2, 0.7, 1.3), Color("#59636b")],
		[Vector3(-1.2, -1.22, -2.6), Vector3(0.9, 0.55, 0.8), Color("#6f6a5c")],
		[Vector3(2.8, -1.18, -1.4), Vector3(1.1, 0.6, 1.0), Color("#5f6d69")],
	]
	for spec in rock_specs:
		var rock := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = 0.45
		sphere.height = 0.9
		sphere.radial_segments = 16
		sphere.rings = 8
		rock.mesh = sphere
		rock.position = spec[0]
		rock.scale = spec[1]
		var rock_mat := StandardMaterial3D.new()
		rock_mat.albedo_color = spec[2]
		rock_mat.roughness = 0.9
		rock.material_override = rock_mat
		pond.add_child(rock)

	# 反射探针：让水面能映出石沿
	var probe := ReflectionProbe.new()
	probe.size = Vector3(16, 8, 16)
	probe.position = Vector3(0, 0.5, 0)
	probe.update_mode = ReflectionProbe.UPDATE_ONCE
	probe.intensity = 0.7
	probe.max_distance = 40.0
	probe.box_projection = true
	pond.add_child(probe)


func _build_water() -> void:
	var water := MeshInstance3D.new()
	water.name = "Water"
	var plane := PlaneMesh.new()
	plane.size = Vector2(WATER_SIZE, WATER_SIZE)
	plane.subdivide_width = 96
	plane.subdivide_depth = 96
	water.mesh = plane
	water.position = Vector3(0, -0.05, 0)
	water_material = ShaderMaterial.new()
	water_material.shader = WATER_SHADER
	water.material_override = water_material
	add_child(water)


func _build_camera() -> void:
	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.set_script(ORBIT_CAMERA)
	cam.fov = 60.0
	cam.near = 0.05
	cam.far = 200.0
	cam.set("target", Vector3(0.0, -0.3, 0.0))
	cam.set("distance", 9.5)
	cam.set("elevation", 16.0)
	cam.set("yaw", 24.0)
	add_child(cam)
	cam.current = true


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	layer.name = "UI"
	var panel := PanelContainer.new()
	panel.set_script(PARAM_PANEL)
	panel.set("water_material", water_material)
	panel.set("sun", sun)
	layer.add_child(panel)
	add_child(layer)
