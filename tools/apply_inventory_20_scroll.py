from pathlib import Path

p=Path("Main.gd")
s=p.read_text(encoding="utf-8")

if "INVENTORY_20_SCROLL_PATCH_APPLIED" in s:
    print("INVENTORY_20_SCROLL_PATCH PASS (already applied)")
    raise SystemExit(0)

anchor = "var inventory_selected := 0\n"
if anchor not in s: raise SystemExit("inventory state anchor failed")
s=s.replace(anchor, anchor + "var inventory_scroll_offset := 0 # INVENTORY_20_SCROLL_PATCH_APPLIED\nvar inventory_scroll_drag_y := 0.0\nconst INVENTORY_CAPACITY := 20\nconst INVENTORY_VISIBLE_ROWS := 7\n",1)

anchor = "func inventory_entry_count() -> int:\n"
if anchor not in s: raise SystemExit("inventory helper anchor failed")
helpers='''func inventory_has_space_for(name: String) -> bool:
\tif is_projectile_name(name):
\t\tfor entry in inventory_items:
\t\t\tif str(entry.get("name", "")) == name:
\t\t\t\treturn true
\treturn inventory_items.size() < INVENTORY_CAPACITY


func inventory_sync_scroll() -> void:
\tvar max_offset := max(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tif inventory_selected < inventory_scroll_offset:
\t\tinventory_scroll_offset = inventory_selected
\telif inventory_selected >= inventory_scroll_offset + INVENTORY_VISIBLE_ROWS:
\t\tinventory_scroll_offset = inventory_selected - INVENTORY_VISIBLE_ROWS + 1
\tinventory_scroll_offset = clampi(inventory_scroll_offset, 0, max_offset)


func inventory_scroll(delta_rows: int) -> void:
\tvar max_offset := max(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tinventory_scroll_offset = clampi(inventory_scroll_offset + delta_rows, 0, max_offset)
\tinventory_selected = clampi(inventory_selected, inventory_scroll_offset, min(max(0, inventory_entry_count()-1), inventory_scroll_offset + INVENTORY_VISIBLE_ROWS - 1))
\tqueue_redraw()


'''
s=s.replace(anchor,helpers+anchor,1)

needle='''func add_inventory_item(name: String, identified: bool = false, count: int = 1) -> void:
\tif not valid_inventory_item_name(name): return
\tif is_projectile_name(name):'''
repl='''func add_inventory_item(name: String, identified: bool = false, count: int = 1) -> void:
\tif not valid_inventory_item_name(name): return
\tif not inventory_has_space_for(name):
\t\tmessage = "道具は20個まで。持ち物がいっぱいだ。"
\t\treturn
\tif is_projectile_name(name):'''
if needle not in s: raise SystemExit("add inventory capacity anchor failed")
s=s.replace(needle,repl,1)

start=s.find("func pickup(consume_turn: bool = true) -> void:")
end=s.find("\n\nfunc is_projectile_name",start)
if start<0 or end<0: raise SystemExit("pickup anchors failed")
pickup='''func pickup(consume_turn: bool = true) -> void:
\tvar found = -1
\tfor i in range(items.size()):
\t\tif items[i]["pos"] == player:
\t\t\tfound = i
\t\t\tbreak
\tif found < 0:
\t\tmessage = "ここには何もない。"
\t\treturn
\tvar item: Dictionary = items[found]
\tvar item_name := str(item.get("name", ""))
\tif not bool(item.get("shop", false)) and not inventory_has_space_for(item_name):
\t\tmessage = "道具は20個まで。これ以上持てない。"
\t\treturn
\titems.remove_at(found)
\tif bool(item.get("shop", false)):
\t\tunpaid_items.append(item)
\t\tmessage = "%sを手に取った。未精算。" % item_name
\telse:
\t\tvar picked_count := max(1, int(item.get("count", 1)))
\t\tadd_inventory_item(item_name, false, picked_count)
\t\tmessage = "%s×%dを拾った。" % [item_name, picked_count] if picked_count > 1 else "%sを拾った。" % item_name
\tif consume_turn:
\t\tend_turn()'''
s=s[:start]+pickup+s[end:]

s=s.replace('\tinventory_selected = clamp(inventory_selected, 0, max(0, inventory_entry_count() - 1))\n\tmessage = "道具を確認する。"','\tinventory_selected = clamp(inventory_selected, 0, max(0, inventory_entry_count() - 1))\n\tinventory_sync_scroll()\n\tinventory_scroll_drag_y = 0.0\n\tmessage = "道具を確認する。"',1)
s=s.replace('\telif event.keycode == KEY_D:\n\t\tinventory_identify_selected()\n\tqueue_redraw()','\telif event.keycode == KEY_D:\n\t\tinventory_identify_selected()\n\tinventory_sync_scroll()\n\tqueue_redraw()',1)

