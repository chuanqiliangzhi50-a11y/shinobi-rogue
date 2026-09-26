from pathlib import Path


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE_APPLIED" in s:
    print("STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP85 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP85 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP84_SHOP_GUARD_ENEMY_MOTION_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP85 STEP84 anchor failed")
s = s.replace(marker, marker + "# STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE_APPLIED\n", 1)

s = s.replace("const RUN_SAVE_VERSION := 10", "const RUN_SAVE_VERSION := 11", 1)

const_anchor = "const ENEMY_MOVE_ANIM_DURATION := 0.18\n"
if const_anchor not in s:
    raise SystemExit("STEP85 constant anchor failed")
s = s.replace(
    const_anchor,
    const_anchor
    + "const ENEMY_RESPAWN_TURNS := 30\n"
    + "const ENEMY_RESPAWN_CAP := 14\n"
    + "const WAREHOUSE_MULTI_ROWS := 7\n",
    1,
)

state_anchor = "var checkout_exit_gate := false\n"
if state_anchor not in s:
    raise SystemExit("STEP85 state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + "var floor_turns_elapsed := 0\n"
    + "var warehouse_bag_scroll := 0\n"
    + "var warehouse_bag_selected: Dictionary = {}\n"
    + "var warehouse_store_selected: Dictionary = {}\n",
    1,
)

# Honor alignment and width, and give every bitmap glyph the same baseline and shadow.
replace_func("draw_ui_text", r'''func ui_text_line_width(text: String, font_size: int) -> float:
	var width := 0.0
	for i in range(text.length()):
		var code := text.unicode_at(i)
		width += float(font_size) * (0.62 if code < 128 else 1.0)
	return width


func draw_ui_glyph_line(start: Vector2, text: String, font_size: int, color: Color) -> void:
	var x := roundf(start.x)
	var y := roundf(start.y - float(font_size) * 0.84)
	var scale := float(font_size) / UI_GLYPH_BASE
	for i in range(text.length()):
		var ch := text.substr(i, 1)
		var code := ch.unicode_at(0)
		var advance := float(font_size) * (0.62 if code < 128 else 1.0)
		var dst_size := Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL) * scale
		var dst := Rect2(Vector2(x, y), dst_size)
		var shadow_dst := Rect2(dst.position + Vector2(1.0, 1.5), dst.size)
		if UI_GLYPH_MAP.has(ch):
			var cell_pos: Vector2i = UI_GLYPH_MAP[ch]
			var src := Rect2(Vector2(cell_pos.x, cell_pos.y) * UI_GLYPH_CELL, Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL))
			draw_texture_rect_region(ui_glyph_texture, shadow_dst, src, Color(0, 0, 0, color.a * 0.55))
			draw_texture_rect_region(ui_glyph_texture, dst, src, color)
		elif extra_ui_glyphs.has(ch):
			var extra_tex: Texture2D = extra_ui_glyphs[ch]
			draw_texture_rect(extra_tex, shadow_dst, false, Color(0, 0, 0, color.a * 0.55))
			draw_texture_rect(extra_tex, dst, false, color)
		x += advance


func draw_ui_text(pos: Vector2, text: String, alignment: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT, width: float = -1.0, font_size: int = 16, color: Color = Color.WHITE) -> void:
	if ui_glyph_texture == null: return
	var lines := text.split("\n")
	for row in range(lines.size()):
		var line := str(lines[row])
		var line_width := ui_text_line_width(line, font_size)
		var start_x := pos.x
		if width > 0.0 and alignment == HORIZONTAL_ALIGNMENT_CENTER: start_x += (width - line_width) * 0.5
		elif width > 0.0 and alignment == HORIZONTAL_ALIGNMENT_RIGHT: start_x += width - line_width
		draw_ui_glyph_line(Vector2(start_x, pos.y + float(row * font_size) * 1.25), line, font_size, color)''')

