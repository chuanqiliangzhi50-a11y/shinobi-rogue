from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP76_SHINOBI_VILLAGE_APPLIED" in s:
    print("STEP76_SHINOBI_VILLAGE PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP75_LEVEL_FULL_HEAL_GROWTH_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP76 STEP75 anchor failed")
s = s.replace(marker, marker + "# STEP76_SHINOBI_VILLAGE_APPLIED\nconst WAREHOUSE_CAPACITY := 50\n", 1)

glyph_paths = '''const STEP76_EXTRA_GLYPH_PATHS := {
\t"び": "res://art/step76_glyphs/u3073.svg",
\t"ク": "res://art/step76_glyphs/u30af.svg",
\t"個": "res://art/step76_glyphs/u500b.svg",
\t"移": "res://art/step76_glyphs/u79fb.svg",
\t"倉": "res://art/step76_glyphs/u5009.svg",
\t"購": "res://art/step76_glyphs/u8cfc.svg",
\t"変": "res://art/step76_glyphs/u5909.svg",
\t"固": "res://art/step76_glyphs/u56fa.svg",
\t"印": "res://art/step76_glyphs/u5370.svg",
\t"乗": "res://art/step76_glyphs/u4e57.svg",
\t"以": "res://art/step76_glyphs/u4ee5.svg",
\t"×": "res://art/step76_glyphs/u00d7.svg",
\t"命": "res://art/step76_glyphs/u547d.svg",
\t"ら": "res://art/step76_glyphs/u3089.svg",
\t"元": "res://art/step76_glyphs/u5143.svg",
\t"ぶ": "res://art/step76_glyphs/u3076.svg",
\t"放": "res://art/step76_glyphs/u653e.svg",
\t"既": "res://art/step76_glyphs/u65e2.svg",
\t"セ": "res://art/step76_glyphs/u30bb.svg",
\t"地": "res://art/step76_glyphs/u5730.svg",
\t"揃": "res://art/step76_glyphs/u63c3.svg",
\t"預": "res://art/step76_glyphs/u9810.svg",
\t"管": "res://art/step76_glyphs/u7ba1.svg",
\t"解": "res://art/step76_glyphs/u89e3.svg",
\t"禁": "res://art/step76_glyphs/u7981.svg",
\t"庫": "res://art/step76_glyphs/u5eab.svg",
\t"○": "res://art/step76_glyphs/u25cb.svg",
\t"支": "res://art/step76_glyphs/u652f.svg",
\t"ナ": "res://art/step76_glyphs/u30ca.svg",
\t"送": "res://art/step76_glyphs/u9001.svg",
\t"更": "res://art/step76_glyphs/u66f4.svg",
\t"定": "res://art/step76_glyphs/u5b9a.svg",
\t"結": "res://art/step76_glyphs/u7d50.svg",
\t"ぱ": "res://art/step76_glyphs/u3071.svg",
\t"設": "res://art/step76_glyphs/u8a2d.svg",
\t"始": "res://art/step76_glyphs/u59cb.svg",
\t"｜": "res://art/step76_glyphs/uff5c.svg",
\t"押": "res://art/step76_glyphs/u62bc.svg",
\t"図": "res://art/step76_glyphs/u56f3.svg",
\t"整": "res://art/step76_glyphs/u6574.svg",
\t"除": "res://art/step76_glyphs/u9664.svg",
\t"キ": "res://art/step76_glyphs/u30ad.svg",
\t"練": "res://art/step76_glyphs/u7df4.svg",
\t"　": "res://art/step76_glyphs/u3000.svg",
\t"●": "res://art/step76_glyphs/u25cf.svg",
\t"駆": "res://art/step76_glyphs/u99c6.svg",
\t"込": "res://art/step76_glyphs/u8fbc.svg",
\t"前": "res://art/step76_glyphs/u524d.svg",
\t"ロ": "res://art/step76_glyphs/u30ed.svg",
\t"ル": "res://art/step76_glyphs/u30eb.svg"
}
'''
glyph_anchor = 'const WAREHOUSE_CAPACITY := 50\n'
s = s.replace(glyph_anchor, glyph_anchor + glyph_paths, 1)

