from pathlib import Path
p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
if 'DIRECTION_ONLY_BUTTON_PATCH_APPLIED' in s:
    print('DIRECTION_ONLY_BUTTON_PATCH PASS (already applied)'); raise SystemExit(0)
anchor='var facing_dir := Vector2i(0, 1)\n'
if anchor not in s: raise SystemExit('direction-only state anchor failed')
s=s.replace(anchor, anchor + 'var direction_only_mode: bool = false # DIRECTION_ONLY_BUTTON_PATCH_APPLIED\n',1)
old='''\t\tif d == Vector2i.ZERO:
\t\t\treturn
\t\telse:
\t\t\tstart_dash_hold(d)'''
new='''\t\tif d == Vector2i.ZERO:
\t\t\tdirection_only_mode = not direction_only_mode
\t\t\tmessage = "向き変更：方向を選択。" if direction_only_mode else "向き変更を解除した。"
\t\t\tqueue_redraw()
\t\t\treturn
\t\tif direction_only_mode:
\t\t\tfacing_dir = d
\t\t\tdirection_only_mode = false
\t\t\tmessage = "向きを変えた。"
\t\t\tqueue_redraw()
\t\t\treturn
\t\tstart_dash_hold(d)'''
if old not in s: raise SystemExit('direction-only touch anchor failed')
s=s.replace(old,new,1)
old='''\t\t\t\tdraw_circle(cc, 12.0, Color("#eef1f4"))'''
new='''\t\t\t\tdraw_circle(cc, 18.0, Color("#f4f5f2"))
\t\t\t\tdraw_arc(cc, 21.0, 0.0, TAU, 40, Color("#f1c95b") if direction_only_mode else Color("#7f8b98"), 2.5)'''
if old not in s: raise SystemExit('direction-only draw anchor failed')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('DIRECTION_ONLY_BUTTON_PATCH PASS')
