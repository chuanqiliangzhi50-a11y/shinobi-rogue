from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP69_CLOSE_DUNGEON_COMPOSITION_APPLIED' in s:
    print('STEP69_CLOSE_DUNGEON_COMPOSITION PASS (already applied)')
    raise SystemExit(0)

# The reference reads as a close, room-filling dungeon rather than a distant
# map view. Keep the logical map unchanged and change only the portrait camera.
origin = '''func portrait_camera_origin() -> Vector2i: # STEP69_CLOSE_DUNGEON_COMPOSITION_APPLIED
\tconst VIEW_W := 13
\tconst VIEW_H := 9
\tvar ox: int = player.x - int(VIEW_W / 2)
\tvar oy: int = player.y - int(VIEW_H / 2)
\treturn Vector2i(ox, oy)'''
s, n = re.subn(r'func portrait_camera_origin\(\) -> Vector2i:\n.*?(?=\n\nfunc portrait_cell_in_view)', origin, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP69 camera origin failed: {n}')

in_view = '''func portrait_cell_in_view(p: Vector2i) -> bool:
\tconst VIEW_W := 13
\tconst VIEW_H := 9
\tvar origin := portrait_camera_origin()
\treturn p.x >= origin.x and p.y >= origin.y and p.x < origin.x + VIEW_W and p.y < origin.y + VIEW_H'''
s, n = re.subn(r'func portrait_cell_in_view\(p: Vector2i\) -> bool:\n.*?(?=\n\nfunc portrait_cell_center)', in_view, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP69 in-view failed: {n}')

center = '''func portrait_cell_center(p: Vector2i) -> Vector2:
\tconst PTILE := 48
\tconst PMAP_X := 48
\tconst PMAP_Y := 207
\tvar origin := portrait_camera_origin()
\tvar local := p - origin
\treturn Vector2(PMAP_X + local.x * PTILE + PTILE * 0.5, PMAP_Y + local.y * PTILE + PTILE * 0.5)'''
s, n = re.subn(r'func portrait_cell_center\(p: Vector2i\) -> Vector2:\n.*?(?=\n\nfunc handle_press_portrait)', center, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP69 center failed: {n}')

# STEP67 owns the final portrait draw function. Replace only its local camera
# constants and entity visual sizes. This leaves generation/collision untouched.
draw_start = s.find('func draw_dungeon_portrait() -> void:')
draw_end = s.find('\n\nfunc draw_mobile_controls_portrait()', draw_start)
if draw_start < 0 or draw_end < 0:
    raise SystemExit('STEP69 draw function bounds failed')
block = s[draw_start:draw_end]
block = block.replace('const PTILE := 40', 'const PTILE := 48', 1)
block = block.replace('const PMAP_X := 44', 'const PMAP_X := 48', 1)
block = block.replace('const PMAP_Y := 204', 'const PMAP_Y := 207', 1)
block = block.replace('const VIEW_W := 15', 'const VIEW_W := 13', 1)
block = block.replace('const VIEW_H := 11', 'const VIEW_H := 9', 1)
# Larger actors/items are a visual-only scale change.
block = block.replace('PTILE + 5.0)', 'PTILE + 8.0)')
block = block.replace('PTILE + 10.0)', 'PTILE + 13.0)')
block = block.replace('PTILE + 8.0)', 'PTILE + 11.0)')
block = block.replace('PTILE + 13.0)', 'PTILE + 17.0)')
s = s[:draw_start] + block + s[draw_end:]

required = [
    'STEP69_CLOSE_DUNGEON_COMPOSITION_APPLIED',
    'const VIEW_W := 13',
    'const VIEW_H := 9',
    'const PTILE := 48',
    'const PMAP_X := 48',
    'const PMAP_Y := 207'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP69 verification failed: {needle}')
if s == original:
    raise SystemExit('STEP69 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP69_CLOSE_DUNGEON_COMPOSITION PASS')
exec(Path('tools/apply_step70_reference_map_presentation.py').read_text(encoding='utf-8'), {})
