from pathlib import Path
import re

p = Path("Main.gd")
s = p.read_text(encoding="utf-8")

corrected_shop = '''func generate_shop() -> void:
\tshop_active = true
\tmerchant_type = "闇商人" if floor_no >= 20 and rng.randi_range(0, 99) < 25 else "旅商人"
\tvar candidates: Array = []
\tfor r in floor_rooms:
\t\tif not r.has_point(player) and not r.has_point(stairs_pos):
\t\t\tcandidates.append(r)
\tvar chosen: Rect2i = candidates[rng.randi_range(0, candidates.size() - 1)] if not candidates.is_empty() else floor_rooms[0]
\tshop_rect = chosen
\tshopkeeper_home = chosen.get_center()
\tshopkeeper = {"pos": shopkeeper_home, "hp": 999, "atk": 18 + floor_no if merchant_type == "闇商人" else 12 + floor_no}
\tvar names: Array[String] = ["薬", "兵糧丸", "忍気丸"]
\tif merchant_type == "闇商人":
\t\tnames = ["上薬", "中巻物", "大巻物" if floor_no >= 50 else "忍気丸"]
\telif floor_no >= 40:
\t\tnames[rng.randi_range(0, 2)] = "上薬"
\tif floor_no >= 70:
\t\tnames[rng.randi_range(0, 2)] = "大兵糧丸"
\tvar offsets: Array[Vector2i] = [Vector2i(-1, 1), Vector2i(0, 1), Vector2i(1, 1)]
\tfor i in range(3):
\t\tvar ip: Vector2i = shopkeeper_home + offsets[i]
\t\tvar price: int = int(item_shop_price(str(names[i])))
\t\tif merchant_type == "闇商人":
\t\t\tprice = int(ceil(float(price) * 1.25))
\t\tvar it: Dictionary = {"pos": ip, "name": names[i], "count": 1, "price": price, "shop": true}
\t\titems.append(it)
\t\tshop_items.append(it)
'''

s2, n = re.subn(
    r'func generate_shop\(\) -> void:\n.*?(?=\n\nfunc find_random_open_cell)',
    corrected_shop,
    s,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"shop function anchor failed: {n}")

required = [
    'price = int(ceil(float(price) * 1.25))',
    'elif floor_no >= 40:',
    'if floor_no >= 70:',
    'names[rng.randi_range(0, 2)] = "上薬"',
    'names[rng.randi_range(0, 2)] = "大兵糧丸"',
]
for token in required:
    if token not in s2:
        raise SystemExit(f"shop rule restore assertion failed: {token}")

p.write_text(s2, encoding="utf-8")
print("SHOP_RULE_RESTORE_PATCH PASS")
