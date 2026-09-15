from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")
original = s

if "DASH_RUN_EFFECT_PATCH_APPLIED" in s:
    print("DASH_RUN_EFFECT_PATCH PASS (already applied)")
    raise SystemExit(0)

# Replace only the existing player draw function. Do not consume any following
# gameplay/helper functions.
pattern = r'''func draw_player_facing_visual\(center: Vector2, tile_size: float\) -> void:\n.*?(?=\n\nfunc )'''

replacement = '''func draw_dash_run_effect(center: Vector2, tile_size: float, dir: Vector2) -> void: # DASH_RUN_EFFECT_PATCH_APPLIED
\tvar now := float(Time.get_ticks_msec()) / 1000.0
\tvar side := Vector2(-dir.y, dir.x)
\tvar behind := center - dir * (tile_size * 0.34)
\t# Small dust puffs stay behind the ninja and fade quickly.
\tfor i in range(3):
\t\tvar phase := fmod(now * 5.5 + float(i) * 0.31, 1.0)
\t\tvar dust_pos := behind - dir * (phase * 11.0) + side * (float(i - 1) * 4.0)
\t\tvar alpha := (1.0 - phase) * 0.30
\t\tdraw_circle(dust_pos, 2.5 + phase * 2.8, Color(0.78, 0.82, 0.86, alpha))


func draw_player_facing_visual(center: Vector2, tile_size: float) -> void:
\tvar key := player_direction_key()
\tvar dir := Vector2(float(facing_dir.x), float(facing_dir.y))
\tif dir.length() < 0.1:
\t\tdir = Vector2.DOWN
\tdir = dir.normalized()
\tvar running := dash_hold_active and dash_hold_repeating
\tvar draw_center := center
\tif running:
\t\tvar now := float(Time.get_ticks_msec()) / 1000.0
\t\t# Slight forward lean/bob without changing collision or movement timing.
\t\tdraw_center += dir * 2.2
\t\tdraw_center.y += sin(now * 28.0) * 1.8
\t\tdraw_dash_run_effect(center, tile_size, dir)
\tif player_direction_art.has(key):
\t\tvar tex: Texture2D = player_direction_art[key]
\t\tvar size: float = maxf(12.0, tile_size - 2.0)
\t\tif running:
\t\t\t# Two short afterimages make high-speed movement readable.
\t\t\tfor ghost_i in range(2, 0, -1):
\t\t\t\tvar ghost_center := draw_center - dir * (float(ghost_i) * 8.0)
\t\t\t\tvar ghost_alpha := 0.10 + float(2 - ghost_i) * 0.07
\t\t\t\tdraw_texture_rect(tex, Rect2(ghost_center - Vector2(size, size) * 0.5, Vector2(size, size)), false, Color(0.70, 0.88, 1.0, ghost_alpha))
\t\tdraw_texture_rect(tex, Rect2(draw_center - Vector2(size, size) * 0.5, Vector2(size, size)), false)
\telse:
\t\tdraw_entity_visual(draw_center, "player", "忍", 21, Color("#ffffff"), tile_size)
'''

s, n = re.subn(pattern, replacement.rstrip(), s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"dash run effect draw anchor failed: {n}")

required = [
    "DASH_RUN_EFFECT_PATCH_APPLIED",
    "dash_hold_active and dash_hold_repeating",
    "draw_dash_run_effect(center, tile_size, dir)",
    "sin(now * 28.0) * 1.8",
    "ghost_center := draw_center - dir",
    "func apply_permanent_stats() -> void:",
    "func draw_ui_text(",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f"dash run effect verification failed: {needle}")

if s == original:
    raise SystemExit("dash run effect made no changes")

p.write_text(s, encoding="utf-8")
print("DASH_RUN_EFFECT_PATCH PASS")
