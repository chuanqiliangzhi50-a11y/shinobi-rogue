from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP81_WEAPON_FUSION_APPLIED" in s:
    print("STEP81_WEAPON_FUSION PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP81 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP81 function end failed: {name}")
    s = s[:start] + body.rstrip() + s[end:]


marker = "# STEP80_EQUIPMENT_ARSENAL_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP81 STEP80 anchor failed")
s = s.replace(marker, marker + "# STEP81_WEAPON_FUSION_APPLIED\n", 1)

glyph_anchor = '\t"制": "res://art/step76_glyphs/u5236.svg"\n}'
glyph_rows = '''\t"制": "res://art/step76_glyphs/u5236.svg",
\t"双": "res://art/step76_glyphs/u53cc.svg",
\t"斬": "res://art/step76_glyphs/u65ac.svg",
\t"乱": "res://art/step76_glyphs/u4e71.svg",
\t"網": "res://art/step76_glyphs/u7db2.svg",
\t"鉄": "res://art/step76_glyphs/u9244.svg",
\t"縫": "res://art/step76_glyphs/u7e2b.svg",
\t"羽": "res://art/step76_glyphs/u7fbd.svg",
\t"鋼": "res://art/step76_glyphs/u92fc.svg",
\t"巾": "res://art/step76_glyphs/u5dfe.svg",
\t"マ": "res://art/step76_glyphs/u30de.svg",
\t"直": "res://art/step76_glyphs/u76f4.svg",
\t"バ": "res://art/step76_glyphs/u30d0.svg",
\t"〜": "res://art/step76_glyphs/u301c.svg",
\t"範": "res://art/step76_glyphs/u7bc4.svg",
\t"素": "res://art/step76_glyphs/u7d20.svg",
\t"新": "res://art/step76_glyphs/u65b0.svg",
\t"効": "res://art/step76_glyphs/u52b9.svg",
\t"有": "res://art/step76_glyphs/u6709.svg",
\t"継": "res://art/step76_glyphs/u7d99.svg",
\t"切": "res://art/step76_glyphs/u5207.svg",
\t"ベ": "res://art/step76_glyphs/u30d9.svg",
\t"舞": "res://art/step76_glyphs/u821e.svg",
\t"織": "res://art/step76_glyphs/u7e54.svg",
\t"貫": "res://art/step76_glyphs/u8cab.svg",
\t"囲": "res://art/step76_glyphs/u56f2.svg",
\t"材": "res://art/step76_glyphs/u6750.svg",
\t"承": "res://art/step76_glyphs/u627f.svg",
\t"果": "res://art/step76_glyphs/u679c.svg",
\t"後": "res://art/step76_glyphs/u5f8c.svg",
\t"目": "res://art/step76_glyphs/u76ee.svg",
\t"通": "res://art/step76_glyphs/u901a.svg",
\t"退": "res://art/step76_glyphs/u9000.svg",
\t"維": "res://art/step76_glyphs/u7dad.svg",
\t"べ": "res://art/step76_glyphs/u3079.svg"
}'''
if glyph_anchor not in s:
    raise SystemExit("STEP81 glyph map anchor failed")
s = s.replace(glyph_anchor, glyph_rows, 1)

const_anchor = "const VILLAGE_SHOP_VISIBLE_ROWS := 9\n"
effect_constants = '''const WEAPON_EFFECT_LABELS := {
\t"double_strike":"2連撃",
\t"triple_strike":"3連撃",
\t"reach_2":"2マス攻撃",
\t"front_three":"前方3方向",
\t"reach_3":"3マス攻撃",
\t"pierce_3":"直線貫通",
\t"knockback":"ノックバック",
\t"random_range":"3〜5マス",
\t"wide_slash":"広範囲斬り",
\t"all_direction":"全方向攻撃",
\t"pull_6":"6マス引寄せ",
\t"ranged_throw":"遠距離手裏剣"
}
'''
if const_anchor not in s:
    raise SystemExit("STEP81 effect constant anchor failed")
s = s.replace(const_anchor, const_anchor + effect_constants, 1)

state_anchor = 'var equipped_armor := "忍装束"\n'
if state_anchor not in s:
    raise SystemExit("STEP81 fusion state anchor failed")
s = s.replace(state_anchor, state_anchor + "var weapon_fusion_states: Dictionary = {}\n", 1)

helper_anchor = "\n\nfunc first_enemy_on_line("
if helper_anchor not in s:
    raise SystemExit("STEP81 weapon helper anchor failed")
