const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT_ID = process.env.TELEGRAM_CHAT_ID;

const headers = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ ok: false, error: 'Method not allowed' }) };
  }

  if (!BOT_TOKEN || !CHAT_ID) {
    return {
      statusCode: 503,
      headers,
      body: JSON.stringify({ ok: false, error: 'Telegram not configured on host' }),
    };
  }

  let data = {};
  try {
    data = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers, body: JSON.stringify({ ok: false, error: 'Invalid JSON' }) };
  }

  const name = (data.name || '').trim();
  const phone = (data.phone || '').trim();
  const model = (data.model || 'Потрібна консультація').trim();
  const message = (data.message || '—').trim();

  if (!name || !phone) {
    return { statusCode: 400, headers, body: JSON.stringify({ ok: false, error: "Ім'я та телефон обов'язкові" }) };
  }

  const text = [
    '🔥 <b>Нова заявка OneTech</b>',
    '',
    `👤 <b>Ім'я:</b> ${name}`,
    `📞 <b>Телефон:</b> ${phone}`,
    `📦 <b>Модель:</b> ${model}`,
    `💬 <b>Коментар:</b> ${message}`,
  ].join('\n');

  const resp = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
  });

  const body = await resp.json();
  if (!body.ok) {
    return {
      statusCode: 502,
      headers,
      body: JSON.stringify({ ok: false, error: body.description || 'Telegram error' }),
    };
  }

  return { statusCode: 200, headers, body: JSON.stringify({ ok: true }) };
};
