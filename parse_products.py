import re, json, html as h

html = open('_page.html', encoding='utf-8').read()
items = re.findall(r'<li class="item product product-item">([\s\S]*?)</li>', html)
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
    products.append({
        'name': h.unescape(name.group(1).strip()),
        'url': link.group(1) if link else '',
        'image': img.group(1),
        'price': int(float(price.group(1))),
        'oldPrice': int(float(old.group(1))) if old else None,
        'reviews': int(reviews.group(1)) if reviews else 0,
        'sale': bool(old),
    })

for i, p in enumerate(products):
    p['id'] = i + 1
    m = re.search(r'(\d+(?:\.\d+)?)\s*кВт', p['name'])
    p['power'] = float(m.group(1)) if m else 0
    if 'Aquaviva' in p['name']: p['brand'] = 'aquaviva'
    elif 'Aquajoy Plus' in p['name']: p['brand'] = 'aquajoy-plus'
    elif 'Aquajoy' in p['name']: p['brand'] = 'aquajoy-comfort'
    elif 'Fairland' in p['name']: p['brand'] = 'fairland'
    else: p['brand'] = 'other'

with open('js/products-data.js', 'w', encoding='utf-8') as f:
    f.write('const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n')
print('Exported', len(products), 'products to js/products-data.js')
