from pathlib import Path


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP84_SHOP_GUARD_ENEMY_MOTION_APPLIED" in s:
    print("STEP84_SHOP_GUARD_ENEMY_MOTION PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP84 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP84 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP84 STEP83 anchor failed")
s = s.replace(marker, marker + "# STEP84_SHOP_GUARD_ENEMY_MOTION_APPLIED\n", 1)

const_anchor = "const ENEMY_ATTACK_ANIM_DURATION := 0.22\n"
if const_anchor not in s:
    raise SystemExit("STEP84 enemy animation constant anchor failed")
s = s.replace(const_anchor, const_anchor + "const ENEMY_MOVE_ANIM_DURATION := 0.18\n", 1)

state_anchor = "var player_hit_flash_remaining := 0.0\n"
if state_anchor not in s:
    raise SystemExit("STEP84 animation state anchor failed")
s = s.replace(state_anchor, state_anchor + "var enemy_idle_anim_time := 0.0\nvar checkout_exit_gate := false\n", 1)

# Keep enemy idle, walk, attack and hit reactions animated every frame.
process_anchor = '''\tfor flash_enemy in enemies:
\t\tvar flash_left := float(flash_enemy.get("_hit_flash", 0.0))'''
process_new = '''\tenemy_idle_anim_time = fmod(enemy_idle_anim_time + delta, 1000.0)
\tfor flash_enemy in enemies:
\t\tvar move_left := float(flash_enemy.get("_move_anim", 0.0))
\t\tif move_left > 0.0:
\t\t\tflash_enemy["_move_anim"] = maxf(0.0, move_left - delta)
\t\tvar flash_left := float(flash_enemy.get("_hit_flash", 0.0))'''
if process_anchor not in s:
    raise SystemExit("STEP84 process animation anchor failed")
s = s.replace(process_anchor, process_new, 1)

motion_anchor = "\nfunc start_enemy_attack_animation(index: int) -> void:\n"
if motion_anchor not in s:
    raise SystemExit("STEP84 motion helper anchor failed")
