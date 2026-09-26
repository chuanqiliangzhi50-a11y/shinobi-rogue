from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP77_VILLAGE_CARRY_SCROLL_APPLIED" in s:
    print("STEP77_VILLAGE_CARRY_SCROLL PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP76_SHINOBI_VILLAGE_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP77 STEP76 anchor failed")
s = s.replace(
    marker,
    marker
    + "# STEP77_VILLAGE_CARRY_SCROLL_APPLIED\n"
    + "const VILLAGE_CARRY_CAP := 5\n"
    + "const WAREHOUSE_VISIBLE_ROWS := 8\n",
    1,
)

state_anchor = "var warehouse_items: Array = []\n"
if state_anchor not in s:
    raise SystemExit("STEP77 warehouse state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + "var warehouse_scroll_offset := 0\n"
    + "var warehouse_scroll_drag_y := 0.0\n"
    + "var warehouse_touch_pending := -1\n"
    + "var warehouse_touch_dragged := false\n",
    1,
)

helper_anchor = "\n\nfunc village_unlocked_floor() -> int:\n"
if helper_anchor not in s:
    raise SystemExit("STEP77 helper anchor failed")
helpers = '''

func village_carry_has_space_for(name: String) -> bool:
\tif is_projectile_name(name):
\t\tfor entry in inventory_items:
\t\t\tif str(entry.get("name", "")) == name: return true
\treturn inventory_items.size() < VILLAGE_CARRY_CAP


func warehouse_max_scroll() -> int:
\treturn maxi(0, warehouse_items.size() - WAREHOUSE_VISIBLE_ROWS)


func warehouse_sync_scroll() -> void:
\twarehouse_scroll_offset = clampi(warehouse_scroll_offset, 0, warehouse_max_scroll())


func warehouse_scroll(delta_rows: int) -> void:
\twarehouse_scroll_offset = clampi(warehouse_scroll_offset + delta_rows, 0, warehouse_max_scroll())
\tqueue_redraw()
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

# Enforce the five-slot departure loadout at both selection and departure time.
withdraw_old = '''\tvar entry: Dictionary = warehouse_items[index]
\tvar name := str(entry.get("name", ""))
\tif not inventory_has_space_for(name):
\t\tmessage = "持ち物は20個まで。"
\t\treturn'''
withdraw_new = '''\tvar entry: Dictionary = warehouse_items[index]
\tvar name := str(entry.get("name", ""))
\tif not village_carry_has_space_for(name):
\t\tmessage = "出陣に持ち込める道具は5個まで。"
\t\treturn
\tif not inventory_has_space_for(name):
\t\tmessage = "持ち物がいっぱいだ。"
\t\treturn'''
if withdraw_old not in s:
    raise SystemExit("STEP77 withdraw capacity anchor failed")
s = s.replace(withdraw_old, withdraw_new, 1)
s = s.replace(
    '''\twarehouse_items.remove_at(index)
\tsave_meta()''',
    '''\twarehouse_items.remove_at(index)
\twarehouse_sync_scroll()
\tsave_meta()''',
    1,
)

start_anchor = '''func start_run() -> void:
\tin_village = false'''
start_new = '''func start_run() -> void:
\tif inventory_items.size() > VILLAGE_CARRY_CAP:
\t\tmessage = "出陣に持ち込める道具は5個まで。倉庫へ預けよう。"
\t\tqueue_redraw()
\t\treturn
\tin_village = false'''
if start_anchor not in s:
    raise SystemExit("STEP77 start capacity anchor failed")
s = s.replace(start_anchor, start_new, 1)

# Reset/synchronize list position when entering or changing the warehouse.
s = s.replace(
    'if event.keycode == KEY_2: village_menu = "warehouse"; message = "倉庫"',
    'if event.keycode == KEY_2: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"',
    1,
)
s = s.replace(
    '''\t\telif village_menu == "warehouse":
\t\t\tif event.keycode == KEY_P: message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all()
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9: warehouse_withdraw(int(event.keycode - KEY_1))''',
    '''\t\telif village_menu == "warehouse":
