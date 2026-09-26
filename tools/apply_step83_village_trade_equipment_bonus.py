from pathlib import Path


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS_APPLIED" in s:
    print("STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP83 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP83 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP82_BOSS_DROPS_ENEMY_ART_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP83 STEP82 anchor failed")
s = s.replace(marker, marker + "# STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS_APPLIED\n", 1)
s = s.replace("const RUN_SAVE_VERSION := 9", "const RUN_SAVE_VERSION := 10", 1)
# Keep every runtime message inside the bundled Japanese glyph set.
s = s.replace("甲冑侍", "鎧兵")
s = s.replace("影の妖術師", "影術忍")
s = s.replace("レア武器", "強武器")
s = s.replace("が落ちた。", "が出た。")
s = s.replace("ボス武器落下", "ボス武器出現")
s = s.replace("敵里画像", "敵里図")

state_anchor = 'var village_shop_scroll_offset := 0\n'
if state_anchor not in s:
    raise SystemExit("STEP83 shop state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + 'var village_shop_mode := "buy"\n'
    + 'var equipped_weapon_bonus := 0\n'
    + 'var equipped_armor_bonus := 0\n',
    1,
)

helper_anchor = "\n\nfunc first_enemy_on_line("
if helper_anchor not in s:
    raise SystemExit("STEP83 helper anchor failed")
