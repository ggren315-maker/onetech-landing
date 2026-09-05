import re, json, html, urllib.request, time

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='replace')

def to_hd(url):
    m = re.search(r'/media/catalog/product/cache/[a-f0-9]+/(.+\.(jpg|jpeg|png|webp))', url, re.I)
    if m:
        return f"https://aquafamily.ua/media/catalog/product/{m.group(1).replace('.webp', '.jpg')}"
    return url.replace('.webp', '.jpg')

page = fetch('https://aquafamily.ua/teplovye-nasosy-dlja-doma.html')
items = re.findall(r'<li class="item product product-item">([\s\S]*?)</li>', page)

products = []
for item in items:
    img = re.search(r'product-image-photo[^>]*src="([^"]+)"', item)
    link = re.search(r'href="(https://aquafamily\.ua/[^"]+\.html)"', item)
    name = re.search(r'class="product-item-link"[^>]*>\s*([^<]+)', item)
    price = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="finalPrice"', item)
    old = re.search(r'data-price-amount="([\d.]+)"\s+data-price-type="oldPrice"', item)
    reviews = re.search(r'Відгуки \((\d+)\)', item)
    if not img or not name or not price:
        continue
    img_url = to_hd(img.group(1))
    full_name = html.unescape(name.group(1).strip())
    m = re.search(r'(\d+(?:\.\d+)?)\s*кВт', full_name)
    power = float(m.group(1)) if m else 0
    if 'Aquaviva' in full_name: brand = 'aquaviva'
    elif 'Aquajoy Plus' in full_name: brand = 'aquajoy-plus'
    elif 'Aquajoy' in full_name: brand = 'aquajoy-comfort'
    elif 'Fairland' in full_name: brand = 'fairland'
    else: brand = 'other'

    products.append({
        'id': len(products) + 1,
        'name': full_name,
        'url': link.group(1) if link else '',
        'image': img_url,
        'gallery': [img_url],
        'price': int(float(price.group(1))),
        'oldPrice': int(float(old.group(1))) if old else None,
        'reviews': int(reviews.group(1)) if reviews else 0,
        'sale': bool(old),
        'power': power,
        'brand': brand,
    })

# Fetch extra gallery images per product page (unique only)
for p in products:
    if not p.get('url'):
        continue
    try:
        pg = fetch(p['url'])
        imgs = re.findall(r'(https://aquafamily\.ua/media/catalog/product/cache/[a-f0-9]+/[^"\s]+\.(?:jpg|jpeg|png|webp))', pg)
        unique = []
        seen = set()
        for u in imgs:
            hd = to_hd(u)
            key = hd.rsplit('/', 1)[-1]
            if key not in seen:
                seen.add(key)
                unique.append(hd)
        if unique:
            filtered = []
            for hd in unique:
                name = hd.rsplit('/', 1)[-1]
                if re.search(r'hqdefault|35156_35157_35158_mainpic|inner_structure_outdoor_unit', name, re.I):
                    continue
                if re.match(r'^[1-5]_1_1(_1)*\.jpg$', name, re.I):
                    continue
                filtered.append(hd)
            p['gallery'] = (filtered or unique)[:4]
            p['image'] = p['gallery'][0]
        print(f"#{p['id']:2d} {p['image'].split('/')[-1]:30s} gallery={len(p['gallery'])}")
        time.sleep(0.25)
    except Exception as e:
        print(f"ERR #{p['id']}: {e}")

# Verify uniqueness
images = [p['image'] for p in products]
dupes = len(images) - len(set(images))
print(f'\nTotal: {len(products)}, duplicate main images: {dupes}')

site_gallery = {
    'hero': list(dict.fromkeys([products[i]['image'] for i in [3, 0, 6, 17] if i < len(products)])),
    'install': [
        'https://aquafamily.ua/media/wysiwyg/teplov_nasos.png',
        'https://aquafamily.ua/media/wysiwyg/kalkulator_heat_1_.png',
        'https://aquafamily.ua/media/wysiwyg/circ_nasos_2.png',
        'https://aquafamily.ua/media/wysiwyg/bufer.png',
        'https://aquafamily.ua/media/wysiwyg/klapan.png',
        'https://aquafamily.ua/media/wysiwyg/podstavki_dla_teplovih.png',
    ],
    'allProducts': list(dict.fromkeys(p['image'] for p in products)),
}

with open('js/products-data.js', 'w', encoding='utf-8') as f:
    f.write('const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n')
    f.write('const SITE_GALLERY = ' + json.dumps(site_gallery, ensure_ascii=False, indent=2) + ';\n')

print('Saved js/products-data.js')
