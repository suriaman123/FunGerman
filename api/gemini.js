const https = require('https');

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return { statusCode: 500, body: JSON.stringify({ error: 'GEMINI_API_KEY not set' }) };
  }

  let prompt;
  try {
    const body = JSON.parse(event.body);
    prompt = body.prompt;
  } catch {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid request body' }) };
  }

  if (!prompt) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Missing prompt' }) };
  }

  const postData = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 500 }
  });

  return new Promise((resolve) => {
    const options = {
      hostname: 'generativelanguage.googleapis.com',
      path: `/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode !== 200) {
            console.error('Gemini error:', data);
            resolve({
              statusCode: res.statusCode,
              body: JSON.stringify({ error: 'Gemini API error', details: parsed })
            });
            return;
          }
          const text = parsed?.candidates?.[0]?.content?.parts?.[0]?.text || '';
          console.log('Gemini response:', text.substring(0, 200));
          resolve({
            statusCode: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
          });
        } catch (e) {
          resolve({ statusCode: 500, body: JSON.stringify({ error: 'Parse error', raw: data.substring(0, 500) }) });
        }
      });
    });

    req.on('error', (e) => {
      console.error('Request error:', e.message);
      resolve({ statusCode: 500, body: JSON.stringify({ error: e.message }) });
    });

    req.write(postData);
    req.end();
  });
};
