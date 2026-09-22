from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP71_TORNEKO_MELEE_ATTACK_MOTION_APPLIED' in s:
    print('STEP71_TORNEKO_MELEE_ATTACK_MOTION PASS (already applied)')
    raise SystemExit(0)

# Visual-only, Torneko-like quick melee motion: wind-up -> lunge/slash -> return.
state_anchor = 'var hide_hold_active := false\nvar hide_hold_elapsed := 0.0\n'
if state_anchor not in s:
    raise SystemExit('STEP71 state anchor failed')
s = s.replace(state_anchor, state_anchor + '''# STEP71_TORNEKO_MELEE_ATTACK_MOTION_APPLIED
const MELEE_ATTACK_ANIM_DURATION := 0.20
var melee_attack_anim_active := false
var melee_attack_anim_elapsed := 0.0
var melee_attack_anim_dir := Vector2i(0, 1)
var melee_attack_anim_target := Vector2i(-999, -999)
''', 1)

# Start the animation only for adjacent sword attacks. Projectile attacks keep
# their own behavior and do not trigger a sword lunge.
old_melee = '''\tfor i in range(enemies.size()):
\t\tif enemies[i]["pos"] == target:
\t\t\tattack_enemy(i)
\t\t\tskip_auto_pickup_once = false
\t\t\tend_turn()
\t\t\treturn'''
new_melee = '''\tfor i in range(enemies.size()):
\t\tif enemies[i]["pos"] == target:
\t\t\tstart_melee_attack_animation(dir, target)
\t\t\tattack_enemy(i)
\t\t\tskip_auto_pickup_once = false
\t\t\tend_turn()
\t\t\treturn'''
if old_melee not in s:
    raise SystemExit('STEP71 melee trigger anchor failed')
s = s.replace(old_melee, new_melee, 1)

# Advance the visual animation from _process without delaying turn resolution.
m = re.search(r'func _process\(delta: float\) -> void:\n(.*?)(?=\n\nfunc _unhandled_key_input)', s, flags=re.S)
if not m:
    raise SystemExit('STEP71 process function failed')
body = m.group(1)
if 'melee_attack_anim_elapsed += delta' not in body:
    insert = '''\tif melee_attack_anim_active:
\t\tmelee_attack_anim_elapsed += delta
\t\tif melee_attack_anim_elapsed >= MELEE_ATTACK_ANIM_DURATION:
\t\t\tmelee_attack_anim_active = false
\t\t\tmelee_attack_anim_elapsed = 0.0
'''
    q = body.rfind('\tqueue_redraw()')
    if q < 0:
        raise SystemExit('STEP71 process redraw anchor failed')
    body = body[:q] + insert + body[q:]
    s = s[:m.start(1)] + body + s[m.end(1):]

# Helpers calculate the short Torneko-style lunge. The logical player cell
# never changes: only the rendered sprite shifts toward the attacked cell.
helper_anchor = '\n\nfunc attack_enemy(index: int) -> void:\n'
if helper_anchor not in s:
    raise SystemExit('STEP71 attack helper anchor failed')
helpers = '''

func start_melee_attack_animation(dir: Vector2i, target: Vector2i) -> void:
\tmelee_attack_anim_active = true
\tmelee_attack_anim_elapsed = 0.0
\tmelee_attack_anim_dir = Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))
\tmelee_attack_anim_target = target
\tqueue_redraw()


func melee_attack_visual_offset() -> Vector2:
\tif not melee_attack_anim_active:
\t\treturn Vector2.ZERO
\tvar t := clampf(melee_attack_anim_elapsed / MELEE_ATTACK_ANIM_DURATION, 0.0, 1.0)
\tvar amount := 0.0
\tif t < 0.22:
\t\t# Small anticipation opposite the target.
\t\tamount = -3.0 * (t / 0.22)
\telif t < 0.58:
\t\t# Fast one-cell-feel strike without changing the logical cell.
\t\tamount = lerpf(-3.0, 15.0, (t - 0.22) / 0.36)
\telse:
\t\tamount = lerpf(15.0, 0.0, (t - 0.58) / 0.42)
\treturn Vector2(melee_attack_anim_dir) * amount


func draw_melee_attack_effect(player_center: Vector2, tile_size: float) -> void:
\tif not melee_attack_anim_active:
\t\treturn
\tvar t := clampf(melee_attack_anim_elapsed / MELEE_ATTACK_ANIM_DURATION, 0.0, 1.0)
\tif t < 0.24 or t > 0.76:
\t\treturn
\tvar d := Vector2(melee_attack_anim_dir).normalized()
\tif d.length() < 0.5:
\t\treturn
\tvar n := Vector2(-d.y, d.x)
\tvar hit_center := player_center + d * (tile_size * 0.62)
\tvar sweep := (t - 0.24) / 0.52
\tvar radius := tile_size * (0.32 + 0.08 * sin(sweep * PI))
\t# Bright blade trail and compact impact spark, readable at phone size.
\tvar a := hit_center - d * 7.0 + n * radius
\tvar b := hit_center + d * 5.0
\tvar c := hit_center - d * 7.0 - n * radius
\tdraw_polyline(PackedVector2Array([a, b, c]), Color(1.0,0.93,0.72,0.95), 4.0)
\tdraw_polyline(PackedVector2Array([a + d*3.0, b + d*4.0, c + d*3.0]), Color(1.0,0.63,0.20,0.72), 2.0)
\tif t >= 0.42 and t <= 0.64:
\t\tfor v in [Vector2(1,0),Vector2(-1,0),Vector2(0,1),Vector2(0,-1),Vector2(0.7,0.7),Vector2(-0.7,-0.7)]:
\t\t\tdraw_line(hit_center + v*4.0, hit_center + v*11.0, Color(1.0,0.78,0.28,0.88), 2.0)
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

# Apply the offset only to the player sprite/ring, then draw the slash over it.
old_player = '''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tdraw_arc(pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(pc, PTILE + 17.0)'''
if old_player not in s:
    # STEP69 replacement ordering can leave the +13 form depending on patch text.
    old_player = '''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tdraw_arc(pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(pc, PTILE + 13.0)'''
new_player = '''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tvar attack_offset := melee_attack_visual_offset()
\t\tvar visual_pc := pc + attack_offset
\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
if old_player not in s:
    raise SystemExit('STEP71 portrait player draw anchor failed')
s = s.replace(old_player, new_player, 1)

required = [
    'STEP71_TORNEKO_MELEE_ATTACK_MOTION_APPLIED',
    'start_melee_attack_animation(dir, target)',
    'melee_attack_anim_elapsed += delta',
    'func melee_attack_visual_offset()',
    'func draw_melee_attack_effect',
    'var visual_pc := pc + attack_offset'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP71 verification failed: {needle}')
if s == original:
    raise SystemExit('STEP71 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP71_TORNEKO_MELEE_ATTACK_MOTION PASS')
exec(Path('tools/apply_step72_sword_swing_damage_blink.py').read_text(encoding='utf-8'), {})
