from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP92_CONFIRM_SCROLL_STORAGE_APPLIED" in s:
    print("STEP92_CONFIRM_SCROLL_STORAGE PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP91_JUTSU_IDLE_STATUS_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP92 requires STEP91")
s = s.replace(marker, marker + "# STEP92_CONFIRM_SCROLL_STORAGE_APPLIED\n", 1)

glyph_anchor = '\t"侍": "res://art/step76_glyphs/u4f8d.svg"\n'
if glyph_anchor not in s:
    raise SystemExit("STEP92 glyph anchor failed")
step92_glyphs = {
    "外": "u5916.svg",
    "替": "u66ff.svg",
    "却": "u5374.svg",
}
glyph_lines = "".join(
    f'\t"{ch}": "res://art/step76_glyphs/{filename}",\n'
    for ch, filename in step92_glyphs.items()
)
s = s.replace(glyph_anchor, glyph_lines + glyph_anchor, 1)


def replace_func(name: str, body: str) -> None:
    global s
    start = s.find(f"func {name}(")
    if start < 0:
        raise SystemExit(f"STEP92 function anchor failed: {name}")
    end = s.find("\nfunc ", start + 1)
    if end < 0:
        raise SystemExit(f"STEP92 function end failed: {name}")
    s = s[:start] + body.rstrip() + "\n\n" + s[end + 1:]


state_anchor = "var fusion_scroll_offset := 0\n"
if state_anchor not in s:
    raise SystemExit("STEP92 state anchor failed")
s = s.replace(state_anchor, state_anchor + '''var jutsu_scroll_offset := 0
var list_touch_active := false
var list_touch_dragged := false
var list_touch_start := Vector2.ZERO
var list_scroll_drag_y := 0.0
var village_confirm_kind := ""
var village_confirm_source := ""
var village_confirm_index := -1
var village_confirm_label := ""
var village_confirm_price := 0
''', 1)

# Make the feet themselves alternate instead of floating the whole character.
player_start = s.find("func draw_player_facing_visual(")
player_end = s.find("\n\nconst UI_GLYPH_MAP := {", player_start)
if player_start < 0 or player_end < 0:
    raise SystemExit("STEP92 player boundary failed")
player_draw = '''func draw_stepping_region(texture: Texture2D, source: Rect2, center: Vector2, size: float, phase: int, tint: Color = Color.WHITE) -> void:
\tvar top_ratio := 0.70
\tvar top_source := Rect2(source.position,Vector2(source.size.x,source.size.y*top_ratio))
\tvar lower_y := source.position.y+source.size.y*top_ratio
\tvar lower_h := source.size.y*(1.0-top_ratio)
\tvar half_w := source.size.x*0.5
\tvar top_dest := Rect2(center-Vector2(size,size)*0.5,Vector2(size,size*top_ratio+1.0))
\tvar lower_dest_y := center.y-size*0.5+size*top_ratio
\tvar left_y := 2.8 if phase==0 else (-0.8 if phase==2 else 0.8)
\tvar right_y := 2.8 if phase==2 else (-0.8 if phase==0 else 0.8)
\tdraw_texture_rect_region(texture,top_dest,top_source,tint)
\tdraw_texture_rect_region(texture,Rect2(Vector2(center.x-size*0.5-0.8,lower_dest_y+left_y),Vector2(size*0.5+1.0,size*(1.0-top_ratio))),Rect2(Vector2(source.position.x,lower_y),Vector2(half_w,lower_h)),tint)
\tdraw_texture_rect_region(texture,Rect2(Vector2(center.x-0.2,lower_dest_y+right_y),Vector2(size*0.5+1.0,size*(1.0-top_ratio))),Rect2(Vector2(source.position.x+half_w,lower_y),Vector2(half_w,lower_h)),tint)


func draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
\tvar key := player_direction_key(); var dir := Vector2(float(facing_dir.x),float(facing_dir.y))
\tif dir.length()<0.1: dir=Vector2.DOWN
\tdir=dir.normalized()
\tvar running := dash_hold_active and dash_hold_repeating
\tvar draw_center := center; var idle_phase := int(floor(enemy_idle_anim_time*5.4))%4
\tif not running: draw_grounded_step_marks(center,idle_phase,tile_size,Color(0.08,0.11,0.15,0.72))
\tif running:
\t\tvar now := float(Time.get_ticks_msec())/1000.0
\t\tdraw_center += dir*2.2; draw_center.y += sin(now*28.0)*1.8; draw_dash_run_effect(center,tile_size,dir)
\tif player_direction_art.has(key):
\t\tvar tex: Texture2D = player_direction_art[key]; var size := maxf(12.0,tile_size-2.0)
\t\tif running:
\t\t\tfor ghost_i in range(2,0,-1):
\t\t\t\tvar ghost_center := draw_center-dir*(float(ghost_i)*8.0); var ghost_alpha := 0.10+float(2-ghost_i)*0.07
\t\t\t\tdraw_texture_rect(tex,Rect2(ghost_center-Vector2(size,size)*0.5,Vector2(size,size)),false,Color(0.70,0.88,1.0,ghost_alpha))
\t\tif running: draw_texture_rect(tex,Rect2(draw_center-Vector2(size,size)*0.5,Vector2(size,size)),false)
\t\telse: draw_stepping_region(tex,Rect2(0,0,tex.get_width(),tex.get_height()),draw_center,size,idle_phase)
\telse: draw_entity_visual(draw_center,"player","忍",21,Color("#ffffff"),tile_size)'''
s = s[:player_start] + player_draw.rstrip() + s[player_end:]

