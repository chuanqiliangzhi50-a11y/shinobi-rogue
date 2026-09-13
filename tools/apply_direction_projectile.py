from pathlib import Path
import re

p=Path('Main.gd'); s=p.read_text(encoding='utf-8'); original=s

def sub(pattern,repl,name):
    global s
    s,n=re.subn(pattern,repl,s,count=1,flags=re.S)
    if n!=1: raise SystemExit(f'{name} anchor failed: {n}')

s=s.replace('const RUN_SAVE_VERSION := 5','const RUN_SAVE_VERSION := 6',1)
s=s.replace('var inventory_selected := 0\n','var inventory_selected := 0\nvar facing_dir := Vector2i(0, 1)\nvar equipped_projectile := ""\n',1)
s=s.replace('\tfinal_clear = false\n\tapply_permanent_stats()','\tfinal_clear = false\n\tinventory_items.clear()\n\tequipped_projectile = ""\n\tfacing_dir = Vector2i(0, 1)\n\tapply_permanent_stats()',1)
a=s.index('func generate_floor() -> void:'); b=s.index('\n\nfunc carve_safe_path',a); g=s[a:b]
if '\tinventory_items.clear()\n' not in g: raise SystemExit('generate inventory anchor failed')
g=g.replace('\tinventory_items.clear()\n','',1); s=s[:a]+g+s[b:]
s=s.replace('func try_move(dir: Vector2i) -> void:\n\tif dir == Vector2i.ZERO:\n\t\tend_turn()\n\t\treturn\n\tvar target = player + dir','func try_move(dir: Vector2i) -> void:\n\tif dir == Vector2i.ZERO:\n\t\tend_turn()\n\t\treturn\n\tfacing_dir = Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))\n\tvar target = player + dir',1)

sub(r'func spawn_item\(\) -> void:\n.*?(?=\n\nfunc carve_shop_room)', '''func spawn_item() -> void:
\tvar p = find_random_open_cell()
\tvar roll = rng.randi_range(0, 999)
\tvar item_name = "兵糧丸"
\tvar count := 1
\tif roll < 150: item_name = "薬"
\telif roll < 300: item_name = "兵糧丸"
\telif roll < 410: item_name = "忍気丸"
\telif roll < 500:
\t\titem_name = "手裏剣"; count = rng.randi_range(3, 8)
\telif roll < 565:
\t\titem_name = "クナイ"; count = rng.randi_range(2, 6)
\telif roll < 650: item_name = "上薬"
\telif roll < 730: item_name = "大兵糧丸"
\telif roll < 850: item_name = "小巻物"
\telif roll < 930: item_name = "中巻物"
\telif roll < 985: item_name = "大巻物"
\telse: item_name = "究極巻物"
\titems.append({"pos": p, "name": item_name, "count": count, "price": 0, "shop": false})
''','spawn')

s=s.replace('\telse:\n\t\tadd_inventory_item(str(item["name"]), false)\n\t\tmessage = "%sを拾った。" % str(item["name"])','\telse:\n\t\tvar picked_count := max(1, int(item.get("count", 1)))\n\t\tadd_inventory_item(str(item["name"]), false, picked_count)\n\t\tmessage = "%s×%dを拾った。" % [str(item["name"]), picked_count] if picked_count > 1 else "%sを拾った。" % str(item["name"])',1)

sub(r'func valid_inventory_item_name\(name: String\) -> bool:\n.*?(?=\n\nfunc inventory_entry_count)', '''func is_projectile_name(name: String) -> bool:
\treturn name == "手裏剣" or name == "クナイ"

func valid_inventory_item_name(name: String) -> bool:
\treturn name in ["薬", "兵糧丸", "忍気丸", "上薬", "大兵糧丸", "小巻物", "中巻物", "大巻物", "究極巻物", "手裏剣", "クナイ"]

func add_inventory_item(name: String, identified: bool = false, count: int = 1) -> void:
\tif not valid_inventory_item_name(name): return
\tif is_projectile_name(name):
\t\tfor entry in inventory_items:
\t\t\tif str(entry.get("name", "")) == name:
\t\t\t\tentry["count"] = min(99, int(entry.get("count", 1)) + max(1, count)); entry["identified"] = true; return
\t\tinventory_items.append({"name": name, "identified": true, "count": min(99, max(1, count))}); return
\tinventory_items.append({"name": name, "identified": identified, "count": 1})

func sanitize_inventory_array(value: Variant) -> Array:
\tvar out: Array = []
\tif typeof(value) != TYPE_ARRAY: return out
\tfor raw in value:
\t\tif typeof(raw) != TYPE_DICTIONARY: continue
\t\tvar name := str(raw.get("name", ""))
\t\tif not valid_inventory_item_name(name): continue
\t\tvar count := clampi(int(raw.get("count", 1)), 1, 99)
\t\tif is_projectile_name(name):
\t\t\tvar merged := false
\t\t\tfor entry in out:
\t\t\t\tif str(entry.get("name", "")) == name:
\t\t\t\t\tentry["count"] = min(99, int(entry.get("count", 1)) + count); merged = true; break
\t\t\tif not merged: out.append({"name": name, "identified": true, "count": count})
\t\telse: out.append({"name": name, "identified": bool(raw.get("identified", false)), "count": 1})
\treturn out
''','inventory core')

