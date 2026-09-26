from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP80_EQUIPMENT_ARSENAL_APPLIED" in s:
    print("STEP80_EQUIPMENT_ARSENAL PASS (already applied)")
    raise SystemExit(0)

s = s.replace("const RUN_SAVE_VERSION := 8", "const RUN_SAVE_VERSION := 9", 1)

marker = "# STEP79_VILLAGE_BOTTOM_CHOICES_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP80 STEP79 anchor failed")
catalogs = '''# STEP80_EQUIPMENT_ARSENAL_APPLIED
const WEAPON_CATALOG := {
\t"忍刀": {"design_id":"weapon_01", "kind":"katana", "attack":7, "rarity":1, "floor":1, "hits":1, "native_effects":[], "price":100},
\t"双牙刀": {"design_id":"weapon_02", "kind":"katana", "attack":8, "rarity":2, "floor":8, "hits":2, "native_effects":["double_strike"], "price":240},
\t"影斬刀": {"design_id":"weapon_03", "kind":"katana", "attack":10, "rarity":4, "floor":32, "hits":3, "native_effects":["triple_strike"], "price":760},
\t"疾風槍": {"design_id":"weapon_04", "kind":"spear", "attack":6, "rarity":2, "floor":5, "range":2, "native_effects":["reach_2"], "price":180},
\t"三方向槍": {"design_id":"weapon_05", "kind":"spear", "attack":7, "rarity":3, "floor":20, "range":2, "spread":true, "native_effects":["reach_2","front_three"], "price":430},
\t"破軍槍": {"design_id":"weapon_06", "kind":"spear", "attack":9, "rarity":4, "floor":35, "range":3, "pierce":true, "knockback":true, "native_effects":["reach_3","pierce_3","knockback"], "price":820},
\t"鎖鎌": {"design_id":"weapon_07", "kind":"chain", "attack":3, "rarity":2, "floor":10, "min_range":3, "max_range":5, "native_effects":["random_range"], "price":210},
\t"乱舞鎖鎌": {"design_id":"weapon_08", "kind":"chain", "attack":4, "rarity":3, "floor":24, "min_range":3, "max_range":5, "spread":true, "native_effects":["random_range","wide_slash"], "price":470},
\t"天網鎖鎌": {"design_id":"weapon_09", "kind":"chain", "attack":5, "rarity":4, "floor":40, "min_range":3, "max_range":5, "omni":true, "native_effects":["random_range","all_direction"], "price":880},
\t"鉤爪": {"design_id":"weapon_10", "kind":"hook", "attack":1, "rarity":3, "floor":15, "range":6, "native_effects":["pull_6"], "price":520},
\t"忍手裏剣": {"design_id":"weapon_11", "kind":"shuriken", "attack":4, "rarity":2, "floor":12, "range":8, "native_effects":["ranged_throw"], "price":260}
}
const ARMOR_CATALOG := {
\t"忍装束": {"design_id":"armor_01", "defense":1, "rarity":1, "floor":1, "effect":"none", "price":70},
\t"軽忍装束": {"design_id":"armor_02", "defense":1, "rarity":2, "floor":5, "effect":"dodge8", "price":150},
\t"鉄忍装束": {"design_id":"armor_03", "defense":3, "rarity":2, "floor":10, "effect":"cut1", "price":240},
\t"影縫い装束": {"design_id":"armor_04", "defense":2, "rarity":3, "floor":18, "effect":"dodge15", "price":380},
\t"疾風の羽織": {"design_id":"armor_05", "defense":2, "rarity":3, "floor":25, "effect":"dodge12", "price":470},
\t"月影の鎧": {"design_id":"armor_06", "defense":4, "rarity":4, "floor":32, "effect":"regen", "price":650},
\t"黒鋼の重鎧": {"design_id":"armor_07", "defense":7, "rarity":4, "floor":42, "effect":"cut3", "price":920},
\t"霧隠れ頭巾": {"design_id":"armor_08", "defense":2, "rarity":4, "floor":48, "effect":"dodge20", "price":980}
}
const VILLAGE_SHOP_VISIBLE_ROWS := 9
'''
s = s.replace(marker, marker + catalogs, 1)

