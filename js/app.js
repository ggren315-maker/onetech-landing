const BRANDS = {
  aquaviva: 'Aquaviva',
  'aquajoy-comfort': 'Aquajoy Comfort',
  'aquajoy-plus': 'Aquajoy Plus',
  fairland: 'Fairland',
  other: 'Інше',
};

const KIT_ITEMS = [
  { img: SITE_GALLERY.install[0], title: 'Спліт-система', desc: 'Зовнішній + внутрішній блок' },
  { img: SITE_GALLERY.install[2], title: 'Циркуляційний насос', desc: 'Подача теплоносія в систему' },
  { img: SITE_GALLERY.install[3], title: 'Буферна ємність', desc: 'Для ГВС та стабільної роботи' },
  { img: SITE_GALLERY.install[4], title: 'Триходовий клапан', desc: 'Перемикання опалення / ГВС' },
  { img: SITE_GALLERY.install[5], title: 'Оpори та кріплення', desc: 'Надійне встановлення блоків' },
  { img: SITE_GALLERY.install[1], title: 'Система управління', desc: 'Пульт, датчики, автоматика' },
];

function shortName(full) {
  const m = full.match(/(?:Aquaviva|Aquajoy|Fairland)[^\,]+/);
  return m ? m[0].trim() : full.slice(0, 60);
}

function formatPrice(n) {
  return n.toLocaleString('uk-UA') + ' ₴';
}

function discountPercent(price, oldPrice) {
  if (!oldPrice) return 0;
  return Math.round((1 - price / oldPrice) * 100);
}

function getAllGalleryPhotos() {
  const items = [];
  const seen = new Set();

  const add = (src, title, id, kit = false) => {
    if (!src || seen.has(src)) return;
    seen.add(src);
    items.push({ src, title, id, kit });
  };

  PRODUCTS.forEach(p => {
    add(p.image, shortName(p.name), p.id);
    (p.gallery || []).forEach(g => add(g, shortName(p.name), p.id));
  });

  KIT_ITEMS.forEach(k => add(k.img, k.title, null, true));

  return items;
}

function getProductGallery(p) {
  const imgs = p.gallery?.length ? p.gallery : [p.image];
  return [...new Set([p.image, ...imgs])];
}

let currentFilter = 'all';
let heroIndex = 0;
let heroTimer;

function cardHTML(p, featured = false) {
  const title = shortName(p.name);

  return `
    <article class="product-card reveal ${featured ? 'featured' : ''}" data-id="${p.id}" data-brand="${p.brand}">
      <a href="product.html?id=${p.id}" class="product-img">
        <img src="${p.image}" alt="${title}" loading="lazy">
      </a>
      <div class="product-body">
        <div class="product-brand">${BRANDS[p.brand] || p.brand}</div>
        <h3 class="product-title"><a href="product.html?id=${p.id}">${title}</a></h3>
        <div class="product-meta">
          <span class="meta-chip">${p.power} кВт</span>
          ${p.sale ? '<span class="meta-chip meta-chip-soft">Спецпропозиція</span>' : ''}
        </div>
        <div class="product-price-block">
          <div class="price-row">
            <span class="price-now">${formatPrice(p.price)}</span>
            ${p.oldPrice ? `<span class="price-old">${formatPrice(p.oldPrice)}</span>` : ''}
          </div>
        </div>
        <div class="product-actions">
          <a href="product.html?id=${p.id}" class="btn btn-outline btn-sm btn-block">Характеристики</a>
          <button class="btn btn-primary btn-sm btn-block order-btn" data-id="${p.id}">Консультація</button>
        </div>
      </div>
    </article>`;
}

