from pathlib import Path


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP86_VILLAGE_SOURCES_ATTACK_BUTTON_APPLIED" in s:
    print("STEP86_VILLAGE_SOURCES_ATTACK_BUTTON PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP86 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP86 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP85_TORNEKO_MAP_SPAWN_WAREHOUSE_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP86 STEP85 anchor failed")
s = s.replace(marker, marker + "# STEP86_VILLAGE_SOURCES_ATTACK_BUTTON_APPLIED\n", 1)

state_anchor = "var warehouse_store_selected: Dictionary = {}\n"
if state_anchor not in s:
    raise SystemExit("STEP86 source state anchor failed")
s = s.replace(state_anchor, state_anchor + "var fusion_scroll_offset := 0\n", 1)

# Weapon fusion can consume a material from either the carried bag or storage.
replace_func("fusion_material_indices", r'''func fusion_material_indices() -> Array[int]:
	return fusion_material_indices_for_source("bag")


func fusion_material_indices_for_source(source: String) -> Array[int]:
	var source_items: Array = inventory_items if source == "bag" else warehouse_items
	var result: Array[int] = []
	for index in range(source_items.size()):
		var name := str(source_items[index].get("name", ""))
		if is_weapon_name(name) and name != equipped_weapon: result.append(index)
	return result


func fusion_source_items(source: String) -> Array:
	return inventory_items if source == "bag" else warehouse_items


func fusion_max_scroll(source: String) -> int:
	return maxi(0, fusion_material_indices_for_source(source).size() - 6)


func fusion_scroll(source: String, rows: int) -> void:
	fusion_scroll_offset = clampi(fusion_scroll_offset + rows, 0, fusion_max_scroll(source))
	queue_redraw()''')

replace_func("fuse_weapon_from_inventory", r'''func fuse_weapon_from_inventory(index: int) -> void:
	fuse_weapon_from_source("bag", index)


func fuse_weapon_from_source(source: String, index: int) -> void:
	if not in_village or not village_menu.begins_with("weapon_fusion"):
		message = "武器合成は鍛冶屋で行う。"
		return
	var source_items: Array = fusion_source_items(source)
	if index < 0 or index >= source_items.size(): return
	var material_name := str(source_items[index].get("name", ""))
	if not is_weapon_name(material_name) or material_name == equipped_weapon:
		message = "素材にできる別の武器を選ぶ。"
		return
	var before := weapon_inherited_effects(equipped_weapon)
	var after := merge_unique_effects(before, weapon_all_effects(material_name))
	if after.size() == before.size():
		message = "新しく継承できる効果がない。"
		return
	weapon_fusion_states[equipped_weapon] = after
	if source == "bag": inventory_items.remove_at(index)
	else: warehouse_items.remove_at(index)
	fusion_scroll_offset = 0
	message = "%sの効果を%sへ継承した。" % [material_name, equipped_weapon]
	save_meta()
	queue_redraw()''')

# Swing the equipped weapon without stepping into the facing tile.
attack_anchor = "\nfunc try_move(dir: Vector2i) -> void:\n"
if attack_anchor not in s:
    raise SystemExit("STEP86 attack helper anchor failed")
attack_func = r'''
func attack_in_place() -> void:
	if in_village or inventory_menu or checkout_prompt or stairs_prompt or ad_menu: return
	stop_dash_hold()
	if facing_dir == Vector2i.ZERO: facing_dir = Vector2i(0, 1)
	if try_weapon_reach_attack(facing_dir):
		skip_auto_pickup_once = false
		end_turn()
		return
	var target := player + facing_dir
	start_melee_attack_animation(facing_dir, target)
	var index := enemy_index_at(target)
	if index >= 0: attack_enemy(index, facing_dir)
	else: message = "攻撃した。"
	skip_auto_pickup_once = false
	end_turn()
'''
s = s.replace(attack_anchor, "\n" + attack_func.rstrip() + attack_anchor, 1)