replace_func("enemy_idle_visual_offset", '''func enemy_idle_visual_offset(enemy: Dictionary) -> Vector2:
\tvar seed := absi(str(enemy.get("name","敵")).hash())%4
\tvar speed := 4.2 if bool(enemy.get("boss",false)) else 5.2
\tvar phase := (int(floor(enemy_idle_anim_time*speed))+seed)%4
\tvar stride := 0.25 if bool(enemy.get("boss",false)) else 0.45
\tif int(enemy.get("bound",0))>0: stride*=0.2
\tif phase==0: return Vector2(-stride,0.0)
\tif phase==2: return Vector2(stride,0.0)
\treturn Vector2.ZERO''')

replace_func("draw_grounded_step_marks", '''func draw_grounded_step_marks(center: Vector2, phase: int, tile_size: float, color: Color) -> void:
\tvar y := center.y+tile_size*0.34
\tvar left_width := 9.0 if phase in [0,1] else 4.0; var right_width := 9.0 if phase in [2,3] else 4.0
\tdraw_line(Vector2(center.x-9.0-left_width*0.5,y),Vector2(center.x-9.0+left_width*0.5,y),color,3.5)
\tdraw_line(Vector2(center.x+9.0-right_width*0.5,y),Vector2(center.x+9.0+right_width*0.5,y),color,3.5)
\tif phase==0: draw_circle(Vector2(center.x-15.0,y-1.0),2.2,Color(0.65,0.60,0.48,0.30))
\telif phase==2: draw_circle(Vector2(center.x+15.0,y-1.0),2.2,Color(0.65,0.60,0.48,0.30))''')

replace_func("draw_8dir_enemy_cell", '''func draw_8dir_enemy_cell(texture: Texture2D, row: int, direction: Vector2i, center: Vector2, tile_size: float, is_boss: bool) -> void:
\tvar column := enemy_direction_index(direction); var source := Rect2(float(column*128),float(row*128),128.0,128.0)
\tvar size := maxf(38.0,tile_size+(22.0 if is_boss else 15.0))
\tvar speed := 4.2 if is_boss else 5.2; var phase := (int(floor(enemy_idle_anim_time*speed))+row+column)%4
\tdraw_stepping_region(texture,source,center,size,phase)''')

# Route every long list through one touch-scroll path.
input_anchor = '''func _input(event: InputEvent) -> void:
\tif in_village and village_menu == "warehouse" and event is InputEventScreenTouch:'''
if input_anchor not in s:
    raise SystemExit("STEP92 input anchor failed")
s = s.replace(input_anchor, '''func _input(event: InputEvent) -> void:
\tif scrolling_list_active() and event is InputEventScreenTouch:
\t\tvar list_pos: Vector2 = event.position-content_offset()
\t\tif event.pressed:
\t\t\tlist_touch_active=true; list_touch_dragged=false; list_touch_start=list_pos; list_scroll_drag_y=0.0
\t\telse:
\t\t\tif list_touch_active and not list_touch_dragged: handle_press(list_pos)
\t\t\tlist_touch_active=false; list_touch_dragged=false; list_scroll_drag_y=0.0
\t\treturn
\tif scrolling_list_active() and event is InputEventScreenDrag and list_touch_active:
\t\tif event.position.distance_to(list_touch_start)>12.0: list_touch_dragged=true
\t\tlist_scroll_drag_y += event.relative.y
\t\tif abs(list_scroll_drag_y)>=30.0:
\t\t\tscroll_active_list(-1 if list_scroll_drag_y>0.0 else 1); list_scroll_drag_y=0.0
\t\treturn
\tif in_village and village_menu == "warehouse" and event is InputEventScreenTouch:''', 1)

helper_anchor = "\nfunc is_hide_button_position(pos: Vector2) -> bool:\n"
if helper_anchor not in s:
    raise SystemExit("STEP92 scroll helper anchor failed")
