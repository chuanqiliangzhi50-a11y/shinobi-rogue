from pathlib import Path
import re, sys

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

# Align entity art with the actual portrait dungeon origin.
s = re.sub(
    r'(func portrait_cell_center\(p: Vector2i\) -> Vector2:\n\tconst PTILE := 21\n\tconst PMAP_X := 34\n\tconst PMAP_Y := )\d+',
    r'\g<1>154', s, count=1)

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

\t# Adopted portrait UI: round map toggle + four-command diamond + 8-way pad.
\tif Rect2(28, 638, 92, 92).has_point(pos):
\t\ttoggle_map_visibility()
\t\treturn

\tvar diamond_actions = [
\t\t[Rect2(174, 756, 92, 92), "inventory"],
\t\t[Rect2(104, 826, 92, 92), "trap"],
\t\t[Rect2(244, 826, 92, 92), "throw"],
\t\t[Rect2(174, 896, 92, 92), "suspend"]
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

\tvar base := Vector2(410, 758)
\tvar cell := 88.0
\tif pos.x >= base.x and pos.x < base.x + cell * 3.0 and pos.y >= base.y and pos.y < base.y + cell * 3.0:
\t\tvar cx := int((pos.x - base.x) / cell)
\t\tvar cy := int((pos.y - base.y) / cell)
\t\tvar d := Vector2i(cx - 1, cy - 1)
\t\tif d == Vector2i.ZERO:
\t\t\thide_one_turn()
\t\telse:
\t\t\ttry_move(d)
\t\treturn
'''
s, n1 = re.subn(r'func handle_press_portrait\(pos: Vector2\) -> void:\n.*?(?=\n\nfunc handle_village_touch_portrait)', handle, s, count=1, flags=re.S)

draw = '''func draw_dungeon_portrait() -> void:
\tconst PTILE := 21
\tconst PMAP_X := 34
\tconst PMAP_Y := 154
\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#080c11"))
\tdraw_rect(Rect2(0, 0, 720, 128), Color("#101822"))
\tdraw_rect(Rect2(0, 126, 720, 2), Color("#8d7740"))
\tdraw_ui_text(Vector2(20, 34), "忍道 - SHINOBI ROGUE", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#e8d47f"))
\tdraw_ui_text(Vector2(535, 33), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#7f8b98"))
\tdraw_ui_text(Vector2(20, 66), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\tdraw_ui_text(Vector2(72, 66), "HP %d/%d" % [hp, max_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
\tdraw_meter(Vector2(178, 53), Vector2(120, 13), hp, max_hp, Color("#67b96f"))
\tdraw_ui_text(Vector2(320, 66), "満腹 %d" % hunger, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
\tdraw_meter(Vector2(430, 53), Vector2(90, 13), hunger, 100, Color("#5f8fe8"))
\tdraw_ui_text(Vector2(540, 66), "忍気 %d" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color("#e7ebef"))
\tdraw_ui_text(Vector2(20, 102), "忍道:%s   銭 %d(+%d)   忍魂 %d(+%d)   T%d" % [style_name, coins, run_coins, souls, run_souls, turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#aeb7c2"))

\t# Enlarged dungeon panel; old command grid is intentionally removed.
\tdraw_panel(Rect2(20, 140, 680, 482), Color("#0b0f14"), Color("#8d7740"), 2.0)
\tif map_visible:
\t\tfor y in range(MAP_H):
\t\t\tfor x in range(MAP_W):
\t\t\t\tvar p := Vector2(PMAP_X + x * PTILE, PMAP_Y + y * PTILE)
\t\t\t\tvar seen := validate_grid(explored) and bool(explored[y][x])
\t\t\t\tvar tile := str(map[y][x]) if validate_grid(map) else "#"
\t\t\t\tdraw_dungeon_tile(p, tile, seen, x, y, PTILE)
\tfor trap in placed_traps:
\t\tvar tp: Vector2i = trap
\t\tif is_visible_cell(tp): draw_entity_visual(portrait_cell_center(tp), "trap", "罠", 14, Color("#e0a35c"), PTILE)
\tfor item in items:
\t\tvar ip: Vector2i = item["pos"]
\t\tif is_visible_cell(ip): draw_entity_visual(portrait_cell_center(ip), "item", "物", 14, Color("#f0d45f"), PTILE)
\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif is_visible_cell(ep): draw_entity_visual(portrait_cell_center(ep), "boss" if bool(e["boss"]) else "enemy", "将" if bool(e["boss"]) else "敵", 14, Color("#f08a7d"), PTILE)
\tif shopkeeper.size() > 0:
\t\tvar sp: Vector2i = shopkeeper["pos"]
\t\tif is_visible_cell(sp): draw_entity_visual(portrait_cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", "闇" if merchant_type == "闇商人" else "商", 14, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), PTILE)
\tif clone_active and is_visible_cell(clone_pos): draw_entity_visual(portrait_cell_center(clone_pos), "clone", "影", 14, Color("#91a9d6"), PTILE)
\tdraw_entity_visual(portrait_cell_center(player), "player", "忍", 15, Color("#ffffff"), PTILE)

\t# Message window and round map toggle from the adopted mockup.
\tdraw_panel(Rect2(20, 634, 680, 108), Color("#111820"), Color("#8d7740"), 1.5)
\tdraw_circle(Vector2(74, 688), 43.0, Color("#1b2632"))
\tdraw_arc(Vector2(74, 688), 43.0, 0.0, TAU, 48, Color("#d7bf66"), 2.0)
\tdraw_ui_text(Vector2(48, 696), "地図", HORIZONTAL_ALIGNMENT_LEFT, -1, 15, Color.WHITE)
\tdraw_ui_text(Vector2(132, 671), message.left(38), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#e8d47f"))
\tvar hunger_note := "【空腹注意】" if hunger <= 20 else ""
\tdraw_ui_text(Vector2(132, 710), "装備: %s / %s   %s" % [WEAPON_NAME, ARMOR_NAME, hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color("#aeb7c2"))

\tdraw_mobile_controls_portrait()
\tif inventory_menu:
\t\tdraw_inventory_overlay(true)
\telif checkout_prompt or stairs_prompt or ad_menu:
\t\tdraw_modal_overlay_portrait()
'''
s, n2 = re.subn(r'func draw_dungeon_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_mobile_controls_portrait)', draw, s, count=1, flags=re.S)

controls = '''func draw_mobile_controls_portrait() -> void:
\tvar diamond_controls = [
\t\t["道具", Vector2(220, 802)],
\t\t["罠", Vector2(150, 872)],
\t\t["飛", Vector2(290, 872)],
\t\t["中断", Vector2(220, 942)]
\t]
\tfor d_control in diamond_controls:
\t\tvar c: Vector2 = d_control[1]
\t\tdraw_circle(c, 43.0, Color("#202934"))
\t\tdraw_arc(c, 43.0, 0.0, TAU, 48, Color("#d7bf66"), 2.0)
\t\tdraw_ui_text(c + Vector2(-25, 7), str(d_control[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)

\tvar base := Vector2(410, 758)
\tvar cell := 88.0
\tvar labels = [["↖", "↑", "↗"], ["←", "隠", "→"], ["↙", "↓", "↘"]]
\tfor y in range(3):
\t\tfor x in range(3):
\t\t\tvar r := Rect2(base.x + x * cell, base.y + y * cell, cell - 6, cell - 6)
\t\t\tvar center := x == 1 and y == 1
\t\t\tdraw_panel(r, Color("#29333f") if center else Color("#202934"), Color("#d7bf66") if center else Color("#596675"), 1.8)
\t\t\tdraw_ui_text(r.position + Vector2(28 if not center else 24, 52), labels[y][x], HORIZONTAL_ALIGNMENT_LEFT, -1, 22 if not center else 19, Color("#e8d47f") if center else Color.WHITE)

\tdraw_ui_text(Vector2(118, 1035), "道具・罠・飛・中断", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#8995a3"))
\tdraw_ui_text(Vector2(445, 1035), "8方向移動 / 中央:隠", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#8995a3"))
'''
s, n3 = re.subn(r'func draw_mobile_controls_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_modal_overlay_portrait)', controls, s, count=1, flags=re.S)

if (n1, n2, n3) != (1, 1, 1):
    raise SystemExit(f'patch anchors failed: handle={n1}, draw={n2}, controls={n3}')
if s == original:
    raise SystemExit('no changes made')

p.write_text(s, encoding='utf-8')
print('FINAL_PORTRAIT_UI_PATCH PASS')