# Replace the portrait touch handler with source-selection screens and a 3+2 command layout.
replace_func("handle_press_portrait", r'''func handle_press_portrait(pos: Vector2) -> void: # STEP64_CONTROLS_PATCH_APPLIED
	if in_village:
		handle_village_touch_portrait(pos)
		return
	if inventory_menu:
		handle_inventory_touch(pos, true)
		return
	if checkout_prompt or stairs_prompt or ad_menu:
		handle_modal_touch_portrait(pos)
		return
	if Rect2(22,662,76,76).has_point(pos): toggle_map_visibility(); return
	var command_buttons = [
		[Vector2(78,840),39.0,"inventory"], [Vector2(174,840),39.0,"trap"], [Vector2(270,840),39.0,"attack"],
		[Vector2(126,936),39.0,"technique"], [Vector2(222,936),39.0,"throw"]
	]
	for button in command_buttons:
		if pos.distance_to(button[0]) <= float(button[1]):
			var action := str(button[2])
			if action == "inventory": open_inventory()
			elif action == "trap": place_trap()
			elif action == "attack": attack_in_place()
			elif action == "technique": hide_one_turn()
			elif action == "throw": use_projectile()
			queue_redraw(); return
	if Rect2(54,1002,240,44).has_point(pos): suspend_run(); return
	var base := Vector2(390,770); var cell := 96.0
	if pos.x >= base.x and pos.x < base.x+cell*3.0 and pos.y >= base.y and pos.y < base.y+cell*3.0:
		var cx := int((pos.x-base.x)/cell); var cy := int((pos.y-base.y)/cell); var d := Vector2i(cx-1,cy-1)
		if d == Vector2i.ZERO: stop_dash_hold(); start_center_hold(); return
		if direction_only_mode:
			stop_dash_hold(); facing_dir = d; message = "向きを変えた。"; queue_redraw(); return
		start_dash_hold(d)''')

replace_func("handle_village_touch_portrait", r'''func handle_village_touch_portrait(pos: Vector2) -> void:
	if village_menu == "main":
		for i in range(4):
			if village_main_choice_rect(i).has_point(pos):
				if i == 0: village_menu = "blacksmith"; message = "鍛冶屋"
				elif i == 1: village_menu = "warehouse_select"; message = "中を見る場所を選ぶ。"
				elif i == 2: village_menu = "village_shop"; village_shop_mode = "buy"; village_shop_scroll_offset = 0; message = "商店"
				else: start_run()
				queue_redraw(); return
		return
	if Rect2(48,910,180,48).has_point(pos):
		if village_menu in ["warehouse_bag","warehouse_storage"]: village_menu = "warehouse_select"; message = "中を見る場所を選ぶ。"
		elif village_menu in ["weapon_fusion_bag","weapon_fusion_storage"]: village_menu = "weapon_fusion_source"; message = "素材の場所を選ぶ。"
		elif village_menu == "weapon_fusion_source": village_menu = "blacksmith"; message = "鍛冶屋"
		elif village_menu == "warehouse_select": village_menu = "main"; message = "忍びの里。"
		else: village_menu = "main"; message = "忍びの里。"
		queue_redraw(); return
	if village_menu == "blacksmith":
		if Rect2(48,628,624,76).has_point(pos): synthesize_equipment("weapon")
		elif Rect2(48,716,624,76).has_point(pos): synthesize_equipment("armor")
		elif Rect2(48,804,624,76).has_point(pos): village_menu = "weapon_fusion_source"; fusion_scroll_offset = 0; message = "素材の場所を選ぶ。"
	elif village_menu == "warehouse_select":
		if Rect2(48,548,624,90).has_point(pos): village_menu = "warehouse_bag"; warehouse_bag_scroll = 0; warehouse_bag_selected.clear(); message = "道具袋"
		elif Rect2(48,660,624,90).has_point(pos): village_menu = "warehouse_storage"; warehouse_scroll_offset = 0; warehouse_store_selected.clear(); message = "倉庫"
	elif village_menu == "warehouse_bag":
		if Rect2(48,790,270,48).has_point(pos): warehouse_bag_scroll = maxi(0,warehouse_bag_scroll-8)
		elif Rect2(402,790,270,48).has_point(pos): warehouse_bag_scroll = mini(maxi(0,inventory_items.size()-8),warehouse_bag_scroll+8)
		elif Rect2(48,850,624,48).has_point(pos): store_selected_bag_items()
		else:
			for row in range(8):
				if Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(true,warehouse_bag_scroll+row); break
	elif village_menu == "warehouse_storage":
		if Rect2(48,790,270,48).has_point(pos): warehouse_scroll_offset = maxi(0,warehouse_scroll_offset-8)
		elif Rect2(402,790,270,48).has_point(pos): warehouse_scroll_offset = mini(maxi(0,warehouse_items.size()-8),warehouse_scroll_offset+8)
		elif Rect2(48,850,410,48).has_point(pos): withdraw_selected_warehouse_items()
		elif Rect2(470,850,202,48).has_point(pos): warehouse_sort_items(); warehouse_store_selected.clear()
		else:
			for row in range(8):
				if Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(false,warehouse_scroll_offset+row); break
	elif village_menu == "weapon_fusion_source":
		if Rect2(48,548,624,90).has_point(pos): village_menu = "weapon_fusion_bag"; fusion_scroll_offset = 0; message = "道具袋から素材を選ぶ。"
		elif Rect2(48,660,624,90).has_point(pos): village_menu = "weapon_fusion_storage"; fusion_scroll_offset = 0; message = "倉庫から素材を選ぶ。"
	elif village_menu in ["weapon_fusion_bag","weapon_fusion_storage"]:
		var source := "bag" if village_menu == "weapon_fusion_bag" else "warehouse"
		var materials := fusion_material_indices_for_source(source)
		if Rect2(48,790,270,48).has_point(pos): fusion_scroll(source,-6)
		elif Rect2(402,790,270,48).has_point(pos): fusion_scroll(source,6)
		else:
			for row in range(6):
				var material_row := fusion_scroll_offset+row
				if material_row >= materials.size(): break
				if Rect2(48,430+row*58,624,50).has_point(pos): fuse_weapon_from_source(source,materials[material_row]); break
	elif village_menu == "village_shop":
		if Rect2(48,286,624,48).has_point(pos): village_shop_toggle_mode()
		elif Rect2(48,842,270,48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
		elif Rect2(402,842,270,48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
		else:
			var entries := village_shop_entries(); village_shop_sync_scroll()
			var visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
			for row in range(visible_count):
				var index := village_shop_scroll_offset+row
				if Rect2(48,village_shop_choice_y(visible_count,row),624,46).has_point(pos):
					if village_shop_mode == "buy": buy_village_shop_item(index)
					else: sell_village_shop_item(index)
					break''')

