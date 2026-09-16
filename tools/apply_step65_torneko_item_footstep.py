from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

if 'STEP65_TORNEKO_ITEM_FOOTSTEP_APPLIED' in s:
    print('STEP65_TORNEKO_ITEM_FOOTSTEP PASS (already applied)')
    raise SystemExit(0)

# --- state / timing ---------------------------------------------------------
anchor = 'const DASH_HOLD_INTERVAL := 0.075\n'
if anchor not in s:
    raise SystemExit('STEP65 dash const anchor failed')
s = s.replace(anchor, anchor + '''const CENTER_HOLD_DELAY := 0.38 # STEP65_TORNEKO_ITEM_FOOTSTEP_APPLIED
const CENTER_STEP_INTERVAL := 0.11
''', 1)

anchor = 'var dash_hold_repeating := false\n'
if anchor not in s:
    raise SystemExit('STEP65 dash state anchor failed')
s = s.replace(anchor, anchor + '''var center_hold_active := false
var center_hold_elapsed := 0.0
var center_hold_stepping := false
var natural_heal_progress := 0.0
var skip_auto_pickup_once := false
var dash_pending_floor_pickup := false
''', 1)

# --- center circle: tap toggles facing mode; hold performs rapid wait turns ---
old = '''\t\tif d == Vector2i.ZERO:
\t\t\tstop_dash_hold()
\t\t\tdirection_only_mode = not direction_only_mode
\t\t\tmessage = "向き固定ON。方向キーで向きだけ変える。" if direction_only_mode else "向き固定OFF。"
\t\t\tqueue_redraw()
\t\t\treturn'''
new = '''\t\tif d == Vector2i.ZERO:
\t\t\tstop_dash_hold()
\t\t\tstart_center_hold()
\t\t\treturn'''
if old not in s:
    raise SystemExit('STEP65 center touch anchor failed')
s = s.replace(old, new, 1)

process_anchor = '\tqueue_redraw()\n\n\nfunc _unhandled_key_input(event: InputEvent) -> void:\n'
if process_anchor not in s:
    raise SystemExit('STEP65 process anchor failed')
process_insert = '''\tif center_hold_active and not direction_only_mode and not in_village and not checkout_prompt and not stairs_prompt and not ad_menu and not inventory_menu:
\t\tcenter_hold_elapsed += delta
\t\tif not center_hold_stepping and center_hold_elapsed >= CENTER_HOLD_DELAY:
\t\t\tcenter_hold_stepping = true
\t\t\tcenter_hold_elapsed = 0.0
\t\t\tfootstep_once()
\t\telif center_hold_stepping and center_hold_elapsed >= CENTER_STEP_INTERVAL:
\t\t\tcenter_hold_elapsed = 0.0
\t\t\tfootstep_once()
\tqueue_redraw()


func _unhandled_key_input(event: InputEvent) -> void:
'''
s = s.replace(process_anchor, process_insert, 1)

# Touch release must distinguish a short center tap from a long footstep hold,
# and a short direction tap from a held dash.
release_old = '''\t\telse:
\t\t\thide_hold_active = false
\t\t\tstop_dash_hold()'''
release_new = '''\t\telse:
\t\t\thide_hold_active = false
\t\t\tfinish_center_hold()
\t\t\tfinish_dash_hold_release()'''
release_count = s.count(release_old)
if release_count < 2:
    raise SystemExit(f'STEP65 touch release anchors failed: {release_count}')
s = s.replace(release_old, release_new, 2)

helper_anchor = '\n\nfunc stop_dash_hold() -> void:\n'
if helper_anchor not in s:
    raise SystemExit('STEP65 stop dash anchor failed')