motion_helpers = r'''
func enemy_idle_visual_offset(enemy: Dictionary) -> Vector2:
	var phase := float(absi(str(enemy.get("name", "敵")).hash()) % 628) / 100.0
	var speed := 4.2 if bool(enemy.get("boss", false)) else 5.4
	var bob := sin(enemy_idle_anim_time * speed + phase) * (1.2 if bool(enemy.get("boss", false)) else 1.8)
	var sway := sin(enemy_idle_anim_time * speed * 0.5 + phase) * 0.8
	if int(enemy.get("bound", 0)) > 0: sway *= 0.2
	return Vector2(sway, bob)


func enemy_move_visual_offset(enemy: Dictionary, grid_size: float) -> Vector2:
	var left := float(enemy.get("_move_anim", 0.0))
	if left <= 0.0: return Vector2.ZERO
	var from_dir: Vector2 = enemy.get("_move_from", Vector2.ZERO)
	var t := clampf(left / ENEMY_MOVE_ANIM_DURATION, 0.0, 1.0)
	return from_dir * grid_size * t


func shop_exit_needs_checkout(from_pos: Vector2i, target_pos: Vector2i) -> bool:
	return is_inside_shop(from_pos) and not is_inside_shop(target_pos) and not unpaid_items.is_empty()


func request_shop_exit_checkout() -> void:
	checkout_exit_gate = true
	checkout_prompt = true
	stop_dash_hold()
	message = "未精算の商品がある。精算か品を戻す。"
	queue_redraw()


func shop_bag_has_space_for(name: String) -> bool:
	if is_projectile_name(name):
		for entry in inventory_items:
			if str(entry.get("name", "")) == name: return true
		for entry in unpaid_items:
			if str(entry.get("name", "")) == name: return true
	return inventory_items.size() + unpaid_items.size() < INVENTORY_CAPACITY


func find_shop_return_cell(preferred: Vector2i) -> Vector2i:
	if shop_rect.has_point(preferred) and is_walkable(preferred) and preferred != player and not cell_has_item(preferred) and shopkeeper.get("pos", Vector2i(-1, -1)) != preferred:
		return preferred
	for y in range(shop_rect.position.y, shop_rect.end.y):
		for x in range(shop_rect.position.x, shop_rect.end.x):
			var candidate := Vector2i(x, y)
			if is_walkable(candidate) and candidate != player and not cell_has_item(candidate) and shopkeeper.get("pos", Vector2i(-1, -1)) != candidate:
				return candidate
	return Vector2i(-1, -1)


func return_unpaid_items_to_shop() -> int:
	var returned := 0
	var remaining: Array = []
	for raw in unpaid_items:
		if typeof(raw) != TYPE_DICTIONARY: continue
		var item: Dictionary = raw.duplicate(true)
		var target := find_shop_return_cell(item.get("pos", shopkeeper_home))
		if target == Vector2i(-1, -1):
			remaining.append(item)
			continue
		item["pos"] = target
		item["shop"] = true
		items.append(item)
		returned += 1
	unpaid_items = remaining
	save_run_state()
	return returned


func draw_shop_guardian(center: Vector2, tile_size: float) -> void:
	var phase := enemy_idle_anim_time * 4.4
	var c := center + Vector2(sin(phase) * 0.8, sin(phase * 2.0) * 1.4)
	var scale := maxf(0.72, tile_size / 64.0)
	var stone := Color("#71677d") if merchant_type == "闇商人" else Color("#687581")
	var dark := stone.darkened(0.30)
	var light := stone.lightened(0.24)
	var gold := Color("#d4a94f")
	# Small wings, broad body and large head form an original two-head-tall shop guardian.
	draw_colored_polygon(PackedVector2Array([c+Vector2(-13,-5)*scale,c+Vector2(-27,-16)*scale,c+Vector2(-23,2)*scale,c+Vector2(-16,9)*scale]), dark)
	draw_colored_polygon(PackedVector2Array([c+Vector2(13,-5)*scale,c+Vector2(27,-16)*scale,c+Vector2(23,2)*scale,c+Vector2(16,9)*scale]), dark)
	draw_circle(c + Vector2(0,10)*scale, 15.0*scale, stone)
	draw_circle(c + Vector2(0,-10)*scale, 17.0*scale, light)
	draw_colored_polygon(PackedVector2Array([c+Vector2(-12,-21)*scale,c+Vector2(-6,-31)*scale,c+Vector2(-2,-20)*scale]), dark)
	draw_colored_polygon(PackedVector2Array([c+Vector2(12,-21)*scale,c+Vector2(6,-31)*scale,c+Vector2(2,-20)*scale]), dark)
	draw_circle(c + Vector2(-6,-11)*scale, 3.2*scale, Color("#f3d46b"))
	draw_circle(c + Vector2(6,-11)*scale, 3.2*scale, Color("#f3d46b"))
	draw_circle(c + Vector2(-6,-11)*scale, 1.4*scale, Color("#15131a"))
	draw_circle(c + Vector2(6,-11)*scale, 1.4*scale, Color("#15131a"))
	draw_line(c+Vector2(-5,-2)*scale,c+Vector2(5,-2)*scale,dark,2.0*scale)
	draw_rect(Rect2(c+Vector2(-13,4)*scale,Vector2(26,7)*scale),gold)
	draw_circle(c + Vector2(0,8)*scale, 3.0*scale, Color("#332719"))
	draw_line(c+Vector2(-9,22)*scale,c+Vector2(-12,29)*scale,dark,5.0*scale)
	draw_line(c+Vector2(9,22)*scale,c+Vector2(12,29)*scale,dark,5.0*scale)
'''
s = s.replace(motion_anchor, "\n" + motion_helpers.rstrip() + motion_anchor, 1)