effect_helpers = '''

func valid_weapon_effect(effect_id: String) -> bool:
\treturn WEAPON_EFFECT_LABELS.has(effect_id)


func weapon_native_effects(name: String) -> Array[String]:
\tvar result: Array[String] = []
\tvar data: Dictionary = WEAPON_CATALOG.get(name, {})
\tvar raw: Variant = data.get("native_effects", [])
\tif typeof(raw) != TYPE_ARRAY: return result
\tfor value in raw:
\t\tvar effect_id := str(value)
\t\tif valid_weapon_effect(effect_id) and effect_id not in result: result.append(effect_id)
\treturn result


func weapon_inherited_effects(name: String) -> Array[String]:
\tvar result: Array[String] = []
\tvar raw: Variant = weapon_fusion_states.get(name, [])
\tif typeof(raw) != TYPE_ARRAY: return result
\tfor value in raw:
\t\tvar effect_id := str(value)
\t\tif valid_weapon_effect(effect_id) and effect_id not in result: result.append(effect_id)
\treturn result


func merge_unique_effects(base: Array[String], extra: Array[String]) -> Array[String]:
\tvar result: Array[String] = base.duplicate()
\tfor effect_id in extra:
\t\tif valid_weapon_effect(effect_id) and effect_id not in result: result.append(effect_id)
\treturn result


func weapon_all_effects(name: String = equipped_weapon) -> Array[String]:
\treturn merge_unique_effects(weapon_native_effects(name), weapon_inherited_effects(name))


func weapon_has_effect(effect_id: String) -> bool:
\treturn effect_id in weapon_all_effects(equipped_weapon)


func weapon_effect_summary(effects: Array[String]) -> String:
\tif effects.is_empty(): return "なし"
\tvar labels: Array[String] = []
\tfor effect_id in effects:
\t\tlabels.append(str(WEAPON_EFFECT_LABELS.get(effect_id, effect_id)))
\treturn "・".join(labels)


func sanitize_weapon_fusion_states(raw: Variant) -> Dictionary:
\tvar clean: Dictionary = {}
\tif typeof(raw) != TYPE_DICTIONARY: return clean
\tfor key in raw:
\t\tvar weapon_name := str(key)
\t\tif not is_weapon_name(weapon_name): continue
\t\tvar source: Variant = raw[key]
\t\tif typeof(source) != TYPE_ARRAY: continue
\t\tvar effects: Array[String] = []
\t\tfor value in source:
\t\t\tvar effect_id := str(value)
\t\t\tif valid_weapon_effect(effect_id) and effect_id not in effects: effects.append(effect_id)
\t\tif not effects.is_empty(): clean[weapon_name] = effects
\treturn clean
'''
s = s.replace(helper_anchor, effect_helpers + helper_anchor, 1)

replace_func("try_weapon_reach_attack", '''func try_weapon_reach_attack(dir: Vector2i) -> bool:
\tvar has_area := weapon_has_effect("reach_2") or weapon_has_effect("reach_3") or weapon_has_effect("random_range") or weapon_has_effect("front_three") or weapon_has_effect("wide_slash") or weapon_has_effect("all_direction")
\tif not has_area: return false
\tvar min_range := 1
\tvar max_range := 1
\tif weapon_has_effect("reach_2"): max_range = maxi(max_range, 2)
\tif weapon_has_effect("reach_3") or weapon_has_effect("pierce_3"): max_range = maxi(max_range, 3)
\tif weapon_has_effect("random_range"):
\t\tmax_range = maxi(max_range, rng.randi_range(3, 5))
\t\tif not weapon_has_effect("reach_2") and not weapon_has_effect("reach_3"): min_range = 3
\tvar dirs: Array[Vector2i] = [dir]
\tif weapon_has_effect("all_direction"): dirs = all_attack_dirs()
\telif weapon_has_effect("front_three") or weapon_has_effect("wide_slash"): dirs = front_spread_dirs(dir)
\tvar targets: Array[Vector2i] = []
\tfor attack_dir in dirs:
\t\tif weapon_has_effect("pierce_3"):
\t\t\tfor step in range(max_range, min_range - 1, -1):
\t\t\t\tvar p2 := player + attack_dir * step
\t\t\t\tif not position_in_bounds(p2) or not is_walkable(p2): continue
\t\t\t\tif enemy_index_at(p2) >= 0 and p2 not in targets: targets.append(p2)
\t\telse:
\t\t\tvar target_pos := first_enemy_on_line(attack_dir, min_range, max_range)
\t\t\tif target_pos != Vector2i(-1, -1) and target_pos not in targets: targets.append(target_pos)
\tif targets.is_empty(): return false
\tstart_melee_attack_animation(dir, targets[0])
\tvar hit_count := 0
\tfor target_pos in targets:
\t\tvar index := enemy_index_at(target_pos)
\t\tif index < 0: continue
\t\tvar attack_dir := Vector2i(clampi(target_pos.x - player.x, -1, 1), clampi(target_pos.y - player.y, -1, 1))
\t\tattack_enemy(index, attack_dir)
\t\thit_count += 1
\tif hit_count > 1: message += " %d体同時攻撃。" % hit_count
\treturn hit_count > 0''')