# Map marks are revealed only on explored cells. Enemies remain red and stairs yellow.
replace_func("draw_explored_minimap_portrait", r'''func map_cell_was_explored(pos: Vector2i) -> bool:
	return position_in_bounds(pos) and validate_grid(explored) and bool(explored[pos.y][pos.x])


func draw_explored_minimap_portrait() -> void:
	if not validate_grid(explored): return
	var cell: float = 9.0
	var map_size := Vector2(float(MAP_W) * cell, float(MAP_H) * cell)
	var origin := Vector2(690.0 - map_size.x, 214.0)
	var frame := Rect2(origin - Vector2(8, 8), map_size + Vector2(16, 16))
	draw_rect(frame, Color(0.02, 0.03, 0.04, 0.82), true)
	draw_rect(frame, Color(0.82, 0.72, 0.36, 0.78), false, 1.5)
	for y in range(MAP_H):
		for x in range(MAP_W):
			var pos := Vector2i(x, y)
			if not map_cell_was_explored(pos) or str(map[y][x]) == "#": continue
			var col := Color(0.55, 0.62, 0.70, 0.62)
			if pos == stairs_pos: col = Color(1.0, 0.82, 0.12, 1.0)
			draw_rect(Rect2(origin + Vector2(float(x) * cell + 1.0, float(y) * cell + 1.0), Vector2(cell - 2.0, cell - 2.0)), col, true)
	for raw_enemy in enemies:
		var enemy: Dictionary = raw_enemy
		var enemy_pos: Vector2i = enemy["pos"]
		if map_cell_was_explored(enemy_pos):
			draw_circle(origin + Vector2((float(enemy_pos.x) + 0.5) * cell, (float(enemy_pos.y) + 0.5) * cell), 3.5, Color(1.0, 0.18, 0.18, 1.0))
	for raw_item in items:
		var item: Dictionary = raw_item
		var item_pos: Vector2i = item["pos"]
		if map_cell_was_explored(item_pos):
			draw_circle(origin + Vector2((float(item_pos.x) + 0.5) * cell, (float(item_pos.y) + 0.5) * cell), 2.3, Color(0.42, 0.86, 0.58, 0.95))
	draw_circle(origin + Vector2((float(player.x) + 0.5) * cell, (float(player.y) + 0.5) * cell), 4.2, Color(0.45, 0.82, 1.0, 1.0))''')

# Reset the floor-local respawn clock whenever a new floor is created.
generate_anchor = '''func generate_floor() -> void:
	explored = make_bool_grid(false); visible_now = make_bool_grid(false)'''
if generate_anchor not in s:
    raise SystemExit("STEP85 generate floor anchor failed")
s = s.replace(generate_anchor, '''func generate_floor() -> void:
	floor_turns_elapsed = 0
	explored = make_bool_grid(false); visible_now = make_bool_grid(false)''', 1)

# Give every enemy a facing direction and preserve it through save/load.
spawn_anchor = '''		"soul_reward": int(profile["soul_reward"])
	}'''
if spawn_anchor not in s:
    raise SystemExit("STEP85 spawn facing anchor failed")
s = s.replace(spawn_anchor, '''		"soul_reward": int(profile["soul_reward"]),
		"_facing": [Vector2i(0,1), Vector2i(1,0), Vector2i(0,-1), Vector2i(-1,0)][rng.randi_range(0,3)]
	}''', 1)

sanitize_anchor = '''			"soul_reward": max(0, int(entry.get("soul_reward", 3 if is_boss else 1)))
		})'''
if sanitize_anchor not in s:
    raise SystemExit("STEP85 sanitize facing anchor failed")
s = s.replace(sanitize_anchor, '''			"soul_reward": max(0, int(entry.get("soul_reward", 3 if is_boss else 1))),
			"_facing": entry.get("_facing", Vector2i(0,1)) if validate_vector2i(entry.get("_facing", null)) else Vector2i(0,1)
		})''', 1)

attack_anchor = '''	var delta := player - enemy_pos
	enemies[index]["_attack_anim"] = ENEMY_ATTACK_ANIM_DURATION'''
if attack_anchor not in s:
    raise SystemExit("STEP85 attack facing anchor failed")
