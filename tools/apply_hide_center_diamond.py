from pathlib import Path
p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
if 'HIDE_CENTER_DIAMOND_PATCH_APPLIED' in s:
    print('HIDE_CENTER_DIAMOND_PATCH PASS (already applied)'); raise SystemExit(0)
needle='''\tvar diamond_actions = [
\t\t[Rect2(122, 770, 96, 96), "inventory"],'''
repl='''\t# HIDE_CENTER_DIAMOND_PATCH_APPLIED: hide is now the center of the left command diamond.
\tif Rect2(132, 850, 76, 76).has_point(pos):
\t\thide_one_turn()
\t\treturn
\tvar diamond_actions = [
\t\t[Rect2(122, 770, 96, 96), "inventory"],'''
if needle not in s: raise SystemExit('hide center touch anchor failed')
s=s.replace(needle,repl,1)
s=s.replace('''\t\tif d == Vector2i.ZERO:
\t\t\thide_one_turn()
\t\telse:
\t\t\tstart_dash_hold(d)''','''\t\tif d == Vector2i.ZERO:
\t\t\treturn
\t\telse:
\t\t\tstart_dash_hold(d)''',1)
needle='''\tfor d_control in diamond_controls:
\t\tvar c: Vector2 = d_control[1]
\t\tdraw_circle(c, 45.0, Color("#172438"))
\t\tdraw_arc(c, 45.0, 0.0, TAU, 48, Color("#d6a74f"), 2.5)
\t\tvar label := str(d_control[0])
\t\tdraw_ui_text(c + Vector2(-25 if label.length() > 1 else -9, 7), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar base := Vector2(382, 772)'''
repl='''\tfor d_control in diamond_controls:
\t\tvar c: Vector2 = d_control[1]
\t\tdraw_circle(c, 45.0, Color("#172438"))
\t\tdraw_arc(c, 45.0, 0.0, TAU, 48, Color("#d6a74f"), 2.5)
\t\tvar label := str(d_control[0])
\t\tdraw_ui_text(c + Vector2(-25 if label.length() > 1 else -9, 7), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, Color.WHITE)
\tvar hide_center := Vector2(170, 888)
\tdraw_circle(hide_center, 36.0, Color("#25364a"))
\tdraw_arc(hide_center, 36.0, 0.0, TAU, 48, Color("#f1c95b"), 2.5)
\tdraw_ui_text(hide_center + Vector2(-10, 8), "隠", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, Color("#f1c95b"))
\tvar base := Vector2(382, 772)'''
if needle not in s: raise SystemExit('hide center draw anchor failed')
s=s.replace(needle,repl,1)
s=s.replace('var labels = [["↖", "↑", "↗"], ["←", "隠", "→"], ["↙", "↓", "↘"]]','var labels = [["↖", "↑", "↗"], ["←", " ", "→"], ["↙", "↓", "↘"]]',1)
s=s.replace('''\t\t\t\tdraw_ui_text(cc + Vector2(-10, 8), "隠", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Color("#f1c95b"))''','''\t\t\t\tdraw_circle(cc, 12.0, Color("#eef1f4"))''',1)
p.write_text(s,encoding='utf-8')
print('HIDE_CENTER_DIAMOND_PATCH PASS')
