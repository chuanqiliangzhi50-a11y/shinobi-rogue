from pathlib import Path

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')

if 'TITLE_SCREEN_PATCH_APPLIED' in s:
    print('TITLE_SCREEN_PATCH PASS (already applied)')
    raise SystemExit(0)

asset = Path('art/title_screen.jpg')
if not asset.is_file() or asset.stat().st_size < 40000:
    raise SystemExit('title screen asset missing or too small')

anchor = 'const ARMOR_NAME := "忍装束"\n'
if anchor not in s:
    raise SystemExit('title const anchor failed')
s = s.replace(anchor, anchor + 'const TITLE_SCREEN_PATH := "res://art/title_screen.jpg" # TITLE_SCREEN_PATCH_APPLIED\n', 1)

anchor = 'var entity_art: Dictionary = {}\n'
if anchor not in s:
    raise SystemExit('title state anchor failed')
s = s.replace(anchor, anchor + 'var title_screen_active: bool = true\nvar title_screen_texture: Texture2D = null\n', 1)

anchor = '\tload_optional_entity_art()\n\tload_meta()\n'
if anchor not in s:
    raise SystemExit('title ready anchor failed')
s = s.replace(anchor, '\tload_optional_entity_art()\n\tif ResourceLoader.exists(TITLE_SCREEN_PATH):\n\t\ttitle_screen_texture = load(TITLE_SCREEN_PATH) as Texture2D\n\telse:\n\t\ttitle_screen_active = false\n\tload_meta()\n', 1)

anchor = 'func _unhandled_key_input(event: InputEvent) -> void:\n\tif not event.pressed:\n\t\treturn\n'
if anchor not in s:
    raise SystemExit('title key input anchor failed')
s = s.replace(anchor, anchor + '\tif title_screen_active:\n\t\ttitle_screen_active = false\n\t\tqueue_redraw()\n\t\treturn\n', 1)

anchor = 'func _input(event: InputEvent) -> void:\n'
if anchor not in s:
    raise SystemExit('title pointer input anchor failed')
insert = '''func _input(event: InputEvent) -> void:\n\tif title_screen_active:\n\t\tif event is InputEventScreenTouch:\n\t\t\tif event.pressed:\n\t\t\t\ttitle_screen_active = false\n\t\t\t\tqueue_redraw()\n\t\t\treturn\n\t\tif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:\n\t\t\tif event.pressed:\n\t\t\t\ttitle_screen_active = false\n\t\t\t\tqueue_redraw()\n\t\t\treturn\n'''
s = s.replace(anchor, insert, 1)

anchor = 'func _draw() -> void:\n\tdraw_set_transform(content_offset())\n'
if anchor not in s:
    raise SystemExit('title draw anchor failed')
s = s.replace(anchor, anchor + '\tif title_screen_active and title_screen_texture != null:\n\t\tdraw_texture_rect(title_screen_texture, Rect2(0, 0, CONTENT_W, CONTENT_H), false)\n\t\treturn\n', 1)

p.write_text(s, encoding='utf-8')
required = [
    'TITLE_SCREEN_PATCH_APPLIED',
    'title_screen_active: bool = true',
    'title_screen_texture = load(TITLE_SCREEN_PATH)',
    'draw_texture_rect(title_screen_texture, Rect2(0, 0, CONTENT_W, CONTENT_H), false)',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'title verification failed: {needle}')
print('TITLE_SCREEN_PATCH PASS')

# Keep post-title iPhone behavior/presentation patches in the same build stage so
# Pages and future Web exports cannot drift apart.
exec(Path('tools/apply_vertical_confirm_modal.py').read_text(encoding='utf-8'), {})
exec(Path('tools/apply_hold_dash.py').read_text(encoding='utf-8'), {})
exec(Path('tools/apply_dash_run_effect.py').read_text(encoding='utf-8'), {})
