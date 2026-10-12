// Tạo giọng ElevenLabs cho các âm chưa có và LƯU VĨNH VIỄN vào GitHub (audio/*.mp3), mỗi lượt một commit.
// POST /api/warm?pin=XXXX            -> xử lý một lượt (tối đa BATCH file) rồi trả về số file còn lại
// POST /api/warm?pin=XXXX&reset=1    -> bỏ qua danh sách đã làm, tạo lại tất cả (khi đổi giọng)
// Biến môi trường: ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, GITHUB_TOKEN, (tuỳ chọn) WARM_PIN, GITHUB_REPO
const MANIFEST = require('../audio/manifest.json');
let PUNCT = {};
try { PUNCT = require('../tools/punct.json'); } catch (e) {}

const REPO = process.env.GITHUB_REPO || 'tineethudieu-hash/MiaoChinese-site';
const BRANCH = 'main';
const BATCH = 36, CONC = 3;
const GH = 'https://api.github.com/repos/' + REPO;

function gh(path, opt) {
  return fetch(GH + path, Object.assign({ headers: { Authorization: 'Bearer ' + process.env.GITHUB_TOKEN, Accept: 'application/vnd.github+json', 'User-Agent': 'miaochinese-warm', 'Content-Type': 'application/json' } }, opt || {}));
}
async function ghJson(path, opt) {
  const r = await gh(path, opt);
  const t = await r.text();
  if (!r.ok) throw new Error('GitHub ' + r.status + ' ' + t.slice(0, 200));
  return t ? JSON.parse(t) : {};
}
function clean(v, strip) { v = String(v || '').trim().replace(/^["']|["']$/g, ''); return v; }

async function tts(text, voice, key) {
  const speed = text.length >= 6 ? 0.75 : 0.85;
  for (let k = 0; k < 3; k++) {
    const r = await fetch('https://api.elevenlabs.io/v1/text-to-speech/' + encodeURIComponent(voice) + '?output_format=mp3_44100_64', {
      method: 'POST', headers: { 'xi-api-key': key, 'Content-Type': 'application/json', Accept: 'audio/mpeg' },
      body: JSON.stringify({ text, model_id: 'eleven_multilingual_v2', voice_settings: { stability: 0.6, similarity_boost: 0.8, speed } })
    });
    if (r.ok) return Buffer.from(await r.arrayBuffer());
    const body = (await r.text()).slice(0, 300);
    if ([401, 402, 403, 404].includes(r.status)) { const e = new Error('ElevenLabs ' + r.status + ' ' + body); e.fatal = true; throw e; }
    await new Promise(s => setTimeout(s, 1500 * (k + 1)));
  }
  throw new Error('ElevenLabs lỗi tạm thời');
}

module.exports = async (req, res) => {
  const send = (code, obj) => { res.status(code).setHeader('Content-Type', 'application/json; charset=utf-8'); res.send(JSON.stringify(obj)); };
  try {
    const q = req.query || {};
    if (String(q.pin || '') !== String(process.env.WARM_PIN || '0108')) return send(403, { error: 'Sai PIN' });
    const key = clean(process.env.ELEVENLABS_API_KEY);
    let voice = clean(process.env.ELEVENLABS_VOICE_ID); if (voice.indexOf('/') >= 0) voice = voice.split('/').filter(Boolean).pop();
    if (!key || !voice) return send(500, { error: 'Thiếu ELEVENLABS_API_KEY hoặc ELEVENLABS_VOICE_ID trên Vercel' });
    if (!process.env.GITHUB_TOKEN) return send(500, { error: 'Thiếu GITHUB_TOKEN trên Vercel' });

    // danh sách đã làm (đọc trực tiếp từ GitHub để luôn mới)
    let done = new Set();
    if (!q.reset) {
      const r = await gh('/contents/audio/_eleven.json?ref=' + BRANCH);
      if (r.ok) { const j = await r.json(); try { done = new Set(JSON.parse(Buffer.from(j.content, 'base64').toString('utf8'))); } catch (e) {} }
    }
    const todo = Object.keys(MANIFEST).filter(t => !done.has(MANIFEST[t]));
    if (!todo.length) return send(200, { done: done.size, total: Object.keys(MANIFEST).length, remaining: 0, message: 'Đã xong hết' });
    const batch = todo.slice(0, BATCH);

    // tạo âm (3 file song song)
    const out = [];
    let i = 0;
    await Promise.all(Array.from({ length: CONC }, async () => {
      while (i < batch.length) {
        const t = batch[i++];
        const text = (PUNCT[t] || t).replace(/\//g, '，');
        out.push({ t, f: MANIFEST[t], buf: await tts(text, voice, key) });
      }
    }));

    // một commit cho cả lượt
    const ref = await ghJson('/git/ref/heads/' + BRANCH);
    const baseCommit = await ghJson('/git/commits/' + ref.object.sha);
    const blobs = await Promise.all(out.map(o => ghJson('/git/blobs', { method: 'POST', body: JSON.stringify({ content: o.buf.toString('base64'), encoding: 'base64' }) })));
    const newDone = new Set([...done, ...out.map(o => o.f)]);
    const listBlob = await ghJson('/git/blobs', { method: 'POST', body: JSON.stringify({ content: JSON.stringify(Array.from(newDone).sort()), encoding: 'utf-8' }) });
    const tree = await ghJson('/git/trees', { method: 'POST', body: JSON.stringify({ base_tree: baseCommit.tree.sha,
      tree: out.map((o, k) => ({ path: 'audio/' + o.f, mode: '100644', type: 'blob', sha: blobs[k].sha })).concat([{ path: 'audio/_eleven.json', mode: '100644', type: 'blob', sha: listBlob.sha }]) }) });
    const commit = await ghJson('/git/commits', { method: 'POST', body: JSON.stringify({ message: 'Giọng ElevenLabs: ' + out.length + ' file', tree: tree.sha, parents: [ref.object.sha] }) });
    await ghJson('/git/refs/heads/' + BRANCH, { method: 'PATCH', body: JSON.stringify({ sha: commit.sha }) });

    send(200, { done: newDone.size, total: Object.keys(MANIFEST).length, remaining: todo.length - out.length, added: out.length });
  } catch (e) {
    send(e.fatal ? 402 : 500, { error: String(e.message || e) });
  }
};
