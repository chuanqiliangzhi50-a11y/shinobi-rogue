from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP91_JUTSU_IDLE_STATUS_APPLIED" in s:
    print("STEP91_JUTSU_IDLE_STATUS PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP90_JUTSU_LEARNING_SYSTEM_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP91 requires STEP90")
s = s.replace(marker, marker + "# STEP91_JUTSU_IDLE_STATUS_APPLIED\n", 1)

glyph_anchor = '\t"侍": "res://art/step76_glyphs/u4f8d.svg"\n'
if glyph_anchor not in s:
    raise SystemExit("STEP91 glyph anchor failed")
status_glyphs = {
    "口": "u53e3.svg", "欄": "u6b04.svg", "経": "u7d4c.svg",
    "基": "u57fa.svg", "補": "u88dc.svg", "値": "u5024.svg",
    "＋": "uff0b.svg", "正": "u6b63.svg",
}
glyph_lines = "".join(f'\t"{ch}": "res://art/step76_glyphs/{filename}",\n' for ch, filename in status_glyphs.items())
s = s.replace(glyph_anchor, glyph_lines + glyph_anchor, 1)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP91 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 1)
    if end < 0:
        raise SystemExit(f"STEP91 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n\n" + s[end + 1:]


state_anchor = "var jutsu_menu := false\n"
if state_anchor not in s:
    raise SystemExit("STEP91 state anchor failed")
s = s.replace(state_anchor, state_anchor + "var status_menu := false\n", 1)

# Torneko-style grounded stepping: a four-beat weight shift with planted shadows.
replace_func("enemy_idle_visual_offset", '''func enemy_idle_visual_offset(enemy: Dictionary) -> Vector2:
\tvar seed := absi(str(enemy.get("name", "敵")).hash()) % 4
\tvar speed := 3.6 if bool(enemy.get("boss", false)) else 4.6
\tvar phase := (int(floor(enemy_idle_anim_time * speed)) + seed) % 4
\tvar stride := 0.45 if bool(enemy.get("boss", false)) else 0.8
\tif int(enemy.get("bound", 0)) > 0: stride *= 0.2
\tif phase == 0: return Vector2(-stride, 0.0)
\tif phase == 2: return Vector2(stride, 0.0)
\treturn Vector2(0.0, 0.35)''')

player_body = '''func draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
\tvar key := player_direction_key()
\tvar dir := Vector2(float(facing_dir.x), float(facing_dir.y))
\tif dir.length() < 0.1: dir = Vector2.DOWN
\tdir = dir.normalized()
\tvar running := dash_hold_active and dash_hold_repeating
\tvar draw_center := center
\tvar idle_phase := int(floor(enemy_idle_anim_time * 4.6)) % 4
\tif not running:
\t\tif idle_phase == 0: draw_center.x -= 0.8
\t\telif idle_phase == 2: draw_center.x += 0.8
\t\telse: draw_center.y += 0.35
\t\tdraw_grounded_step_marks(center, idle_phase, tile_size, Color(0.08,0.11,0.15,0.62))
\tif running:
\t\tvar now := float(Time.get_ticks_msec()) / 1000.0
\t\tdraw_center += dir * 2.2
\t\tdraw_center.y += sin(now * 28.0) * 1.8
\t\tdraw_dash_run_effect(center, tile_size, dir)
\tif player_direction_art.has(key):
\t\tvar tex: Texture2D = player_direction_art[key]
\t\tvar size: float = maxf(12.0, tile_size - 2.0)
\t\tif running:
\t\t\tfor ghost_i in range(2, 0, -1):
\t\t\t\tvar ghost_center := draw_center - dir * (float(ghost_i) * 8.0)
\t\t\t\tvar ghost_alpha := 0.10 + float(2 - ghost_i) * 0.07
\t\t\t\tdraw_texture_rect(tex, Rect2(ghost_center - Vector2(size, size) * 0.5, Vector2(size, size)), false, Color(0.70, 0.88, 1.0, ghost_alpha))
\t\tvar lean := 0.0 if running else (-0.012 if idle_phase == 0 else (0.012 if idle_phase == 2 else 0.0))
\t\tdraw_set_transform(draw_center, lean, Vector2.ONE)
\t\tdraw_texture_rect(tex, Rect2(Vector2(-size,-size)*0.5,Vector2(size,size)), false)
\t\tdraw_set_transform(Vector2.ZERO,0.0,Vector2.ONE)
\telse: draw_entity_visual(draw_center, "player", "忍", 21, Color("#ffffff"), tile_size)'''
player_start = s.find("func draw_player_facing_visual(")
player_end = s.find("\n\nconst UI_GLYPH_MAP := {", player_start)
if player_start < 0 or player_end < 0:
    raise SystemExit("STEP91 player draw boundary failed")
s = s[:player_start] + player_body.rstrip() + s[player_end:]

enemy_draw_anchor = '''func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tcenter += enemy_idle_visual_offset(enemy)'''
if enemy_draw_anchor not in s:
    raise SystemExit("STEP91 enemy draw anchor failed")
s = s.replace(enemy_draw_anchor, '''func draw_grounded_step_marks(center: Vector2, phase: int, tile_size: float, color: Color) -> void:
\tvar y := center.y + tile_size * 0.33
\tvar left_width := 7.0 if phase in [0,1] else 4.0
\tvar right_width := 7.0 if phase in [2,3] else 4.0
\tdraw_line(Vector2(center.x-9.0-left_width*0.5,y),Vector2(center.x-9.0+left_width*0.5,y),color,3.0)
\tdraw_line(Vector2(center.x+9.0-right_width*0.5,y),Vector2(center.x+9.0+right_width*0.5,y),color,3.0)


func draw_enemy_reference_visual(center: Vector2, enemy: Dictionary, tile_size: float) -> void:
\tvar seed := absi(str(enemy.get("name","敵")).hash()) % 4
\tvar speed := 3.6 if bool(enemy.get("boss",false)) else 4.6
\tvar idle_phase := (int(floor(enemy_idle_anim_time*speed))+seed)%4
\tdraw_grounded_step_marks(center,idle_phase,tile_size,Color(0.08,0.09,0.12,0.62))
\tcenter += enemy_idle_visual_offset(enemy)''', 1)

# Status and jutsu entry points are visible in the HUD without changing the 2x2 commands.
press_anchor = '''\tif jutsu_menu: handle_jutsu_touch(pos); return
\tif not jutsu_targeting.is_empty():'''
if press_anchor not in s:
    raise SystemExit("STEP91 portrait input anchor failed")
s = s.replace(press_anchor, '''\tif jutsu_menu: handle_jutsu_touch(pos); return
\tif status_menu: handle_status_touch(pos); return
\tif not jutsu_targeting.is_empty():''', 1)

meter_anchor = '''\tif Rect2(476,112,172,68).has_point(pos): open_jutsu_menu(); return
\tif Rect2(22,662,76,76).has_point(pos): toggle_map_visibility(); return'''
if meter_anchor not in s:
    raise SystemExit("STEP91 HUD touch anchor failed")
s = s.replace(meter_anchor, '''\tif Rect2(476,112,172,68).has_point(pos): open_jutsu_menu(); return
\tif Rect2(22,116,92,68).has_point(pos): open_status_menu(); return
\tif Rect2(22,662,76,76).has_point(pos): toggle_map_visibility(); return''', 1)

helper_anchor = "\nfunc handle_jutsu_touch(pos: Vector2) -> void:\n"
if helper_anchor not in s:
    raise SystemExit("STEP91 helper anchor failed")
status_helpers = '''
func open_status_menu() -> void:
\tstop_dash_hold(); center_hold_active = false; center_hold_elapsed = 0.0; center_hold_stepping = false
\tstatus_menu = true; message = "能力を確認する。"; queue_redraw()


func close_status_menu() -> void:
\tstatus_menu = false; message = "能力画面を閉じた。"; queue_redraw()


func handle_status_touch(pos: Vector2) -> void:
\tif Rect2(500,790,150,50).has_point(pos) or not Rect2(40,220,640,640).has_point(pos): close_status_menu()
'''
s = s.replace(helper_anchor, "\n" + status_helpers.rstrip() + helper_anchor, 1)

hud_anchor = '''\tdraw_ui_text(Vector2(34,143), "Lv.%d" % player_level, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#241d18"))
\tdraw_ui_text(Vector2(43,176), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#4b3524"))'''
if hud_anchor not in s:
    raise SystemExit("STEP91 level HUD anchor failed")
s = s.replace(hud_anchor, '''\tdraw_ui_text(Vector2(34,143), "Lv.%d" % player_level, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color("#241d18"))
\tdraw_ui_text(Vector2(82,130), "能力", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("#70441f"))
\tdraw_ui_text(Vector2(43,176), "%dF" % floor_no, HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#4b3524"))''', 1)

jutsu_hud_anchor = '''\tdraw_ui_text(Vector2(488,135), "忍気  %d" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
\tdraw_meter(Vector2(488,146), Vector2(146,14), ninja_energy, 100, Color("#8a61e8"))'''
if jutsu_hud_anchor not in s:
    raise SystemExit("STEP91 jutsu HUD anchor failed")
s = s.replace(jutsu_hud_anchor, '''\tdraw_ui_text(Vector2(488,135), "忍気  %d　術" % ninja_energy, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color.WHITE)
\tdraw_meter(Vector2(488,146), Vector2(146,14), ninja_energy, 100, Color("#8a61e8"))
\tdraw_ui_text(Vector2(488,176), "ここを押す", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#cbb8ff"))''', 1)

hint_anchor = '''\tdraw_ui_text(Vector2(116,744), "○長押し:足踏み回復　●:向き変更　長押し移動:駆ける", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#8f9aa8"))'''
if hint_anchor not in s:
    raise SystemExit("STEP91 hint anchor failed")
s = s.replace(hint_anchor, '''\tdraw_ui_text(Vector2(116,744), "忍気欄:術　Lv欄:能力　○長押し:足踏み", HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("#8f9aa8"))''', 1)

overlay_anchor = '''\tif not pending_jutsu_choices.is_empty(): draw_jutsu_learning_overlay()
\telif jutsu_menu: draw_jutsu_overlay()
\telif inventory_menu: draw_inventory_overlay(true)'''
if overlay_anchor not in s:
    raise SystemExit("STEP91 overlay anchor failed")
s = s.replace(overlay_anchor, '''\tif not pending_jutsu_choices.is_empty(): draw_jutsu_learning_overlay()
\telif jutsu_menu: draw_jutsu_overlay()
\telif status_menu: draw_status_overlay()
\telif inventory_menu: draw_inventory_overlay(true)''', 1)

draw_anchor = "\nfunc draw_jutsu_overlay() -> void:\n"
if draw_anchor not in s:
    raise SystemExit("STEP91 status draw anchor failed")
status_draw = '''
func draw_status_overlay() -> void:
\tvar weapon_data := equipped_weapon_data(); var armor_data := equipped_armor_data()
\tvar weapon_base := int(weapon_data.get("attack",0)); var armor_base := int(armor_data.get("defense",0))
\tvar weapon_strength := weapon_attack_bonus(); var armor_strength := armor_defense_bonus()
\tdraw_rect(Rect2(40,220,640,640),Color(0.025,0.035,0.06,0.985)); draw_rect(Rect2(40,220,640,640),Color("#d0a34c"),false,3.0)
\tdraw_ui_text(Vector2(72,270),"能力",HORIZONTAL_ALIGNMENT_LEFT,-1,30,Color("#f3dfaa"))
\tdraw_ui_text(Vector2(72,314),"レベル　%d　　経験値　%d/%d" % [player_level,player_exp,exp_needed_for_next_level()],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
\tdraw_ui_text(Vector2(72,350),"HP　%d/%d　　満腹　%d" % [hp,max_hp,hunger],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE)
\tdraw_ui_text(Vector2(72,386),"攻撃力　%d　　防御力　%d" % [attack_power+weapon_strength,defense_power+armor_strength],HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("#d9e7f6"))
\tdraw_line(Vector2(72,414),Vector2(648,414),Color("#59687a"),2.0)
\tdraw_ui_text(Vector2(72,456),"武器　%s" % equipment_display_name(equipped_weapon,equipped_weapon_bonus),HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color("#f0d77c"))
\tdraw_ui_text(Vector2(72,502),"強さ　%d" % weapon_strength,HORIZONTAL_ALIGNMENT_LEFT,-1,28,Color.WHITE)
\tdraw_ui_text(Vector2(240,500),"基本%d ＋ 補正%d" % [weapon_base,equipped_weapon_bonus],HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#aeb9c8"))
\tdraw_ui_text(Vector2(72,548),"防具　%s" % equipment_display_name(equipped_armor,equipped_armor_bonus),HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color("#8fd1ea"))
\tdraw_ui_text(Vector2(72,594),"強さ　%d" % armor_strength,HORIZONTAL_ALIGNMENT_LEFT,-1,28,Color.WHITE)
\tdraw_ui_text(Vector2(240,592),"基本%d ＋ 補正%d" % [armor_base,equipped_armor_bonus],HORIZONTAL_ALIGNMENT_LEFT,-1,16,Color("#aeb9c8"))
\tdraw_line(Vector2(72,622),Vector2(648,622),Color("#59687a"),2.0)
\tdraw_ui_text(Vector2(72,664),"忍気　%d/100　　習得術　%d" % [ninja_energy,learned_jutsu.size()],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("#cbb8ff"))
\tdraw_ui_text(Vector2(72,704),"武器と防具の強さは補正込み。",HORIZONTAL_ALIGNMENT_LEFT,-1,15,Color("#aeb9c8"))
\tvar close := Rect2(500,790,150,50); draw_panel(close,Color("#202632"),Color("#687786")); draw_ui_text(close.position+Vector2(0,34),"戻る",HORIZONTAL_ALIGNMENT_CENTER,close.size.x,18,Color.WHITE)
'''
s = s.replace(draw_anchor, "\n" + status_draw.rstrip() + draw_anchor, 1)

test_anchor = "\nfunc debug_test_step90_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP91 regression anchor failed")
test_func = '''
func debug_test_step91_contract() -> String:
\tvar weapon_old := equipped_weapon; var weapon_bonus_old := equipped_weapon_bonus
\tvar armor_old := equipped_armor; var armor_bonus_old := equipped_armor_bonus
\tequipped_weapon = "忍刀"; equipped_weapon_bonus = 3; equipped_armor = "忍装束"; equipped_armor_bonus = 2
\tvar power_ok := weapon_attack_bonus()==int(WEAPON_CATALOG["忍刀"]["attack"])+3 and armor_defense_bonus()==int(ARMOR_CATALOG["忍装束"]["defense"])+2
\tvar grounded := enemy_idle_visual_offset({"name":"下忍","boss":false,"bound":0})
\tequipped_weapon = weapon_old; equipped_weapon_bonus = weapon_bonus_old; equipped_armor = armor_old; equipped_armor_bonus = armor_bonus_old
\treturn "PASS 術入口・接地足踏み・装備能力画面" if power_ok and grounded.y>=0.0 and grounded.y<=0.36 else "FAIL 術入口待機能力画面"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step90_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP91 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step91_contract(),\n", 1)

required = [
    "STEP91_JUTSU_IDLE_STATUS_APPLIED", "var status_menu := false", "func draw_status_overlay(",
    "func draw_grounded_step_marks(", "忍気欄:術", "Lv欄:能力", "PASS 術入口・接地足踏み・装備能力画面",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP91 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP91 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP91_JUTSU_IDLE_STATUS PASS")