function getFiltered() {
  const q = (document.getElementById('search')?.value || '').toLowerCase();
  const sort = document.getElementById('sort')?.value || 'default';

  let list = PRODUCTS.filter(p => {
    if (currentFilter !== 'all' && currentFilter !== 'sale' && p.brand !== currentFilter) return false;
    if (currentFilter === 'sale' && !p.sale) return false;
    if (q && !p.name.toLowerCase().includes(q)) return false;
    return true;
  });

  if (sort === 'price-asc') list.sort((a, b) => a.price - b.price);
  else if (sort === 'price-desc') list.sort((a, b) => b.price - a.price);
  else if (sort === 'power-asc') list.sort((a, b) => a.power - b.power);
  else if (sort === 'power-desc') list.sort((a, b) => b.power - a.power);

  return list;
}

function renderFeatured() {
  const picks = [4, 1, 8].map(id => PRODUCTS.find(p => p.id === id)).filter(Boolean);
  const el = document.getElementById('featuredGrid');
  if (el) { el.innerHTML = picks.map(p => cardHTML(p, true)).join(''); bindCards('#featuredGrid'); }
}

function renderCatalog() {
  const grid = document.getElementById('catalogGrid');
  if (!grid) return;
  const list = getFiltered();
  grid.innerHTML = list.length
    ? list.map(p => cardHTML(p)).join('')
    : '<p style="grid-column:1/-1;text-align:center;padding:48px;color:var(--ink-muted)">Нічого не знайдено</p>';
  bindCards('#catalogGrid');
  observeReveal();
}

function renderMosaic() {
  const el = document.getElementById('photoMosaic');
  if (!el) return;
  const photos = getAllGalleryPhotos();

  el.innerHTML = photos.map(item => `
    <div class="mosaic-item ${item.kit ? 'kit-item' : ''}" data-id="${item.id || ''}">
      <img src="${item.src}" alt="${item.title}" loading="lazy">
      <div class="mosaic-label">${item.title}</div>
    </div>`).join('');

  const countEl = document.getElementById('galleryCount');
  if (countEl) countEl.textContent = `${photos.length} фото в галереї`;

  el.querySelectorAll('.mosaic-item[data-id]').forEach(item => {
    if (!item.dataset.id) return;
    item.addEventListener('click', () => { location.href = `product.html?id=${item.dataset.id}`; });
  });
}

function renderKit() {
  const el = document.getElementById('kitGrid');
  if (!el) return;
  el.innerHTML = KIT_ITEMS.map(k => `
    <div class="kit-card">
      <img src="${k.img}" alt="${k.title}" loading="lazy">
      <div class="kit-card-body"><h4>${k.title}</h4><p>${k.desc}</p></div>
    </div>`).join('');
}

function initHeroSlider() {
  const imgs = SITE_GALLERY.hero;
  const slide = document.querySelector('[data-hero-slide]');
  const thumbs = document.getElementById('heroThumbs');
  if (!slide || !thumbs) return;

  slide.src = imgs[0];
  slide.alt = 'Тепловий насос';
  thumbs.innerHTML = imgs.map((src, i) => `
    <button class="hero-thumb ${i === 0 ? 'active' : ''}" data-i="${i}">
      <img src="${src}" alt="">
    </button>`).join('');

  thumbs.querySelectorAll('.hero-thumb').forEach(btn => {
    btn.addEventListener('click', () => setHeroSlide(+btn.dataset.i));
  });

  heroTimer = setInterval(() => setHeroSlide((heroIndex + 1) % imgs.length), 4500);
}

function setHeroSlide(i) {
  heroIndex = i;
  const imgs = SITE_GALLERY.hero;
  const slide = document.querySelector('[data-hero-slide]');
  if (slide) slide.src = imgs[i];
  document.querySelectorAll('.hero-thumb').forEach((t, j) => t.classList.toggle('active', j === i));
}

function bindCards(selector) {
  document.querySelectorAll(`${selector} .order-btn`).forEach(btn => {
    btn.addEventListener('click', e => { e.preventDefault(); openOrder(+btn.dataset.id); });
  });
}

