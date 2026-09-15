from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP64_CONTROLS_PATCH_APPLIED' in s:
    print('STEP64_CONTROLS_PATCH PASS (already applied)')
    raise SystemExit(0)

# Final touch routing. This deliberately overrides the earlier temporary
# hide-center/direction-only handlers so the center pad can never call hide.
handle = '''func handle_press_portrait(pos: Vector2) -> void: # STEP64_CONTROLS_PATCH_APPLIED
\tif in_village:
\t\thandle_village_touch_portrait(pos)
\t\treturn
\tif inventory_menu:
\t\thandle_inventory_touch(pos, true)
\t\treturn
\tif checkout_prompt or stairs_prompt or ad_menu:
\t\thandle_modal_touch_portrait(pos)
\t\treturn
\tif Rect2(22, 662, 76, 76).has_point(pos):
\t\ttoggle_map_visibility()
\t\treturn

\t# Five separated left-side command buttons. No hit areas overlap.
\tvar command_buttons = [
\t\t[Vector2(170, 812), 42.0, "inventory"],
\t\t[Vector2(82, 895), 42.0, "trap"],
\t\t[Vector2(170, 895), 36.0, "technique"],
\t\t[Vector2(258, 895), 42.0, "throw"],
\t\t[Vector2(170, 978), 42.0, "suspend"]
\t]
\tfor button in command_buttons:
\t\tvar center: Vector2 = button[0]
\t\tvar radius: float = float(button[1])
\t\tif pos.distance_to(center) <= radius:
\t\t\tvar action := str(button[2])
\t\t\tif action == "inventory": open_inventory()
\t\t\telif action == "trap": place_trap()
\t\t\telif action == "technique": hide_one_turn()
\t\t\telif action == "throw": use_projectile()
\t\t\telif action == "suspend": suspend_run()
\t\t\tqueue_redraw()
\t\t\treturn

\t# 3x3 direction pad. Center toggles facing-lock mode only.
\tvar base := Vector2(390, 770)
\tvar cell := 96.0
\tif pos.x >= base.x and pos.x < base.x + cell * 3.0 and pos.y >= base.y and pos.y < base.y + cell * 3.0:
\t\tvar cx := int((pos.x - base.x) / cell)
\t\tvar cy := int((pos.y - base.y) / cell)
\t\tvar d := Vector2i(cx - 1, cy - 1)
\t\tif d == Vector2i.ZERO:
\t\t\tstop_dash_hold()
\t\t\tdirection_only_mode = not direction_only_mode
\t\t\tmessage = "向き固定ON。方向キーで向きだけ変える。" if direction_only_mode else "向き固定OFF。"
\t\t\tqueue_redraw()
\t\t\treturn
\t\tif direction_only_mode:
\t\t\tstop_dash_hold()
\t\t\tfacing_dir = d
\t\t\tmessage = "向きを変えた。"
\t\t\tqueue_redraw()
\t\t\treturn
\t\tstart_dash_hold(d)
\t\treturn
'''
s, n = re.subn(r'func handle_press_portrait\(pos: Vector2\) -> void:.*?(?=\n\nfunc handle_village_touch_portrait)', handle.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP64 handle anchor failed: {n}')

controls = '''func draw_mobile_controls_portrait() -> void:
\tdraw_rect(Rect2(0, 760, 720, 340), Color("#07101b"))
\tdraw_reference_leaf(Vector2(35, 1050), 0.75)
\tdraw_reference_leaf(Vector2(330, 1032), 0.50)
\tdraw_reference_leaf(Vector2(685, 1015), 0.65)

\t# Separated five-button ninja command cluster.
\tvar command_buttons = [
\t\t["道具", Vector2(170, 812), 42.0],
\t\t["罠", Vector2(82, 895), 42.0],
\t\t["術", Vector2(170, 895), 36.0],
\t\t["飛", Vector2(258, 895), 42.0],
\t\t["中断", Vector2(170, 978), 42.0]
\t]
\t# Decorative diamond lines stay behind the buttons.
\tvar gold := Color("#d6a74f")
\tdraw_line(Vector2(170, 854), Vector2(124, 882), Color(0.84,0.65,0.31,0.22), 2.0)
\tdraw_line(Vector2(170, 854), Vector2(216, 882), Color(0.84,0.65,0.31,0.22), 2.0)
\tdraw_line(Vector2(124, 908), Vector2(170, 936), Color(0.84,0.65,0.31,0.22), 2.0)
\tdraw_line(Vector2(216, 908), Vector2(170, 936), Color(0.84,0.65,0.31,0.22), 2.0)
\tfor button in command_buttons:
\t\tvar label := str(button[0])
\t\tvar c: Vector2 = button[1]
\t\tvar radius: float = float(button[2])
\t\tdraw_circle(c, radius, Color("#172438"))
\t\tdraw_arc(c, radius, 0.0, TAU, 48, gold, 2.5)
\t\tif label == "術":
\t\t\t# Smoke motif for the ninjutsu button.
\t\t\tdraw_circle(c + Vector2(-9,-8), 8.0, Color(0.55,0.62,0.72,0.18))
\t\t\tdraw_circle(c + Vector2(7,-11), 10.0, Color(0.55,0.62,0.72,0.14))
\t\t\tdraw_ui_text(c + Vector2(-10, 10), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#f1c95b"))
\t\telse:
\t\t\tdraw_ui_text(c + Vector2(-25 if label.length() > 1 else -9, 7), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)

\t# Direction pad: gold-trimmed, with a true toggle in the center.
\tvar base := Vector2(390, 770)
\tvar cell := 96.0
\tvar labels = [["↖", "↑", "↗"], ["←", "", "→"], ["↙", "↓", "↘"]]
\tfor y in range(3):
\t\tfor x in range(3):
\t\t\tvar r := Rect2(base.x + x * cell, base.y + y * cell, 88.0, 88.0)
\t\t\tvar center := x == 1 and y == 1
\t\t\tif center:
\t\t\t\tvar cc := r.get_center()
\t\t\t\tdraw_circle(cc, 39.0, Color("#172438"))
\t\t\t\tdraw_arc(cc, 39.0, 0.0, TAU, 48, gold, 2.5)
\t\t\t\tif direction_only_mode:
\t\t\t\t\t# Filled white circle = ON.
\t\t\t\t\tdraw_circle(cc, 19.0, Color("#f4f5f2"))
\t\t\t\t\tdraw_arc(cc, 22.0, 0.0, TAU, 40, Color("#9eabb8"), 2.0)
\t\t\t\telse:
\t\t\t\t\t# Hollow circle = OFF.
\t\t\t\t\tdraw_arc(cc, 19.0, 0.0, TAU, 40, Color("#f4f5f2"), 3.0)
\t\t\telse:
\t\t\t\tdraw_panel(r, Color("#1a293b"), gold, 2.0)
\t\t\t\tdraw_ui_text(r.position + Vector2(29, 56), labels[y][x], HORIZONTAL_ALIGNMENT_LEFT, -1, 27, Color.WHITE)
'''
s, n = re.subn(r'func draw_mobile_controls_portrait\(\) -> void:.*?(?=\n\nfunc draw_modal_overlay_portrait)', controls.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP64 controls anchor failed: {n}')

required = [
    'STEP64_CONTROLS_PATCH_APPLIED',
    '["術", Vector2(170, 895), 36.0]',
    'direction_only_mode = not direction_only_mode',
    'facing_dir = d',
    'start_dash_hold(d)',
    'Filled white circle = ON',
    'Hollow circle = OFF'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP64 verification failed: {needle}')
if '出会い、拾い、伏せ、進む' in s:
    raise SystemExit('STEP64 obsolete tagline still present')
if s == original:
    raise SystemExit('STEP64 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP64_CONTROLS_PATCH PASS')