replace_func("start_enemy_attack_animation", r'''func start_enemy_attack_animation(index: int) -> void:
	if index < 0 or index >= enemies.size(): return
	var enemy_pos: Vector2i = enemies[index]["pos"]
	var delta := player - enemy_pos
	enemies[index]["_attack_anim"] = ENEMY_ATTACK_ANIM_DURATION
	enemies[index]["_attack_dir"] = Vector2(sign(delta.x), sign(delta.y))
	queue_redraw()''')

# Animate the movement from the previous tile to the new tile.
move_old = '''\t\tif is_walkable(target) and target != player and target != clone_pos and not cell_has_enemy(target, i):
\t\t\tenemies[i]["pos"] = target'''
move_new = '''\t\tif is_walkable(target) and target != player and target != clone_pos and not cell_has_enemy(target, i):
\t\t\tenemies[i]["pos"] = target
\t\t\tenemies[i]["_move_anim"] = ENEMY_MOVE_ANIM_DURATION
\t\t\tenemies[i]["_move_from"] = Vector2(pos - target)'''
if move_old not in s:
    raise SystemExit("STEP84 enemy move anchor failed")
s = s.replace(move_old, move_new, 1)

# Block the doorway before the player can leave with unpaid goods.
merchant_old = '''\tif shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == target:
\t\tskip_auto_pickup_once = false
\t\tif shop_hostile:
\t\t\tmessage = "商人が道を塞いでいる。"
\t\telse:
\t\t\tmessage = "%s「代金を払っていきな」" % merchant_type
\t\treturn

\tvar was_inside = is_inside_shop(player)
\tplayer = target'''
merchant_new = '''\tif shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == target:
\t\tskip_auto_pickup_once = false
\t\tif shop_hostile: message = "商人が道を塞いでいる。"
\t\telif not unpaid_items.is_empty(): buy_unpaid()
\t\telse: message = "%s「品を見ていきな」" % merchant_type
\t\treturn

\tvar was_inside = is_inside_shop(player)
\tif shop_exit_needs_checkout(player, target):
\t\tskip_auto_pickup_once = false
\t\trequest_shop_exit_checkout()
\t\treturn
\tplayer = target'''
if merchant_old not in s:
    raise SystemExit("STEP84 shop exit gate anchor failed")
s = s.replace(merchant_old, merchant_new, 1)

# The post-move theft path remains only for explicit ranged stealing.
exit_old = '''\tvar now_inside = is_inside_shop(player)
\tif was_inside and not now_inside and unpaid_items.size() > 0:
\t\ttry_theft_escape()'''
exit_new = '''\tvar now_inside = is_inside_shop(player)
\tif was_inside and not now_inside and unpaid_items.size() > 0:
\t\tplayer -= dir
\t\trequest_shop_exit_checkout()
\t\treturn'''
if exit_old not in s:
    raise SystemExit("STEP84 theft fallback anchor failed")
s = s.replace(exit_old, exit_new, 1)

# Do not let the player reserve more shop goods than the bag can hold.
pickup_anchor = '''\tvar item: Dictionary = items[found]
\tvar item_name := str(item.get("name", ""))
\tif not bool(item.get("shop", false)) and not inventory_has_space_for(item_name):'''
pickup_new = '''\tvar item: Dictionary = items[found]
\tvar item_name := str(item.get("name", ""))
\tif bool(item.get("shop", false)) and not shop_bag_has_space_for(item_name):
\t\tmessage = "道具は20個まで。持ち物がいっぱいだ。"
\t\treturn
\tif not bool(item.get("shop", false)) and not inventory_has_space_for(item_name):'''
if pickup_anchor not in s:
    raise SystemExit("STEP84 shop bag capacity anchor failed")
s = s.replace(pickup_anchor, pickup_new, 1)

replace_func("buy_unpaid", r'''func buy_unpaid() -> void:
	if unpaid_items.is_empty():
		message = "未精算の商品はない。"
		return
	if shop_hostile:
		message = "商人は取引に応じない。"
		return
	checkout_exit_gate = false
	checkout_prompt = true
	message = "合計%d銭。精算しますか？" % shop_total_unpaid()
	queue_redraw()''')

