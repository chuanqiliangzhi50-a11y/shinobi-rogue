from pathlib import Path


p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP82_BOSS_DROPS_ENEMY_ART_APPLIED" in s:
    print("STEP82_BOSS_DROPS_ENEMY_ART PASS (already applied)")
    raise SystemExit(0)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP82 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 5)
    if end < 0:
        raise SystemExit(f"STEP82 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n" + s[end:]


marker = "# STEP81_WEAPON_FUSION_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP82 STEP81 anchor failed")
s = s.replace(marker, marker + "# STEP82_BOSS_DROPS_ENEMY_ART_APPLIED\n", 1)

state_anchor = "var item_sheet_texture: Texture2D = null\n"
if state_anchor not in s:
    raise SystemExit("STEP82 texture state anchor failed")
s = s.replace(
    state_anchor,
    state_anchor
    + "var enemy_roster_texture: Texture2D = null\n"
    + "var boss_roster_texture: Texture2D = null\n",
    1,
)

load_anchor = '''\tif ResourceLoader.exists("res://art/item_sheet.svg"):
\t\titem_sheet_texture = load("res://art/item_sheet.svg") as Texture2D
'''
if load_anchor not in s:
    raise SystemExit("STEP82 texture load anchor failed")
s = s.replace(
    load_anchor,
    load_anchor
    + '''\tif ResourceLoader.exists("res://art/enemy_roster_v2.png"):
\t\tenemy_roster_texture = load("res://art/enemy_roster_v2.png") as Texture2D
\tif ResourceLoader.exists("res://art/boss_roster_v2.png"):
\t\tboss_roster_texture = load("res://art/boss_roster_v2.png") as Texture2D
''',
    1,
)

replace_func("enemy_profile", '''func enemy_profile(is_boss: bool) -> Dictionary:
\tvar tier = clamp(int((floor_no - 1) / 20), 0, 4)
\tif is_boss:
\t\tvar boss_names = ["甲冑侍", "忍頭領", "鬼面重装兵", "影の妖術師", "百階ノ影"]
\t\treturn {
\t\t\t"kind": "boss",
\t\t\t"name": boss_names[tier],
\t\t\t"hp": 42 + floor_no * 2 + tier * 12,
\t\t\t"atk": 6 + int(floor_no / 5) + tier,
\t\t\t"range": 1 + (1 if floor_no >= 50 else 0),
\t\t\t"coin_reward": 5 + tier * 2,
\t\t\t"soul_reward": 3 + tier
\t\t}

\tvar pool: Array = [
\t\t{"kind": "samurai", "name": "下忍", "hp_mod": 0, "atk_mod": 0, "range": 1},
\t\t{"kind": "hound", "name": "忍犬", "hp_mod": -2, "atk_mod": 1, "range": 1},
\t\t{"kind": "bandit", "name": "野盗", "hp_mod": 1, "atk_mod": 1, "range": 1}
\t]
\tif floor_no >= 15:
\t\tpool.append({"kind": "archer", "name": "手裏剣兵", "hp_mod": -3, "atk_mod": 0, "range": 4})
\tif floor_no >= 35:
\t\tpool.append({"kind": "shadow", "name": "くノ一", "hp_mod": 3, "atk_mod": 2, "range": 1})
\tif floor_no >= 65:
\t\tpool.append({"kind": "elite", "name": "上忍", "hp_mod": 8, "atk_mod": 3, "range": 1})
\tvar profile_base: Dictionary = pool[rng.randi_range(0, pool.size() - 1)]
\treturn {
\t\t"kind": str(profile_base["kind"]),
\t\t"name": str(profile_base["name"]),
\t\t"hp": max(4, 8 + floor_no + int(profile_base["hp_mod"])),
\t\t"atk": max(1, 2 + int(floor_no / 7) + int(profile_base["atk_mod"])),
\t\t"range": int(profile_base["range"]),
\t\t"coin_reward": 1 + (1 if tier >= 3 else 0),
\t\t"soul_reward": 1
\t}''')

