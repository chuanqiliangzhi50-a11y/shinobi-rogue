from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'REFERENCE_GAMEPLAY_SKIN_PATCH_APPLIED' in s:
    print('REFERENCE_GAMEPLAY_SKIN_PATCH PASS (already applied)')
    raise SystemExit(0)

anchor = 'var entity_art: Dictionary = {}\n'
if anchor not in s:
    raise SystemExit('skin entity art anchor failed')
s = s.replace(anchor, anchor + 'var enemy_sheet_texture: Texture2D = null # REFERENCE_GAMEPLAY_SKIN_PATCH_APPLIED\nvar item_sheet_texture: Texture2D = null\n', 1)

anchor = '\tload_optional_entity_art()\n'
if anchor not in s:
    raise SystemExit('skin ready anchor failed')
s = s.replace(anchor, anchor + '\tif ResourceLoader.exists("res://art/enemy_sheet.svg"):\n\t\tenemy_sheet_texture = load("res://art/enemy_sheet.svg") as Texture2D\n\tif ResourceLoader.exists("res://art/item_sheet.svg"):\n\t\titem_sheet_texture = load("res://art/item_sheet.svg") as Texture2D\n', 1)

s, n = re.subn(r'func portrait_cell_center\(p: Vector2i\) -> Vector2:\n.*?(?=\n\nfunc handle_press_portrait)', '''func portrait_cell_center(p: Vector2i) -> Vector2:
\tconst PTILE := 39
\tconst PMAP_X := 38
\tconst PMAP_Y := 206
\tvar origin := portrait_camera_origin()
\tvar local := p - origin
\treturn Vector2(PMAP_X + local.x * PTILE + PTILE * 0.5, PMAP_Y + local.y * PTILE + PTILE * 0.5)''', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'skin portrait center anchor failed: {n}')

handle = '''func handle_press_portrait(pos: Vector2) -> void:
\tif in_village:
\t\thandle_village_touch_portrait(pos)
\t\treturn
\tif inventory_menu:
\t\thandle_inventory_touch(pos, true)
\t\treturn
\tif checkout_prompt or stairs_prompt or ad_menu:
\t\thandle_modal_touch_portrait(pos)
\t\treturn
\tif Rect2(22, 662, 76, 76).has_point(pos):
\t\ttoggle_map_visibility()
\t\treturn
\tvar diamond_actions = [
\t\t[Rect2(122, 770, 96, 96), "inventory"],
\t\t[Rect2(52, 840, 96, 96), "trap"],
\t\t[Rect2(192, 840, 96, 96), "throw"],
\t\t[Rect2(122, 910, 96, 96), "suspend"]
\t]
\tfor d_action in diamond_actions:
\t\tvar d_rect: Rect2 = d_action[0]
\t\tif d_rect.has_point(pos):
\t\t\tvar d_name := str(d_action[1])
\t\t\tif d_name == "inventory": open_inventory()
\t\t\telif d_name == "trap": place_trap()
\t\t\telif d_name == "throw": use_projectile()
\t\t\telif d_name == "suspend": suspend_run()
\t\t\tqueue_redraw()
\t\t\treturn
\tvar base := Vector2(382, 772)
\tvar cell := 98.0
\tif pos.x >= base.x and pos.x < base.x + cell * 3.0 and pos.y >= base.y and pos.y < base.y + cell * 3.0:
\t\tvar cx := int((pos.x - base.x) / cell)
\t\tvar cy := int((pos.y - base.y) / cell)
\t\tvar d := Vector2i(cx - 1, cy - 1)
\t\tif d == Vector2i.ZERO:
\t\t\thide_one_turn()
\t\telse:
\t\t\tstart_dash_hold(d)
\t\treturn
'''
s, n = re.subn(r'func handle_press_portrait\(pos: Vector2\) -> void:\n.*?(?=\n\nfunc handle_village_touch_portrait)', handle.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'skin touch anchor failed: {n}')

