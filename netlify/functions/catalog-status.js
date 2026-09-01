exports.handler = async () => ({
  statusCode: 200,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    at: new Date().toISOString(),
    platform: 'netlify',
    note: 'Price sync runs on Render/Koyeb Python server only',
  }),
});
