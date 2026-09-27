from pathlib import Path
import re


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP87_ENEMY_DIRECTIONS_RANKED_DROPS_APPLIED" in s:
    print("STEP87_ENEMY_DIRECTIONS_RANKED_DROPS PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP87 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP87 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP86_VILLAGE_SOURCES_ATTACK_BUTTON_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP87 STEP86 anchor failed")
s = s.replace(marker, marker + "# STEP87_ENEMY_DIRECTIONS_RANKED_DROPS_APPLIED\n", 1)

# Food terminology is unified throughout data, shops, messages and tests.
s = s.replace("大兵糧丸", "大きなおにぎり")
s = s.replace("兵糧丸", "おにぎり")
s = s.replace("おにぎり小", "おにぎり")

glyph_anchor = '\t"べ": "res://art/step76_glyphs/u3079.svg"\n}'
if glyph_anchor not in s:
    raise SystemExit("STEP87 glyph map anchor failed")
s = s.replace(glyph_anchor, '''\t"べ": "res://art/step76_glyphs/u3079.svg",
\t"お": "res://art/step76_glyphs/u304a.svg",
\t"甲": "res://art/step76_glyphs/u7532.svg",
\t"妖": "res://art/step76_glyphs/u5996.svg",
\t"チ": "res://art/step76_glyphs/u30c1.svg",
\t"賊": "res://art/step76_glyphs/u8cca.svg",
\t"八": "res://art/step76_glyphs/u516b.svg",
\t"ぎ": "res://art/step76_glyphs/u304e.svg",
\t"冑": "res://art/step76_glyphs/u5191.svg",
\t"師": "res://art/step76_glyphs/u5e2b.svg",
\t"級": "res://art/step76_glyphs/u7d1a.svg",
\t"侍": "res://art/step76_glyphs/u4f8d.svg"
}''', 1)

state_anchor = "var boss_roster_texture: Texture2D = null\n"
if state_anchor not in s:
    raise SystemExit("STEP87 direction texture state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + "var enemy_8dir_texture: Texture2D = null\n"
    + "var boss_8dir_texture: Texture2D = null\n",
    1,
)

load_anchor = '''\tif ResourceLoader.exists("res://art/boss_roster_v2.png"):
\t\tboss_roster_texture = load("res://art/boss_roster_v2.png") as Texture2D
'''
if load_anchor not in s:
    raise SystemExit("STEP87 direction texture load anchor failed")
s = s.replace(
    load_anchor,
    load_anchor
    + '''\tif ResourceLoader.exists("res://art/enemy_8dir_atlas.png"):
\t\tenemy_8dir_texture = load("res://art/enemy_8dir_atlas.png") as Texture2D
\tif ResourceLoader.exists("res://art/boss_8dir_atlas.png"):
\t\tboss_8dir_texture = load("res://art/boss_8dir_atlas.png") as Texture2D
''',
    1,
)

replace_func("enemy_profile", r'''func enemy_rank_pool_for_floor(for_floor: int) -> Array[int]:
\tif for_floor < 10: return [0]
\tif for_floor < 30: return [0, 1]
\tif for_floor < 60: return [1, 2]
\treturn [2]


func enemy_rank_for_floor(for_floor: int) -> int:
\tvar ranks := enemy_rank_pool_for_floor(for_floor)
\treturn int(ranks[rng.randi_range(0, ranks.size() - 1)])


func enemy_profile(is_boss: bool) -> Dictionary:
\tvar tier := clampi(int((floor_no - 1) / 20), 0, 4)
\tif is_boss:
\t\tvar boss_names := ["甲冑侍", "忍頭領", "鬼面重装兵", "影の妖術師"]
\t\tvar boss_index := rng.randi_range(0, 3) if floor_no >= 90 else mini(3, tier)
\t\treturn {
\t\t\t"kind":"boss", "name":boss_names[boss_index], "boss_index":boss_index, "rank":2,
\t\t\t"hp":42 + floor_no * 2 + boss_index * 12,
\t\t\t"atk":6 + int(floor_no / 5) + boss_index,
\t\t\t"range":1 + (1 if floor_no >= 50 else 0),
\t\t\t"coin_reward":5 + boss_index * 2, "soul_reward":3 + boss_index
\t\t}
\tvar rank := enemy_rank_for_floor(floor_no)
\tvar pool: Array = [
\t\t{"kind":"samurai", "name":"下忍", "hp_mod":0, "atk_mod":0, "range":1},
\t\t{"kind":"shadow", "name":"クノイチ", "hp_mod":-1, "atk_mod":1, "range":3},
\t\t{"kind":"spear", "name":"槍兵", "hp_mod":2, "atk_mod":1, "range":2},
\t\t{"kind":"archer", "name":"手裏剣兵", "hp_mod":-2, "atk_mod":0, "range":4},
\t\t{"kind":"bandit", "name":"盗賊", "hp_mod":1, "atk_mod":1, "range":1},
\t\t{"kind":"chain", "name":"鎖鎌兵", "hp_mod":0, "atk_mod":1, "range":3},
\t\t{"kind":"hound", "name":"忍犬", "hp_mod":-3, "atk_mod":1, "range":1}
\t]
\tvar base: Dictionary = pool[rng.randi_range(0, pool.size() - 1)]
\treturn {
\t\t"kind":str(base["kind"]), "name":str(base["name"]), "rank":rank,
\t\t"hp":maxi(4, 8 + floor_no + int(base["hp_mod"]) + rank * 8),
\t\t"atk":maxi(1, 2 + int(floor_no / 7) + int(base["atk_mod"]) + rank * 2),
\t\t"range":int(base["range"]), "coin_reward":1 + rank, "soul_reward":1 + rank
\t}''')

