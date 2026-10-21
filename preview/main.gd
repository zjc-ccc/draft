extends Control
## Draft 素材库预览器
##
## 直接扫描 `../assets/`，读取每个素材文件夹里的 `export/*.png`，
## 按文件名识别动画状态并循环播放；`preview/` 里的简化图标也能单独查看。

const ICON_KEY := "__icon__"

@onready var category_list: ItemList = $HSplit/Left/CategoryList
@onready var asset_list: ItemList = $HSplit/Left/AssetList
@onready var state_option: OptionButton = $HSplit/Right/Header/StateOption
@onready var title_label: Label = $HSplit/Right/Header/Title
@onready var info_label: Label = $HSplit/Right/Info
@onready var preview: TextureRect = $HSplit/Right/Preview

var root_dir := ""
var all_assets: Array[Dictionary] = []
var filtered: Array[Dictionary] = []
var current: Dictionary = {}
var state_keys: Array[String] = []

var frames: Array[Texture2D] = []
var frame_index := 0
var frame_time := 0.0
var playing := true

var texture_cache := {}


func _ready() -> void:
	root_dir = ProjectSettings.globalize_path("res://").path_join("..").simplify_path()
	$HSplit/Left/Rescan.pressed.connect(scan)
	category_list.item_selected.connect(_on_category_selected)
	asset_list.item_selected.connect(_on_asset_selected)
	state_option.item_selected.connect(_on_state_selected)
	scan()


func _process(delta: float) -> void:
	if not playing or frames.size() <= 1:
		return

	var fps := 0.0
	if current.has("meta"):
		fps = float(current["meta"].get("fps", "0"))
	if fps <= 0.0:
		fps = 8.0

	frame_time += delta
	while frame_time >= 1.0 / fps:
		frame_time -= 1.0 / fps
		frame_index = (frame_index + 1) % frames.size()
		preview.texture = frames[frame_index]


func scan() -> void:
	texture_cache.clear()
	all_assets.clear()
	filtered.clear()
	category_list.clear()
	asset_list.clear()
	state_option.clear()
	frames.clear()
	preview.texture = null

	var assets_root := root_dir.path_join("assets")
	if not DirAccess.dir_exists_absolute(assets_root):
		title_label.text = "找不到 assets/ 目录"
		info_label.text = assets_root
		return

	for category in DirAccess.get_directories_at(assets_root):
		if category.begins_with("."):
			continue
		var category_dir := assets_root.path_join(category)
		for id in DirAccess.get_directories_at(category_dir):
			if id.begins_with("."):
				continue
			var dir := category_dir.path_join(id)
			all_assets.append({
				"id": id,
				"category": category,
				"dir": dir,
				"meta": _read_meta(dir),
				"files": _list_pngs(dir.path_join("export")),
			})

	all_assets.sort_custom(_sort_assets)

	var categories: Array[String] = []
	for asset in all_assets:
		if not categories.has(asset["category"]):
			categories.append(asset["category"])
	categories.sort()

	category_list.add_item("全部")
	for category in categories:
		category_list.add_item(category)
	category_list.select(0)

	_populate("")
	print("[draft-preview] %d 个素材，%d 个分类" % [all_assets.size(), categories.size()])


func _sort_assets(a: Dictionary, b: Dictionary) -> bool:
	return "%s/%s" % [a["category"], a["id"]] < "%s/%s" % [b["category"], b["id"]]


func _populate(category: String) -> void:
	filtered.clear()
	asset_list.clear()
	for asset in all_assets:
		if category != "" and asset["category"] != category:
			continue
		filtered.append(asset)
		asset_list.add_item(asset["id"])

	if filtered.is_empty():
		title_label.text = "（没有素材）"
		info_label.text = "用 tools/new-asset.ps1 新建一个素材，或点「重新扫描」。"
		state_option.clear()
		state_option.disabled = true
		frames.clear()
		preview.texture = null
		return

	asset_list.select(0)
	_show(filtered[0])


