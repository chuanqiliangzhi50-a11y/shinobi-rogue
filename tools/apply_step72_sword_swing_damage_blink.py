from pathlib import Path
import re

p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
original=s

if 'STEP72_SWORD_SWING_DAMAGE_BLINK_APPLIED' in s:
    print('STEP72_SWORD_SWING_DAMAGE_BLINK PASS (already applied)')
    raise SystemExit(0)

# --- damage flash state ----------------------------------------------------
anchor='var melee_attack_anim_target := Vector2i(-999, -999)\n'
if anchor not in s:
    raise SystemExit('STEP72 STEP71 state anchor failed')
s=s.replace(anchor, anchor+'''# STEP72_SWORD_SWING_DAMAGE_BLINK_APPLIED
const HIT_FLASH_DURATION := 0.24
const HIT_FLASH_INTERVAL := 0.055
var player_hit_flash_remaining := 0.0
''',1)

# Advance player/enemy flash timers inside the existing process function.
m=re.search(r'func _process\(delta: float\) -> void:\n(.*?)(?=\n\nfunc _unhandled_key_input)',s,flags=re.S)
if not m:
    raise SystemExit('STEP72 process function failed')
body=m.group(1)
insert='''\tif player_hit_flash_remaining > 0.0:
\t\tplayer_hit_flash_remaining = maxf(0.0, player_hit_flash_remaining - delta)
\tfor flash_enemy in enemies:
\t\tvar flash_left := float(flash_enemy.get("_hit_flash", 0.0))
\t\tif flash_left > 0.0:
\t\t\tflash_enemy["_hit_flash"] = maxf(0.0, flash_left - delta)
'''
q=body.rfind('\tqueue_redraw()')
if q<0:
    raise SystemExit('STEP72 process redraw anchor failed')
body=body[:q]+insert+body[q:]
s=s[:m.start(1)]+body+s[m.end(1):]

# Helpers for classic roguelike damage blinking.
helper_anchor='\n\nfunc start_melee_attack_animation(dir: Vector2i, target: Vector2i) -> void:\n'
if helper_anchor not in s:
    raise SystemExit('STEP72 helper anchor failed')
helpers='''

func start_player_hit_flash() -> void:
\tplayer_hit_flash_remaining = HIT_FLASH_DURATION
\tqueue_redraw()


func start_enemy_hit_flash(index: int) -> void:
\tif index < 0 or index >= enemies.size():
\t\treturn
\tenemies[index]["_hit_flash"] = HIT_FLASH_DURATION
\tqueue_redraw()


func player_hit_flash_hidden() -> bool:
\tif player_hit_flash_remaining <= 0.0:
\t\treturn false
\treturn int(floor(player_hit_flash_remaining / HIT_FLASH_INTERVAL)) % 2 == 0


func enemy_hit_flash_hidden(enemy: Dictionary) -> bool:
\tvar left := float(enemy.get("_hit_flash", 0.0))
\tif left <= 0.0:
\t\treturn false
\treturn int(floor(left / HIT_FLASH_INTERVAL)) % 2 == 0
'''
s=s.replace(helper_anchor,helpers+helper_anchor,1)

# Replace the chevron-like slash with an actual visible katana that swings
# around the ninja's hand. The player still keeps the STEP71 lunge.
new_sword='''func draw_melee_attack_effect(player_center: Vector2, tile_size: float) -> void:
\tif not melee_attack_anim_active:
\t\treturn
\tvar t := clampf(melee_attack_anim_elapsed / MELEE_ATTACK_ANIM_DURATION, 0.0, 1.0)
\tif t < 0.16 or t > 0.86:
\t\treturn
\tvar d := Vector2(melee_attack_anim_dir).normalized()
\tif d.length() < 0.5:
\t\treturn
\tvar swing_t := clampf((t - 0.16) / 0.70, 0.0, 1.0)
\t# Ease the blade through a broad 135-degree cut.
\tvar eased := 1.0 - pow(1.0 - swing_t, 3.0)
\tvar facing_angle := atan2(d.y, d.x)
\tvar blade_angle := facing_angle + lerpf(-1.35, 1.02, eased)
\tvar blade_dir := Vector2(cos(blade_angle), sin(blade_angle))
\tvar blade_n := Vector2(-blade_dir.y, blade_dir.x)
\tvar pivot := player_center + d * (tile_size * 0.13) + Vector2(0,-3)
\tvar grip_end := pivot + blade_dir * 7.0
\tvar blade_base := pivot + blade_dir * 9.0
\tvar blade_tip := pivot + blade_dir * 34.0
\t# Brown hilt + gold guard.
\tdraw_line(pivot - blade_dir * 4.0, grip_end, Color("#5b321d"), 5.0)
\tdraw_line(blade_base - blade_n * 6.0, blade_base + blade_n * 6.0, Color("#d8aa4c"), 3.0)
\t# Filled silver blade with a bright cutting edge, clearly sword-shaped.
\tvar blade_poly := PackedVector2Array([
\t\tblade_base + blade_n * 2.8,
\t\tblade_tip,
\t\tblade_base - blade_n * 2.8,
\t\tblade_base - blade_dir * 2.0
\t])
\tdraw_colored_polygon(blade_poly, Color("#d9e1e8"))
\tdraw_line(blade_base + blade_n * 1.5, blade_tip, Color("#ffffff"), 1.5)
\t# Curved after-trail follows the sword instead of forming a > mark.
\tif swing_t > 0.12 and swing_t < 0.88:
\t\tvar trail_from := facing_angle + lerpf(-1.35, 1.02, maxf(0.0, eased - 0.28))
\t\tdraw_arc(pivot, tile_size * 0.64, trail_from, blade_angle, 14, Color(1.0,0.84,0.42,0.58), 3.0)
\t# Small hit spark at the end of the forward half of the swing.
\tif swing_t >= 0.46 and swing_t <= 0.72:
\t\tvar hit_center := player_center + d * (tile_size * 0.70)
\t\tfor v in [Vector2(1,0),Vector2(-1,0),Vector2(0,1),Vector2(0,-1)]:
\t\t\tdraw_line(hit_center + v*3.0, hit_center + v*9.0, Color(1.0,0.82,0.32,0.88), 2.0)
'''
s,n=re.subn(r'func draw_melee_attack_effect\(player_center: Vector2, tile_size: float\) -> void:\n.*?(?=\n\nfunc attack_enemy)',new_sword.rstrip(),s,count=1,flags=re.S)
if n!=1:
    raise SystemExit(f'STEP72 sword function replace failed: {n}')

