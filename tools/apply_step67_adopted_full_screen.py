from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP67_ADOPTED_FULL_SCREEN_APPLIED' in s:
    print('STEP67_ADOPTED_FULL_SCREEN PASS (already applied)')
    raise SystemExit(0)

helpers = r'''func draw_step67_corner(pos: Vector2, sx: float, sy: float) -> void: # STEP67_ADOPTED_FULL_SCREEN_APPLIED
	var gold := Color("#d5a34c")
	draw_line(pos, pos + Vector2(18.0 * sx, 0), gold, 2.0)
	draw_line(pos, pos + Vector2(0, 18.0 * sy), gold, 2.0)
	draw_line(pos + Vector2(5.0 * sx, 5.0 * sy), pos + Vector2(13.0 * sx, 5.0 * sy), gold.darkened(0.12), 1.5)
	draw_line(pos + Vector2(5.0 * sx, 5.0 * sy), pos + Vector2(5.0 * sx, 13.0 * sy), gold.darkened(0.12), 1.5)

func draw_step67_frame(r: Rect2, fill: Color, width: float = 2.0) -> void:
	draw_rect(r, fill)
	draw_rect(r, Color("#c89a49"), false, width)
	draw_step67_corner(r.position + Vector2(3,3), 1.0, 1.0)
	draw_step67_corner(Vector2(r.end.x - 3, r.position.y + 3), -1.0, 1.0)
	draw_step67_corner(Vector2(r.position.x + 3, r.end.y - 3), 1.0, -1.0)
	draw_step67_corner(r.end - Vector2(3,3), -1.0, -1.0)

func draw_step67_header_scene() -> void:
	draw_circle(Vector2(575, 46), 31.0, Color(1.0, 0.82, 0.48, 0.16))
	draw_circle(Vector2(575, 46), 24.0, Color("#f1d08a"))
	draw_colored_polygon(PackedVector2Array([Vector2(445,93),Vector2(485,58),Vector2(520,92),Vector2(557,65),Vector2(606,93)]), Color("#111827"))
	var pagoda := Color("#090d14")
	draw_rect(Rect2(610,42,7,51), pagoda)
	for i in range(3):
		var yy := 50.0 + i * 14.0
		var half := 24.0 - i * 4.0
		draw_colored_polygon(PackedVector2Array([Vector2(613.5-half,yy),Vector2(613.5+half,yy),Vector2(613.5+half-6,yy+5),Vector2(613.5-half+6,yy+5)]), pagoda)
	for leaf in [Vector2(500,26),Vector2(535,76),Vector2(668,40),Vector2(691,78)]:
		draw_reference_leaf(leaf, 0.55)

func draw_step67_command_icon(label: String, c: Vector2) -> void:
	var ink := Color("#f4f1e8")
	if label == "道具":
		draw_circle(c + Vector2(0,-5), 12.0, ink)
		draw_line(c + Vector2(-7,-18), c + Vector2(7,-18), ink, 3.0)
		draw_line(c + Vector2(-5,-21), c + Vector2(0,-16), ink, 2.0)
		draw_line(c + Vector2(5,-21), c + Vector2(0,-16), ink, 2.0)
	elif label == "罠":
		draw_arc(c + Vector2(0,-4), 13.0, PI, TAU, 20, ink, 3.0)
		for dx in [-10.0,-5.0,0.0,5.0,10.0]:
			draw_line(c + Vector2(dx,-5), c + Vector2(dx*0.75,-16), ink, 2.0)
		draw_circle(c + Vector2(0,-2), 3.0, ink)
	elif label == "飛":
		for a in range(4):
			var ang := float(a) * PI * 0.5
			var tip := c + Vector2(cos(ang), sin(ang)) * 17.0 + Vector2(0,-5)
			var left := c + Vector2(cos(ang+0.55), sin(ang+0.55)) * 6.0 + Vector2(0,-5)
			var right := c + Vector2(cos(ang-0.55), sin(ang-0.55)) * 6.0 + Vector2(0,-5)
			draw_colored_polygon(PackedVector2Array([c+Vector2(0,-5), left, tip, right]), ink)
		draw_circle(c + Vector2(0,-5), 4.0, Color("#172438"))
	elif label == "中断":
		draw_rect(Rect2(c + Vector2(-13,-18), Vector2(25,27)), ink, false, 3.0)
		draw_line(c + Vector2(-8,-12), c + Vector2(7,-12), ink, 2.0)
		draw_line(c + Vector2(-8,-5), c + Vector2(7,-5), ink, 2.0)
		draw_line(c + Vector2(-8,2), c + Vector2(3,2), ink, 2.0)
	elif label == "術":
		draw_circle(c + Vector2(-8,-8), 8.0, Color(0.72,0.78,0.86,0.25))
		draw_circle(c + Vector2(6,-12), 10.0, Color(0.72,0.78,0.86,0.20))
		draw_circle(c + Vector2(11,-2), 7.0, Color(0.72,0.78,0.86,0.17))

func draw_step67_message_icon(c: Vector2) -> void:
	var paper := Color("#f0eee7")
	draw_colored_polygon(PackedVector2Array([c+Vector2(-19,-15),c+Vector2(-3,-11),c+Vector2(-3,16),c+Vector2(-19,11)]), paper)
	draw_colored_polygon(PackedVector2Array([c+Vector2(3,-11),c+Vector2(19,-15),c+Vector2(19,11),c+Vector2(3,16)]), paper)
	draw_line(c + Vector2(0,-12), c + Vector2(0,16), Color("#788391"), 2.0)
'''