s = s.replace(attack_anchor, '''	var delta := player - enemy_pos
	enemies[index]["_facing"] = Vector2i(sign(delta.x), sign(delta.y))
	enemies[index]["_attack_anim"] = ENEMY_ATTACK_ANIM_DURATION''', 1)

move_anchor = '''			enemies[i]["pos"] = target
			enemies[i]["_move_anim"] = ENEMY_MOVE_ANIM_DURATION'''
if move_anchor not in s:
    raise SystemExit("STEP85 move facing anchor failed")
s = s.replace(move_anchor, '''			enemies[i]["pos"] = target
			enemies[i]["_facing"] = step
			enemies[i]["_move_anim"] = ENEMY_MOVE_ANIM_DURATION''', 1)

respawn_anchor = "\nfunc has_clear_shot(source: Vector2i, target_pos: Vector2i, max_range: int) -> bool:\n"
if respawn_anchor not in s:
    raise SystemExit("STEP85 respawn helper anchor failed")
respawn_helpers = r'''
func find_timed_enemy_spawn_cell() -> Vector2i:
	for _attempt in range(140):
		var pos := Vector2i(rng.randi_range(1, MAP_W - 2), rng.randi_range(1, MAP_H - 2))
		if not is_walkable(pos) or occupied(pos) or cell_has_item(pos) or pos == stairs_pos: continue
		if max(absi(pos.x - player.x), absi(pos.y - player.y)) < 7: continue
		if is_visible_cell(pos): continue
		return pos
	return Vector2i(-1, -1)


func spawn_timed_enemy() -> bool:
	if enemies.size() >= ENEMY_RESPAWN_CAP: return false
	var pos := find_timed_enemy_spawn_cell()
	if pos == Vector2i(-1, -1): return false
	var profile := enemy_profile(false)
	enemies.append({
		"pos":pos, "hp":int(profile["hp"]), "atk":int(profile["atk"]), "bound":0,
		"boss":false, "name":str(profile["name"]), "kind":str(profile["kind"]),
		"range":int(profile["range"]), "coin_reward":int(profile["coin_reward"]),
		"soul_reward":int(profile["soul_reward"]), "_facing":Vector2i(0,1)
	})
	return true
'''
s = s.replace(respawn_anchor, "\n" + respawn_helpers.rstrip() + respawn_anchor, 1)

end_turn_anchor = '''	turn_no += 1
	hunger_tick += 1'''
if end_turn_anchor not in s:
    raise SystemExit("STEP85 turn clock anchor failed")
s = s.replace(end_turn_anchor, '''	turn_no += 1
	floor_turns_elapsed += 1
	hunger_tick += 1''', 1)

move_call_anchor = '''	move_enemies()
	trigger_enemy_traps()'''
if move_call_anchor not in s:
    raise SystemExit("STEP85 respawn call anchor failed")
s = s.replace(move_call_anchor, '''	move_enemies()
	trigger_enemy_traps()
	if floor_turns_elapsed >= ENEMY_RESPAWN_TURNS:
		floor_turns_elapsed = 0
		if spawn_timed_enemy(): message = "遠くで新たな敵の気配がした。"''', 1)

save_anchor = '''		"turn_no": turn_no,
		"player_level": player_level,'''
if save_anchor not in s:
    raise SystemExit("STEP85 save clock anchor failed")
s = s.replace(save_anchor, '''		"turn_no": turn_no,
		"floor_turns_elapsed": floor_turns_elapsed,
		"player_level": player_level,''', 1)

load_anchor = '''	turn_no = max(0, int(data.get("turn_no", 0)))
	player_level = clampi'''
if load_anchor not in s:
    raise SystemExit("STEP85 load clock anchor failed")
s = s.replace(load_anchor, '''	turn_no = max(0, int(data.get("turn_no", 0)))
	floor_turns_elapsed = clampi(int(data.get("floor_turns_elapsed", 0)), 0, ENEMY_RESPAWN_TURNS - 1)
	player_level = clampi''', 1)