glyph_anchor = '\t"ル": "res://art/step76_glyphs/u30eb.svg"\n}'
glyph_extra = '''\t"ル": "res://art/step76_glyphs/u30eb.svg",
\t"走": "res://art/step76_glyphs/u8d70.svg",
\t"疾": "res://art/step76_glyphs/u75be.svg",
\t"修": "res://art/step76_glyphs/u4fee.svg",
\t"葉": "res://art/step76_glyphs/u8449.svg",
\t"雷": "res://art/step76_glyphs/u96f7.svg",
\t"天": "res://art/step76_glyphs/u5929.svg",
\t"鎖": "res://art/step76_glyphs/u9396.svg",
\t"毒": "res://art/step76_glyphs/u6bd2.svg",
\t"月": "res://art/step76_glyphs/u6708.svg",
\t"鉤": "res://art/step76_glyphs/u9264.svg",
\t"癒": "res://art/step76_glyphs/u7652.svg",
\t"守": "res://art/step76_glyphs/u5b88.svg",
\t"返": "res://art/step76_glyphs/u8fd4.svg",
\t"剛": "res://art/step76_glyphs/u525b.svg",
\t"体": "res://art/step76_glyphs/u4f53.svg",
\t"連": "res://art/step76_glyphs/u9023.svg",
\t"会": "res://art/step76_glyphs/u4f1a.svg",
\t"低": "res://art/step76_glyphs/u4f4e.svg",
\t"反": "res://art/step76_glyphs/u53cd.svg",
\t"器": "res://art/step76_glyphs/u5668.svg",
\t"寄": "res://art/step76_glyphs/u5bc4.svg",
\t"風": "res://art/step76_glyphs/u98a8.svg",
\t"羅": "res://art/step76_glyphs/u7f85.svg",
\t"槍": "res://art/step76_glyphs/u69cd.svg",
\t"鳴": "res://art/step76_glyphs/u9cf4.svg",
\t"穿": "res://art/step76_glyphs/u7a7f.svg",
\t"鎌": "res://art/step76_glyphs/u938c.svg",
\t"牙": "res://art/step76_glyphs/u7259.svg",
\t"輪": "res://art/step76_glyphs/u8f2a.svg",
\t"爪": "res://art/step76_glyphs/u722a.svg",
\t"帷": "res://art/step76_glyphs/u5e37.svg",
\t"同": "res://art/step76_glyphs/u540c.svg",
\t"心": "res://art/step76_glyphs/u5fc3.svg",
\t"下": "res://art/step76_glyphs/u4e0b.svg",
\t"せ": "res://art/step76_glyphs/u305b.svg",
\t"二": "res://art/step76_glyphs/u4e8c.svg",
\t"三": "res://art/step76_glyphs/u4e09.svg",
\t"捉": "res://art/step76_glyphs/u6349.svg",
\t"場": "res://art/step76_glyphs/u5834.svg",
\t"先": "res://art/step76_glyphs/u5148.svg",
\t"叉": "res://art/step76_glyphs/u53c9.svg",
\t"制": "res://art/step76_glyphs/u5236.svg"
}'''
if glyph_anchor not in s:
    raise SystemExit("STEP80 glyph map anchor failed")
s = s.replace(glyph_anchor, glyph_extra, 1)

state_anchor = 'var equipped_projectile := ""\n'
if state_anchor not in s:
    raise SystemExit("STEP80 equipment state anchor failed")
s = s.replace(state_anchor, state_anchor + 'var equipped_weapon := "忍刀"\nvar equipped_armor := "忍装束"\nvar village_shop_scroll_offset := 0\n', 1)

helper_anchor = "\n\nfunc try_move(dir: Vector2i) -> void:\n"
if helper_anchor not in s:
    raise SystemExit("STEP80 movement helper anchor failed")
helpers = '''

func is_weapon_name(name: String) -> bool:
\treturn WEAPON_CATALOG.has(name)


func is_armor_name(name: String) -> bool:
\treturn ARMOR_CATALOG.has(name)


func is_equipment_name(name: String) -> bool:
\treturn is_weapon_name(name) or is_armor_name(name)


func equipped_weapon_data() -> Dictionary:
\treturn WEAPON_CATALOG.get(equipped_weapon, WEAPON_CATALOG["忍刀"])


func equipped_armor_data() -> Dictionary:
\treturn ARMOR_CATALOG.get(equipped_armor, ARMOR_CATALOG["忍装束"])


func equipment_display_name(name: String) -> String:
\tvar data: Dictionary = WEAPON_CATALOG.get(name, ARMOR_CATALOG.get(name, {}))
\treturn "%s R%d" % [name, int(data.get("rarity", 1))]


func weapon_attack_bonus() -> int:
\treturn int(equipped_weapon_data().get("attack", 0))


func armor_defense_bonus() -> int:
\treturn int(equipped_armor_data().get("defense", 0))


func all_attack_dirs() -> Array[Vector2i]:
\treturn [Vector2i(0,-1), Vector2i(1,-1), Vector2i(1,0), Vector2i(1,1), Vector2i(0,1), Vector2i(-1,1), Vector2i(-1,0), Vector2i(-1,-1)]


func front_spread_dirs(dir: Vector2i) -> Array[Vector2i]:
\tvar dirs := all_attack_dirs()
\tvar normalized := Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))
\tvar center := dirs.find(normalized)
\tif center < 0: return [Vector2i(0, 1)]
\treturn [dirs[(center + 7) % 8], dirs[center], dirs[(center + 1) % 8]]


func first_enemy_on_line(dir: Vector2i, min_range: int, max_range: int) -> Vector2i:
\tfor step in range(1, max_range + 1):
\t\tvar p2 := player + dir * step
\t\tif not position_in_bounds(p2) or not is_walkable(p2): break
\t\tif step >= min_range and enemy_index_at(p2) >= 0: return p2
\treturn Vector2i(-1, -1)


func try_weapon_reach_attack(dir: Vector2i) -> bool:
\tvar data := equipped_weapon_data()
\tvar kind := str(data.get("kind", "katana"))
\tif kind != "spear" and kind != "chain": return false
\tvar targets: Array[Vector2i] = []
\tif kind == "spear":
\t\tvar dirs: Array[Vector2i] = front_spread_dirs(dir) if bool(data.get("spread", false)) else [dir]
\t\tfor attack_dir in dirs:
\t\t\tvar target_pos := first_enemy_on_line(attack_dir, 1, int(data.get("range", 2)))
\t\t\tif target_pos != Vector2i(-1, -1) and target_pos not in targets: targets.append(target_pos)
\telse:
\t\tvar reach := rng.randi_range(int(data.get("min_range", 3)), int(data.get("max_range", 5)))
\t\tvar dirs: Array[Vector2i] = all_attack_dirs() if bool(data.get("omni", false)) else [dir]
\t\tfor attack_dir in dirs:
\t\t\tvar target_pos := first_enemy_on_line(attack_dir, int(data.get("min_range", 3)), reach)
\t\t\tif target_pos != Vector2i(-1, -1) and target_pos not in targets: targets.append(target_pos)
\tif targets.is_empty(): return false
\tstart_melee_attack_animation(dir, targets[0])
\tfor target_pos in targets:
\t\tvar index := enemy_index_at(target_pos)
\t\tif index >= 0: attack_enemy(index)
\tif targets.size() > 1: message += " %d体同時攻撃。" % targets.size()
\treturn true
'''
s = s.replace(helper_anchor, helpers + helper_anchor, 1)