tile_func = '''func draw_dungeon_tile(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int) -> void:
\tvar r := Rect2(p, Vector2(tile_size - 1, tile_size - 1))
\tif not seen:
\t\tdraw_rect(r, Color("#05070b"))
\t\treturn
\tvar seed := abs(x * 37 + y * 61)
\tif tile == "#":
\t\tvar wall := Color("#27313d") if seed % 3 else Color("#303b47")
\t\tdraw_rect(r, wall)
\t\tdraw_rect(Rect2(p + Vector2(2, 2), Vector2(tile_size - 5, tile_size - 5)), Color("#202833"))
\t\tdraw_line(p + Vector2(2, tile_size * 0.52), p + Vector2(tile_size - 3, tile_size * 0.52), Color("#3c4854"), 1.0)
\t\tif seed % 2 == 0:
\t\t\tdraw_line(p + Vector2(tile_size * 0.48, 3), p + Vector2(tile_size * 0.48, tile_size * 0.50), Color("#141a22"), 1.0)
\t\tif seed % 11 == 0:
\t\t\tvar lamp := p + Vector2(tile_size * 0.5, tile_size * 0.5)
\t\t\tdraw_circle(lamp, tile_size * 0.36, Color(1.0, 0.55, 0.18, 0.08))
\t\t\tdraw_circle(lamp, 3.2, Color("#ffb44a"))
\telif tile == ">":
\t\tdraw_rect(r, Color("#5b5040"))
\t\tdraw_rect(Rect2(p + Vector2(5, 5), Vector2(tile_size - 11, tile_size - 11)), Color("#1c2027"))
\t\tdraw_rect(Rect2(p + Vector2(10, 9), Vector2(tile_size - 21, tile_size - 18)), Color("#5f5361"))
\t\tdraw_rect(Rect2(p + Vector2(13, 11), Vector2(tile_size - 27, tile_size - 22)), Color("#11151a"))
\telse:
\t\tvar floor_col := Color("#6c5b46") if seed % 4 else Color("#75634b")
\t\tdraw_rect(r, floor_col)
\t\tdraw_rect(Rect2(p + Vector2(1, 1), Vector2(tile_size - 3, tile_size - 3)), floor_col.lightened(0.04))
\t\tif seed % 3 == 0:
\t\t\tdraw_line(p + Vector2(5, tile_size - 7), p + Vector2(tile_size - 6, tile_size - 7), Color("#4f4437"), 1.0)
\t\tif seed % 7 == 0:
\t\t\tdraw_line(p + Vector2(tile_size * 0.35, 5), p + Vector2(tile_size * 0.55, 12), Color("#504438"), 1.0)
'''
s, n = re.subn(r'func draw_dungeon_tile\(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int\) -> void:\n.*?(?=\n\nfunc draw_dungeon_portrait)', tile_func.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'skin tile anchor failed: {n}')

helpers = '''func enemy_sheet_index(kind: String, is_boss: bool) -> int:
\tif is_boss: return 5
\tif kind == "hound": return 1
\tif kind == "archer": return 2
\tif kind == "shadow": return 3
\tif kind == "elite": return 4
\treturn 0

func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tif enemy_sheet_texture == null:
\t\tdraw_entity_visual(center, "boss" if bool(enemy.get("boss", false)) else "enemy", "将" if bool(enemy.get("boss", false)) else "敵", 20, Color("#f08a7d"), tile_size)
\t\treturn
\tvar idx := enemy_sheet_index(str(enemy.get("kind", "samurai")), bool(enemy.get("boss", false)))
\tvar size := maxf(28.0, tile_size + 7.0)
\tvar dest := Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size))
\tdraw_texture_rect_region(enemy_sheet_texture, dest, Rect2(float(idx * 64), 0.0, 64.0, 64.0))

func item_sheet_index(name: String) -> int:
\tif name == "兵糧丸" or name == "大兵糧丸": return 1
\tif name.find("巻物") >= 0: return 2
\tif name == "手裏剣": return 3
\tif name == "クナイ": return 4
\treturn 0

func draw_item_reference_visual(center: Vector2, item: Dictionary, tile_size: float) -> void:
\tif item_sheet_texture == null:
\t\tdraw_entity_visual(center, "item", "物", 20, Color("#f0d45f"), tile_size)
\t\treturn
\tvar idx := item_sheet_index(str(item.get("name", "")))
\tvar size := maxf(25.0, tile_size - 2.0)
\tvar dest := Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size))
\tdraw_texture_rect_region(item_sheet_texture, dest, Rect2(float(idx * 64), 0.0, 64.0, 64.0))

func draw_reference_leaf(pos: Vector2, scale: float = 1.0) -> void:
\tvar c := Color("#9d2832")
\tdraw_colored_polygon(PackedVector2Array([pos + Vector2(0,-7)*scale, pos + Vector2(3,-2)*scale, pos + Vector2(8,-3)*scale, pos + Vector2(4,1)*scale, pos + Vector2(6,6)*scale, pos + Vector2(0,3)*scale, pos + Vector2(-5,7)*scale, pos + Vector2(-4,1)*scale, pos + Vector2(-8,-2)*scale, pos + Vector2(-3,-2)*scale]), c)
'''
anchor = '\n\nfunc draw_dungeon_portrait() -> void:\n'
if anchor not in s:
    raise SystemExit('skin helper insertion anchor failed')
s = s.replace(anchor, '\n\n' + helpers.rstrip() + anchor, 1)

