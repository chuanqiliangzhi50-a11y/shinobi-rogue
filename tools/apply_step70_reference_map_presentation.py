from pathlib import Path
import re

p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
original=s

if 'STEP70_REFERENCE_MAP_PRESENTATION_APPLIED' in s:
    print('STEP70_REFERENCE_MAP_PRESENTATION PASS (already applied)')
    raise SystemExit(0)

# Reference screen shows the dungeon itself at all times and no minimap overlay
# until the book/map control is requested.
s=s.replace('var map_visible: bool = true', 'var map_visible: bool = false # STEP70_REFERENCE_MAP_PRESENTATION_APPLIED', 1)

start=s.find('func draw_dungeon_portrait() -> void:')
end=s.find('\n\nfunc draw_mobile_controls_portrait()', start)
if start < 0 or end < 0:
    raise SystemExit('STEP70 portrait draw bounds failed')
block=s[start:end]
needle='\tif map_visible:\n\t\tfor vy in range(VIEW_H):'
idx=block.find(needle)
if idx < 0:
    raise SystemExit('STEP70 dungeon visibility anchor failed')
loop_end=block.find('\n\tfor trap in placed_traps:', idx)
if loop_end < 0:
    raise SystemExit('STEP70 dungeon loop end failed')
chunk=block[idx:loop_end]
lines=chunk.splitlines()
# Remove the map_visible guard and dedent its dungeon tile loop one level.
dedented=[]
for line in lines[1:]:
    dedented.append(line[1:] if line.startswith('\t') else line)
block=block[:idx]+'\n'.join(dedented)+block[loop_end:]
s=s[:start]+block+s[end:]

required=[
    'STEP70_REFERENCE_MAP_PRESENTATION_APPLIED',
    'var map_visible: bool = false',
    'if map_visible:\n\t\tdraw_explored_minimap_portrait()'
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'STEP70 verification failed: {needle}')
# The dungeon tile loop must no longer be directly guarded by map_visible.
final_block=s[s.find('func draw_dungeon_portrait() -> void:'):s.find('\n\nfunc draw_mobile_controls_portrait()',s.find('func draw_dungeon_portrait() -> void:'))]
if '\tif map_visible:\n\t\tfor vy in range(VIEW_H):' in final_block:
    raise SystemExit('STEP70 dungeon still hidden with minimap')
if s == original:
    raise SystemExit('STEP70 made no changes')

p.write_text(s,encoding='utf-8')
print('STEP70_REFERENCE_MAP_PRESENTATION PASS')
