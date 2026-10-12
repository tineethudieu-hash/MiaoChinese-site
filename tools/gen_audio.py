# Tạo lại toàn bộ audio bằng giọng Microsoft Edge Neural (miễn phí). Chạy bởi GitHub Actions.
import asyncio, json, os, subprocess, sys, tempfile
import edge_tts
try:
    from gtts import gTTS
except Exception:
    gTTS = None
FBF = 'audio/_fallback.json'
FALLBACK = set(json.load(open(FBF, encoding='utf8'))) if os.path.exists(FBF) else set()
STATE = {'streak': 0, 'dead': False}
VOICE = os.environ.get('VOICE', 'zh-CN-YunxiNeural')
RATE = os.environ.get('RATE', '-15%')
M = json.load(open('audio/manifest.json', encoding='utf8'))
# Bảng sửa đọc: chữ hiển thị -> chữ đồng âm để đọc đúng
FIX = json.load(open('tools/doc_dung.json', encoding='utf8')) if os.path.exists('tools/doc_dung.json') else {}
PUNCT = json.load(open('tools/punct.json', encoding='utf8')) if os.path.exists('tools/punct.json') else {}
def prep(t):
    t = PUNCT.get(t, t)
    for k, v in FIX.items(): t = t.replace(k, v)
    return t.replace('/', '，')
def rate_for(t):
    # câu (>=6 chữ, không phải danh sách '/') đọc chậm thêm 20%: 0.85*0.8=0.68 -> -32%
    return os.environ.get('RATE_SENT','-32%') if len(t)>=6 and '/' not in t else RATE
def norm(tmp, fn):
    out = 'audio/' + fn
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af',
      'loudnorm=I=-23:TP=-2:LRA=11,adelay=250|250,apad=pad_dur=0.45',
      '-ar','24000','-ac','1','-codec:a','libmp3lame','-b:a','48k',out], check=True)
    os.remove(tmp)
def gtts_make(text, fn):
    tmp = tempfile.mktemp(suffix='.mp3')
    gTTS(prep(text), lang='zh-CN', slow=len(text) >= 1).save(tmp)
    norm(tmp, fn)
async def one(sem, text, fn):
    async with sem:
        have = os.path.exists('audio/' + fn)
        if have and not os.environ.get('FORCE') and fn not in FALLBACK:
            return True
        if not STATE['dead']:
            for attempt in range(3 if STATE['streak'] else 6):
                if STATE['dead']: break
                try:
                    tmp = tempfile.mktemp(suffix='.mp3')
                    await asyncio.wait_for(edge_tts.Communicate(prep(text), VOICE, rate=rate_for(text)).save(tmp), 30)
                    norm(tmp, fn); STATE['streak'] = 0; FALLBACK.discard(fn)
                    print('done', fn, flush=True); return True
                except Exception as e:
                    STATE['streak'] += 1
                    if STATE['streak'] >= 8 and not STATE['dead']:
                        STATE['dead'] = True; print('EDGE BI CHAN -> dung gTTS', flush=True)
                    await asyncio.sleep(3)
        if have: return True      # Edge hỏng nhưng đã có file cũ -> giữ nguyên
        if gTTS:
            try:
                await asyncio.get_event_loop().run_in_executor(None, gtts_make, text, fn)
                FALLBACK.add(fn); print('gtts', fn, flush=True); return True
            except Exception as e:
                print('gtts fail', fn, repr(e)[:80], flush=True)
        return False
async def main():
    sem = asyncio.Semaphore(3)
    res = await asyncio.gather(*[one(sem, t, f) for t, f in M.items()])
    bad = [t for (t, f), ok in zip(M.items(), res) if not ok]
    json.dump(sorted(FALLBACK), open(FBF, 'w', encoding='utf8'))
    print('ok', len(res) - len(bad), 'fail', len(bad), bad)
    if len(bad) > len(res) * 0.2: sys.exit(1)
asyncio.run(main())