replace_func("spawn_enemy", r'''func spawn_enemy(is_boss: bool) -> void:
\tvar p := find_random_open_cell()
\tvar profile := enemy_profile(is_boss)
\tvar e := {
\t\t"pos":p, "hp":int(profile["hp"]), "atk":int(profile["atk"]), "bound":0,
\t\t"boss":is_boss, "name":str(profile["name"]), "kind":str(profile["kind"]),
\t\t"rank":clampi(int(profile.get("rank", 2 if is_boss else 0)), 0, 2),
\t\t"boss_index":clampi(int(profile.get("boss_index", 0)), 0, 3),
\t\t"range":int(profile["range"]), "coin_reward":int(profile["coin_reward"]),
\t\t"soul_reward":int(profile["soul_reward"]),
\t\t"_facing":[Vector2i(0,-1),Vector2i(1,-1),Vector2i(1,0),Vector2i(1,1),Vector2i(0,1),Vector2i(-1,1),Vector2i(-1,0),Vector2i(-1,-1)][rng.randi_range(0,7)]
\t}
\tenemies.append(e)''')

boss_spawn_old = "\tif floor_no % 10 == 0: spawn_boss()\n"
if boss_spawn_old not in s:
    raise SystemExit("STEP87 late boss generation anchor failed")
s = s.replace(
    boss_spawn_old,
    '''\tif floor_no >= 90:
\t\tfor _boss in range(rng.randi_range(2, 3)): spawn_boss()
\telif floor_no % 10 == 0: spawn_boss()
''',
    1,
)

replace_func("spawn_item", r'''func random_unlocked_armor(max_floor: int) -> String:
\tvar names: Array[String] = []
\tfor armor_name in ARMOR_CATALOG:
\t\tif int(ARMOR_CATALOG[armor_name].get("floor", 1)) <= max_floor: names.append(str(armor_name))
\treturn names[rng.randi_range(0, names.size() - 1)] if not names.is_empty() else "忍装束"


func spawn_item() -> void:
\tvar p := find_random_open_cell()
\tif rng.randi_range(1, 100) <= 10:
\t\tvar armor_name := random_unlocked_armor(floor_no)
\t\titems.append({"pos":p,"name":armor_name,"count":1,"price":0,"shop":false,"bonus":random_equipment_bonus(floor_no)})
\t\treturn
\tvar roll := rng.randi_range(0, 999)
\tvar item_name := "おにぎり"
\tvar count := 1
\tif roll < 170: item_name = "薬"
\telif roll < 350: item_name = "おにぎり"
\telif roll < 470: item_name = "忍気丸"
\telif roll < 570: item_name = "手裏剣"; count = rng.randi_range(3, 8)
\telif roll < 650: item_name = "クナイ"; count = rng.randi_range(2, 6)
\telif roll < 740: item_name = "上薬"
\telif roll < 820: item_name = "大きなおにぎり"
\telif roll < 900: item_name = "小巻物"
\telif roll < 955: item_name = "中巻物"
\telif roll < 990: item_name = "大巻物"
\telse: item_name = "究極巻物"
\titems.append({"pos":p,"name":item_name,"count":count,"price":0,"shop":false,"bonus":0})''')

