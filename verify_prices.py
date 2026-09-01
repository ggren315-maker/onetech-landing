import re, html, urllib.request, json

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='replace')

# Load local products
local_text = open('js/products-data.js', encoding='utf-8').read()
local = json.loads(re.search(r'const PRODUCTS = (\[[\s\S]*?\]);', local_text).group(1))

# Parse live catalog
page = fetch('https://aquafamily.ua/teplovye-nasosy-dlja-doma.html')
items = re.findall(r'<li class="item product product-item">([\s\S]*?)</li>', page)

live = []
for item in items:
    link = re.search(r'href="(https://aquafamily\.ua/[^"]+\.html)"', item)
    name = re.search(r'class="product-item-link"[^>]*>\s*([^<]+)', item)
    price = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="finalPrice"', item)
    old = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="oldPrice"', item)
    if not name or not price or not link:
        continue
    live.append({
        'url': link.group(1),
        'name': html.unescape(name.group(1).strip()),
        'price': int(float(price.group(1))),
        'oldPrice': int(float(old.group(1))) if old else None,
    })

print(f'Local products: {len(local)}')
print(f'Live catalog:   {len(live)}')
print()

mismatches = []
for i, (loc, lv) in enumerate(zip(local, live), 1):
    ok_price = loc['price'] == lv['price']
    ok_old = loc.get('oldPrice') == lv.get('oldPrice')
    ok_url = loc.get('url') == lv.get('url')
    if not (ok_price and ok_old and ok_url):
        mismatches.append((i, loc, lv, ok_price, ok_old, ok_url))

if not mismatches:
    print('All prices match the live catalog.')
else:
    print(f'Mismatches: {len(mismatches)}')
    for i, loc, lv, ok_p, ok_o, ok_u in mismatches:
        short = loc['name'][:60] + '...'
        print(f'\n#{i} {short}')
        if not ok_u:
            print(f'  URL local: {loc.get("url")}')
            print(f'  URL live:  {lv.get("url")}')
        if not ok_p:
            print(f'  Price local: {loc["price"]:,}  live: {lv["price"]:,}')
        if not ok_o:
            print(f'  Old   local: {loc.get("oldPrice")}  live: {lv.get("oldPrice")}')

# Also spot-check a few product pages individually
print('\n--- Spot-check on product pages (first 3 with sale) ---')
sale_items = [p for p in local if p.get('oldPrice')][:3]
for p in sale_items:
    pg = fetch(p['url'])
    price = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="finalPrice"', pg)
    old = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="oldPrice"', pg)
    lp = int(float(price.group(1))) if price else None
    lo = int(float(old.group(1))) if old else None
    ok = lp == p['price'] and lo == p.get('oldPrice')
    status = 'OK' if ok else 'MISMATCH'
    print(f'#{p["id"]} [{status}] local {p["price"]}/{p.get("oldPrice")} page {lp}/{lo}')
