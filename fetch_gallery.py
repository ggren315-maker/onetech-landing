"""Fetch gallery images from aquafamily product pages and update products-data.js"""
import re, json, html, urllib.request, time

BASE = 'https://aquafamily.ua'
CACHE = '/media/catalog/product/cache/fc2407be589ad4a0d0391a9477787f8e/'

# Read existing products from JS file
with open('js/products-data.js', encoding='utf-8') as f:
    content = f.read()
products = json.loads(content.replace('const PRODUCTS = ', '').rstrip().rstrip(';'))

EXTRA_GALLERY = [
    'https://aquafamily.ua/media/wysiwyg/teplov_nasos.png',
    'https://aquafamily.ua/media/wysiwyg/kalkulator_heat_1_.png',
    'https://aquafamily.ua/media/wysiwyg/circ_nasos_2.png',
    'https://aquafamily.ua/media/wysiwyg/bufer.png',
    'https://aquafamily.ua/media/wysiwyg/klapan.png',
    'https://aquafamily.ua/media/wysiwyg/podstavki_dla_teplovih.png',
]

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

for p in products:
    if not p.get('url'):
        p['gallery'] = [p['image']]
        continue
    try:
        page = fetch(p['url'])
        imgs = re.findall(r'(https://aquafamily\.ua/media/catalog/product/cache/fc2407be589ad4a0d0391a9477787f8e/[^"\s]+\.(?:jpg|webp))', page)
        imgs = list(dict.fromkeys(imgs))  # unique, preserve order
        # prefer jpg over webp duplicates
        clean = []
        seen = set()
        for img in imgs:
            key = img.rsplit('.', 1)[0]
            if key not in seen:
                seen.add(key)
                clean.append(img.replace('.webp', '.jpg') if '.webp' in img else img)
        if p['image'] not in clean:
            clean.insert(0, p['image'])
        p['gallery'] = clean[:6] if clean else [p['image']]
        print(f"OK {p['id']}: {len(p['gallery'])} imgs")
        time.sleep(0.3)
    except Exception as e:
        p['gallery'] = [p['image']]
        print(f"ERR {p['id']}: {e}")

site_gallery = {
    'hero': [products[3]['image'], products[0]['image'], products[6]['image'], products[17]['image']],
    'install': EXTRA_GALLERY,
    'allProducts': [p['image'] for p in products],
}

with open('js/products-data.js', 'w', encoding='utf-8') as f:
    f.write('const PRODUCTS = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n')
    f.write('const SITE_GALLERY = ' + json.dumps(site_gallery, ensure_ascii=False, indent=2) + ';\n')

print('Done. Updated js/products-data.js')
