import urllib.request, re
h = urllib.request.urlopen(urllib.request.Request(
    'https://aquafamily.ua/teplovye-nasosy-dlja-doma.html',
    headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8', 'replace')
for u in sorted(set(re.findall(r'https://aquafamily\.ua/media/brand[^\s"\']+', h))):
    print(u)
