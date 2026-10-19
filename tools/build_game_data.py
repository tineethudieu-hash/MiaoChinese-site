#!/usr/bin/env python3
"""Tạo games/words.js từ các bài ôn trong lessons/ (chạy lại mỗi khi thêm bài mới):
   python3 tools/build_game_data.py"""
import re, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
idx = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'^const LEVELS = (\[.*\]);\s*$', idx, flags=re.M)
levels = json.loads(m.group(1))
out = []   # danh sách phẳng các bài có dữ liệu
lvs = []   # theo cấp độ (kể cả cấp chưa có bài)
for lv in levels:
    lessons = []
    for l in lv['lessons']:
        if not l.get('url'): continue
        p = os.path.join(ROOT, l['url'])
        if not os.path.exists(p): continue
        s = open(p, encoding='utf-8').read()
        mm = re.search(r'^const WORDS = (\[.*\]);\s*$', s, flags=re.M)
        if not mm: continue
        words = []
        for w in json.loads(mm.group(1)):
            d = {'cn': w['cn'], 'py': w['py'], 'vi': w['vi']}
            if w.get('img'): d['img'] = w['img']
            words.append(d)
        item = {'num': l['num'], 'title': l['title'], 'level': lv['id'], 'words': words}
        lessons.append(item); out.append(item)
    lvs.append({'id': lv['id'], 'name': lv['name'], 'subtitle': lv.get('subtitle',''), 'range': lv.get('range',''), 'lessons': [{'num': x['num'], 'title': x['title']} for x in lessons]})
js = ('/* Tự tạo bởi tools/build_game_data.py — đừng sửa tay */\nwindow.GAME_LESSONS = ' + json.dumps(out, ensure_ascii=False)
      + ';\nwindow.GAME_LEVELS = ' + json.dumps(lvs, ensure_ascii=False) + ';\n')
open(os.path.join(ROOT, 'games', 'words.js'), 'w', encoding='utf-8').write(js)
print({o['num']: (len(o['words']), sum(1 for w in o['words'] if 'img' in w)) for o in out})