move_anchor = '''\tfacing_dir = Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))
\tvar target = player + dir'''
move_new = '''\tfacing_dir = Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))
\tif try_weapon_reach_attack(facing_dir):
\t\tskip_auto_pickup_once = false
\t\tend_turn()
\t\treturn
\tvar target = player + dir'''
if move_anchor not in s:
    raise SystemExit("STEP80 reach attack movement anchor failed")
s = s.replace(move_anchor, move_new, 1)

attack_anchor = "func attack_enemy(index: int) -> void:\n"
if attack_anchor not in s:
    raise SystemExit("STEP80 attack function anchor failed")
attack_wrapper = '''func attack_enemy(index: int) -> void:
\tif index < 0 or index >= enemies.size(): return
\tvar target_pos: Vector2i = enemies[index]["pos"]
\tvar requested_hits := maxi(1, int(equipped_weapon_data().get("hits", 1)))
\tvar actual_hits := 0
\tfor _hit in range(requested_hits):
\t\tvar current_index := enemy_index_at(target_pos)
\t\tif current_index < 0: break
\t\tattack_enemy_single(current_index)
\t\tactual_hits += 1
\tif actual_hits >= 2: message += " %d連撃。" % actual_hits


func attack_enemy_single(index: int) -> void:
'''
s = s.replace(attack_anchor, attack_wrapper, 1)

damage_anchor = '''\tvar damage = max(1, attack_power + rng.randi_range(0, 2))
\tif style_name == "武":
\t\tdamage += 2
\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage'''
damage_new = '''\tvar weapon_data := equipped_weapon_data()
\tvar damage = max(1, attack_power + weapon_attack_bonus() + rng.randi_range(0, 2))
\tif style_name == "武": damage += 2
\tvar critical := int(weapon_data.get("critical", 0)) > 0 and rng.randi_range(1, 100) <= int(weapon_data.get("critical", 0))
\tif critical: damage *= 2
\tenemies[index]["hp"] = int(enemies[index]["hp"]) - damage
\tif bool(weapon_data.get("weaken", false)) and int(enemies[index]["hp"]) > 0:
\t\tenemies[index]["atk"] = maxi(1, int(enemies[index].get("atk", 1)) - 1)'''
if damage_anchor not in s:
    raise SystemExit("STEP80 weapon damage anchor failed")
s = s.replace(damage_anchor, damage_new, 1)
s = s.replace(
    '''\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]''',
    '''\tmessage = "%sに%dダメージ。" % [str(enemies[index]["name"]), damage]
\tif critical: message += " 会心。"
\tif bool(weapon_data.get("weaken", false)) and int(enemies[index]["hp"]) > 0: message += " 攻撃低下。"''',
    1,
)

hunger_anchor = '''\thunger_tick += 1
\tif hunger_tick >= 10:
\t\thunger_tick = 0
\t\thunger = max(0, hunger - 1)'''
hunger_new = '''\thunger_tick += 1
\tvar hunger_limit := 20 if str(equipped_armor_data().get("effect", "none")) == "hunger" else 10
\tif hunger_tick >= hunger_limit:
\t\thunger_tick = 0
\t\thunger = max(0, hunger - 1)
\tif str(equipped_armor_data().get("effect", "none")) == "regen" and turn_no % 12 == 0 and hp > 0:
\t\thp = mini(max_hp, hp + 1)'''
if hunger_anchor not in s:
    raise SystemExit("STEP80 armor hunger anchor failed")
s = s.replace(hunger_anchor, hunger_new, 1)

armor_helper_anchor = "\n\nfunc enemy_attack(index: int) -> void:\n"
if armor_helper_anchor not in s:
    raise SystemExit("STEP80 armor damage anchor failed")
