export async function onRequestPost(context) {
  const apiKey = context.env.GEMINI_API_KEY;
  if (!apiKey) return response({ error: 'NO_API_KEY' }, 500);

  let prompt;
  try { prompt = (await context.request.json()).prompt; }
  catch { return response({ error: 'BAD_BODY' }, 400); }

  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: 500 }
      })
    });
    const data = await res.json();
    if (!res.ok) return response({ error: 'GEMINI_ERROR', detail: data?.error?.message }, 500);
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    return response({ text });
  } catch(e) {
    return response({ error: e.message }, 500);
  }
}

function response(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status, headers: { 'Content-Type': 'application/json' }
  });
}