scroll_helpers = '''
func scrolling_list_active() -> bool:
\tif inventory_menu or jutsu_menu: return true
\treturn in_village and village_menu in ["warehouse_bag","warehouse_storage","weapon_fusion_bag","weapon_fusion_storage"] or (in_village and village_menu=="village_shop" and village_shop_mode!="choose")


func scroll_active_list(rows: int) -> void:
\tif jutsu_menu: jutsu_scroll_offset=clampi(jutsu_scroll_offset+rows,0,maxi(0,learned_jutsu.size()-6)); queue_redraw(); return
\tif inventory_menu: inventory_scroll(rows); return
\tif village_menu=="warehouse_bag": warehouse_bag_scroll=clampi(warehouse_bag_scroll+rows,0,warehouse_bag_max_scroll())
\telif village_menu=="warehouse_storage": warehouse_scroll_offset=clampi(warehouse_scroll_offset+rows,0,maxi(0,warehouse_items.size()-8))
\telif village_menu in ["weapon_fusion_bag","weapon_fusion_storage"]:
\t\tvar source := "bag" if village_menu=="weapon_fusion_bag" else "warehouse"; fusion_scroll(source,rows); return
\telif village_menu=="village_shop": village_shop_scroll(rows); return
\tqueue_redraw()


func draw_list_scrollbar(x: float, y: float, height: float, total: int, visible: int, offset: int) -> void:
\tif total<=visible: return
\tdraw_rect(Rect2(x,y,8.0,height),Color(0.16,0.19,0.23,0.9))
\tvar thumb_h := maxf(32.0,height*float(visible)/float(total)); var max_offset := maxi(1,total-visible)
\tvar thumb_y := y+(height-thumb_h)*float(clampi(offset,0,max_offset))/float(max_offset)
\tdraw_rect(Rect2(x-2.0,thumb_y,12.0,thumb_h),Color("#d3b35b"))
'''
s = s.replace(helper_anchor, "\n" + scroll_helpers.rstrip() + helper_anchor, 1)

# Warehouse bulk deposit and full-capacity messaging.
replace_func("store_selected_bag_items", '''func store_selected_bag_items() -> int:
\tvar indices: Array = warehouse_bag_selected.keys(); indices.sort(); indices.reverse()
\tvar moved := 0; var blocked := false
\tfor raw_index in indices:
\t\tvar index := int(raw_index)
\t\tif index<0 or index>=inventory_items.size(): continue
\t\tif warehouse_add_item(inventory_items[index]): inventory_items.remove_at(index); moved+=1
\t\telse: blocked=true
\twarehouse_bag_selected.clear(); warehouse_multi_sync()
\tif moved>0: save_meta()
\tmessage = "倉庫がいっぱいだ。" if blocked else "%d個を倉庫へ預けた。" % moved
\treturn moved''')

bulk_anchor = "\nfunc withdraw_selected_warehouse_items() -> int:\n"
if bulk_anchor not in s:
    raise SystemExit("STEP92 bulk anchor failed")
bulk_helpers = '''
func store_all_non_equipment() -> int:
\tvar moved := 0; var blocked := false; var remaining: Array = []
\tfor raw in inventory_items:
\t\tvar entry: Dictionary = raw; var name := str(entry.get("name",""))
\t\tif is_equipment_name(name): remaining.append(entry)
\t\telif warehouse_add_item(entry): moved+=1
\t\telse: remaining.append(entry); blocked=true
\tinventory_items=remaining; warehouse_bag_selected.clear(); warehouse_multi_sync()
\tif moved>0: save_meta()
\tif blocked: message="倉庫がいっぱいだ。"
\telif moved>0: message="装備品以外を全て預けた。"
\telse: message="預けられる道具がない。"
\tqueue_redraw(); return moved


func request_warehouse_sell_selected() -> void:
\tvar indices: Array = warehouse_store_selected.keys()
\tif indices.is_empty(): message="売る道具を選ぶ。"; queue_redraw(); return
\tvar total := 0
\tfor raw_index in indices:
\t\tvar index := int(raw_index)
\t\tif index>=0 and index<warehouse_items.size(): total += village_sell_price(warehouse_items[index])
\trequest_village_confirm("warehouse_sell","warehouse",-1,"選択%d点" % indices.size(),total)


func commit_warehouse_sell_selected() -> void:
\tvar indices: Array = warehouse_store_selected.keys(); indices.sort(); indices.reverse(); var total := 0; var sold := 0
\tfor raw_index in indices:
\t\tvar index := int(raw_index)
\t\tif index<0 or index>=warehouse_items.size(): continue
\t\ttotal += village_sell_price(warehouse_items[index]); warehouse_items.remove_at(index); sold+=1
\twarehouse_store_selected.clear(); warehouse_multi_sync(); coins+=total; save_meta()
\tmessage="%d点を%d銭で売った。" % [sold,total]; queue_redraw()
'''
s = s.replace(bulk_anchor, "\n" + bulk_helpers.rstrip() + bulk_anchor, 1)

# Shared yes/no confirmation for fusion, smithing, buying, and selling.
buy_start = s.find("func buy_village_shop_item(")
if buy_start < 0:
    raise SystemExit("STEP92 buy anchor failed")
