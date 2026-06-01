// Test endpoint — visit /api/test in browser to diagnose
// DELETE THIS FILE after everything is working

export async function onRequestGet(context) {
  const apiKey = context.env.GEMINI_API_KEY;

  // Step 1: check if key exists
  if (!apiKey) {
    return json({ 
      status: 'FAIL', 
      problem: 'GEMINI_API_KEY environment variable is not set in Cloudflare Pages settings'
    });
  }

  // Step 2: try calling Gemini with a simple prompt
  try {
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
    const res = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: 'Say the word "hello" in JSON like this: {"word":"hello"}' }] }],
        generationConfig: { maxOutputTokens: 100 }
      })
    });

    const data = await res.json();

    if (!res.ok) {
      return json({
        status: 'FAIL',
        problem: 'Gemini API rejected the request',
        gemini_error: data?.error?.message || JSON.stringify(data),
        key_preview: apiKey.substring(0, 8) + '...' + apiKey.slice(-4)
      });
    }

    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    return json({
      status: 'OK',
      message: 'Everything is working!',
      gemini_response: text,
      key_preview: apiKey.substring(0, 8) + '...' + apiKey.slice(-4)
    });

  } catch (err) {
    return json({ status: 'FAIL', problem: 'Network error', error: err.message });
  }
}

function json(data) {
  return new Response(JSON.stringify(data, null, 2), {
    headers: { 'Content-Type': 'application/json' }
  });
}