armor_helpers = '''

func armor_adjust_damage(raw_damage: int, from_boss: bool = false) -> int:
\tvar data := equipped_armor_data()
\tvar effect := str(data.get("effect", "none"))
\tif effect.begins_with("dodge"):
\t\tvar dodge_rate := int(effect.trim_prefix("dodge"))
\t\tif rng.randi_range(1, 100) <= dodge_rate: return 0
\tvar damage := maxi(1, raw_damage - armor_defense_bonus())
\tif effect == "cut1": damage = maxi(1, damage - 1)
\telif effect == "cut3": damage = maxi(1, damage - 3)
\telif effect == "boss_guard" and from_boss: damage = maxi(1, int(ceil(float(damage) * 0.7)))
\treturn damage
'''
s = s.replace(armor_helper_anchor, armor_helpers + armor_helper_anchor, 1)

enemy_start = s.find("func enemy_attack(index: int) -> void:")
enemy_end = s.find("\n\nfunc handle_death", enemy_start)
if enemy_start < 0 or enemy_end < 0:
    raise SystemExit("STEP80 enemy attack block failed")
enemy_attack = '''func enemy_attack(index: int) -> void:
\tif index < 0 or index >= enemies.size(): return
\tvar raw_damage := maxi(1, int(enemies[index]["atk"]) - defense_power)
\tif style_name == "影": raw_damage = maxi(1, raw_damage - 1)
\tvar dmg := armor_adjust_damage(raw_damage, bool(enemies[index].get("boss", false)))
\tstart_enemy_attack_animation(index)
\tif dmg <= 0:
\t\tmessage = "%sの攻撃をかわした。" % str(enemies[index]["name"])
\t\treturn
\thp -= dmg
\tstart_player_hit_flash()
\tmessage = "%sの攻撃。%dダメージ。" % [str(enemies[index]["name"]), dmg]
\tif hp <= 0:
\t\thandle_death(str(enemies[index]["name"]))
\t\treturn
\tif str(equipped_armor_data().get("effect", "none")) == "counter" and rng.randi_range(1, 100) <= 25:
\t\tvar target_pos: Vector2i = enemies[index]["pos"]
\t\tdamage_enemy_with_projectile(index, 3, "返し装束")
\t\tif enemy_index_at(target_pos) >= 0: message += " 反撃。"
'''
s = s[:enemy_start] + enemy_attack + s[enemy_end:]