confirm_helpers = '''func request_village_confirm(kind: String, source: String, index: int, label: String, price: int) -> void:
\tvillage_confirm_kind=kind; village_confirm_source=source; village_confirm_index=index; village_confirm_label=label; village_confirm_price=price; queue_redraw()


func clear_village_confirm() -> void:
\tvillage_confirm_kind=""; village_confirm_source=""; village_confirm_index=-1; village_confirm_label=""; village_confirm_price=0; queue_redraw()


func confirm_village_action(accepted: bool) -> void:
\tvar kind := village_confirm_kind; var source := village_confirm_source; var index := village_confirm_index
\tclear_village_confirm()
\tif not accepted: message="やめた。"; queue_redraw(); return
\tif kind=="buy": commit_village_buy(index)
\telif kind=="sell": commit_village_sell(index)
\telif kind=="fusion": commit_weapon_fusion(source,index)
\telif kind=="smith_weapon": commit_synthesize("weapon")
\telif kind=="smith_armor": commit_synthesize("armor")
\telif kind=="warehouse_sell": commit_warehouse_sell_selected()


func handle_village_confirm_touch(pos: Vector2) -> void:
\tif Rect2(150,560,190,68).has_point(pos): confirm_village_action(true)
\telif Rect2(380,560,190,68).has_point(pos): confirm_village_action(false)


func draw_village_action_confirm() -> void:
\tvar question := "合成しますか？"
\tif village_confirm_kind=="buy": question="買いますか？"
\telif village_confirm_kind in ["sell","warehouse_sell"]: question="売りますか？"
\tdraw_rect(Rect2(80,360,560,310),Color(0.025,0.035,0.05,0.985)); draw_rect(Rect2(80,360,560,310),Color("#d7bf66"),false,3.0)
\tdraw_ui_text(Vector2(120,418),question,HORIZONTAL_ALIGNMENT_LEFT,-1,29,Color.WHITE)
\tdraw_ui_text(Vector2(120,468),village_confirm_label.left(28),HORIZONTAL_ALIGNMENT_LEFT,-1,20,Color("#f0d77c"))
\tif village_confirm_price>0: draw_ui_text(Vector2(120,512),"%d銭" % village_confirm_price,HORIZONTAL_ALIGNMENT_LEFT,-1,21,Color.WHITE)
\tvar yes := Rect2(150,560,190,68); var no := Rect2(380,560,190,68)
\tdraw_panel(yes,Color("#24405b"),Color("#78b9e8"),2.0); draw_panel(no,Color("#202632"),Color("#687786"),2.0)
\tdraw_ui_text(yes.position+Vector2(0,44),"はい",HORIZONTAL_ALIGNMENT_CENTER,yes.size.x,22,Color.WHITE)
\tdraw_ui_text(no.position+Vector2(0,44),"いいえ",HORIZONTAL_ALIGNMENT_CENTER,no.size.x,22,Color.WHITE)


'''
s = s[:buy_start] + confirm_helpers + s[buy_start:]

replace_func("buy_village_shop_item", '''func buy_village_shop_item(index: int) -> void:
\tvar catalog := village_shop_catalog()
\tif index<0 or index>=catalog.size(): return
\tvar offer: Dictionary=catalog[index]; var price:=int(offer["price"])
\tif coins<price: message="銭が足りない。"; queue_redraw(); return
\tif self_test_mode: commit_village_buy(index); return
\trequest_village_confirm("buy","shop",index,str(offer["label"]),price)''')

buy_commit_anchor = "\nfunc synthesize_equipment(kind: String) -> void:\n"
if buy_commit_anchor not in s:
    raise SystemExit("STEP92 commit buy anchor failed")
buy_commit = '''
func commit_village_buy(index: int) -> void:
\tvar catalog:=village_shop_catalog()
\tif index<0 or index>=catalog.size(): return
\tvar offer: Dictionary=catalog[index]; var price:=int(offer["price"])
\tif coins<price: message="銭が足りない。"; queue_redraw(); return
\tif not warehouse_add_item({"name":offer["name"],"count":offer["count"],"identified":true}): message="倉庫がいっぱいだ。"; queue_redraw(); return
\tcoins-=price; save_meta(); message="%sを購入し、倉庫へ送った。" % str(offer["label"]); queue_redraw()
'''
s = s.replace(buy_commit_anchor, "\n" + buy_commit.rstrip() + buy_commit_anchor, 1)

replace_func("synthesize_equipment", '''func synthesize_equipment(kind: String) -> void:
\tif not in_village or village_menu!="blacksmith": message="合成は鍛冶屋で行う。"; return
\tvar rank:=smith_weapon_rank if kind=="weapon" else smith_armor_rank; var price:=50+rank*25
\tif coins<price: message="合成に必要な銭が足りない。"; queue_redraw(); return
\tif self_test_mode: commit_synthesize(kind); return
\trequest_village_confirm("smith_weapon" if kind=="weapon" else "smith_armor","",-1,equipped_weapon if kind=="weapon" else equipped_armor,price)''')

smith_commit_anchor = "\nfunc fusion_material_indices() -> Array[int]:\n"
smith_commit = '''
func commit_synthesize(kind: String) -> void:
\tvar rank:=smith_weapon_rank if kind=="weapon" else smith_armor_rank; var price:=50+rank*25
\tif coins<price: message="合成に必要な銭が足りない。"; return
\tcoins-=price
\tif kind=="weapon": smith_weapon_rank+=1; perm_attack+=1; message="忍刀を合成した。攻撃+1。"
\telse: smith_armor_rank+=1; perm_defense+=1; message="忍装束を合成した。防御+1。"
\tsave_meta(); queue_redraw()
'''
if smith_commit_anchor not in s:
    raise SystemExit("STEP92 smith commit anchor failed")