sub(r'func inventory_equip_selected\(\) -> void:\n.*?(?=\n\nfunc inventory_use_selected)', '''func inventory_equip_selected() -> void:
\tif inventory_selected == 0 or inventory_selected == 1:
\t\tmessage = "%sは装備中。" % inventory_selected_name()
\telse:
\t\tvar idx := inventory_selected - 2
\t\tif idx >= 0 and idx < inventory_items.size():
\t\t\tvar name := str(inventory_items[idx].get("name", ""))
\t\t\tif is_projectile_name(name): equipped_projectile = name; message = "%sを飛び道具に装備した。" % name
\t\t\telse: message = "この道具は装備できない。"
\tqueue_redraw()
''','equip')

s=s.replace('\tvar name := str(inventory_items[idx].get("name", ""))\n\tinventory_items.remove_at(idx)\n\tapply_item_effect(name)','\tvar name := str(inventory_items[idx].get("name", ""))\n\tif is_projectile_name(name):\n\t\tmessage = "%sは「装備」してから「飛」で使う。" % name\n\t\tqueue_redraw(); return\n\tinventory_items.remove_at(idx)\n\tapply_item_effect(name)',1)

sub(r'func inventory_display_name\(index: int\) -> String:\n.*?(?=\n\nfunc draw_inventory_overlay)', '''func inventory_display_name(index: int) -> String:
\tif index == 0: return "%s（装備中）" % WEAPON_NAME
\tif index == 1: return "%s（装備中）" % ARMOR_NAME
\tvar idx := index - 2
\tif idx < 0 or idx >= inventory_items.size(): return ""
\tvar entry: Dictionary = inventory_items[idx]; var name := str(entry.get("name", ""))
\tif is_projectile_name(name):
\t\tvar suffix := "（装備中）" if equipped_projectile == name else ""
\t\treturn "%s×%d%s" % [name, int(entry.get("count", 1)), suffix]
\treturn name if bool(entry.get("identified", false)) else "未識別の道具"
''','display')

sub(r'func sanitize_item_array\(value: Variant\) -> Array:\n.*?(?=\n\nfunc sanitize_shopkeeper)', '''func sanitize_item_array(value: Variant) -> Array:
\tvar out: Array = []
\tif typeof(value) != TYPE_ARRAY: return out
\tfor raw in value:
\t\tif typeof(raw) != TYPE_DICTIONARY: continue
\t\tvar entry: Dictionary = raw; var pos_value: Variant = entry.get("pos", null)
\t\tif not validate_vector2i(pos_value): continue
\t\tvar pos: Vector2i = pos_value
\t\tif not position_in_bounds(pos) or str(map[pos.y][pos.x]) == "#": continue
\t\tif pos == stairs_pos or item_position_taken(pos, out): continue
\t\tvar name = str(entry.get("name", ""))
\t\tif not valid_inventory_item_name(name): continue
\t\tout.append({"pos": pos, "name": name, "count": clampi(int(entry.get("count", 1)), 1, 99), "price": max(0, int(entry.get("price", 0))), "shop": bool(entry.get("shop", false))})
\treturn out
''','item sanitizer')