replace_func("attack_enemy", '''func attack_enemy(index: int, attack_dir: Vector2i = Vector2i.ZERO) -> void:
\tif index < 0 or index >= enemies.size(): return
\tif attack_dir == Vector2i.ZERO: attack_dir = facing_dir
\tattack_dir = Vector2i(clampi(attack_dir.x, -1, 1), clampi(attack_dir.y, -1, 1))
\tvar target_pos: Vector2i = enemies[index]["pos"]
\tvar requested_hits := 1
\tif weapon_has_effect("triple_strike"): requested_hits = 3
\telif weapon_has_effect("double_strike"): requested_hits = 2
\tvar actual_hits := 0
\tfor _hit in range(requested_hits):
\t\tvar current_index := enemy_index_at(target_pos)
\t\tif current_index < 0: break
\t\tattack_enemy_single(current_index)
\t\tactual_hits += 1
\tif actual_hits >= 2: message += " %d連撃。" % actual_hits
\tvar survivor_index := enemy_index_at(target_pos)
\tif survivor_index >= 0 and weapon_has_effect("knockback"):
\t\tvar moved := knockback_enemy(survivor_index, attack_dir, 3)
\t\tif moved > 0: message += " %dマス後退。" % moved''')

attack_single_anchor = "\nfunc attack_enemy_single(index: int) -> void:\n"
if attack_single_anchor not in s:
    raise SystemExit("STEP81 knockback insertion anchor failed")
knockback_func = '''

func knockback_enemy(index: int, attack_dir: Vector2i, max_cells: int = 3) -> int:
\tif index < 0 or index >= enemies.size() or attack_dir == Vector2i.ZERO: return 0
\tvar moved := 0
\tfor _step in range(max_cells):
\t\tvar next: Vector2i = enemies[index]["pos"] + attack_dir
\t\tif not position_in_bounds(next) or not is_walkable(next): break
\t\tif enemy_index_at(next) >= 0: break
\t\tif shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == next: break
\t\tif cell_has_item(next): break
\t\tenemies[index]["pos"] = next
\t\tmoved += 1
\treturn moved
'''
s = s.replace(attack_single_anchor, knockback_func + attack_single_anchor, 1)

replace_func("use_projectile", '''func use_projectile() -> void:
\tif weapon_has_effect("pull_6"):
\t\tvar hook_target := find_hook_target()
\t\tif not hook_target.is_empty() or not weapon_has_effect("ranged_throw"):
\t\t\tuse_hook_claw()
\t\t\treturn
\tif weapon_has_effect("ranged_throw"):
\t\tuse_ninja_shuriken()
\t\treturn
\tif not is_projectile_name(equipped_projectile): message = "飛び道具を装備していない。"; return
\tif projectile_inventory_index(equipped_projectile) < 0: equipped_projectile = ""; message = "飛び道具がない。"; return
\tif facing_dir == Vector2i.ZERO: facing_dir = Vector2i(0, 1)
\tvar projectile_name := equipped_projectile; var damage := 10 if projectile_name == "クナイ" else 6; var pos := player; var last_open := player; var hit := false
\tfor _step in range(10):
\t\tvar next := pos + facing_dir
\t\tif not position_in_bounds(next) or not is_walkable(next): break
\t\tpos = next; last_open = pos
\t\tvar enemy_index := enemy_index_at(pos)
\t\tif enemy_index >= 0: damage_enemy_with_projectile(enemy_index, damage, projectile_name); hit = true; break
\tconsume_equipped_projectile()
\tif not hit: drop_projectile_on_floor(projectile_name, last_open); message = "%sを放った。" % projectile_name
\tend_turn()''')

projectile_anchor = "\nfunc use_projectile() -> void:\n"
if projectile_anchor not in s:
    raise SystemExit("STEP81 shuriken insertion anchor failed")
shuriken_func = '''

func use_ninja_shuriken() -> void:
\tif facing_dir == Vector2i.ZERO: facing_dir = Vector2i(0, 1)
\tfor step in range(1, 9):
\t\tvar p2 := player + facing_dir * step
\t\tif not position_in_bounds(p2) or not is_walkable(p2): break
\t\tvar index := enemy_index_at(p2)
\t\tif index >= 0:
\t\t\tstart_melee_attack_animation(facing_dir, p2)
\t\t\tattack_enemy(index, facing_dir)
\t\t\tmessage = "忍手裏剣。 " + message
\t\t\tend_turn()
\t\t\treturn
\tmessage = "忍手裏剣は空を切った。"
\tend_turn()
'''
s = s.replace(projectile_anchor, shuriken_func + projectile_anchor, 1)