center_helpers = '''

func start_center_hold() -> void:
\tcenter_hold_active = true
\tcenter_hold_elapsed = 0.0
\tcenter_hold_stepping = false


func finish_center_hold() -> void:
\tif not center_hold_active:
\t\treturn
\tvar was_stepping := center_hold_stepping
\tcenter_hold_active = false
\tcenter_hold_elapsed = 0.0
\tcenter_hold_stepping = false
\tif was_stepping:
\t\treturn
\tdirection_only_mode = not direction_only_mode
\tmessage = "向き固定ON。方向キーで向きだけ変える。" if direction_only_mode else "向き固定OFF。"
\tqueue_redraw()


func footstep_once() -> void:
\tif in_village or hp <= 0:
\t\treturn
\tmessage = "その場で足踏みしている。"
\tend_turn()
\tif in_village or hp <= 0:
\t\treturn
\tif hunger <= 0:
\t\tnatural_heal_progress = 0.0
\t\treturn
\tif hp >= max_hp:
\t\tnatural_heal_progress = 0.0
\t\treturn
\t# Torneko-style natural recovery: roughly MaxHP / 150 each elapsed turn.
\tnatural_heal_progress += float(max_hp) / 150.0
\tvar heal := int(floor(natural_heal_progress))
\tif heal > 0:
\t\thp = mini(max_hp, hp + heal)
\t\tnatural_heal_progress -= float(heal)

'''
s = s.replace(helper_anchor, center_helpers + helper_anchor, 1)

# --- dash item behavior -----------------------------------------------------
# A quick tap onto an adjacent item still auto-picks it. Holding the direction
# button turns that move into a dash and leaves the item under the player.
stop_anchor = '''func stop_dash_hold() -> void:
\tdash_hold_active = false
\tdash_hold_dir = Vector2i.ZERO
\tdash_hold_elapsed = 0.0
\tdash_hold_repeating = false
'''
if stop_anchor not in s:
    raise SystemExit('STEP65 stop dash body anchor failed')
stop_repl = stop_anchor + '''\tdash_pending_floor_pickup = false


func finish_dash_hold_release() -> void:
\tvar quick_item_tap := dash_hold_active and dash_pending_floor_pickup and not dash_hold_repeating and cell_has_item(player)
\tstop_dash_hold()
\tif quick_item_tap:
\t\tpickup(false)
'''
s = s.replace(stop_anchor, stop_repl, 1)

