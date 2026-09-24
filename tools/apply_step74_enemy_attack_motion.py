from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP74_ENEMY_ATTACK_MOTION_APPLIED" in s:
    print("STEP74_ENEMY_ATTACK_MOTION PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP73_NINJUTSU_CHARGE_POSE_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP74 STEP73 state anchor failed")
s = s.replace(
    marker,
    marker
    + "# STEP74_ENEMY_ATTACK_MOTION_APPLIED\n"
    + "const ENEMY_ATTACK_ANIM_DURATION := 0.22\n",
    1,
)

process_match = re.search(
    r"func _process\(delta: float\) -> void:\n(.*?)(?=\n\nfunc _unhandled_key_input)",
    s,
    flags=re.S,
)
if not process_match:
    raise SystemExit("STEP74 process function failed")
process_body = process_match.group(1)
flash_loop = '''\tfor flash_enemy in enemies:
\t\tvar flash_left := float(flash_enemy.get("_hit_flash", 0.0))
\t\tif flash_left > 0.0:
\t\t\tflash_enemy["_hit_flash"] = maxf(0.0, flash_left - delta)
'''
if flash_loop not in process_body:
    raise SystemExit("STEP74 enemy flash loop anchor failed")
process_body = process_body.replace(
    flash_loop,
    flash_loop
    + '''\t\tvar attack_left := float(flash_enemy.get("_attack_anim", 0.0))
\t\tif attack_left > 0.0:
\t\t\tflash_enemy["_attack_anim"] = maxf(0.0, attack_left - delta)
''',
    1,
)
s = s[: process_match.start(1)] + process_body + s[process_match.end(1) :]

helper_anchor = "\n\nfunc start_player_hit_flash() -> void:\n"
if helper_anchor not in s:
    raise SystemExit("STEP74 hit helper anchor failed")
helpers = '''

func start_enemy_attack_animation(index: int) -> void:
\tif index < 0 or index >= enemies.size():
\t\treturn
\tvar enemy_pos: Vector2i = enemies[index]["pos"]
\tvar delta := player - enemy_pos
\tif max(abs(delta.x), abs(delta.y)) > 1:
\t\treturn
\tenemies[index]["_attack_anim"] = ENEMY_ATTACK_ANIM_DURATION
\tenemies[index]["_attack_dir"] = Vector2(sign(delta.x), sign(delta.y))
\tqueue_redraw()


func enemy_attack_visual_offset(enemy: Dictionary) -> Vector2:
\tvar left := float(enemy.get("_attack_anim", 0.0))
\tif left <= 0.0:
\t\treturn Vector2.ZERO
\tvar t := clampf(1.0 - left / ENEMY_ATTACK_ANIM_DURATION, 0.0, 1.0)
\tvar amount := 0.0
\tif t < 0.28:
\t\tamount = lerpf(0.0, -5.0, t / 0.28)
\telif t < 0.62:
\t\tamount = lerpf(-5.0, 13.0, (t - 0.28) / 0.34)
\telse:
\t\tamount = lerpf(13.0, 0.0, (t - 0.62) / 0.38)
\treturn Vector2(enemy.get("_attack_dir", Vector2.ZERO)) * amount
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

enemy_damage = '''\thp -= dmg
\tstart_player_hit_flash()
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
enemy_damage_new = '''\tstart_enemy_attack_animation(index)
\thp -= dmg
\tstart_player_hit_flash()
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
if enemy_damage not in s:
    raise SystemExit("STEP74 enemy attack anchor failed")
s = s.replace(enemy_damage, enemy_damage_new, 1)

enemy_draw = '''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep)
\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tif not enemy_hit_flash_hidden(e):
\t\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 17.0)'''
enemy_draw_new = '''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep) + enemy_attack_visual_offset(e)
\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tif not enemy_hit_flash_hidden(e):
\t\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 17.0)'''
if enemy_draw not in s:
    raise SystemExit("STEP74 enemy draw anchor failed")
s = s.replace(enemy_draw, enemy_draw_new, 1)

required = [
    "STEP74_ENEMY_ATTACK_MOTION_APPLIED",
    "func start_enemy_attack_animation",
    "func enemy_attack_visual_offset",
    "start_enemy_attack_animation(index)",
    "portrait_cell_center(ep) + enemy_attack_visual_offset(e)",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP74 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP74 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP74_ENEMY_ATTACK_MOTION PASS")