loot_anchor = "\nfunc rare_boss_weapon_pool(for_floor: int) -> Array[String]:\n"
if loot_anchor not in s:
    raise SystemExit("STEP87 enemy loot helper anchor failed")
loot_helpers = r'''
func enemy_weapon_drop_for(kind: String, rank: int) -> String:
\tvar level := clampi(rank, 0, 2)
\tif kind == "samurai": return ["忍刀","双牙刀","影斬刀"][level]
\tif kind == "spear": return ["疾風槍","三方向槍","破軍槍"][level]
\tif kind == "chain": return ["鎖鎌","乱舞鎖鎌","天網鎖鎌"][level]
\tif kind == "bandit": return "鉤爪"
\tif kind == "shadow": return "クナイ"
\tif kind == "archer": return "手裏剣"
\treturn ""


func drop_enemy_loot(defeated: Dictionary) -> String:
\tif bool(defeated.get("boss", false)): return ""
\tvar kind := str(defeated.get("kind", ""))
\tvar rank := clampi(int(defeated.get("rank", 0)), 0, 2)
\tvar chance := 45 if kind == "hound" else 20
\tif rng.randi_range(1, 100) > chance: return ""
\tvar item_name := enemy_weapon_drop_for(kind, rank)
\tvar count := 1
\tif kind == "hound":
\t\tvar foods := ["薬","おにぎり"] if rank == 0 else (["薬","おにぎり","上薬"] if rank == 1 else ["上薬","大きなおにぎり","おにぎり"])
\t\titem_name = str(foods[rng.randi_range(0, foods.size() - 1)])
\telif kind == "shadow": count = [2,4,7][rank]
\telif kind == "archer": count = [3,6,10][rank]
\tif item_name.is_empty(): return ""
\tvar origin: Vector2i = defeated.get("pos", player)
\tvar drop_pos := find_nearest_item_drop_cell(origin)
\tif drop_pos == Vector2i(-1,-1): return ""
\titems.append({"pos":drop_pos,"name":item_name,"count":count,"price":0,"shop":false,"bonus":random_equipment_bonus(floor_no) if is_equipment_name(item_name) else 0,"enemy_drop":true})
\treturn item_name
'''
s = s.replace(loot_anchor, "\n" + loot_helpers.rstrip() + loot_anchor, 1)

# Every combat path uses the same enemy-drop rule and keeps its indentation.
s = re.sub(
    r"(?m)^(\t+)gain_enemy_exp\(defeated\)$",
    lambda match: match.group(1) + "gain_enemy_exp(defeated)\n" + match.group(1) + "drop_enemy_loot(defeated)",
    s,
)

sanitize_anchor = '''\t\t\t"kind": str(entry.get("kind", "legacy")),
\t\t\t"range": clamp(int(entry.get("range", 1)), 1, 5),'''
if sanitize_anchor not in s:
    raise SystemExit("STEP87 sanitize enemy rank anchor failed")
s = s.replace(
    sanitize_anchor,
    '''\t\t\t"kind": str(entry.get("kind", "legacy")),
\t\t\t"rank": clampi(int(entry.get("rank", 0)), 0, 2),
\t\t\t"boss_index": clampi(int(entry.get("boss_index", 0)), 0, 3),
\t\t\t"range": clamp(int(entry.get("range", 1)), 1, 5),''',
    1,
)

timed_anchor = '''\t\t"boss":false, "name":str(profile["name"]), "kind":str(profile["kind"]),
\t\t"range":int(profile["range"]),'''
if timed_anchor not in s:
    raise SystemExit("STEP87 timed spawn rank anchor failed")
s = s.replace(
    timed_anchor,
    '''\t\t"boss":false, "name":str(profile["name"]), "kind":str(profile["kind"]),
\t\t"rank":clampi(int(profile.get("rank",0)),0,2), "boss_index":0,
\t\t"range":int(profile["range"]),''',
    1,
)

