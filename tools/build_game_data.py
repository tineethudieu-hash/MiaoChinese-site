#!/usr/bin/env python3
"""Tạo games/words.js từ các bài ôn trong lessons/ (chạy lại mỗi khi thêm bài mới):
   python3 tools/build_game_data.py"""
import re, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'^const LEVELS = (\[.*\]);\s*$', idx, flags=re.M)
levels = json.loads(m.group(1))
titles = {}
for lv in levels:
    for l in lv['lessons']:
        if l.get('url'): titles[l['num']] = (l['title'], l['url'])
out = []
for num in sorted(titles):
    title, url = titles[num]
    p = os.path.join(ROOT, url)
    if not os.path.exists(p): continue
    s = open(p, encoding='utf-8').read()
    mm = re.search(r'^const WORDS = (\[.*\]);\s*$', s, flags=re.M)
    if not mm: continue
    words = []
    for w in json.loads(mm.group(1)):
        d = {'cn': w['cn'], 'py': w['py'], 'vi': w['vi']}
        if w.get('img'): d['img'] = w['img']
        words.append(d)
    out.append({'num': num, 'title': title, 'words': words})
js = '/* Tự tạo bởi tools/build_game_data.py — đừng sửa tay */\nwindow.GAME_LESSONS = ' + json.dumps(out, ensure_ascii=False) + ';\n'
open(os.path.join(ROOT, 'games', 'words.js'), 'w', encoding='utf-8').write(js)
print({o['num']: (len(o['words']), sum(1 for w in o['words'] if 'img' in w)) for o in out})
