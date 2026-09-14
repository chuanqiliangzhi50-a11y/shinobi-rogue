from pathlib import Path
import re, struct, zlib, binascii

MAIN = Path("Main.gd")
PLAYER = Path("art/player.png")
s = MAIN.read_text(encoding="utf-8")
orig = s

PNG_SIG = b"\x89PNG\r\n\x1a\n"

def read_png_rgba(path: Path):
    data = path.read_bytes()
    if not data.startswith(PNG_SIG):
        raise SystemExit("player.png is not PNG")
    pos = 8
    width = height = None
    color_type = bit_depth = None
    compressed = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        payload = data[pos+8:pos+8+length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack(">IIBBBBB", payload)
            if bit_depth != 8 or color_type != 6 or interlace != 0:
                raise SystemExit("player.png must be non-interlaced 8-bit RGBA")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    raw = zlib.decompress(bytes(compressed))
    bpp = 4
    stride = width * bpp
    rows = []
    off = 0
    prev = bytearray(stride)
    for _y in range(height):
        f = raw[off]
        off += 1
        cur = bytearray(raw[off:off+stride])
        off += stride
        recon = bytearray(stride)
        for i, x in enumerate(cur):
            a = recon[i-bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i-bpp] if i >= bpp else 0
            if f == 0:
                val = x
            elif f == 1:
                val = (x + a) & 255
            elif f == 2:
                val = (x + b) & 255
            elif f == 3:
                val = (x + ((a + b) >> 1)) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p-a), abs(p-b), abs(p-c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                val = (x + pr) & 255
            else:
                raise SystemExit(f"unsupported PNG filter {f}")
            recon[i] = val
        rows.append(recon)
        prev = recon
    pixels = [[tuple(row[x:x+4]) for x in range(0, stride, 4)] for row in rows]
    return width, height, pixels

def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(kind + payload) & 0xffffffff)

def write_png_rgba(path: Path, width: int, height: int, pixels):
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw.extend(bytes(pixels[y][x]))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    out = PNG_SIG + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b"")
    path.write_bytes(out)

def clone(pix):
    return [row[:] for row in pix]

def rect(pix, x0, y0, x1, y1, color):
    h, w = len(pix), len(pix[0])
    for y in range(max(0,y0), min(h,y1+1)):
        for x in range(max(0,x0), min(w,x1+1)):
            pix[y][x] = color

def mirror(pix):
    return [list(reversed(row)) for row in pix]

def compress(pix, new_w=54, xoff=5):
    h, w = len(pix), len(pix[0])
    out = [[(0,0,0,0) for _ in range(w)] for _ in range(h)]
    for y in range(h):
        for nx in range(new_w):
            sx = min(w-1, int(nx * w / new_w))
            out[y][xoff + nx] = pix[y][sx]
    return out

def make_up(base):
    out = clone(base)
    rect(out,17,22,47,34,(14,15,15,255))
    rect(out,20,23,44,25,(39,40,39,255))
    rect(out,20,31,44,32,(3,3,3,255))
    rect(out,31,23,31,33,(28,29,28,255))
    return out

def make_right(base):
    out = compress(base,54,5)
    rect(out,16,22,32,34,(12,13,13,255))
    rect(out,34,24,42,27,(52,48,39,255))
    rect(out,39,24,42,26,(6,6,6,255))
    rect(out,42,28,45,30,(196,151,82,255))
    return out

def make_down_right(base):
    out = clone(base)
    rect(out,16,22,27,33,(14,15,15,255))
    rect(out,33,24,42,27,(76,61,42,255))
    rect(out,39,24,42,26,(6,6,6,255))
    return out

def make_up_right(base):
    out = compress(make_up(base),56,4)
    rect(out,39,25,42,26,(119,101,72,255))
    rect(out,41,25,42,25,(4,4,4,255))
    return out

w, h, base = read_png_rgba(PLAYER)
if (w,h) != (64,64):
    raise SystemExit(f"unexpected player size {(w,h)}")

sprites = {
    "down": clone(base),
    "down_right": make_down_right(base),
    "right": make_right(base),
    "up_right": make_up_right(base),
    "up": make_up(base),
}
sprites["up_left"] = mirror(sprites["up_right"])
sprites["left"] = mirror(sprites["right"])
sprites["down_left"] = mirror(sprites["down_right"])

art_dir = Path("art")
for key, pix in sprites.items():
    target = art_dir / f"player_dir_{key}.png"
    if not target.exists():
        write_png_rgba(target, w, h, pix)

if "var player_direction_art: Dictionary = {}" not in s:
    s = s.replace(
        "var entity_art: Dictionary = {}\n",
        "var entity_art: Dictionary = {}\nvar player_direction_art: Dictionary = {}\n",
        1,
    )