load_glyph_anchor = '''\tif ResourceLoader.exists("res://art/glyph_ken.svg"):
\t\textra_ui_glyphs["剣"] = load("res://art/glyph_ken.svg") as Texture2D'''
if load_glyph_anchor not in s:
    raise SystemExit("STEP76 extra glyph load anchor failed")
s = s.replace(load_glyph_anchor, load_glyph_anchor + '''
\tfor glyph in STEP76_EXTRA_GLYPH_PATHS:
\t\tvar glyph_path := str(STEP76_EXTRA_GLYPH_PATHS[glyph])
\t\tif ResourceLoader.exists(glyph_path): extra_ui_glyphs[glyph] = load(glyph_path) as Texture2D''', 1)
s = s.replace('"✦ 忍道:%s ｜ EXP', '"* 忍道:%s ｜ EXP', 1)

state_anchor = 'var village_menu := "main"\n'
if state_anchor not in s:
    raise SystemExit("STEP76 village state anchor failed")
s = s.replace(state_anchor, state_anchor + "var warehouse_items: Array = []\nvar smith_weapon_rank := 0\nvar smith_armor_rank := 0\n", 1)

# The title's Start action must always lead to the village, including when a suspended run exists.
title_helper_anchor = "\n\nfunc _unhandled_key_input(event: InputEvent) -> void:\n"
title_helper = '''

func enter_village_from_title() -> void:
\ttitle_screen_active = false
\tin_village = true
\tvillage_menu = "main"
\tmessage = "忍びの里。出陣の支度を整えよう。"
\tqueue_redraw()
'''
if title_helper_anchor not in s:
    raise SystemExit("STEP76 title helper anchor failed")
s = s.replace(title_helper_anchor, title_helper + title_helper_anchor, 1)
s = s.replace('''\tif title_screen_active:
\t\ttitle_screen_active = false
\t\tqueue_redraw()
\t\treturn''', '''\tif title_screen_active:
\t\tenter_village_from_title()
\t\treturn''', 1)
s = s.replace('''\tif title_screen_active:
\t\tif event is InputEventScreenTouch:
\t\t\tif event.pressed:
\t\t\t\ttitle_screen_active = false
\t\t\t\tqueue_redraw()
\t\t\treturn
\t\tif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
\t\t\tif event.pressed:
\t\t\t\ttitle_screen_active = false
\t\t\t\tqueue_redraw()
\t\t\treturn''', '''\tif title_screen_active:
\t\tif event is InputEventScreenTouch:
\t\t\tif event.pressed: enter_village_from_title()
\t\t\treturn
\t\tif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
\t\t\tif event.pressed: enter_village_from_title()
\t\t\treturn''', 1)

helpers_anchor = "\n\nfunc handle_village_input(event: InputEvent) -> void:\n"
if helpers_anchor not in s:
    raise SystemExit("STEP76 village helpers anchor failed")