replace_func("confirm_checkout", r'''func confirm_checkout(yes: bool) -> void:
	checkout_prompt = false
	if not yes:
		var returned := return_unpaid_items_to_shop()
		checkout_exit_gate = false
		message = "商品%d点を店へ戻した。" % returned
		queue_redraw()
		return
	var total = shop_total_unpaid()
	if run_coins + coins < total:
		checkout_exit_gate = false
		message = "銭が足りない。商品を店へ戻す。"
		queue_redraw()
		return
	var from_run = min(run_coins, total)
	run_coins -= from_run
	coins -= total - from_run
	for item in unpaid_items:
		add_inventory_item(str(item["name"]), false, int(item.get("count", 1)), entry_bonus(item))
	unpaid_items.clear()
	checkout_exit_gate = false
	message = "精算した。店から出られる。"
	save_run_state()
	queue_redraw()''')

# Add idle bobbing and tile-to-tile movement to all chibi enemy art.
draw_enemy_anchor = '''func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tvar is_boss := bool(enemy.get("boss", false))'''
draw_enemy_new = '''func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tcenter += enemy_idle_visual_offset(enemy)
\tcenter += enemy_move_visual_offset(enemy, minf(tile_size, 48.0))
\tvar is_boss := bool(enemy.get("boss", false))'''
if draw_enemy_anchor not in s:
    raise SystemExit("STEP84 enemy draw motion anchor failed")
s = s.replace(draw_enemy_anchor, draw_enemy_new, 1)

portrait_merchant = '''\t\tif portrait_cell_in_view(sp) and is_visible_cell(sp): draw_entity_visual(portrait_cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", "闇" if merchant_type == "闇商人" else "商", 20, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), PTILE + 11.0)'''
portrait_guard = '''\t\tif portrait_cell_in_view(sp) and is_visible_cell(sp): draw_shop_guardian(portrait_cell_center(sp), PTILE + 11.0)'''
if portrait_merchant not in s:
    raise SystemExit("STEP84 portrait merchant draw anchor failed")
s = s.replace(portrait_merchant, portrait_guard, 1)

landscape_enemy = '''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif is_visible_cell(ep):
\t\t\tvar mark = "将" if bool(e["boss"]) else "敵"
\t\t\tdraw_entity_visual(cell_center(ep), "boss" if bool(e["boss"]) else "enemy", mark, 14, Color("#e07a72"), TILE)'''
landscape_enemy_new = '''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif is_visible_cell(ep):
\t\t\tvar ec := cell_center(ep) + enemy_attack_visual_offset(e)
\t\t\tif not enemy_hit_flash_hidden(e): draw_enemy_reference_visual(ec, e, TILE + 5.0)'''
if landscape_enemy not in s:
    raise SystemExit("STEP84 landscape enemy draw anchor failed")
s = s.replace(landscape_enemy, landscape_enemy_new, 1)

landscape_merchant = '''\tif shopkeeper.size() > 0:
\t\tvar sp: Vector2i = shopkeeper["pos"]
\t\tif is_visible_cell(sp):
\t\t\tvar merchant_mark = "闇" if merchant_type == "闇商人" else "商"
\t\t\tdraw_entity_visual(cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", merchant_mark, 14, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), TILE)'''
landscape_guard = '''\tif shopkeeper.size() > 0:
\t\tvar sp: Vector2i = shopkeeper["pos"]
\t\tif is_visible_cell(sp): draw_shop_guardian(cell_center(sp), TILE + 5.0)'''
if landscape_merchant not in s:
    raise SystemExit("STEP84 landscape merchant draw anchor failed")
s = s.replace(landscape_merchant, landscape_guard, 1)

# Make the touch modal choices explicit: pay or return the goods.
portrait_labels = '''\t\tdraw_ui_text(yes.position+Vector2(138,47),"はい",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)
\t\tdraw_ui_text(no.position+Vector2(130,47),"いいえ",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)'''
portrait_labels_new = '''\t\tdraw_ui_text(yes.position+Vector2(125,47),"精算",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)
\t\tdraw_ui_text(no.position+Vector2(105,47),"品を戻す",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)'''
if portrait_labels not in s:
    raise SystemExit("STEP84 portrait checkout label anchor failed")
