extends SceneTree
## 临时验证：取餐后站到收货点，截一张图看顾客与 HUD

func _init() -> void:
	var main: Node3D = load("res://main.tscn").instantiate()
	get_root().add_child(main)
	await process_frame
	var d: Node3D = main.get_node("Delivery")
	var p: Node3D = main.get_node("Player")

	p.global_position = Vector3(-4.98, 0.37, 4.62)
	d._interact()
	p.global_position = Vector3(5.55, 0.37, -4.18)
	p.rotation.y = 0.0            # 面向 -Z，正对顾客
	for i in 50:
		await process_frame
	await RenderingServer.frame_post_draw
	var img := get_root().get_texture().get_image()
	img.save_png("res://drop_shot.png")
	print("DROP_SHOT ", img.get_size(), " COINS=", d.coins, " TIME=", d.time_left)
	quit()