s = s.replace(smith_commit_anchor, "\n" + smith_commit.rstrip() + smith_commit_anchor, 1)

replace_func("fuse_weapon_from_source", '''func fuse_weapon_from_source(source: String, index: int) -> void:
\tif not in_village or not village_menu.begins_with("weapon_fusion"): message="武器合成は鍛冶屋で行う。"; return
\tvar source_items:=fusion_source_items(source)
\tif index<0 or index>=source_items.size(): return
\tvar material_name:=str(source_items[index].get("name",""))
\tif not is_weapon_name(material_name) or material_name==equipped_weapon: message="素材にできる別の武器を選ぶ。"; return
\tvar before:=weapon_inherited_effects(equipped_weapon); var after:=merge_unique_effects(before,weapon_all_effects(material_name))
\tif after.size()==before.size(): message="新しく継承できる効果がない。"; return
\tif self_test_mode: commit_weapon_fusion(source,index); return
\trequest_village_confirm("fusion",source,index,"%s → %s" % [material_name,equipped_weapon],0)''')

fusion_commit_anchor = "\nfunc handle_village_input(event: InputEvent) -> void:\n"
fusion_commit = '''
func commit_weapon_fusion(source: String, index: int) -> void:
\tvar source_items:=fusion_source_items(source)
\tif index<0 or index>=source_items.size(): return
\tvar material_name:=str(source_items[index].get("name","")); var before:=weapon_inherited_effects(equipped_weapon); var after:=merge_unique_effects(before,weapon_all_effects(material_name))
\tif after.size()==before.size(): message="新しく継承できる効果がない。"; return
\tweapon_fusion_states[equipped_weapon]=after
\tif source=="bag": inventory_items.remove_at(index)
\telse: warehouse_items.remove_at(index)
\tfusion_scroll_offset=0; message="%sの効果を%sへ継承した。" % [material_name,equipped_weapon]; save_meta(); queue_redraw()
'''
if fusion_commit_anchor not in s:
    raise SystemExit("STEP92 fusion commit anchor failed")
s = s.replace(fusion_commit_anchor, "\n" + fusion_commit.rstrip() + fusion_commit_anchor, 1)

replace_func("sell_village_shop_item", '''func sell_village_shop_item(index: int) -> void:
\tif index<0 or index>=warehouse_items.size(): return
\tvar entry: Dictionary=warehouse_items[index]; var label:=equipment_entry_label(entry); var price:=village_sell_price(entry)
\tif self_test_mode: commit_village_sell(index); return
\trequest_village_confirm("sell","warehouse",index,label,price)''')

sell_commit_anchor = "\nfunc retain_random_death_items(limit: int = 3) -> int:\n"
sell_commit = '''
func commit_village_sell(index: int) -> void:
\tif index<0 or index>=warehouse_items.size(): return
\tvar entry: Dictionary=warehouse_items[index]; var label:=equipment_entry_label(entry); var price:=village_sell_price(entry)
\twarehouse_items.remove_at(index); coins+=price; village_shop_sync_scroll(); save_meta(); message="%sを%d銭で手放した。" % [label,price]; queue_redraw()
'''
if sell_commit_anchor not in s:
    raise SystemExit("STEP92 sell commit anchor failed")
s = s.replace(sell_commit_anchor, "\n" + sell_commit.rstrip() + sell_commit_anchor, 1)

# Remove page arrows and use swipe scrolling everywhere.
replace_func("handle_inventory_touch", '''func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:
\tvar panel_x:=60.0 if portrait else 270.0; var panel_y:=225.0 if portrait else 120.0; var row_h:=46.0
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index:=inventory_scroll_offset+row
\t\tif index>=inventory_entry_count(): break
\t\tif Rect2(panel_x+20.0,panel_y+74.0+row*row_h,490.0,40.0).has_point(pos): inventory_selected=index; inventory_sync_scroll(); queue_redraw(); return
\tvar action_y:=panel_y+510.0; var actions=[["equip",panel_x+12.0],["use",panel_x+148.0],["floor",panel_x+284.0],["back",panel_x+420.0]]
\tfor action in actions:
\t\tif Rect2(float(action[1]),action_y,124.0,52.0).has_point(pos):
\t\t\tmatch str(action[0]):
\t\t\t\t"equip": inventory_equip_selected()
\t\t\t\t"use": inventory_use_selected()
\t\t\t\t"floor": inventory_floor_pick_or_swap()
\t\t\t\t"back": close_inventory()
\t\t\treturn''')

inventory_arrows = '''\tvar max_offset: int = maxi(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tif inventory_scroll_offset > 0: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0), "↑", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tif inventory_scroll_offset < max_offset: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h), "↓", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))'''
if inventory_arrows not in s:
    raise SystemExit("STEP92 inventory arrows anchor failed")
