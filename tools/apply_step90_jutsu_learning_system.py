from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP90_JUTSU_LEARNING_SYSTEM_APPLIED" in s:
    print("STEP90_JUTSU_LEARNING_SYSTEM PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP89_FLOOR_TRAPS_CONTROLS_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP90 requires STEP89")
s = s.replace(marker, marker + "# STEP90_JUTSU_LEARNING_SYSTEM_APPLIED\n", 1)

glyph_anchor = '\t"列": "res://art/step76_glyphs/u5217.svg",\n'
if glyph_anchor not in s:
    raise SystemExit("STEP90 glyph map anchor failed")
jutsu_glyphs = {
    "土":"u571f.svg", "岩":"u5ca9.svg", "衝":"u885d.svg", "迅":"u8fc5.svg",
    "水":"u6c34.svg", "牢":"u7262.svg", "刃":"u5203.svg", "爆":"u7206.svg",
    "炎":"u708e.svg", "透":"u900f.svg", "視":"u8996.svg", "絶":"u7d76.svg",
    "周":"u5468.svg", "指":"u6307.svg", "狙":"u72d9.svg", "抜":"u629c.svg",
    "早":"u65e9.svg", "混":"u6df7.svg", "～":"uff5e.svg", "表":"u8868.svg",
    "示":"u793a.svg", "残":"u6b8b.svg", "習":"u7fd2.svg", "そ":"u305d.svg",
    "惑":"u60d1.svg", "避":"u907f.svg", "シ":"u30b7.svg", "レ":"u30ec.svg",
}
glyph_lines = "".join(f'\t"{ch}": "res://art/step76_glyphs/{filename}",\n' for ch, filename in jutsu_glyphs.items())
s = s.replace(glyph_anchor, glyph_anchor + glyph_lines, 1)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP90 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 1)
    if end < 0:
        raise SystemExit(f"STEP90 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n\n" + s[end + 1:]


state_anchor = 'var level_up_notice := ""\n'
if state_anchor not in s:
    raise SystemExit("STEP90 state anchor failed")
s = s.replace(state_anchor, state_anchor + '''var learned_jutsu: Array[String] = []
var pending_jutsu_choices: Array[String] = []
var jutsu_menu := false
var jutsu_targeting := ""
var trap_sense_steps := 0
var swift_steps := 0
var jutsu_vision_steps := 0

const JUTSU_LEARN_LEVELS := [2,4,6,8,10,12,15,18,22,26]
const JUTSU_ORDER := [
\t"火遁・火走り", "風遁・鎌風", "土遁・岩衝", "雷遁・迅雷", "水遁・水牢", "影刃乱舞", "爆炎陣",
\t"隠れ身", "忍足", "疾風歩", "煙遁", "影縛り", "透視", "影分身"
]
const JUTSU_DATA := {
\t"火遁・火走り":{"cost":12,"min_level":2,"range":5,"target":true,"desc":"前方5マスへ炎攻撃"},
\t"風遁・鎌風":{"cost":18,"min_level":4,"range":2,"target":true,"desc":"前方3方向へ攻撃"},
\t"土遁・岩衝":{"cost":18,"min_level":6,"range":3,"target":true,"desc":"攻撃して2マス後退"},
\t"雷遁・迅雷":{"cost":20,"min_level":8,"range":4,"target":true,"desc":"遠距離攻撃と気絶"},
\t"水遁・水牢":{"cost":22,"min_level":10,"range":3,"target":true,"desc":"敵を3ターン拘束"},
\t"影刃乱舞":{"cost":28,"min_level":15,"range":1,"target":false,"desc":"周囲8方向を攻撃"},
\t"爆炎陣":{"cost":40,"min_level":22,"range":4,"target":true,"desc":"指定地点を範囲攻撃"},
\t"隠れ身":{"cost":10,"min_level":2,"range":0,"target":false,"desc":"1ターン狙われない"},
\t"忍足":{"cost":15,"min_level":2,"range":0,"target":false,"desc":"30歩罠を見抜く"},
\t"疾風歩":{"cost":18,"min_level":6,"range":0,"target":false,"desc":"3回素早く移動"},
\t"煙遁":{"cost":20,"min_level":8,"range":0,"target":false,"desc":"敵を3ターン混乱"},
\t"影縛り":{"cost":20,"min_level":10,"range":5,"target":true,"desc":"敵を2～4ターン拘束"},
\t"透視":{"cost":30,"min_level":15,"range":0,"target":false,"desc":"30歩敵と道具を表示"},
\t"影分身":{"cost":30,"min_level":18,"range":0,"target":false,"desc":"分身が30歩敵を引く"}
}
''', 1)

start_anchor = '''\tplayer_exp = 0
\tlevel_up_notice = ""
\tsmoke_turns = 0'''
if start_anchor not in s:
    raise SystemExit("STEP90 new run anchor failed")
s = s.replace(start_anchor, '''\tplayer_exp = 0
\tlevel_up_notice = ""
\tlearned_jutsu.clear(); pending_jutsu_choices.clear(); jutsu_menu = false; jutsu_targeting = ""
\ttrap_sense_steps = 0; swift_steps = 0; jutsu_vision_steps = 0
\tsmoke_turns = 0''', 1)

level_anchor = '''\t\tif player_level % 3 == 0:
\t\t\tdefense_power += 1'''
if level_anchor not in s:
    raise SystemExit("STEP90 level choice anchor failed")
s = s.replace(level_anchor, level_anchor + '''
\t\tif player_level in JUTSU_LEARN_LEVELS and pending_jutsu_choices.is_empty():
\t\t\tprepare_jutsu_choices()''', 1)

jutsu_helpers_anchor = "\nfunc enemy_weapon_drop_for(kind: String, rank: int) -> String:\n"
if jutsu_helpers_anchor not in s:
    raise SystemExit("STEP90 jutsu helper anchor failed")
jutsu_helpers = '''
func jutsu_cost(name: String) -> int:
\treturn int(JUTSU_DATA.get(name, {}).get("cost", 999))


func sanitize_jutsu_list(value: Variant) -> Array[String]:
\tvar out: Array[String] = []
\tif typeof(value) != TYPE_ARRAY: return out
\tfor raw in value:
\t\tvar name := str(raw)
\t\tif name in JUTSU_ORDER and name not in out and out.size() < 10: out.append(name)
\treturn out


func prepare_jutsu_choices() -> void:
\tif learned_jutsu.size() >= 10: return
\tvar pool: Array[String] = []
\tfor name in JUTSU_ORDER:
\t\tif name not in learned_jutsu and int(JUTSU_DATA[name].get("min_level", 1)) <= player_level: pool.append(name)
\tpending_jutsu_choices.clear()
\twhile not pool.is_empty() and pending_jutsu_choices.size() < 3:
\t\tvar index := rng.randi_range(0, pool.size() - 1)
\t\tpending_jutsu_choices.append(pool[index]); pool.remove_at(index)


func learn_jutsu(name: String) -> void:
\tif name not in pending_jutsu_choices or name in learned_jutsu: return
\tlearned_jutsu.append(name)
\tpending_jutsu_choices.clear()
\tmessage = "%sを習得した。" % name
\tsave_run_state(); queue_redraw()


func open_jutsu_menu() -> void:
\tif learned_jutsu.is_empty(): message = "まだ術を習得していない。"; queue_redraw(); return
\tjutsu_menu = true; jutsu_targeting = ""; message = "使う術を選ぶ。"; queue_redraw()


func close_jutsu_menu() -> void:
\tjutsu_menu = false; jutsu_targeting = ""; message = "術選択を閉じた。"; queue_redraw()


func jutsu_target_valid(name: String, target: Vector2i) -> bool:
\tif not position_in_bounds(target) or not is_walkable(target): return false
\tvar max_range := int(JUTSU_DATA.get(name, {}).get("range", 0))
\tif maxi(absi(target.x-player.x),absi(target.y-player.y)) > max_range: return false
\tif name in ["土遁・岩衝","雷遁・迅雷","水遁・水牢","影縛り"]: return enemy_index_at(target) >= 0
\treturn target != player


func spend_jutsu_energy(name: String) -> bool:
\tvar cost := jutsu_cost(name)
\tif ninja_energy < cost: message = "忍気が足りない。必要%d。" % cost; queue_redraw(); return false
\tninja_energy -= cost
\treturn true


func jutsu_damage_positions(positions: Array[Vector2i], damage: int, label: String) -> int:
\tvar hits := 0
\tfor pos in positions:
\t\tvar index := enemy_index_at(pos)
\t\tif index >= 0: damage_enemy_with_projectile(index, damage, label); hits += 1
\treturn hits


func cast_targeted_jutsu(name: String, target: Vector2i) -> void:
\tif not jutsu_target_valid(name,target): message = "その場所には術を使えない。"; queue_redraw(); return
\tif not spend_jutsu_energy(name): return
\tvar delta := target-player; var dir := Vector2i(signi(delta.x),signi(delta.y)); var base_damage := maxi(1, attack_power + weapon_attack_bonus())
\tif name == "火遁・火走り":
\t\tvar cells: Array[Vector2i] = []
\t\tfor step in range(1,6):
\t\t\tvar pos := player+dir*step
\t\t\tif not position_in_bounds(pos) or not is_walkable(pos): break
\t\t\tcells.append(pos)
\t\tvar hits := jutsu_damage_positions(cells,int(ceil(base_damage*1.3)),name); message = "%s！ %d体に命中。" % [name,hits]
\telif name == "風遁・鎌風":
\t\tvar cells: Array[Vector2i] = []
\t\tfor side in [-1,0,1]:
\t\t\tvar side_dir := Vector2i(clampi(dir.x + (-dir.y)*side,-1,1),clampi(dir.y + dir.x*side,-1,1))
\t\t\tfor step in range(1,3): cells.append(player+side_dir*step)
\t\tvar hits := jutsu_damage_positions(cells,base_damage,name); message = "%s！ %d体を斬った。" % [name,hits]
\telif name == "土遁・岩衝":
\t\tvar index := enemy_index_at(target); damage_enemy_with_projectile(index,int(ceil(base_damage*1.2)),name)
\t\tvar survivor := enemy_index_at(target)
\t\tif survivor >= 0: knockback_enemy(survivor,dir,2)
\t\tmessage = "%s！ 敵を押し戻した。" % name
\telif name == "雷遁・迅雷":
\t\tvar index := enemy_index_at(target); damage_enemy_with_projectile(index,int(ceil(base_damage*1.5)),name)
\t\tvar survivor := enemy_index_at(target)
\t\tif survivor >= 0 and rng.randi_range(1,100) <= 30: enemies[survivor]["bound"] = maxi(1,int(enemies[survivor].get("bound",0)))
\t\tmessage = "%s！" % name
\telif name == "水遁・水牢":
\t\tvar index := enemy_index_at(target); damage_enemy_with_projectile(index,maxi(1,int(base_damage*0.8)),name)
\t\tvar survivor := enemy_index_at(target)
\t\tif survivor >= 0: enemies[survivor]["bound"] = maxi(3,int(enemies[survivor].get("bound",0)))
\t\tmessage = "%s！ 3ターン拘束。" % name
\telif name == "爆炎陣":
\t\tvar cells: Array[Vector2i] = []
\t\tfor enemy in enemies:
\t\t\tvar pos: Vector2i = enemy["pos"]
\t\t\tif maxi(absi(pos.x-target.x),absi(pos.y-target.y)) <= 2: cells.append(pos)
\t\tvar hits := jutsu_damage_positions(cells,int(ceil(base_damage*1.5)),name); message = "%s！ %d体を巻き込んだ。" % [name,hits]
\telif name == "影縛り":
\t\tvar index := enemy_index_at(target); enemies[index]["bound"] = rng.randi_range(2,4); message = "%s！ %dターン拘束。" % [name,int(enemies[index]["bound"])]
\tjutsu_menu = false; jutsu_targeting = ""; end_turn()


func cast_direct_jutsu(name: String) -> void:
\tif not spend_jutsu_energy(name): return
\tif name == "影刃乱舞":
\t\tvar cells: Array[Vector2i] = []
\t\tfor dy in range(-1,2):
\t\t\tfor dx in range(-1,2):
\t\t\t\tif dx != 0 or dy != 0: cells.append(player+Vector2i(dx,dy))
\t\tvar hits := jutsu_damage_positions(cells,int(ceil((attack_power+weapon_attack_bonus())*1.2)),name); message = "%s！ %d体に命中。" % [name,hits]
\telif name == "隠れ身": hidden_mode = true; message = "隠れ身。1ターン敵に狙われない。"
\telif name == "忍足": trap_sense_steps = 30; message = "忍足。30歩罠を見抜く。"
\telif name == "疾風歩": swift_steps = 3; message = "疾風歩。3回素早く移動できる。"
\telif name == "煙遁": smoke_turns = 3; message = "煙遁。3ターン敵を惑わせる。"
\telif name == "透視": jutsu_vision_steps = 30; message = "透視。30歩敵と道具を見通す。"
\telif name == "影分身": clone_active = true; clone_pos = player; clone_steps_left = 30; message = "影分身。30歩敵を引きつける。"
\tjutsu_menu = false; jutsu_targeting = ""; end_turn()


func choose_jutsu_to_cast(name: String) -> void:
\tif name not in learned_jutsu: return
\tif bool(JUTSU_DATA[name].get("target",false)):
\t\tjutsu_targeting = name; jutsu_menu = false; message = "対象を選ぶ。"
\telse: cast_direct_jutsu(name)
\tqueue_redraw()


func portrait_world_from_screen(pos: Vector2) -> Vector2i:
\tvar origin := portrait_camera_origin()
\treturn origin + Vector2i(int(floor((pos.x-48.0)/48.0)),int(floor((pos.y-207.0)/48.0)))


func handle_jutsu_touch(pos: Vector2) -> void:
\tif Rect2(500,780,170,50).has_point(pos): close_jutsu_menu(); return
\tfor i in range(learned_jutsu.size()):
\t\tvar column := i%2; var row := int(i/2); var rect := Rect2(40+column*330,300+row*82,310,68)
\t\tif rect.has_point(pos): choose_jutsu_to_cast(learned_jutsu[i]); return


func handle_jutsu_learning_touch(pos: Vector2) -> void:
\tfor i in range(pending_jutsu_choices.size()):
\t\tif Rect2(80,410+i*120,560,96).has_point(pos): learn_jutsu(pending_jutsu_choices[i]); return
'''
s = s.replace(jutsu_helpers_anchor, "\n" + jutsu_helpers.rstrip() + jutsu_helpers_anchor, 1)

# Walking counts down detection effects and allows three swift moves without an enemy turn.
walk_anchor = '''func on_player_walked() -> void:
\ttrigger_player_floor_trap()
\tif not clone_active: return'''
if walk_anchor not in s:
    raise SystemExit("STEP90 walked effect anchor failed")
s = s.replace(walk_anchor, '''func on_player_walked() -> void:
\ttrigger_player_floor_trap()
\tif trap_sense_steps > 0: trap_sense_steps -= 1
\tif jutsu_vision_steps > 0: jutsu_vision_steps -= 1
\tif not clone_active: return''', 1)

trap_trigger_anchor = '''\tvar trap: Dictionary = placed_traps[index]
\tplaced_traps.remove_at(index)
\tactivate_floor_trap(str(trap.get("type", "木矢の罠")))'''
if trap_trigger_anchor not in s:
    raise SystemExit("STEP90 ninja foot trap anchor failed")
s = s.replace(trap_trigger_anchor, '''\tvar trap: Dictionary = placed_traps[index]
\tif trap_sense_steps > 0 and rng.randi_range(1,100) <= 50:
\t\tplaced_traps.remove_at(index); message = "%sを見抜いて回避した。" % str(trap.get("type","罠")); return
\tplaced_traps.remove_at(index)
\tactivate_floor_trap(str(trap.get("type", "木矢の罠")))''', 1)

move_end_anchor = '''\tend_turn()
\tif not in_village and player == stairs_pos:
\t\trequest_stairs_confirmation()'''
if move_end_anchor not in s:
    raise SystemExit("STEP90 swift move anchor failed")
s = s.replace(move_end_anchor, '''\tif swift_steps > 0:
\t\tswift_steps -= 1
\t\tmessage = "疾風歩。残り%d回。" % swift_steps
\telse: end_turn()
\tif not in_village and player == stairs_pos:
\t\trequest_stairs_confirmation()''', 1)

# Save and load all learned techniques and active effects.
save_anchor = '\t\t"ninja_energy": ninja_energy,\n'
if save_anchor not in s:
    raise SystemExit("STEP90 save anchor failed")
s = s.replace(save_anchor, save_anchor + '''\t\t"learned_jutsu": learned_jutsu,
\t\t"pending_jutsu_choices": pending_jutsu_choices,
\t\t"trap_sense_steps": trap_sense_steps,
\t\t"swift_steps": swift_steps,
\t\t"jutsu_vision_steps": jutsu_vision_steps,
''', 1)

load_anchor = '\tninja_energy = clamp(int(data.get("ninja_energy", perm_ninja_energy)), 0, 100)\n'
if load_anchor not in s:
    raise SystemExit("STEP90 load anchor failed")
s = s.replace(load_anchor, load_anchor + '''\tlearned_jutsu = sanitize_jutsu_list(data.get("learned_jutsu", []))
\tpending_jutsu_choices = sanitize_jutsu_list(data.get("pending_jutsu_choices", []))
\ttrap_sense_steps = clampi(int(data.get("trap_sense_steps",0)),0,30)
\tswift_steps = clampi(int(data.get("swift_steps",0)),0,3)
\tjutsu_vision_steps = clampi(int(data.get("jutsu_vision_steps",0)),0,30)
\tjutsu_menu = false; jutsu_targeting = ""
''', 1)

capture_anchor = '\t\t"ninja_energy": ninja_energy, "run_souls": run_souls, "run_coins": run_coins,\n'
if capture_anchor not in s:
    raise SystemExit("STEP90 debug capture anchor failed")
s = s.replace(capture_anchor, capture_anchor + '\t\t"learned_jutsu": learned_jutsu.duplicate(), "pending_jutsu_choices": pending_jutsu_choices.duplicate(), "trap_sense_steps": trap_sense_steps, "swift_steps": swift_steps, "jutsu_vision_steps": jutsu_vision_steps,\n', 1)

restore_anchor = '\tninja_energy = int(state["ninja_energy"])\n'
if restore_anchor not in s:
    raise SystemExit("STEP90 debug restore anchor failed")
s = s.replace(restore_anchor, restore_anchor + '\tlearned_jutsu = sanitize_jutsu_list(state.get("learned_jutsu", [])); pending_jutsu_choices = sanitize_jutsu_list(state.get("pending_jutsu_choices", [])); trap_sense_steps = int(state.get("trap_sense_steps",0)); swift_steps = int(state.get("swift_steps",0)); jutsu_vision_steps = int(state.get("jutsu_vision_steps",0)); jutsu_menu = false; jutsu_targeting = ""\n', 1)

# Touching the ninja-energy meter opens techniques. Choices block other input.
press_anchor = '''func handle_press_portrait(pos: Vector2) -> void: # STEP64_CONTROLS_PATCH_APPLIED
\tif in_village:'''
if press_anchor not in s:
    raise SystemExit("STEP90 portrait input anchor failed")
s = s.replace(press_anchor, '''func handle_press_portrait(pos: Vector2) -> void: # STEP64_CONTROLS_PATCH_APPLIED
\tif not pending_jutsu_choices.is_empty(): handle_jutsu_learning_touch(pos); return
\tif jutsu_menu: handle_jutsu_touch(pos); return
\tif not jutsu_targeting.is_empty():
\t\tif Rect2(48,207,624,432).has_point(pos): cast_targeted_jutsu(jutsu_targeting,portrait_world_from_screen(pos))
\t\telse: jutsu_targeting = ""; message = "術を取り消した。"; queue_redraw()
\t\treturn
\tif in_village:''', 1)

meter_touch_anchor = '\tif Rect2(22,662,76,76).has_point(pos): toggle_map_visibility(); return\n'
if meter_touch_anchor not in s:
    raise SystemExit("STEP90 meter touch anchor failed")
s = s.replace(meter_touch_anchor, '\tif Rect2(476,112,172,68).has_point(pos): open_jutsu_menu(); return\n' + meter_touch_anchor, 1)

# Target cells and sensed traps are drawn on the dungeon map.
tile_loop_anchor = '''\tfor item in items:
\t\tvar ip: Vector2i = item["pos"]'''
if tile_loop_anchor not in s:
    raise SystemExit("STEP90 target draw anchor failed")
s = s.replace(tile_loop_anchor, '''\tif not jutsu_targeting.is_empty():
\t\tvar max_range := int(JUTSU_DATA[jutsu_targeting].get("range",0))
\t\tfor y in range(-max_range,max_range+1):
\t\t\tfor x in range(-max_range,max_range+1):
\t\t\t\tvar target := player+Vector2i(x,y)
\t\t\t\tif portrait_cell_in_view(target) and jutsu_target_valid(jutsu_targeting,target): draw_rect(Rect2(portrait_cell_center(target)-Vector2(22,22),Vector2(44,44)),Color(0.55,0.28,0.92,0.28),true)
\tif trap_sense_steps > 0:
\t\tfor trap in placed_traps:
\t\t\tif typeof(trap) == TYPE_DICTIONARY:
\t\t\t\tvar tp: Vector2i = trap.get("pos",Vector2i(-1,-1))
\t\t\t\tif portrait_cell_in_view(tp) and is_visible_cell(tp): draw_entity_visual(portrait_cell_center(tp),"trap","罠",18,Color("#e0a35c"),PTILE)
\tfor item in items:
\t\tvar ip: Vector2i = item["pos"]''', 1)

overlay_anchor = '''\tif inventory_menu:
\t\tdraw_inventory_overlay(true)
\telif checkout_prompt or stairs_prompt or ad_menu:
\t\tdraw_modal_overlay_portrait()'''
if overlay_anchor not in s:
    raise SystemExit("STEP90 overlay anchor failed")
s = s.replace(overlay_anchor, '''\tif not pending_jutsu_choices.is_empty(): draw_jutsu_learning_overlay()
\telif jutsu_menu: draw_jutsu_overlay()
\telif inventory_menu: draw_inventory_overlay(true)
\telif checkout_prompt or stairs_prompt or ad_menu: draw_modal_overlay_portrait()''', 1)

draw_anchor = "\nfunc draw_mobile_controls_portrait() -> void:\n"
if draw_anchor not in s:
    raise SystemExit("STEP90 overlay functions anchor failed")
draw_helpers = '''
func draw_jutsu_overlay() -> void:
\tdraw_rect(Rect2(20,220,680,640),Color(0.03,0.04,0.08,0.98)); draw_rect(Rect2(20,220,680,640),Color("#9b78e8"),false,3.0)
\tdraw_ui_text(Vector2(46,268),"術一覧　忍気%d" % ninja_energy,HORIZONTAL_ALIGNMENT_LEFT,-1,27,Color.WHITE)
\tfor i in range(learned_jutsu.size()):
\t\tvar column := i%2; var row := int(i/2); var rect := Rect2(40+column*330,300+row*82,310,68); var name := learned_jutsu[i]; var cost := jutsu_cost(name)
\t\tdraw_panel(rect,Color("#182039"),Color("#765ac2"),1.5)
\t\tdraw_ui_text(rect.position+Vector2(12,26),"%s　%d" % [name,cost],HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color.WHITE if ninja_energy>=cost else Color("#777777"))
\t\tdraw_ui_text(rect.position+Vector2(12,52),str(JUTSU_DATA[name].get("desc","")),HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color("#cfc9df"))
\tvar close := Rect2(500,780,170,50); draw_panel(close,Color("#202632"),Color("#687786")); draw_ui_text(close.position+Vector2(0,34),"戻る",HORIZONTAL_ALIGNMENT_CENTER,close.size.x,18,Color.WHITE)


func draw_jutsu_learning_overlay() -> void:
\tdraw_rect(Rect2(40,300,640,520),Color(0.03,0.04,0.08,0.98)); draw_rect(Rect2(40,300,640,520),Color("#e2c45f"),false,3.0)
\tdraw_ui_text(Vector2(80,350),"レベルアップ！ 術を1つ選ぶ",HORIZONTAL_ALIGNMENT_LEFT,-1,27,Color.WHITE)
\tfor i in range(pending_jutsu_choices.size()):
\t\tvar name := pending_jutsu_choices[i]; var rect := Rect2(80,410+i*120,560,96)
\t\tdraw_panel(rect,Color("#182039"),Color("#9b78e8"),2.0)
\t\tdraw_ui_text(rect.position+Vector2(20,38),"%s　忍気%d" % [name,jutsu_cost(name)],HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color.WHITE)
\t\tdraw_ui_text(rect.position+Vector2(20,73),str(JUTSU_DATA[name].get("desc","")),HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("#d9d3e8"))
'''
s = s.replace(draw_anchor, "\n" + draw_helpers.rstrip() + draw_anchor, 1)

# Vision shows entities on the minimap without revealing unvisited terrain.
s = s.replace('if map_cell_was_explored(enemy_pos):\n\t\t\tdraw_circle', 'if map_cell_was_explored(enemy_pos) or jutsu_vision_steps > 0:\n\t\t\tdraw_circle', 1)
s = s.replace('if map_cell_was_explored(item_pos):\n\t\t\tdraw_circle', 'if map_cell_was_explored(item_pos) or jutsu_vision_steps > 0:\n\t\t\tdraw_circle', 1)

test_anchor = "\nfunc debug_test_step89_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP90 regression anchor failed")
test_func = '''
func debug_test_step90_contract() -> String:
\tvar catalog_ok := JUTSU_ORDER.size()==14 and JUTSU_DATA.size()==14 and JUTSU_LEARN_LEVELS.size()==10
\tvar costs_ok := jutsu_cost("隠れ身")==10 and jutsu_cost("爆炎陣")==40 and int(JUTSU_DATA["火遁・火走り"]["range"])==5
\tvar save_data := build_run_state(); var save_ok := save_data.has("learned_jutsu") and save_data.has("trap_sense_steps")
\treturn "PASS 術14種・三択習得・忍気使用保存" if catalog_ok and costs_ok and save_ok else "FAIL 術習得システム"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step89_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP90 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step90_contract(),\n", 1)

required = [
    "STEP90_JUTSU_LEARNING_SYSTEM_APPLIED", "const JUTSU_DATA", "func prepare_jutsu_choices(",
    "func cast_targeted_jutsu(", "func draw_jutsu_overlay(",
    '"learned_jutsu": learned_jutsu', "PASS 術14種・三択習得・忍気使用保存",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP90 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP90 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP90_JUTSU_LEARNING_SYSTEM PASS")