# Direct melee damage: surviving enemies blink.
old='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage
\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]'''
new='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage
\tstart_enemy_hit_flash(index)
\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]'''
if old not in s:
    raise SystemExit('STEP72 melee damage anchor failed')
s=s.replace(old,new,1)

# Projectile damage also flashes the enemy.
proj_old='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)
\tmessage = "%sが%sに命中。%dダメージ。" % [projectile_name, str(enemies[index]["name"]), max(1, damage)]'''
proj_new='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)
\tstart_enemy_hit_flash(index)
\tmessage = "%sが%sに命中。%dダメージ。" % [projectile_name, str(enemies[index]["name"]), max(1, damage)]'''
if proj_old not in s:
    raise SystemExit('STEP72 projectile damage anchor failed')
s=s.replace(proj_old,proj_new,1)

# Ultimate damage flashes any enemy that survives the hit.
ult_old='''\t\tif p.distance_to(player) <= 3.0:
\t\t\tenemies[i]["hp"] = int(enemies[i]["hp"]) - 25
\t\t\tif int(enemies[i]["hp"]) <= 0:'''
ult_new='''\t\tif p.distance_to(player) <= 3.0:
\t\t\tenemies[i]["hp"] = int(enemies[i]["hp"]) - 25
\t\t\tstart_enemy_hit_flash(i)
\t\t\tif int(enemies[i]["hp"]) <= 0:'''
if ult_old not in s:
    raise SystemExit('STEP72 ultimate damage anchor failed')
s=s.replace(ult_old,ult_new,1)

# Player blinks for combat damage from enemies and hostile merchant.
enemy_hit='''\thp -= dmg
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
enemy_hit_new='''\thp -= dmg
\tstart_player_hit_flash()
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
if enemy_hit not in s:
    raise SystemExit('STEP72 enemy attack anchor failed')
s=s.replace(enemy_hit,enemy_hit_new,1)

merchant='''\t\t\thp -= dmg
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
merchant_new='''\t\t\thp -= dmg
\t\t\tstart_player_hit_flash()
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
if merchant not in s:
    raise SystemExit('STEP72 merchant damage anchor failed')
s=s.replace(merchant,merchant_new,1)

# Starvation is still damage, so keep the feedback consistent.
hunger='''\tif hunger <= 0:
\t\thp -= 1
\t\tmessage = "空腹で1ダメージ。"'''
hunger_new='''\tif hunger <= 0:
\t\thp -= 1
\t\tstart_player_hit_flash()
\t\tmessage = "空腹で1ダメージ。"'''
if hunger not in s:
    raise SystemExit('STEP72 hunger damage anchor failed')
s=s.replace(hunger,hunger_new,1)

# Enemy sprite blink. Keep its ground ring visible so the occupied cell remains
# readable even during the brief invisible frames.
enemy_draw='''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep)
\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 17.0)'''
if enemy_draw not in s:
    enemy_draw=enemy_draw.replace('PTILE + 17.0','PTILE + 13.0')
enemy_draw_new='''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep)
\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tif not enemy_hit_flash_hidden(e):
\t\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 17.0)'''
if enemy_draw not in s:
    raise SystemExit('STEP72 enemy draw anchor failed')
s=s.replace(enemy_draw,enemy_draw_new,1)

# Player sprite blink while keeping the blue ground ring and sword animation.
player_old='''\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
player_new='''\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tif not player_hit_flash_hidden():
\t\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
if player_old not in s:
    raise SystemExit('STEP72 player draw anchor failed')
s=s.replace(player_old,player_new,1)

required=[
 'STEP72_SWORD_SWING_DAMAGE_BLINK_APPLIED',
 'draw_colored_polygon(blade_poly',
 'start_enemy_hit_flash(index)',
 'start_player_hit_flash()',
 'enemy_hit_flash_hidden(e)',
 'player_hit_flash_hidden()'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP72 verification failed: {needle}')
if s==original:
    raise SystemExit('STEP72 made no changes')

p.write_text(s,encoding='utf-8')
print('STEP72_SWORD_SWING_DAMAGE_BLINK PASS')
exec(Path('tools/apply_step73_ninjutsu_charge_pose.py').read_text(encoding='utf-8'), {})