# Replace the village renderer so each source opens as its own scrollable screen.
replace_func("draw_village_portrait", r'''func draw_village_portrait() -> void:
	var scene_key := village_menu
	if village_menu.begins_with("weapon_fusion"): scene_key = "blacksmith"
	elif village_menu.begins_with("warehouse"): scene_key = "warehouse"
	if not VILLAGE_SCENE_PATHS.has(scene_key): scene_key = "main"
	var scene_texture := get_village_scene_texture(scene_key)
	if scene_texture != null: draw_texture_rect(scene_texture,Rect2(0,0,720,1100),false)
	else: draw_rect(Rect2(0,0,720,1100),Color("#0a1017"))
	draw_rect(Rect2(0,0,720,1100),Color(0.015,0.025,0.045,0.12))
	draw_rect(Rect2(0,0,720,198),Color(0.03,0.055,0.09,0.82)); draw_rect(Rect2(0,195,720,3),Color("#d3b35b"))
	draw_ui_text(Vector2(46,72),"忍びの里",HORIZONTAL_ALIGNMENT_LEFT,-1,44,Color("#e8d47f"))
	draw_ui_text(Vector2(48,122),"忍魂 %d    銭 %d" % [souls,coins],HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color("#e4e8ed"))
	draw_ui_text(Vector2(48,162),"最高到達 %dF    倉庫 %d/50    持込 %d/5" % [village_unlocked_floor(),warehouse_items.size(),inventory_items.size()],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("#aeb7c2"))
	if village_menu == "main":
		var labels = ["鍛冶屋","倉庫","商店","出陣"]; var notes = ["装備を合成","50個まで保管","品物を購入","探索を始める"]
		for i in range(4):
			var r := village_main_choice_rect(i); var fill := Color(0.16,0.15,0.08,0.92) if i==3 else Color(0.04,0.07,0.10,0.90)
			draw_panel(r,fill,Color("#d7bf66") if i==3 else Color("#687786"),2.0)
			draw_ui_text(r.position+Vector2(0,35),labels[i],HORIZONTAL_ALIGNMENT_CENTER,r.size.x,24,Color("#f0f2f5"))
			draw_ui_text(r.position+Vector2(0,64),notes[i],HORIZONTAL_ALIGNMENT_CENTER,r.size.x,15,Color("#c8d0d8"))
	else:
		var title := "鍛冶屋"
		if village_menu.begins_with("warehouse"): title = "倉庫"
		elif village_menu.begins_with("weapon_fusion"): title = "武器合成"
		elif village_menu == "village_shop": title = "商店"
		draw_ui_text(Vector2(48,244),title,HORIZONTAL_ALIGNMENT_LEFT,-1,32,Color("#e8d47f"))
		if village_menu == "blacksmith":
			var weapon_price := 50+smith_weapon_rank*25; var armor_price := 50+smith_armor_rank*25
			var labels := ["武器を鍛える","防具を鍛える","武器効果を合成"]
			var details := ["%s  +%d → +%d　%d銭" % [equipped_weapon,smith_weapon_rank,smith_weapon_rank+1,weapon_price],"%s  +%d → +%d　%d銭" % [equipped_armor,smith_armor_rank,smith_armor_rank+1,armor_price],"道具袋か倉庫から素材を選ぶ"]
			for i in range(3):
				var r := Rect2(48,628+i*88,624,76); draw_panel(r,Color(0.035,0.065,0.09,0.94),Color("#d7bf66") if i==2 else Color("#7c8997"),2.2)
				draw_ui_text(r.position+Vector2(20,32),labels[i],HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color("#f5e3a1") if i==2 else Color.WHITE)
				draw_ui_text(r.position+Vector2(20,61),details[i],HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#c7d0d8"))
		elif village_menu in ["warehouse_select","weapon_fusion_source"]:
			var first_label := "道具袋" if village_menu=="warehouse_select" else "道具袋から選ぶ"
			var second_label := "倉庫" if village_menu=="warehouse_select" else "倉庫から選ぶ"
			var first := Rect2(48,548,624,90); var second := Rect2(48,660,624,90)
			for r in [first,second]: draw_panel(r,Color(0.04,0.07,0.10,0.94),Color("#d7bf66"),2.2)
			draw_ui_text(first.position+Vector2(0,55),first_label,HORIZONTAL_ALIGNMENT_CENTER,first.size.x,24,Color.WHITE)
			draw_ui_text(second.position+Vector2(0,55),second_label,HORIZONTAL_ALIGNMENT_CENTER,second.size.x,24,Color.WHITE)
		elif village_menu in ["warehouse_bag","warehouse_storage"]:
			var from_bag := village_menu=="warehouse_bag"; var source_items: Array = inventory_items if from_bag else warehouse_items
			var offset := warehouse_bag_scroll if from_bag else warehouse_scroll_offset
			draw_ui_text(Vector2(48,292),("道具袋 %d/5" if from_bag else "倉庫 %d/50") % source_items.size(),HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color.WHITE)
			for row in range(8):
				var index := offset+row
				if index >= source_items.size(): break
				var selected := warehouse_bag_selected.has(index) if from_bag else warehouse_store_selected.has(index)
				var r := Rect2(48,318+row*56,624,48); draw_panel(r,Color("#253d52") if selected else Color(0.04,0.07,0.10,0.92),Color("#f0c75e") if selected else Color("#687786"),2.0)
				draw_ui_text(r.position+Vector2(16,33),("● " if selected else "○ ")+equipment_entry_label(source_items[index]),HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
			var prev := Rect2(48,790,270,48); var next := Rect2(402,790,270,48)
			for r in [prev,next]: draw_panel(r,Color("#101923"),Color("#687786"))
			draw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE)
			draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)
			if from_bag:
				var action := Rect2(48,850,624,48); draw_panel(action,Color("#62521f"),Color("#f0c75e")); draw_ui_text(action.position+Vector2(0,33),"選択を倉庫へ預ける",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,18,Color.WHITE)
			else:
				var action := Rect2(48,850,410,48); var sort_button := Rect2(470,850,202,48)
				draw_panel(action,Color("#24405b"),Color("#78b9e8")); draw_panel(sort_button,Color("#101923"),Color("#687786"))
				draw_ui_text(action.position+Vector2(0,33),"選択を道具袋へ移す",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,18,Color.WHITE)
				draw_ui_text(sort_button.position+Vector2(0,33),"整える",HORIZONTAL_ALIGNMENT_CENTER,sort_button.size.x,17,Color.WHITE)
		elif village_menu in ["weapon_fusion_bag","weapon_fusion_storage"]:
			var source := "bag" if village_menu=="weapon_fusion_bag" else "warehouse"; var source_items := fusion_source_items(source); var materials := fusion_material_indices_for_source(source)
			draw_ui_text(Vector2(48,300),"ベース：%s（見た目を維持）" % equipped_weapon,HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color.WHITE)
			draw_ui_text(Vector2(48,342),"継承：%s" % weapon_effect_summary(weapon_inherited_effects(equipped_weapon)).left(34),HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("#e8d47f"))
			draw_ui_text(Vector2(48,386),"%sの素材武器" % ("道具袋" if source=="bag" else "倉庫"),HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("#d8dee5"))
			if materials.is_empty(): draw_ui_text(Vector2(48,470),"合成できる武器がない。",HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color.WHITE)
			for row in range(6):
				var material_row := fusion_scroll_offset+row
				if material_row >= materials.size(): break
				var index := materials[material_row]; var name := str(source_items[index].get("name","")); var r := Rect2(48,430+row*58,624,50)
				draw_panel(r,Color(0.04,0.07,0.10,0.92),Color("#687786")); draw_ui_text(r.position+Vector2(16,34),"%s  %s" % [equipment_entry_label(source_items[index]),weapon_effect_summary(weapon_all_effects(name)).left(24)],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE)
			var prev := Rect2(48,790,270,48); var next := Rect2(402,790,270,48)
			for r in [prev,next]: draw_panel(r,Color("#101923"),Color("#687786"))
			draw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)
		elif village_menu == "village_shop":
			var entries := village_shop_entries(); village_shop_sync_scroll(); var mode_button := Rect2(48,286,624,48); draw_panel(mode_button,Color(0.16,0.15,0.08,0.92),Color("#d7bf66"))
			var mode_text := "購入中｜倉庫の品を手放す" if village_shop_mode=="buy" else "手放す｜購入へ戻る"; draw_ui_text(mode_button.position+Vector2(18,33),mode_text,HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
			var visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
			for row in range(visible_count):
				var index := village_shop_scroll_offset+row; var entry: Dictionary = entries[index]; var r := Rect2(48,village_shop_choice_y(visible_count,row),624,46); draw_panel(r,Color(0.04,0.07,0.10,0.90),Color("#687786"))
				var label := (equipment_display_name(str(entry["name"])) if is_equipment_name(str(entry["name"])) else str(entry["label"])) if village_shop_mode=="buy" else equipment_entry_label(entry); var price := int(entry["price"]) if village_shop_mode=="buy" else village_sell_price(entry)
				draw_ui_text(r.position+Vector2(16,31),"%s    %d銭" % [label,price],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE)
			var prev := Rect2(48,842,270,48); var next := Rect2(402,842,270,48); draw_panel(prev,Color("#101923"),Color("#687786")); draw_panel(next,Color("#101923"),Color("#687786"))
			draw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)
		var back := Rect2(48,910,180,48); draw_panel(back,Color(0.04,0.07,0.10,0.92),Color("#687786")); draw_ui_text(back.position+Vector2(0,33),"戻る",HORIZONTAL_ALIGNMENT_CENTER,back.size.x,20,Color.WHITE)
	draw_panel(Rect2(40,984,640,70),Color(0.04,0.07,0.10,0.90),Color("#394653"),1.0); draw_ui_text(Vector2(54,1028),message.left(40),HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("#e5d37d")); draw_ui_text(Vector2(465,46),"Ver.%s" % VERSION,HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#7f8b98"))''')

