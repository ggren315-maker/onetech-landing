"""
OneTech local server: static files + Telegram lead form API + auto price sync.

Setup:
  1. Create Telegram bot via @BotFather -> copy token
  2. Write to bot any message, then open:
     https://api.telegram.org/bot<TOKEN>/getUpdates
     to find your chat_id
  3. Copy .env.example to .env and fill values
  4. pip install flask python-dotenv requests
  5. python server.py
"""
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
import requests

from catalog_sync import run_price_update

load_dotenv()

ROOT = Path(__file__).parent
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
PRICE_UPDATE_ENABLED = os.getenv('PRICE_UPDATE_ENABLED', '1') != '0'
PRICE_UPDATE_HOURS = float(os.getenv('PRICE_UPDATE_HOURS', '6'))
PRICE_UPDATE_ON_START = os.getenv('PRICE_UPDATE_ON_START', '1') != '0'
SYNC_SECRET = os.getenv('SYNC_SECRET', '')

_price_lock = threading.Lock()
_updater_started = False
_price_status = {
    'at': None,
    'products_total': 0,
    'catalog_total': 0,
    'matched': 0,
    'prices_changed': 0,
    'error': None,
    'running': False,
}

app = Flask(__name__, static_folder=str(ROOT), static_url_path='')


@app.route('/')
def index():
    return send_from_directory(ROOT, 'index.html')


@app.route('/<path:path>')
def static_files(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    full = ROOT / path
    if full.is_file():
        return send_from_directory(ROOT, path)
    return jsonify({'error': 'Not found'}), 404


@app.route('/api/lead', methods=['POST'])
def submit_lead():
    if not BOT_TOKEN or not CHAT_ID:
        return jsonify({
            'ok': False,
            'error': 'Telegram bot not configured. Copy .env.example to .env and set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID'
        }), 503

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    model = (data.get('model') or 'Потрібна консультація').strip()
    message = (data.get('message') or '—').strip()

    if not name or not phone:
        return jsonify({'ok': False, 'error': 'Ім\'я та телефон обов\'язкові'}), 400

    text = (
        f"🔥 <b>Нова заявка OneTech</b>\n\n"
        f"👤 <b>Ім'я:</b> {name}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
        f"📦 <b>Модель:</b> {model}\n"
        f"💬 <b>Коментар:</b> {message}"
    )

    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': CHAT_ID, 'text': text, 'parse_mode': 'HTML'},
            timeout=10,
        )
        body = resp.json()
        if not body.get('ok'):
            return jsonify({'ok': False, 'error': body.get('description', 'Telegram error')}), 502
        return jsonify({'ok': True})
    except requests.RequestException as e:
        return jsonify({'ok': False, 'error': str(e)}), 502


@app.route('/api/health')
def health():
    return jsonify({
        'ok': True,
        'telegram_configured': bool(BOT_TOKEN and CHAT_ID),
        'price_update_enabled': PRICE_UPDATE_ENABLED,
        'price_update_hours': PRICE_UPDATE_HOURS,
    })


@app.route('/api/catalog-status')
def catalog_status():
    with _price_lock:
        return jsonify(dict(_price_status))


@app.route('/api/catalog-sync', methods=['POST'])
def catalog_sync():
    """Manual/cron price sync (optional X-Sync-Key header or ?key=)."""
    if SYNC_SECRET:
        key = request.headers.get('X-Sync-Key') or request.args.get('key', '')
        if key != SYNC_SECRET:
            return jsonify({'ok': False, 'error': 'Forbidden'}), 403

    _do_price_update()
    with _price_lock:
        return jsonify({'ok': True, 'status': dict(_price_status)})


def _do_price_update():
    global _price_status
    with _price_lock:
        if _price_status['running']:
            return
        _price_status['running'] = True

    try:
        result = run_price_update()
        with _price_lock:
            _price_status.update(result)
            _price_status['running'] = False
        if result['prices_changed']:
            print(f"Prices updated: {result['prices_changed']} product(s) changed")
    except Exception as exc:
        with _price_lock:
            _price_status['error'] = str(exc)
            _price_status['running'] = False
        print(f'Price update failed: {exc}')


def _price_update_loop():
    if PRICE_UPDATE_ON_START:
        time.sleep(5)
        _do_price_update()

    interval = max(PRICE_UPDATE_HOURS, 0.5) * 3600
    while True:
        time.sleep(interval)
        _do_price_update()


def start_price_updater():
    global _updater_started
    if _updater_started or not PRICE_UPDATE_ENABLED:
        if not PRICE_UPDATE_ENABLED:
            print('Price auto-update: disabled (PRICE_UPDATE_ENABLED=0)')
        return
    _updater_started = True
    thread = threading.Thread(target=_price_update_loop, daemon=True, name='price-updater')
    thread.start()
    print(f'Price auto-update: every {PRICE_UPDATE_HOURS:g} h from aquafamily.ua')


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5500))
    print(f'OneTech server: http://127.0.0.1:{port}')
    if not BOT_TOKEN or not CHAT_ID:
        print('WARNING: Telegram not configured - copy .env.example to .env')
    start_price_updater()
    app.run(host='0.0.0.0', port=port, debug=False)