func _on_category_selected(index: int) -> void:
	var text := category_list.get_item_text(index)
	_populate("" if text == "全部" else text)


func _on_asset_selected(index: int) -> void:
	if index >= 0 and index < filtered.size():
		_show(filtered[index])


func _show(asset: Dictionary) -> void:
	current = asset
	title_label.text = asset["id"]

	var meta: Dictionary = asset["meta"]
	info_label.text = "分类：%s    状态：%s    尺寸：%s    帧数：%s    fps：%s    授权：%s    创建：%s\n%s" % [
		asset["category"],
		meta.get("status", "-"),
		meta.get("size", "-"),
		meta.get("frames", "-"),
		meta.get("fps", "-"),
		meta.get("license", "-"),
		meta.get("created", "-"),
		String(asset["dir"]).replace(root_dir + "/", ""),
	]

	state_option.clear()
	state_keys.clear()

	var groups := _group_frames(asset)
	var icons := _list_pngs(String(asset["dir"]).path_join("preview"))

	if groups.is_empty() and icons.is_empty():
		state_option.add_item("无导出文件")
		state_option.disabled = true
		frames.clear()
		preview.texture = null
		return

	state_option.disabled = false
	var keys := groups.keys()
	keys.sort()
	for key in keys:
		state_keys.append(key)
		state_option.add_item("静帧" if key == "" else key)
	if not icons.is_empty():
		state_keys.append(ICON_KEY)
		state_option.add_item("图标")
	state_option.select(0)
	_set_state(state_keys[0])


func _on_state_selected(index: int) -> void:
	if index >= 0 and index < state_keys.size():
		_set_state(state_keys[index])


func _set_state(state: String) -> void:
	frames.clear()
	frame_index = 0
	frame_time = 0.0

	var paths: Array = []
	if state == ICON_KEY:
		paths = _list_pngs(String(current["dir"]).path_join("preview"))
	else:
		paths = _group_frames(current).get(state, [])

	for path in paths:
		var texture := _load_texture(path)
		if texture != null:
			frames.append(texture)

	preview.texture = frames[0] if not frames.is_empty() else null


## 按文件名把导出图分组：<id>_<state>_<帧号>.png
func _group_frames(asset: Dictionary) -> Dictionary:
	var groups := {}
	var id: String = asset["id"]
	for path in asset["files"]:
		var base := String(path).get_file().get_basename()
		var state := ""
		if base.begins_with(id + "_"):
			var rest := base.substr(id.length() + 1)
			var parts := rest.split("_", false)
			if parts.size() > 1 and parts[parts.size() - 1].is_valid_int():
				parts.remove_at(parts.size() - 1)
				state = "_".join(parts)
			else:
				state = rest
		if not groups.has(state):
			groups[state] = []
		groups[state].append(path)
	return groups


func _read_meta(dir_path: String) -> Dictionary:
	var meta := {}
	var path := dir_path.path_join("README.md")
	if not FileAccess.file_exists(path):
		return meta

	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return meta

	var in_block := false
	while not file.eof_reached():
		var line := file.get_line()
		if line.strip_edges() == "---":
			if in_block:
				break
			in_block = true
			continue
		if in_block:
			var idx := line.find(":")
			if idx > 0:
				meta[line.substr(0, idx).strip_edges()] = line.substr(idx + 1).strip_edges()
	return meta


func _list_pngs(dir_path: String) -> Array:
	var files := []
	if not DirAccess.dir_exists_absolute(dir_path):
		return files
	for name in DirAccess.get_files_at(dir_path):
		if name.get_extension().to_lower() == "png":
			files.append(dir_path.path_join(name))
	files.sort()
	return files


func _load_texture(path: String) -> Texture2D:
	if texture_cache.has(path):
		return texture_cache[path]
	if not FileAccess.file_exists(path):
		return null

	var image := Image.load_from_file(path)
	if image == null:
		return null

	var texture := ImageTexture.create_from_image(image)
	texture_cache[path] = texture
	return texture
