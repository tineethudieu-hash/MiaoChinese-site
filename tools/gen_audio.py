# Tạo lại toàn bộ audio bằng giọng Microsoft Edge Neural (miễn phí). Chạy bởi GitHub Actions.
import asyncio, json, os, subprocess, sys, tempfile
import edge_tts
VOICE = os.environ.get('VOICE', 'zh-CN-XiaoxiaoNeural')
RATE = os.environ.get('RATE', '-15%')
M = json.load(open('audio/manifest.json', encoding='utf8'))
# Bảng sửa đọc: chữ hiển thị -> chữ đồng âm để đọc đúng
FIX = json.load(open('tools/doc_dung.json', encoding='utf8')) if os.path.exists('tools/doc_dung.json') else {}
def prep(t):
    for k, v in FIX.items(): t = t.replace(k, v)
    return t.replace('/', '，')
async def one(sem, text, fn):
    async with sem:
        for attempt in range(4):
            try:
                tmp = tempfile.mktemp(suffix='.mp3')
                await edge_tts.Communicate(prep(text), VOICE, rate=RATE).save(tmp)
                out = 'audio/' + fn
                subprocess.run(['ffmpeg','-loglevel','error','-y','-i',tmp,'-af',
                  'loudnorm=I=-23:TP=-2:LRA=11,adelay=250|250,apad=pad_dur=0.45',
                  '-ar','24000','-ac','1','-codec:a','libmp3lame','-b:a','48k',out], check=True)
                os.remove(tmp); return True
            except Exception as e:
                print('retry', fn, text, e, file=sys.stderr); await asyncio.sleep(2 + attempt * 3)
        return False
async def main():
    sem = asyncio.Semaphore(4)
    res = await asyncio.gather(*[one(sem, t, f) for t, f in M.items()])
    bad = [t for (t, f), ok in zip(M.items(), res) if not ok]
    print('ok', len(res) - len(bad), 'fail', len(bad), bad)
    if len(bad) > len(res) * 0.2: sys.exit(1)
asyncio.run(main())
