from pathlib import Path


def replace_setting(path: Path, old: str, new: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if old not in text:
        return new in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


root = Path(__file__).resolve().parents[1]

portrait_sources = [
    root / "art/title_screen.jpg",
    root / "art/village_dojo.jpg",
    root / "art/village_blacksmith.jpg",
    root / "art/village_merchant.jpg",
    root / "art/village_warehouse.jpg",
]
portrait_count = 0
for source in portrait_sources:
    import_file = Path(str(source) + ".import")
    if replace_setting(import_file, "process/size_limit=0", "process/size_limit=512"):
        portrait_count += 1

glyph_count = 0
for source in sorted((root / "art/step76_glyphs").glob("*.svg")):
    import_file = Path(str(source) + ".import")
    if replace_setting(import_file, "svg/scale=1.0", "svg/scale=0.5"):
        glyph_count += 1

if portrait_count != len(portrait_sources):
    raise SystemExit(f"portrait import optimization incomplete: {portrait_count}/{len(portrait_sources)}")
if glyph_count < 100:
    raise SystemExit(f"glyph import optimization incomplete: {glyph_count}")

print(f"MOBILE_IMPORT_OPTIMIZATION PASS portraits={portrait_count} glyphs={glyph_count}")
