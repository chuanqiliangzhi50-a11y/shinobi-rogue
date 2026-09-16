from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP66_DUNGEON_VISUAL_DEPTH_APPLIED' in s:
    print('STEP66_DUNGEON_VISUAL_DEPTH PASS (already applied)')
    raise SystemExit(0)

helpers = '''func dungeon_visual_hash(x: int, y: int, salt: int = 0) -> int: # STEP66_DUNGEON_VISUAL_DEPTH_APPLIED
\treturn absi((x * 92821 + y * 68917 + floor_no * 193 + salt * 997) % 2147483647)


func dungeon_walkable_neighbor(x: int, y: int, dx: int, dy: int) -> bool:
\tvar p2 := Vector2i(x + dx, y + dy)
\treturn position_in_bounds(p2) and str(map[p2.y][p2.x]) != "#"


func draw_dungeon_moss(p: Vector2, tile_size: int, seed: int) -> void:
\tvar moss := Color("#334737")
\tvar dark := Color("#26362d")
\tvar side := -1.0 if seed % 2 == 0 else 1.0
\tvar cx := p.x + (7.0 if side < 0.0 else float(tile_size) - 7.0)
\tvar cy := p.y + float(tile_size) - 8.0
\tdraw_circle(Vector2(cx, cy), 5.0, dark)
\tdraw_circle(Vector2(cx + side * 4.0, cy - 2.0), 4.0, moss)
\tdraw_circle(Vector2(cx - side * 3.0, cy + 1.0), 3.0, moss.lightened(0.08))


func draw_dungeon_wall_prop(p: Vector2, tile_size: int, seed: int) -> void:
\tvar center := p + Vector2(tile_size * 0.5, tile_size * 0.58)
\tvar variant := seed % 17
\tif variant == 0:
\t\t# Lantern fixed to the stone wall; warm glow matches the adopted design.
\t\tdraw_circle(center, tile_size * 0.48, Color(1.0, 0.52, 0.12, 0.07))
\t\tdraw_circle(center, tile_size * 0.31, Color(1.0, 0.50, 0.10, 0.10))
\t\tdraw_rect(Rect2(center + Vector2(-4,-7), Vector2(8,14)), Color("#2b2118"))
\t\tdraw_rect(Rect2(center + Vector2(-2,-5), Vector2(4,9)), Color("#ffb347"))
\t\tdraw_circle(center + Vector2(0,-3), 2.5, Color("#ffe0a0"))
\telif variant == 1:
\t\t# Barrel occupies an already-solid wall cell, so gameplay collision is unchanged.
\t\tdraw_rect(Rect2(center + Vector2(-10,-12), Vector2(20,24)), Color("#5b3c27"))
\t\tdraw_arc(center + Vector2(0,-8), 10.0, 0.0, PI, 20, Color("#9a7045"), 2.0)
\t\tdraw_line(center + Vector2(-10,-4), center + Vector2(10,-4), Color("#2a211b"), 2.0)
\t\tdraw_line(center + Vector2(-10,6), center + Vector2(10,6), Color("#2a211b"), 2.0)
\telif variant == 2:
\t\t# Small crate, again only on an impassable wall tile.
\t\tdraw_rect(Rect2(center + Vector2(-11,-10), Vector2(22,21)), Color("#68452b"))
\t\tdraw_rect(Rect2(center + Vector2(-11,-10), Vector2(22,21)), Color("#a37643"), false, 2.0)
\t\tdraw_line(center + Vector2(-9,-8), center + Vector2(9,9), Color("#3e2a20"), 2.0)
\t\tdraw_line(center + Vector2(9,-8), center + Vector2(-9,9), Color("#3e2a20"), 2.0)
\telif variant in [3, 4, 5]:
\t\tdraw_dungeon_moss(p, tile_size, seed)
'''

anchor = '\n\nfunc draw_dungeon_tile(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int) -> void:\n'
if anchor not in s:
    raise SystemExit('STEP66 tile helper anchor failed')
s = s.replace(anchor, '\n\n' + helpers.rstrip() + anchor, 1)