fusion_anchor = "\nfunc handle_village_input(event: InputEvent) -> void:\n"
if fusion_anchor not in s:
    raise SystemExit("STEP81 fusion helper anchor failed")
fusion_helpers = '''

func fusion_material_indices() -> Array[int]:
\tvar result: Array[int] = []
\tfor index in range(inventory_items.size()):
\t\tvar name := str(inventory_items[index].get("name", ""))
\t\tif is_weapon_name(name) and name != equipped_weapon: result.append(index)
\treturn result


func fuse_weapon_from_inventory(index: int) -> void:
\tif index < 0 or index >= inventory_items.size(): return
\tvar material_name := str(inventory_items[index].get("name", ""))
\tif not is_weapon_name(material_name) or material_name == equipped_weapon:
\t\tmessage = "素材にできる別の武器を選ぶ。"
\t\treturn
\tvar before := weapon_inherited_effects(equipped_weapon)
\tvar after := merge_unique_effects(before, weapon_all_effects(material_name))
\tif after.size() == before.size():
\t\tmessage = "新しく継承できる効果がない。"
\t\treturn
\tweapon_fusion_states[equipped_weapon] = after
\tinventory_items.remove_at(index)
\tmessage = "%sの効果を%sへ継承した。" % [material_name, equipped_weapon]
\tsave_meta()
\tqueue_redraw()
'''
s = s.replace(fusion_anchor, fusion_helpers + fusion_anchor, 1)

replace_func("handle_village_input", '''func handle_village_input(event: InputEvent) -> void:
\tif village_menu == "main":
\t\tif event.keycode == KEY_1: village_menu = "blacksmith"; message = "鍛冶屋"
\t\telif event.keycode == KEY_2: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"
\t\telif event.keycode == KEY_3: village_menu = "village_shop"; village_shop_scroll_offset = 0; message = "商店"
\t\telif event.keycode == KEY_4 or event.keycode == KEY_ENTER: start_run()
\telse:
\t\tif event.keycode == KEY_ESCAPE: village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "blacksmith":
\t\t\tif event.keycode == KEY_A: synthesize_equipment("weapon")
\t\t\telif event.keycode == KEY_D: synthesize_equipment("armor")
\t\t\telif event.keycode == KEY_F: village_menu = "weapon_fusion"; message = "素材武器を選ぶ。"
\t\telif village_menu == "weapon_fusion":
\t\t\tif event.keycode >= KEY_1 and event.keycode <= KEY_5:
\t\t\t\tvar materials := fusion_material_indices()
\t\t\t\tvar row := int(event.keycode - KEY_1)
\t\t\t\tif row < materials.size(): fuse_weapon_from_inventory(materials[row])
\t\telif village_menu == "warehouse":
\t\t\tif event.keycode == KEY_P: message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
\t\t\telif event.keycode == KEY_UP: warehouse_scroll(-1)
\t\t\telif event.keycode == KEY_DOWN: warehouse_scroll(1)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_8: warehouse_withdraw(warehouse_scroll_offset + int(event.keycode - KEY_1))
\t\telif village_menu == "village_shop":
\t\t\tif event.keycode == KEY_UP: village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode == KEY_DOWN: village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\t\tbuy_village_shop_item(village_shop_scroll_offset + int(event.keycode - KEY_1))
\tqueue_redraw()''')

replace_func("handle_village_touch_portrait", '''func handle_village_touch_portrait(pos: Vector2) -> void:
\tif village_menu == "main":
\t\tfor i in range(4):
\t\t\tif village_main_choice_rect(i).has_point(pos):
\t\t\t\tif i == 0: village_menu = "blacksmith"; message = "鍛冶屋"
\t\t\t\telif i == 1: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"
\t\t\t\telif i == 2: village_menu = "village_shop"; village_shop_scroll_offset = 0; message = "商店"
\t\t\t\telse: start_run()
\t\t\t\tqueue_redraw(); return
\telse:
\t\tif Rect2(48, 910, 180, 48).has_point(pos): village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "blacksmith":
\t\t\tif Rect2(48, 662, 624, 64).has_point(pos): synthesize_equipment("weapon")
\t\t\telif Rect2(48, 738, 624, 64).has_point(pos): synthesize_equipment("armor")
\t\t\telif Rect2(48, 814, 624, 64).has_point(pos): village_menu = "weapon_fusion"; message = "素材武器を選ぶ。"
\t\telif village_menu == "weapon_fusion":
\t\t\tvar materials := fusion_material_indices()
\t\t\tfor row in range(materials.size()):
\t\t\t\tif Rect2(48, 560 + row * 58, 624, 50).has_point(pos):
\t\t\t\t\tfuse_weapon_from_inventory(materials[row]); break
\t\telif village_menu == "warehouse":
\t\t\tif Rect2(48, 520, 624, 54).has_point(pos):
\t\t\t\tmessage = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
\t\t\telif Rect2(48, 846, 270, 48).has_point(pos): warehouse_scroll(-WAREHOUSE_VISIBLE_ROWS)
\t\t\telif Rect2(402, 846, 270, 48).has_point(pos): warehouse_scroll(WAREHOUSE_VISIBLE_ROWS)
\t\t\telse:
\t\t\t\tfor row in range(WAREHOUSE_VISIBLE_ROWS):
\t\t\t\t\tvar index := warehouse_scroll_offset + row
\t\t\t\t\tif index >= warehouse_items.size(): break
\t\t\t\t\tif Rect2(48, 584 + row * 54, 624, 46).has_point(pos): warehouse_withdraw(index); break
\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tvillage_shop_sync_scroll()
\t\t\tif Rect2(48, 842, 270, 48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif Rect2(402, 842, 270, 48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telse:
\t\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, catalog.size() - village_shop_scroll_offset)
\t\t\t\tfor row in range(visible_count):
\t\t\t\t\tvar index := village_shop_scroll_offset + row
\t\t\t\t\tif Rect2(48, village_shop_choice_y(visible_count, row), 624, 46).has_point(pos): buy_village_shop_item(index); break
\t\tqueue_redraw()''')