merchant_anchor = '''\t\t\tvar dmg = max(1, int(shopkeeper.get("atk", 10)) - defense_power)
\t\t\thp -= dmg
\t\t\tstart_player_hit_flash()
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
merchant_new = '''\t\t\tvar dmg := armor_adjust_damage(maxi(1, int(shopkeeper.get("atk", 10)) - defense_power), true)
\t\t\tif dmg <= 0:
\t\t\t\tmessage = "怒った商人の一撃をかわした。"
\t\t\t\treturn
\t\t\thp -= dmg
\t\t\tstart_player_hit_flash()
\t\t\tmessage = "怒った商人の一撃！ %dダメージ。" % dmg'''
if merchant_anchor not in s:
    raise SystemExit("STEP80 merchant armor anchor failed")
s = s.replace(merchant_anchor, merchant_new, 1)

valid_start = s.find("func valid_inventory_item_name(name: String) -> bool:")
valid_end = s.find("\n\nfunc add_inventory_item", valid_start)
if valid_start < 0 or valid_end < 0:
    raise SystemExit("STEP80 inventory validity block failed")
valid_func = '''func valid_inventory_item_name(name: String) -> bool:
\treturn name in ["薬", "兵糧丸", "忍気丸", "上薬", "大兵糧丸", "小巻物", "中巻物", "大巻物", "究極巻物", "手裏剣", "クナイ"] or is_equipment_name(name)
'''
s = s[:valid_start] + valid_func + s[valid_end:]
s = s.replace(
    'inventory_items.append({"name": name, "identified": identified, "count": 1})',
    'inventory_items.append({"name": name, "identified": identified or is_equipment_name(name), "count": 1})',
    1,
)

selected_start = s.find("func inventory_selected_name() -> String:")
selected_end = s.find("\n\nfunc open_inventory", selected_start)
if selected_start < 0 or selected_end < 0:
    raise SystemExit("STEP80 inventory selected block failed")
selected_func = '''func inventory_selected_name() -> String:
\tif inventory_selected == 0: return equipped_weapon
\tif inventory_selected == 1: return equipped_armor
\tvar idx := inventory_selected - 2
\tif idx >= 0 and idx < inventory_items.size(): return str(inventory_items[idx].get("name", ""))
\treturn ""
'''
s = s[:selected_start] + selected_func + s[selected_end:]

equip_start = s.find("func inventory_equip_selected() -> void:")
equip_end = s.find("\n\nfunc inventory_use_selected", equip_start)
if equip_start < 0 or equip_end < 0:
    raise SystemExit("STEP80 inventory equip block failed")
equip_func = '''func inventory_equip_selected() -> void:
\tif inventory_selected == 0 or inventory_selected == 1:
\t\tmessage = "%sは装備中。" % inventory_selected_name()
\telse:
\t\tvar idx := inventory_selected - 2
\t\tif idx >= 0 and idx < inventory_items.size():
\t\t\tvar name := str(inventory_items[idx].get("name", ""))
\t\t\tif is_weapon_name(name): equipped_weapon = name; message = "%sを武器に装備した。" % name
\t\t\telif is_armor_name(name): equipped_armor = name; message = "%sを防具に装備した。" % name
\t\t\telif is_projectile_name(name): equipped_projectile = name; message = "%sを飛び道具に装備した。" % name
\t\t\telse: message = "この道具は装備できない。"
\tqueue_redraw()
'''
s = s[:equip_start] + equip_func + s[equip_end:]

use_anchor = '''\tvar name := str(inventory_items[idx].get("name", ""))
\tif is_projectile_name(name):'''
use_new = '''\tvar name := str(inventory_items[idx].get("name", ""))
\tif is_equipment_name(name):
\t\tmessage = "%sは「装備」で身につける。" % name
\t\tqueue_redraw(); return
\tif is_projectile_name(name):'''
if use_anchor not in s:
    raise SystemExit("STEP80 equipment use anchor failed")
s = s.replace(use_anchor, use_new, 1)

drop_anchor = '''\tif equipped_projectile == dropped_name:
\t\tequipped_projectile = ""'''
drop_new = '''\tif equipped_projectile == dropped_name: equipped_projectile = ""
\tif equipped_weapon == dropped_name: equipped_weapon = "忍刀"
\tif equipped_armor == dropped_name: equipped_armor = "忍装束"'''
if drop_anchor not in s:
    raise SystemExit("STEP80 equipment drop anchor failed")
s = s.replace(drop_anchor, drop_new, 1)

display_start = s.find("func inventory_display_name(index: int) -> String:")
display_end = s.find("\n\nfunc draw_inventory_overlay", display_start)
if display_start < 0 or display_end < 0:
    raise SystemExit("STEP80 inventory display block failed")
display_func = '''func inventory_display_name(index: int) -> String:
\tif index == 0: return "%s（装備中）" % equipment_display_name(equipped_weapon)
\tif index == 1: return "%s（装備中）" % equipment_display_name(equipped_armor)
\tvar idx := index - 2
\tif idx < 0 or idx >= inventory_items.size(): return ""
\tvar entry: Dictionary = inventory_items[idx]; var name := str(entry.get("name", ""))
\tif is_projectile_name(name):
\t\tvar suffix := "（装備中）" if equipped_projectile == name else ""
\t\treturn "%s×%d%s" % [name, int(entry.get("count", 1)), suffix]
\tif is_equipment_name(name):
\t\tvar equipped := (is_weapon_name(name) and equipped_weapon == name) or (is_armor_name(name) and equipped_armor == name)
\t\treturn "%s%s" % [equipment_display_name(name), "（装備中）" if equipped else ""]
\treturn name if bool(entry.get("identified", false)) else "未識別の道具"
'''
s = s[:display_start] + display_func + s[display_end:]

price_anchor = '''func item_shop_price(name: String) -> int:
\tif name == "薬":'''
price_new = '''func item_shop_price(name: String) -> int:
\tif is_weapon_name(name): return int(WEAPON_CATALOG[name].get("price", 100))
\tif is_armor_name(name): return int(ARMOR_CATALOG[name].get("price", 100))
\tif name == "薬":'''
if price_anchor not in s:
    raise SystemExit("STEP80 equipment price anchor failed")
s = s.replace(price_anchor, price_new, 1)

spawn_anchor = "\n\nfunc spawn_item() -> void:\n"
if spawn_anchor not in s:
    raise SystemExit("STEP80 equipment spawn anchor failed")
spawn_helpers = '''

func unlocked_equipment_names(max_floor: int) -> Array[String]:
\tvar names: Array[String] = []
\tfor name in WEAPON_CATALOG:
\t\tif int(WEAPON_CATALOG[name].get("floor", 1)) <= max_floor: names.append(str(name))
\tfor name in ARMOR_CATALOG:
\t\tif int(ARMOR_CATALOG[name].get("floor", 1)) <= max_floor: names.append(str(name))
\treturn names