helpers = '''

func village_unlocked_floor() -> int:
\treturn clampi(maxi(1, int(known_enemies.get("max_floor", 1))), 1, 50)


func village_shop_catalog() -> Array:
\tvar catalog: Array = [
\t\t{"label":"手裏剣10", "name":"手裏剣", "count":10, "price":10, "floor":1},
\t\t{"label":"薬小", "name":"薬", "count":1, "price":8, "floor":1},
\t\t{"label":"兵糧丸小", "name":"兵糧丸", "count":1, "price":8, "floor":1},
\t\t{"label":"忍気丸", "name":"忍気丸", "count":1, "price":18, "floor":5},
\t\t{"label":"クナイ5", "name":"クナイ", "count":5, "price":24, "floor":10},
\t\t{"label":"上薬", "name":"上薬", "count":1, "price":30, "floor":15},
\t\t{"label":"大兵糧丸", "name":"大兵糧丸", "count":1, "price":30, "floor":20},
\t\t{"label":"小巻物", "name":"小巻物", "count":1, "price":45, "floor":25},
\t\t{"label":"中巻物", "name":"中巻物", "count":1, "price":70, "floor":30},
\t\t{"label":"大巻物", "name":"大巻物", "count":1, "price":110, "floor":40},
\t\t{"label":"究極巻物", "name":"究極巻物", "count":1, "price":180, "floor":50}
\t]
\tvar unlocked: Array = []
\tfor entry in catalog:
\t\tif int(entry["floor"]) <= village_unlocked_floor(): unlocked.append(entry)
\treturn unlocked


func warehouse_add_item(entry: Dictionary) -> bool:
\tvar name := str(entry.get("name", ""))
\tif not valid_inventory_item_name(name): return false
\tvar count := clampi(int(entry.get("count", 1)), 1, 99)
\tif is_projectile_name(name):
\t\tfor stored in warehouse_items:
\t\t\tif str(stored.get("name", "")) == name:
\t\t\t\tstored["count"] = mini(99, int(stored.get("count", 1)) + count)
\t\t\t\treturn true
\tif warehouse_items.size() >= WAREHOUSE_CAPACITY: return false
\twarehouse_items.append({"name":name, "identified":true, "count":count if is_projectile_name(name) else 1})
\treturn true


func warehouse_store_carried_all() -> int:
\tvar stored_count := 0
\tvar remaining: Array = []
\tfor raw in inventory_items:
\t\tvar entry: Dictionary = raw
\t\tif warehouse_add_item(entry): stored_count += 1
\t\telse: remaining.append(entry)
\tinventory_items = remaining
\tif stored_count > 0: save_meta()
\treturn stored_count


func warehouse_withdraw(index: int) -> void:
\tif index < 0 or index >= warehouse_items.size(): return
\tvar entry: Dictionary = warehouse_items[index]
\tvar name := str(entry.get("name", ""))
\tif not inventory_has_space_for(name):
\t\tmessage = "持ち物は20個まで。"
\t\treturn
\tadd_inventory_item(name, true, int(entry.get("count", 1)))
\twarehouse_items.remove_at(index)
\tsave_meta()
\tmessage = "%sを持ち物へ移した。" % name


func buy_village_shop_item(index: int) -> void:
\tvar catalog := village_shop_catalog()
\tif index < 0 or index >= catalog.size(): return
\tvar offer: Dictionary = catalog[index]
\tvar price := int(offer["price"])
\tif coins < price:
\t\tmessage = "銭が足りない。"
\t\treturn
\tif not warehouse_add_item({"name":offer["name"], "count":offer["count"], "identified":true}):
\t\tmessage = "倉庫は50個まで。"
\t\treturn
\tcoins -= price
\tsave_meta()
\tmessage = "%sを購入し、倉庫へ送った。" % str(offer["label"])


func synthesize_equipment(kind: String) -> void:
\tvar rank := smith_weapon_rank if kind == "weapon" else smith_armor_rank
\tvar price := 50 + rank * 25
\tif coins < price:
\t\tmessage = "合成に必要な銭が足りない。"
\t\treturn
\tcoins -= price
\tif kind == "weapon":
\t\tsmith_weapon_rank += 1; perm_attack += 1
\t\tmessage = "忍刀を合成した。攻撃+1。"
\telse:
\t\tsmith_armor_rank += 1; perm_defense += 1
\t\tmessage = "忍装束を合成した。防御+1。"
\tsave_meta()
'''
s = s.replace(helpers_anchor, helpers + helpers_anchor, 1)

# Replace village keyboard navigation.
start = s.find("func handle_village_input(event: InputEvent) -> void:")
end = s.find("\n\nfunc handle_village_touch(pos: Vector2) -> void:", start)
if start < 0 or end < 0:
    raise SystemExit("STEP76 village input block failed")