\t\t\tif event.keycode == KEY_P: message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
\t\t\telif event.keycode == KEY_UP: warehouse_scroll(-1)
\t\t\telif event.keycode == KEY_DOWN: warehouse_scroll(1)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_8: warehouse_withdraw(warehouse_scroll_offset + int(event.keycode - KEY_1))''',
    1,
)

# Swipe scrolling takes priority while the warehouse screen is open.
input_anchor = '''func _input(event: InputEvent) -> void:
\tif inventory_menu and event is InputEventScreenDrag:'''
input_new = '''func _input(event: InputEvent) -> void:
\tif in_village and village_menu == "warehouse" and event is InputEventScreenTouch:
\t\tvar warehouse_touch_pos := event.position - content_offset()
\t\tif event.pressed:
\t\t\twarehouse_touch_pending = -1
\t\t\twarehouse_touch_dragged = false
\t\t\tfor row in range(WAREHOUSE_VISIBLE_ROWS):
\t\t\t\tvar index := warehouse_scroll_offset + row
\t\t\t\tif index >= warehouse_items.size(): break
\t\t\t\tif Rect2(48, 318 + row * 62, 624, 52).has_point(warehouse_touch_pos):
\t\t\t\t\twarehouse_touch_pending = index
\t\t\t\t\treturn
\t\t\thandle_village_touch_portrait(warehouse_touch_pos)
\t\telse:
\t\t\tif warehouse_touch_pending >= 0 and not warehouse_touch_dragged:
\t\t\t\twarehouse_withdraw(warehouse_touch_pending)
\t\t\twarehouse_touch_pending = -1
\t\t\twarehouse_touch_dragged = false
\t\treturn
\tif in_village and village_menu == "warehouse" and event is InputEventScreenDrag:
\t\twarehouse_touch_dragged = true
\t\twarehouse_scroll_drag_y += event.relative.y
\t\tif abs(warehouse_scroll_drag_y) >= 36.0:
\t\t\twarehouse_scroll(-1 if warehouse_scroll_drag_y > 0.0 else 1)
\t\t\twarehouse_scroll_drag_y = 0.0
\t\treturn
\tif inventory_menu and event is InputEventScreenDrag:'''
if input_anchor not in s:
    raise SystemExit("STEP77 drag input anchor failed")
s = s.replace(input_anchor, input_new, 1)

# Touch rows use the scroll offset; dedicated buttons offer an alternative to swiping.
s = s.replace(
    'elif i == 1: village_menu = "warehouse"; message = "倉庫"',
    'elif i == 1: village_menu = "warehouse"; warehouse_sync_scroll(); message = "倉庫"',
    1,
)
touch_old = '''\t\telif village_menu == "warehouse":
\t\t\tif Rect2(48, 238, 624, 64).has_point(pos): message = "%d個を倉庫へ預けた。" % warehouse_store_carried_all()
\t\t\telse:
\t\t\t\tfor i in range(mini(8, warehouse_items.size())):
\t\t\t\t\tif Rect2(48, 318 + i * 64, 624, 54).has_point(pos): warehouse_withdraw(i); break'''
touch_new = '''\t\telif village_menu == "warehouse":
\t\t\tif Rect2(48, 238, 624, 64).has_point(pos):
\t\t\t\tmessage = "%d個を倉庫へ預けた。" % warehouse_store_carried_all(); warehouse_sync_scroll()
\t\t\telif Rect2(48, 824, 270, 48).has_point(pos): warehouse_scroll(-WAREHOUSE_VISIBLE_ROWS)
\t\t\telif Rect2(402, 824, 270, 48).has_point(pos): warehouse_scroll(WAREHOUSE_VISIBLE_ROWS)
\t\t\telse:
\t\t\t\tfor row in range(WAREHOUSE_VISIBLE_ROWS):
\t\t\t\t\tvar index := warehouse_scroll_offset + row
\t\t\t\t\tif index >= warehouse_items.size(): break
\t\t\t\t\tif Rect2(48, 318 + row * 62, 624, 52).has_point(pos): warehouse_withdraw(index); break'''
if touch_old not in s:
    raise SystemExit("STEP77 warehouse touch anchor failed")
s = s.replace(touch_old, touch_new, 1)

draw_old = '''\t\t\tfor i in range(mini(8, warehouse_items.size())):
\t\t\t\tvar entry: Dictionary = warehouse_items[i]; var r := Rect2(48, 318 + i * 64, 624, 54); draw_panel(r)
\t\t\t\tvar suffix := "×%d" % int(entry.get("count", 1)) if is_projectile_name(str(entry.get("name", ""))) else ""
\t\t\t\tdraw_ui_text(r.position + Vector2(18, 36), "%d  %s%s    持ち出す" % [i + 1, str(entry.get("name", "")), suffix], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)'''
draw_new = '''\t\t\twarehouse_sync_scroll()
\t\t\tfor row in range(WAREHOUSE_VISIBLE_ROWS):
\t\t\t\tvar index := warehouse_scroll_offset + row
\t\t\t\tif index >= warehouse_items.size(): break
\t\t\t\tvar entry: Dictionary = warehouse_items[index]; var r := Rect2(48, 318 + row * 62, 624, 52); draw_panel(r)
\t\t\t\tvar suffix := "×%d" % int(entry.get("count", 1)) if is_projectile_name(str(entry.get("name", ""))) else ""
\t\t\t\tdraw_ui_text(r.position + Vector2(18, 35), "%d  %s%s    持ち出す" % [index + 1, str(entry.get("name", "")), suffix], HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\t\tvar prev := Rect2(48, 824, 270, 48); var next := Rect2(402, 824, 270, 48)
\t\t\tdraw_panel(prev, Color("#18212b"), Color("#455464") if warehouse_scroll_offset > 0 else Color("#29323b"))
\t\t\tdraw_panel(next, Color("#18212b"), Color("#455464") if warehouse_scroll_offset < warehouse_max_scroll() else Color("#29323b"))
\t\t\tdraw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\t\tdraw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)'''
if draw_old not in s:
    raise SystemExit("STEP77 warehouse draw anchor failed")
s = s.replace(draw_old, draw_new, 1)

# Make the departure cap visible in the village header.
s = s.replace(
    '''"最高到達 %dF    倉庫 %d/50    持ち物 %d/20" % [village_unlocked_floor(), warehouse_items.size(), inventory_items.size()]''',
    '''"最高到達 %dF    倉庫 %d/50    持込 %d/5" % [village_unlocked_floor(), warehouse_items.size(), inventory_items.size()]''',
    1,
)

test_anchor = "\n\nfunc debug_test_shinobi_village_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP77 regression anchor failed")
test_func = '''

