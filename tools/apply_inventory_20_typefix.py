from pathlib import Path
p=Path('Main.gd')
s=p.read_text(encoding='utf-8')
s=s.replace('var max_offset := max(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)', 'var max_offset: int = maxi(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)')
s=s.replace('min(max(0, inventory_entry_count()-1), inventory_scroll_offset + INVENTORY_VISIBLE_ROWS - 1)', 'mini(maxi(0, inventory_entry_count()-1), inventory_scroll_offset + INVENTORY_VISIBLE_ROWS - 1)')
p.write_text(s,encoding='utf-8')
if 'var max_offset := max(0, inventory_entry_count() - INVENTORY_VISIBLE_ROWS)' in s:
    raise SystemExit('inventory typefix failed')
print('INVENTORY_20_TYPEFIX PASS')
exec(Path('tools/apply_hide_center_diamond.py').read_text(encoding='utf-8'), {})
