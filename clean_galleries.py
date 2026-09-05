"""Clean product galleries: drop junk/shared images, cap per product."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'js' / 'products-data.js'
MAX_GALLERY = 4

JUNK_RE = re.compile(
    r'hqdefault|35156_35157_35158_mainpic|inner_structure_outdoor_unit',
    re.I,
)

# Generic numbered shots reused across unrelated models
GENERIC_RE = re.compile(r'^[1-5]_1_1(_1)*\.jpg$', re.I)


def filename(url: str) -> str:
    return url.rsplit('/', 1)[-1].split('?')[0]


def is_junk(url: str, *, allow_main: bool = False) -> bool:
    name = filename(url)
    if JUNK_RE.search(name):
        return not allow_main
    if GENERIC_RE.match(name):
        return not allow_main
    return False


def load_js(path: Path):
    text = path.read_text(encoding='utf-8')
    products = json.loads(text.split('=', 1)[1].split(';', 1)[0].strip())
    site = json.loads(text.split('SITE_GALLERY =', 1)[1].split(';', 1)[0].strip())
    return products, site


def save_js(path: Path, products, site):
    path.write_text(
        'const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n'
        + 'const SITE_GALLERY = ' + json.dumps(site, ensure_ascii=False, indent=2) + ';\n',
        encoding='utf-8',
    )


def clean_gallery(product, global_counts):
    main = product['image']
    candidates = [main, *(product.get('gallery') or [])]
    seen = set()
    out = []

    for i, url in enumerate(candidates):
        if not url:
            continue
        key = filename(url)
        if key in seen:
            continue
        seen.add(key)

        allow_main = i == 0 or url == main
        if is_junk(url, allow_main=allow_main):
            continue
        # Drop images that appear on many unrelated products (shared pool bleed)
        if not allow_main and global_counts.get(key, 0) > 4:
            continue

        out.append(url)
        if len(out) >= MAX_GALLERY:
            break

    if not out:
        out = [main]
    product['gallery'] = out
    product['image'] = out[0]
    return len(out)


def main():
    products, site = load_js(DATA)

    counts = {}
    for p in products:
        for url in [p['image'], *(p.get('gallery') or [])]:
            counts[filename(url)] = counts.get(filename(url), 0) + 1

    before = sum(len(p.get('gallery') or []) for p in products)
    for p in products:
        n = clean_gallery(p, counts)
        print(f"#{p['id']:2d} {filename(p['image'])[:36]:36s} -> {n} photos")

    after = sum(len(p.get('gallery') or []) for p in products)

    # Hero: one distinct main image per brand / size class
    hero_ids = [1, 2, 4, 18]
    site['hero'] = list(dict.fromkeys(
        products[i - 1]['image'] for i in hero_ids if i <= len(products)
    ))
    site.pop('allProducts', None)

    save_js(DATA, products, site)
    print(f'\nGallery slots: {before} -> {after} (max {MAX_GALLERY} per product)')


if __name__ == '__main__':
    main()
