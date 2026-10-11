// Vercel serverless: tạo giọng đọc tiếng Trung, chỉ cho các câu/từ có trong bài (allowlist).
// Kết quả được Vercel CDN lưu 1 năm nên mỗi câu chỉ tạo 1 lần.
// Nhà cung cấp (ưu tiên từ trên xuống):
//   1) Azure Speech  — cần AZURE_SPEECH_KEY + AZURE_SPEECH_REGION (tuỳ chọn AZURE_VOICE, mặc định zh-CN-XiaoxiaoNeural)
//   2) ElevenLabs    — cần ELEVENLABS_API_KEY + ELEVENLABS_VOICE_ID
const ALLOW = new Set(require('./_allow.json'));
const clean = s => String(s || '').replace(/[（(].*?[）)]/g, '').replace(/[.,，。！？!?]/g, '').trim();
const xml = s => s.replace(/[<>&"']/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;', "'": '&apos;' }[c]));

async function azure(t, env) {
  const voice = env.AZURE_VOICE || 'zh-CN-XiaoxiaoNeural';
  const rate = env.AZURE_RATE || '-12%';
  const ssml = `<speak version="1.0" xml:lang="zh-CN" xmlns="http://www.w3.org/2001/10/synthesis"><voice name="${xml(voice)}"><prosody rate="${xml(rate)}">${xml(t)}</prosody></voice></speak>`;
  return fetch(`https://${encodeURIComponent(env.AZURE_SPEECH_REGION)}.tts.speech.microsoft.com/cognitiveservices/v1`, {
    method: 'POST',
    headers: {
      'Ocp-Apim-Subscription-Key': env.AZURE_SPEECH_KEY,
      'Content-Type': 'application/ssml+xml',
      'X-Microsoft-OutputFormat': 'audio-24khz-48kbitrate-mono-mp3',
      'User-Agent': 'miaochinese'
    },
    body: ssml
  });
}
async function eleven(t, env) {
  return fetch(`https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(env.ELEVENLABS_VOICE_ID)}?output_format=mp3_44100_64`, {
    method: 'POST',
    headers: { 'xi-api-key': env.ELEVENLABS_API_KEY, 'Content-Type': 'application/json', Accept: 'audio/mpeg' },
    body: JSON.stringify({ text: t, model_id: 'eleven_multilingual_v2', language_code: 'zh', voice_settings: { stability: 0.6, similarity_boost: 0.8, speed: 0.9 } })
  });
}

module.exports = async (req, res) => {
  const env = process.env;
  const t = clean(req.query && req.query.t);
  if (!t || t.length > 60 || !ALLOW.has(t)) { res.statusCode = 400; return res.end('bad text'); }
  const useAzure = env.AZURE_SPEECH_KEY && env.AZURE_SPEECH_REGION;
  const useEleven = env.ELEVENLABS_API_KEY && env.ELEVENLABS_VOICE_ID;
  if (!useAzure && !useEleven) { res.statusCode = 503; return res.end('tts not configured'); }
  try {
    const r = useAzure ? await azure(t, env) : await eleven(t, env);
    if (!r.ok) { res.statusCode = 502; return res.end((useAzure ? 'azure ' : 'elevenlabs ') + r.status); }
    const buf = Buffer.from(await r.arrayBuffer());
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'public, max-age=31536000, s-maxage=31536000, immutable');
    res.statusCode = 200;
    return res.end(buf);
  } catch (e) { res.statusCode = 502; return res.end('error'); }
};
