extends Node2D
## 试玩场景：一间空屋子，一只用 WASD 驱动的蟑螂。
##
## 地板和墙都是代码画的，不占素材；蟑螂是 `prefabs/cockroach.tscn` 实例。
## Esc 回素材预览。

## 房间范围（世界坐标，中心在原点）
const ROOM := Rect2(-420, -300, 840, 600)
## 墙厚
const WALL := 18.0
## 地砖边长
const TILE := 48.0

const FLOOR_A := Color(0.17, 0.18, 0.20)
const FLOOR_B := Color(0.14, 0.15, 0.17)
const FLOOR_LINE := Color(0.11, 0.12, 0.14)
const WALL_FILL := Color(0.24, 0.23, 0.22)
const WALL_EDGE := Color(0.34, 0.32, 0.30)

@onready var roach: CharacterBody2D = $Spawn/Cockroach
@onready var camera: Camera2D = $Camera2D
@onready var hint: Label = $HUD/Hint


func _ready() -> void:
	_build_walls()
	_setup_camera()
	camera.global_position = roach.global_position
	queue_redraw()


func _process(_delta: float) -> void:
	camera.global_position = roach.global_position

	if Input.is_action_just_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://main.tscn")


func _setup_camera() -> void:
	camera.zoom = Vector2(2.5, 2.5)
	camera.position_smoothing_enabled = true
	camera.position_smoothing_speed = 10.0
	camera.limit_left = int(ROOM.position.x)
	camera.limit_top = int(ROOM.position.y)
	camera.limit_right = int(ROOM.end.x)
	camera.limit_bottom = int(ROOM.end.y)
	camera.limit_smoothed = true


## 四面墙：只做碰撞，形状是矩形；外观由 _draw() 画
func _build_walls() -> void:
	var rects := [
		Rect2(ROOM.position.x, ROOM.position.y, ROOM.size.x, WALL),
		Rect2(ROOM.position.x, ROOM.end.y - WALL, ROOM.size.x, WALL),
		Rect2(ROOM.position.x, ROOM.position.y, WALL, ROOM.size.y),
		Rect2(ROOM.end.x - WALL, ROOM.position.y, WALL, ROOM.size.y),
	]
	for rect in rects:
		var body := StaticBody2D.new()
		body.name = "Wall"
		var collider := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = rect.size
		collider.shape = shape
		collider.position = rect.position + rect.size * 0.5
		body.add_child(collider)
		add_child(body)


func _draw() -> void:
	# 地板：棋盘格 + 砖缝
	var cols := int(ceil(ROOM.size.x / TILE))
	var rows := int(ceil(ROOM.size.y / TILE))
	for row in rows:
		for col in cols:
			var tile := Rect2(
				ROOM.position + Vector2(col * TILE, row * TILE),
				Vector2(TILE, TILE)
			)
			tile = tile.intersection(ROOM)
			if tile.has_area():
				draw_rect(tile, FLOOR_A if (row + col) % 2 == 0 else FLOOR_B)

	for row in rows + 1:
		var y := ROOM.position.y + row * TILE
		if y <= ROOM.end.y:
			draw_line(Vector2(ROOM.position.x, y), Vector2(ROOM.end.x, y), FLOOR_LINE, 1.0)
	for col in cols + 1:
		var x := ROOM.position.x + col * TILE
		if x <= ROOM.end.x:
			draw_line(Vector2(x, ROOM.position.y), Vector2(x, ROOM.end.y), FLOOR_LINE, 1.0)

	# 墙：底色 + 靠屋里那一条亮边
	var walls := [
		Rect2(ROOM.position.x, ROOM.position.y, ROOM.size.x, WALL),
		Rect2(ROOM.position.x, ROOM.end.y - WALL, ROOM.size.x, WALL),
		Rect2(ROOM.position.x, ROOM.position.y, WALL, ROOM.size.y),
		Rect2(ROOM.end.x - WALL, ROOM.position.y, WALL, ROOM.size.y),
	]
	for rect in walls:
		draw_rect(rect, WALL_FILL)
	draw_rect(Rect2(ROOM.position.x + WALL, ROOM.position.y + WALL, ROOM.size.x - WALL * 2, 2), WALL_EDGE)
	draw_rect(Rect2(ROOM.position.x + WALL, ROOM.position.y + WALL, 2, ROOM.size.y - WALL * 2), WALL_EDGE)