input_block = '''func handle_village_input(event: InputEvent) -> void:
\tif village_menu == "main":
\t\tif event.keycode == KEY_1: village_menu = "blacksmith"; message = "鍛冶屋"
\t\telif event.keycode == KEY_2: village_menu = "warehouse"; message = "倉庫"
\t\telif event.keycode == KEY_3: village_menu = "village_shop"; message = "商店"
\t\telif event.keycode == KEY_4 or event.keycode == KEY_ENTER: start_run()
\telse:
\t\tif event.keycode == KEY_ESCAPE: village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "blacksmith":
\t\t\tif event.keycode == KEY_A: synthesize_equipment("weapon")
\t\t\telif event.keycode == KEY_D: synthesize_equipment("armor")
\t\telif village_menu == "warehouse":
\t\t\tif event.keycode == KEY_P: message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all()
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9: warehouse_withdraw(int(event.keycode - KEY_1))
\t\telif village_menu == "village_shop" and event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\tbuy_village_shop_item(int(event.keycode - KEY_1))
\tqueue_redraw()
'''
s = s[:start] + input_block + s[end:]

# Carry selected warehouse items into the dungeon; do not erase them at departure.
s = s.replace("\tfinal_clear = false\n\tinventory_items.clear()\n\tequipped_projectile", "\tfinal_clear = false\n\tequipped_projectile", 1)

# Torneko-style: a successful return stores loot; defeat loses carried items.
return_anchor = '''\tvar gained = bank_run_rewards()
\tin_village = true
\tvillage_menu = "main"
\tapply_permanent_stats()'''
return_new = '''\tvar gained = bank_run_rewards()
\tvar stored_loot := 0
\tif cause == "": stored_loot = warehouse_store_carried_all()
\telse: inventory_items.clear()
\tin_village = true
\tvillage_menu = "main"
\tapply_permanent_stats()'''
if return_anchor not in s:
    raise SystemExit("STEP76 return village anchor failed")
s = s.replace(return_anchor, return_new, 1)
s = s.replace('''\tmessage = "忍の里へ帰還。忍魂+%d 銭+%d。" % [int(gained["souls"]), int(gained["coins"])]''', '''\tmessage = "忍びの里へ帰還。忍魂+%d 銭+%d 倉庫+%d。" % [int(gained["souls"]), int(gained["coins"]), stored_loot]''', 1)

# Persist warehouse and smith progression in the meta save.
s = s.replace('''\t\t"version": 2,
\t\t"souls": souls,''', '''\t\t"version": 3,
\t\t"warehouse_items": warehouse_items,
\t\t"smith_weapon_rank": smith_weapon_rank,
\t\t"smith_armor_rank": smith_armor_rank,
\t\t"souls": souls,''', 1)
load_anchor = '''\tvar data: Dictionary = parsed
\tsouls = max(0, int(data.get("souls", 0)))'''
load_new = '''\tvar data: Dictionary = parsed
\twarehouse_items = sanitize_inventory_array(data.get("warehouse_items", []))
\tif warehouse_items.size() > WAREHOUSE_CAPACITY: warehouse_items.resize(WAREHOUSE_CAPACITY)
\tsmith_weapon_rank = maxi(0, int(data.get("smith_weapon_rank", 0)))
\tsmith_armor_rank = maxi(0, int(data.get("smith_armor_rank", 0)))
\tsouls = max(0, int(data.get("souls", 0)))'''
if load_anchor not in s:
    raise SystemExit("STEP76 meta load anchor failed")
s = s.replace(load_anchor, load_new, 1)

# Replace portrait touch routing.
start = s.find("func handle_village_touch_portrait(pos: Vector2) -> void:")
end = s.find("\n\nfunc handle_modal_touch_portrait", start)
if start < 0 or end < 0:
    raise SystemExit("STEP76 portrait touch block failed")