# Draw chibi enemies with a horizontal flip, lean and trailing cloth based on facing.
replace_func("draw_roster_cell", r'''func draw_enemy_direction_cloth(center: Vector2, direction: Vector2i, size: float) -> void:
	var dir := Vector2(direction)
	if dir == Vector2.ZERO: dir = Vector2(0, 1)
	dir = dir.normalized()
	var side := Vector2(-dir.y, dir.x)
	var back := -dir
	var root := center + back * size * 0.12
	var points := PackedVector2Array([root + side * size * 0.12, root + back * size * 0.38, root - side * size * 0.12])
	draw_colored_polygon(points, Color("#a62f3b"))


func draw_roster_cell(texture: Texture2D, index: int, cells: int, center: Vector2, tile_size: float, direction: Vector2i = Vector2i(0, 1)) -> void:
	var cell_width := float(texture.get_width()) / float(cells)
	var source := Rect2(cell_width * float(index), 0.0, cell_width, float(texture.get_height()))
	var size := maxf(34.0, tile_size + 15.0)
	var aspect := cell_width / maxf(1.0, float(texture.get_height()))
	draw_enemy_direction_cloth(center, direction, size)
	var flip_x := -1.0 if direction.x < 0 else 1.0
	var lean := 0.06 * float(sign(direction.x))
	var vertical_scale := 0.93 if direction.y < 0 else 1.0
	draw_set_transform(center, lean, Vector2(flip_x, vertical_scale))
	var dest := Rect2(Vector2(-size * aspect, -size) * 0.5, Vector2(size * aspect, size))
	var tint := Color(0.82, 0.86, 0.92) if direction.y < 0 else Color.WHITE
	draw_texture_rect_region(texture, dest, source, tint)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)''')

enemy_call_1 = '''	if is_boss and boss_roster_texture != null:
		draw_roster_cell(boss_roster_texture, boss_roster_index(str(enemy.get("name", ""))), 4, center, tile_size)'''
enemy_call_1_new = '''	var direction: Vector2i = enemy.get("_facing", Vector2i(0,1))
	if is_boss and boss_roster_texture != null:
		draw_roster_cell(boss_roster_texture, boss_roster_index(str(enemy.get("name", ""))), 4, center, tile_size, direction)'''
if enemy_call_1 not in s:
    raise SystemExit("STEP85 boss facing draw anchor failed")
s = s.replace(enemy_call_1, enemy_call_1_new, 1)
s = s.replace(
    'draw_roster_cell(enemy_roster_texture, normal_enemy_roster_index(str(enemy.get("kind", "samurai"))), 5, center, tile_size)',
    'draw_roster_cell(enemy_roster_texture, normal_enemy_roster_index(str(enemy.get("kind", "samurai"))), 5, center, tile_size, direction)',
    1,
)

# Stair confirmation must always use yes/no, while checkout keeps pay/return.
replace_func("draw_modal_overlay_portrait", r'''func draw_modal_overlay_portrait() -> void:
	if checkout_prompt or stairs_prompt:
		draw_rect(Rect2(100,340,520,330),Color(0.05,0.07,0.09,0.97))
		draw_rect(Rect2(100,340,520,330),Color("#e4cf7a"),false,3)
		draw_ui_text(Vector2(180,420), "商品を精算しますか？" if checkout_prompt else "次の階に降りますか？", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color.WHITE)
		var yes := Rect2(190,465,340,70); var no := Rect2(190,555,340,70)
		for r in [yes,no]:
			draw_rect(r,Color("#252c35")); draw_rect(r,Color("#596575"),false,2)
		if checkout_prompt:
			draw_ui_text(yes.position+Vector2(0,47),"精算",HORIZONTAL_ALIGNMENT_CENTER,yes.size.x,24,Color.WHITE)
			draw_ui_text(no.position+Vector2(0,47),"品を戻す",HORIZONTAL_ALIGNMENT_CENTER,no.size.x,24,Color.WHITE)
		else:
			draw_ui_text(yes.position+Vector2(0,47),"はい",HORIZONTAL_ALIGNMENT_CENTER,yes.size.x,24,Color.WHITE)
			draw_ui_text(no.position+Vector2(0,47),"いいえ",HORIZONTAL_ALIGNMENT_CENTER,no.size.x,24,Color.WHITE)
	else:
		draw_rect(Rect2(40,320,640,360),Color(0.05,0.07,0.09,0.97)); draw_rect(Rect2(40,320,640,360),Color("#e4cf7a"),false,3)
		draw_ui_text(Vector2(85,400),"任意広告ブースト（試作）",HORIZONTAL_ALIGNMENT_LEFT,-1,26,Color.WHITE)
		var labels = ["忍気","能力","全回復","見ない"]
		var rects = [Rect2(80,500,250,70),Rect2(390,500,250,70),Rect2(80,590,250,70),Rect2(390,590,250,70)]
		for i in range(4):
			draw_rect(rects[i],Color("#252c35")); draw_rect(rects[i],Color("#596575"),false,2)
			draw_ui_text(rects[i].position+Vector2(0,47),labels[i],HORIZONTAL_ALIGNMENT_CENTER,rects[i].size.x,22,Color.WHITE)''')

