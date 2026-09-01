# Деплой OneTech на безкоштовний хостинг (Render)

Сайт + Telegram-бот працюють **без вашого ПК**, якщо проєкт задеплоєно на сервер у хмарі.

**Render Free** — безкоштовно, публічна URL, підтримує Python/Flask.

> На безкоштовному тарифі сервер «засинає» після ~15 хв без відвідувачів.  
> Перший запит після сну — 30–60 сек (cold start).  
> Рішення: безкоштовний **UptimeRobot** (крок 6) — сервер майже завжди онлайн.

---

## Крок 1. GitHub — завантажити код

1. Створіть акаунт на [github.com](https://github.com) (якщо немає).
2. **New repository** → назва `onetech-landing` → Public → Create.
3. У папці проєкту виконайте (PowerShell):

```powershell
cd "C:\Users\Utkin\Desktop\Новая папка"
git init -b main
git add -A
git commit -m "OneTech landing: deploy ready"
git remote add origin https://github.com/ВАШ_ЛОГІН/onetech-landing.git
git push -u origin main
```

Замініть `ВАШ_ЛОГІН` на свій GitHub-логін.

---

## Крок 2. Telegram — chat_id (якщо ще не налаштовано)

1. Напишіть боту `@blablablaLID_bot` будь-яке повідомлення (наприклад `/start`).
2. Локально:

```powershell
python get_chat_id.py
```

3. Скопіюйте `TELEGRAM_CHAT_ID` — знадобиться на Render.

---

## Крок 3. Render — створити сервер

1. Зареєструйтесь на [render.com](https://render.com) (можна через GitHub).
2. **Dashboard → New + → Blueprint**.
3. Підключіть репозиторій `onetech-landing`.
4. Render прочитає `render.yaml` і створить Web Service.

---

## Крок 4. Змінні середовища на Render

**Dashboard → ваш сервіс onetech → Environment:**

| Змінна | Значення |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | токен від @BotFather |
| `TELEGRAM_CHAT_ID` | число з `get_chat_id.py` |
| `SYNC_SECRET` | згенеровано автоматично (не змінюйте) |

Натисніть **Save Changes** → сервер перезапуститься.

---

## Крок 5. Перевірка

Ваша URL виглядає так: `https://onetech-xxxx.onrender.com`

1. Відкрийте сайт у браузері.
2. Перевірте API: `https://onetech-xxxx.onrender.com/api/health`  
   → `"telegram_configured": true`
3. Заповніть форму на сайті → заявка має прийти в Telegram.

---

## Крок 6. UptimeRobot — щоб сервер не засинав (рекомендовано)

1. [uptimerobot.com](https://uptimerobot.com) → безкоштовний акаунт.
2. **Add New Monitor**:
   - Type: **HTTP(s)**
   - URL: `https://onetech-xxxx.onrender.com/api/health`
   - Interval: **5 minutes**
3. Збережіть.

Сервер буде «прокинатися» кожні 5 хв і форма працюватиме миттєво.

---

## Крок 7 (опційно). Cron для оновлення цін

На [cron-job.org](https://cron-job.org) (безкоштовно):

- URL: `https://onetech-xxxx.onrender.com/api/catalog-sync?key=ВАШ_SYNC_SECRET`
- Method: **POST**
- Розклад: раз на 6 годин

`SYNC_SECRET` — з Render → Environment.

---

## Оновлення сайту після змін

```powershell
git add -A
git commit -m "Update site"
git push
```

Render задеплоїть нову версію автоматично (~2–3 хв).

---

## Локальний запуск (для розробки)

```powershell
pip install -r requirements.txt
python server.py
```

→ `http://127.0.0.1:5500`

---

## Інші безкоштовні хостинги

| Хостинг | Плюси | Мінуси |
|---------|-------|--------|
| **Render** | Простий деплой з GitHub | Засинає без UptimeRobot |
| **Railway** | Швидкий | Потрібна картка, ліміт $5/міс |
| **Fly.io** | Стабільніший | Складніший setup |

Для тесту рекомендуємо **Render + UptimeRobot**.
