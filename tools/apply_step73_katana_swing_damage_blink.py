from pathlib import Path
import re

p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
original=s

if 'STEP73_KATANA_SWING_DAMAGE_BLINK_APPLIED' in s:
    print('STEP73_KATANA_SWING_DAMAGE_BLINK PASS (already applied)')
    raise SystemExit(0)

# Damage flash state. Enemy flash is stored on each enemy dictionary so it follows movement.
anchor='var melee_attack_anim_target := Vector2i(-999, -999)\n'
if anchor not in s:
    raise SystemExit('STEP73 state anchor failed')
s=s.replace(anchor, anchor+'''# STEP73_KATANA_SWING_DAMAGE_BLINK_APPLIED
const DAMAGE_FLASH_DURATION := 0.30
var player_damage_flash_remaining := 0.0
''',1)

# Replace the >-like slash polyline with an actual katana sweep.
a=s.find('func draw_melee_attack_effect(player_center: Vector2, tile_size: float) -> void:')
b=s.find('\n\nfunc attack_enemy(index: int) -> void:',a)
if a<0 or b<0:
    raise SystemExit('STEP73 melee effect bounds failed')
katana='''func draw_melee_attack_effect(player_center: Vector2, tile_size: float) -> void:
\tif not melee_attack_anim_active:
\t\treturn
\tvar t := clampf(melee_attack_anim_elapsed / MELEE_ATTACK_ANIM_DURATION, 0.0, 1.0)
\tif t < 0.12 or t > 0.90:
\t\treturn
\tvar facing := Vector2(melee_attack_anim_dir).normalized()
\tif facing.length() < 0.5:
\t\treturn
\t# A visible katana rotates through the target direction: raised blade -> cut -> follow-through.
\tvar sweep := clampf((t - 0.12) / 0.78, 0.0, 1.0)
\tvar swing_angle := lerpf(-1.30, 0.92, sweep)
\tvar blade_dir := facing.rotated(swing_angle).normalized()
\tvar side := Vector2(-facing.y, facing.x)
\tvar hand := player_center + facing * 5.0 + side * 2.0
\tvar guard := hand + blade_dir * 4.0
\tvar tip := guard + blade_dir * (tile_size * 0.70)
\tvar pommel := hand - blade_dir * 8.0
\tvar guard_side := Vector2(-blade_dir.y, blade_dir.x)
\t# Dark outline keeps the weapon readable over pale dungeon tiles.
\tdraw_line(pommel, guard, Color(0.08,0.06,0.05,1.0), 7.0)
\tdraw_line(pommel, guard, Color(0.34,0.18,0.08,1.0), 4.0)
\tdraw_line(guard - guard_side*7.0, guard + guard_side*7.0, Color(0.90,0.67,0.20,1.0), 5.0)
\tdraw_line(guard, tip, Color(0.10,0.12,0.16,1.0), 7.0)
\tdraw_line(guard, tip, Color(0.94,0.96,1.0,1.0), 4.0)
\tdraw_line(guard + guard_side*1.2, tip + guard_side*1.2, Color(0.70,0.86,1.0,0.95), 1.5)
\t# Short curved-looking after-trail during the fastest part of the swing.
\tif sweep >= 0.30 and sweep <= 0.72:
\t\tvar prev_dir := facing.rotated(swing_angle - 0.34).normalized()
\t\tvar trail_tip := guard + prev_dir * (tile_size * 0.62)
\t\tdraw_line(guard, trail_tip, Color(1.0,0.84,0.42,0.38), 3.0)
'''
s=s[:a]+katana+s[b:]

# Advance blink timers from _process.
m=re.search(r'func _process\(delta: float\) -> void:\n(.*?)(?=\n\nfunc _unhandled_key_input)',s,flags=re.S)
if not m:
    raise SystemExit('STEP73 process bounds failed')
body=m.group(1)
insert='''\tif player_damage_flash_remaining > 0.0:
\t\tplayer_damage_flash_remaining = maxf(0.0, player_damage_flash_remaining - delta)
\tfor enemy in enemies:
\t\tif float(enemy.get("damage_flash", 0.0)) > 0.0:
\t\t\tenemy["damage_flash"] = maxf(0.0, float(enemy.get("damage_flash", 0.0)) - delta)
'''
q=body.rfind('\tqueue_redraw()')
if q<0:
    raise SystemExit('STEP73 process redraw anchor failed')
body=body[:q]+insert+body[q:]
s=s[:m.start(1)]+body+s[m.end(1):]

