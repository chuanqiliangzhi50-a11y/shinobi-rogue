from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")

if "EXTRA_PROJECTILE_GLYPHS_PATCH_APPLIED" in s:
    print("EXTRA_PROJECTILE_GLYPHS_PATCH PASS (already applied)")
    raise SystemExit(0)

anchor = "var ui_glyph_texture: Texture2D = null\n"
if anchor not in s:
    raise SystemExit("extra glyph state anchor failed")
s = s.replace(anchor, anchor + 'var extra_ui_glyphs: Dictionary = {} # EXTRA_PROJECTILE_GLYPHS_PATCH_APPLIED\n', 1)

anchor = '\tui_glyph_texture = load("res://ui_glyphs.png") as Texture2D\n'
if anchor not in s:
    raise SystemExit("extra glyph ready anchor failed")
s = s.replace(anchor, anchor +
    '\tif ResourceLoader.exists("res://art/glyph_ura.svg"):\n'
    '\t\textra_ui_glyphs["裏"] = load("res://art/glyph_ura.svg") as Texture2D\n'
    '\tif ResourceLoader.exists("res://art/glyph_ken.svg"):\n'
    '\t\textra_ui_glyphs["剣"] = load("res://art/glyph_ken.svg") as Texture2D\n', 1)

old = '''\t\tif UI_GLYPH_MAP.has(ch):
\t\t\tvar cell_pos: Vector2i = UI_GLYPH_MAP[ch]
\t\t\tvar src := Rect2(Vector2(cell_pos.x, cell_pos.y) * UI_GLYPH_CELL, Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL))
\t\t\tvar dst_size := Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL) * scale
\t\t\tvar dst := Rect2(Vector2(x, y), dst_size)
\t\t\tdraw_texture_rect_region(ui_glyph_texture, dst, src, color)
\t\tx += advance'''
new = '''\t\tif UI_GLYPH_MAP.has(ch):
\t\t\tvar cell_pos: Vector2i = UI_GLYPH_MAP[ch]
\t\t\tvar src := Rect2(Vector2(cell_pos.x, cell_pos.y) * UI_GLYPH_CELL, Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL))
\t\t\tvar dst_size := Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL) * scale
\t\t\tvar dst := Rect2(Vector2(x, y), dst_size)
\t\t\tdraw_texture_rect_region(ui_glyph_texture, dst, src, color)
\t\telif extra_ui_glyphs.has(ch):
\t\t\tvar extra_tex: Texture2D = extra_ui_glyphs[ch]
\t\t\tvar extra_size := Vector2(UI_GLYPH_CELL, UI_GLYPH_CELL) * scale
\t\t\tdraw_texture_rect(extra_tex, Rect2(Vector2(x, y), extra_size), false, color)
\t\tx += advance'''
if old not in s:
    raise SystemExit("extra glyph draw anchor failed")
s = s.replace(old, new, 1)

for needle in ['extra_ui_glyphs["裏"]', 'extra_ui_glyphs["剣"]', 'elif extra_ui_glyphs.has(ch):']:
    if needle not in s:
        raise SystemExit("extra glyph verification failed: " + needle)

p.write_text(s, encoding="utf-8")
print("EXTRA_PROJECTILE_GLYPHS_PATCH PASS")
