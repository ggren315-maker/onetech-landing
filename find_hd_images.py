import re, urllib.request, json

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8', errors='replace')

# Sample product page for HD images
page = fetch('https://aquafamily.ua/teplovoj-nasos-aquaviva-avh-15s-teplo-holod-gvs-15-kvt-220-v.html')
all_imgs = re.findall(r'(https://aquafamily\.ua/media/catalog/product[^"\s]+\.(?:jpg|jpeg|png|webp))', page)
print('Product page images:')
for u in sorted(set(all_imgs)):
    print(u)

# Check cache sizes available
caches = re.findall(r'/media/catalog/product/cache/([a-f0-9]+)/', page)
print('\nCache hashes:', sorted(set(caches)))

# Full path without cache
full = re.findall(r'/media/catalog/product/([a-z0-9/_\-]+\.(?:jpg|jpeg|png))', page, re.I)
print('\nDirect paths:')
for p in sorted(set(full))[:10]:
    print('https://aquafamily.ua/media/catalog/product/' + p)