replace_func("draw_enemy_reference_visual", '''func normal_enemy_roster_index(kind: String) -> int:
\tif kind == "shadow": return 1
\tif kind == "bandit" or kind == "elite": return 2
\tif kind == "hound": return 3
\tif kind == "archer": return 4
\treturn 0


func boss_roster_index(name: String) -> int:
\tif name == "忍頭領": return 1
\tif name == "鬼面重装兵": return 2
\tif name == "影の妖術師" or name == "百階ノ影": return 3
\treturn 0


func draw_roster_cell(texture: Texture2D, index: int, cells: int, center: Vector2, tile_size: float) -> void:
\tvar cell_width := float(texture.get_width()) / float(cells)
\tvar source := Rect2(cell_width * float(index), 0.0, cell_width, float(texture.get_height()))
\tvar size := maxf(34.0, tile_size + 15.0)
\tvar aspect := cell_width / maxf(1.0, float(texture.get_height()))
\tvar dest := Rect2(center - Vector2(size * aspect, size) * 0.5, Vector2(size * aspect, size))
\tdraw_texture_rect_region(texture, dest, source)


func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tvar is_boss := bool(enemy.get("boss", false))
\tif is_boss and boss_roster_texture != null:
\t\tdraw_roster_cell(boss_roster_texture, boss_roster_index(str(enemy.get("name", ""))), 4, center, tile_size)
\t\treturn
\tif not is_boss and enemy_roster_texture != null:
\t\tdraw_roster_cell(enemy_roster_texture, normal_enemy_roster_index(str(enemy.get("kind", "samurai"))), 5, center, tile_size)
\t\treturn
\tif enemy_sheet_texture == null:
\t\tdraw_entity_visual(center, "boss" if is_boss else "enemy", "将" if is_boss else "敵", 20, Color("#f08a7d"), tile_size)
\t\treturn
\tvar idx := enemy_sheet_index(str(enemy.get("kind", "samurai")), is_boss)
\tvar size := maxf(28.0, tile_size + 7.0)
\tvar dest := Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size))
\tdraw_texture_rect_region(enemy_sheet_texture, dest, Rect2(float(idx * 64), 0.0, 64.0, 64.0))''')

village_old = '''\tvar scene_key := "blacksmith" if village_menu == "weapon_fusion" else village_menu
\tif not village_scene_textures.has(scene_key): scene_key = "main"
\tvar scene_texture: Texture2D = village_scene_textures.get(scene_key, null) as Texture2D'''
village_new = '''\tvar scene_key := "blacksmith" if village_menu == "weapon_fusion" else village_menu
\tif not VILLAGE_SCENE_PATHS.has(scene_key): scene_key = "main"
\tvar scene_texture := get_village_scene_texture(scene_key)'''
if village_old not in s:
    raise SystemExit("STEP82 village lazy-load anchor failed")
s = s.replace(village_old, village_new, 1)

drop_anchor = "\nfunc attack_enemy(index: int, attack_dir: Vector2i = Vector2i.ZERO) -> void:\n"
if drop_anchor not in s:
    raise SystemExit("STEP82 drop helper anchor failed")
drop_helpers = '''
func rare_boss_weapon_pool(for_floor: int) -> Array[String]:
\tvar result: Array[String] = []
\tvar unlock_floor := maxi(20, for_floor + 10)
\tfor weapon_name in WEAPON_CATALOG:
\t\tvar data: Dictionary = WEAPON_CATALOG[weapon_name]
\t\tif int(data.get("rarity", 1)) >= 3 and int(data.get("floor", 1)) <= unlock_floor:
\t\t\tresult.append(str(weapon_name))
\treturn result


func drop_rare_boss_weapon(defeated: Dictionary) -> String:
\tif not bool(defeated.get("boss", false)): return ""
\tvar pool := rare_boss_weapon_pool(floor_no)
\tif pool.is_empty(): return ""
\tvar weapon_name := pool[rng.randi_range(0, pool.size() - 1)]
\tvar origin: Vector2i = defeated.get("pos", player)
\tvar drop_pos := find_nearest_item_drop_cell(origin)
\tif drop_pos != Vector2i(-1, -1):
\t\titems.append({"pos":drop_pos, "name":weapon_name, "count":1, "price":0, "shop":false, "boss_drop":true})
\telse:
\t\tadd_inventory_item(weapon_name, true, 1)
\treturn weapon_name
'''
s = s.replace(drop_anchor, "\n" + drop_helpers.rstrip() + drop_anchor, 1)

melee_old = '''\t\tif was_boss:
\t\t\tboss_defeated = true
\t\t\tmessage = "ボスを討ち取った。階段が使える。"'''
melee_new = '''\t\tif was_boss:
\t\t\tboss_defeated = true
\t\t\tvar rare_weapon := drop_rare_boss_weapon(defeated)
\t\t\tmessage = "ボスを討ち取った。レア武器「%s」が落ちた。" % rare_weapon'''
if melee_old not in s:
    raise SystemExit("STEP82 melee drop anchor failed")