function setOrderModel(label) {
  const input = document.getElementById('model');
  const hint = document.getElementById('modelHint');
  const text = document.getElementById('modelHintText');
  if (!input) return;
  input.value = label || '';
  if (hint && text) {
    if (label) {
      text.textContent = label;
      hint.hidden = false;
      hint.classList.add('show');
    } else {
      hint.hidden = true;
      hint.classList.remove('show');
      text.textContent = '';
    }
  }
}

function clearOrderModel() {
  setOrderModel('');
}

function openOrder(id) {
  const p = PRODUCTS.find(x => x.id === id);
  if (!p) return;
  const label = shortName(p.name);
  const onContact = document.body.dataset.page === 'contact';

  if (onContact) {
    setOrderModel(label);
    document.getElementById('order')?.scrollIntoView({ behavior: 'smooth' });
    document.getElementById('phone')?.focus();
  } else {
    location.href = `contact.html?order=${id}`;
  }
}

function setModalImage(src) {
  document.getElementById('modalImg').src = src;
  document.querySelectorAll('.modal-thumb').forEach(t => {
    t.classList.toggle('active', t.querySelector('img').src === src);
  });
}

function openModal(id) {
  const p = PRODUCTS.find(x => x.id === id);
  if (!p) return;
  const title = shortName(p.name);
  const gallery = getProductGallery(p);

  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalImg').src = gallery[0];
  document.getElementById('modalPrice').innerHTML = `
    <span class="price-now">${formatPrice(p.price)}</span>
    ${p.oldPrice ? `<span class="price-old">${formatPrice(p.oldPrice)}</span>` : ''}`;

  document.getElementById('modalThumbs').innerHTML = gallery.map((src, i) => `
    <button class="modal-thumb ${i === 0 ? 'active' : ''}" type="button">
      <img src="${src}" alt="">
    </button>`).join('');

  document.getElementById('modalThumbs').querySelectorAll('.modal-thumb').forEach(btn => {
    btn.addEventListener('click', () => setModalImage(btn.querySelector('img').src));
  });

  document.getElementById('modalSpecs').innerHTML = `
    <li><span>Бренд</span><span>${BRANDS[p.brand]}</span></li>
    <li><span>Потужність</span><span>${p.power} кВт</span></li>
    <li><span>Фото</span><span>${gallery.length} зображень</span></li>
    <li><span>Доставка</span><span>Безкоштовна по Україні</span></li>
    <li><span>Гарантія</span><span>Офіційна від виробника</span></li>`;

  document.getElementById('modalOrder').onclick = () => { closeModal(); openOrder(id); };
  document.getElementById('productModal').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('productModal')?.classList.remove('open');
  document.body.style.overflow = '';
}

function initForm() {
  const form = document.getElementById('orderForm');
  if (!form) return;

  document.getElementById('modelHintClear')?.addEventListener('click', clearOrderModel);

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const ok = document.getElementById('formOk');
    const err = document.getElementById('formErr');
    const btn = form.querySelector('[type=submit]');
    const submitLabel = btn.dataset.submitLabel || btn.textContent;
    ok.classList.remove('show');
    err.classList.remove('show');

    const modelValue = document.getElementById('model').value.trim();
    const payload = {
      name: document.getElementById('name').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      model: modelValue || 'Потрібна консультація — підберемо модель',
      message: document.getElementById('message').value.trim() || '—',
    };

    btn.disabled = true;
    btn.textContent = 'Відправляємо...';

    try {
      await submitLead(payload);
      ok.classList.add('show');
      form.reset();
      clearOrderModel();
    } catch (ex) {
      err.textContent = ex.message;
      err.classList.add('show');
    } finally {
      btn.disabled = false;
      btn.textContent = submitLabel;
    }
  });
}