replace_func("draw_village_portrait", '''func draw_village_portrait() -> void:
\tvar scene_key := "blacksmith" if village_menu == "weapon_fusion" else village_menu
\tif not village_scene_textures.has(scene_key): scene_key = "main"
\tvar scene_texture: Texture2D = village_scene_textures.get(scene_key, null) as Texture2D
\tif scene_texture != null: draw_texture_rect(scene_texture, Rect2(0, 0, 720, 1100), false)
\telse: draw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
\tdraw_rect(Rect2(0, 0, 720, 1100), Color(0.015, 0.025, 0.045, 0.12))
\tdraw_rect(Rect2(0, 0, 720, 198), Color(0.03, 0.055, 0.09, 0.82))
\tdraw_rect(Rect2(0, 195, 720, 3), Color("#d3b35b"))
\tdraw_ui_text(Vector2(46, 72), "忍びの里", HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color("#e8d47f"))
\tdraw_ui_text(Vector2(48, 122), "忍魂 %d    銭 %d" % [souls, coins], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color("#e4e8ed"))
\tdraw_ui_text(Vector2(48, 162), "最高到達 %dF    倉庫 %d/50    持込 %d/5" % [village_unlocked_floor(), warehouse_items.size(), inventory_items.size()], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#aeb7c2"))
\tif village_menu == "main":
\t\tvar labels = ["鍛冶屋", "倉庫", "商店", "出陣"]
\t\tvar notes = ["装備を合成", "50個まで保管", "品物を購入", "探索を始める"]
\t\tfor i in range(labels.size()):
\t\t\tvar r := village_main_choice_rect(i)
\t\t\tvar fill := Color(0.16, 0.15, 0.08, 0.92) if i == 3 else Color(0.04, 0.07, 0.10, 0.90)
\t\t\tvar border := Color("#d7bf66") if i == 3 else Color("#687786")
\t\t\tdraw_panel(r, fill, border, 2.0)
\t\t\tdraw_ui_text(r.position + Vector2(0, 35), labels[i], HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 24, Color("#f0f2f5"))
\t\t\tdraw_ui_text(r.position + Vector2(0, 64), notes[i], HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 15, Color("#c8d0d8"))
\telse:
\t\tvar title := "武器合成" if village_menu == "weapon_fusion" else ("鍛冶屋" if village_menu == "blacksmith" else ("倉庫" if village_menu == "warehouse" else "商店"))
\t\tdraw_ui_text(Vector2(48, 244), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color("#e8d47f"))
\t\tif village_menu == "blacksmith":
\t\t\tvar weapon_price := 50 + smith_weapon_rank * 25
\t\t\tvar armor_price := 50 + smith_armor_rank * 25
\t\t\tvar actions = ["%s +%d → +%d（銭%d）" % [equipped_weapon, smith_weapon_rank, smith_weapon_rank + 1, weapon_price], "%s +%d → +%d（銭%d）" % [equipped_armor, smith_armor_rank, smith_armor_rank + 1, armor_price], "武器効果を合成"]
\t\t\tfor i in range(actions.size()):
\t\t\t\tvar r := Rect2(48, 662 + i * 76, 624, 64); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"), 2.0)
\t\t\t\tdraw_ui_text(r.position + Vector2(20, 42), actions[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\t\telif village_menu == "weapon_fusion":
\t\t\tdraw_ui_text(Vector2(48, 300), "ベース：%s（見た目を維持）" % equipped_weapon, HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color.WHITE)
\t\t\tdraw_ui_text(Vector2(48, 340), "固有：%s" % weapon_effect_summary(weapon_native_effects(equipped_weapon)).left(34), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#d8dee5"))
\t\t\tdraw_ui_text(Vector2(48, 378), "継承：%s" % weapon_effect_summary(weapon_inherited_effects(equipped_weapon)).left(34), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e8d47f"))
\t\t\tdraw_ui_text(Vector2(48, 432), "素材武器の効果をすべて継承", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d8dee5"))
\t\t\tvar materials := fusion_material_indices()
\t\t\tif materials.is_empty(): draw_ui_text(Vector2(48, 548), "持ち物に素材武器がない。", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color.WHITE)
\t\t\tfor row in range(materials.size()):
\t\t\t\tvar index := materials[row]; var name := str(inventory_items[index].get("name", ""))
\t\t\t\tvar r := Rect2(48, 560 + row * 58, 624, 50); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 34), "%d  %s  %s" % [row + 1, name, weapon_effect_summary(weapon_all_effects(name)).left(24)], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\telif village_menu == "warehouse":
\t\t\tvar store := Rect2(48, 520, 624, 54); draw_panel(store, Color(0.16, 0.15, 0.08, 0.92), Color("#d7bf66"))
\t\t\tdraw_ui_text(store.position + Vector2(18, 37), "持ち物を全て預ける", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color.WHITE)
\t\t\twarehouse_sync_scroll()
\t\t\tfor row in range(WAREHOUSE_VISIBLE_ROWS):
\t\t\t\tvar index := warehouse_scroll_offset + row
\t\t\t\tif index >= warehouse_items.size(): break
\t\t\t\tvar entry: Dictionary = warehouse_items[index]; var r := Rect2(48, 584 + row * 54, 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tvar suffix := "×%d" % int(entry.get("count", 1)) if is_projectile_name(str(entry.get("name", ""))) else ""
\t\t\t\tdraw_ui_text(r.position + Vector2(18, 32), "%d  %s%s    持ち出す" % [index + 1, str(entry.get("name", "")), suffix], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\t\tvar prev := Rect2(48, 846, 270, 48); var next := Rect2(402, 846, 270, 48)
\t\t\tdraw_panel(prev, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if warehouse_scroll_offset > 0 else Color("#29323b"))
\t\t\tdraw_panel(next, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if warehouse_scroll_offset < warehouse_max_scroll() else Color("#29323b"))
\t\t\tdraw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\t\tdraw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog(); village_shop_sync_scroll()
\t\t\tdraw_ui_text(Vector2(240, 244), "%d階到達までの商品" % village_unlocked_floor(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d8dee5"))
\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, catalog.size() - village_shop_scroll_offset)
\t\t\tfor row in range(visible_count):
\t\t\t\tvar index := village_shop_scroll_offset + row
\t\t\t\tvar offer: Dictionary = catalog[index]; var r := Rect2(48, village_shop_choice_y(visible_count, row), 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tvar offer_label := equipment_display_name(str(offer["name"])) if is_equipment_name(str(offer["name"])) else str(offer["label"])
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [offer_label, int(offer["price"])], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\t\tvar prev := Rect2(48, 842, 270, 48); var next := Rect2(402, 842, 270, 48)
\t\t\tdraw_panel(prev, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset > 0 else Color("#29323b"))
\t\t\tdraw_panel(next, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset < village_shop_max_scroll() else Color("#29323b"))
\t\t\tdraw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\t\tdraw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\tvar back := Rect2(48, 910, 180, 48); draw_panel(back, Color(0.04, 0.07, 0.10, 0.92), Color("#687786"))
\t\tdraw_ui_text(back.position + Vector2(24, 33), "戻る", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\tdraw_panel(Rect2(40, 984, 640, 70), Color(0.04, 0.07, 0.10, 0.90), Color("#394653"), 1.0)
\tdraw_ui_text(Vector2(54, 1028), message.left(40), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#e5d37d"))
\tdraw_ui_text(Vector2(465, 46), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#7f8b98"))''')

