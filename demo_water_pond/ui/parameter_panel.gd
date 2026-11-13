extends PanelContainer
# 水面参数面板：由 GROUPS 表驱动生成滑块/取色器，实时写入 ShaderMaterial。

var water_material: ShaderMaterial
var sun: DirectionalLight3D

const GROUPS := [
	{
		"title": "波浪",
		"items": [
			{"key": "wave_height", "label": "浪高 m", "min": 0.0, "max": 0.35, "step": 0.001, "default": 0.055},
			{"key": "wave_scale", "label": "波浪频率", "min": 0.02, "max": 0.6, "step": 0.001, "default": 0.22},
			{"key": "wave_speed", "label": "波浪速度", "min": 0.0, "max": 3.0, "step": 0.01, "default": 0.6},
			{"key": "wave_chop", "label": "波峰锐度", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.35},
		],
	},
	{
		"title": "涟漪",
		"items": [
			{"key": "ripple_scale", "label": "涟漪密度", "min": 1.0, "max": 40.0, "step": 0.1, "default": 10.0},
			{"key": "ripple_strength", "label": "涟漪强度", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.30},
			{"key": "ripple_speed", "label": "涟漪速度", "min": 0.0, "max": 3.0, "step": 0.01, "default": 1.0},
		],
	},
	{
		"title": "光学",
		"items": [
			{"key": "clarity", "label": "清澈度", "min": 0.1, "max": 8.0, "step": 0.05, "default": 0.60},
			{"key": "surface_roughness", "label": "水面粗糙", "min": 0.0, "max": 0.5, "step": 0.005, "default": 0.05},
			{"key": "specular_amount", "label": "反射强度", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.70},
			{"key": "refraction_strength", "label": "折射扰动", "min": 0.0, "max": 0.06, "step": 0.001, "default": 0.012},
		],
	},
	{
		"title": "泡沫",
		"items": [
			{"key": "shore_foam_depth", "label": "岸边泡沫", "min": 0.0, "max": 1.5, "step": 0.01, "default": 0.30},
			{"key": "crest_foam", "label": "浪尖泡沫", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.05},
			{"key": "foam_breakup", "label": "泡沫破碎", "min": 0.0, "max": 1.0, "step": 0.01, "default": 0.55},
		],
	},
	{
		"title": "颜色",
		"items": [
			{"key": "shallow_color", "label": "浅水色", "kind": "color", "default": Color(0.36, 0.62, 0.60)},
			{"key": "deep_color", "label": "深水色", "kind": "color", "default": Color(0.03, 0.16, 0.22)},
			{"key": "foam_color", "label": "泡沫色", "kind": "color", "default": Color(0.93, 0.96, 0.97)},
		],
	},
	{
		"title": "场景",
		"items": [
			{"key": "sun_elevation", "label": "太阳仰角", "kind": "sun", "min": 5.0, "max": 80.0, "step": 0.5, "default": 42.0},
		],
	},
]

var _sliders := {}
var _value_labels := {}
var _colors := {}


func _ready() -> void:
	position = Vector2(16, 16)

	var ui_font := SystemFont.new()
	ui_font.font_names = PackedStringArray(["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "Noto Sans CJK SC"])
	ui_font.allow_system_fallback = true
	var ui_theme := Theme.new()
	ui_theme.default_font = ui_font
	ui_theme.default_font_size = 13
	theme = ui_theme

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	add_child(margin)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 5)
	margin.add_child(box)

	var title := Label.new()
	title.text = "水面参数"
	title.add_theme_font_size_override("font_size", 17)
	box.add_child(title)

	for group in GROUPS:
		var header := Label.new()
		header.text = String(group["title"])
		header.add_theme_color_override("font_color", Color(0.52, 0.86, 0.93))
		header.add_theme_font_size_override("font_size", 13)
		box.add_child(header)
		for item in group["items"]:
			box.add_child(_build_row(item))

	box.add_child(HSeparator.new())

	var reset := Button.new()
	reset.text = "重置到默认"
	reset.pressed.connect(_reset_all)
	box.add_child(reset)

	var hint := Label.new()
	hint.text = "右键拖动旋转 · 滚轮缩放"
	hint.add_theme_color_override("font_color", Color(0.72, 0.76, 0.80))
	hint.add_theme_font_size_override("font_size", 12)
	box.add_child(hint)


func _build_row(item: Dictionary) -> Control:
	var kind: String = String(item.get("kind", "float"))
	var row := HBoxContainer.new()
	row.custom_minimum_size = Vector2(300, 23)
	row.add_theme_constant_override("separation", 8)

	var name_label := Label.new()
	name_label.text = String(item["label"])
	name_label.custom_minimum_size = Vector2(78, 0)
	row.add_child(name_label)

	if kind == "color":
		var picker := ColorPickerButton.new()
		picker.edit_alpha = false
		picker.custom_minimum_size = Vector2(0, 21)
		picker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		var cur = water_material.get_shader_parameter(String(item["key"]))
		picker.color = cur if cur is Color else item["default"]
		picker.color_changed.connect(_on_color_changed.bind(String(item["key"])))
		row.add_child(picker)
		_colors[String(item["key"])] = picker
		return row

	var slider := HSlider.new()
	slider.min_value = float(item["min"])
	slider.max_value = float(item["max"])
	slider.step = float(item["step"])
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER

	var start := float(item["default"])
	if kind == "float":
		var cur = water_material.get_shader_parameter(String(item["key"]))
		if cur != null:
			start = float(cur)
	slider.value = start
	row.add_child(slider)

	var value_label := Label.new()
	value_label.custom_minimum_size = Vector2(48, 0)
	value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	value_label.text = _fmt(start)
	row.add_child(value_label)

	slider.value_changed.connect(_on_slider_changed.bind(item, value_label))
	_sliders[String(item["key"])] = slider
	_value_labels[String(item["key"])] = value_label
	return row


func _on_slider_changed(value: float, item: Dictionary, value_label: Label) -> void:
	value_label.text = _fmt(value)
	var key := String(item["key"])
	if String(item.get("kind", "float")) == "sun":
		if sun != null:
			sun.rotation_degrees = Vector3(-value, 138.0, 0.0)
	else:
		water_material.set_shader_parameter(key, value)


func _on_color_changed(color: Color, key: String) -> void:
	water_material.set_shader_parameter(key, color)


func _reset_all() -> void:
	for group in GROUPS:
		for item in group["items"]:
			var key := String(item["key"])
			var kind := String(item.get("kind", "float"))
			if kind == "color":
				var picker: ColorPickerButton = _colors[key]
				picker.color = item["default"]
				water_material.set_shader_parameter(key, item["default"])
				continue

			var slider: HSlider = _sliders[key]
			slider.set_value_no_signal(float(item["default"]))
			_value_labels[key].text = _fmt(float(item["default"]))
			if kind == "sun":
				if sun != null:
					sun.rotation_degrees = Vector3(-float(item["default"]), 138.0, 0.0)
			else:
				water_material.set_shader_parameter(key, float(item["default"]))


func _fmt(v: float) -> String:
	if absf(v) >= 100.0:
		return String.num(v, 0)
	if absf(v) >= 1.0:
		return String.num(v, 2)
	return String.num(v, 3)
