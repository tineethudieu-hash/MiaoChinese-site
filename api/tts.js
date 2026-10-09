// Vercel serverless: tạo giọng đọc tiếng Trung bằng ElevenLabs, chỉ cho các câu/từ có trong bài (allowlist),
// kết quả được Vercel CDN lưu 1 năm nên mỗi câu chỉ tốn credit 1 lần.
const ALLOW = new Set(require('./_allow.json'));
const clean = s => String(s || '').replace(/[（(].*?[）)]/g, '').replace(/[.,，。！？!?]/g, '').trim();

module.exports = async (req, res) => {
  const key = process.env.ELEVENLABS_API_KEY;
  const voice = process.env.ELEVENLABS_VOICE_ID;
  const t = clean(req.query && req.query.t);
  if (!t || t.length > 60 || !ALLOW.has(t)) { res.statusCode = 400; return res.end('bad text'); }
  if (!key || !voice) { res.statusCode = 503; return res.end('tts not configured'); }
  try {
    const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(voice)}?output_format=mp3_44100_64`, {
      method: 'POST',
      headers: { 'xi-api-key': key, 'Content-Type': 'application/json', Accept: 'audio/mpeg' },
      body: JSON.stringify({ text: t, model_id: 'eleven_multilingual_v2', language_code: 'zh', voice_settings: { stability: 0.6, similarity_boost: 0.8, speed: 0.9 } })
    });
    if (!r.ok) { res.statusCode = 502; return res.end('upstream ' + r.status); }
    const buf = Buffer.from(await r.arrayBuffer());
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'public, max-age=31536000, s-maxage=31536000, immutable');
    res.statusCode = 200;
    return res.end(buf);
  } catch (e) { res.statusCode = 502; return res.end('error'); }
};