replace_func("draw_modal_overlay", r'''func draw_modal_overlay() -> void:
	draw_rect(Rect2(220,220,660,260),Color(0.05,0.07,0.09,0.96)); draw_rect(Rect2(220,220,660,260),Color("#e4cf7a"),false,2)
	if checkout_prompt or stairs_prompt:
		draw_ui_text(Vector2(285,300),"商品を精算しますか？" if checkout_prompt else "次の階に降りますか？",HORIZONTAL_ALIGNMENT_LEFT,-1,25,Color.WHITE)
		var yes_r := Rect2(350,390,160,54); var no_r := Rect2(590,390,160,54)
		for r in [yes_r,no_r]: draw_panel(r,Color("#252c35"),Color("#596575"),1)
		var yes_label := "精算" if checkout_prompt else "はい"
		var no_label := "品を戻す" if checkout_prompt else "いいえ"
		draw_ui_text(yes_r.position+Vector2(0,35),yes_label,HORIZONTAL_ALIGNMENT_CENTER,yes_r.size.x,20,Color.WHITE)
		draw_ui_text(no_r.position+Vector2(0,35),no_label,HORIZONTAL_ALIGNMENT_CENTER,no_r.size.x,20,Color.WHITE)
	else:
		draw_ui_text(Vector2(285,285),"任意広告ブースト（試作）",HORIZONTAL_ALIGNMENT_LEFT,-1,23,Color.WHITE)
		var labels = ["忍気","能力","全回復","見ない"]; var xs = [255,405,555,705]
		for i in range(labels.size()):
			var r := Rect2(xs[i],355,130,54); draw_panel(r,Color("#252c35"),Color("#596575"),1)
			draw_ui_text(r.position+Vector2(0,35),labels[i],HORIZONTAL_ALIGNMENT_CENTER,r.size.x,17,Color.WHITE)''')

# Multi-select warehouse helpers.
warehouse_anchor = "\nfunc village_unlocked_floor() -> int:\n"
if warehouse_anchor not in s:
    raise SystemExit("STEP85 warehouse helper anchor failed")
