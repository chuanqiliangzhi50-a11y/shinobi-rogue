from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP68_ADOPTED_DUNGEON_UI_REFINEMENT_APPLIED' in s:
    print('STEP68_ADOPTED_DUNGEON_UI_REFINEMENT PASS (already applied)')
    raise SystemExit(0)

tile_func = r'''func draw_dungeon_tile(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int) -> void: # STEP68_ADOPTED_DUNGEON_UI_REFINEMENT_APPLIED
	var r := Rect2(p, Vector2(tile_size, tile_size))
	if not seen:
		draw_rect(r, Color("#020407"))
		return
	var seed := dungeon_visual_hash(x, y)
	if tile == "#":
		# Continuous blue-gray masonry. No per-game-cell outline: the stone seams
		# are smaller than the movement grid so the dungeon reads like a room.
		var base := Color("#252f3b") if seed % 3 else Color("#2b3643")
		draw_rect(r, base)
		var mortar := Color("#121922")
		var hi := Color("#44515e")
		for yy in [12.0, 25.0]:
			draw_line(p + Vector2(0,yy), p + Vector2(tile_size,yy), mortar, 2.0)
		var off1 := 10.0 + float(seed % 12)
		var off2 := 24.0 + float(seed % 8)
		draw_line(p + Vector2(off1,0), p + Vector2(off1,12), mortar, 1.5)
		draw_line(p + Vector2(off2,12), p + Vector2(off2,25), mortar, 1.5)
		draw_line(p + Vector2(tile_size-off1,25), p + Vector2(tile_size-off1,tile_size), mortar, 1.5)
		draw_line(p + Vector2(1,2), p + Vector2(tile_size-1,2), hi, 1.0)
		# A thick front face beside walkable space gives the wall depth visible
		# in the adopted illustration.
		if dungeon_walkable_neighbor(x,y,0,1):
			draw_rect(Rect2(p + Vector2(0,tile_size-9), Vector2(tile_size,9)), Color("#111820"))
			draw_line(p + Vector2(0,tile_size-9), p + Vector2(tile_size,tile_size-9), Color("#56616c"), 1.5)
		elif dungeon_walkable_neighbor(x,y,1,0):
			draw_rect(Rect2(p + Vector2(tile_size-7,0), Vector2(7,tile_size)), Color("#151d26"))
		elif dungeon_walkable_neighbor(x,y,-1,0):
			draw_rect(Rect2(p, Vector2(7,tile_size)), Color("#151d26"))
		var faces_floor := dungeon_walkable_neighbor(x,y,0,1) or dungeon_walkable_neighbor(x,y,1,0) or dungeon_walkable_neighbor(x,y,-1,0)
		if faces_floor:
			draw_dungeon_wall_prop(p, tile_size, seed)
	elif tile == ">":
		# Framed stairwell matching the heavy stone stair opening in the reference.
		draw_rect(r, Color("#75664f"))
		draw_rect(Rect2(p + Vector2(2,2), Vector2(tile_size-4,tile_size-4)), Color("#a18d6a"), false, 2.0)
		draw_rect(Rect2(p + Vector2(7,6), Vector2(tile_size-14,tile_size-12)), Color("#171a20"))
		for i in range(4):
			var sy := 9.0 + float(i) * 6.0
			var inset := 9.0 + float(i) * 2.0
			draw_rect(Rect2(p + Vector2(inset,sy), Vector2(maxf(4.0,tile_size-inset*2.0),4.0)), Color("#706778"))
		draw_rect(Rect2(p + Vector2(5,4), Vector2(tile_size-10,tile_size-8)), Color("#d1bd8d"), false, 1.5)
	else:
		# Continuous irregular paving. Movement cells are deliberately hidden:
		# each logical tile is split into smaller offset stones.
		var palette := [Color("#746650"),Color("#7d6d55"),Color("#6e624f"),Color("#85735a")]
		var floor_col: Color = palette[seed % palette.size()]
		draw_rect(r, floor_col)
		var seam := Color("#4a4034")
		var ymid := 18.0 + float(seed % 5)
		draw_line(p + Vector2(0,ymid), p + Vector2(tile_size,ymid), seam, 1.4)
		var top_x := 12.0 + float((seed / 7) % 15)
		var bot_x := 9.0 + float((seed / 11) % 18)
		draw_line(p + Vector2(top_x,0), p + Vector2(top_x,ymid), seam, 1.2)
		draw_line(p + Vector2(bot_x,ymid), p + Vector2(bot_x,tile_size), seam, 1.2)
		draw_line(p + Vector2(1,1), p + Vector2(tile_size-1,1), floor_col.lightened(0.09), 1.0)
		# Wall-contact shadows visually sink the floor into the room.
		if dungeon_walkable_neighbor(x,y,0,-1) == false:
			draw_rect(Rect2(p,Vector2(tile_size,5)),Color(0.02,0.03,0.04,0.24))
		if dungeon_walkable_neighbor(x,y,-1,0) == false:
			draw_rect(Rect2(p,Vector2(5,tile_size)),Color(0.02,0.03,0.04,0.16))
		if seed % 5 == 0:
			draw_line(p+Vector2(8,10),p+Vector2(14,14),Color("#4d4337"),1.0)
			draw_line(p+Vector2(14,14),p+Vector2(11,19),Color("#4d4337"),1.0)
		if seed % 9 == 0:
			draw_circle(p+Vector2(tile_size*0.72,tile_size*0.66),2.6,Color(0.20,0.18,0.15,0.20))
'''
s, n = re.subn(r'func draw_dungeon_tile\(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int\) -> void:\n.*?(?=\n\nfunc enemy_sheet_index)', tile_func.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP68 tile replacement failed: {n}')

# Message area: the adopted design has a taller framed log with a large icon,
# primary message, status line and a small gameplay hint.
old = '''	draw_step67_frame(Rect2(12,654,696,102), Color("#081321"), 2.2)
	draw_circle(Vector2(60,705), 35.0, Color("#17263a"))
	draw_arc(Vector2(60,705), 35.0, 0.0, TAU, 48, Color("#d6a74f"), 2.4)
	draw_step67_message_icon(Vector2(60,705))
	draw_ui_text(Vector2(112,690), message.left(46), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#f4f1e9"))
	var hunger_note := "【空腹注意】" if hunger <= 20 else ""
	draw_ui_text(Vector2(112,724), "装備:%s / %s  %s" % [WEAPON_NAME,ARMOR_NAME,hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#b7c0cc"))
	if unpaid_items.size() > 0:
		draw_ui_text(Vector2(470,724), "未精算 %d点/%d銭" % [unpaid_items.size(),shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ff9a7a"))
	draw_mobile_controls_portrait()'''
new = '''	draw_step67_frame(Rect2(12,640,696,120), Color("#081321"), 2.2)
	draw_circle(Vector2(62,699), 39.0, Color("#17263a"))
	draw_arc(Vector2(62,699), 39.0, 0.0, TAU, 48, Color("#d6a74f"), 2.6)
	draw_step67_message_icon(Vector2(62,699))
	draw_ui_text(Vector2(116,680), message.left(48), HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("#f4f1e9"))
	var hunger_note := "【空腹注意】" if hunger <= 20 else ""
	draw_ui_text(Vector2(116,714), "装備:%s / %s  %s" % [WEAPON_NAME,ARMOR_NAME,hunger_note], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#c6cbd2"))
	draw_ui_text(Vector2(116,744), "○長押し:足踏み回復　●:向き変更　長押し移動:駆ける", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#8f9aa8"))
	if unpaid_items.size() > 0:
		draw_ui_text(Vector2(490,714), "未精算 %d点/%d銭" % [unpaid_items.size(),shop_total_unpaid()], HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#ff9a7a"))
	draw_mobile_controls_portrait()'''
if old not in s:
    raise SystemExit('STEP68 message window anchor failed')
s = s.replace(old, new, 1)

# Stronger, more tactile controls while preserving the STEP64/65 hit areas.
s = s.replace('draw_circle(c, radius, Color("#14243a"))\n\t\tdraw_arc(c, radius, 0.0, TAU, 52, gold, 2.6)',
              'draw_circle(c, radius + 3.0, Color("#101b2a"))\n\t\tdraw_circle(c, radius, Color("#1b2d45"))\n\t\tdraw_arc(c, radius + 2.0, 0.0, TAU, 52, Color("#8d6631"), 1.5)\n\t\tdraw_arc(c, radius, 0.0, TAU, 52, gold, 2.8)', 1)
s = s.replace('draw_rect(r, Color("#192b41"))\n\t\t\t\tdraw_rect(r, gold, false, 2.5)',
              'draw_rect(r, Color("#101a29"))\n\t\t\t\tdraw_rect(r.grow(-3.0), Color("#20344e"))\n\t\t\t\tdraw_rect(r, Color("#8d6631"), false, 1.2)\n\t\t\t\tdraw_rect(r.grow(-2.0), gold, false, 2.2)', 1)

required = [
    'STEP68_ADOPTED_DUNGEON_UI_REFINEMENT_APPLIED',
    'Continuous irregular paving',
    'draw_step67_frame(Rect2(12,640,696,120)',
    '○長押し:足踏み回復',
    'draw_rect(r.grow(-3.0), Color("#20344e"))'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP68 verification failed: {needle}')
if s == original:
    raise SystemExit('STEP68 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP68_ADOPTED_DUNGEON_UI_REFINEMENT PASS')
