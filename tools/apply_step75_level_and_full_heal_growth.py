from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP75_LEVEL_FULL_HEAL_GROWTH_APPLIED" in s:
    print("STEP75_LEVEL_FULL_HEAL_GROWTH PASS (already applied)")
    raise SystemExit(0)

if "const RUN_SAVE_VERSION := 7" not in s:
    raise SystemExit("STEP75 save version anchor failed")
s = s.replace("const RUN_SAVE_VERSION := 7", "const RUN_SAVE_VERSION := 8", 1)

marker = "# STEP74_ENEMY_ATTACK_MOTION_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP75 STEP74 state anchor failed")
s = s.replace(
    marker,
    marker
    + "# STEP75_LEVEL_FULL_HEAL_GROWTH_APPLIED\n"
    + "const MAX_RUN_LEVEL := 50\n",
    1,
)

state_anchor = 'var style_name := "武"\n'
if state_anchor not in s:
    raise SystemExit("STEP75 player state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + "var player_level := 1\n"
    + "var player_exp := 0\n"
    + 'var level_up_notice := ""\n',
    1,
)

helper_anchor = "\n\nfunc attack_enemy(index: int) -> void:\n"
if helper_anchor not in s:
    raise SystemExit("STEP75 attack helper anchor failed")
helpers = '''

func exp_needed_for_next_level() -> int:
\treturn 8 + player_level * player_level * 4


func enemy_exp_reward(defeated: Dictionary) -> int:
\tif defeated.has("exp_reward"):
\t\treturn maxi(1, int(defeated["exp_reward"]))
\tvar reward := 2 + int(floor_no / 3)
\tif bool(defeated.get("boss", false)):
\t\treward = reward * 5 + 10
\treturn maxi(1, reward)


func gain_enemy_exp(defeated: Dictionary) -> void:
\tif player_level >= MAX_RUN_LEVEL:
\t\tplayer_exp = 0
\t\treturn
\tplayer_exp += enemy_exp_reward(defeated)
\tvar gained_levels := 0
\twhile player_level < MAX_RUN_LEVEL and player_exp >= exp_needed_for_next_level():
\t\tplayer_exp -= exp_needed_for_next_level()
\t\tplayer_level += 1
\t\tgained_levels += 1
\t\tmax_hp += 3
\t\thp = mini(max_hp, hp + 3)
\t\tattack_power += 1
\t\tif player_level % 3 == 0:
\t\t\tdefense_power += 1
\tif player_level >= MAX_RUN_LEVEL:
\t\tplayer_exp = 0
\tif gained_levels > 0:
\t\tlevel_up_notice += " Lv.%d!" % player_level
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

attack_start = '''func attack_enemy(index: int) -> void:
\tif index < 0 or index >= enemies.size():
\t\treturn
\tvar damage = max(1, attack_power + rng.randi_range(0, 2))'''
attack_start_new = '''func attack_enemy(index: int) -> void:
\tif index < 0 or index >= enemies.size():
\t\treturn
\tlevel_up_notice = ""
\tvar damage = max(1, attack_power + rng.randi_range(0, 2))'''
if attack_start not in s:
    raise SystemExit("STEP75 melee start anchor failed")
s = s.replace(attack_start, attack_start_new, 1)

melee_reward = '''\t\tknown_enemies[name] = int(known_enemies.get(name, 0)) + 1
\t\tif was_boss:
\t\t\tboss_defeated = true
\t\t\tmessage = "ボスを討ち取った。階段が使える。"
\t\telse:
\t\t\tmessage = "%sを倒した。" % name'''
melee_reward_new = '''\t\tgain_enemy_exp(defeated)
\t\tknown_enemies[name] = int(known_enemies.get(name, 0)) + 1
\t\tif was_boss:
\t\t\tboss_defeated = true
\t\t\tmessage = "ボスを討ち取った。階段が使える。"
\t\telse:
\t\t\tmessage = "%sを倒した。" % name
\t\tmessage += level_up_notice'''
if melee_reward not in s:
    raise SystemExit("STEP75 melee reward anchor failed")
s = s.replace(melee_reward, melee_reward_new, 1)

projectile_start = '''func damage_enemy_with_projectile(index: int, damage: int, projectile_name: String) -> void:
\tif index < 0 or index >= enemies.size(): return
\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)'''
projectile_start_new = '''func damage_enemy_with_projectile(index: int, damage: int, projectile_name: String) -> void:
\tif index < 0 or index >= enemies.size(): return
\tlevel_up_notice = ""
\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)'''
if projectile_start not in s:
    raise SystemExit("STEP75 projectile start anchor failed")
s = s.replace(projectile_start, projectile_start_new, 1)

projectile_reward = '''\t\tknown_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1; enemies.remove_at(index); ninja_energy = min(100, ninja_energy + (20 if was_boss else 8))
\t\tif was_boss: boss_defeated = true
\t\tmessage = "%sを倒した。" % defeated_name'''
projectile_reward_new = '''\t\tgain_enemy_exp(defeated)
\t\tknown_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1; enemies.remove_at(index); ninja_energy = min(100, ninja_energy + (20 if was_boss else 8))
\t\tif was_boss: boss_defeated = true
\t\tmessage = "%sを倒した。" % defeated_name + level_up_notice'''
if projectile_reward not in s:
    raise SystemExit("STEP75 projectile reward anchor failed")
s = s.replace(projectile_reward, projectile_reward_new, 1)

ultimate_start = '''\tninja_energy = 0
\tfor i in range(enemies.size() - 1, -1, -1):'''
ultimate_start_new = '''\tninja_energy = 0
\tlevel_up_notice = ""
\tfor i in range(enemies.size() - 1, -1, -1):'''
if ultimate_start not in s:
    raise SystemExit("STEP75 ultimate start anchor failed")
s = s.replace(ultimate_start, ultimate_start_new, 1)

ultimate_reward = '''\t\t\t\tknown_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1
\t\t\t\tenemies.remove_at(i)'''
ultimate_reward_new = '''\t\t\t\tgain_enemy_exp(defeated)
\t\t\t\tknown_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1
\t\t\t\tenemies.remove_at(i)'''
if ultimate_reward not in s:
    raise SystemExit("STEP75 ultimate reward anchor failed")
s = s.replace(ultimate_reward, ultimate_reward_new, 1)
s = s.replace(
    '\tmessage = "奥義・影滅！"\n\tend_turn()',
    '\tmessage = "奥義・影滅！" + level_up_notice\n\tend_turn()',
    1,
)

old_items = '''\tif name == "薬":
\t\thp = min(max_hp, hp + 10)
\t\tmessage = "薬でHPを回復した。"
\telif name == "兵糧丸":'''
new_items = '''\tif name == "薬":
\t\tif hp >= max_hp:
\t\t\tmax_hp += 1
\t\t\thp = max_hp
\t\t\tmessage = "薬で最大HP+1。"
\t\telse:
\t\t\thp = min(max_hp, hp + 10)
\t\t\tmessage = "薬でHPを回復した。"
\telif name == "兵糧丸":'''
if old_items not in s:
    raise SystemExit("STEP75 medicine anchor failed")
s = s.replace(old_items, new_items, 1)

old_upper = '''\telif name == "上薬":
\t\thp = min(max_hp, hp + 25)
\t\tmessage = "上薬でHPを大きく回復した。"'''
new_upper = '''\telif name == "上薬":
\t\tif hp >= max_hp:
\t\t\tmax_hp += 2
\t\t\thp = max_hp
\t\t\tmessage = "上薬で最大HP+2。"
\t\telse:
\t\t\thp = min(max_hp, hp + 25)
\t\t\tmessage = "上薬でHPを大きく回復した。"'''
if old_upper not in s:
    raise SystemExit("STEP75 upper medicine anchor failed")
s = s.replace(old_upper, new_upper, 1)

start_anchor = '''\tstyle_name = "武"
\tsmoke_turns = 0'''
start_new = '''\tstyle_name = "武"
\tplayer_level = 1
\tplayer_exp = 0
\tlevel_up_notice = ""
\tsmoke_turns = 0'''
if start_anchor not in s:
    raise SystemExit("STEP75 start run anchor failed")
s = s.replace(start_anchor, start_new, 1)

save_anchor = '''\t\t"turn_no": turn_no,
\t\t"player": player,'''
save_new = '''\t\t"turn_no": turn_no,
\t\t"player_level": player_level,
\t\t"player_exp": player_exp,
\t\t"player": player,'''
if save_anchor not in s:
    raise SystemExit("STEP75 save fields anchor failed")
s = s.replace(save_anchor, save_new, 1)

load_anchor = '''\tfloor_no = clamp(int(data.get("floor_no", 1)), 1, 100)
\tturn_no = max(0, int(data.get("turn_no", 0)))
\tplayer = data["player"]'''
load_new = '''\tfloor_no = clamp(int(data.get("floor_no", 1)), 1, 100)
\tturn_no = max(0, int(data.get("turn_no", 0)))
\tplayer_level = clampi(int(data.get("player_level", 1)), 1, MAX_RUN_LEVEL)
\tplayer_exp = maxi(0, int(data.get("player_exp", 0)))
\tif player_level >= MAX_RUN_LEVEL:
\t\tplayer_exp = 0
\tlevel_up_notice = ""
\tplayer = data["player"]'''
if load_anchor not in s:
    raise SystemExit("STEP75 load fields anchor failed")
s = s.replace(load_anchor, load_new, 1)

save_contract_old = '''var required = ["player", "stairs_pos", "map", "explored", "enemies", "items", "inventory_items", "placed_traps", "unpaid_items", "merchant_bound_turns", "clone_active", "clone_pos", "clone_steps_left", "merchant_type", "last_ad_checkpoint_floor"]'''
save_contract_new = '''var required = ["player", "player_level", "player_exp", "stairs_pos", "map", "explored", "enemies", "items", "inventory_items", "placed_traps", "unpaid_items", "merchant_bound_turns", "clone_active", "clone_pos", "clone_steps_left", "merchant_type", "last_ad_checkpoint_floor"]'''
if save_contract_old not in s:
    raise SystemExit("STEP75 save contract regression anchor failed")
s = s.replace(save_contract_old, save_contract_new, 1)

s = s.replace(
    'draw_ui_text(Vector2(38,177), "迷いの里", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#4b3524"))',
    'draw_ui_text(Vector2(38,177), "Lv.%d" % player_level, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("#4b3524"))',
    1,
)
old_status = '''draw_ui_text(Vector2(132,180), "✦ 忍道:%s  ｜  銭 %d(+%d)  ｜  忍魂 %d(+%d)  ｜  T%d" % [style_name,coins,run_coins,souls,run_souls,turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ddd5c5"))'''
new_status = '''draw_ui_text(Vector2(132,180), "✦ 忍道:%s ｜ EXP %d/%d ｜ 銭 %d(+%d) ｜ T%d" % [style_name,player_exp,exp_needed_for_next_level(),coins,run_coins,turn_no], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("#ddd5c5"))'''
if old_status not in s:
    raise SystemExit("STEP75 HUD anchor failed")
s = s.replace(old_status, new_status, 1)

test_anchor = "\n\nfunc debug_test_ui_glyph_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP75 regression anchor failed")
test_func = '''

func debug_test_level_and_full_heal_growth() -> String:
\tvar old_level := player_level
\tvar old_exp := player_exp
\tvar old_hp := hp
\tvar old_max_hp := max_hp
\tvar old_attack := attack_power
\tvar old_defense := defense_power
\tvar old_notice := level_up_notice
\tplayer_level = 1
\tplayer_exp = 0
\tmax_hp = 30
\thp = 30
\tattack_power = 5
\tdefense_power = 1
\tlevel_up_notice = ""
\tgain_enemy_exp({"boss": false, "exp_reward": exp_needed_for_next_level()})
\tvar level_ok := player_level == 2 and max_hp == 33 and attack_power == 6
\thp = max_hp
\tvar before_medicine := max_hp
\tapply_item_effect("薬")
\tvar medicine_ok := max_hp == before_medicine + 1 and hp == max_hp
\tvar before_upper := max_hp
\tapply_item_effect("上薬")
\tvar upper_ok := max_hp == before_upper + 2 and hp == max_hp
\tplayer_level = old_level
\tplayer_exp = old_exp
\thp = old_hp
\tmax_hp = old_max_hp
\tattack_power = old_attack
\tdefense_power = old_defense
\tlevel_up_notice = old_notice
\treturn "PASS LV薬成長" if level_ok and medicine_ok and upper_ok else "FAIL LV薬成長"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)

suite_anchor = '''\t\tdebug_test_research_contract(),
\t\tdebug_test_ui_glyph_contract()'''
suite_new = '''\t\tdebug_test_research_contract(),
\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_ui_glyph_contract()'''
if suite_anchor not in s:
    raise SystemExit("STEP75 regression suite anchor failed")
s = s.replace(suite_anchor, suite_new, 1)

required = [
    "STEP75_LEVEL_FULL_HEAL_GROWTH_APPLIED",
    "const RUN_SAVE_VERSION := 8",
    "func gain_enemy_exp",
    'message = "薬で最大HP+1。"',
    'message = "上薬で最大HP+2。"',
    '"player_level": player_level',
    '"player_exp": player_exp',
    "debug_test_level_and_full_heal_growth()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP75 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP75 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP75_LEVEL_FULL_HEAL_GROWTH PASS")