tile_func = '''func draw_dungeon_tile(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int) -> void:
\tvar r := Rect2(p, Vector2(tile_size - 1, tile_size - 1))
\tif not seen:
\t\tdraw_rect(r, Color("#030508"))
\t\treturn
\tvar seed := dungeon_visual_hash(x, y)
\tif tile == "#":
\t\t# Deep blue-gray block wall with a lit face and heavy lower shadow.
\t\tvar wall_base := Color("#27323e") if seed % 4 else Color("#303b48")
\t\tdraw_rect(r, Color("#111820"))
\t\tdraw_rect(Rect2(p + Vector2(1,1), Vector2(tile_size - 3, tile_size - 4)), wall_base)
\t\tdraw_line(p + Vector2(2,3), p + Vector2(tile_size - 3,3), Color("#465462"), 2.0)
\t\tdraw_line(p + Vector2(2,tile_size - 5), p + Vector2(tile_size - 3,tile_size - 5), Color("#141b23"), 3.0)
\t\t# Masonry seams vary deterministically so the wall does not look tiled by one stamp.
\t\tvar seam_y := 13.0 if seed % 2 == 0 else 18.0
\t\tdraw_line(p + Vector2(2,seam_y), p + Vector2(tile_size - 3,seam_y), Color("#1a222b"), 1.5)
\t\tvar seam_x := 11.0 + float(seed % 11)
\t\tdraw_line(p + Vector2(seam_x,3), p + Vector2(seam_x,seam_y), Color("#182029"), 1.5)
\t\tif seed % 3 == 0:
\t\t\tdraw_line(p + Vector2(tile_size - seam_x, seam_y), p + Vector2(tile_size - seam_x,tile_size - 6), Color("#3a4651"), 1.0)
\t\t# Props appear mainly on wall faces bordering a room/corridor.
\t\tvar faces_floor := dungeon_walkable_neighbor(x,y,0,1) or dungeon_walkable_neighbor(x,y,1,0) or dungeon_walkable_neighbor(x,y,-1,0)
\t\tif faces_floor:
\t\t\tdraw_dungeon_wall_prop(p, tile_size, seed)
\telif tile == ">":
\t\t# Stone stairwell with a raised rim and dark descending center.
\t\tdraw_rect(r, Color("#6d604d"))
\t\tdraw_rect(Rect2(p + Vector2(2,2), Vector2(tile_size - 5,tile_size - 5)), Color("#88765b"))
\t\tdraw_rect(Rect2(p + Vector2(6,6), Vector2(tile_size - 13,tile_size - 13)), Color("#22232a"))
\t\tfor i in range(3):
\t\t\tvar inset := 8.0 + float(i * 4)
\t\t\tdraw_rect(Rect2(p + Vector2(inset, 9.0 + i * 5.0), Vector2(maxf(4.0, tile_size - inset * 2.0), 4.0)), Color("#71677a"))
\t\tdraw_rect(Rect2(p + Vector2(5,5), Vector2(tile_size - 11,tile_size - 11)), Color("#b6a47c"), false, 2.0)
\telse:
\t\t# Warm irregular stone floor like the adopted dungeon illustration.
\t\tvar palette := [Color("#76654f"), Color("#806e55"), Color("#6e604d"), Color("#89745a")]
\t\tvar floor_col: Color = palette[seed % palette.size()]
\t\tdraw_rect(r, Color("#4c4338"))
\t\tdraw_rect(Rect2(p + Vector2(1,1), Vector2(tile_size - 3,tile_size - 3)), floor_col)
\t\tdraw_line(p + Vector2(2,2), p + Vector2(tile_size - 3,2), floor_col.lightened(0.12), 1.0)
\t\tdraw_line(p + Vector2(2,tile_size - 3), p + Vector2(tile_size - 3,tile_size - 3), floor_col.darkened(0.18), 1.0)
\t\t# Fine cracks, chips and worn patches are visual only.
\t\tif seed % 4 == 0:
\t\t\tdraw_line(p + Vector2(8,10), p + Vector2(14,14), Color("#50463a"), 1.0)
\t\t\tdraw_line(p + Vector2(14,14), p + Vector2(11,20), Color("#50463a"), 1.0)
\t\tif seed % 7 == 0:
\t\t\tdraw_circle(p + Vector2(tile_size * 0.72,tile_size * 0.68), 3.0, Color(0.20,0.18,0.15,0.20))
\t\tif seed % 13 == 0:
\t\t\tdraw_line(p + Vector2(5,tile_size - 8), p + Vector2(tile_size - 7,tile_size - 10), Color("#9a8464"), 1.0)
'''
s, n = re.subn(r'func draw_dungeon_tile\(p: Vector2, tile: String, seen: bool, x: int, y: int, tile_size: int\) -> void:\n.*?(?=\n\nfunc enemy_sheet_index)', tile_func.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP66 tile replacement failed: {n}')

required = [
    'STEP66_DUNGEON_VISUAL_DEPTH_APPLIED',
    'func draw_dungeon_wall_prop',
    'Warm irregular stone floor',
    'Stone stairwell with a raised rim',
    'faces_floor := dungeon_walkable_neighbor'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP66 verification failed: {needle}')
if s == original:
    raise SystemExit('STEP66 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP66_DUNGEON_VISUAL_DEPTH PASS')