async function submitLead(data) {
  const res = await fetch('/api/lead', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  const body = await res.json();
  if (!res.ok) throw new Error(body.error || 'Помилка відправки');
  return body;
}

const INSULATION_W = { good: 0.06, avg: 0.08, poor: 0.10 };
let pickInsulation = 'avg';

function requiredPowerKw(area, ins = pickInsulation) {
  return Math.round(area * (INSULATION_W[ins] || 0.08) * 10) / 10;
}

function recommendByArea(area, ins = pickInsulation) {
  const required = requiredPowerKw(area, ins);
  const sorted = [...PRODUCTS].sort((a, b) => a.power - b.power);
  const fits = sorted.filter(p => p.power >= required * 0.92);
  const primary = fits[0] || sorted[sorted.length - 1];
  const idx = sorted.findIndex(p => p.id === primary.id);

  const items = [{ product: primary, tag: 'Оптимально', main: true }];
  if (idx > 0) items.push({ product: sorted[idx - 1], tag: 'Економніше', main: false });
  const next = sorted[idx + 1];
  if (next && next.id !== primary.id) items.push({ product: next, tag: 'З запасом', main: false });

  return {
    required,
    items: items.slice(0, 3),
    undersized: primary.power < required,
    maxPower: sorted[sorted.length - 1].power,
  };
}

function pickCardHTML(item) {
  const p = item.product;
  const title = shortName(p.name);
  return `
    <article class="pick-card ${item.main ? 'pick-card-main' : ''}">
      <span class="pick-tag">${item.tag}</span>
      <div class="pick-card-brand">${BRANDS[p.brand]}</div>
      <h4>${title}</h4>
      <div class="pick-card-meta">${p.power} кВт · ${formatPrice(p.price)}</div>
      <div class="pick-card-actions">
        <a href="product.html?id=${p.id}" class="btn btn-ghost btn-sm">Деталі</a>
        <button type="button" class="btn btn-primary btn-sm pick-order-btn" data-id="${p.id}">Замовити</button>
      </div>
    </article>`;
}

function updatePickRecommendations() {
  const area = parseFloat(document.getElementById('saveArea')?.value) || 120;
  const { required, items, undersized, maxPower } = recommendByArea(area);
  const insLabel = { good: 'добра', avg: 'середня', poor: 'слабка' }[pickInsulation];

  const summary = document.getElementById('pickSummary');
  const cards = document.getElementById('pickCards');
  if (!summary || !cards) return;

  let text = `Для <strong>${area} м²</strong> (${insLabel} теплоізоляція) рекомендована потужність — <strong>${required} кВт</strong>.`;
  if (undersized && required > maxPower) {
    text += ` Максимальна модель у каталозі — <strong>${maxPower} кВт</strong>; для такої площі може знадобитися кілька блоків — передзвонимо та порахуємо.`;
  }
  summary.innerHTML = text;

  cards.innerHTML = items.map(pickCardHTML).join('');
  cards.querySelectorAll('.pick-order-btn').forEach(btn => {
    btn.addEventListener('click', () => openOrder(+btn.dataset.id));
  });

  const orderBtn = document.getElementById('pickOrderBtn');
  if (orderBtn) {
    const main = items.find(i => i.main)?.product;
    orderBtn.onclick = () => { if (main) openOrder(main.id); };
  }
}

function initPickCalculator() {
  document.getElementById('pickInsulation')?.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('#pickInsulation .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      pickInsulation = chip.dataset.ins || 'avg';
      calcSavings();
    });
  });
  document.getElementById('saveArea')?.addEventListener('input', calcSavings);
}

function calcSavings() {
  const area = parseFloat(document.getElementById('saveArea')?.value) || 120;
  const gas = Math.round(area * 42 * 5);
  const el = Math.round(area * 58 * 5);
  const hp = Math.round(area * 14 * 5);
  document.getElementById('saveGas').textContent = formatPrice(gas);
  document.getElementById('saveEl').textContent = formatPrice(el);
  document.getElementById('saveHp').textContent = formatPrice(hp);
  document.getElementById('saveTotal').textContent = formatPrice(gas - hp);
  const max = el;
  document.querySelector('.bar-fill.gas').style.width = (gas / max * 100) + '%';
  document.querySelector('.bar-fill.el').style.width = '100%';
  document.querySelector('.bar-fill.hp').style.width = (hp / max * 100) + '%';
  updatePickRecommendations();
}