s = s.replace(inventory_arrows, '''\tdraw_list_scrollbar(panel_x+522.0,panel_y+74.0,float(INVENTORY_VISIBLE_ROWS)*row_h-6.0,inventory_entry_count(),INVENTORY_VISIBLE_ROWS,inventory_scroll_offset)
\tdraw_ui_text(Vector2(panel_x+390.0,panel_y+48.0),"上下に動かす",HORIZONTAL_ALIGNMENT_LEFT,-1,13,Color("#aeb9c8"))''', 1)

replace_func("handle_jutsu_touch", '''func handle_jutsu_touch(pos: Vector2) -> void:
\tif Rect2(500,780,170,50).has_point(pos): close_jutsu_menu(); return
\tfor row in range(6):
\t\tvar index:=jutsu_scroll_offset+row
\t\tif index>=learned_jutsu.size(): break
\t\tif Rect2(40,300+row*76,620,66).has_point(pos): choose_jutsu_to_cast(learned_jutsu[index]); return''')

replace_func("draw_jutsu_overlay", '''func draw_jutsu_overlay() -> void:
\tjutsu_scroll_offset=clampi(jutsu_scroll_offset,0,maxi(0,learned_jutsu.size()-6))
\tdraw_rect(Rect2(20,220,680,640),Color(0.03,0.04,0.08,0.98)); draw_rect(Rect2(20,220,680,640),Color("#9b78e8"),false,3.0)
\tdraw_ui_text(Vector2(46,268),"術一覧　忍気%d" % ninja_energy,HORIZONTAL_ALIGNMENT_LEFT,-1,27,Color.WHITE)
\tdraw_ui_text(Vector2(520,268),"上下に動かす",HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color("#cfc9df"))
\tfor row in range(6):
\t\tvar index:=jutsu_scroll_offset+row
\t\tif index>=learned_jutsu.size(): break
\t\tvar rect:=Rect2(40,300+row*76,620,66); var name:=learned_jutsu[index]; var cost:=jutsu_cost(name)
\t\tdraw_panel(rect,Color("#182039"),Color("#765ac2"),1.5)
\t\tdraw_ui_text(rect.position+Vector2(12,25),"%s　忍気%d" % [name,cost],HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color.WHITE if ninja_energy>=cost else Color("#777777"))
\t\tdraw_ui_text(rect.position+Vector2(330,25),str(JUTSU_DATA[name].get("desc","")),HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#cfc9df"))
\tdraw_list_scrollbar(674,300,446,learned_jutsu.size(),6,jutsu_scroll_offset)
\tvar close:=Rect2(500,780,170,50); draw_panel(close,Color("#202632"),Color("#687786")); draw_ui_text(close.position+Vector2(0,34),"戻る",HORIZONTAL_ALIGNMENT_CENTER,close.size.x,18,Color.WHITE)''')

# Village input: modal first, then swipe-only lists and warehouse actions.
village_input_anchor = '''func handle_village_touch_portrait(pos: Vector2) -> void:
\tif village_menu == "main":'''
if village_input_anchor not in s:
    raise SystemExit("STEP92 village input anchor failed")
s = s.replace(village_input_anchor, '''func handle_village_touch_portrait(pos: Vector2) -> void:
\tif not village_confirm_kind.is_empty(): handle_village_confirm_touch(pos); return
\tif village_menu == "main":''', 1)

old_bag_input = '''\telif village_menu == "warehouse_bag":
\t\tif Rect2(48,790,270,48).has_point(pos): warehouse_bag_scroll = maxi(0,warehouse_bag_scroll-8)
\t\telif Rect2(402,790,270,48).has_point(pos): warehouse_bag_scroll = mini(maxi(0,inventory_items.size()-8),warehouse_bag_scroll+8)
\t\telif Rect2(48,850,624,48).has_point(pos): store_selected_bag_items()
\t\telse:
\t\t\tfor row in range(8):
\t\t\t\tif Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(true,warehouse_bag_scroll+row); break
\telif village_menu == "warehouse_storage":
\t\tif Rect2(48,790,270,48).has_point(pos): warehouse_scroll_offset = maxi(0,warehouse_scroll_offset-8)
\t\telif Rect2(402,790,270,48).has_point(pos): warehouse_scroll_offset = mini(maxi(0,warehouse_items.size()-8),warehouse_scroll_offset+8)
\t\telif Rect2(48,850,410,48).has_point(pos): withdraw_selected_warehouse_items()
\t\telif Rect2(470,850,202,48).has_point(pos): warehouse_sort_items(); warehouse_store_selected.clear()
\t\telse:
\t\t\tfor row in range(8):
\t\t\t\tif Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(false,warehouse_scroll_offset+row); break'''
new_bag_input = '''\telif village_menu == "warehouse_bag":
\t\tif Rect2(48,850,306,48).has_point(pos): store_selected_bag_items()
\t\telif Rect2(366,850,306,48).has_point(pos): store_all_non_equipment()
\t\telse:
\t\t\tfor row in range(8):
\t\t\t\tif Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(true,warehouse_bag_scroll+row); break
\telif village_menu == "warehouse_storage":
\t\tif Rect2(48,850,292,48).has_point(pos): withdraw_selected_warehouse_items()
\t\telif Rect2(348,850,156,48).has_point(pos): request_warehouse_sell_selected()
\t\telif Rect2(512,850,160,48).has_point(pos): warehouse_sort_items(); warehouse_store_selected.clear()
\t\telse:
\t\t\tfor row in range(8):
\t\t\t\tif Rect2(48,318+row*56,624,48).has_point(pos): toggle_warehouse_selection(false,warehouse_scroll_offset+row); break'''
if old_bag_input not in s:
    raise SystemExit("STEP92 warehouse input block failed")
