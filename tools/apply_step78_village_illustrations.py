from pathlib import Path

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "STEP78_VILLAGE_ILLUSTRATIONS_APPLIED" in s:
    print("STEP78_VILLAGE_ILLUSTRATIONS PASS (already applied)")
    raise SystemExit(0)

marker = "# STEP77_VILLAGE_CARRY_SCROLL_APPLIED\n"
if marker not in s:
    raise SystemExit("STEP78 STEP77 anchor failed")
scene_paths = '''# STEP78_VILLAGE_ILLUSTRATIONS_APPLIED
const VILLAGE_SCENE_PATHS := {
\t"main": "res://art/village_dojo.jpg",
\t"blacksmith": "res://art/village_blacksmith.jpg",
\t"village_shop": "res://art/village_merchant.jpg",
\t"warehouse": "res://art/village_warehouse.jpg"
}
'''
s = s.replace(marker, scene_paths, 1)

state_anchor = "var title_screen_texture: Texture2D = null\n"
if state_anchor not in s:
    raise SystemExit("STEP78 texture state anchor failed")
s = s.replace(state_anchor, state_anchor + "var village_scene_textures: Dictionary = {}\n", 1)

load_anchor = '''\tif ResourceLoader.exists(TITLE_SCREEN_PATH):
\t\ttitle_screen_texture = load(TITLE_SCREEN_PATH) as Texture2D
\telse:
\t\ttitle_screen_active = false'''
load_new = load_anchor + '''
\tfor scene_key in VILLAGE_SCENE_PATHS:
\t\tvar scene_path := str(VILLAGE_SCENE_PATHS[scene_key])
\t\tif ResourceLoader.exists(scene_path):
\t\t\tvillage_scene_textures[scene_key] = load(scene_path) as Texture2D'''
if load_anchor not in s:
    raise SystemExit("STEP78 texture load anchor failed")
s = s.replace(load_anchor, load_new, 1)

draw_start = s.find("func draw_village_portrait() -> void:")
draw_end = s.find("\n\nfunc dungeon_visual_hash", draw_start)
if draw_start < 0 or draw_end < 0:
    raise SystemExit("STEP78 village draw block failed")
block = s[draw_start:draw_end]
old_top = '''func draw_village_portrait() -> void:
\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
\tdraw_rect(Rect2(0, 0, 720, 198), Color("#111b27"))
\tdraw_rect(Rect2(0, 195, 720, 3), Color("#8d7740"))'''
new_top = '''func draw_village_portrait() -> void:
\tvar scene_key := village_menu if village_scene_textures.has(village_menu) else "main"
\tvar scene_texture: Texture2D = village_scene_textures.get(scene_key, null) as Texture2D
\tif scene_texture != null:
\t\tdraw_texture_rect(scene_texture, Rect2(0, 0, 720, 1100), false)
\telse:
\t\tdraw_rect(Rect2(0, 0, 720, 1100), Color("#0a1017"))
\t# A light veil and translucent panels keep controls readable while preserving the one-piece art.
\tdraw_rect(Rect2(0, 0, 720, 1100), Color(0.015, 0.025, 0.045, 0.18))
\tdraw_rect(Rect2(0, 0, 720, 198), Color(0.03, 0.055, 0.09, 0.82))
\tdraw_rect(Rect2(0, 195, 720, 3), Color("#d3b35b"))'''
if old_top not in block:
    raise SystemExit("STEP78 village background anchor failed")
block = block.replace(old_top, new_top, 1)

# Keep facility artwork visible beneath the existing controls.
block = block.replace('Color("#18212b")', 'Color(0.07, 0.10, 0.14, 0.86)')
block = block.replace('Color("#282717")', 'Color(0.16, 0.15, 0.08, 0.90)')
block = block.replace('Color("#111820")', 'Color(0.04, 0.07, 0.10, 0.90)')
s = s[:draw_start] + block + s[draw_end:]

test_anchor = "\n\nfunc debug_test_village_carry_and_scroll() -> String:\n"
if test_anchor not in s:
    raise SystemExit("STEP78 regression anchor failed")
test_func = '''

func debug_test_village_illustration_contract() -> String:
\tvar required := ["main", "blacksmith", "village_shop", "warehouse"]
\tfor scene_key in required:
\t\tif not VILLAGE_SCENE_PATHS.has(scene_key): return "FAIL village art key:%s" % scene_key
\t\tif not ResourceLoader.exists(str(VILLAGE_SCENE_PATHS[scene_key])): return "FAIL village art file:%s" % scene_key
\treturn "PASS village art 4 screens"
'''
s = s.replace(test_anchor, test_func + test_anchor, 1)
s = s.replace(
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_carry_and_scroll(),''',
    '''\t\tdebug_test_level_and_full_heal_growth(),
\t\tdebug_test_village_illustration_contract(),
\t\tdebug_test_village_carry_and_scroll(),''',
    1,
)

required = [
    "STEP78_VILLAGE_ILLUSTRATIONS_APPLIED",
    '"main": "res://art/village_dojo.jpg"',
    '"blacksmith": "res://art/village_blacksmith.jpg"',
    '"village_shop": "res://art/village_merchant.jpg"',
    '"warehouse": "res://art/village_warehouse.jpg"',
    "var village_scene_textures: Dictionary = {}",
    "draw_texture_rect(scene_texture, Rect2(0, 0, 720, 1100), false)",
    "debug_test_village_illustration_contract()",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"STEP78 verification failed: {needle}")
if s == original:
    raise SystemExit("STEP78 made no changes")

p.write_text(s, encoding="utf-8")
print("STEP78_VILLAGE_ILLUSTRATIONS PASS")
exec(Path("tools/apply_step79_village_bottom_choices.py").read_text(encoding="utf-8"), {})
