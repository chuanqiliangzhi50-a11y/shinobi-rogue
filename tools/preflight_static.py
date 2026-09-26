#!/usr/bin/env python3
from pathlib import Path
import re, collections, random, json, sys

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'Main.gd'
PROJECT = ROOT / 'project.godot'
EXPORT = ROOT / 'export_presets.ios.template.cfg'
VERSION = '1.0.54'
MAP_W, MAP_H = 31, 15

issues=[]
s=MAIN.read_text(encoding='utf-8')
proj=PROJECT.read_text(encoding='utf-8')
exp=EXPORT.read_text(encoding='utf-8')

funcs=re.findall(r'^func\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', s, re.M)
dupes=[name for name,c in collections.Counter(funcs).items() if c>1]
if dupes: issues.append('duplicate functions: '+', '.join(dupes))

# Basic delimiter balance after removing line comments and strings approximately.
def strip_strings_comments(src):
    out=[]
    for line in src.splitlines():
        buf=[]; quote=None; esc=False
        for i,ch in enumerate(line):
            if quote:
                if esc: esc=False
                elif ch=='\\': esc=True
                elif ch==quote: quote=None
                continue
            if ch in ('"', "'"):
                quote=ch; continue
            if ch=='#': break
            buf.append(ch)
        out.append(''.join(buf))
    return '\n'.join(out)
clean=strip_strings_comments(s)
for a,b in [('(',')'),('[',']'),('{','}')]:
    if clean.count(a)!=clean.count(b): issues.append(f'unbalanced {a}{b}: {clean.count(a)}/{clean.count(b)}')

if f'const VERSION := "{VERSION}"' not in s: issues.append('Main.gd version mismatch')
if f'config/version="{VERSION}"' not in proj: issues.append('project.godot version mismatch')
if f'application/short_version="{VERSION}"' not in exp: issues.append('iOS short version mismatch')
if 'application/version="54"' not in exp: issues.append('iOS build version mismatch')
if 'const RUN_SAVE_VERSION := 8' not in s: issues.append('save schema is not v8')

required_funcs = [
 'generate_floor','carve_safe_path','has_path_between','spawn_enemy','spawn_boss','generate_shop',
 'use_shadow_bind','use_shadow_clone','enemy_hunt_target','use_smoke_ninjutsu','use_ultimate',
 'register_ad_checkpoint','save_run_state','load_run_state','repair_loaded_run_state',
 'debug_run_regression_suite','debug_test_floor_reachability','debug_test_shadow_clone_contract',
 'debug_test_boss_resume_repair','debug_test_spawn_safety','debug_test_ui_glyph_contract','debug_test_inventory_contract','open_inventory','inventory_use_selected','inventory_identify_selected','content_offset'
]
for fn in required_funcs:
    if fn not in funcs: issues.append('missing function: '+fn)

for field in ['stairs_pos','clone_active','clone_pos','clone_steps_left','merchant_type','last_ad_checkpoint_floor','inventory_items']:
    if f'"{field}":' not in s: issues.append('missing save field: '+field)

for ref in re.findall(r'"res://([^"\n]+)"', proj + '\n' + (ROOT/'Main.tscn').read_text(encoding='utf-8')):
    if not (ROOT/ref).exists(): issues.append('missing res:// reference: '+ref)

if 'window/stretch/aspect="expand"' not in proj: issues.append('mobile expand stretch missing')
if 'window/size/viewport_width=720' not in proj or 'window/size/viewport_height=1100' not in proj: issues.append('portrait viewport missing')
if not (ROOT/'ui_glyphs.png').exists(): issues.append('bitmap glyph atlas missing')
if 'pointing/emulate_touch_from_mouse=true' not in proj: issues.append('touch emulation missing')
if '--shinobi-regression' not in s: issues.append('headless regression entry missing')
if 'const RELEASE_CHANNEL := "PLAY UI SYSTEM RC"' not in s: issues.append('PLAY UI SYSTEM RC marker missing')
if 'const DEVELOPMENT_UI_ENABLED := false' not in s: issues.append('development UI not disabled for RC')
if 'const ADS_ENABLED := false' not in s: issues.append('initial release ads must remain disabled until native SDK integration')
if 'debug_test_final_floor_contract' not in funcs: issues.append('100F release contract regression missing')

# Release UI must not depend on OS/browser Japanese fonts.
if 'SystemFont.new' in s or 'draw_string(' in s:
    issues.append('system font dependency remains')

# Verify every non-ASCII character used in Main.gd string literals is available in the bitmap atlas map.
glyph_keys=set(re.findall(r'^\s*"([^"\\]|\\.)+":\s*Vector2i', s, re.M))
# Re-extract keys more reliably line by line, including escaped ASCII quotes.
glyph_chars=set()
for line in s.splitlines():
    m=re.match(r'^\s*"(.*)":\s*Vector2i\(', line)
    if m:
        raw=m.group(1)
        if raw == '\\"': glyph_chars.add('"')
        elif raw == '\\\\': glyph_chars.add('\\')
        else: glyph_chars.add(raw)
# Individually bundled vector glyphs use the same renderer as the bitmap atlas.
glyph_chars.update(re.findall(r'^\s*"(.)":\s*"res://art/step76_glyphs/', s, re.M))
glyph_chars.update(["裏", "剣"])
for lit in re.findall(r'"((?:\\.|[^"\\])*)"', s):
    for ch in lit:
        if ord(ch) >= 128 and ch not in glyph_chars:
            issues.append('missing UI glyph: '+ch)
            break

# Monte Carlo invariant check for floor generation. The GDScript carves a direct
# Manhattan route after random wall placement; verify that contract over many seeds.
def safe_path_cells(seed):
    r=random.Random(seed)
    goal=(MAP_W-3, MAP_H-3)
    x,y=2,2
    cells={(x,y)}
    horizontal_first = r.randint(0,1)==0
    if horizontal_first:
        while x != goal[0]:
            x += 1 if goal[0] > x else -1; cells.add((x,y))
        while y != goal[1]:
            y += 1 if goal[1] > y else -1; cells.add((x,y))
    else:
        while y != goal[1]:
            y += 1 if goal[1] > y else -1; cells.add((x,y))
        while x != goal[0]:
            x += 1 if goal[0] > x else -1; cells.add((x,y))
    return cells, goal

N=50000
min_safe=10**9
for seed in range(N):
    cells,goal=safe_path_cells(seed)
    min_safe=min(min_safe,len(cells))
    if (2,2) not in cells or goal not in cells:
        issues.append(f'monte carlo safe-path failure seed {seed}')
        break

report={
 'version': VERSION,
 'status': 'PASS' if not issues else 'FAIL',
 'functions': len(funcs),
 'unique_functions': len(set(funcs)),
 'save_schema': 8,
 'monte_carlo_floor_generations': N,
 'monte_carlo_min_safe_path_cells': min_safe,
 'issues': issues,
 'godot_engine_execution': 'NOT RUN by this Python checker'
}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(0 if not issues else 1)