warehouse_helpers = r'''
func warehouse_bag_max_scroll() -> int:
	return maxi(0, inventory_items.size() - WAREHOUSE_MULTI_ROWS)


func warehouse_multi_sync() -> void:
	warehouse_bag_scroll = clampi(warehouse_bag_scroll, 0, warehouse_bag_max_scroll())
	warehouse_scroll_offset = clampi(warehouse_scroll_offset, 0, maxi(0, warehouse_items.size() - WAREHOUSE_MULTI_ROWS))
	for key in warehouse_bag_selected.keys():
		if int(key) < 0 or int(key) >= inventory_items.size(): warehouse_bag_selected.erase(key)
	for key in warehouse_store_selected.keys():
		if int(key) < 0 or int(key) >= warehouse_items.size(): warehouse_store_selected.erase(key)


func toggle_warehouse_selection(from_bag: bool, index: int) -> void:
	var source := inventory_items if from_bag else warehouse_items
	if index < 0 or index >= source.size(): return
	var selected := warehouse_bag_selected if from_bag else warehouse_store_selected
	if selected.has(index): selected.erase(index)
	else: selected[index] = true
	queue_redraw()


func clear_warehouse_selections() -> void:
	warehouse_bag_selected.clear(); warehouse_store_selected.clear(); queue_redraw()


func store_selected_bag_items() -> int:
	var indices: Array = warehouse_bag_selected.keys(); indices.sort(); indices.reverse()
	var moved := 0
	for raw_index in indices:
		var index := int(raw_index)
		if index < 0 or index >= inventory_items.size(): continue
		if warehouse_add_item(inventory_items[index]): inventory_items.remove_at(index); moved += 1
	warehouse_bag_selected.clear(); warehouse_multi_sync()
	if moved > 0: save_meta()
	message = "%d個を倉庫へ預けた。" % moved
	return moved


func withdraw_selected_warehouse_items() -> int:
	var indices: Array = warehouse_store_selected.keys(); indices.sort(); indices.reverse()
	var moved := 0
	for raw_index in indices:
		var index := int(raw_index)
		if index < 0 or index >= warehouse_items.size(): continue
		var before := warehouse_items.size(); warehouse_withdraw(index)
		if warehouse_items.size() < before: moved += 1
	warehouse_store_selected.clear(); warehouse_multi_sync()
	message = "%d個を道具袋へ移した。" % moved
	return moved
'''
s = s.replace(warehouse_anchor, "\n" + warehouse_helpers.rstrip() + warehouse_anchor, 1)

# Touch layout: both lists are visible and each side supports multi-selection.
touch_start = s.find('func handle_village_touch_portrait(pos: Vector2) -> void:')
touch_end = s.find('\nfunc handle_modal_touch_portrait', touch_start)
if touch_start < 0 or touch_end < 0:
    raise SystemExit("STEP85 village touch block failed")
touch = s[touch_start:touch_end]
old_warehouse_touch_start = touch.find('\t\telif village_menu == "warehouse":')
old_shop_touch_start = touch.find('\t\telif village_menu == "village_shop":', old_warehouse_touch_start)
if old_warehouse_touch_start < 0 or old_shop_touch_start < 0:
    raise SystemExit("STEP85 warehouse touch anchors failed")
new_warehouse_touch = r'''		elif village_menu == "warehouse":
			warehouse_multi_sync()
			if Rect2(48,768,300,54).has_point(pos): store_selected_bag_items()
			elif Rect2(372,768,300,54).has_point(pos): withdraw_selected_warehouse_items()
			elif Rect2(48,834,300,48).has_point(pos): clear_warehouse_selections(); message = "選択を解除した。"
			elif Rect2(372,834,300,48).has_point(pos): warehouse_sort_items(); warehouse_store_selected.clear(); warehouse_multi_sync()
			elif Rect2(48,712,142,44).has_point(pos): warehouse_bag_scroll = maxi(0, warehouse_bag_scroll - WAREHOUSE_MULTI_ROWS)
			elif Rect2(206,712,142,44).has_point(pos): warehouse_bag_scroll = mini(warehouse_bag_max_scroll(), warehouse_bag_scroll + WAREHOUSE_MULTI_ROWS)
			elif Rect2(372,712,142,44).has_point(pos): warehouse_scroll_offset = maxi(0, warehouse_scroll_offset - WAREHOUSE_MULTI_ROWS)
			elif Rect2(530,712,142,44).has_point(pos): warehouse_scroll_offset = mini(maxi(0, warehouse_items.size()-WAREHOUSE_MULTI_ROWS), warehouse_scroll_offset + WAREHOUSE_MULTI_ROWS)
			else:
				for row in range(WAREHOUSE_MULTI_ROWS):
					if Rect2(48,336+row*52,300,46).has_point(pos): toggle_warehouse_selection(true,warehouse_bag_scroll+row); break
					if Rect2(372,336+row*52,300,46).has_point(pos): toggle_warehouse_selection(false,warehouse_scroll_offset+row); break
'''
touch = touch[:old_warehouse_touch_start] + new_warehouse_touch + touch[old_shop_touch_start:]
s = s[:touch_start] + touch + s[touch_end:]