s = s.replace(old_bag_input,new_bag_input,1)

old_fusion_page = '''\t\tif Rect2(48,790,270,48).has_point(pos): fusion_scroll(source,-6)
\t\telif Rect2(402,790,270,48).has_point(pos): fusion_scroll(source,6)
\t\telse:
\t\t\tfor row in range(6):'''
if old_fusion_page not in s:
    raise SystemExit("STEP92 fusion paging input failed")
s = s.replace(old_fusion_page, '''\t\tfor row in range(6):''', 1)
s = s.replace('''\t\t\t\tif Rect2(48,430+row*58,624,50).has_point(pos): fuse_weapon_from_source(source,materials[material_row]); break
\telif village_menu == "village_shop":''','''\t\t\tif Rect2(48,430+row*58,624,50).has_point(pos): fuse_weapon_from_source(source,materials[material_row]); break
\telif village_menu == "village_shop":''',1)

shop_page_input = '''\t\telif Rect2(48,286,624,48).has_point(pos): village_shop_toggle_mode()
\t\telif Rect2(48,842,270,48).has_point(pos): village_shop_scroll(-VILLAGE_SHOP_VISIBLE_ROWS)
\t\telif Rect2(402,842,270,48).has_point(pos): village_shop_scroll(VILLAGE_SHOP_VISIBLE_ROWS)
\t\telse:'''
if shop_page_input not in s:
    raise SystemExit("STEP92 shop paging input failed")
s = s.replace(shop_page_input, '''\t\telif Rect2(48,286,624,48).has_point(pos): village_shop_toggle_mode()
\t\telse:''', 1)

# Village drawing blocks.
warehouse_draw_old = '''\t\t\tvar prev := Rect2(48,790,270,48); var next := Rect2(402,790,270,48)
\t\t\tfor r in [prev,next]: draw_panel(r,Color("#101923"),Color("#687786"))
\t\t\tdraw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE)
\t\t\tdraw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)
\t\t\tif from_bag:
\t\t\t\tvar action := Rect2(48,850,624,48); draw_panel(action,Color("#62521f"),Color("#f0c75e")); draw_ui_text(action.position+Vector2(0,33),"選択を倉庫へ預ける",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,18,Color.WHITE)
\t\t\telse:
\t\t\t\tvar action := Rect2(48,850,410,48); var sort_button := Rect2(470,850,202,48)
\t\t\t\tdraw_panel(action,Color("#24405b"),Color("#78b9e8")); draw_panel(sort_button,Color("#101923"),Color("#687786"))
\t\t\t\tdraw_ui_text(action.position+Vector2(0,33),"選択を道具袋へ移す",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,18,Color.WHITE)
\t\t\t\tdraw_ui_text(sort_button.position+Vector2(0,33),"整える",HORIZONTAL_ALIGNMENT_CENTER,sort_button.size.x,17,Color.WHITE)'''
warehouse_draw_new = '''\t\t\tdraw_list_scrollbar(684,318,440,source_items.size(),8,offset)
\t\t\tdraw_ui_text(Vector2(48,815),"一覧を上下に動かす",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#c7d0d8"))
\t\t\tif from_bag:
\t\t\t\tvar action:=Rect2(48,850,306,48); var all_button:=Rect2(366,850,306,48)
\t\t\t\tdraw_panel(action,Color("#62521f"),Color("#f0c75e")); draw_panel(all_button,Color("#24405b"),Color("#78b9e8"))
\t\t\t\tdraw_ui_text(action.position+Vector2(0,33),"選択を預ける",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,17,Color.WHITE)
\t\t\t\tdraw_ui_text(all_button.position+Vector2(0,33),"全て預ける",HORIZONTAL_ALIGNMENT_CENTER,all_button.size.x,17,Color.WHITE)
\t\t\telse:
\t\t\t\tvar action:=Rect2(48,850,292,48); var sell_button:=Rect2(348,850,156,48); var sort_button:=Rect2(512,850,160,48)
\t\t\t\tdraw_panel(action,Color("#24405b"),Color("#78b9e8")); draw_panel(sell_button,Color("#5a3028"),Color("#e59a78")); draw_panel(sort_button,Color("#101923"),Color("#687786"))
\t\t\t\tdraw_ui_text(action.position+Vector2(0,33),"道具袋へ移す",HORIZONTAL_ALIGNMENT_CENTER,action.size.x,16,Color.WHITE)
\t\t\t\tdraw_ui_text(sell_button.position+Vector2(0,33),"売る",HORIZONTAL_ALIGNMENT_CENTER,sell_button.size.x,17,Color.WHITE)
\t\t\t\tdraw_ui_text(sort_button.position+Vector2(0,33),"整える",HORIZONTAL_ALIGNMENT_CENTER,sort_button.size.x,16,Color.WHITE)'''
if warehouse_draw_old not in s:
    raise SystemExit("STEP92 warehouse draw block failed")