replace_func("handle_inventory_touch", '''func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:
\tvar panel_x := 60.0 if portrait else 270.0
\tvar panel_y := 225.0 if portrait else 120.0
\tvar row_h := 46.0
\tif Rect2(panel_x + 500.0, panel_y + 74.0, 40.0, 40.0).has_point(pos): inventory_scroll(-1); return
\tif Rect2(panel_x + 500.0, panel_y + 74.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h, 40.0, 40.0).has_point(pos): inventory_scroll(1); return
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index := inventory_scroll_offset + row
\t\tif index >= inventory_entry_count(): break
\t\tvar r := Rect2(panel_x + 20.0, panel_y + 74.0 + row * row_h, 470.0, 40.0)
\t\tif r.has_point(pos): inventory_selected = index; inventory_sync_scroll(); queue_redraw(); return
\tvar action_y := panel_y + 510.0
\tvar actions = [["equip", panel_x + 12.0], ["use", panel_x + 118.0], ["identify", panel_x + 224.0], ["floor", panel_x + 330.0], ["back", panel_x + 436.0]]
\tfor action in actions:
\t\tif Rect2(float(action[1]), action_y, 96.0, 52.0).has_point(pos):
\t\t\tmatch str(action[0]):
\t\t\t\t"equip": inventory_equip_selected()
\t\t\t\t"use": inventory_use_selected()
\t\t\t\t"identify": inventory_identify_selected()
\t\t\t\t"floor": inventory_floor_pick_or_swap()
\t\t\t\t"back": close_inventory()
\t\t\treturn''')

