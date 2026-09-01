const SITE_NAV = [
  { id: 'home', href: 'index.html', label: 'Головна' },
  { id: 'about', href: 'about.html', label: 'Що це таке' },
  { id: 'catalog', href: 'catalog.html', label: 'Каталог' },
  { id: 'pick', href: 'pick.html', label: 'Підбір' },
  { id: 'contact', href: 'contact.html', label: 'Контакт' },
];

function renderSiteHeader(active) {
  const links = SITE_NAV.map(n => `
    <a href="${n.href}" class="${n.id === active ? 'active' : ''}">${n.label}</a>`).join('');

  return `
  <header class="header">
    <div class="container header-inner">
      <a href="index.html" class="logo"><img src="img/logo.png" alt="OneTech"></a>
      <nav class="nav" id="nav">${links}</nav>
      <div class="header-right">
        <a href="tel:0800300144" class="header-phone">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z"/></svg>
          <span>0 800 300 144</span>
        </a>
        <a href="contact.html" class="btn btn-primary btn-sm">Консультація</a>
        <button class="menu-btn" id="menuBtn" aria-label="Меню">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
        </button>
      </div>
    </div>
  </header>`;
}

function renderSiteFooter() {
  return `
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="index.html" class="logo"><img src="img/logo.png" alt="OneTech"></a>
          <p>Інженерні рішення для опалення приватного будинку. Офіційні бренди, підбір потужності, монтаж.</p>
        </div>
        <div>
          <h4>Розділи</h4>
          <ul>
            <li><a href="about.html">Що таке тепловий насос</a></li>
            <li><a href="catalog.html">Каталог моделей</a></li>
            <li><a href="pick.html">Підбір за площею</a></li>
            <li><a href="contact.html">Консультація</a></li>
          </ul>
        </div>
        <div>
          <h4>Контакти</h4>
          <ul>
            <li><a href="tel:0800300144">0 800 300 144</a></li>
            <li><a href="tel:0683949600">068 39 49 600</a></li>
            <li><a href="contact.html">Форма зворотного зв'язку</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">© 2026 OneTech · Теплові насоси для дому</div>
    </div>
  </footer>`;
}

function initLayout(activePage) {
  const headerEl = document.getElementById('site-header');
  const footerEl = document.getElementById('site-footer');
  if (headerEl) headerEl.innerHTML = renderSiteHeader(activePage);
  if (footerEl) footerEl.innerHTML = renderSiteFooter();

  document.getElementById('menuBtn')?.addEventListener('click', () => {
    document.getElementById('nav')?.classList.toggle('open');
  });
}