touch_block = '''func handle_village_touch_portrait(pos: Vector2) -> void:
\tif village_menu == "main":
\t\tfor i in range(4):
\t\t\tif Rect2(48, 246 + i * 104, 624, 82).has_point(pos):
\t\t\t\tif i == 0: village_menu = "blacksmith"; message = "鍛冶屋"
\t\t\t\telif i == 1: village_menu = "warehouse"; message = "倉庫"
\t\t\t\telif i == 2: village_menu = "village_shop"; message = "商店"
\t\t\t\telse: start_run()
\t\t\t\tqueue_redraw(); return
\telse:
\t\tif Rect2(48, 882, 270, 64).has_point(pos): village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "blacksmith":
\t\t\tif Rect2(48, 310, 624, 70).has_point(pos): synthesize_equipment("weapon")
\t\t\telif Rect2(48, 398, 624, 70).has_point(pos): synthesize_equipment("armor")
\t\telif village_menu == "warehouse":
\t\t\tif Rect2(48, 238, 624, 64).has_point(pos): message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all()
\t\t\telse:
\t\t\t\tfor i in range(mini(8, warehouse_items.size())):
\t\t\t\t\tif Rect2(48, 318 + i * 64, 624, 54).has_point(pos): warehouse_withdraw(i); break
\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tfor i in range(catalog.size()):
\t\t\t\tif Rect2(48, 250 + i * 54, 624, 46).has_point(pos): buy_village_shop_item(i); break
\t\tqueue_redraw()
'''
s = s[:start] + touch_block + s[end:]

# Replace portrait village presentation with the requested three facilities and departure.
start = s.find("func draw_village_portrait() -> void:")
end = s.find("\n\nfunc dungeon_visual_hash", start)
if start < 0 or end < 0:
    raise SystemExit("STEP76 portrait draw block failed")
draw_block = '''func draw_village_portrait() -> void:
\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
\tdraw_rect(Rect2(0, 0, 720, 198), Color("#111b27"))
\tdraw_rect(Rect2(0, 195, 720, 3), Color("#8d7740"))
\tdraw_ui_text(Vector2(46, 72), "忍びの里", HORIZONTAL_ALIGNMENT_LEFT, -1, 44, Color("#e8d47f"))
\tdraw_ui_text(Vector2(48, 122), "忍魂 %d    銭 %d" % [souls, coins], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color("#e4e8ed"))
\tdraw_ui_text(Vector2(48, 162), "最高到達 %dF    倉庫 %d/50    持ち物 %d/20" % [village_unlocked_floor(), warehouse_items.size(), inventory_items.size()], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#aeb7c2"))
\tif village_menu == "main":
\t\tvar labels = ["鍛冶屋", "倉庫", "商店", "出陣"]
\t\tvar notes = ["装備品を合成", "道具を50個まで保管", "到達階に応じて品揃え解禁", "1階から探索を始める"]
\t\tfor i in range(labels.size()):
\t\t\tvar r := Rect2(48, 246 + i * 104, 624, 82)
\t\t\tvar fill := Color("#282717") if i == 3 else Color("#18212b")
\t\t\tvar border := Color("#d7bf66") if i == 3 else Color("#455464")
\t\t\tdraw_panel(r, fill, border, 2.0)
\t\t\tdraw_ui_text(r.position + Vector2(24, 37), labels[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color("#f0f2f5"))
\t\t\tdraw_ui_text(r.position + Vector2(190, 35), notes[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#aeb7c2"))
\telse:
\t\tvar title := "鍛冶屋" if village_menu == "blacksmith" else ("倉庫" if village_menu == "warehouse" else "商店")
\t\tdraw_ui_text(Vector2(48, 244), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color("#e8d47f"))
\t\tif village_menu == "blacksmith":
\t\t\tvar weapon_price := 50 + smith_weapon_rank * 25
\t\t\tvar armor_price := 50 + smith_armor_rank * 25
\t\t\tvar actions = ["忍刀 +%d → +%d（銭%d）" % [smith_weapon_rank, smith_weapon_rank + 1, weapon_price], "忍装束 +%d → +%d（銭%d）" % [smith_armor_rank, smith_armor_rank + 1, armor_price]]
\t\t\tfor i in range(actions.size()):
\t\t\t\tvar r := Rect2(48, 310 + i * 88, 624, 70); draw_panel(r)
\t\t\t\tdraw_ui_text(r.position + Vector2(20, 45), actions[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color.WHITE)
\t\telif village_menu == "warehouse":
\t\t\tvar store := Rect2(48, 238, 624, 64); draw_panel(store, Color("#282717"), Color("#d7bf66"))
\t\t\tdraw_ui_text(store.position + Vector2(18, 42), "持ち物を全て預ける", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\t\t\tfor i in range(mini(8, warehouse_items.size())):
\t\t\t\tvar entry: Dictionary = warehouse_items[i]; var r := Rect2(48, 318 + i * 64, 624, 54); draw_panel(r)
\t\t\t\tvar suffix := "×%d" % int(entry.get("count", 1)) if is_projectile_name(str(entry.get("name", ""))) else ""
\t\t\t\tdraw_ui_text(r.position + Vector2(18, 36), "%d  %s%s    持ち出す" % [i + 1, str(entry.get("name", "")), suffix], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tdraw_ui_text(Vector2(240, 244), "%d階到達までの商品" % village_unlocked_floor(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#aeb7c2"))
\t\t\tfor i in range(catalog.size()):
\t\t\t\tvar offer: Dictionary = catalog[i]; var r := Rect2(48, 250 + i * 54, 624, 46); draw_panel(r)
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [str(offer["label"]), int(offer["price"])], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\tvar back := Rect2(48, 882, 270, 64); draw_panel(back)
\t\tdraw_ui_text(back.position + Vector2(24, 42), "戻る", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color.WHITE)
\tdraw_panel(Rect2(40, 984, 640, 70), Color("#111820"), Color("#394653"), 1.0)
\tdraw_ui_text(Vector2(54, 1028), message.left(40), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#e5d37d"))
\tdraw_ui_text(Vector2(465, 46), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#7f8b98"))
'''
s = s[:start] + draw_block + s[end:]