anchor = '\n\nfunc draw_dungeon_portrait() -> void:\n'
if anchor not in s:
    raise SystemExit('STEP67 helper anchor failed')
s = s.replace(anchor, '\n\n' + helpers.rstrip() + anchor, 1)

center_func = '''func portrait_cell_center(p: Vector2i) -> Vector2:
	const PTILE := 40
	const PMAP_X := 44
	const PMAP_Y := 204
	var origin := portrait_camera_origin()
	var local := p - origin
	return Vector2(PMAP_X + local.x * PTILE + PTILE * 0.5, PMAP_Y + local.y * PTILE + PTILE * 0.5)'''
s, n = re.subn(r'func portrait_cell_center\(p: Vector2i\) -> Vector2:\n.*?(?=\n\nfunc handle_press_portrait)', center_func, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP67 portrait center replacement failed: {n}')

draw = r'''func draw_dungeon_portrait() -> void:
	const PTILE := 40
	const PMAP_X := 44
	const PMAP_Y := 204
	const VIEW_W := 15
	const VIEW_H := 11
	draw_rect(Rect2(0,0,720,1100), Color("#06101c"))
	draw_rect(Rect2(0,0,720,104), Color("#0a1422"))
	draw_step67_header_scene()
	draw_circle(Vector2(67,48), 38.0, Color("#9a2831"))
	draw_ui_text(Vector2(22,65), "忍道", HORIZONTAL_ALIGNMENT_LEFT, -1, 39, Color("#f5f0e5"))
	draw_ui_text(Vector2(118,54), "- SHINOBI ROGUE -", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#f5f0e5"))
	draw_ui_text(Vector2(118,82), "小さな一歩が、大きな物語になる。", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#d9caa8"))
	draw_ui_text(Vector2(632,24), "Ver.%s" % VERSION, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#ded7c9"))
	draw_step67_frame(Rect2(12,106,696,88), Color("#0a1421"), 2.2)
	draw_rect(Rect2(22,116,92,68), Color("#d8c49c"))
	draw_rect(Rect2(22,116,92,68), Color("#b88a42"), false, 2.0)
	draw_ui_text(Vector2(46,153), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color("#241d18"))
	draw_ui_text(Vector2(38,177), "迷いの里", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#4b3524"))
	draw_ui_text(Vector2(132,135), "HP  %d/%d" % [hp,max_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
	draw_meter(Vector2(132,146), Vector2(146,14), hp, max_hp, Color("#55c85b"))
	draw_ui_text(Vector2(310,135), "満腹  %d" % hunger, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
	draw_meter(Vector2(310,146), Vector2(146,14), hunger, 100, Color("#2389e8"))
	draw_ui_text(Vector2(488,135), "忍気  %d" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
	draw_meter(Vector2(488,146), Vector2(146,14), ninja_energy, 100, Color("#8a61e8"))
	draw_ui_text(Vector2(132,180), "✦ 忍道:%s  ｜  銭 %d(+%d)  ｜  忍魂 %d(+%d)  ｜  T%d" % [style_name,coins,run_coins,souls,run_souls,turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ddd5c5"))
	draw_step67_frame(Rect2(12,198,696,450), Color("#04070b"), 2.2)
	var origin := portrait_camera_origin()
	if map_visible:
		for vy in range(VIEW_H):
			for vx in range(VIEW_W):
				var wx := origin.x + vx
				var wy := origin.y + vy
				var cell_pos := Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)
				var seen := validate_grid(explored) and bool(explored[wy][wx])
				var tile := str(map[wy][wx]) if validate_grid(map) else "#"
				draw_dungeon_tile(cell_pos, tile, seen, wx, wy, PTILE)
	for trap in placed_traps:
		var tp: Vector2i = trap
		if portrait_cell_in_view(tp) and is_visible_cell(tp): draw_entity_visual(portrait_cell_center(tp), "trap", "罠", 20, Color("#e0a35c"), PTILE)
	for item in items:
		var ip: Vector2i = item["pos"]
		if portrait_cell_in_view(ip) and is_visible_cell(ip): draw_item_reference_visual(portrait_cell_center(ip), item, PTILE + 5.0)
	for e in enemies:
		var ep: Vector2i = e["pos"]
		if portrait_cell_in_view(ep) and is_visible_cell(ep):
			var ec := portrait_cell_center(ep)
			draw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
			draw_enemy_reference_visual(ec, e, PTILE + 10.0)
	if shopkeeper.size() > 0:
		var sp: Vector2i = shopkeeper["pos"]
		if portrait_cell_in_view(sp) and is_visible_cell(sp): draw_entity_visual(portrait_cell_center(sp), "dark_merchant" if merchant_type == "闇商人" else "merchant", "闇" if merchant_type == "闇商人" else "商", 20, Color("#c59cff") if merchant_type == "闇商人" else Color("#8ad5a2"), PTILE + 8.0)
	if clone_active and portrait_cell_in_view(clone_pos) and is_visible_cell(clone_pos): draw_entity_visual(portrait_cell_center(clone_pos), "clone", "影", 20, Color("#91a9d6"), PTILE + 8.0)
	if portrait_cell_in_view(player):
		var pc := portrait_cell_center(player)
		draw_arc(pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
		draw_player_facing_visual(pc, PTILE + 13.0)
	if map_visible:
		draw_explored_minimap_portrait()
	draw_step67_frame(Rect2(12,654,696,102), Color("#081321"), 2.2)
	draw_circle(Vector2(60,705), 35.0, Color("#17263a"))
	draw_arc(Vector2(60,705), 35.0, 0.0, TAU, 48, Color("#d6a74f"), 2.4)
	draw_step67_message_icon(Vector2(60,705))
	draw_ui_text(Vector2(112,690), message.left(46), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#f4f1e9"))
	var hunger_note := "【空腹注意】" if hunger <= 20 else ""
	draw_ui_text(Vector2(112,724), "装備:%s / %s  %s" % [WEAPON_NAME,ARMOR_NAME,hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#b7c0cc"))
	if unpaid_items.size() > 0:
		draw_ui_text(Vector2(470,724), "未精算 %d点/%d銭" % [unpaid_items.size(),shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ff9a7a"))
	draw_mobile_controls_portrait()
	if inventory_menu:
		draw_inventory_overlay(true)
	elif checkout_prompt or stairs_prompt or ad_menu:
		draw_modal_overlay_portrait()
'''
s, n = re.subn(r'func draw_dungeon_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_mobile_controls_portrait)', draw.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP67 dungeon replacement failed: {n}')

controls = r'''func draw_mobile_controls_portrait() -> void:
	draw_rect(Rect2(0,760,720,340), Color("#06101c"))
	draw_colored_polygon(PackedVector2Array([Vector2(0,1098),Vector2(0,1018),Vector2(70,978),Vector2(126,1024),Vector2(205,966),Vector2(285,1035),Vector2(360,990),Vector2(430,1045),Vector2(520,978),Vector2(610,1030),Vector2(720,970),Vector2(720,1100)]), Color("#0b1b2c"))
	for leaf in [Vector2(36,1044),Vector2(334,1030),Vector2(675,1008),Vector2(698,930)]: draw_reference_leaf(leaf,0.65)
	var command_buttons = [
		["道具", Vector2(170,812), 42.0],
		["罠", Vector2(82,895), 42.0],
		["術", Vector2(170,895), 36.0],
		["飛", Vector2(258,895), 42.0],
		["中断", Vector2(170,978), 42.0]
	]
	var gold := Color("#d6a74f")
	draw_line(Vector2(170,854),Vector2(124,882),Color(0.84,0.65,0.31,0.24),2.0)
	draw_line(Vector2(170,854),Vector2(216,882),Color(0.84,0.65,0.31,0.24),2.0)
	draw_line(Vector2(124,908),Vector2(170,936),Color(0.84,0.65,0.31,0.24),2.0)
	draw_line(Vector2(216,908),Vector2(170,936),Color(0.84,0.65,0.31,0.24),2.0)
	for button in command_buttons:
		var label := str(button[0])
		var c: Vector2 = button[1]
		var radius: float = float(button[2])
		draw_circle(c + Vector2(0,4), radius + 2.0, Color(0,0,0,0.28))
		draw_circle(c, radius, Color("#14243a"))
		draw_arc(c, radius, 0.0, TAU, 52, gold, 2.6)
		draw_step67_command_icon(label,c)
		if label == "術":
			draw_ui_text(c + Vector2(-10,11), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#f1c95b"))
		else:
			draw_ui_text(c + Vector2(-24 if label.length()>1 else -9,31), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#f4f1e8"))
	var base := Vector2(390,770)
	var cell := 96.0
	var labels = [["↖","↑","↗"],["←","","→"],["↙","↓","↘"]]
	for y in range(3):
		for x in range(3):
			var r := Rect2(base.x + x*cell, base.y + y*cell, 88.0, 88.0)
			var center := x == 1 and y == 1
			if center:
				var cc := r.get_center()
				draw_circle(cc + Vector2(0,4), 41.0, Color(0,0,0,0.30))
				draw_circle(cc, 39.0, Color("#17283e"))
				draw_arc(cc,39.0,0.0,TAU,52,gold,2.7)
				if direction_only_mode:
					draw_circle(cc,19.0,Color("#f4f5f2"))
					draw_arc(cc,22.0,0.0,TAU,40,Color("#9eabb8"),2.0)
				else:
					draw_arc(cc,19.0,0.0,TAU,40,Color("#f4f5f2"),3.0)
			else:
				draw_rect(r, Color("#192b41"))
				draw_rect(r, gold, false, 2.5)
				draw_line(r.position+Vector2(4,4),r.position+Vector2(13,4),gold.lightened(0.12),1.5)
				draw_line(r.position+Vector2(4,4),r.position+Vector2(4,13),gold.lightened(0.12),1.5)
				draw_ui_text(r.position+Vector2(29,57),labels[y][x],HORIZONTAL_ALIGNMENT_LEFT,-1,28,Color("#f4f1e8"))
'''
s, n = re.subn(r'func draw_mobile_controls_portrait\(\) -> void:\n.*?(?=\n\nfunc draw_modal_overlay_portrait)', controls.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP67 controls replacement failed: {n}')

required = ['STEP67_ADOPTED_FULL_SCREEN_APPLIED','func draw_step67_message_icon','func draw_step67_command_icon','const PTILE := 40','["術", Vector2(170,895), 36.0]','if direction_only_mode:','draw_step67_frame(Rect2(12,654,696,102)']
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP67 verification failed: {needle}')
if '出会い、拾い、伏せ、進む' in s:
    raise SystemExit('STEP67 obsolete tagline remains')
if s == original:
    raise SystemExit('STEP67 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP67_ADOPTED_FULL_SCREEN PASS')
