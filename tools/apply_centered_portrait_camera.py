from pathlib import Path

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

old_origin = '''\tvar ox: int = clampi(player.x - int(VIEW_W / 2), 0, MAP_W - VIEW_W)\n\tvar oy: int = clampi(player.y - int(VIEW_H / 2), 0, MAP_H - VIEW_H)'''
new_origin = '''\t# Keep the player at the viewport center even near dungeon edges.\n\t# Cells outside the map are rendered as darkness below.\n\tvar ox: int = player.x - int(VIEW_W / 2)\n\tvar oy: int = player.y - int(VIEW_H / 2)'''
if old_origin not in s:
    raise SystemExit('center-camera origin anchor not found')
s = s.replace(old_origin, new_origin, 1)

old_draw = '''\t\t\t\tvar wx := origin.x + vx\n\t\t\t\tvar wy := origin.y + vy\n\t\t\t\tvar p := Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)\n\t\t\t\tvar seen := validate_grid(explored) and bool(explored[wy][wx])\n\t\t\t\tvar tile := str(map[wy][wx]) if validate_grid(map) else "#"\n\t\t\t\tdraw_dungeon_tile(p, tile, seen, wx, wy, PTILE)'''
new_draw = '''\t\t\t\tvar wx := origin.x + vx\n\t\t\t\tvar wy := origin.y + vy\n\t\t\t\tvar p := Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)\n\t\t\t\tif wx < 0 or wy < 0 or wx >= MAP_W or wy >= MAP_H:\n\t\t\t\t\tdraw_rect(Rect2(p, Vector2(PTILE - 1, PTILE - 1)), Color("#05080b"))\n\t\t\t\t\tcontinue\n\t\t\t\tvar seen := validate_grid(explored) and bool(explored[wy][wx])\n\t\t\t\tvar tile := str(map[wy][wx]) if validate_grid(map) else "#"\n\t\t\t\tdraw_dungeon_tile(p, tile, seen, wx, wy, PTILE)'''
if old_draw not in s:
    raise SystemExit('center-camera draw anchor not found')
s = s.replace(old_draw, new_draw, 1)

if s == original:
    raise SystemExit('no changes made')
p.write_text(s, encoding='utf-8')
print('CENTERED_PORTRAIT_CAMERA_PATCH PASS')