a=s.find("func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:"); b=s.find("\n\nfunc inventory_display_name",a)
if a<0 or b<0: raise SystemExit("inventory touch anchors failed")
touch='''func handle_inventory_touch(pos: Vector2, portrait: bool) -> void:
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
\tvar actions = [["equip", panel_x + 20.0], ["use", panel_x + 150.0], ["identify", panel_x + 280.0], ["back", panel_x + 410.0]]
\tfor action in actions:
\t\tif Rect2(float(action[1]), action_y, 115.0, 52.0).has_point(pos):
\t\t\tmatch str(action[0]):
\t\t\t\t"equip": inventory_equip_selected()
\t\t\t\t"use": inventory_use_selected()
\t\t\t\t"identify": inventory_identify_selected()
\t\t\t\t"back": close_inventory()
\t\t\treturn'''
s=s[:a]+touch+s[b:]

a=s.find("func draw_inventory_overlay(portrait: bool) -> void:"); b=s.find("\nfunc item_shop_price",a)
if a<0 or b<0: raise SystemExit("inventory draw anchors failed")
draw='''func draw_inventory_overlay(portrait: bool) -> void:
\tvar panel_x := 60.0 if portrait else 270.0
\tvar panel_y := 225.0 if portrait else 120.0
\tvar panel_w := 560.0
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color(0.05, 0.07, 0.09, 0.98))
\tdraw_rect(Rect2(panel_x, panel_y, panel_w, 500.0), Color("#e4cf7a"), false, 2.0)
\tdraw_ui_text(Vector2(panel_x + 22.0, panel_y + 48.0), "道具 %d/20" % inventory_items.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 25, Color.WHITE)
\tvar row_h := 46.0
\tfor row in range(INVENTORY_VISIBLE_ROWS):
\t\tvar index := inventory_scroll_offset + row
\t\tif index >= inventory_entry_count(): break
\t\tvar r := Rect2(panel_x + 20.0, panel_y + 74.0 + row * row_h, 470.0, 40.0)
\t\tdraw_rect(r, Color("#343527") if index == inventory_selected else Color("#202934"))
\t\tdraw_rect(r, Color("#dbc66e") if index == inventory_selected else Color("#4c5865"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(12, 27), inventory_display_name(index), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar max_offset := max(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)
\tif inventory_scroll_offset > 0: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0), "↑", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tif inventory_scroll_offset < max_offset: draw_ui_text(Vector2(panel_x + 505.0, panel_y + 101.0 + (INVENTORY_VISIBLE_ROWS - 1) * row_h), "↓", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Color("#e4cf7a"))
\tvar action_y := panel_y + 420.0
\tvar labels = [["装備", panel_x + 20.0], ["使用", panel_x + 150.0], ["識別", panel_x + 280.0], ["戻る", panel_x + 410.0]]
\tfor action in labels:
\t\tvar r := Rect2(float(action[1]), action_y, 115.0, 52.0)
\t\tdraw_rect(r, Color("#252c35")); draw_rect(r, Color("#596575"), false, 1.5)
\t\tdraw_ui_text(r.position + Vector2(22, 34), str(action[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
'''
s=s[:a]+draw+s[b:]

anchor='func _input(event: InputEvent) -> void:\n'; idx=s.find(anchor)
if idx<0: raise SystemExit("_input anchor failed")
insert_at=idx+len(anchor)
swipe='''\tif inventory_menu and event is InputEventScreenDrag:
\t\tinventory_scroll_drag_y += event.relative.y
\t\tif abs(inventory_scroll_drag_y) >= 34.0:
\t\t\tinventory_scroll(-1 if inventory_scroll_drag_y > 0.0 else 1)
\t\t\tinventory_scroll_drag_y = 0.0
\t\treturn
'''
s=s[:insert_at]+swipe+s[insert_at:]

needle='\treturn out\n\n\nfunc inventory_entry_count() -> int:'
if needle not in s: raise SystemExit("sanitize cap anchor failed")
s=s.replace(needle,'\treturn out.slice(0, INVENTORY_CAPACITY)\n\n\nfunc inventory_entry_count() -> int:',1)

p.write_text(s,encoding="utf-8")
print("INVENTORY_20_SCROLL_PATCH PASS")