replace_func("draw_mobile_controls_portrait", r'''func draw_mobile_controls_portrait() -> void:
	draw_rect(Rect2(0,760,720,340),Color("#06101c"))
	draw_colored_polygon(PackedVector2Array([Vector2(0,1098),Vector2(0,1018),Vector2(70,978),Vector2(126,1024),Vector2(205,966),Vector2(285,1035),Vector2(360,990),Vector2(430,1045),Vector2(520,978),Vector2(610,1030),Vector2(720,970),Vector2(720,1100)]),Color("#0b1b2c"))
	for leaf in [Vector2(36,1044),Vector2(334,1030),Vector2(675,1008),Vector2(698,930)]: draw_reference_leaf(leaf,0.65)
	var command_buttons = [["道具",Vector2(78,840),39.0],["罠",Vector2(174,840),39.0],["攻撃",Vector2(270,840),39.0],["術",Vector2(126,936),39.0],["飛",Vector2(222,936),39.0]]
	var gold := Color("#d6a74f")
	for button in command_buttons:
		var label := str(button[0]); var c: Vector2 = button[1]; var radius := float(button[2]); var attack_button := label=="攻撃"
		draw_circle(c+Vector2(0,4),radius+2.0,Color(0,0,0,0.28)); draw_circle(c,radius+3.0,Color("#101b2a")); draw_circle(c,radius,Color("#582a2a") if attack_button else Color("#1b2d45"))
		draw_arc(c,radius+2.0,0.0,TAU,52,Color("#8d6631"),1.5); draw_arc(c,radius,0.0,TAU,52,Color("#e57b69") if attack_button else gold,2.8)
		draw_step67_command_icon(label,c)
		draw_ui_text(c+Vector2(-18 if label.length()>1 else -9,29),label,HORIZONTAL_ALIGNMENT_LEFT,-1,15 if label.length()>1 else 18,Color("#fff0e5") if attack_button else Color("#f4f1e8"))
	var suspend := Rect2(54,1002,240,44); draw_panel(suspend,Color("#101923"),Color("#687786"),1.5); draw_ui_text(suspend.position+Vector2(0,30),"中断",HORIZONTAL_ALIGNMENT_CENTER,suspend.size.x,16,Color.WHITE)
	var base := Vector2(390,770); var cell := 96.0; var labels = [["↖","↑","↗"],["←","","→"],["↙","↓","↘"]]
	for y in range(3):
		for x in range(3):
			var r := Rect2(base.x+x*cell,base.y+y*cell,88.0,88.0); var center := x==1 and y==1
			if center:
				var cc := r.get_center(); draw_circle(cc+Vector2(0,4),41.0,Color(0,0,0,0.30)); draw_circle(cc,39.0,Color("#17283e")); draw_arc(cc,39.0,0.0,TAU,52,gold,2.7)
				if direction_only_mode: draw_circle(cc,19.0,Color("#f4f5f2")); draw_arc(cc,22.0,0.0,TAU,40,Color("#9eabb8"),2.0)
				else: draw_arc(cc,19.0,0.0,TAU,40,Color("#f4f5f2"),3.0)
			else:
				draw_rect(r,Color("#101a29")); draw_rect(r.grow(-3.0),Color("#20344e")); draw_rect(r,Color("#8d6631"),false,1.2); draw_rect(r.grow(-2.0),gold,false,2.2)
				draw_ui_text(r.position+Vector2(29,57),labels[y][x],HORIZONTAL_ALIGNMENT_LEFT,-1,28,Color("#f4f1e8"))''')

