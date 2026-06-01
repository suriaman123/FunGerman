export async function onRequestPost(context) {
  const apiKey = context.env.GEMINI_API_KEY;

  if (!apiKey) {
    return new Response(JSON.stringify({ error: 'NO_API_KEY', message: 'GEMINI_API_KEY not set in environment' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  }

  let prompt;
  try {
    const body = await context.request.json();
    prompt = body.prompt;
  } catch(e) {
    return new Response(JSON.stringify({ error: 'BAD_BODY', message: e.message }), {
      status: 400, headers: { 'Content-Type': 'application/json' }
    });
  }

  const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;

  let geminiRes, data;
  try {
    geminiRes = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: { temperature: 0.7, maxOutputTokens: 500 }
      })
    });
    data = await geminiRes.json();
  } catch(e) {
    return new Response(JSON.stringify({ error: 'FETCH_FAILED', message: e.message }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  }

  // Always return full Gemini response so we can debug
  if (!geminiRes.ok) {
    return new Response(JSON.stringify({
      error: 'GEMINI_ERROR',
      status: geminiRes.status,
      full_response: data
    }), { status: 500, headers: { 'Content-Type': 'application/json' } });
  }

  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
  return new Response(JSON.stringify({ text }), {
    status: 200, headers: { 'Content-Type': 'application/json' }
  });
}

export async function onRequestGet(context) {
  const apiKey = context.env.GEMINI_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ status: 'FAIL', reason: 'GEMINI_API_KEY not found in env' }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: 'Reply with exactly this JSON: {"word":"Hund"}' }] }],
        generationConfig: { maxOutputTokens: 50 }
      })
    });
    const data = await res.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    return new Response(JSON.stringify({
      status: res.ok ? 'OK' : 'FAIL',
      http_status: res.status,
      gemini_text: text,
      full_response: data,
      key_starts_with: apiKey.substring(0, 10)
    }), { headers: { 'Content-Type': 'application/json' } });
  } catch(e) {
    return new Response(JSON.stringify({ status: 'FAIL', error: e.message }), {
      status: 500, headers: { 'Content-Type': 'application/json' }
    });
  }
}
