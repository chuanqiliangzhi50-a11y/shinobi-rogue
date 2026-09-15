from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'HOLD_DASH_PATCH_APPLIED' in s:
    print('HOLD_DASH_PATCH PASS (already applied)')
    raise SystemExit(0)

anchor = 'const HIDE_HOLD_INTERVAL := 0.22\n'
if anchor not in s:
    raise SystemExit('hold dash const anchor failed')
s = s.replace(anchor, anchor + '''const DASH_HOLD_DELAY := 0.28 # HOLD_DASH_PATCH_APPLIED\nconst DASH_HOLD_INTERVAL := 0.075\n''', 1)

anchor = 'var hide_hold_elapsed := 0.0\n'
if anchor not in s:
    raise SystemExit('hold dash state anchor failed')
s = s.replace(anchor, anchor + '''var dash_hold_active := false\nvar dash_hold_dir := Vector2i.ZERO\nvar dash_hold_elapsed := 0.0\nvar dash_hold_repeating := false\n''', 1)

process_anchor = '\tqueue_redraw()\n\n\nfunc _unhandled_key_input(event: InputEvent) -> void:\n'
if process_anchor not in s:
    raise SystemExit('hold dash process anchor failed')
process_insert = '''\tif dash_hold_active and not in_village and not checkout_prompt and not stairs_prompt and not ad_menu and not inventory_menu:\n\t\tdash_hold_elapsed += delta\n\t\tif not dash_hold_repeating:\n\t\t\tif dash_hold_elapsed >= DASH_HOLD_DELAY:\n\t\t\t\tdash_hold_repeating = true\n\t\t\t\tdash_hold_elapsed = 0.0\n\t\t\t\tdash_hold_step()\n\t\telif dash_hold_elapsed >= DASH_HOLD_INTERVAL:\n\t\t\tdash_hold_elapsed = 0.0\n\t\t\tdash_hold_step()\n\tqueue_redraw()\n\n\nfunc _unhandled_key_input(event: InputEvent) -> void:\n'''
s = s.replace(process_anchor, process_insert, 1)

s = s.replace('\t\t\thide_hold_active = false\n\t\treturn\n', '\t\t\thide_hold_active = false\n\t\t\tstop_dash_hold()\n\t\treturn\n', 1)
s = s.replace('\t\t\thide_hold_active = false\n\n\nfunc handle_press(pos: Vector2) -> void:\n', '\t\t\thide_hold_active = false\n\t\t\tstop_dash_hold()\n\n\nfunc handle_press(pos: Vector2) -> void:\n', 1)

portrait_match = re.search(r'(func handle_press_portrait\(pos: Vector2\) -> void:\n.*?)(?=\n\nfunc handle_village_touch_portrait)', s, re.S)
if not portrait_match:
    raise SystemExit('hold dash portrait handler anchor failed')
portrait = portrait_match.group(1)
old = '\t\telse:\n\t\t\ttry_move(d)\n\t\treturn\n'
if old not in portrait:
    raise SystemExit('hold dash portrait dpad anchor failed')
portrait = portrait.replace(old, '\t\telse:\n\t\t\tstart_dash_hold(d)\n\t\treturn\n', 1)
s = s[:portrait_match.start(1)] + portrait + s[portrait_match.end(1):]

land_match = re.search(r'(func handle_touch\(pos: Vector2\) -> void:\n.*?)(?=\n\nfunc start_run)', s, re.S)
if not land_match:
    raise SystemExit('hold dash landscape handler anchor failed')
land = land_match.group(1)
if old in land:
    land = land.replace(old, '\t\telse:\n\t\t\tstart_dash_hold(d)\n\t\treturn\n', 1)
    s = s[:land_match.start(1)] + land + s[land_match.end(1):]

helper_anchor = '\n\nfunc try_move(dir: Vector2i) -> void:\n'
if helper_anchor not in s:
    raise SystemExit('hold dash try_move anchor failed')
helpers = '''\n\nfunc stop_dash_hold() -> void:\n\tdash_hold_active = false\n\tdash_hold_dir = Vector2i.ZERO\n\tdash_hold_elapsed = 0.0\n\tdash_hold_repeating = false\n\n\nfunc dash_enemy_nearby() -> bool:\n\tfor e in enemies:\n\t\tvar ep: Vector2i = e.get("pos", Vector2i(-99, -99))\n\t\tif max(abs(ep.x - player.x), abs(ep.y - player.y)) <= 1:\n\t\t\treturn true\n\tif shopkeeper.size() > 0:\n\t\tvar sp: Vector2i = shopkeeper.get("pos", Vector2i(-99, -99))\n\t\tif max(abs(sp.x - player.x), abs(sp.y - player.y)) <= 1:\n\t\t\treturn true\n\treturn false\n\n\nfunc dash_blocker_ahead(dir: Vector2i) -> bool:\n\tvar target := player + dir\n\tif not is_walkable(target):\n\t\treturn true\n\tif cell_has_enemy(target, -1):\n\t\treturn true\n\tif shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == target:\n\t\treturn true\n\treturn false\n\n\nfunc start_dash_hold(dir: Vector2i) -> void:\n\tstop_dash_hold()\n\tif dir == Vector2i.ZERO:\n\t\treturn\n\tdash_hold_active = true\n\tdash_hold_dir = dir\n\tvar target := player + dir\n\tvar stop_after_tap := dash_blocker_ahead(dir) or cell_has_item(target) or target == stairs_pos\n\ttry_move(dir)\n\tif stop_after_tap or in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:\n\t\tstop_dash_hold()\n\n\nfunc dash_hold_step() -> void:\n\tif not dash_hold_active or dash_hold_dir == Vector2i.ZERO:\n\t\treturn\n\tif in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:\n\t\tstop_dash_hold()\n\t\treturn\n\tif dash_enemy_nearby() or dash_blocker_ahead(dash_hold_dir):\n\t\tstop_dash_hold()\n\t\treturn\n\tvar target := player + dash_hold_dir\n\tvar stop_after_move := cell_has_item(target) or target == stairs_pos\n\ttry_move(dash_hold_dir)\n\tif stop_after_move or in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:\n\t\tstop_dash_hold()\n'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

required = ['HOLD_DASH_PATCH_APPLIED', 'func start_dash_hold(dir: Vector2i) -> void:', 'func dash_hold_step() -> void:', 'start_dash_hold(d)', 'DASH_HOLD_DELAY := 0.28', 'DASH_HOLD_INTERVAL := 0.075']
for needle in required:
    if needle not in s:
        raise SystemExit(f'hold dash verification failed: {needle}')
if s == original:
    raise SystemExit('hold dash made no changes')
p.write_text(s, encoding='utf-8')
print('HOLD_DASH_PATCH PASS')
