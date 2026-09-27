from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP89_FLOOR_TRAPS_CONTROLS_APPLIED" in s:
    print("STEP89_FLOOR_TRAPS_CONTROLS PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP88_IDLE_SHOP_IDENTIFICATION_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP89 requires STEP88")
s = s.replace(marker, marker + "# STEP89_FLOOR_TRAPS_CONTROLS_APPLIED\n", 1)

glyph_anchor = '\t"買": "res://art/step76_glyphs/u8cb7.svg",\n'
if glyph_anchor not in s:
    raise SystemExit("STEP89 glyph map anchor failed")
trap_glyphs = {
    "木":"u6728.svg", "矢":"u77e2.svg", "落":"u843d.svg", "穴":"u7a74.svg",
    "睡":"u7761.svg", "眠":"u7720.svg", "ガ":"u30ac.svg", "召":"u53ec.svg",
    "喚":"u559a.svg", "転":"u8ee2.svg", "石":"u77f3.svg", "減":"u6e1b.svg",
    "半":"u534a.svg", "ョ":"u30e7.svg", "列":"u5217.svg",
}
glyph_lines = "".join(f'\t"{ch}": "res://art/step76_glyphs/{filename}",\n' for ch, filename in trap_glyphs.items())
s = s.replace(glyph_anchor, glyph_anchor + glyph_lines, 1)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP89 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 1)
    if end < 0:
        raise SystemExit(f"STEP89 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n\n" + s[end + 1:]


# Eight dungeon traps inspired by classic turn-based dungeon crawlers.
trap_anchor = "var placed_traps: Array = []\n"
if trap_anchor not in s:
    raise SystemExit("STEP89 trap state anchor failed")
s = s.replace(trap_anchor, trap_anchor + '''const FLOOR_TRAP_TYPES := [
\t"木矢の罠", "毒矢の罠", "地雷の罠", "落とし穴",
\t"睡眠ガス", "召喚の罠", "転び石", "空腹の罠"
]
''', 1)

generation_anchor = '''\tfor i in range(4): spawn_item()
\tif floor_no >= 90:'''
if generation_anchor not in s:
    raise SystemExit("STEP89 trap generation anchor failed")
s = s.replace(generation_anchor, '''\tfor i in range(4): spawn_item()
\tgenerate_floor_traps()
\tif floor_no >= 90:''', 1)

spawn_anchor = "\nfunc carve_shop_room() -> void:\n"
if spawn_anchor not in s:
    raise SystemExit("STEP89 trap helper anchor failed")
trap_helpers = '''
func trap_spawn_chance(for_floor: int) -> int:
\tif for_floor < 10: return 0
\tif for_floor < 30: return 45
\tif for_floor < 60: return 60
\treturn 75


func trap_count_for_floor(for_floor: int) -> int:
\tif for_floor < 10: return 0
\tif for_floor < 30: return 1
\tif for_floor < 60: return rng.randi_range(1, 2)
\treturn rng.randi_range(2, 3)


func random_floor_trap_cell() -> Vector2i:
\tfor _attempt in range(180):
\t\tvar pos := Vector2i(rng.randi_range(1, MAP_W - 2), rng.randi_range(1, MAP_H - 2))
\t\tif not is_walkable(pos) or pos == player or pos == stairs_pos: continue
\t\tif enemy_index_at(pos) >= 0 or cell_has_item(pos): continue
\t\tif is_inside_shop(pos): continue
\t\tvar occupied := false
\t\tfor trap in placed_traps:
\t\t\tif typeof(trap) == TYPE_DICTIONARY and trap.get("pos", Vector2i(-1, -1)) == pos: occupied = true; break
\t\tif not occupied: return pos
\treturn Vector2i(-1, -1)


func generate_floor_traps() -> void:
\tif floor_no < 10 or rng.randi_range(1, 100) > trap_spawn_chance(floor_no): return
\tfor _i in range(trap_count_for_floor(floor_no)):
\t\tvar pos := random_floor_trap_cell()
\t\tif pos == Vector2i(-1, -1): continue
\t\tplaced_traps.append({"pos":pos, "type":FLOOR_TRAP_TYPES[rng.randi_range(0, FLOOR_TRAP_TYPES.size() - 1)], "revealed":false})
'''
s = s.replace(spawn_anchor, "\n" + trap_helpers.rstrip() + spawn_anchor, 1)

replace_func("place_trap", '''func place_trap() -> void:
\tmessage = "罠はダンジョンに隠されている。"
\tqueue_redraw()''')

replace_func("trigger_enemy_traps", '''func trigger_enemy_traps() -> void:
\t# Floor traps react only to the player.
\tpass''')

trigger_anchor = "\nfunc on_player_walked() -> void:\n"
if trigger_anchor not in s:
    raise SystemExit("STEP89 player trap trigger anchor failed")
trigger_helpers = '''
func trap_index_at(pos: Vector2i) -> int:
\tfor i in range(placed_traps.size()):
\t\tvar trap = placed_traps[i]
\t\tif typeof(trap) == TYPE_DICTIONARY and trap.get("pos", Vector2i(-1, -1)) == pos: return i
\treturn -1


func drop_random_bag_item_from_trap() -> String:
\tif inventory_items.is_empty(): return ""
\tvar index := rng.randi_range(0, inventory_items.size() - 1)
\tvar entry: Dictionary = inventory_items[index].duplicate(true)
\tvar name := str(entry.get("name", ""))
\tvar drop_pos := find_nearest_item_drop_cell(player)
\tif drop_pos == Vector2i(-1, -1): return ""
\tinventory_items.remove_at(index)
\tentry["pos"] = drop_pos; entry["shop"] = false; entry["price"] = 0
\titems.append(entry)
\treturn name


func activate_floor_trap(trap_type: String) -> void:
\tmatch trap_type:
\t\t"木矢の罠":
\t\t\thp = maxi(1, hp - 5); start_player_hit_flash(); message = "木矢の罠！ 5ダメージ。"
\t\t"毒矢の罠":
\t\t\thp = maxi(1, hp - 4); hunger = maxi(0, hunger - 10); start_player_hit_flash(); message = "毒矢の罠！ 体力と満腹度が減った。"
\t\t"地雷の罠":
\t\t\thp = maxi(1, int(ceil(float(hp) * 0.5))); start_player_hit_flash(); message = "地雷の罠！ 体力が半分になった。"
\t\t"落とし穴":
\t\t\thp = maxi(1, hp - 3); player = find_random_open_cell(); message = "落とし穴！ 別の場所へ落ちた。"
\t\t"睡眠ガス":
\t\t\tmove_enemies(); move_enemies(); message = "睡眠ガス！ 敵に2回動かれた。"
\t\t"召喚の罠":
\t\t\tspawn_enemy(false); spawn_enemy(false); message = "召喚の罠！ 敵が2体現れた。"
\t\t"転び石":
\t\t\tvar dropped := drop_random_bag_item_from_trap(); message = "転び石！" if dropped.is_empty() else "転び石！ %sを落とした。" % dropped
\t\t"空腹の罠":
\t\t\thunger = maxi(0, hunger - 25); message = "空腹の罠！ 満腹度が25減った。"


func trigger_player_floor_trap() -> void:
\tvar index := trap_index_at(player)
\tif index < 0: return
\tvar trap: Dictionary = placed_traps[index]
\tplaced_traps.remove_at(index)
\tactivate_floor_trap(str(trap.get("type", "木矢の罠")))
'''
s = s.replace(trigger_anchor, "\n" + trigger_helpers.rstrip() + trigger_anchor, 1)

replace_func("on_player_walked", '''func on_player_walked() -> void:
\ttrigger_player_floor_trap()
\tif not clone_active: return
\tclone_steps_left -= 1
\tif clone_steps_left <= 0:
\t\tclone_active = false
\t\tclone_pos = Vector2i(-1, -1)
\t\tclone_steps_left = 0
\t\tmessage = "影分身が霧のように消えた。"''')

# Preserve new trap dictionaries and convert old position-only saves safely.
sanitize_anchor = "\nfunc sanitize_enemy_array(value: Variant) -> Array:\n"
if sanitize_anchor not in s:
    raise SystemExit("STEP89 trap sanitize anchor failed")
sanitize_func = '''
func sanitize_trap_array(value: Variant) -> Array:
\tvar out: Array = []
\tif typeof(value) != TYPE_ARRAY: return out
\tfor raw in value:
\t\tif raw is Vector2i:
\t\t\tout.append({"pos":raw, "type":"木矢の罠", "revealed":false})
\t\telif raw is Vector2:
\t\t\tout.append({"pos":Vector2i(int(raw.x), int(raw.y)), "type":"木矢の罠", "revealed":false})
\t\telif typeof(raw) == TYPE_DICTIONARY:
\t\t\tvar pos = raw.get("pos", Vector2i(-1, -1)); var trap_type := str(raw.get("type", "木矢の罠"))
\t\t\tif validate_vector2i(pos) and trap_type in FLOOR_TRAP_TYPES:
\t\t\t\tout.append({"pos":pos, "type":trap_type, "revealed":bool(raw.get("revealed", false))})
\treturn out
'''
s = s.replace(sanitize_anchor, "\n" + sanitize_func.rstrip() + sanitize_anchor, 1)
s = s.replace('placed_traps = sanitize_vector2i_array(data.get("placed_traps", [])) if version >= 5 else []',
              'placed_traps = sanitize_trap_array(data.get("placed_traps", [])) if version >= 5 else []', 1)

# Hidden traps are not drawn before activation.
portrait_trap_draw = '''\tfor trap in placed_traps:
\t\tvar tp: Vector2i = trap
\t\tif portrait_cell_in_view(tp) and is_visible_cell(tp): draw_entity_visual(portrait_cell_center(tp), "trap", "罠", 20, Color("#e0a35c"), PTILE)
'''
if portrait_trap_draw not in s:
    raise SystemExit("STEP89 portrait trap draw anchor failed")
s = s.replace(portrait_trap_draw, '', 1)

landscape_trap_draw = '''\tfor trap in placed_traps:
\t\tvar tp: Vector2i = trap
\t\tif is_visible_cell(tp):
\t\t\tdraw_entity_visual(cell_center(tp), "trap", "罠", 14, Color("#e0a35c"), TILE)
'''
if landscape_trap_draw not in s:
    raise SystemExit("STEP89 landscape trap draw anchor failed")
s = s.replace(landscape_trap_draw, '', 1)

# Portrait controls: two rows, two columns, exactly as specified.
old_press = '''\tvar command_buttons = [
\t\t[Vector2(78,840),39.0,"inventory"], [Vector2(174,840),39.0,"trap"], [Vector2(270,840),39.0,"attack"],
\t\t[Vector2(126,936),39.0,"technique"], [Vector2(222,936),39.0,"throw"]
\t]'''
new_press = '''\tvar command_buttons = [
\t\t[Vector2(92,842),45.0,"throw"], [Vector2(238,842),45.0,"attack"],
\t\t[Vector2(92,946),45.0,"suspend"], [Vector2(238,946),45.0,"inventory"]
\t]'''
if old_press not in s:
    raise SystemExit("STEP89 portrait press layout anchor failed")
s = s.replace(old_press, new_press, 1)
s = s.replace('''\t\t\telif action == "trap": place_trap()
\t\t\telif action == "attack": attack_in_place()
\t\t\telif action == "technique": hide_one_turn()
\t\t\telif action == "throw": use_projectile()''', '''\t\t\telif action == "attack": attack_in_place()
\t\t\telif action == "throw": use_projectile()
\t\t\telif action == "suspend": suspend_run()''', 1)
s = s.replace('\tif Rect2(54,1002,240,44).has_point(pos): suspend_run(); return\n', '', 1)

old_draw_buttons = 'var command_buttons = [["道具",Vector2(78,840),39.0],["罠",Vector2(174,840),39.0],["攻撃",Vector2(270,840),39.0],["術",Vector2(126,936),39.0],["飛",Vector2(222,936),39.0]]'
new_draw_buttons = 'var command_buttons = [["飛",Vector2(92,842),45.0],["攻撃",Vector2(238,842),45.0],["中断",Vector2(92,946),45.0],["道具",Vector2(238,946),45.0]]'
if old_draw_buttons not in s:
    raise SystemExit("STEP89 portrait draw layout anchor failed")
s = s.replace(old_draw_buttons, new_draw_buttons, 1)
s = s.replace('''\tvar suspend := Rect2(54,1002,240,44); draw_panel(suspend,Color("#101923"),Color("#687786"),1.5); draw_ui_text(suspend.position+Vector2(0,30),"中断",HORIZONTAL_ALIGNMENT_CENTER,suspend.size.x,16,Color.WHITE)
''', '', 1)

# Landscape keeps the same four-command order.
old_land_touch = '''\tvar diamond_actions_landscape = [
\t\t[Rect2(714, 566, 48, 48), "inventory"],
\t\t[Rect2(660, 618, 48, 48), "trap"],
\t\t[Rect2(768, 618, 48, 48), "throw"],
\t\t[Rect2(714, 670, 48, 42), "suspend"]
\t]'''
new_land_touch = '''\tvar diamond_actions_landscape = [
\t\t[Rect2(660, 566, 48, 48), "throw"], [Rect2(714, 566, 48, 48), "attack"],
\t\t[Rect2(660, 620, 48, 48), "suspend"], [Rect2(714, 620, 48, 48), "inventory"]
\t]'''
if old_land_touch not in s:
    raise SystemExit("STEP89 landscape touch anchor failed")
s = s.replace(old_land_touch, new_land_touch, 1)
s = s.replace('''\t\t\telif d_name == "trap": place_trap()
\t\t\telif d_name == "throw": use_projectile()
\t\t\telif d_name == "suspend": suspend_run()''', '''\t\t\telif d_name == "throw": use_projectile()
\t\t\telif d_name == "attack": attack_in_place()
\t\t\telif d_name == "suspend": suspend_run()''', 1)
s = s.replace('''\t\t\telif action == "trap":
\t\t\t\tplace_trap()
''', '', 1)

old_land_draw = '''\tvar diamond_controls_landscape = [
\t\t["道具", Rect2(714, 566, 48, 48)],
\t\t["罠", Rect2(660, 618, 48, 48)],
\t\t["飛", Rect2(768, 618, 48, 48)],
\t\t["中断", Rect2(714, 670, 48, 42)]
\t]'''
new_land_draw = '''\tvar diamond_controls_landscape = [
\t\t["飛", Rect2(660, 566, 48, 48)], ["攻撃", Rect2(714, 566, 48, 48)],
\t\t["中断", Rect2(660, 620, 48, 48)], ["道具", Rect2(714, 620, 48, 48)]
\t]'''
if old_land_draw not in s:
    raise SystemExit("STEP89 landscape draw anchor failed")
s = s.replace(old_land_draw, new_land_draw, 1)
s = s.replace('if action == "throw" or action == "trap":', 'if action == "throw":', 1)

test_anchor = "\nfunc debug_test_step88_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP89 regression anchor failed")
test_func = '''
func debug_test_step89_contract() -> String:
\tvar types_ok := FLOOR_TRAP_TYPES.size() == 8 and FLOOR_TRAP_TYPES.has("地雷の罠") and FLOOR_TRAP_TYPES.has("転び石")
\tvar floor_ok := trap_spawn_chance(9) == 0 and trap_spawn_chance(10) == 45 and trap_spawn_chance(60) == 75
\tvar save_ok := sanitize_trap_array([{"pos":Vector2i(2,2),"type":"木矢の罠"}]).size() == 1
\treturn "PASS 罠8種・10階生成・2段2列" if types_ok and floor_ok and save_ok else "FAIL 罠生成操作配置"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step88_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP89 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step89_contract(),\n", 1)

required = [
    "STEP89_FLOOR_TRAPS_CONTROLS_APPLIED",
    "const FLOOR_TRAP_TYPES", "func generate_floor_traps(",
    "func trigger_player_floor_trap(", "PASS 罠8種・10階生成・2段2列",
    '[["飛",Vector2(92,842),45.0],["攻撃",Vector2(238,842),45.0]',
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP89 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP89 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP89_FLOOR_TRAPS_CONTROLS PASS")

exec(Path("tools/apply_step90_jutsu_learning_system.py").read_text(encoding="utf-8"), {})

