from pathlib import Path
import re

MAIN = Path("Main.gd")
s = MAIN.read_text(encoding="utf-8")
orig = s

DIRECTIONS = [
    "up_left", "up", "up_right", "left",
    "right", "down_left", "down", "down_right",
]
for key in DIRECTIONS:
    p = Path("art") / f"player_dir_{key}.png"
    if not p.exists():
        raise SystemExit(f"missing adopted direction asset: {p}")

if "var player_direction_art: Dictionary = {}" not in s:
    anchor = "var entity_art: Dictionary = {}\n"
    if anchor not in s:
        raise SystemExit("entity_art variable anchor failed")
    s = s.replace(anchor, anchor + "var player_direction_art: Dictionary = {}\n", 1)

direction_const = '''const PLAYER_DIRECTION_ART_PATHS := {
\t"up_left": "res://art/player_dir_up_left.png",
\t"up": "res://art/player_dir_up.png",
\t"up_right": "res://art/player_dir_up_right.png",
\t"left": "res://art/player_dir_left.png",
\t"right": "res://art/player_dir_right.png",
\t"down_left": "res://art/player_dir_down_left.png",
\t"down": "res://art/player_dir_down.png",
\t"down_right": "res://art/player_dir_down_right.png"
}
'''
if "const PLAYER_DIRECTION_ART_PATHS" not in s:
    anchor = "const UI_GLYPH_CELL := 40.0\n"
    if anchor not in s:
        raise SystemExit("UI_GLYPH_CELL anchor failed")
    s = s.replace(anchor, direction_const + anchor, 1)

load_pattern = r'(func load_optional_entity_art\(\) -> void:\n.*?)(?=\n\nfunc draw_entity_visual)'
m = re.search(load_pattern, s, flags=re.S)
if not m:
    raise SystemExit("direction art load function anchor failed")
load_block = m.group(1).rstrip()
if "player_direction_art.clear()" not in load_block:
    load_block += '''
\tplayer_direction_art.clear()
\tfor key in PLAYER_DIRECTION_ART_PATHS.keys():
\t\tvar direction_path := str(PLAYER_DIRECTION_ART_PATHS[key])
\t\tif ResourceLoader.exists(direction_path):
\t\t\tvar direction_tex := load(direction_path) as Texture2D
\t\t\tif direction_tex != null:
\t\t\t\tplayer_direction_art[key] = direction_tex
'''
    s = s[:m.start()] + load_block + s[m.end():]

direction_funcs = '''func player_direction_key() -> String:
\tvar dx: int = clampi(facing_dir.x, -1, 1)
\tvar dy: int = clampi(facing_dir.y, -1, 1)
\tif dx < 0 and dy < 0: return "up_left"
\tif dx == 0 and dy < 0: return "up"
\tif dx > 0 and dy < 0: return "up_right"
\tif dx < 0 and dy == 0: return "left"
\tif dx > 0 and dy == 0: return "right"
\tif dx < 0 and dy > 0: return "down_left"
\tif dx > 0 and dy > 0: return "down_right"
\treturn "down"


func draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
\tvar key := player_direction_key()
\tif player_direction_art.has(key):
\t\tvar tex: Texture2D = player_direction_art[key]
\t\tvar size: float = maxf(12.0, tile_size - 2.0)
\t\tdraw_texture_rect(tex, Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size)), false)
\telse:
\t\tdraw_entity_visual(center, "player", "忍", 21, Color("#ffffff"), tile_size)
'''
s, n = re.subn(
    r'func draw_player_facing_visual\(center: Vector2, tile_size: float\) -> void:\n.*?(?=\n\nconst UI_GLYPH_MAP)',
    direction_funcs.rstrip(), s, count=1, flags=re.S
)
if n != 1:
    raise SystemExit(f"direction player function replace failed: {n}")

map_func = '''func draw_explored_minimap_portrait() -> void:
\tif not validate_grid(explored): return
\tvar cell: float = 9.0
\tvar map_size := Vector2(float(MAP_W) * cell, float(MAP_H) * cell)
\tvar origin := Vector2(690.0 - map_size.x, 214.0)
\tvar frame := Rect2(origin - Vector2(8, 8), map_size + Vector2(16, 16))
\tdraw_rect(frame, Color(0.02, 0.03, 0.04, 0.34), true)
\tdraw_rect(frame, Color(0.82, 0.72, 0.36, 0.60), false, 1.5)

\tfor y in range(MAP_H):
\t\tfor x in range(MAP_W):
\t\t\tif not bool(explored[y][x]) or str(map[y][x]) == "#":
\t\t\t\tcontinue
\t\t\tvar col := Color(0.55, 0.62, 0.70, 0.54)
\t\t\tif str(map[y][x]) == ">":
\t\t\t\tcol = Color(0.95, 0.78, 0.28, 0.90)
\t\t\tdraw_rect(Rect2(origin + Vector2(float(x) * cell + 1.0, float(y) * cell + 1.0), Vector2(cell - 2.0, cell - 2.0)), col, true)

\tfor raw_enemy in enemies:
\t\tvar enemy: Dictionary = raw_enemy
\t\tvar enemy_pos: Vector2i = enemy["pos"]
\t\tif is_visible_cell(enemy_pos):
\t\t\tdraw_circle(origin + Vector2((float(enemy_pos.x) + 0.5) * cell, (float(enemy_pos.y) + 0.5) * cell), 3.4, Color(0.94, 0.32, 0.36, 0.95))

\tfor raw_item in items:
\t\tvar item: Dictionary = raw_item
\t\tvar item_pos: Vector2i = item["pos"]
\t\tif is_visible_cell(item_pos):
\t\t\tdraw_circle(origin + Vector2((float(item_pos.x) + 0.5) * cell, (float(item_pos.y) + 0.5) * cell), 2.4, Color(0.45, 0.86, 0.58, 0.92))

\tdraw_circle(origin + Vector2((float(player.x) + 0.5) * cell, (float(player.y) + 0.5) * cell), 4.2, Color(0.45, 0.82, 1.0, 1.0))
'''
s, n = re.subn(
    r'func draw_explored_minimap_portrait\(\) -> void:\n.*?(?=\n\nfunc generate_floor\(\) -> void:)',
    map_func.rstrip(), s, count=1, flags=re.S
)
if n != 1:
    raise SystemExit(f"map overlay function replace failed: {n}")

if s == orig:
    raise SystemExit("no Main.gd changes made")

MAIN.write_text(s, encoding="utf-8")

for token in [
    "PLAYER_DIRECTION_ART_PATHS",
    "player_direction_art.clear()",
    "player_direction_key()",
    "player_direction_art.has(key)",
    "var cell: float = 9.0",
]:
    if token not in s:
        raise SystemExit(f"missing required token: {token}")

print("DIRECTIONAL_PLAYER_MAP_OVERLAY_PATCH PASS")