# Enemy takes melee damage.
needle='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage
\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]'''
repl='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage
\tenemies[index]["damage_flash"] = DAMAGE_FLASH_DURATION
\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]'''
if needle not in s:
    raise SystemExit('STEP73 melee damage anchor failed')
s=s.replace(needle,repl,1)

# Enemy takes projectile damage.
needle='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)
\tmessage = "%sが%sに命中。%dダメージ。" % [projectile_name, str(enemies[index]["name"]), max(1, damage)]'''
repl='''\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)
\tenemies[index]["damage_flash"] = DAMAGE_FLASH_DURATION
\tmessage = "%sが%sに命中。%dダメージ。" % [projectile_name, str(enemies[index]["name"]), max(1, damage)]'''
if needle not in s:
    raise SystemExit('STEP73 projectile damage anchor failed')
s=s.replace(needle,repl,1)

# Ultimate damage also flashes surviving enemies.
needle='''\t\t\tenemies[i]["hp"] = int(enemies[i]["hp"]) - 25
\t\t\tif int(enemies[i]["hp"]) <= 0:'''
repl='''\t\t\tenemies[i]["hp"] = int(enemies[i]["hp"]) - 25
\t\t\tenemies[i]["damage_flash"] = DAMAGE_FLASH_DURATION
\t\t\tif int(enemies[i]["hp"]) <= 0:'''
if needle in s:
    s=s.replace(needle,repl,1)

# Player damage: enemy, merchant, and hunger all trigger the same Torneko-like blink.
needle='''\thp -= dmg
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
repl='''\thp -= dmg
\tplayer_damage_flash_remaining = DAMAGE_FLASH_DURATION
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]'''
if needle not in s:
    raise SystemExit('STEP73 enemy attack anchor failed')
s=s.replace(needle,repl,1)

needle='''\t\t\thp -= dmg
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
repl='''\t\t\thp -= dmg
\t\t\tplayer_damage_flash_remaining = DAMAGE_FLASH_DURATION
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
if needle in s:
    s=s.replace(needle,repl,1)

needle='''\t\thp -= 1
\t\tmessage = "空腹で1ダメージ。"'''
repl='''\t\thp -= 1
\t\tplayer_damage_flash_remaining = DAMAGE_FLASH_DURATION
\t\tmessage = "空腹で1ダメージ。"'''
if needle in s:
    s=s.replace(needle,repl,1)

# Blink by skipping the character sprite on alternating ~50 ms phases.
enemy_old='''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar ec := portrait_cell_center(ep)
\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 14.0)'''
if enemy_old not in s:
    enemy_old=enemy_old.replace('PTILE + 14.0','PTILE + 10.0')
enemy_new='''\tfor e in enemies:
\t\tvar ep: Vector2i = e["pos"]
\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):
\t\t\tvar enemy_flash := float(e.get("damage_flash", 0.0))
\t\t\tvar enemy_hidden_by_flash := enemy_flash > 0.0 and int(enemy_flash * 20.0) % 2 == 0
\t\t\tif not enemy_hidden_by_flash:
\t\t\t\tvar ec := portrait_cell_center(ep)
\t\t\t\tdraw_arc(ec + Vector2(0,15), 16.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)
\t\t\t\tdraw_enemy_reference_visual(ec, e, PTILE + 14.0)'''
if enemy_old not in s:
    raise SystemExit('STEP73 enemy draw anchor failed')
s=s.replace(enemy_old,enemy_new,1)

player_old='''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tvar attack_offset := melee_attack_visual_offset()
\t\tvar visual_pc := pc + attack_offset
\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
player_new='''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tvar attack_offset := melee_attack_visual_offset()
\t\tvar visual_pc := pc + attack_offset
\t\tvar player_hidden_by_flash := player_damage_flash_remaining > 0.0 and int(player_damage_flash_remaining * 20.0) % 2 == 0
\t\tif not player_hidden_by_flash:
\t\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
if player_old not in s:
    raise SystemExit('STEP73 player draw anchor failed')
s=s.replace(player_old,player_new,1)

required=[
 'STEP73_KATANA_SWING_DAMAGE_BLINK_APPLIED',
 'var swing_angle := lerpf(-1.30, 0.92, sweep)',
 'player_damage_flash_remaining = DAMAGE_FLASH_DURATION',
 'enemies[index]["damage_flash"] = DAMAGE_FLASH_DURATION',
 'enemy_hidden_by_flash',
 'player_hidden_by_flash'
]
for x in required:
    if x not in s:
        raise SystemExit('STEP73 verification failed: '+x)
if s==original:
    raise SystemExit('STEP73 made no changes')

p.write_text(s,encoding='utf-8')
print('STEP73_KATANA_SWING_DAMAGE_BLINK PASS')