function initFAQ() {
  document.querySelectorAll('.faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const open = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!open) item.classList.add('open');
    });
  });
}

function observeReveal() {
  document.querySelectorAll('.reveal:not(.show)').forEach(el => {
    new IntersectionObserver(([e]) => { if (e.isIntersecting) el.classList.add('show'); }, { threshold: 0.08 }).observe(el);
  });
}

function initCatalogNav() {
  document.querySelectorAll('.filter-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentFilter = tab.dataset.filter;
      renderCatalog();
    });
  });
  document.getElementById('search')?.addEventListener('input', renderCatalog);
  document.getElementById('sort')?.addEventListener('change', renderCatalog);
  document.getElementById('productModal')?.addEventListener('click', e => {
    if (e.target.id === 'productModal') closeModal();
  });
  document.querySelector('.modal-close')?.addEventListener('click', closeModal);
}

function initProductPage() {
  const params = new URLSearchParams(location.search);
  const id = +params.get('id');
  const p = PRODUCTS.find(x => x.id === id);
  if (!p) { document.getElementById('productContent').innerHTML = '<p>Товар не знайдено. <a href="index.html">На головну</a></p>'; return; }

  const gallery = getProductGallery(p);
  const title = shortName(p.name);

  document.title = `${title} — OneTech`;
  document.getElementById('productContent').innerHTML = `
    <div class="product-page-grid">
      <div>
        <div class="product-gallery-main"><img id="pgMain" src="${gallery[0]}" alt="${title}"></div>
        <div class="product-gallery-thumbs" id="pgThumbs">${gallery.map((s, i) => `
          <button class="modal-thumb ${i ? '' : 'active'}" type="button"><img src="${s}" alt=""></button>`).join('')}
        </div>
      </div>
      <div class="product-info-panel">
        <div class="product-brand">${BRANDS[p.brand]}</div>
        <h1>${title}</h1>
        <div class="price-row" style="margin-bottom:20px">
          <span class="price-now">${formatPrice(p.price)}</span>
          ${p.oldPrice ? `<span class="price-old">${formatPrice(p.oldPrice)}</span>` : ''}
        </div>
        <ul class="modal-specs">
          <li><span>Потужність</span><span>${p.power} кВт</span></li>
          <li><span>Тип</span><span>Інверторний, повітря–вода</span></li>
          <li><span>Доставка</span><span>Безкоштовна</span></li>
          <li><span>Фото</span><span>${gallery.length} зображень</span></li>
        </ul>
        <button class="btn btn-primary btn-block" id="pgOrder" style="margin-top:20px">Консультація</button>
        <a href="catalog.html" class="card-link" style="display:block;text-align:center;margin-top:14px">← Каталог</a>
      </div>
    </div>`;

  document.getElementById('pgThumbs').querySelectorAll('.modal-thumb').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('pgMain').src = btn.querySelector('img').src;
      document.getElementById('pgThumbs').querySelectorAll('.modal-thumb').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  document.getElementById('pgOrder').addEventListener('click', () => {
    location.href = `contact.html?order=${id}`;
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page || 'home';
  initLayout(page === 'product' ? 'catalog' : page);

  observeReveal();

  if (page === 'home') {
    renderFeatured();
    initHeroSlider();
    bindCards('#featuredGrid');
  }

  if (page === 'catalog') {
    renderCatalog();
    initCatalogNav();
    bindCards('#catalogGrid');
  }

  if (page === 'pick') {
    initPickCalculator();
    calcSavings();
  }

  if (page === 'about') {
    initFAQ();
  }

  if (page === 'contact') {
    initForm();
    const orderParam = new URLSearchParams(location.search).get('order');
    if (orderParam) setTimeout(() => openOrder(+orderParam), 300);
  }

  if (page === 'product') {
    initProductPage();
  }
});
