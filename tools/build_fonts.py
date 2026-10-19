#!/usr/bin/env python3
"""Tạo font tự lưu trữ trong assets/fonts/ (chạy lại khi cần):
   - Nunito, Baloo 2 (latin + tiếng Việt, có đủ dấu thanh pinyin)
   - Noto Serif SC chia nhiều mảnh (unicode-range) -> trình duyệt chỉ tải mảnh có chữ Hán đang dùng
Nguồn font: github.com/google/fonts (OFL). Cần: fonttools. Đặt đường dẫn nguồn qua biến FONTS_SRC."""
import os, re, glob, sys
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.varLib import instancer

SRC = os.environ.get('FONTS_SRC', '/home/claude/google/fonts/ofl')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'fonts'); os.makedirs(OUT, exist_ok=True)

def save_subset(src, codes, out, wght=None, wrange=None):
    f = TTFont(src)
    opt = subset.Options(); opt.flavor = 'woff'; opt.layout_features = ['kern','liga','mark','mkmk','locl','ccmp']
    opt.hinting = False; opt.notdef_outline = True; opt.name_IDs = [1,2,3,4,6]; opt.drop_tables += ['DSIG']
    s = subset.Subsetter(opt); s.populate(unicodes=codes); s.subset(f)
    if wght is not None:
        f = instancer.instantiateVariableFont(f, {'wght': wght})
    elif wrange:
        f = instancer.instantiateVariableFont(f, {'wght': wrange})
    f.flavor = 'woff'; f.save(out)
    return os.path.getsize(out)

def rng(codes):
    codes = sorted(codes); out = []; a = b = None
    for c in codes:
        if a is None: a = b = c
        elif c == b + 1: b = c
        else: out.append((a, b)); a = b = c
    if a is not None: out.append((a, b))
    return ', '.join('U+%X' % x if x == y else 'U+%X-%X' % (x, y) for x, y in out)

latin = set(range(0x20, 0x250)) | set(range(0x300, 0x370)) | set(range(0x1E00, 0x1F00)) | set(range(0x2000, 0x2070)) | {0x20AB, 0x20AC, 0x2122, 0x2190, 0x2192, 0x2212, 0x2022, 0x2713, 0x2715}
css = ['/* Tự tạo bởi tools/build_fonts.py — đừng sửa tay */']
# Nunito + Baloo 2 (biến thiên, một file mỗi họ)
for fam, path, rngw, out in [('Nunito', 'nunito/Nunito[wght].ttf', (400, 900), 'nunito.woff'),
                             ('Baloo 2', 'baloo2/Baloo2[wght].ttf', (400, 800), 'baloo2.woff')]:
    n = save_subset(os.path.join(SRC, path), latin, os.path.join(OUT, out), wrange=rngw)
    css.append("@font-face{font-family:'%s';font-style:normal;font-weight:%d %d;font-display:swap;src:url('/assets/fonts/%s') format('woff');}" % (fam, rngw[0], rngw[1], out))
    print(fam, n)

# Chữ Hán: GB2312 (6763 chữ thường dùng) + dấu câu + mọi chữ Hán đang dùng trên site
gb = set()
for hi in range(0xB0, 0xF8):
    for lo in range(0xA1, 0xFF):
        try: gb.add(ord(bytes([hi, lo]).decode('gb2312')))
        except Exception: pass
used = set()
for p in ['index.html', 'games/words.js'] + glob.glob('lessons/*.html'):
    t = open(os.path.join(ROOT, p), encoding='utf-8').read()
    used |= {ord(c) for c in t if 0x4E00 <= ord(c) <= 0x9FFF}
punct = set(range(0x3000, 0x3040)) | set(range(0xFF00, 0xFF60)) | {0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x00B7, 0x25CB, 0x25A1}
han = (gb | used) & set(range(0x4E00, 0xA000))
core = sorted(used | punct)                       # mảnh 0: những gì site đang dùng (nhẹ, tải trước)
rest = sorted(han - used)
slices = [core] + [rest[i:i + 650] for i in range(0, len(rest), 650)]
nserif = os.path.join(SRC, 'notoserifsc/NotoSerifSC[wght].ttf')
tot = 0
for w in (400, 700):
    for i, cs in enumerate(slices):
        fn = 'notoserifsc-%d-%02d.woff' % (w, i)
        tot += save_subset(nserif, cs, os.path.join(OUT, fn), wght=w)
        css.append("@font-face{font-family:'Noto Serif SC';font-style:normal;font-weight:%d;font-display:swap;src:url('/assets/fonts/%s') format('woff');unicode-range:%s;}" % (w, fn, rng(cs)))
open(os.path.join(ROOT, 'assets', 'fonts.css'), 'w', encoding='utf-8').write('\n'.join(css) + '\n')
print('Noto Serif SC tổng', tot // 1024, 'KB;', len(slices), 'mảnh; chữ Hán site dùng:', len(used))