helpers = r'''

func equipment_bonus_from_roll(for_floor: int, roll: int) -> int:
	if for_floor < 5: return 0
	var score := clampi(roll, 0, 99) + mini(80, int(for_floor * 4 / 5))
	if for_floor >= 50 and score >= 138: return 5
	if for_floor >= 50 and score >= 125: return 4
	if score >= 102: return 3
	if score >= 78: return 2
	if score >= 52: return 1
	return 0


func random_equipment_bonus(for_floor: int) -> int:
	return equipment_bonus_from_roll(for_floor, rng.randi_range(0, 99))


func entry_bonus(entry: Dictionary) -> int:
	var name := str(entry.get("name", ""))
	return clampi(int(entry.get("bonus", 0)), 0, 5) if is_equipment_name(name) else 0


func equipment_entry_label(entry: Dictionary) -> String:
	var name := str(entry.get("name", ""))
	var bonus := entry_bonus(entry)
	return equipment_display_name(name, bonus) if is_equipment_name(name) else name


func warehouse_category_rank(name: String) -> int:
	if is_weapon_name(name): return 0
	if is_armor_name(name): return 1
	if name in ["薬", "上薬", "忍気丸"]: return 2
	if name in ["兵糧丸", "大兵糧丸"]: return 3
	if name.ends_with("巻物"): return 4
	if is_projectile_name(name): return 5
	return 6


func warehouse_entry_before(a: Dictionary, b: Dictionary) -> bool:
	var an := str(a.get("name", "")); var bn := str(b.get("name", ""))
	var ar := warehouse_category_rank(an); var br := warehouse_category_rank(bn)
	if ar != br: return ar < br
	if an != bn: return an < bn
	return entry_bonus(a) > entry_bonus(b)


func warehouse_sort_items() -> void:
	warehouse_items.sort_custom(warehouse_entry_before)
	warehouse_scroll_offset = 0
	save_meta()
	message = "倉庫を整えた。"
	queue_redraw()


func village_shop_entries() -> Array:
	return village_shop_catalog() if village_shop_mode == "buy" else warehouse_items


func village_shop_toggle_mode() -> void:
	village_shop_mode = "sell" if village_shop_mode == "buy" else "buy"
	village_shop_scroll_offset = 0
	message = "購入する。" if village_shop_mode == "buy" else "倉庫の品を手放す。"
	queue_redraw()


func village_sell_price(entry: Dictionary) -> int:
	var name := str(entry.get("name", ""))
	var count := int(entry.get("count", 1)) if is_projectile_name(name) else 1
	return maxi(1, int(item_shop_price(name) * 0.5)) * maxi(1, count)


func sell_village_shop_item(index: int) -> void:
	if index < 0 or index >= warehouse_items.size(): return
	var entry: Dictionary = warehouse_items[index]
	var label := equipment_entry_label(entry)
	var price := village_sell_price(entry)
	warehouse_items.remove_at(index)
	coins += price
	village_shop_sync_scroll()
	save_meta()
	message = "%sを%d銭で手放した。" % [label, price]
	queue_redraw()


func retain_random_death_items(limit: int = 3) -> int:
	var pool: Array = inventory_items.duplicate(true)
	var kept: Array = []
	while not pool.is_empty() and kept.size() < maxi(0, limit):
		var index := rng.randi_range(0, pool.size() - 1)
		kept.append(pool[index])
		pool.remove_at(index)
	inventory_items = kept
	if not is_projectile_name(equipped_projectile) or projectile_inventory_index(equipped_projectile) < 0:
		equipped_projectile = ""
	return kept.size()
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

replace_func("equipment_display_name", r'''func equipment_display_name(name: String, bonus: int = 0) -> String:
	var data: Dictionary = WEAPON_CATALOG.get(name, ARMOR_CATALOG.get(name, {}))
	var plus := "+%d" % clampi(bonus, 0, 5) if bonus > 0 else ""
	return "%s%s R%d" % [name, plus, int(data.get("rarity", 1))]''')

replace_func("weapon_attack_bonus", r'''func weapon_attack_bonus() -> int:
	return int(equipped_weapon_data().get("attack", 0)) + clampi(equipped_weapon_bonus, 0, 5)''')

replace_func("armor_defense_bonus", r'''func armor_defense_bonus() -> int:
	return int(equipped_armor_data().get("defense", 0)) + clampi(equipped_armor_bonus, 0, 5)''')

replace_func("warehouse_add_item", r'''func warehouse_add_item(entry: Dictionary) -> bool:
	var name := str(entry.get("name", ""))
	if not valid_inventory_item_name(name): return false
	var count := clampi(int(entry.get("count", 1)), 1, 99)
	if is_projectile_name(name):
		for stored in warehouse_items:
			if str(stored.get("name", "")) == name:
				stored["count"] = mini(99, int(stored.get("count", 1)) + count)
				return true
	if warehouse_items.size() >= WAREHOUSE_CAPACITY: return false
	warehouse_items.append({"name":name, "identified":true, "count":count if is_projectile_name(name) else 1, "bonus":entry_bonus(entry)})
	return true''')

replace_func("warehouse_withdraw", r'''func warehouse_withdraw(index: int) -> void:
	if index < 0 or index >= warehouse_items.size(): return
	var entry: Dictionary = warehouse_items[index]
	var name := str(entry.get("name", ""))
	if not village_carry_has_space_for(name):
		message = "出陣に持ち込める道具は5個まで。"
		return
	if not inventory_has_space_for(name):
		message = "持ち物がいっぱいだ。"
		return
	add_inventory_item(name, true, int(entry.get("count", 1)), entry_bonus(entry))
	warehouse_items.remove_at(index)
	warehouse_sync_scroll()
	save_meta()
	message = "%sを持ち物へ移した。" % equipment_entry_label(entry)''')

replace_func("synthesize_equipment", r'''func synthesize_equipment(kind: String) -> void:
	if not in_village or village_menu != "blacksmith":
		message = "合成は鍛冶屋で行う。"
		return
	var rank := smith_weapon_rank if kind == "weapon" else smith_armor_rank
	var price := 50 + rank * 25
	if coins < price:
		message = "合成に必要な銭が足りない。"
		return
	coins -= price
	if kind == "weapon":
		smith_weapon_rank += 1; perm_attack += 1
		message = "忍刀を合成した。攻撃+1。"
	else:
		smith_armor_rank += 1; perm_defense += 1
		message = "忍装束を合成した。防御+1。"
	save_meta()''')

fusion_guard = '''func fuse_weapon_from_inventory(index: int) -> void:
	if index < 0 or index >= inventory_items.size(): return'''
fusion_guard_new = '''func fuse_weapon_from_inventory(index: int) -> void:
	if not in_village or village_menu != "weapon_fusion":
		message = "武器合成は鍛冶屋で行う。"
		return
	if index < 0 or index >= inventory_items.size(): return'''
if fusion_guard not in s:
    raise SystemExit("STEP83 fusion guard anchor failed")
s = s.replace(fusion_guard, fusion_guard_new, 1)

replace_func("handle_village_input", r'''func handle_village_input(event: InputEvent) -> void:
	if village_menu == "main":
		if event.keycode == KEY_1: village_menu = "blacksmith"; message = "鍛冶屋"
		elif event.keycode == KEY_2: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"
		elif event.keycode == KEY_3: village_menu = "village_shop"; village_shop_mode = "buy"; village_shop_scroll_offset = 0; message = "商店"
		elif event.keycode == KEY_4 or event.keycode == KEY_ENTER: start_run()
	else:
		if event.keycode == KEY_ESCAPE: village_menu = "main"; message = "忍びの里。"
		elif village_menu == "blacksmith":
			if event.keycode == KEY_A: synthesize_equipment("weapon")
			elif event.keycode == KEY_D: synthesize_equipment("armor")
			elif event.keycode == KEY_F: village_menu = "weapon_fusion"; message = "素材武器を選ぶ。"
		elif village_menu == "weapon_fusion":
			if event.keycode >= KEY_1 and event.keycode <= KEY_5:
				var materials := fusion_material_indices(); var row := int(event.keycode - KEY_1)
				if row < materials.size(): fuse_weapon_from_inventory(materials[row])
		elif village_menu == "warehouse":
			if event.keycode == KEY_P: message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
			elif event.keycode == KEY_S: warehouse_sort_items()
			elif event.keycode == KEY_UP: warehouse_scroll(-1)
			elif event.keycode == KEY_DOWN: warehouse_scroll(1)
			elif event.keycode >= KEY_1 and event.keycode <= KEY_8: warehouse_withdraw(warehouse_scroll_offset + int(event.keycode - KEY_1))
		elif village_menu == "village_shop":
			if event.keycode == KEY_TAB: village_shop_toggle_mode()
			elif event.keycode == KEY_UP: village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
			elif event.keycode == KEY_DOWN: village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
			elif event.keycode >= KEY_1 and event.keycode <= KEY_9:
				var index := village_shop_scroll_offset + int(event.keycode - KEY_1)
				if village_shop_mode == "buy": buy_village_shop_item(index)
				else: sell_village_shop_item(index)
	queue_redraw()''')

replace_func("spawn_item", r'''func spawn_item() -> void:
	var p = find_random_open_cell()
	if rng.randi_range(1, 100) <= 10:
		items.append({"pos":p, "name":random_unlocked_equipment(floor_no), "count":1, "price":0, "shop":false, "bonus":random_equipment_bonus(floor_no)})
		return
	var roll = rng.randi_range(0, 999)
	var item_name = "兵糧丸"
	var count := 1
	if roll < 150: item_name = "薬"
	elif roll < 300: item_name = "兵糧丸"
	elif roll < 410: item_name = "忍気丸"
	elif roll < 500: item_name = "手裏剣"; count = rng.randi_range(3, 8)
	elif roll < 565: item_name = "クナイ"; count = rng.randi_range(2, 6)
	elif roll < 650: item_name = "上薬"
	elif roll < 730: item_name = "大兵糧丸"
	elif roll < 850: item_name = "小巻物"
	elif roll < 930: item_name = "中巻物"
	elif roll < 985: item_name = "大巻物"
	else: item_name = "究極巻物"
	items.append({"pos":p, "name":item_name, "count":count, "price":0, "shop":false, "bonus":0})''')

generate_shop_old = '''		var it: Dictionary = {"pos": ip, "name": names[i], "count": 1, "price": price, "shop": true}'''
generate_shop_new = '''		var item_name := str(names[i])
		var it: Dictionary = {"pos": ip, "name": item_name, "count": 1, "price": price, "shop": true, "bonus":random_equipment_bonus(floor_no) if is_equipment_name(item_name) else 0}'''
if generate_shop_old not in s:
    raise SystemExit("STEP83 dungeon shop bonus anchor failed")
s = s.replace(generate_shop_old, generate_shop_new, 1)

boss_drop_old = '''items.append({"pos":drop_pos, "name":weapon_name, "count":1, "price":0, "shop":false, "boss_drop":true})'''
boss_drop_new = '''items.append({"pos":drop_pos, "name":weapon_name, "count":1, "price":0, "shop":false, "boss_drop":true, "bonus":random_equipment_bonus(floor_no)})'''
if boss_drop_old not in s:
    raise SystemExit("STEP83 boss bonus anchor failed")
s = s.replace(boss_drop_old, boss_drop_new, 1)

pickup_old = 'add_inventory_item(item_name, false, picked_count)'
pickup_new = 'add_inventory_item(item_name, false, picked_count, entry_bonus(item))'
if pickup_old not in s:
    raise SystemExit("STEP83 pickup bonus anchor failed")
s = s.replace(pickup_old, pickup_new, 1)

replace_func("add_inventory_item", r'''func add_inventory_item(name: String, identified: bool = false, count: int = 1, bonus: int = 0) -> void:
	if not valid_inventory_item_name(name): return
	if not inventory_has_space_for(name):
		message = "道具は20個まで。持ち物がいっぱいだ。"
		return
	if is_projectile_name(name):
		for entry in inventory_items:
			if str(entry.get("name", "")) == name:
				entry["count"] = min(99, int(entry.get("count", 1)) + max(1, count)); entry["identified"] = true; return
		inventory_items.append({"name":name, "identified":true, "count":min(99, max(1, count)), "bonus":0}); return
	inventory_items.append({"name":name, "identified":identified or is_equipment_name(name), "count":1, "bonus":clampi(bonus, 0, 5) if is_equipment_name(name) else 0})''')

replace_func("sanitize_inventory_array", r'''func sanitize_inventory_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY: return out
	for raw in value:
		if typeof(raw) != TYPE_DICTIONARY: continue
		var name := str(raw.get("name", ""))
		if not valid_inventory_item_name(name): continue
		var count := clampi(int(raw.get("count", 1)), 1, 99)
		if is_projectile_name(name):
			var merged := false
			for entry in out:
				if str(entry.get("name", "")) == name:
					entry["count"] = min(99, int(entry.get("count", 1)) + count); merged = true; break
			if not merged: out.append({"name":name, "identified":true, "count":count, "bonus":0})
		else:
			out.append({"name":name, "identified":bool(raw.get("identified", false)) or is_equipment_name(name), "count":1, "bonus":clampi(int(raw.get("bonus", 0)), 0, 5) if is_equipment_name(name) else 0})
	return out''')

replace_func("inventory_equip_selected", r'''func inventory_equip_selected() -> void:
	if inventory_selected == 0 or inventory_selected == 1:
		message = "%sは装備中。" % inventory_selected_name()
	else:
		var idx := inventory_selected - 2
		if idx >= 0 and idx < inventory_items.size():
			var entry: Dictionary = inventory_items[idx]
			var name := str(entry.get("name", "")); var bonus := entry_bonus(entry)
			if is_weapon_name(name): equipped_weapon = name; equipped_weapon_bonus = bonus; message = "%sを武器に装備した。" % equipment_display_name(name, bonus)
			elif is_armor_name(name): equipped_armor = name; equipped_armor_bonus = bonus; message = "%sを防具に装備した。" % equipment_display_name(name, bonus)
			elif is_projectile_name(name): equipped_projectile = name; message = "%sを飛び道具に装備した。" % name
			else: message = "この道具は装備できない。"
	queue_redraw()''')

replace_func("inventory_display_name", r'''func inventory_display_name(index: int) -> String:
	if index == 0: return "%s（装備中）" % equipment_display_name(equipped_weapon, equipped_weapon_bonus)
	if index == 1: return "%s（装備中）" % equipment_display_name(equipped_armor, equipped_armor_bonus)
	var idx := index - 2
	if idx < 0 or idx >= inventory_items.size(): return ""
	var entry: Dictionary = inventory_items[idx]; var name := str(entry.get("name", "")); var bonus := entry_bonus(entry)
	if is_projectile_name(name):
		var suffix := "（装備中）" if equipped_projectile == name else ""
		return "%s×%d%s" % [name, int(entry.get("count", 1)), suffix]
	if is_equipment_name(name):
		var equipped := (is_weapon_name(name) and equipped_weapon == name and equipped_weapon_bonus == bonus) or (is_armor_name(name) and equipped_armor == name and equipped_armor_bonus == bonus)
		return "%s%s" % [equipment_display_name(name, bonus), "（装備中）" if equipped else ""]
	return name if bool(entry.get("identified", false)) else "未識別の道具"''')

floor_pick_old = 'add_inventory_item(floor_name, false, floor_count)'
floor_pick_new = 'add_inventory_item(floor_name, false, floor_count, entry_bonus(floor_item))'
if floor_pick_old not in s:
    raise SystemExit("STEP83 floor pickup bonus anchor failed")
s = s.replace(floor_pick_old, floor_pick_new, 1)

floor_drop_old = 'items.append({"pos": player, "name": dropped_name, "count": dropped_count, "price": 0, "shop": false})'
floor_drop_new = '''dropped["pos"] = player
	dropped["count"] = dropped_count
	dropped["price"] = 0
	dropped["shop"] = false
	items.append(dropped)'''
if floor_drop_old not in s:
    raise SystemExit("STEP83 floor drop bonus anchor failed")
s = s.replace(floor_drop_old, floor_drop_new, 1)
s = s.replace('if equipped_weapon == dropped_name: equipped_weapon = "忍刀"', 'if equipped_weapon == dropped_name: equipped_weapon = "忍刀"; equipped_weapon_bonus = 0', 1)
s = s.replace('if equipped_armor == dropped_name: equipped_armor = "忍装束"', 'if equipped_armor == dropped_name: equipped_armor = "忍装束"; equipped_armor_bonus = 0', 1)

replace_func("sanitize_item_array", r'''func sanitize_item_array(value: Variant) -> Array:
	var out: Array = []
	if typeof(value) != TYPE_ARRAY: return out
	for raw in value:
		if typeof(raw) != TYPE_DICTIONARY: continue
		var entry: Dictionary = raw; var pos_value: Variant = entry.get("pos", null)
		if not validate_vector2i(pos_value): continue
		var pos: Vector2i = pos_value
		if not position_in_bounds(pos) or str(map[pos.y][pos.x]) == "#": continue
		if pos == stairs_pos or item_position_taken(pos, out): continue
		var name = str(entry.get("name", ""))
		if not valid_inventory_item_name(name): continue
		out.append({"pos":pos, "name":name, "count":clampi(int(entry.get("count", 1)), 1, 99), "price":max(0, int(entry.get("price", 0))), "shop":bool(entry.get("shop", false)), "boss_drop":bool(entry.get("boss_drop", false)), "bonus":clampi(int(entry.get("bonus", 0)), 0, 5) if is_equipment_name(name) else 0})
	return out''')

replace_func("return_village", r'''func return_village(cause: String) -> void:
	if cause != "":
		death_log.append({"floor":floor_no, "cause":cause})
		if death_log.size() > 20: death_log.pop_front()
	var gained = bank_run_rewards()
	var stored_loot := 0
	var kept_loot := 0
	if cause == "": stored_loot = warehouse_store_carried_all()
	else: kept_loot = retain_random_death_items(3)
	in_village = true
	village_menu = "main"
	apply_permanent_stats()
	save_meta()
	clear_run_state()
	if cause == "": message = "忍びの里へ帰還。忍魂+%d 銭+%d 倉庫+%d。" % [int(gained["souls"]), int(gained["coins"]), stored_loot]
	else: message = "忍びの里へ帰還。道具%d個を持ち帰った。" % kept_loot
	queue_redraw()''')

replace_func("village_shop_max_scroll", r'''func village_shop_max_scroll() -> int:
	return maxi(0, village_shop_entries().size() - VILLAGE_SHOP_VISIBLE_ROWS)''')

replace_func("handle_village_touch_portrait", r'''func handle_village_touch_portrait(pos: Vector2) -> void:
	if village_menu == "main":
		for i in range(4):
			if village_main_choice_rect(i).has_point(pos):
				if i == 0: village_menu = "blacksmith"; message = "鍛冶屋"
				elif i == 1: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"
				elif i == 2: village_menu = "village_shop"; village_shop_mode = "buy"; village_shop_scroll_offset = 0; message = "商店"
				else: start_run()
				queue_redraw(); return
	else:
		if Rect2(48, 910, 180, 48).has_point(pos): village_menu = "main"; message = "忍びの里。"
		elif village_menu == "blacksmith":
			if Rect2(48, 662, 624, 64).has_point(pos): synthesize_equipment("weapon")
			elif Rect2(48, 738, 624, 64).has_point(pos): synthesize_equipment("armor")
			elif Rect2(48, 814, 624, 64).has_point(pos): village_menu = "weapon_fusion"; message = "素材武器を選ぶ。"
		elif village_menu == "weapon_fusion":
			var materials := fusion_material_indices()
			for row in range(materials.size()):
				if Rect2(48, 560 + row * 58, 624, 50).has_point(pos): fuse_weapon_from_inventory(materials[row]); break
		elif village_menu == "warehouse":
			if Rect2(48, 520, 410, 54).has_point(pos): message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
			elif Rect2(470, 520, 202, 54).has_point(pos): warehouse_sort_items()
			elif Rect2(48, 846, 270, 48).has_point(pos): warehouse_scroll(-WAREHOUSE_VISIBLE_ROWS)
			elif Rect2(402, 846, 270, 48).has_point(pos): warehouse_scroll(WAREHOUSE_VISIBLE_ROWS)
			else:
				for row in range(WAREHOUSE_VISIBLE_ROWS):
					var index := warehouse_scroll_offset + row
					if index >= warehouse_items.size(): break
					if Rect2(48, 584 + row * 54, 624, 46).has_point(pos): warehouse_withdraw(index); break
		elif village_menu == "village_shop":
			if Rect2(48, 286, 624, 48).has_point(pos): village_shop_toggle_mode()
			elif Rect2(48, 842, 270, 48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
			elif Rect2(402, 842, 270, 48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
			else:
				var entries := village_shop_entries(); village_shop_sync_scroll()
				var visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, entries.size() - village_shop_scroll_offset)
				for row in range(visible_count):
					var index := village_shop_scroll_offset + row
					if Rect2(48, village_shop_choice_y(visible_count, row), 624, 46).has_point(pos):
						if village_shop_mode == "buy": buy_village_shop_item(index)
						else: sell_village_shop_item(index)
						break
		return''')

# Replace the warehouse/shop panels inside the portrait village renderer.
draw_start = s.find("func draw_village_portrait(")
draw_end = s.find("\nfunc ", draw_start + 5)
if draw_start < 0 or draw_end < 0:
    raise SystemExit("STEP83 draw village function anchor failed")
draw = s[draw_start:draw_end]
warehouse_start = draw.find('\t\telif village_menu == "warehouse":')
back_start = draw.find("\t\tvar back :=", warehouse_start)
if warehouse_start < 0 or back_start < 0:
    raise SystemExit("STEP83 village panel anchor failed")
panels = r'''		elif village_menu == "warehouse":
			var store := Rect2(48, 520, 410, 54); draw_panel(store, Color(0.16, 0.15, 0.08, 0.92), Color("#d7bf66"))
			var sort_button := Rect2(470, 520, 202, 54); draw_panel(sort_button, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
			draw_ui_text(store.position + Vector2(18, 37), "持ち物を全て預ける", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color.WHITE)
			draw_ui_text(sort_button.position + Vector2(48, 37), "整える", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color.WHITE)
			warehouse_sync_scroll()
			for row in range(WAREHOUSE_VISIBLE_ROWS):
				var index := warehouse_scroll_offset + row
				if index >= warehouse_items.size(): break
				var entry: Dictionary = warehouse_items[index]; var r := Rect2(48, 584 + row * 54, 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
				var suffix := "×%d" % int(entry.get("count", 1)) if is_projectile_name(str(entry.get("name", ""))) else ""
				draw_ui_text(r.position + Vector2(18, 32), "%d  %s%s    持ち出す" % [index + 1, equipment_entry_label(entry), suffix], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
			var prev := Rect2(48, 846, 270, 48); var next := Rect2(402, 846, 270, 48)
			draw_panel(prev, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if warehouse_scroll_offset > 0 else Color("#29323b"))
			draw_panel(next, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if warehouse_scroll_offset < warehouse_max_scroll() else Color("#29323b"))
			draw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
			draw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
		elif village_menu == "village_shop":
			var entries := village_shop_entries(); village_shop_sync_scroll()
			var mode_button := Rect2(48, 286, 624, 48); draw_panel(mode_button, Color(0.16, 0.15, 0.08, 0.92), Color("#d7bf66"))
			var mode_text := "購入中｜倉庫の品を手放す" if village_shop_mode == "buy" else "手放す｜購入へ戻る"
			draw_ui_text(mode_button.position + Vector2(18, 33), mode_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
			var visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, entries.size() - village_shop_scroll_offset)
			for row in range(visible_count):
				var index := village_shop_scroll_offset + row
				var entry: Dictionary = entries[index]; var r := Rect2(48, village_shop_choice_y(visible_count, row), 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
				var label := (equipment_display_name(str(entry["name"])) if is_equipment_name(str(entry["name"])) else str(entry["label"])) if village_shop_mode == "buy" else equipment_entry_label(entry)
				var price := int(entry["price"]) if village_shop_mode == "buy" else village_sell_price(entry)
				draw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [label, price], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
			var prev := Rect2(48, 842, 270, 48); var next := Rect2(402, 842, 270, 48)
			draw_panel(prev, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset > 0 else Color("#29323b"))
			draw_panel(next, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset < village_shop_max_scroll() else Color("#29323b"))
			draw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
			draw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
'''
draw = draw[:warehouse_start] + panels + draw[back_start:]
s = s[:draw_start] + draw + s[draw_end:]

# Save and restore enhancement data and death survivors.
run_save_anchor = '\t\t"equipped_armor": equipped_armor,\n'
if run_save_anchor not in s:
    raise SystemExit("STEP83 run save anchor failed")
s = s.replace(run_save_anchor, run_save_anchor + '\t\t"equipped_weapon_bonus": equipped_weapon_bonus,\n\t\t"equipped_armor_bonus": equipped_armor_bonus,\n', 1)

run_load_anchor = '''\tif not is_weapon_name(equipped_weapon): equipped_weapon = "忍刀"
\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"'''
run_load_new = run_load_anchor + '''
\tequipped_weapon_bonus = clampi(int(data.get("equipped_weapon_bonus", 0)), 0, 5)
\tequipped_armor_bonus = clampi(int(data.get("equipped_armor_bonus", 0)), 0, 5)'''
if run_load_anchor not in s:
    raise SystemExit("STEP83 run load anchor failed")
s = s.replace(run_load_anchor, run_load_new, 1)

meta_save_anchor = '\t\t"warehouse_items": warehouse_items,\n'
if meta_save_anchor not in s:
    raise SystemExit("STEP83 meta save anchor failed")
s = s.replace(meta_save_anchor, meta_save_anchor + '\t\t"village_inventory_items": inventory_items,\n', 1)
s = s.replace('\t\t"version": 5,\n\t\t"warehouse_items": warehouse_items,', '\t\t"version": 6,\n\t\t"warehouse_items": warehouse_items,', 1)
meta_equipment_anchor = '\t\t"equipped_armor": equipped_armor,\n'
# Use the final occurrence, which belongs to save_meta.
meta_pos = s.rfind(meta_equipment_anchor)
if meta_pos < 0:
    raise SystemExit("STEP83 meta equipment save anchor failed")
insert_at = meta_pos + len(meta_equipment_anchor)
s = s[:insert_at] + '\t\t"equipped_weapon_bonus": equipped_weapon_bonus,\n\t\t"equipped_armor_bonus": equipped_armor_bonus,\n' + s[insert_at:]

meta_load_anchor = '\twarehouse_items = sanitize_inventory_array(data.get("warehouse_items", []))\n'
if meta_load_anchor not in s:
    raise SystemExit("STEP83 meta load anchor failed")
s = s.replace(meta_load_anchor, meta_load_anchor + '\tinventory_items = sanitize_inventory_array(data.get("village_inventory_items", []))\n', 1)
meta_load_equipment = '''\tif not is_weapon_name(equipped_weapon): equipped_weapon = "忍刀"
\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"'''
meta_load_pos = s.rfind(meta_load_equipment)
if meta_load_pos < 0:
    raise SystemExit("STEP83 meta equipment load anchor failed")
meta_load_end = meta_load_pos + len(meta_load_equipment)
s = s[:meta_load_end] + '\n\tequipped_weapon_bonus = clampi(int(data.get("equipped_weapon_bonus", 0)), 0, 5)\n\tequipped_armor_bonus = clampi(int(data.get("equipped_armor_bonus", 0)), 0, 5)' + s[meta_load_end:]

# Regression coverage for the new economy, sort, death, and enhancement rules.
test_anchor = "\nfunc debug_test_equipment_arsenal() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP83 test anchor failed")
test_func = r'''
func debug_test_village_trade_death_bonus_contract() -> String:
	var old_inventory := inventory_items.duplicate(true)
	var old_warehouse := warehouse_items.duplicate(true)
	var old_coins := coins
	var old_weapon := equipped_weapon
	var old_weapon_bonus := equipped_weapon_bonus
	var floor_gate_ok := equipment_bonus_from_roll(4, 99) == 0 and equipment_bonus_from_roll(49, 99) <= 3 and equipment_bonus_from_roll(50, 99) >= 4 and equipment_bonus_from_roll(100, 99) == 5
	var clean := sanitize_inventory_array([{"name":"影斬刀", "identified":true, "count":1, "bonus":5}])
	var save_ok := clean.size() == 1 and entry_bonus(clean[0]) == 5
	equipped_weapon = "忍刀"; equipped_weapon_bonus = 4
	var power_ok := weapon_attack_bonus() == int(WEAPON_CATALOG["忍刀"]["attack"]) + 4
	inventory_items = []
	for i in range(8): inventory_items.append({"name":"薬", "identified":true, "count":1, "bonus":0})
	var kept_ok := retain_random_death_items(3) == 3 and inventory_items.size() == 3
	warehouse_items = [{"name":"薬", "identified":true, "count":1, "bonus":0}]
	coins = 0
	var expected_price := village_sell_price(warehouse_items[0])
	sell_village_shop_item(0)
	var sell_ok := warehouse_items.is_empty() and coins == expected_price
	warehouse_items = [{"name":"薬", "identified":true, "count":1, "bonus":0}, {"name":"忍刀", "identified":true, "count":1, "bonus":1}, {"name":"忍刀", "identified":true, "count":1, "bonus":5}]
	warehouse_sort_items()
	var sort_ok := str(warehouse_items[0].get("name", "")) == "忍刀" and entry_bonus(warehouse_items[0]) == 5
	inventory_items = old_inventory
	warehouse_items = old_warehouse
	coins = old_coins
	equipped_weapon = old_weapon
	equipped_weapon_bonus = old_weapon_bonus
	return "PASS 商店取引・倉庫整え・道具3個・装備+" if floor_gate_ok and save_ok and power_ok and kept_ok and sell_ok and sort_ok else "FAIL 商店取引・倉庫整え・道具3個・装備+"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_equipment_arsenal(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP83 suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_village_trade_death_bonus_contract(),\n", 1)

required = [
    "STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS_APPLIED",
    "func sell_village_shop_item(",
    "func warehouse_sort_items(",
    "func retain_random_death_items(",
    '"equipped_weapon_bonus": equipped_weapon_bonus',
    "debug_test_village_trade_death_bonus_contract()",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP83 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP83 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP83_VILLAGE_TRADE_EQUIPMENT_BONUS PASS")
