"""Sync product prices from aquafamily.ua catalog."""
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
PRODUCTS_JS = ROOT / 'js' / 'products-data.js'
CATALOG_URL = 'https://aquafamily.ua/teplovye-nasosy-dlja-doma.html'


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode('utf-8', errors='replace')


def parse_catalog(page: str) -> dict[str, dict]:
    """Return {product_url: {price, oldPrice, sale, reviews, name}}."""
    items = re.findall(r'<li class="item product product-item">([\s\S]*?)</li>', page)
    catalog = {}

    for item in items:
        link = re.search(r'href="(https://aquafamily\.ua/[^"]+\.html)"', item)
        name = re.search(r'class="product-item-link"[^>]*>\s*([^<]+)', item)
        price = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="finalPrice"', item)
        old = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="oldPrice"', item)
        reviews = re.search(r'Відгуки \((\d+)\)', item)
        if not link or not price:
            continue

        url = link.group(1)
        catalog[url] = {
            'name': html.unescape(name.group(1).strip()) if name else '',
            'price': int(float(price.group(1))),
            'oldPrice': int(float(old.group(1))) if old else None,
            'sale': bool(old),
            'reviews': int(reviews.group(1)) if reviews else 0,
        }

    return catalog


def load_products_js() -> tuple[list, dict]:
    text = PRODUCTS_JS.read_text(encoding='utf-8')
    products_match = re.search(r'const PRODUCTS = (\[[\s\S]*?\]);', text)
    gallery_match = re.search(r'const SITE_GALLERY = (\{[\s\S]*?\});', text)
    if not products_match or not gallery_match:
        raise ValueError('Invalid products-data.js format')
    return json.loads(products_match.group(1)), json.loads(gallery_match.group(1))


def save_products_js(products: list, site_gallery: dict) -> None:
    content = (
        'const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n'
        'const SITE_GALLERY = ' + json.dumps(site_gallery, ensure_ascii=False, indent=2) + ';\n'
    )
    PRODUCTS_JS.write_text(content, encoding='utf-8')


def apply_catalog_prices(products: list, catalog: dict[str, dict]) -> int:
    """Update local products from catalog. Returns number of changed items."""
    changed = 0

    for product in products:
        live = catalog.get(product.get('url', ''))
        if not live:
            continue

        updates = {
            'price': live['price'],
            'oldPrice': live['oldPrice'],
            'sale': live['sale'],
            'reviews': live['reviews'],
        }

        if any(product.get(k) != v for k, v in updates.items()):
            product.update(updates)
            changed += 1

    return changed


def run_price_update() -> dict:
    """Fetch live catalog and update js/products-data.js prices."""
    page = fetch(CATALOG_URL)
    catalog = parse_catalog(page)
    products, site_gallery = load_products_js()

    matched = sum(1 for p in products if p.get('url') in catalog)
    changed = apply_catalog_prices(products, catalog)

    if changed:
        save_products_js(products, site_gallery)

    return {
        'at': datetime.now(timezone.utc).isoformat(),
        'products_total': len(products),
        'catalog_total': len(catalog),
        'matched': matched,
        'prices_changed': changed,
        'error': None,
    }


if __name__ == '__main__':
    result = run_price_update()
    print(
        f"Updated {result['prices_changed']}/{result['products_total']} products "
        f"(matched {result['matched']} from catalog)"
    )