func random_unlocked_equipment(max_floor: int) -> String:
\tvar names := unlocked_equipment_names(max_floor)
\treturn names[rng.randi_range(0, names.size() - 1)] if not names.is_empty() else "忍刀"
'''
s = s.replace(spawn_anchor, spawn_helpers + spawn_anchor, 1)

spawn_body_anchor = '''\tvar p = find_random_open_cell()
\tvar roll = rng.randi_range(0, 999)'''
spawn_body_new = '''\tvar p = find_random_open_cell()
\tif rng.randi_range(1, 100) <= 10:
\t\titems.append({"pos":p, "name":random_unlocked_equipment(floor_no), "count":1, "price":0, "shop":false})
\t\treturn
\tvar roll = rng.randi_range(0, 999)'''
if spawn_body_anchor not in s:
    raise SystemExit("STEP80 spawn item body anchor failed")
s = s.replace(spawn_body_anchor, spawn_body_new, 1)

shop_names_anchor = '''\tif floor_no >= 70:
\t\tnames[rng.randi_range(0, 2)] = "大兵糧丸"'''
shop_names_new = shop_names_anchor + '''
\tif floor_no >= 5 and rng.randi_range(1, 100) <= 45:
\t\tnames[rng.randi_range(0, 2)] = random_unlocked_equipment(floor_no)'''
if shop_names_anchor not in s:
    raise SystemExit("STEP80 dungeon shop equipment anchor failed")
s = s.replace(shop_names_anchor, shop_names_new, 1)

village_catalog_anchor = '''\tvar unlocked: Array = []
\tfor entry in catalog:'''
village_catalog_new = '''\tfor equipment_name in unlocked_equipment_names(50):
\t\tvar data: Dictionary = WEAPON_CATALOG.get(equipment_name, ARMOR_CATALOG.get(equipment_name, {}))
\t\tif int(data.get("floor", 1)) > 1:
\t\t\tcatalog.append({"label":equipment_name, "name":equipment_name, "count":1, "price":int(data.get("price", 100)), "floor":int(data.get("floor", 1))})
\tvar unlocked: Array = []
\tfor entry in catalog:'''
if village_catalog_anchor not in s:
    raise SystemExit("STEP80 village shop catalog anchor failed")
s = s.replace(village_catalog_anchor, village_catalog_new, 1)

shop_y_anchor = '''func village_shop_choice_y(item_count: int, index: int) -> float:
\treturn maxf(330.0, 890.0 - item_count * 54.0) + index * 54.0'''
shop_y_new = '''func village_shop_choice_y(visible_count: int, row: int) -> float:
\treturn maxf(350.0, 818.0 - visible_count * 52.0) + row * 52.0


func village_shop_max_scroll() -> int:
\treturn maxi(0, village_shop_catalog().size() - VILLAGE_SHOP_VISIBLE_ROWS)


func village_shop_sync_scroll() -> void:
\tvillage_shop_scroll_offset = clampi(village_shop_scroll_offset, 0, village_shop_max_scroll())


