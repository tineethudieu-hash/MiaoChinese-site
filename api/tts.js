// Vercel Serverless Function: giọng đọc ElevenLabs theo yêu cầu, được CDN lưu lại.
// GET /api/tts?f=<tên-file>.mp3  (tên file lấy từ audio/manifest.json)
// Cần biến môi trường (đã có trên Vercel): ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
const MANIFEST = require('../audio/manifest.json');
let PUNCT = {};
try { PUNCT = require('../tools/punct.json'); } catch (e) {}

const BY_FILE = {};
for (const text of Object.keys(MANIFEST)) BY_FILE[MANIFEST[text]] = text;

module.exports = async (req, res) => {
  try {
    const f = String((req.query && req.query.f) || '');
    const key = process.env.ELEVENLABS_API_KEY, voice = process.env.ELEVENLABS_VOICE_ID;
    if (!/^[0-9a-f]{10}\.mp3$/.test(f) || !BY_FILE[f]) { res.status(404).send('not found'); return; }
    if (!key || !voice) { res.status(500).send('missing env'); return; }
    const key0 = BY_FILE[f];
    const text = (PUNCT[key0] || key0).replace(/\//g, '，');
    const speed = text.length >= 6 ? 0.75 : 0.85;
    const r = await fetch('https://api.elevenlabs.io/v1/text-to-speech/' + encodeURIComponent(voice) + '?output_format=mp3_44100_64', {
      method: 'POST',
      headers: { 'xi-api-key': key, 'Content-Type': 'application/json', 'Accept': 'audio/mpeg' },
      body: JSON.stringify({ text, model_id: 'eleven_multilingual_v2',
        voice_settings: { stability: 0.6, similarity_boost: 0.8, speed } })
    });
    if (!r.ok) { res.status(502).send('tts error ' + r.status); return; }
    const buf = Buffer.from(await r.arrayBuffer());
    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'public, max-age=31536000, s-maxage=31536000, immutable');
    res.status(200).send(buf);
  } catch (e) {
    res.status(502).send('error');
  }
};
