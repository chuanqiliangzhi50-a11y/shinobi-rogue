from pathlib import Path
import re

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

# Portrait confirmation modal: stack Yes/No vertically for easier iPhone tapping.
handle = '''func handle_modal_touch_portrait(pos: Vector2) -> void:\n\tif checkout_prompt:\n\t\tif Rect2(190, 465, 340, 70).has_point(pos): confirm_checkout(true)\n\t\telif Rect2(190, 555, 340, 70).has_point(pos): confirm_checkout(false)\n\t\treturn\n\tif stairs_prompt:\n\t\tif Rect2(190, 465, 340, 70).has_point(pos): confirm_stairs(true)\n\t\telif Rect2(190, 555, 340, 70).has_point(pos): confirm_stairs(false)\n\t\treturn\n\tif ad_menu:\n\t\tvar rects = [Rect2(80,500,250,70),Rect2(390,500,250,70),Rect2(80,590,250,70),Rect2(390,590,250,70)]\n\t\tfor i in range(rects.size()):\n\t\t\tif rects[i].has_point(pos):\n\t\t\t\tif i == 0: apply_ad_reward("A")\n\t\t\t\telif i == 1: apply_ad_reward("B")\n\t\t\t\telif i == 2: apply_ad_reward("C")\n\t\t\t\telse:\n\t\t\t\t\tad_menu = false\n\t\t\t\t\tmessage = "広告を見ずに進む。"\n\t\t\t\t\tqueue_redraw()\n\t\t\t\treturn\n'''
s, n1 = re.subn(r'func handle_modal_touch_portrait\(pos: Vector2\) -> void:\n.*?(?=\n\nfunc draw_panel)', handle, s, count=1, flags=re.S)

draw = '''func draw_modal_overlay_portrait() -> void:\n\t# Compact centered confirmation, matching the adopted iPhone mockup.\n\tif checkout_prompt or stairs_prompt:\n\t\tdraw_rect(Rect2(100,340,520,330),Color(0.05,0.07,0.09,0.97))\n\t\tdraw_rect(Rect2(100,340,520,330),Color("#e4cf7a"),false,3)\n\t\tdraw_ui_text(Vector2(180,420), "商品を精算しますか？" if checkout_prompt else "次の階に降りますか？", HORIZONTAL_ALIGNMENT_LEFT, -1, 28, Color.WHITE)\n\t\tvar yes := Rect2(190,465,340,70)\n\t\tvar no := Rect2(190,555,340,70)\n\t\tfor r in [yes,no]:\n\t\t\tdraw_rect(r,Color("#252c35"))\n\t\t\tdraw_rect(r,Color("#596575"),false,2)\n\t\tdraw_ui_text(yes.position+Vector2(138,47),"はい",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)\n\t\tdraw_ui_text(no.position+Vector2(130,47),"いいえ",HORIZONTAL_ALIGNMENT_LEFT,-1,24,Color.WHITE)\n\telse:\n\t\tdraw_rect(Rect2(40,320,640,360),Color(0.05,0.07,0.09,0.97))\n\t\tdraw_rect(Rect2(40,320,640,360),Color("#e4cf7a"),false,3)\n\t\tdraw_ui_text(Vector2(85,400),"任意広告ブースト（試作）",HORIZONTAL_ALIGNMENT_LEFT,-1,26,Color.WHITE)\n\t\tvar labels = ["忍気","能力","全回復","見ない"]\n\t\tvar rects = [Rect2(80,500,250,70),Rect2(390,500,250,70),Rect2(80,590,250,70),Rect2(390,590,250,70)]\n\t\tfor i in range(4):\n\t\t\tdraw_rect(rects[i],Color("#252c35"))\n\t\t\tdraw_rect(rects[i],Color("#596575"),false,2)\n\t\t\tdraw_ui_text(rects[i].position+Vector2(55,47),labels[i],HORIZONTAL_ALIGNMENT_LEFT,-1,22,Color.WHITE)\n'''
s, n2 = re.subn(r'func draw_modal_overlay_portrait\(\) -> void:\n.*?(?=\n\nfunc debug_prepare_shop)', draw, s, count=1, flags=re.S)

if (n1, n2) != (1, 1):
    raise SystemExit(f'vertical confirm modal patch anchors failed: handle={n1}, draw={n2}')
if s == original:
    raise SystemExit('vertical confirm modal patch made no changes')

p.write_text(s, encoding='utf-8')

required = [
    'Rect2(190, 465, 340, 70).has_point(pos)',
    'Rect2(190, 555, 340, 70).has_point(pos)',
    'var yes := Rect2(190,465,340,70)',
    'var no := Rect2(190,555,340,70)',
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'vertical confirm modal verification failed: {needle}')
print('VERTICAL_CONFIRM_MODAL_PATCH PASS')