s = s.replace(melee_old, melee_new, 1)

projectile_old = '''\t\tif was_boss: boss_defeated = true
\t\tmessage = "%sを倒した。" % defeated_name + level_up_notice'''
projectile_new = '''\t\tif was_boss:
\t\t\tboss_defeated = true
\t\t\tvar rare_weapon := drop_rare_boss_weapon(defeated)
\t\t\tmessage = "%sを倒した。レア武器「%s」が落ちた。" % [defeated_name, rare_weapon] + level_up_notice
\t\telse:
\t\t\tmessage = "%sを倒した。" % defeated_name + level_up_notice'''
if projectile_old not in s:
    raise SystemExit("STEP82 projectile drop anchor failed")
s = s.replace(projectile_old, projectile_new, 1)

ultimate_old = '''\t\t\t\tif was_boss:
\t\t\t\t\tboss_defeated = true
\tmessage = "奥義・影滅！" + level_up_notice'''
ultimate_new = '''\t\t\t\tif was_boss:
\t\t\t\t\tboss_defeated = true
\t\t\t\t\tvar rare_weapon := drop_rare_boss_weapon(defeated)
\t\t\t\t\tlevel_up_notice += " レア武器「%s」が落ちた。" % rare_weapon
\tmessage = "奥義・影滅！" + level_up_notice'''
if ultimate_old not in s:
    raise SystemExit("STEP82 ultimate drop anchor failed")
s = s.replace(ultimate_old, ultimate_new, 1)

test_anchor = "\nfunc debug_test_equipment_arsenal() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP82 test anchor failed")
test_func = '''
func debug_test_boss_drop_and_art_contract() -> String:
\tvar pool := rare_boss_weapon_pool(10)
\tvar rare_ok := not pool.is_empty()
\tfor weapon_name in pool:
\t\trare_ok = rare_ok and int(WEAPON_CATALOG[weapon_name].get("rarity", 1)) >= 3
\tvar old_floor := floor_no
\tvar old_map := map.duplicate(true)
\tvar old_items := items.duplicate(true)
\tvar old_player := player
\tfloor_no = 10
\tmap = []
\tfor y in range(MAP_H):
\t\tvar row: Array[String] = []
\t\tfor x in range(MAP_W): row.append(".")
\t\tmap.append(row)
\titems = []
\tplayer = Vector2i(1, 1)
\tvar dropped_name := drop_rare_boss_weapon({"boss":true, "pos":Vector2i(3, 3)})
\tvar drop_ok := not dropped_name.is_empty() and items.size() == 1 and bool(items[0].get("boss_drop", false))
\tfloor_no = old_floor
\tmap = old_map
\titems = old_items
\tplayer = old_player
\tvar paths := ["res://art/enemy_roster_v2.png", "res://art/boss_roster_v2.png"]
\tvar art_ok := true
\tfor path in paths:
\t\tif not ResourceLoader.exists(path):
\t\t\tart_ok = false
\t\telse:
\t\t\tvar roster_texture := load(path) as Texture2D
\t\t\tart_ok = art_ok and roster_texture != null and roster_texture.get_width() > 0
\tvar village_ok := true
\tfor scene_key in VILLAGE_SCENE_PATHS:
\t\tvar path := str(VILLAGE_SCENE_PATHS[scene_key])
\t\tif not ResourceLoader.exists(path):
\t\t\tvillage_ok = false
\t\telse:
\t\t\tvar village_texture := get_village_scene_texture(str(scene_key))
\t\t\tvillage_ok = village_ok and village_texture != null and village_texture.get_width() > 0
\treturn "PASS ボス武器落下・敵里画像" if rare_ok and drop_ok and art_ok and village_ok else "FAIL ボス武器落下・敵里画像"

'''
s = s.replace(test_anchor, "\n" + test_func + test_anchor.lstrip("\n"), 1)
s = s.replace(
    "\t\tdebug_test_weapon_fusion_contract(),\n",
    "\t\tdebug_test_weapon_fusion_contract(),\n\t\tdebug_test_boss_drop_and_art_contract(),\n",
    1,
)

required = [
    "STEP82_BOSS_DROPS_ENEMY_ART_APPLIED",
    "func drop_rare_boss_weapon(",
    "func draw_roster_cell(",
    "get_village_scene_texture(scene_key)",
    "debug_test_boss_drop_and_art_contract()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP82 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP82 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP82_BOSS_DROPS_ENEMY_ART PASS")
