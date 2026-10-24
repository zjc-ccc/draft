extends CharacterBody2D
## 蟑螂玩家预制体
##
## 贴地爬行的俯视小怪/玩家：WASD 或方向键控制，转向时整个节点跟着转，
## 所以触角、腿、朝向都是一套贴图搞定的（不需要左右翻转图）。
##
## 帧图在运行时从 `../assets/characters/cockroach/export/` 直接读，
## 素材重画之后不用重新导入，重开场景就生效。

const FRAME_DIR := "../assets/characters/cockroach/export"
const FRAME_TEMPLATE := "cockroach_walk_%02d.png"
const ACTIONS := {
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"move_up": [KEY_W, KEY_UP],
	"move_down": [KEY_S, KEY_DOWN],
}

@export_group("移动")
## 最大速度（像素/秒）
@export var speed := 130.0
## 加速度：按方向时多快加到满速
@export var accel := 1100.0
## 松开按键后的减速度
@export var brake := 1700.0
## 转身速度，越大越"急"
@export var turn_speed := 18.0

@export_group("动画")
@export var frame_count := 8
@export var animation_fps := 8.0
## 站着不动时动画降到这个倍速，触角还在慢慢动
@export var idle_speed_scale := 0.25

@onready var sprite: AnimatedSprite2D = $Sprite

## 精灵是"头朝下"画的，转到某个方向要减掉 90°
const SPRITE_HEAD_OFFSET := -PI / 2.0


func _ready() -> void:
	_ensure_actions()
	sprite.sprite_frames = _load_frames()
	sprite.play("walk")
	sprite.speed_scale = idle_speed_scale


func _physics_process(delta: float) -> void:
	var dir := Input.get_vector("move_left", "move_right", "move_up", "move_down")

	if dir.length() > 0.01:
		velocity = velocity.move_toward(dir * speed, accel * delta)
		var target := dir.angle() + SPRITE_HEAD_OFFSET
		rotation = lerp_angle(rotation, target, 1.0 - exp(-turn_speed * delta))
		sprite.speed_scale = 1.0
	else:
		velocity = velocity.move_toward(Vector2.ZERO, brake * delta)
		sprite.speed_scale = idle_speed_scale

	move_and_slide()


## 输入动作不存在时在运行期补上，工程里没配 Input Map 也能跑；
## 想改键只要工程里自己加同名 action，这里就不会覆盖。
func _ensure_actions() -> void:
	for action in ACTIONS:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action)
		for key in ACTIONS[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = key
			InputMap.action_add_event(action, ev)


func _load_frames() -> SpriteFrames:
	var frames := SpriteFrames.new()
	frames.remove_animation("default")
	frames.add_animation("walk")
	frames.set_animation_speed("walk", animation_fps)
	frames.set_animation_loop("walk", true)

	var base := ProjectSettings.globalize_path("res://").path_join(FRAME_DIR).simplify_path()
	for i in frame_count:
		var path := base.path_join(FRAME_TEMPLATE % i)
		var image := Image.load_from_file(path)
		if image == null:
			push_warning("蟑螂帧找不到：%s" % path)
			continue
		frames.add_frame("walk", ImageTexture.create_from_image(image))

	if frames.get_frame_count("walk") == 0:
		push_error("蟑螂一帧都没读到，检查 %s" % base)
	return frames