# Replace the portrait warehouse panel, and shorten the blacksmith choices.
draw_start = s.find("func draw_village_portrait() -> void:")
draw_end = s.find("\nfunc draw_dungeon_portrait", draw_start)
if draw_start < 0 or draw_end < 0:
    raise SystemExit("STEP85 village draw block failed")
draw = s[draw_start:draw_end]

blacksmith_start = draw.find('\t\tif village_menu == "blacksmith":')
fusion_start = draw.find('\t\telif village_menu == "weapon_fusion":', blacksmith_start)
if blacksmith_start < 0 or fusion_start < 0:
    raise SystemExit("STEP85 blacksmith draw anchors failed")
blacksmith_panel = r'''		if village_menu == "blacksmith":
			var weapon_price := 50 + smith_weapon_rank * 25
			var armor_price := 50 + smith_armor_rank * 25
			var labels := ["武器を鍛える", "防具を鍛える", "武器効果を合成"]
			var details := ["%s  +%d → +%d　%d銭" % [equipped_weapon,smith_weapon_rank,smith_weapon_rank+1,weapon_price], "%s  +%d → +%d　%d銭" % [equipped_armor,smith_armor_rank,smith_armor_rank+1,armor_price], "素材武器の効果を継承"]
			for i in range(3):
				var r := Rect2(48,628+i*88,624,76); draw_panel(r,Color(0.035,0.065,0.09,0.94),Color("#d7bf66") if i==2 else Color("#7c8997"),2.2)
				draw_ui_text(r.position+Vector2(20,32),labels[i],HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color("#f5e3a1") if i==2 else Color.WHITE)
				draw_ui_text(r.position+Vector2(20,61),details[i],HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#c7d0d8"))
'''
draw = draw[:blacksmith_start] + blacksmith_panel + draw[fusion_start:]

warehouse_start = draw.find('\t\telif village_menu == "warehouse":')
shop_start = draw.find('\t\telif village_menu == "village_shop":', warehouse_start)
if warehouse_start < 0 or shop_start < 0:
    raise SystemExit("STEP85 warehouse draw anchors failed")
warehouse_panel = r'''		elif village_menu == "warehouse":
			warehouse_multi_sync()
			var bag_head := Rect2(48,286,300,40); var store_head := Rect2(372,286,300,40)
			draw_panel(bag_head,Color("#17293d"),Color("#d7bf66")); draw_panel(store_head,Color("#17293d"),Color("#d7bf66"))
			draw_ui_text(bag_head.position+Vector2(0,29),"道具袋 %d/5" % inventory_items.size(),HORIZONTAL_ALIGNMENT_CENTER,bag_head.size.x,18,Color.WHITE)
			draw_ui_text(store_head.position+Vector2(0,29),"倉庫 %d/50" % warehouse_items.size(),HORIZONTAL_ALIGNMENT_CENTER,store_head.size.x,18,Color.WHITE)
			for row in range(WAREHOUSE_MULTI_ROWS):
				var bag_index := warehouse_bag_scroll + row
				var store_index := warehouse_scroll_offset + row
				if bag_index < inventory_items.size():
					var entry: Dictionary = inventory_items[bag_index]; var r := Rect2(48,336+row*52,300,46); var selected := warehouse_bag_selected.has(bag_index)
					draw_panel(r,Color("#253d52") if selected else Color(0.04,0.07,0.10,0.92),Color("#f0c75e") if selected else Color("#687786"),2.0)
					draw_ui_text(r.position+Vector2(12,31),("● " if selected else "○ ")+equipment_entry_label(entry).left(13),HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color.WHITE)
				if store_index < warehouse_items.size():
					var entry: Dictionary = warehouse_items[store_index]; var r := Rect2(372,336+row*52,300,46); var selected := warehouse_store_selected.has(store_index)
					draw_panel(r,Color("#253d52") if selected else Color(0.04,0.07,0.10,0.92),Color("#f0c75e") if selected else Color("#687786"),2.0)
					draw_ui_text(r.position+Vector2(12,31),("● " if selected else "○ ")+equipment_entry_label(entry).left(13),HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color.WHITE)
			var buttons := [Rect2(48,712,142,44),Rect2(206,712,142,44),Rect2(372,712,142,44),Rect2(530,712,142,44)]
			var labels := ["前へ","次へ","前へ","次へ"]
			for i in range(4): draw_panel(buttons[i],Color("#101923"),Color("#687786")); draw_ui_text(buttons[i].position+Vector2(0,30),labels[i],HORIZONTAL_ALIGNMENT_CENTER,buttons[i].size.x,16,Color.WHITE)
			var store_button := Rect2(48,768,300,54); var take_button := Rect2(372,768,300,54)
			draw_panel(store_button,Color("#62521f"),Color("#f0c75e")); draw_panel(take_button,Color("#24405b"),Color("#78b9e8"))
			draw_ui_text(store_button.position+Vector2(0,37),"選択を預ける",HORIZONTAL_ALIGNMENT_CENTER,store_button.size.x,19,Color.WHITE)
			draw_ui_text(take_button.position+Vector2(0,37),"選択を持ち出す",HORIZONTAL_ALIGNMENT_CENTER,take_button.size.x,19,Color.WHITE)
			var clear_button := Rect2(48,834,300,48); var sort_button := Rect2(372,834,300,48)
			draw_panel(clear_button,Color("#101923"),Color("#687786")); draw_panel(sort_button,Color("#101923"),Color("#687786"))
			draw_ui_text(clear_button.position+Vector2(0,33),"選択を解除",HORIZONTAL_ALIGNMENT_CENTER,clear_button.size.x,17,Color.WHITE)
			draw_ui_text(sort_button.position+Vector2(0,33),"倉庫を整える",HORIZONTAL_ALIGNMENT_CENTER,sort_button.size.x,17,Color.WHITE)
'''
draw = draw[:warehouse_start] + warehouse_panel + draw[shop_start:]
s = s[:draw_start] + draw + s[draw_end:]

