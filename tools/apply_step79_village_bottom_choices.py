from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP79_VILLAGE_BOTTOM_CHOICES_APPLIED" in s:
    print("STEP79_VILLAGE_BOTTOM_CHOICES PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP78_VILLAGE_ILLUSTRATIONS_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP79 STEP78 anchor failed")
s = s.replace(marker, marker + "# STEP79_VILLAGE_BOTTOM_CHOICES_APPLIED\n", 1)

s = s.replace(
    "const WAREHOUSE_VISIBLE_ROWS := 8",
    "const WAREHOUSE_VISIBLE_ROWS := 5",
    1,
)
s = s.replace(
    "var scroll_ok := warehouse_scroll_offset == 4",
    "var scroll_ok := warehouse_scroll_offset == mini(WAREHOUSE_VISIBLE_ROWS, warehouse_max_scroll())",
    1,
)

# Warehouse row hit testing must follow its new lower-screen list.
s = s.replace(
    "Rect2(48, 318 + row * 62, 624, 52).has_point(warehouse_touch_pos)",
    "Rect2(48, 584 + row * 54, 624, 46).has_point(warehouse_touch_pos)",
    1,
)

touch_start = s.find("func handle_village_touch_portrait(pos: Vector2) -> void:")
touch_end = s.find("\n\nfunc handle_modal_touch_portrait", touch_start)
if touch_start < 0 or touch_end < 0:
    raise SystemExit("STEP79 touch block failed")

touch_block = '''func village_main_choice_rect(index: int) -> Rect2:
\tvar column := index % 2
\tvar row := floori(index / 2.0)
\treturn Rect2(48 + column * 324, 758 + row * 96, 300, 82)


func village_shop_choice_y(item_count: int, index: int) -> float:
\treturn maxf(330.0, 890.0 - item_count * 54.0) + index * 54.0


func handle_village_touch_portrait(pos: Vector2) -> void:
\tif village_menu == "main":
\t\tfor i in range(4):
\t\t\tif village_main_choice_rect(i).has_point(pos):
\t\t\t\tif i == 0: village_menu = "blacksmith"; message = "鍛冶屋"
\t\t\t\telif i == 1: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"
\t\t\t\telif i == 2: village_menu = "village_shop"; message = "商店"
\t\t\t\telse: start_run()
\t\t\t\tqueue_redraw(); return
\telse:
\t\tif Rect2(48, 910, 180, 48).has_point(pos): village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "blacksmith":
\t\t\tif Rect2(48, 744, 624, 68).has_point(pos): synthesize_equipment("weapon")
\t\t\telif Rect2(48, 826, 624, 68).has_point(pos): synthesize_equipment("armor")
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
\t\t\tfor i in range(catalog.size()):
\t\t\t\tif Rect2(48, village_shop_choice_y(catalog.size(), i), 624, 46).has_point(pos): buy_village_shop_item(i); break
\t\tqueue_redraw()
'''
s = s[:touch_start] + touch_block + s[touch_end:]

draw_start = s.find("func draw_village_portrait() -> void:")
draw_end = s.find("\n\nfunc dungeon_visual_hash", draw_start)
if draw_start < 0 or draw_end < 0:
    raise SystemExit("STEP79 village draw block failed")

draw_block = '''func draw_village_portrait() -> void:
\tvar scene_key := village_menu if village_scene_textures.has(village_menu) else "main"
\tvar scene_texture: Texture2D = village_scene_textures.get(scene_key, null) as Texture2D
\tif scene_texture != null:
\t\tdraw_texture_rect(scene_texture, Rect2(0, 0, 720, 1100), false)
\telse:
\t\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
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
\t\tvar title := "鍛冶屋" if village_menu == "blacksmith" else ("倉庫" if village_menu == "warehouse" else "商店")
\t\tdraw_ui_text(Vector2(48, 244), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 32, Color("#e8d47f"))
\t\tif village_menu == "blacksmith":
\t\t\tvar weapon_price := 50 + smith_weapon_rank * 25
\t\t\tvar armor_price := 50 + smith_armor_rank * 25
\t\t\tvar actions = ["忍刀 +%d → +%d（銭%d）" % [smith_weapon_rank, smith_weapon_rank + 1, weapon_price], "忍装束 +%d → +%d（銭%d）" % [smith_armor_rank, smith_armor_rank + 1, armor_price]]
\t\t\tfor i in range(actions.size()):
\t\t\t\tvar r := Rect2(48, 744 + i * 82, 624, 68); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"), 2.0)
\t\t\t\tdraw_ui_text(r.position + Vector2(20, 44), actions[i], HORIZONTAL_ALIGNMENT_LEFT, -1, 21, Color.WHITE)
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
\t\t\tvar catalog := village_shop_catalog()
\t\t\tdraw_ui_text(Vector2(240, 244), "%d階到達までの商品" % village_unlocked_floor(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d8dee5"))
\t\t\tfor i in range(catalog.size()):
\t\t\t\tvar offer: Dictionary = catalog[i]; var r := Rect2(48, village_shop_choice_y(catalog.size(), i), 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [str(offer["label"]), int(offer["price"])], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\tvar back := Rect2(48, 910, 180, 48); draw_panel(back, Color(0.04, 0.07, 0.10, 0.92), Color("#687786"))
\t\tdraw_ui_text(back.position + Vector2(24, 33), "戻る", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color.WHITE)
\tdraw_panel(Rect2(40, 984, 640, 70), Color(0.04, 0.07, 0.10, 0.90), Color("#394653"), 1.0)
\tdraw_ui_text(Vector2(54, 1028), message.left(40), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#e5d37d"))
\tdraw_ui_text(Vector2(465, 46), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#7f8b98"))
'''
s = s[:draw_start] + draw_block + s[draw_end:]

test_anchor = "\n\nfunc debug_test_village_illustration_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP79 regression anchor failed")
test_func = '''

func debug_test_village_bottom_choice_layout() -> String:
\tvar a := village_main_choice_rect(0)
\tvar b := village_main_choice_rect(1)
\tvar c := village_main_choice_rect(2)
\tvar d := village_main_choice_rect(3)
\tvar bottom_ok := a.position.y >= 740.0 and d.end.y < 984.0
\tvar grid_ok := a.position.y == b.position.y and c.position.y == d.position.y and a.position.x == c.position.x and b.position.x == d.position.x
\treturn "PASS village bottom 2x2" if bottom_ok and grid_ok else "FAIL village bottom 2x2"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace(
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_illustration_contract(),''',
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_bottom_choice_layout(),
\t\tdebug_test_village_illustration_contract(),''',
    1,
)

required = [
    "STEP79_VILLAGE_BOTTOM_CHOICES_APPLIED",
    "func village_main_choice_rect(index: int) -> Rect2:",
    "Rect2(48 + column * 324, 758 + row * 96, 300, 82)",
    "const WAREHOUSE_VISIBLE_ROWS := 5",
    "debug_test_village_bottom_choice_layout()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP79 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP79 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP79_VILLAGE_BOTTOM_CHOICES PASS")
exec(Path("tools/apply_step80_equipment_arsenal.py").read_text(encoding="utf-8"), {})