draw = '''func draw_dungeon_portrait() -> void:
\tconst PTILE := 39
\tconst PMAP_X := 38
\tconst PMAP_Y := 206
\tconst VIEW_W := 15
\tconst VIEW_H := 11
\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#07101b"))
\tdraw_rect(Rect2(0, 0, 720, 104), Color("#0c1625"))
\tdraw_circle(Vector2(67, 46), 34.0, Color("#8d2630"))
\tdraw_ui_text(Vector2(24, 61), "忍道", HORIZONTAL_ALIGNMENT_LEFT, -1, 36, Color("#f2eee3"))
\tdraw_ui_text(Vector2(116, 56), "- SHINOBI ROGUE -", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#f2eee3"))
\tdraw_ui_text(Vector2(116, 82), "小さな一歩が、大きな物語になる。", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#d9cfae"))
\tdraw_ui_text(Vector2(626, 28), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#c9c2b1"))
\tdraw_reference_leaf(Vector2(520, 65), 0.7)
\tdraw_reference_leaf(Vector2(555, 40), 0.55)
\tdraw_panel(Rect2(12, 106, 696, 90), Color("#0c1521"), Color("#c79a4b"), 2.0)
\tdraw_panel(Rect2(22, 116, 88, 70), Color("#d8c39a"), Color("#b78a42"), 2.0)
\tdraw_ui_text(Vector2(44, 154), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color("#231d19"))
\tdraw_ui_text(Vector2(39, 177), "迷いの里", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#4b3524"))
\tdraw_ui_text(Vector2(128, 135), "HP  %d/%d" % [hp, max_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
\tdraw_meter(Vector2(128, 146), Vector2(150, 14), hp, max_hp, Color("#54c85b"))
\tdraw_ui_text(Vector2(308, 135), "満腹  %d" % hunger, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
\tdraw_meter(Vector2(308, 146), Vector2(150, 14), hunger, 100, Color("#2589e8"))
\tdraw_ui_text(Vector2(488, 135), "忍気  %d" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
\tdraw_meter(Vector2(488, 146), Vector2(150, 14), ninja_energy, 100, Color("#8c61e8"))
\tdraw_ui_text(Vector2(128, 181), "忍道:%s  ｜  銭 %d(+%d)  ｜  忍魂 %d(+%d)  ｜  T%d" % [style_name, coins, run_coins, souls, run_souls, turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#d9d4c8"))
\tdraw_panel(Rect2(14, 200, 692, 442), Color("#070a0e"), Color("#c79a4b"), 2.2)
\tvar origin := portrait_camera_origin()
\tif map_visible:
\t\tfor vy in range(VIEW_H):
\t\t\tfor vx in range(VIEW_W):
\t\t\t\tvar wx := origin.x + vx
\t\t\t\tvar wy := origin.y + vy
\t\t\t\tvar cell_pos := Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)
\t\t\t\tvar seen := validate_grid(explored) and bool(explored[wy][wx])
\t\t\t\tvar tile := str(map[wy][wx]) if validate_grid(map) else "#"
\t\t\t\tdraw_dungeon_tile(cell_pos, tile, seen, wx, wy, PTILE)
\tfor trap in placed_traps:
\t\tvar tp: Vector2i = trap
\t\tif portrait_cell_in_view(tp) and is_visible_cell(tp): draw_entity_visual(portrait_cell_center(tp), "trap", "罠", 20, Color("#e0a35c"), PTILE)
\tfor item in items:
\t\tvar ip: Vector2i = item["pos"]
\t\tif portrait_cell_in_view(ip) and is_visible_cell(ip): draw_item_reference_visual(portrait_cell_center(ip), item, PTILE)
\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep)
\t\t\tdraw_arc(ec + Vector2(0, 13), 15.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tdraw_enemy_reference_visual(ec, e, PTILE)
\tif shopkeeper.size() > 0:
\t\tvar sp: Vector2i = shopkeeper["pos"]
\t\tif portrait_cell_in_view(sp) and is_visible_cell(sp): draw_entity_visual(portrait_cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", "闇" if merchant_type == "闇商人" else "商", 20, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), PTILE)
\tif clone_active and portrait_cell_in_view(clone_pos) and is_visible_cell(clone_pos): draw_entity_visual(portrait_cell_center(clone_pos), "clone", "影", 20, Color("#91a9d6"), PTILE)
\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tdraw_arc(pc + Vector2(0, 13), 16.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(pc, PTILE)
\tif map_visible:
\t\tdraw_explored_minimap_portrait()
\tdraw_panel(Rect2(14, 652, 692, 104), Color("#0b1421"), Color("#c79a4b"), 2.0)
\tdraw_circle(Vector2(60, 704), 34.0, Color("#172438"))
\tdraw_arc(Vector2(60, 704), 34.0, 0.0, TAU, 40, Color("#d6a74f"), 2.0)
\tdraw_line(Vector2(47, 690), Vector2(47, 718), Color.WHITE, 3.0)
\tdraw_line(Vector2(60, 688), Vector2(60, 716), Color.WHITE, 3.0)
\tdraw_line(Vector2(73, 690), Vector2(73, 718), Color.WHITE, 3.0)
\tdraw_ui_text(Vector2(110, 688), message.left(42), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar hunger_note := "【空腹注意】" if hunger <= 20 else ""
\tdraw_ui_text(Vector2(110, 723), "装備:%s / %s  %s" % [WEAPON_NAME, ARMOR_NAME, hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#b7c0cc"))
\tif unpaid_items.size() > 0:
\t\tdraw_ui_text(Vector2(480, 723), "未精算 %d点/%d銭" % [unpaid_items.size(), shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ff9a7a"))
\tdraw_mobile_controls_portrait()
\tif inventory_menu:
\t\tdraw_inventory_overlay(true)
\telif checkout_prompt or stairs_prompt or ad_menu:
\t\tdraw_modal_overlay_portrait()
'''
s, n = re.subn(r'func draw_dungeon_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_mobile_controls_portrait)', draw.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'skin dungeon draw anchor failed: {n}')