s = s.replace(portrait_labels, portrait_labels_new, 1)

landscape_labels = '''\t\tdraw_ui_text(yes_r.position + Vector2(48, 35), "はい", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\t\tdraw_ui_text(no_r.position + Vector2(42, 35), "いいえ", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)'''
landscape_labels_new = '''\t\tdraw_ui_text(yes_r.position + Vector2(45, 35), "精算", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\t\tdraw_ui_text(no_r.position + Vector2(25, 35), "品を戻す", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)'''
if landscape_labels not in s:
    raise SystemExit("STEP84 landscape checkout label anchor failed")
s = s.replace(landscape_labels, landscape_labels_new, 1)

# Do not restore a stale modal after loading a suspended run.
load_modal_anchor = '''\tcheckout_prompt = false
\tad_menu = false'''
if load_modal_anchor not in s:
    raise SystemExit("STEP84 load modal anchor failed")
s = s.replace(load_modal_anchor, '''\tcheckout_prompt = false
\tcheckout_exit_gate = false
\tad_menu = false''', 1)

test_anchor = "\nfunc debug_test_equipment_arsenal() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP84 test anchor failed")
test_func = r'''
func debug_test_shop_gate_and_enemy_motion() -> String:
	var old_map := map.duplicate(true); var old_player := player
	var old_items := items.duplicate(true); var old_unpaid := unpaid_items.duplicate(true)
	var old_shop_active := shop_active; var old_shop_rect := shop_rect
	var old_shopkeeper := shopkeeper.duplicate(true); var old_anim := enemy_idle_anim_time
	map = []
	for y in range(MAP_H):
		var row: Array[String] = []
		for x in range(MAP_W): row.append(".")
		map.append(row)
	shop_active = true; shop_rect = Rect2i(2, 2, 4, 4); player = Vector2i(2, 3)
	shopkeeper = {"pos":Vector2i(4, 4), "hp":999, "atk":10}
	items = []; unpaid_items = [{"pos":Vector2i(3, 3), "name":"薬", "count":1, "price":8, "shop":true}]
	var gate_ok := shop_exit_needs_checkout(player, Vector2i(1, 3)) and not shop_exit_needs_checkout(player, Vector2i(3, 3))
	var returned := return_unpaid_items_to_shop()
	var return_ok := returned == 1 and unpaid_items.is_empty() and items.size() == 1 and bool(items[0].get("shop", false))
	enemy_idle_anim_time = 0.37
	var motion_enemy := {"name":"下忍", "boss":false, "_move_anim":ENEMY_MOVE_ANIM_DURATION, "_move_from":Vector2(-1, 0)}
	var motion_ok := enemy_move_visual_offset(motion_enemy, 48.0).length() > 40.0 and enemy_idle_visual_offset(motion_enemy).length() > 0.1
	map = old_map; player = old_player; items = old_items; unpaid_items = old_unpaid
	shop_active = old_shop_active; shop_rect = old_shop_rect; shopkeeper = old_shopkeeper; enemy_idle_anim_time = old_anim
	return "PASS 商店・商品戻し・敵動作" if gate_ok and return_ok and motion_ok else "FAIL 商店・商品戻し・敵動作"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_village_trade_death_bonus_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP84 suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_shop_gate_and_enemy_motion(),\n", 1)

required = [
    "STEP84_SHOP_GUARD_ENEMY_MOTION_APPLIED",
    "func request_shop_exit_checkout(",
    "func return_unpaid_items_to_shop(",
    "func draw_shop_guardian(",
    "func enemy_move_visual_offset(",
    "debug_test_shop_gate_and_enemy_motion()",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP84 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP84 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP84_SHOP_GUARD_ENEMY_MOTION PASS")

exec(Path("tools/apply_step85_torneko_map_spawn_warehouse.py").read_text(encoding="utf-8"), {})