func debug_test_village_carry_and_scroll() -> String:
\tvar old_inventory := inventory_items.duplicate(true)
\tvar old_warehouse := warehouse_items.duplicate(true)
\tvar old_offset := warehouse_scroll_offset
\tinventory_items = []
\twarehouse_items = []
\tfor _i in range(12): warehouse_items.append({"name":"薬", "identified":true, "count":1})
\tfor _i in range(VILLAGE_CARRY_CAP): inventory_items.append({"name":"兵糧丸", "identified":true, "count":1})
\tvar cap_ok := not village_carry_has_space_for("薬")
\twarehouse_scroll_offset = 0
\twarehouse_scroll(WAREHOUSE_VISIBLE_ROWS)
\tvar scroll_ok := warehouse_scroll_offset == 4
\tinventory_items = old_inventory
\twarehouse_items = old_warehouse
\twarehouse_scroll_offset = old_offset
\treturn "PASS 持込5倉庫スクロール" if cap_ok and scroll_ok else "FAIL 持込5倉庫スクロール"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace(
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_shinobi_village_contract(),''',
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_carry_and_scroll(),
\t\tdebug_test_shinobi_village_contract(),''',
    1,
)

required = [
    "STEP77_VILLAGE_CARRY_SCROLL_APPLIED",
    "const VILLAGE_CARRY_CAP := 5",
    "func village_carry_has_space_for",
    "func warehouse_scroll",
    "warehouse_scroll_offset + row",
    '"最高到達 %dF    倉庫 %d/50    持込 %d/5"',
    "debug_test_village_carry_and_scroll()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP77 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP77 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP77_VILLAGE_CARRY_SCROLL PASS")