# Regression checks for the new contracts.
test_anchor = "\nfunc debug_test_shop_gate_and_enemy_motion() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP85 test anchor failed")
test_func = r'''
func debug_test_step85_contract() -> String:
	var old_inventory := inventory_items.duplicate(true); var old_warehouse := warehouse_items.duplicate(true)
	var old_bag_selected := warehouse_bag_selected.duplicate(true); var old_store_selected := warehouse_store_selected.duplicate(true)
	inventory_items = [{"name":"薬","identified":true,"count":1},{"name":"兵糧丸","identified":true,"count":1}]
	warehouse_items = [{"name":"忍気丸","identified":true,"count":1}]
	warehouse_bag_selected = {0:true,1:true}; warehouse_store_selected = {}
	var stored_ok := store_selected_bag_items() == 2 and inventory_items.is_empty() and warehouse_items.size() == 3
	warehouse_store_selected = {1:true,2:true}
	var withdrew_ok := withdraw_selected_warehouse_items() == 2 and inventory_items.size() == 2 and warehouse_items.size() == 1
	var map_ok := Color(1.0,0.18,0.18,1.0).r > 0.9 and Color(1.0,0.82,0.12,1.0).g > 0.8
	var respawn_ok := ENEMY_RESPAWN_TURNS == 30 and ENEMY_RESPAWN_CAP == 14
	var direction_ok := Vector2i(-1,0).x < 0
	inventory_items = old_inventory; warehouse_items = old_warehouse
	warehouse_bag_selected = old_bag_selected; warehouse_store_selected = old_store_selected
	return "PASS 階段地図敵出現字体鍛冶倉庫選択" if stored_ok and withdrew_ok and map_ok and respawn_ok and direction_ok else "FAIL 階段地図敵出現字体鍛冶倉庫選択"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_shop_gate_and_enemy_motion(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP85 suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step85_contract(),\n", 1)

required = [
    "STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE_APPLIED",
    "const ENEMY_RESPAWN_TURNS := 30",
    "func map_cell_was_explored(",
    "func spawn_timed_enemy(",
    "func store_selected_bag_items(",
    "func withdraw_selected_warehouse_items(",
    "debug_test_step85_contract()",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP85 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP85 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE PASS")
