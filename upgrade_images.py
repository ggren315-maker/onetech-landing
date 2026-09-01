"""Upgrade all product images to HD (large cache or direct URL)"""
import re, json

HD = 'ee9223c9bea144064b4971ae08bedfd9'
SMALL = 'fc2407be589ad4a0d0391a9477787f8e'
BASE = 'https://aquafamily.ua'

def to_hd(url):
    if not url:
        return url
    # direct path (best quality)
    m = re.search(r'/media/catalog/product/cache/[a-f0-9]+/(.+\.(jpg|jpeg|png))', url, re.I)
    if m:
        path = m.group(1).replace('.webp', '.jpg')
        direct = f'{BASE}/media/catalog/product/{path}'
        return direct
    return url.replace(SMALL, HD).replace('.webp', '.jpg')

with open('js/products-data.js', encoding='utf-8') as f:
    text = f.read()

products = json.loads(text.split('const PRODUCTS = ')[1].split(';\nconst SITE_GALLERY')[0])
site = json.loads(text.split('const SITE_GALLERY = ')[1].rstrip().rstrip(';'))

for p in products:
    p['image'] = to_hd(p['image'])
    if p.get('gallery'):
        p['gallery'] = list(dict.fromkeys(to_hd(u) for u in p['gallery']))

for key in site:
    if isinstance(site[key], list):
        site[key] = list(dict.fromkeys(to_hd(u) for u in site[key]))

with open('js/products-data.js', 'w', encoding='utf-8') as f:
    f.write('const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n')
    f.write('const SITE_GALLERY = ' + json.dumps(site, ensure_ascii=False, indent=2) + ';\n')

print('Upgraded', len(products), 'products to HD images')