# Regression: storage fusion, source menus and the no-step attack action remain wired.
test_anchor = "\nfunc debug_test_step85_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP86 test anchor failed")
test_func = r'''
func debug_test_step86_contract() -> String:
	var old_menu := village_menu; var old_weapon := equipped_weapon; var old_inventory := inventory_items.duplicate(true); var old_warehouse := warehouse_items.duplicate(true); var old_states := weapon_fusion_states.duplicate(true)
	village_menu = "weapon_fusion_storage"; equipped_weapon = "忍刀"; inventory_items = []; warehouse_items = [{"name":"双牙刀","identified":true,"count":1,"bonus":0}]; weapon_fusion_states = {}
	fuse_weapon_from_source("warehouse",0)
	var storage_fusion_ok := warehouse_items.is_empty() and weapon_has_effect("double_strike")
	var source_ok := fusion_material_indices_for_source("bag").is_empty() and fusion_material_indices_for_source("warehouse").is_empty()
	var attack_ok := has_method("attack_in_place")
	village_menu = old_menu; equipped_weapon = old_weapon; inventory_items = old_inventory; warehouse_items = old_warehouse; weapon_fusion_states = old_states
	return "PASS 倉庫選択合成攻撃" if storage_fusion_ok and source_ok and attack_ok else "FAIL 倉庫選択合成攻撃"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step85_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP86 suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step86_contract(),\n", 1)

required = [
    "STEP86_VILLAGE_SOURCES_ATTACK_BUTTON_APPLIED",
    "func attack_in_place(",
    "weapon_fusion_storage",
    "warehouse_select",
    'Vector2(270,840),39.0,"attack"',
    "debug_test_step86_contract()",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP86 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP86 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP86_VILLAGE_SOURCES_ATTACK_BUTTON PASS")