func village_shop_scroll(rows: int) -> void:
\tvillage_shop_scroll_offset = clampi(village_shop_scroll_offset + rows, 0, village_shop_max_scroll())
\tqueue_redraw()'''
if shop_y_anchor not in s:
    raise SystemExit("STEP80 village shop scroll helper anchor failed")
s = s.replace(shop_y_anchor, shop_y_new, 1)

# Reset the page whenever the player enters the village shop.
s = s.replace(
    'village_menu = "village_shop"; message = "商店"',
    'village_menu = "village_shop"; village_shop_scroll_offset = 0; message = "商店"',
)

shop_touch_anchor = '''\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tfor i in range(catalog.size()):
\t\t\t\tif Rect2(48, village_shop_choice_y(catalog.size(), i), 624, 46).has_point(pos): buy_village_shop_item(i); break'''
shop_touch_new = '''\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tvillage_shop_sync_scroll()
\t\t\tif Rect2(48, 842, 270, 48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif Rect2(402, 842, 270, 48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telse:
\t\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, catalog.size() - village_shop_scroll_offset)
\t\t\t\tfor row in range(visible_count):
\t\t\t\t\tvar index := village_shop_scroll_offset + row
\t\t\t\t\tif Rect2(48, village_shop_choice_y(visible_count, row), 624, 46).has_point(pos): buy_village_shop_item(index); break'''
if shop_touch_anchor not in s:
    raise SystemExit("STEP80 village shop touch anchor failed")
s = s.replace(shop_touch_anchor, shop_touch_new, 1)

shop_draw_anchor = '''\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tdraw_ui_text(Vector2(240, 244), "%d階到達までの商品" % village_unlocked_floor(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d8dee5"))
\t\t\tfor i in range(catalog.size()):
\t\t\t\tvar offer: Dictionary = catalog[i]; var r := Rect2(48, village_shop_choice_y(catalog.size(), i), 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [str(offer["label"]), int(offer["price"])], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)'''
shop_draw_new = '''\t\telif village_menu == "village_shop":
\t\t\tvar catalog := village_shop_catalog()
\t\t\tvillage_shop_sync_scroll()
\t\t\tdraw_ui_text(Vector2(240, 244), "%d階到達までの商品" % village_unlocked_floor(), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("#d8dee5"))
\t\t\tvar visible_count := mini(VILLAGE_SHOP_VISIBLE_ROWS, catalog.size() - village_shop_scroll_offset)
\t\t\tfor row in range(visible_count):
\t\t\t\tvar index := village_shop_scroll_offset + row
\t\t\t\tvar offer: Dictionary = catalog[index]; var r := Rect2(48, village_shop_choice_y(visible_count, row), 624, 46); draw_panel(r, Color(0.04, 0.07, 0.10, 0.90), Color("#687786"))
\t\t\t\tvar offer_label := equipment_display_name(str(offer["name"])) if is_equipment_name(str(offer["name"])) else str(offer["label"])
\t\t\t\tdraw_ui_text(r.position + Vector2(16, 31), "%s    %d銭" % [offer_label, int(offer["price"])], HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\t\t\tvar prev := Rect2(48, 842, 270, 48); var next := Rect2(402, 842, 270, 48)
\t\t\tdraw_panel(prev, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset > 0 else Color("#29323b"))
\t\t\tdraw_panel(next, Color(0.04, 0.07, 0.10, 0.90), Color("#687786") if village_shop_scroll_offset < village_shop_max_scroll() else Color("#29323b"))
\t\t\tdraw_ui_text(prev.position + Vector2(92, 33), "↑ 前へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
\t\t\tdraw_ui_text(next.position + Vector2(92, 33), "↓ 次へ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)'''
if shop_draw_anchor not in s:
    raise SystemExit("STEP80 village shop draw anchor failed")
s = s.replace(shop_draw_anchor, shop_draw_new, 1)

shop_key_anchor = '''\t\telif village_menu == "village_shop" and event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\tbuy_village_shop_item(int(event.keycode - KEY_1))'''
shop_key_new = '''\t\telif village_menu == "village_shop":
\t\t\tif event.keycode == KEY_UP: village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode == KEY_DOWN: village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\t\telif event.keycode >= KEY_1 and event.keycode <= KEY_9:
\t\t\t\tbuy_village_shop_item(village_shop_scroll_offset + int(event.keycode - KEY_1))'''
if shop_key_anchor not in s:
    raise SystemExit("STEP80 village shop key anchor failed")
s = s.replace(shop_key_anchor, shop_key_new, 1)

hook_anchor = "\n\nfunc use_projectile() -> void:\n"
if hook_anchor not in s:
    raise SystemExit("STEP80 hook anchor failed")
hook_functions = '''

func hook_item_is_theft(item: Dictionary) -> bool:
\treturn bool(item.get("shop", false)) and not is_inside_shop(player)


func find_hook_target() -> Dictionary:
\tfor step in range(1, 7):
\t\tvar p2 := player + facing_dir * step
\t\tif not position_in_bounds(p2) or not is_walkable(p2): break
\t\tvar enemy_index := enemy_index_at(p2)
\t\tif enemy_index >= 0: return {"kind":"enemy", "index":enemy_index, "pos":p2}
\t\tfor item_index in range(items.size()):
\t\t\tif items[item_index].get("pos", Vector2i(-1, -1)) == p2: return {"kind":"item", "index":item_index, "pos":p2}
\treturn {}


func use_hook_claw() -> void:
\tvar target := find_hook_target()
\tif target.is_empty(): message = "鉤爪は何も捉えなかった。"; end_turn(); return
\tif str(target.get("kind", "")) == "enemy":
\t\tvar index := int(target["index"])
\t\tvar front := player + facing_dir
\t\tif index < 0 or index >= enemies.size() or enemy_index_at(front) >= 0 or (shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1,-1)) == front):
\t\t\tmessage = "引き寄せる場所がない。"; end_turn(); return
\t\tenemies[index]["pos"] = front
\t\tstart_melee_attack_animation(facing_dir, front)
\t\tattack_enemy(index)
\t\tmessage = "鉤爪で引き寄せ、先制攻撃。 " + message
\t\tend_turn(); return
\tvar item_index := int(target["index"])
\tif item_index < 0 or item_index >= items.size(): return
\tvar item: Dictionary = items[item_index]
\tvar name := str(item.get("name", ""))
\tif not inventory_has_space_for(name): message = "持ち物がいっぱいだ。"; return
\titems.remove_at(item_index)
\tfor i in range(shop_items.size() - 1, -1, -1):
\t\tif shop_items[i].get("pos", Vector2i(-1,-1)) == target.get("pos", Vector2i(-1,-1)): shop_items.remove_at(i)
\tif hook_item_is_theft(item):
\t\tadd_inventory_item(name, true, int(item.get("count", 1)))
\t\tshop_hostile = true
\t\tmessage = "鉤爪で店の商品を盗んだ！ 商人が追ってくる。"
\telif bool(item.get("shop", false)):
\t\tunpaid_items.append(item)
\t\tmessage = "%sを引き寄せた。未精算。" % name
\telse:
\t\tadd_inventory_item(name, true, int(item.get("count", 1)))
\t\tmessage = "%sを鉤爪で拾った。" % name
\tend_turn()
'''
s = s.replace(hook_anchor, hook_functions + hook_anchor, 1)
s = s.replace(
    '''func use_projectile() -> void:
\tif not is_projectile_name(equipped_projectile):''',
    '''func use_projectile() -> void:
\tif equipped_weapon == "鉤爪": use_hook_claw(); return
\tif not is_projectile_name(equipped_projectile):''',
    1,
)

run_state_anchor = '''\t\t"equipped_projectile": equipped_projectile,
\t\t"placed_traps": placed_traps,'''
run_state_new = '''\t\t"equipped_projectile": equipped_projectile,
\t\t"equipped_weapon": equipped_weapon,
\t\t"equipped_armor": equipped_armor,
\t\t"placed_traps": placed_traps,'''
if run_state_anchor not in s:
    raise SystemExit("STEP80 run save anchor failed")
s = s.replace(run_state_anchor, run_state_new, 1)

load_anchor = '''\tequipped_projectile = str(data.get("equipped_projectile", "")) if version >= 6 else ""
\tif not is_projectile_name(equipped_projectile) or projectile_inventory_index(equipped_projectile) < 0: equipped_projectile = ""'''
load_new = load_anchor + '''
\tequipped_weapon = str(data.get("equipped_weapon", "忍刀")) if version >= 9 else "忍刀"
\tequipped_armor = str(data.get("equipped_armor", "忍装束")) if version >= 9 else "忍装束"
\tif not is_weapon_name(equipped_weapon): equipped_weapon = "忍刀"
\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"'''
if load_anchor not in s:
    raise SystemExit("STEP80 run load anchor failed")
s = s.replace(load_anchor, load_new, 1)

s = s.replace('''\t\t"version": 3,
\t\t"warehouse_items": warehouse_items,''', '''\t\t"version": 4,
\t\t"warehouse_items": warehouse_items,
\t\t"equipped_weapon": equipped_weapon,
\t\t"equipped_armor": equipped_armor,''', 1)
meta_load_anchor = '''\twarehouse_items = sanitize_inventory_array(data.get("warehouse_items", []))
\tif warehouse_items.size() > WAREHOUSE_CAPACITY: warehouse_items.resize(WAREHOUSE_CAPACITY)'''
meta_load_new = meta_load_anchor + '''
\tequipped_weapon = str(data.get("equipped_weapon", "忍刀"))
\tequipped_armor = str(data.get("equipped_armor", "忍装束"))
\tif not is_weapon_name(equipped_weapon): equipped_weapon = "忍刀"
\tif not is_armor_name(equipped_armor): equipped_armor = "忍装束"'''
if meta_load_anchor not in s:
    raise SystemExit("STEP80 meta load anchor failed")
s = s.replace(meta_load_anchor, meta_load_new, 1)

s = s.replace(
    '"装備:%s / %s  %s" % [WEAPON_NAME,ARMOR_NAME,hunger_note]',
    '"装備:%s / %s  %s" % [equipped_weapon,equipped_armor,hunger_note]',
    1,
)
s = s.replace(
    '''var actions = ["忍刀 +%d → +%d（銭%d）" % [smith_weapon_rank, smith_weapon_rank + 1, weapon_price], "忍装束 +%d → +%d（銭%d）" % [smith_armor_rank, smith_armor_rank + 1, armor_price]]''',
    '''var actions = ["%s +%d → +%d（銭%d）" % [equipped_weapon, smith_weapon_rank, smith_weapon_rank + 1, weapon_price], "%s +%d → +%d（銭%d）" % [equipped_armor, smith_armor_rank, smith_armor_rank + 1, armor_price]]''',
    1,
)

test_anchor = "\n\nfunc debug_test_village_bottom_choice_layout() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP80 regression anchor failed")
test_func = '''

func debug_test_equipment_arsenal() -> String:
\tvar count_ok := WEAPON_CATALOG.size() == 11 and ARMOR_CATALOG.size() == 8
\tvar katana_ok := int(WEAPON_CATALOG["双牙刀"]["hits"]) == 2 and int(WEAPON_CATALOG["影斬刀"]["hits"]) == 3
\tvar spear_ok := int(WEAPON_CATALOG["疾風槍"]["range"]) == 2 and int(WEAPON_CATALOG["破軍槍"]["range"]) == 3
\tvar chain_ok := int(WEAPON_CATALOG["鎖鎌"]["min_range"]) == 3 and int(WEAPON_CATALOG["鎖鎌"]["max_range"]) == 5 and bool(WEAPON_CATALOG["天網鎖鎌"]["omni"])
\tvar hook_ok := int(WEAPON_CATALOG["鉤爪"]["range"]) == 6
\tvar armor_ok := str(ARMOR_CATALOG["鉄忍装束"]["effect"]) == "cut1" and str(ARMOR_CATALOG["黒鋼の重鎧"]["effect"]) == "cut3"
\treturn "PASS equipment arsenal 11+8" if count_ok and katana_ok and spear_ok and chain_ok and hook_ok and armor_ok else "FAIL equipment arsenal"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace(
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_bottom_choice_layout(),''',
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_equipment_arsenal(),
\t\tdebug_test_village_bottom_choice_layout(),''',
    1,
)

required = [
    "STEP80_EQUIPMENT_ARSENAL_APPLIED",
    "const RUN_SAVE_VERSION := 9",
    "const WEAPON_CATALOG := {",
    "const ARMOR_CATALOG := {",
    'var equipped_weapon := "忍刀"',
    "func try_weapon_reach_attack(dir: Vector2i) -> bool:",
    "func use_hook_claw() -> void:",
    'shop_hostile = true',
    "debug_test_equipment_arsenal()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP80 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP80 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP80_EQUIPMENT_ARSENAL PASS")
exec(Path("tools/apply_step81_weapon_fusion.py").read_text(encoding="utf-8"), {})