replace_func("draw_enemy_reference_visual", r'''func enemy_direction_index(direction: Vector2i) -> int:
\tvar d := Vector2i(clampi(direction.x,-1,1),clampi(direction.y,-1,1))
\tvar dirs := [Vector2i(0,-1),Vector2i(1,-1),Vector2i(1,0),Vector2i(1,1),Vector2i(0,1),Vector2i(-1,1),Vector2i(-1,0),Vector2i(-1,-1)]
\tvar index := dirs.find(d)
\treturn index if index >= 0 else 4


func enemy_direction_row(kind: String) -> int:
\tif kind == "shadow": return 1
\tif kind == "bandit" or kind == "chain": return 2
\tif kind == "hound": return 3
\tif kind == "archer": return 4
\treturn 0


func boss_direction_row(enemy: Dictionary) -> int:
\tif enemy.has("boss_index"): return clampi(int(enemy["boss_index"]),0,3)
\treturn boss_roster_index(str(enemy.get("name","")))


func draw_8dir_enemy_cell(texture: Texture2D, row: int, direction: Vector2i, center: Vector2, tile_size: float, is_boss: bool) -> void:
\tvar column := enemy_direction_index(direction)
\tvar source := Rect2(float(column*128),float(row*128),128.0,128.0)
\tvar size := maxf(38.0,tile_size + (22.0 if is_boss else 15.0))
\tvar dest := Rect2(center-Vector2(size,size)*0.5,Vector2(size,size))
\tdraw_texture_rect_region(texture,dest,source)


func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tcenter += enemy_idle_visual_offset(enemy)
\tcenter += enemy_move_visual_offset(enemy,minf(tile_size,48.0))
\tvar is_boss := bool(enemy.get("boss",false))
\tvar direction: Vector2i = enemy.get("_facing",Vector2i(0,1))
\tif is_boss and boss_8dir_texture != null:
\t\tdraw_8dir_enemy_cell(boss_8dir_texture,boss_direction_row(enemy),direction,center,tile_size,true); return
\tif not is_boss and enemy_8dir_texture != null:
\t\tdraw_8dir_enemy_cell(enemy_8dir_texture,enemy_direction_row(str(enemy.get("kind","samurai"))),direction,center,tile_size,false); return
\tif is_boss and boss_roster_texture != null:
\t\tdraw_roster_cell(boss_roster_texture,boss_roster_index(str(enemy.get("name",""))),4,center,tile_size,direction); return
\tif enemy_roster_texture != null:
\t\tdraw_roster_cell(enemy_roster_texture,normal_enemy_roster_index(str(enemy.get("kind","samurai"))),5,center,tile_size,direction); return
\tdraw_entity_visual(center,"boss" if is_boss else "enemy","将" if is_boss else "敵",20,Color("#f08a7d"),tile_size)''')

test_anchor = "\nfunc debug_test_step86_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP87 regression anchor failed")
test_func = r'''
func debug_test_step87_contract() -> String:
\tvar ranks_ok := enemy_rank_pool_for_floor(1)==[0] and enemy_rank_pool_for_floor(10)==[0,1] and enemy_rank_pool_for_floor(30)==[1,2] and enemy_rank_pool_for_floor(60)==[2] and enemy_rank_pool_for_floor(90)==[2]
\tvar drops_ok := enemy_weapon_drop_for("samurai",0)=="忍刀" and enemy_weapon_drop_for("samurai",2)=="影斬刀" and enemy_weapon_drop_for("spear",2)=="破軍槍" and enemy_weapon_drop_for("chain",2)=="天網鎖鎌" and enemy_weapon_drop_for("bandit",1)=="鉤爪" and enemy_weapon_drop_for("shadow",1)=="クナイ" and enemy_weapon_drop_for("archer",1)=="手裏剣"
\tvar direction_ok := enemy_direction_index(Vector2i(0,-1))==0 and enemy_direction_index(Vector2i(-1,-1))==7
\tvar food_ok := item_shop_price("おにぎり") > 0 and item_shop_price("大きなおにぎり") > item_shop_price("おにぎり")
\treturn "PASS 敵八方向階級品" if ranks_ok and drops_ok and direction_ok and food_ok else "FAIL 敵八方向階級品"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step86_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP87 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step87_contract(),\n", 1)

# The function bodies above use raw strings for regex safety. Convert their
# visible indentation escapes into real tabs before writing GDScript.
s = s.replace("\\t", "\t")

required = [
    "STEP87_ENEMY_DIRECTIONS_RANKED_DROPS_APPLIED",
    'enemy_8dir_atlas.png', 'boss_8dir_atlas.png',
    "func enemy_rank_pool_for_floor(", "func drop_enemy_loot(",
    "func enemy_direction_index(", "debug_test_step87_contract()",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP87 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP87 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP87_ENEMY_DIRECTIONS_RANKED_DROPS PASS")