s = s.replace(warehouse_draw_old,warehouse_draw_new,1)

fusion_draw_old = '''\t\t\tvar prev := Rect2(48,790,270,48); var next := Rect2(402,790,270,48)
\t\t\tfor r in [prev,next]: draw_panel(r,Color("#101923"),Color("#687786"))
\t\t\tdraw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)'''
if fusion_draw_old not in s:
    raise SystemExit("STEP92 fusion draw block failed")
s = s.replace(fusion_draw_old, '''\t\t\tdraw_list_scrollbar(684,430,340,materials.size(),6,fusion_scroll_offset)
\t\t\tdraw_ui_text(Vector2(48,815),"一覧を上下に動かす",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#c7d0d8"))''', 1)

shop_draw_old = '''\t\t\t\tvar prev := Rect2(48,842,270,48); var next := Rect2(402,842,270,48); draw_panel(prev,Color("#101923"),Color("#687786")); draw_panel(next,Color("#101923"),Color("#687786"))
\t\t\t\tdraw_ui_text(prev.position+Vector2(0,33),"前へ",HORIZONTAL_ALIGNMENT_CENTER,prev.size.x,18,Color.WHITE); draw_ui_text(next.position+Vector2(0,33),"次へ",HORIZONTAL_ALIGNMENT_CENTER,next.size.x,18,Color.WHITE)'''
if shop_draw_old not in s:
    raise SystemExit("STEP92 shop draw block failed")
s = s.replace(shop_draw_old, '''\t\t\t\tdraw_list_scrollbar(684,350,468,entries.size(),VILLAGE_SHOP_VISIBLE_ROWS,village_shop_scroll_offset)
\t\t\t\tdraw_ui_text(Vector2(48,868),"一覧を上下に動かす",HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#c7d0d8"))''', 1)

village_end_anchor = '''\tdraw_panel(Rect2(40,984,640,70),Color(0.04,0.07,0.10,0.90),Color("#394653"),1.0); draw_ui_text(Vector2(54,1028),message.left(40),HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("#e5d37d")); draw_ui_text(Vector2(465,46),"Ver.%s" % VERSION,HORIZONTAL_ALIGNMENT_LEFT,-1,14,Color("#7f8b98"))'''
if village_end_anchor not in s:
    raise SystemExit("STEP92 village confirm draw anchor failed")
s = s.replace(village_end_anchor, village_end_anchor + '''
\tif not village_confirm_kind.is_empty(): draw_village_action_confirm()''', 1)

# Regression contract.
test_anchor = "\nfunc debug_test_step91_contract() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP92 regression anchor failed")
test_func = '''
func debug_test_step92_contract() -> String:
\tvar old_inventory:=inventory_items.duplicate(true); var old_warehouse:=warehouse_items.duplicate(true); var old_confirm:=village_confirm_kind
\tinventory_items=[{"name":"薬","identified":true,"count":1},{"name":"双牙刀","identified":true,"count":1,"bonus":0}]; warehouse_items=[]
\tvar moved:=store_all_non_equipment(); var bulk_ok:=moved==1 and inventory_items.size()==1 and str(inventory_items[0].get("name",""))=="双牙刀"
\trequest_village_confirm("buy","shop",0,"薬小",8); var confirm_ok:=village_confirm_kind=="buy"
\tinventory_items=old_inventory; warehouse_items=old_warehouse; village_confirm_kind=old_confirm
\tvar scroll_ok:=has_method("scroll_active_list") and has_method("draw_list_scrollbar") and has_method("draw_stepping_region")
\treturn "PASS 足替え待機・確認売買合成・一覧スクロール・全預け売却" if bulk_ok and confirm_ok and scroll_ok else "FAIL 確認スクロール倉庫"
'''
s = s.replace(test_anchor, "\n" + test_func.rstrip() + test_anchor, 1)

suite_anchor = "\t\tdebug_test_step91_contract(),\n"
if suite_anchor not in s:
    raise SystemExit("STEP92 regression suite anchor failed")
s = s.replace(suite_anchor, suite_anchor + "\t\tdebug_test_step92_contract(),\n", 1)

required = [
    "STEP92_CONFIRM_SCROLL_STORAGE_APPLIED", "func draw_stepping_region(", "買いますか？", "売りますか？",
    "合成しますか？", "全て預ける", "倉庫がいっぱいだ。", "func scroll_active_list(",
    "PASS 足替え待機・確認売買合成・一覧スクロール・全預け売却",
]
missing = [value for value in required if value not in s]
if missing:
    raise SystemExit(f"STEP92 verification failed: {missing}")
if s == original:
    raise SystemExit("STEP92 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP92_CONFIRM_SCROLL_STORAGE PASS")
