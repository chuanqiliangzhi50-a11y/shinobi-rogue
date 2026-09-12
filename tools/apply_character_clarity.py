from pathlib import Path

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

old_enemy = '''\tfor e in enemies:\n\t\tvar ep: Vector2i = e["pos"]\n\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep): draw_entity_visual(portrait_cell_center(ep), "boss" if bool(e["boss"]) else "enemy", "将" if bool(e["boss"]) else "敵", 20, Color("#f08a7d"), PTILE)'''
new_enemy = '''\tfor e in enemies:\n\t\tvar ep: Vector2i = e["pos"]\n\t\tif portrait_cell_in_view(ep) and is_visible_cell(ep):\n\t\t\tvar ec := portrait_cell_center(ep)\n\t\t\t# Ground marker improves instant friend/foe recognition without changing rules.\n\t\t\tdraw_arc(ec + Vector2(0, 13), 15.0, 0.0, TAU, 32, Color("#e8c85d") if bool(e["boss"]) else Color("#c95f5f"), 3.0)\n\t\t\tdraw_entity_visual(ec, "boss" if bool(e["boss"]) else "enemy", "将" if bool(e["boss"]) else "敵", 20, Color("#f08a7d"), PTILE)'''
if old_enemy not in s:
    raise SystemExit('enemy clarity anchor not found')
s = s.replace(old_enemy, new_enemy, 1)

old_player = '''\tif portrait_cell_in_view(player): draw_entity_visual(portrait_cell_center(player), "player", "忍", 21, Color("#ffffff"), PTILE)'''
new_player = '''\tif portrait_cell_in_view(player):\n\t\tvar pc := portrait_cell_center(player)\n\t\tdraw_arc(pc + Vector2(0, 13), 16.0, 0.0, TAU, 32, Color("#72c7e8"), 3.0)\n\t\tdraw_entity_visual(pc, "player", "忍", 21, Color("#ffffff"), PTILE)'''
if old_player not in s:
    raise SystemExit('player clarity anchor not found')
s = s.replace(old_player, new_player, 1)

if s == original:
    raise SystemExit('no changes made')
p.write_text(s, encoding='utf-8')
print('CHARACTER_CLARITY_PATCH PASS')
