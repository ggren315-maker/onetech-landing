# OneTech — теплові насоси для дому

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://dashboard.render.com/blueprint/new?repo=https://github.com/ggren315-maker/onetech-landing)

## Сайт онлайн

| Де | URL | Що працює |
|----|-----|-----------|
| **GitHub Pages** | https://ggren315-maker.github.io/onetech-landing/ | Сторінки, каталог, калькулятор |
| **Render** (рекомендовано) | https://onetech-4yk7.onrender.com/ | + форма → Telegram, оновлення цін |

> GitHub показує **код** і **статичний сайт**. Посилання `github.com/...` — це репозиторій, не сайт для клієнтів.

## Сторінки

- `index.html` — головна
- `about.html` — що таке тепловий насос
- `catalog.html` — каталог
- `pick.html` — підбір за площею
- `contact.html` — консультація / форма
- `product.html?id=N` — картка товару

## GitHub Pages (автоматично)

Після push у `main` сайт з'являється на:
**https://ggren315-maker.github.io/onetech-landing/**

У репозиторії: **Settings → Pages → Source: GitHub Actions**

## Render (бот Telegram)

1. [Deploy Blueprint](https://dashboard.render.com/blueprint/new?repo=https://github.com/ggren315-maker/onetech-landing)
2. Environment: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Локально

```bash
pip install -r requirements.txt
python server.py
```

→ http://127.0.0.1:5500