# Enlarge and move level display to the top of the Torneko-style status tile.
old_level_hud = '''\tdraw_ui_text(Vector2(46,153), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color("#241d18"))
\tdraw_ui_text(Vector2(38,177), "Lv.%d" % player_level, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#4b3524"))'''
new_level_hud = '''\tdraw_ui_text(Vector2(34,143), "Lv.%d" % player_level, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#241d18"))
\tdraw_ui_text(Vector2(43,176), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#4b3524"))'''
if old_level_hud not in s:
    raise SystemExit("STEP76 level HUD anchor failed")
s = s.replace(old_level_hud, new_level_hud, 1)

# Regression coverage for shop gates, warehouse cap, and the initial catalog.
test_anchor = "\n\nfunc debug_test_ui_glyph_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP76 test anchor failed")
test_func = '''

func debug_test_shinobi_village_contract() -> String:
\tvar old_warehouse := warehouse_items.duplicate(true)
\tvar old_known := known_enemies.duplicate(true)
\twarehouse_items = []
\tknown_enemies["max_floor"] = 1
\tvar initial := village_shop_catalog()
\tvar initial_ok := initial.size() == 3 and str(initial[0].get("label", "")) == "手裏剣10" and str(initial[1].get("label", "")) == "薬小" and str(initial[2].get("label", "")) == "兵糧丸小"
\tfor _i in range(WAREHOUSE_CAPACITY): warehouse_items.append({"name":"薬", "identified":true, "count":1})
\tvar cap_ok := not warehouse_add_item({"name":"兵糧丸", "count":1}) and warehouse_items.size() == WAREHOUSE_CAPACITY
\tknown_enemies["max_floor"] = 50
\tvar gate_ok := village_shop_catalog().size() > initial.size()
\twarehouse_items = old_warehouse
\tknown_enemies = old_known
\treturn "PASS 忍びの里" if initial_ok and cap_ok and gate_ok else "FAIL 忍びの里"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace('''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_ui_glyph_contract()''', '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_shinobi_village_contract(),
\t\tdebug_test_ui_glyph_contract()''', 1)

required = [
    "STEP76_SHINOBI_VILLAGE_APPLIED",
    "const WAREHOUSE_CAPACITY := 50",
    "func village_shop_catalog",
    '"label":"手裏剣10"',
    '"label":"薬小"',
    '"label":"兵糧丸小"',
    "func synthesize_equipment",
    "func warehouse_store_carried_all",
    'draw_ui_text(Vector2(34,143), "Lv.%d" % player_level',
    "debug_test_shinobi_village_contract()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP76 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP76 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP76_SHINOBI_VILLAGE PASS")
exec(Path("tools/apply_step77_village_carry_and_warehouse_scroll.py").read_text(encoding="utf-8"), {})