detail_anchor = "\nfunc draw_inventory_overlay(portrait: bool) -> void:\n"
if detail_anchor not in s:
    raise SystemExit("STEP81 detail helper anchor failed")
detail_helper = '''

func inventory_detail_weapon_name() -> String:
\tif inventory_selected == 0: return equipped_weapon
\tvar index := inventory_selected - 2
\tif index >= 0 and index < inventory_items.size():
\t\tvar name := str(inventory_items[index].get("name", ""))
\t\tif is_weapon_name(name): return name
\treturn ""
'''
s = s.replace(detail_anchor, detail_helper + detail_anchor, 1)

replace_func("draw_inventory_overlay", '''func draw_inventory_overlay(portrait: bool) -> void:
\tvar panel_x := 60.0 if portrait else 270.0
\tvar panel_y := 225.0 if portrait else 120.0
\tvar panel_w := 560.0
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 590.0), Color(0.05, 0.07, 0.09, 0.98))
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 590.0), Color("#e4cf7a"), false, 2.0)
\tdraw_ui_text(Vector2(panel_x + 22.0, panel_y + 48.0), "道具 %d/20" % inventory_items.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color.WHITE)
\tvar floor_idx := floor_item_index_at_player()
\tif floor_idx >= 0: draw_ui_text(Vector2(panel_x + 300.0, panel_y + 48.0), "%sの上" % str(items[floor_idx].get("name", "道具")), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#f1c95b"))
\tvar row_h := 46.0
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index := inventory_scroll_offset + row
\t\tif index >= inventory_entry_count(): break
\t\tvar r := Rect2(panel_x + 20.0, panel_y + 74.0 + row * row_h, 470.0, 40.0)
\t\tdraw_rect(r, Color("#343527") if index == inventory_selected else Color("#202934"))
\t\tdraw_rect(r, Color("#dbc66e") if index == inventory_selected else Color("#4c5865"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(12, 27), inventory_display_name(index), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar max_offset: int = maxi(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tif inventory_scroll_offset > 0: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0), "↑", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tif inventory_scroll_offset < max_offset: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h), "↓", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tvar detail_name := inventory_detail_weapon_name()
\tif not detail_name.is_empty():
\t\tdraw_ui_text(Vector2(panel_x + 22.0, panel_y + 420.0), "固有：%s" % weapon_effect_summary(weapon_native_effects(detail_name)).left(38), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#d8dee5"))
\t\tdraw_ui_text(Vector2(panel_x + 22.0, panel_y + 450.0), "継承：%s" % weapon_effect_summary(weapon_inherited_effects(detail_name)).left(38), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#e8d47f"))
\tvar action_y := panel_y + 510.0
\tvar labels = [["装備", panel_x + 12.0], ["使用", panel_x + 118.0], ["識別", panel_x + 224.0], ["拾う", panel_x + 330.0], ["戻る", panel_x + 436.0]]
\tfor action in labels:
\t\tvar r := Rect2(float(action[1]), action_y, 96.0, 52.0)
\t\tdraw_rect(r, Color("#252c35")); draw_rect(r, Color("#596575"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(14, 34), str(action[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)''')

run_save_anchor = '\t\t"equipped_armor": equipped_armor,\n'
if run_save_anchor not in s:
    raise SystemExit("STEP81 run save anchor failed")
s = s.replace(run_save_anchor, run_save_anchor + '\t\t"weapon_fusion_states": weapon_fusion_states,\n', 1)

run_load_anchor = '\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"\n'
if run_load_anchor not in s:
    raise SystemExit("STEP81 run load anchor failed")
s = s.replace(run_load_anchor, run_load_anchor + '\tweapon_fusion_states = sanitize_weapon_fusion_states(data.get("weapon_fusion_states", {})) if version >= 9 else {}\n', 1)

meta_save_anchor = '\t\t"equipped_armor": equipped_armor,\n'
meta_pos = s.find("func save_meta() -> void:")
anchor_pos = s.find(meta_save_anchor, meta_pos)
if meta_pos < 0 or anchor_pos < 0:
    raise SystemExit("STEP81 meta save anchor failed")