controls = '''func draw_mobile_controls_portrait() -> void:
\tdraw_rect(Rect2(0, 760, 720, 340), Color("#07101b"))
\tdraw_reference_leaf(Vector2(35, 1050), 0.75)
\tdraw_reference_leaf(Vector2(330, 1028), 0.55)
\tdraw_reference_leaf(Vector2(685, 1010), 0.65)
\tvar diamond_controls = [
\t\t["道具", Vector2(170, 818)],
\t\t["罠", Vector2(100, 888)],
\t\t["飛", Vector2(240, 888)],
\t\t["中断", Vector2(170, 958)]
\t]
\tfor d_control in diamond_controls:
\t\tvar c: Vector2 = d_control[1]
\t\tdraw_circle(c, 45.0, Color("#172438"))
\t\tdraw_arc(c, 45.0, 0.0, TAU, 48, Color("#d6a74f"), 2.5)
\t\tvar label := str(d_control[0])
\t\tdraw_ui_text(c + Vector2(-25 if label.length() > 1 else -9, 7), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar base := Vector2(382, 772)
\tvar cell := 98.0
\tvar labels = [["↖", "↑", "↗"], ["←", "隠", "→"], ["↙", "↓", "↘"]]
\tfor y in range(3):
\t\tfor x in range(3):
\t\t\tvar r := Rect2(base.x + x * cell, base.y + y * cell, cell - 7, cell - 7)
\t\t\tvar center := x == 1 and y == 1
\t\t\tif center:
\t\t\t\tvar cc := r.get_center()
\t\t\t\tdraw_circle(cc, 44.0, Color("#1b2a3c"))
\t\t\t\tdraw_arc(cc, 44.0, 0.0, TAU, 48, Color("#d6a74f"), 2.5)
\t\t\t\tdraw_circle(cc, 31.0, Color(0.25, 0.34, 0.44, 0.28))
\t\t\t\tdraw_ui_text(cc + Vector2(-10, 8), "隠", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color("#f1c95b"))
\t\t\telse:
\t\t\t\tdraw_panel(r, Color("#1a293b"), Color("#d2a455"), 2.0)
\t\t\t\tdraw_ui_text(r.position + Vector2(30, 58), labels[y][x], HORIZONTAL_ALIGNMENT_LEFT, -1, 27, Color.WHITE)
\tdraw_ui_text(Vector2(420, 1082), "出会い、拾い、伏せ、進む。それが、忍の道。", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#d6a74f"))
'''
s, n = re.subn(r'func draw_mobile_controls_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_modal_overlay_portrait)', controls.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'skin controls anchor failed: {n}')

required = ['REFERENCE_GAMEPLAY_SKIN_PATCH_APPLIED','enemy_sheet_texture','item_sheet_texture','draw_enemy_reference_visual','draw_item_reference_visual','const PTILE := 39','start_dash_hold(d)','出会い、拾い、伏せ、進む。それが、忍の道。']
for needle in required:
    if needle not in s:
        raise SystemExit(f'skin verification failed: {needle}')
if s == original:
    raise SystemExit('skin patch made no changes')
p.write_text(s, encoding='utf-8')
print('REFERENCE_GAMEPLAY_SKIN_PATCH PASS')
