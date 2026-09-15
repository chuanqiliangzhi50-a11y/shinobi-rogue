from pathlib import Path

p = Path('Main.gd')
s = p.read_text(encoding='utf-8')
original = s

replacements = {
    'var seed := abs(x * 37 + y * 61)': 'var seed: int = abs(x * 37 + y * 61)',
    'var wall := Color("#27313d") if seed % 3 else Color("#303b47")': 'var wall: Color = Color("#27313d") if seed % 3 else Color("#303b47")',
    'var lamp := p + Vector2(tile_size * 0.5, tile_size * 0.5)': 'var lamp: Vector2 = p + Vector2(tile_size * 0.5, tile_size * 0.5)',
    'var floor_col := Color("#6c5b46") if seed % 4 else Color("#75634b")': 'var floor_col: Color = Color("#6c5b46") if seed % 4 else Color("#75634b")',
    'var idx := enemy_sheet_index(str(enemy.get("kind", "samurai")), bool(enemy.get("boss", false)))': 'var idx: int = enemy_sheet_index(str(enemy.get("kind", "samurai")), bool(enemy.get("boss", false)))',
    'var idx := item_sheet_index(str(item.get("name", "")))': 'var idx: int = item_sheet_index(str(item.get("name", "")))',
    'var size := maxf(28.0, tile_size + 7.0)': 'var size: float = maxf(28.0, tile_size + 7.0)',
    'var size := maxf(25.0, tile_size - 2.0)': 'var size: float = maxf(25.0, tile_size - 2.0)',
    'var dest := Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size))': 'var dest: Rect2 = Rect2(center - Vector2(size, size) * 0.5, Vector2(size, size))',
    'var c := Color("#9d2832")': 'var c: Color = Color("#9d2832")',
    'var cell_pos := Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)': 'var cell_pos: Vector2 = Vector2(PMAP_X + vx * PTILE, PMAP_Y + vy * PTILE)',
    'var seen := validate_grid(explored) and bool(explored[wy][wx])': 'var seen: bool = validate_grid(explored) and bool(explored[wy][wx])',
    'var tile := str(map[wy][wx]) if validate_grid(map) else "#"': 'var tile: String = str(map[wy][wx]) if validate_grid(map) else "#"',
    'var label := str(d_control[0])': 'var label: String = str(d_control[0])',
}

for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new)

if 'var seed: int = abs(x * 37 + y * 61)' not in s:
    raise SystemExit('reference skin typefix verification failed')
if s == original:
    raise SystemExit('reference skin typefix made no changes')
p.write_text(s, encoding='utf-8')
print('REFERENCE_GAMEPLAY_SKIN_TYPEFIX PASS')