s = s[:anchor_pos + len(meta_save_anchor)] + '\t\t"weapon_fusion_states": weapon_fusion_states,\n' + s[anchor_pos + len(meta_save_anchor):]
s = s[:meta_pos] + s[meta_pos:].replace('"version": 4,', '"version": 5,', 1)

meta_load_pos = s.find("func load_meta() -> void:")
meta_load_anchor = '\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"\n'
anchor_pos = s.find(meta_load_anchor, meta_load_pos)
if meta_load_pos < 0 or anchor_pos < 0:
    raise SystemExit("STEP81 meta load anchor failed")
s = s[:anchor_pos + len(meta_load_anchor)] + '\tweapon_fusion_states = sanitize_weapon_fusion_states(data.get("weapon_fusion_states", {}))\n' + s[anchor_pos + len(meta_load_anchor):]

test_anchor = "\nfunc debug_test_equipment_arsenal() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP81 regression anchor failed")
test_func = '''

func debug_test_weapon_fusion_contract() -> String:
\tvar old_weapon := equipped_weapon
\tvar old_states := weapon_fusion_states.duplicate(true)
\tequipped_weapon = "忍刀"
\tweapon_fusion_states = {"忍刀":["double_strike","reach_3","knockback","all_direction"]}
\tvar effects := weapon_all_effects()
\tvar fusion_ok := effects.size() == 4 and weapon_has_effect("double_strike") and weapon_has_effect("reach_3") and weapon_has_effect("knockback") and weapon_has_effect("all_direction")
\tvar hagun: Array[String] = weapon_native_effects("破軍槍")
\tvar hagun_ok := "reach_3" in hagun and "pierce_3" in hagun and "knockback" in hagun
\tvar design_ok := str(WEAPON_CATALOG["忍刀"].get("design_id", "")) == "weapon_01" and str(ARMOR_CATALOG["霧隠れ頭巾"].get("design_id", "")) == "armor_08"
\tvar save_ok := build_run_state().has("weapon_fusion_states")
\tequipped_weapon = old_weapon
\tweapon_fusion_states = old_states
\treturn "PASS 武器合成継承破軍槍" if fusion_ok and hagun_ok and design_ok and save_ok else "FAIL 武器合成継承破軍槍"


func debug_test_hagun_knockback_rules() -> String:
\tvar old_map := map.duplicate(true)
\tvar old_player := player
\tvar old_enemies := enemies.duplicate(true)
\tvar old_items := items.duplicate(true)
\tvar old_shopkeeper := shopkeeper.duplicate(true)
\tmap = []
\tfor y in range(MAP_H):
\t\tvar row: Array[String] = []
\t\tfor x in range(MAP_W): row.append(".")
\t\tmap.append(row)
\tplayer = Vector2i(2, 2)
\titems = []
\tshopkeeper = {}
\tenemies = [{"pos":Vector2i(3,2)}, {"pos":Vector2i(6,2)}]
\tvar enemy_stop: bool = knockback_enemy(0, Vector2i(1,0), 3) == 2 and enemies[0]["pos"] == Vector2i(5,2)
\tenemies = [{"pos":Vector2i(MAP_W - 2,2)}]
\tvar edge_stop: bool = knockback_enemy(0, Vector2i(1,0), 3) == 1 and enemies[0]["pos"] == Vector2i(MAP_W - 1,2)
\tenemies = [{"pos":Vector2i(3,2)}]
\tmap[2][5] = "#"
\tvar wall_stop: bool = knockback_enemy(0, Vector2i(1,0), 3) == 1 and enemies[0]["pos"] == Vector2i(4,2)
\tmap = old_map
\tplayer = old_player
\tenemies = old_enemies
\titems = old_items
\tshopkeeper = old_shopkeeper
\treturn "PASS hagun knockback stops" if enemy_stop and edge_stop and wall_stop else "FAIL hagun knockback stops"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace(
    "\t\tdebug_test_equipment_arsenal(),\n",
    "\t\tdebug_test_equipment_arsenal(),\n\t\tdebug_test_weapon_fusion_contract(),\n\t\tdebug_test_hagun_knockback_rules(),\n",
    1,
)

required = [
    "STEP81_WEAPON_FUSION_APPLIED",
    "const WEAPON_EFFECT_LABELS := {",
    "var weapon_fusion_states: Dictionary = {}",
    "func knockback_enemy(",
    "func fuse_weapon_from_inventory(",
    '"weapon_fusion_states": weapon_fusion_states',
    "debug_test_weapon_fusion_contract()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP81 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP81 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP81_WEAPON_FUSION PASS")
exec(Path("tools/apply_step82_boss_drops_enemy_art.py").read_text(encoding="utf-8"), {})