start_dash = '''func start_dash_hold(dir: Vector2i) -> void:
\tstop_dash_hold()
\tif dir == Vector2i.ZERO:
\t\treturn
\tdash_hold_active = true
\tdash_hold_dir = dir
\tvar target := player + dir
\tvar blocked := dash_blocker_ahead(dir)
\tvar target_has_item := (not blocked) and cell_has_item(target)
\tif target_has_item:
\t\tskip_auto_pickup_once = true
\t\tdash_pending_floor_pickup = true
\tvar stop_after_tap := blocked or target == stairs_pos
\ttry_move(dir)
\tif stop_after_tap or in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:
\t\tstop_dash_hold()
'''
s, n = re.subn(r'func start_dash_hold\(dir: Vector2i\) -> void:\n.*?(?=\n\nfunc dash_hold_step)', start_dash.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 start dash replace failed: {n}')

dash_step = '''func dash_hold_step() -> void:
\tif not dash_hold_active or dash_hold_dir == Vector2i.ZERO:
\t\treturn
\tif in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:
\t\tstop_dash_hold()
\t\treturn
\tif dash_pending_floor_pickup and cell_has_item(player):
\t\tdash_pending_floor_pickup = false
\t\tmessage = "%sの上に乗った。" % floor_item_name_at_player()
\t\tstop_dash_hold()
\t\treturn
\tif dash_enemy_nearby() or dash_blocker_ahead(dash_hold_dir):
\t\tstop_dash_hold()
\t\treturn
\tvar target := player + dash_hold_dir
\tif cell_has_item(target):
\t\tskip_auto_pickup_once = true
\t\ttry_move(dash_hold_dir)
\t\tif cell_has_item(player):
\t\t\tmessage = "%sの上に乗った。" % floor_item_name_at_player()
\t\tstop_dash_hold()
\t\treturn
\tvar stop_after_move := target == stairs_pos
\ttry_move(dash_hold_dir)
\tif stop_after_move or in_village or checkout_prompt or stairs_prompt or ad_menu or inventory_menu:
\t\tstop_dash_hold()
'''
s, n = re.subn(r'func dash_hold_step\(\) -> void:\n.*?(?=\n\nfunc try_move)', dash_step.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 dash step replace failed: {n}')

# Movement respects the one-shot dash pickup suppression.
try_move = '''func try_move(dir: Vector2i) -> void:
\tif dir == Vector2i.ZERO:
\t\tend_turn()
\t\treturn
\tfacing_dir = Vector2i(clampi(dir.x, -1, 1), clampi(dir.y, -1, 1))
\tvar target = player + dir
\tif not is_walkable(target):
\t\tmessage = "壁だ。"
\t\tskip_auto_pickup_once = false
\t\treturn
\tfor i in range(enemies.size()):
\t\tif enemies[i]["pos"] == target:
\t\t\tattack_enemy(i)
\t\t\tskip_auto_pickup_once = false
\t\t\tend_turn()
\t\t\treturn
\tif shopkeeper.size() > 0 and shopkeeper.get("pos", Vector2i(-1, -1)) == target:
\t\tskip_auto_pickup_once = false
\t\tif shop_hostile:
\t\t\tmessage = "商人が道を塞いでいる。"
\t\telse:
\t\t\tmessage = "%s「代金を払っていきな」" % merchant_type
\t\treturn

\tvar was_inside = is_inside_shop(player)
\tplayer = target
\ton_player_walked()
\tif cell_has_item(player):
\t\tif skip_auto_pickup_once:
\t\t\tskip_auto_pickup_once = false
\t\telse:
\t\t\tpickup(false)
\telse:
\t\tskip_auto_pickup_once = false
\tvar now_inside = is_inside_shop(player)
\tif was_inside and not now_inside and unpaid_items.size() > 0:
\t\ttry_theft_escape()
\tend_turn()
\tif not in_village and player == stairs_pos:
\t\trequest_stairs_confirmation()
'''
s, n = re.subn(r'func try_move\(dir: Vector2i\) -> void:\n.*?(?=\n\nfunc attack_enemy)', try_move.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 try_move replace failed: {n}')

# --- floor item helpers / full inventory -----------------------------------
floor_helpers = '''func floor_item_index_at_player() -> int:
\tfor i in range(items.size()):
\t\tif typeof(items[i]) == TYPE_DICTIONARY and items[i].get("pos", Vector2i(-1, -1)) == player:
\t\t\treturn i
\treturn -1


func floor_item_name_at_player() -> String:
\tvar idx := floor_item_index_at_player()
\tif idx < 0:
\t\treturn "道具"
\treturn str(items[idx].get("name", "道具"))


func pickup(consume_turn: bool = true) -> void:
\tvar found := floor_item_index_at_player()
\tif found < 0:
\t\tmessage = "ここには何もない。"
\t\treturn
\tvar item: Dictionary = items[found]
\tvar item_name := str(item.get("name", ""))
\tif not bool(item.get("shop", false)) and not inventory_has_space_for(item_name):
\t\tmessage = "これ以上拾えない。道具で置く物を選び「拾う」。"
\t\treturn
\titems.remove_at(found)
\tif bool(item.get("shop", false)):
\t\tunpaid_items.append(item)
\t\tmessage = "%sを手に取った。未精算。" % item_name
\telse:
\t\tvar picked_count := maxi(1, int(item.get("count", 1)))
\t\tadd_inventory_item(item_name, false, picked_count)
\t\tmessage = "%s×%dを拾った。" % [item_name, picked_count] if picked_count > 1 else "%sを拾った。" % item_name
\tif consume_turn:
\t\tend_turn()
'''
s, n = re.subn(r'func pickup\(consume_turn: bool = true\) -> void:\n.*?(?=\n\nfunc is_projectile_name)', floor_helpers.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 pickup replace failed: {n}')

# Inventory floor action: when full, the selected carried item is put down and
# the item underfoot is picked up in the same turn.
inv_helper_anchor = '\n\nfunc handle_inventory_touch(pos: Vector2, portrait: bool) -> void:\n'
if inv_helper_anchor not in s:
    raise SystemExit('STEP65 inventory touch anchor failed')
inv_helpers = '''

func inventory_floor_pick_or_swap() -> void:
\tvar floor_idx := floor_item_index_at_player()
\tif floor_idx < 0:
\t\tmessage = "足元に道具はない。"
\t\tqueue_redraw()
\t\treturn
\tvar floor_item: Dictionary = items[floor_idx]
\tvar floor_name := str(floor_item.get("name", ""))
\tif bool(floor_item.get("shop", false)):
\t\tinventory_menu = false
\t\tpickup(true)
\t\treturn
\tif inventory_has_space_for(floor_name):
\t\tinventory_menu = false
\t\tpickup(true)
\t\treturn
\tvar inv_idx := inventory_selected - 2
\tif inv_idx < 0 or inv_idx >= inventory_items.size():
\t\tmessage = "置く道具を選ぶ。"
\t\tqueue_redraw()
\t\treturn
\tvar dropped: Dictionary = inventory_items[inv_idx].duplicate(true)
\tvar dropped_name := str(dropped.get("name", ""))
\tvar dropped_count := maxi(1, int(dropped.get("count", 1)))
\titems.remove_at(floor_idx)
\tinventory_items.remove_at(inv_idx)
\tif equipped_projectile == dropped_name:
\t\tequipped_projectile = ""
\tvar floor_count := maxi(1, int(floor_item.get("count", 1)))
\tadd_inventory_item(floor_name, false, floor_count)
\titems.append({"pos": player, "name": dropped_name, "count": dropped_count, "price": 0, "shop": false})
\tinventory_selected = clampi(inventory_selected, 0, maxi(0, inventory_entry_count() - 1))
\tinventory_sync_scroll()
\tinventory_menu = false
\tmessage = "%sを置いて%sを拾った。" % [dropped_name, floor_name]
\tend_turn()

'''
s = s.replace(inv_helper_anchor, inv_helpers + inv_helper_anchor, 1)

inventory_touch = '''func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:
\tvar panel_x := 60.0 if portrait else 270.0
\tvar panel_y := 225.0 if portrait else 120.0
\tvar row_h := 46.0
\tif Rect2(panel_x + 500.0, panel_y + 74.0, 40.0, 40.0).has_point(pos):
\t\tinventory_scroll(-1); return
\tif Rect2(panel_x + 500.0, panel_y + 74.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h, 40.0, 40.0).has_point(pos):
\t\tinventory_scroll(1); return
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index := inventory_scroll_offset + row
\t\tif index >= inventory_entry_count(): break
\t\tvar r := Rect2(panel_x + 20.0, panel_y + 74.0 + row * row_h, 470.0, 40.0)
\t\tif r.has_point(pos):
\t\t\tinventory_selected = index; inventory_sync_scroll(); queue_redraw(); return
\tvar action_y := panel_y + 420.0
\tvar actions = [["equip", panel_x + 12.0], ["use", panel_x + 118.0], ["identify", panel_x + 224.0], ["floor", panel_x + 330.0], ["back", panel_x + 436.0]]
\tfor action in actions:
\t\tif Rect2(float(action[1]), action_y, 96.0, 52.0).has_point(pos):
\t\t\tmatch str(action[0]):
\t\t\t\t"equip": inventory_equip_selected()
\t\t\t\t"use": inventory_use_selected()
\t\t\t\t"identify": inventory_identify_selected()
\t\t\t\t"floor": inventory_floor_pick_or_swap()
\t\t\t\t"back": close_inventory()
\t\t\treturn
'''
s, n = re.subn(r'func handle_inventory_touch\(pos: Vector2, portrait: bool\) -> void:\n.*?(?=\n\nfunc inventory_display_name)', inventory_touch.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 inventory touch replace failed: {n}')

inventory_draw = '''func draw_inventory_overlay(portrait: bool) -> void:
\tvar panel_x := 60.0 if portrait else 270.0
\tvar panel_y := 225.0 if portrait else 120.0
\tvar panel_w := 560.0
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color(0.05, 0.07, 0.09, 0.98))
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color("#e4cf7a"), false, 2.0)
\tdraw_ui_text(Vector2(panel_x + 22.0, panel_y + 48.0), "道具 %d/20" % inventory_items.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color.WHITE)
\tvar floor_idx := floor_item_index_at_player()
\tif floor_idx >= 0:
\t\tdraw_ui_text(Vector2(panel_x + 300.0, panel_y + 48.0), "%sの上" % str(items[floor_idx].get("name", "道具")), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("#f1c95b"))
\tvar row_h := 46.0
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index := inventory_scroll_offset + row
\t\tif index >= inventory_entry_count(): break
\t\tvar r := Rect2(panel_x + 20.0, panel_y + 74.0 + row * row_h, 470.0, 40.0)
\t\tdraw_rect(r, Color("#343527") if index == inventory_selected else Color("#202934"))
\t\tdraw_rect(r, Color("#dbc66e") if index == inventory_selected else Color("#4c5865"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(12, 27), inventory_display_name(index), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar max_offset: int = maxi(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tif inventory_scroll_offset > 0: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0), "↑", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tif inventory_scroll_offset < max_offset: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h), "↓", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tvar action_y := panel_y + 420.0
\tvar labels = [["装備", panel_x + 12.0], ["使用", panel_x + 118.0], ["識別", panel_x + 224.0], ["拾う", panel_x + 330.0], ["戻る", panel_x + 436.0]]
\tfor action in labels:
\t\tvar r := Rect2(float(action[1]), action_y, 96.0, 52.0)
\t\tdraw_rect(r, Color("#252c35")); draw_rect(r, Color("#596575"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(14, 34), str(action[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
'''
s, n = re.subn(r'func draw_inventory_overlay\(portrait: bool\) -> void:\n.*?(?=\nfunc item_shop_price)', inventory_draw.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 inventory draw replace failed: {n}')

# --- projectile landing: never merge/disappear on an occupied floor tile ----
projectile_drop = '''func find_nearest_item_drop_cell(origin: Vector2i) -> Vector2i:
\tvar max_radius := maxi(MAP_W, MAP_H)
\tfor radius in range(max_radius + 1):
\t\tfor dy in range(-radius, radius + 1):
\t\t\tfor dx in range(-radius, radius + 1):
\t\t\t\tif maxi(abs(dx), abs(dy)) != radius:
\t\t\t\t\tcontinue
\t\t\t\tvar p2 := origin + Vector2i(dx, dy)
\t\t\t\tif not position_in_bounds(p2) or not is_walkable(p2):
\t\t\t\t\tcontinue
\t\t\t\tif p2 == stairs_pos or cell_has_item(p2):
\t\t\t\t\tcontinue
\t\t\t\treturn p2
\treturn Vector2i(-1, -1)


func drop_projectile_on_floor(name: String, p: Vector2i) -> void:
\tvar drop_pos := find_nearest_item_drop_cell(p)
\tif drop_pos == Vector2i(-1, -1):
\t\t# Extremely defensive fallback: preserve the projectile instead of losing it.
\t\tadd_inventory_item(name, true, 1)
\t\treturn
\titems.append({"pos": drop_pos, "name": name, "count": 1, "price": 0, "shop": false})
'''
s, n = re.subn(r'func drop_projectile_on_floor\(name: String, p: Vector2i\) -> void:\n.*?(?=\n\nfunc consume_equipped_projectile)', projectile_drop.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'STEP65 projectile drop replace failed: {n}')

required = [
    'STEP65_TORNEKO_ITEM_FOOTSTEP_APPLIED',
    'func footstep_once() -> void:',
    'float(max_hp) / 150.0',
    'func find_nearest_item_drop_cell(origin: Vector2i) -> Vector2i:',
    'これ以上拾えない。道具で置く物を選び「拾う」。',
    'func inventory_floor_pick_or_swap() -> void:',
    'message = "%sの上に乗った。" % floor_item_name_at_player()',
    '["拾う", panel_x + 330.0]'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP65 verification failed: {needle}')
if s == original:
    raise SystemExit('STEP65 made no changes')

p.write_text(s, encoding='utf-8')
print('STEP65_TORNEKO_ITEM_FOOTSTEP PASS')
