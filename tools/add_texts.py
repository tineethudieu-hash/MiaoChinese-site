# Đọc bài học, tìm mọi câu/từ có thể được phát âm, thêm vào audio/manifest.json (nếu chưa có).
# Dùng: python3 tools/add_texts.py lessons/bai17.html
import re, json, sys, hashlib, subprocess
lesson = sys.argv[1]
s = open(lesson, encoding='utf8').read()
def clean(t): return re.sub(r'[.,，。！？!?]', '', re.sub(r'[（(].*?[）)]', '', str(t))).strip()
def grab(name):
    m = re.search(r'(?:const|var) '+name+r' = (\{.*?\}|\[.*?\]);\s*\n', s, re.S)
    return json.loads(m.group(1)) if m else None
texts = []
words = grab('WORDS') or []
texts += [w['cn'] for w in words]
for it in grab('SENTENCE_BUILDER') or []: texts.append(it.get('say') or it['answer'])
for it in grab('FILL_BLANK') or []: texts.append(it.get('say') or (it['before'] + it['options'][it['a']] + it['after']))
texts += grab('AUDIO_EXTRA') or []
cfg = grab('CFG')  # có thể bắt nhầm CFG của tracker; lấy cái có 'word'
for m in re.finditer(r'var CFG = (\{"word".*?\});\n', s, re.S):
    c = json.loads(m.group(1))
    texts += [x['cn'] for x in c['word']] + [x['cn'] for x in c['sent']] + [x['cn'] for x in c['free']]
for m in re.finditer(r'cn:`([^`]+)`', s): texts.append(m.group(1))
M = json.load(open('audio/manifest.json', encoding='utf8'))
try: P = json.load(open('tools/punct.json', encoding='utf8'))
except Exception: P = {}
new = 0
for t in texts:
    for part in t.split('/') if False else [t]:
        k = clean(part.replace('/', ''))
        if not k: continue
        if k not in M:
            M[k] = hashlib.sha1(k.encode()).hexdigest()[:10] + '.mp3'; new += 1
        if part != k and re.search(r'[，。！？]', part): P[k] = part.replace('/', '，')
json.dump(M, open('audio/manifest.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
json.dump(P, open('tools/punct.json', 'w', encoding='utf8'), ensure_ascii=False, indent=0)
print('texts', len(texts), 'new', new, 'total', len(M))
