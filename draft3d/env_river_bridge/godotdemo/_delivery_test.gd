extends SceneTree
## 临时验证：外卖取餐 → 交付 → 金币 / 超时 流程

func _init() -> void:
	var main: Node3D = load("res://main.tscn").instantiate()
	get_root().add_child(main)
	await process_frame
	await process_frame

	var d: Node3D = main.get_node("Delivery")
	var p: Node3D = main.get_node("Player")
	var cust: Node3D = d.get_node_or_null("Customer")
	print("CUSTOMER=", cust != null, " STATE=", d.state, " COINS=", d.coins)
	if cust:
		var anim: AnimationPlayer = cust.find_child("AnimationPlayer", true, false)
		print("CUST_ANIM=", anim.current_animation, " POS=", cust.global_position)

	# 远离光圈时不能取餐
	p.global_position = Vector3(0.0, 1.45, 0.0)
	d._interact()
	print("FAR_INTERACT_STATE=", d.state, " (want 0)")

	# 取餐
	p.global_position = Vector3(-4.98, 0.37, 4.62)
	d._interact()
	print("PICK_STATE=", d.state, " TIME=", d.time_left)
	await process_frame
	print("PROMPT_AT_PICK=", d._prompt.visible, " (取餐后应为 false)")

	# 交付
	p.global_position = Vector3(5.55, 0.37, -4.86)
	d._interact()
	print("DELIVER_STATE=", d.state, " COINS=", d.coins, " ORDERS=", d.orders)
	await process_frame

	# RESULT 结束后回到 WAITING
	d._result_t = 0.0
	d._process(0.02)
	print("RESET_STATE=", d.state, " (want 0)")

	# 超时
	p.global_position = Vector3(-4.98, 0.37, 4.62)
	d._interact()
	d.time_left = 0.02
	d._process(0.05)
	print("TIMEOUT_STATE=", d.state, " TIME=", d.time_left, " COINS=", d.coins)
	print("RESULT=", "PASS" if d.orders == 1 and d.coins == 70 and cust != null else "FAIL")
	quit()