sub(r'func use_projectile\(\) -> void:\n.*?(?=\nfunc place_trap)', '''func projectile_inventory_index(name: String) -> int:
\tfor i in range(inventory_items.size()):
\t\tif str(inventory_items[i].get("name", "")) == name and int(inventory_items[i].get("count", 0)) > 0: return i
\treturn -1

func enemy_index_at(p: Vector2i) -> int:
\tfor i in range(enemies.size()):
\t\tif enemies[i]["pos"] == p: return i
\treturn -1

func damage_enemy_with_projectile(index: int, damage: int, projectile_name: String) -> void:
\tif index < 0 or index >= enemies.size(): return
\tenemies[index]["hp"] = int(enemies[index]["hp"]) - max(1, damage)
\tmessage = "%sが%sに命中。%dダメージ。" % [projectile_name, str(enemies[index]["name"]), max(1, damage)]
\tif int(enemies[index]["hp"]) <= 0:
\t\tvar defeated: Dictionary = enemies[index]; var was_boss := bool(defeated["boss"]); var defeated_name := str(defeated["name"])
\t\trun_coins += max(0, int(defeated.get("coin_reward", 3 if was_boss else 1))); run_souls += max(0, int(defeated.get("soul_reward", 3 if was_boss else 1)))
\t\tknown_enemies[defeated_name] = int(known_enemies.get(defeated_name, 0)) + 1; enemies.remove_at(index); ninja_energy = min(100, ninja_energy + (20 if was_boss else 8))
\t\tif was_boss: boss_defeated = true
\t\tmessage = "%sを倒した。" % defeated_name

func drop_projectile_on_floor(name: String, p: Vector2i) -> void:
\tif not position_in_bounds(p) or not is_walkable(p) or cell_has_item(p) or p == stairs_pos: return
\titems.append({"pos": p, "name": name, "count": 1, "price": 0, "shop": false})

func consume_equipped_projectile() -> void:
\tvar idx := projectile_inventory_index(equipped_projectile)
\tif idx < 0: equipped_projectile = ""; return
\tvar left := int(inventory_items[idx].get("count", 1)) - 1
\tif left <= 0: inventory_items.remove_at(idx); equipped_projectile = ""
\telse: inventory_items[idx]["count"] = left

func use_projectile() -> void:
\tif not is_projectile_name(equipped_projectile): message = "飛び道具を装備していない。"; return
\tif projectile_inventory_index(equipped_projectile) < 0: equipped_projectile = ""; message = "飛び道具がない。"; return
\tif facing_dir == Vector2i.ZERO: facing_dir = Vector2i(0, 1)
\tvar projectile_name := equipped_projectile; var damage := 10 if projectile_name == "クナイ" else 6; var pos := player; var last_open := player; var hit := false
\tfor _step in range(10):
\t\tvar next := pos + facing_dir
\t\tif not position_in_bounds(next) or not is_walkable(next): break
\t\tpos = next; last_open = pos
\t\tvar enemy_index := enemy_index_at(pos)
\t\tif enemy_index >= 0: damage_enemy_with_projectile(enemy_index, damage, projectile_name); hit = true; break
\tconsume_equipped_projectile()
\tif not hit: drop_projectile_on_floor(projectile_name, last_open); message = "%sを放った。" % projectile_name
\tend_turn()

''','projectile')

s=s.replace('\t\t"inventory_items": inventory_items,\n','\t\t"inventory_items": inventory_items,\n\t\t"facing_dir": facing_dir,\n\t\t"equipped_projectile": equipped_projectile,\n',1)
s=s.replace('\tinventory_items = sanitize_inventory_array(data.get("inventory_items", [])) if version >= 5 else []\n','\tinventory_items = sanitize_inventory_array(data.get("inventory_items", [])) if version >= 5 else []\n\tfacing_dir = data.get("facing_dir", Vector2i(0, 1)) if version >= 6 and validate_vector2i(data.get("facing_dir", null)) else Vector2i(0, 1)\n\tif facing_dir == Vector2i.ZERO: facing_dir = Vector2i(0, 1)\n\tequipped_projectile = str(data.get("equipped_projectile", "")) if version >= 6 else ""\n\tif not is_projectile_name(equipped_projectile) or projectile_inventory_index(equipped_projectile) < 0: equipped_projectile = ""\n',1)

helper='''\n\nfunc draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
\tvar dir := Vector2(facing_dir.x, facing_dir.y)
\tif dir.length() < 0.1: dir = Vector2(0, 1)
\tdir = dir.normalized(); var tip := center + dir * (tile_size * 0.44); var side := Vector2(-dir.y, dir.x) * 4.0
\tdraw_colored_polygon(PackedVector2Array([tip, center + dir * (tile_size * 0.22) + side, center + dir * (tile_size * 0.22) - side]), Color("#e8d47f"))
\tdraw_entity_visual(center, "player", "忍", 21, Color("#ffffff"), tile_size)
'''
s=s.replace('\n\nconst UI_GLYPH_MAP := {',helper+'\n\nconst UI_GLYPH_MAP := {',1)
old='''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tdraw_arc(pc + Vector2(0, 13), 16.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_entity_visual(pc, "player", "忍", 21, Color("#ffffff"), PTILE)'''
new='''\tif portrait_cell_in_view(player):
\t\tvar pc := portrait_cell_center(player)
\t\tdraw_arc(pc + Vector2(0, 13), 16.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)
\t\tdraw_player_facing_visual(pc, PTILE)'''
if old not in s: raise SystemExit('clarity player anchor failed')
s=s.replace(old,new,1)
s=s.replace('draw_entity_visual(cell_center(player), "player", "忍", 16, Color("#d9e2ee"), TILE)','draw_player_facing_visual(cell_center(player), TILE)',1)
if s==original: raise SystemExit('no changes')
p.write_text(s,encoding='utf-8'); print('DIRECTION_PROJECTILE_PATCH PASS')
