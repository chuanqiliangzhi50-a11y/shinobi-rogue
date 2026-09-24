from pathlib import Path
import re

p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
original=s

if 'STEP73_NINJUTSU_CHARGE_POSE_APPLIED' in s:
    print('STEP73_NINJUTSU_CHARGE_POSE PASS (already applied)')
    raise SystemExit(0)

# Footstep/healing keeps the same turn mechanics, but is presented as a
# stationary ninja hand-seal / chakra charging pose.
marker='const HIT_FLASH_DURATION := 0.24\n'
if marker not in s:
    raise SystemExit('STEP73 STEP72 state anchor failed')
s=s.replace(marker, '# STEP73_NINJUTSU_CHARGE_POSE_APPLIED\n'+marker, 1)

old_msg='message = "その場で足踏みしている。"'
if old_msg not in s:
    raise SystemExit('STEP73 footstep message anchor failed')
s=s.replace(old_msg, 'message = "印を結び、忍気を練っている。"', 1)

helper_anchor='\n\nfunc draw_melee_attack_effect(player_center: Vector2, tile_size: float) -> void:\n'
if helper_anchor not in s:
    raise SystemExit('STEP73 draw helper anchor failed')
helpers='''

func ninjutsu_charge_active() -> bool:
\treturn center_hold_active and center_hold_stepping and not melee_attack_anim_active


func ninjutsu_charge_bob() -> Vector2:
\tif not ninjutsu_charge_active():
\t\treturn Vector2.ZERO
\tvar phase := Time.get_ticks_msec() * 0.010
\treturn Vector2(0.0, sin(phase) * 1.6)


func draw_ninjutsu_charge_pose(center: Vector2, tile_size: float) -> void:
\tif not ninjutsu_charge_active():
\t\treturn
\tvar phase := Time.get_ticks_msec() * 0.010
\tvar pulse := 0.5 + 0.5 * sin(phase)
\t# Chakra rings: quiet, pulsing blue-violet energy around the stationary ninja.
\tdraw_arc(center + Vector2(0,5), tile_size * (0.42 + pulse*0.05), 0.0, TAU, 40, Color(0.34,0.67,1.0,0.32 + pulse*0.20), 2.5)
\tdraw_arc(center + Vector2(0,5), tile_size * (0.31 + (1.0-pulse)*0.04), 0.0, TAU, 36, Color(0.60,0.42,1.0,0.24 + (1.0-pulse)*0.18), 2.0)
\t# Hands meet at the chest to read as a ninja hand seal even on a small phone.
\tvar hand_y := center.y + 2.0
\tdraw_circle(Vector2(center.x-4.0, hand_y), 4.2, Color("#d7aa7c"))
\tdraw_circle(Vector2(center.x+4.0, hand_y), 4.2, Color("#d7aa7c"))
\tdraw_rect(Rect2(center.x-2.0, hand_y-7.0, 4.0, 14.0), Color("#f0c79a"), true)
\tdraw_line(Vector2(center.x,hand_y-8.0), Vector2(center.x,hand_y+7.0), Color(1.0,0.92,0.72,0.90), 1.5)
\t# Small rising chakra motes reinforce that this replaces the old footstep pose.
\tfor i in range(3):
\t\tvar a := phase + float(i) * 2.1
\t\tvar mote := center + Vector2(cos(a)*18.0, 12.0 - fmod(phase*7.0 + float(i)*13.0, 34.0))
\t\tdraw_circle(mote, 2.0, Color(0.45,0.78,1.0,0.72))
'''
s=s.replace(helper_anchor, helpers+helper_anchor, 1)

# STEP72 player draw is the final player rendering block in the patch chain.
old_player='''\t\tvar attack_offset := melee_attack_visual_offset()
\t\tvar visual_pc := pc + attack_offset
\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tif not player_hit_flash_hidden():
\t\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
new_player='''\t\tvar attack_offset := melee_attack_visual_offset()
\t\tvar charge_offset := ninjutsu_charge_bob()
\t\tvar visual_pc := pc + attack_offset + charge_offset
\t\tdraw_arc(visual_pc + Vector2(0,16), 17.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tif not player_hit_flash_hidden():
\t\t\tdraw_player_facing_visual(visual_pc, PTILE + 17.0)
\t\tdraw_ninjutsu_charge_pose(visual_pc, PTILE)
\t\tdraw_melee_attack_effect(pc, PTILE)'''
if old_player not in s:
    raise SystemExit('STEP73 player draw anchor failed')
s=s.replace(old_player,new_player,1)

required=[
 'STEP73_NINJUTSU_CHARGE_POSE_APPLIED',
 '印を結び、忍気を練っている。',
 'func ninjutsu_charge_active()',
 'func draw_ninjutsu_charge_pose',
 'draw_ninjutsu_charge_pose(visual_pc, PTILE)'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP73 verification failed: {needle}')
if s==original:
    raise SystemExit('STEP73 made no changes')

p.write_text(s,encoding='utf-8')
print('STEP73_NINJUTSU_CHARGE_POSE PASS')
exec(Path('tools/apply_step74_enemy_attack_motion.py').read_text(encoding='utf-8'), {})
