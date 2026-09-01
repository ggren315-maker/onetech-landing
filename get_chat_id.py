"""Run after sending any message to your Telegram bot (@blablablaLID_bot)."""
import os
import re
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
if not token:
    print('TELEGRAM_BOT_TOKEN not set in .env')
    exit(1)

url = f'https://api.telegram.org/bot{token}/getUpdates'
data = json.loads(urllib.request.urlopen(url).read().decode())

if not data.get('result'):
    print('No messages yet.')
    print('1. Open @blablablaLID_bot in Telegram')
    print('2. Send /start or any message')
    print('3. Run: python get_chat_id.py')
    exit(0)

chat_id = None
for upd in reversed(data['result']):
    chat = upd.get('message', {}).get('chat') or upd.get('callback_query', {}).get('message', {}).get('chat')
    if chat:
        chat_id = str(chat['id'])
        name = chat.get('first_name', '')
        username = chat.get('username', '')
        print(f'Found: CHAT_ID={chat_id} ({name} @{username})')
        break

if not chat_id:
    exit(1)

env_path = '.env'
with open(env_path, encoding='utf-8') as f:
    content = f.read()

if re.search(r'^TELEGRAM_CHAT_ID=.*$', content, re.M):
    content = re.sub(r'^TELEGRAM_CHAT_ID=.*$', f'TELEGRAM_CHAT_ID={chat_id}', content, flags=re.M)
else:
    content += f'\nTELEGRAM_CHAT_ID={chat_id}\n'

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Updated .env with TELEGRAM_CHAT_ID={chat_id}')
print('Restart server: python server.py')
