from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP88_IDLE_SHOP_IDENTIFICATION_APPLIED" in s:
    print("STEP88_IDLE_SHOP_IDENTIFICATION PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP87_ENEMY_DIRECTIONS_RANKED_DROPS_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP88 requires STEP87")
s = s.replace(marker, marker + "# STEP88_IDLE_SHOP_IDENTIFICATION_APPLIED\n", 1)

glyph_anchor = '\t"級": "res://art/step76_glyphs/u7d1a.svg",\n'
if glyph_anchor not in s:
    raise SystemExit("STEP88 glyph map anchor failed")
s = s.replace(glyph_anchor, glyph_anchor +
              '\t"ぐ": "res://art/step76_glyphs/u3050.svg",\n'
              '\t"売": "res://art/step76_glyphs/u58f2.svg",\n'
              '\t"買": "res://art/step76_glyphs/u8cb7.svg",\n', 1)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP88 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 1)
    if end < 0:
        raise SystemExit(f"STEP88 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n\n" + s[end + 1:]


# The village shop opens on a dedicated buy/sell choice screen.
s = s.replace('var village_shop_mode := "buy"', 'var village_shop_mode := "choose"', 1)
s = s.replace('village_menu = "village_shop"; village_shop_mode = "buy"; village_shop_scroll_offset = 0; message = "商店"',
              'village_menu = "village_shop"; village_shop_mode = "choose"; village_shop_scroll_offset = 0; message = "商店で何をする？"')

replace_func("village_shop_entries", '''func village_shop_entries() -> Array:
\tif village_shop_mode == "buy": return village_shop_catalog()
\tif village_shop_mode == "sell": return warehouse_items
\treturn []''')

replace_func("village_shop_toggle_mode", '''func village_shop_toggle_mode() -> void:
\tif village_shop_mode == "choose": village_shop_mode = "buy"
\telse: village_shop_mode = "sell" if village_shop_mode == "buy" else "buy"
\tvillage_shop_scroll_offset = 0
\tmessage = "どうぐを買う。" if village_shop_mode == "buy" else "道具を売る。"
\tqueue_redraw()''')

# Keyboard support mirrors the touch-first choice screen.
old_keys = '''\t\telif village_menu == "village_shop":
\t\t\tif event.keycode == KEY_TAB: village_shop_toggle_mode()
\t\t\telif event.keycode == KEY_UP: village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode == KEY_DOWN: village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\t\tvar index := village_shop_scroll_offset + int(event.keycode - KEY_1)
\t\t\t\tif village_shop_mode == "buy": buy_village_shop_item(index)
\t\t\t\telse: sell_village_shop_item(index)'''
new_keys = '''\t\telif village_menu == "village_shop":
\t\t\tif village_shop_mode == "choose":
\t\t\t\tif event.keycode == KEY_1: village_shop_mode = "buy"; message = "どうぐを買う。"
\t\t\t\telif event.keycode == KEY_2: village_shop_mode = "sell"; message = "道具を売る。"
\t\t\telif event.keycode == KEY_TAB: village_shop_toggle_mode()
\t\t\telif event.keycode == KEY_UP: village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode == KEY_DOWN: village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\t\tvar index := village_shop_scroll_offset + int(event.keycode - KEY_1)
\t\t\t\tif village_shop_mode == "buy": buy_village_shop_item(index)
\t\t\t\telif village_shop_mode == "sell": sell_village_shop_item(index)'''
if old_keys not in s:
    raise SystemExit("STEP88 shop keyboard anchor failed")
s = s.replace(old_keys, new_keys, 1)

# Back from an item list returns to the shop choice screen.
old_back = '''\t\telif village_menu == "warehouse_select": village_menu = "main"; message = "忍びの里。"
\t\telse: village_menu = "main"; message = "忍びの里。"'''
new_back = '''\t\telif village_menu == "warehouse_select": village_menu = "main"; message = "忍びの里。"
\t\telif village_menu == "village_shop" and village_shop_mode != "choose": village_shop_mode = "choose"; village_shop_scroll_offset = 0; message = "商店で何をする？"
\t\telse: village_menu = "main"; message = "忍びの里。"'''
if old_back not in s:
    raise SystemExit("STEP88 shop back anchor failed")
s = s.replace(old_back, new_back, 1)

old_touch = '''\telif village_menu == "village_shop":
\t\tif Rect2(48,286,624,48).has_point(pos): village_shop_toggle_mode()
\t\telif Rect2(48,842,270,48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\telif Rect2(402,842,270,48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\telse:
\t\t\tvar entries := village_shop_entries(); village_shop_sync_scroll()
\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
\t\t\tfor row in range(visible_count):
\t\t\t\tvar index := village_shop_scroll_offset+row
\t\t\t\tif Rect2(48,village_shop_choice_y(visible_count,row),624,46).has_point(pos):
\t\t\t\t\tif village_shop_mode == "buy": buy_village_shop_item(index)
\t\t\t\t\telse: sell_village_shop_item(index)
\t\t\t\t\tbreak'''
new_touch = '''\telif village_menu == "village_shop":
\t\tif village_shop_mode == "choose":
\t\t\tif Rect2(48,548,624,90).has_point(pos): village_shop_mode = "buy"; village_shop_scroll_offset = 0; message = "どうぐを買う。"
\t\t\telif Rect2(48,660,624,90).has_point(pos): village_shop_mode = "sell"; village_shop_scroll_offset = 0; message = "道具を売る。"
\t\telif Rect2(48,286,624,48).has_point(pos): village_shop_toggle_mode()
\t\telif Rect2(48,842,270,48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\telif Rect2(402,842,270,48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\telse:
\t\t\tvar entries := village_shop_entries(); village_shop_sync_scroll()
\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
\t\t\tfor row in range(visible_count):
\t\t\t\tvar index := village_shop_scroll_offset+row
\t\t\t\tif Rect2(48,village_shop_choice_y(visible_count,row),624,46).has_point(pos):
\t\t\t\t\tif village_shop_mode == "buy": buy_village_shop_item(index)
\t\t\t\t\telif village_shop_mode == "sell": sell_village_shop_item(index)
\t\t\t\t\tbreak'''
if old_touch not in s:
    raise SystemExit("STEP88 shop touch anchor failed")
s = s.replace(old_touch, new_touch, 1)

old_draw = '''\t\telif village_menu == "village_shop":
\t\t\tvar entries := village_shop_entries(); village_shop_sync_scroll(); var mode_button := Rect2(48,286,624,48); draw_panel(mode_button,Color(0.16,0.15,0.08,0.92),Color("#d7bf66"))
\t\t\tvar mode_text := "購入中｜倉庫の品を手放す" if village_shop_mode=="buy" else "手放す｜購入へ戻る"; draw_ui_text(mode_button.position+Vector2(18,33),mode_text,HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
\t\t\tfor row in range(visible_count):
\t\t\t\tvar index := village_shop_scroll_offset+row; var entry: Dictionary = entries[index]; var r := Rect2(48,village_shop_choice_y(visible_count,row),624,46); draw_panel(r,Color(0.04,0.07,0.10,0.90),Color("#687786"))
\t\t\t\tvar label := (equipment_display_name(str(entry["name"])) if is_equipment_name(str(entry["name"])) else str(entry["label"])) if village_shop_mode=="buy" else equipment_entry_label(entry); var price := int(entry["price"]) if village_shop_mode=="buy" else village_sell_price(entry)
\t\t\t\tdraw_ui_text(r.position+Vector2(16,31),"%s    %d銭" % [label,price],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE)
\t\t\tvar prev := Rect2(48,842,270,48); var next := Rect2(402,842,270,48); draw_panel(prev,Color("#101923"),Color("#687786")); draw_panel(next,Color("#101923"),Color("#687786"))
\t\t\tdraw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)'''
new_draw = '''\t\telif village_menu == "village_shop":
\t\t\tif village_shop_mode == "choose":
\t\t\t\tdraw_ui_text(Vector2(48,494),"用件を選んでください",HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color.WHITE)
\t\t\t\tvar buy_choice := Rect2(48,548,624,90); var sell_choice := Rect2(48,660,624,90)
\t\t\t\tdraw_panel(buy_choice,Color(0.12,0.18,0.13,0.94),Color("#d7bf66"),2.0); draw_panel(sell_choice,Color(0.16,0.12,0.10,0.94),Color("#d7bf66"),2.0)
\t\t\t\tdraw_ui_text(buy_choice.position+Vector2(0,57),"どうぐを　買う",HORIZONTAL_ALIGNMENT_CENTER,buy_choice.size.x,24,Color.WHITE)
\t\t\t\tdraw_ui_text(sell_choice.position+Vector2(0,57),"道具を　売る",HORIZONTAL_ALIGNMENT_CENTER,sell_choice.size.x,24,Color.WHITE)
\t\t\telse:
\t\t\t\tvar entries := village_shop_entries(); village_shop_sync_scroll(); var mode_button := Rect2(48,286,624,48); draw_panel(mode_button,Color(0.16,0.15,0.08,0.92),Color("#d7bf66"))
\t\t\t\tvar mode_text := "購入中｜道具を売る" if village_shop_mode=="buy" else "道具を売る｜どうぐを買う"; draw_ui_text(mode_button.position+Vector2(18,33),mode_text,HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
\t\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS,entries.size()-village_shop_scroll_offset)
\t\t\t\tfor row in range(visible_count):
\t\t\t\t\tvar index := village_shop_scroll_offset+row; var entry: Dictionary = entries[index]; var r := Rect2(48,village_shop_choice_y(visible_count,row),624,46); draw_panel(r,Color(0.04,0.07,0.10,0.90),Color("#687786"))
\t\t\t\t\tvar label := (equipment_display_name(str(entry["name"])) if is_equipment_name(str(entry["name"])) else str(entry["label"])) if village_shop_mode=="buy" else equipment_entry_label(entry); var price := int(entry["price"]) if village_shop_mode=="buy" else village_sell_price(entry)
\t\t\t\t\tdraw_ui_text(r.position+Vector2(16,31),"%s    %d銭" % [label,price],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE)
\t\t\t\tvar prev := Rect2(48,842,270,48); var next := Rect2(402,842,270,48); draw_panel(prev,Color("#101923"),Color("#687786")); draw_panel(next,Color("#101923"),Color("#687786"))
\t\t\t\tdraw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)'''
if old_draw not in s:
    raise SystemExit("STEP88 shop draw anchor failed")
s = s.replace(old_draw, new_draw, 1)

# Keep both feet visually grounded while alternating the stance.
replace_func("enemy_idle_visual_offset", '''func enemy_idle_visual_offset(enemy: Dictionary) -> Vector2:
\tvar phase := float(absi(str(enemy.get("name", "敵")).hash()) % 628) / 100.0
\tvar speed := 4.0 if bool(enemy.get("boss", false)) else 5.0
\tvar step := sin(enemy_idle_anim_time * speed + phase)
\tvar side: float = step * (0.55 if bool(enemy.get("boss", false)) else 0.9)
\tvar grounded_drop: float = abs(step) * (0.35 if bool(enemy.get("boss", false)) else 0.7)
\tif int(enemy.get("bound", 0)) > 0: side *= 0.2
\treturn Vector2(side, grounded_drop)''')

player_anchor = '''\tvar running := dash_hold_active and dash_hold_repeating
\tvar draw_center := center
\tif running:'''
player_replacement = '''\tvar running := dash_hold_active and dash_hold_repeating
\tvar draw_center := center
\tif not running:
\t\tvar idle_step := sin(enemy_idle_anim_time * 5.2)
\t\tdraw_center += Vector2(idle_step * 0.9, abs(idle_step) * 0.7)
\tif running:'''
if player_anchor not in s:
    raise SystemExit("STEP88 player idle anchor failed")
s = s.replace(player_anchor, player_replacement, 1)

# Add a clear sword mark to the attack button.
attack_icon_anchor = '''\telif label == "罠":
\t\tdraw_arc(c + Vector2(0,-4), 13.0, PI, TAU, 20, ink, 3.0)'''
attack_icon_replacement = '''\telif label == "攻撃":
\t\tdraw_line(c + Vector2(-12,8), c + Vector2(10,-15), ink, 5.0)
\t\tdraw_line(c + Vector2(-15,4), c + Vector2(-7,12), ink, 4.0)
\t\tdraw_line(c + Vector2(7,-17), c + Vector2(14,-20), ink, 3.0)
\t\tdraw_circle(c + Vector2(-12,9), 3.5, Color("#e57b69"))
\telif label == "罠":
\t\tdraw_arc(c + Vector2(0,-4), 13.0, PI, TAU, 20, ink, 3.0)'''
if attack_icon_anchor not in s:
    raise SystemExit("STEP88 attack icon anchor failed")
s = s.replace(attack_icon_anchor, attack_icon_replacement, 1)

# Identification is automatic below 35F and uncertain from 35F onward.
identify_helper_anchor = "\nfunc add_inventory_item(name: String, identified: bool = false, count: int = 1, bonus: int = 0) -> void:\n"
if identify_helper_anchor not in s:
    raise SystemExit("STEP88 identification helper anchor failed")
identify_helper = '''
func floor_item_starts_identified(name: String, for_floor: int) -> bool:
\tif is_equipment_name(name) or is_projectile_name(name): return true
\tif for_floor < 35: return true
\treturn rng.randi_range(1, 100) > 30
'''
s = s.replace(identify_helper_anchor, "\n" + identify_helper.rstrip() + identify_helper_anchor, 1)

pickup_old = 'add_inventory_item(item_name, false, picked_count, entry_bonus(item))'
pickup_new = 'add_inventory_item(item_name, bool(item.get("identified", floor_item_starts_identified(item_name, floor_no))), picked_count, entry_bonus(item))'
if pickup_old not in s:
    raise SystemExit("STEP88 pickup identification anchor failed")
s = s.replace(pickup_old, pickup_new, 1)

# Remove the identify command from keyboard, touch, and the inventory footer.
s = s.replace('''\telif event.keycode == KEY_D:
\t\tinventory_identify_selected()
''', '', 1)
old_actions = 'var actions = [["equip", panel_x + 12.0], ["use", panel_x + 118.0], ["identify", panel_x + 224.0], ["floor", panel_x + 330.0], ["back", panel_x + 436.0]]'
new_actions = 'var actions = [["equip", panel_x + 12.0], ["use", panel_x + 148.0], ["floor", panel_x + 284.0], ["back", panel_x + 420.0]]'
if old_actions not in s:
    raise SystemExit("STEP88 inventory touch actions anchor failed")
s = s.replace(old_actions, new_actions, 1)
s = s.replace('Rect2(float(action[1]), action_y, 96.0, 52.0)', 'Rect2(float(action[1]), action_y, 124.0, 52.0)', 1)
s = s.replace('''\t\t\t\t"identify": inventory_identify_selected()
''', '', 1)
old_labels = 'var labels = [["装備", panel_x + 12.0], ["使用", panel_x + 118.0], ["識別", panel_x + 224.0], ["拾う", panel_x + 330.0], ["戻る", panel_x + 436.0]]'
new_labels = 'var labels = [["装備", panel_x + 12.0], ["使用", panel_x + 148.0], ["拾う", panel_x + 284.0], ["戻る", panel_x + 420.0]]'
if old_labels not in s:
    raise SystemExit("STEP88 inventory labels anchor failed")
s = s.replace(old_labels, new_labels, 1)
s = s.replace('Rect2(float(action[1]), action_y, 96.0, 52.0)', 'Rect2(float(action[1]), action_y, 124.0, 52.0)', 1)

# Replace the legacy inventory regression with the new 35F rule.
replace_func("debug_test_inventory_contract", '''func debug_test_inventory_contract() -> String:
\tinventory_items = []
\tadd_inventory_item("薬", floor_item_starts_identified("薬", 34))
\tvar early_ok := inventory_items.size() == 1 and bool(inventory_items[0].get("identified", false))
\tinventory_selected = 2
\thp = max(1, max_hp - 10)
\tvar before_hp := hp
\tinventory_use_selected(false)
\tvar use_ok := inventory_items.is_empty() and hp > before_hp
\tinventory_selected = 0
\tinventory_equip_selected()
\treturn "PASS 道具装備使用・35階識別" if early_ok and use_ok and message.find("装備中") >= 0 else "FAIL 道具装備使用"''')

test_anchor = "\nfunc debug_test_step87_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP88 regression anchor failed")
test_func = '''
func debug_test_step88_contract() -> String:
\tvar old_mode := village_shop_mode
\tvillage_shop_mode = "choose"
\tvar shop_ok := village_shop_entries().is_empty()
\tvillage_shop_mode = old_mode
\tvar floor_ok := floor_item_starts_identified("薬", 34)
\tvar motion_enemy := {"name":"下忍","boss":false,"bound":0}
\tenemy_idle_anim_time = 0.31
\tvar motion := enemy_idle_visual_offset(motion_enemy)
\tvar grounded_ok := motion.y >= 0.0 and motion.y <= 0.71
\treturn "PASS 足踏み・商店選択・攻撃印・35階未識別" if shop_ok and floor_ok and grounded_ok else "FAIL 足踏み商店識別"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step87_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP88 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step88_contract(),\n", 1)

required = [
    "STEP88_IDLE_SHOP_IDENTIFICATION_APPLIED",
    'village_shop_mode := "choose"',
    '"どうぐを　買う"', '"道具を　売る"',
    'elif label == "攻撃"',
    "func floor_item_starts_identified(",
    "PASS 足踏み・商店選択・攻撃印・35階未識別",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP88 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP88 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP88_IDLE_SHOP_IDENTIFICATION PASS")