direction_const = '''const PLAYER_DIRECTION_ART_PATHS := {
    "up_left": "res://art/player_dir_up_left.png",
    "up": "res://art/player_dir_up.png",
    "up_right": "res://art/player_dir_up_right.png",
    "left": "res://art/player_dir_left.png",
    "right": "res://art/player_dir_right.png",
    "down_left": "res://art/player_dir_down_left.png",
    "down": "res://art/player_dir_down.png",
    "down_right": "res://art/player_dir_down_right.png"
}
'''
if "const PLAYER_DIRECTION_ART_PATHS" not in s:
    s = s.replace("const UI_GLYPH_CELL := 40.0\n", direction_const + "const UI_GLYPH_CELL := 40.0\n", 1)

load_anchor = '''                entity_art[key] = tex


func draw_entity_visual'''
if load_anchor not in s:
    raise SystemExit("direction art load anchor failed")
s = s.replace(load_anchor, '''                entity_art[key] = tex
    player_direction_art.clear()
    for key in PLAYER_DIRECTION_ART_PATHS.keys():
        var direction_path := str(PLAYER_DIRECTION_ART_PATHS[key])
        if ResourceLoader.exists(direction_path):
            var direction_tex := load(direction_path) as Texture2D
            if direction_tex != null:
                player_direction_art[key] = direction_tex


func draw_entity_visual''', 1)

direction_funcs = '''func player_direction_key() -> String:
    var dx: int = clampi(facing_dir.x, -1, 1)
    var dy: int = clampi(facing_dir.y, -1, 1)
    if dx < 0 and dy < 0: return "up_left"
    if dx == 0 and dy < 0: return "up"
    if dx > 0 and dy < 0: return "up_right"
    if dx < 0 and dy == 0: return "left"
    if dx > 0 and dy == 0: return "right"
    if dx < 0 and dy > 0: return "down_left"
    if dx > 0 and dy > 0: return "down_right"
    return "down"


func draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
    var key := player_direction_key()
    if player_direction_art.has(key):
        var tex: Texture2D = player_direction_art[key]
        var size: float = maxf(12.0, tile_size - 2.0)
        draw_texture_rect(tex, Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size)), false)
    else:
        draw_entity_visual(center, "player", "忍", 21, Color("#ffffff"), tile_size)
'''
s, n = re.subn(
    r'func draw_player_facing_visual\(center: Vector2, tile_size: float\) -> void:\n.*?(?=\n\nconst UI_GLYPH_MAP)',
    direction_funcs.rstrip(), s, count=1, flags=re.S
)
if n != 1:
    raise SystemExit(f"direction player function replace failed: {n}")

map_func = '''func draw_explored_minimap_portrait() -> void:
    if not validate_grid(explored): return
    var cell: float = 9.0
    var map_size := Vector2(float(MAP_W) * cell, float(MAP_H) * cell)
    var origin := Vector2(690.0 - map_size.x, 214.0)
    var frame := Rect2(origin - Vector2(8, 8), map_size + Vector2(16, 16))
    draw_rect(frame, Color(0.02, 0.03, 0.04, 0.34), true)
    draw_rect(frame, Color(0.82, 0.72, 0.36, 0.60), false, 1.5)

    for y in range(MAP_H):
        for x in range(MAP_W):
            if not bool(explored[y][x]) or str(map[y][x]) == "#":
                continue
            var col := Color(0.55, 0.62, 0.70, 0.54)
            if str(map[y][x]) == ">":
                col = Color(0.95, 0.78, 0.28, 0.90)
            draw_rect(Rect2(origin + Vector2(float(x) * cell + 1.0, float(y) * cell + 1.0), Vector2(cell - 2.0, cell - 2.0)), col, true)

    for raw_enemy in enemies:
        var enemy: Dictionary = raw_enemy
        var enemy_pos: Vector2i = enemy["pos"]
        if is_visible_cell(enemy_pos):
            draw_circle(origin + Vector2((float(enemy_pos.x) + 0.5) * cell, (float(enemy_pos.y) + 0.5) * cell), 3.4, Color(0.94, 0.32, 0.36, 0.95))

    for raw_item in items:
        var item: Dictionary = raw_item
        var item_pos: Vector2i = item["pos"]
        if is_visible_cell(item_pos):
            draw_circle(origin + Vector2((float(item_pos.x) + 0.5) * cell, (float(item_pos.y) + 0.5) * cell), 2.4, Color(0.45, 0.86, 0.58, 0.92))

    draw_circle(origin + Vector2((float(player.x) + 0.5) * cell, (float(player.y) + 0.5) * cell), 4.2, Color(0.45, 0.82, 1.0, 1.0))
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

for token in ["PLAYER_DIRECTION_ART_PATHS", "player_direction_key()", 'player_direction_art.has(key)', "var cell: float = 9.0"]:
    if token not in s:
        raise SystemExit(f"missing required token: {token}")

print("DIRECTIONAL_PLAYER_MAP_OVERLAY_PATCH PASS")
