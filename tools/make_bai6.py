#!/usr/bin/env python3
"""Tạo lessons/bai6.html (Ôn tập Bài 6 我学汉语) từ khung của bài 21 + dữ liệu bên dưới.
   python3 tools/make_bai6.py   (rồi chạy build_game_data.py, build_pinyin.py, build_slice_bank.py)"""
import re, json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'lessons/bai21.html'), encoding='utf-8').read()

W = [('国','guó','nước, quốc gia','guo','g5'),('人','rén','người','ren',''),('越南','Yuènán','Việt Nam','yuenan',''),
('哪','nǎ','nào','na3','g1'),('叫','jiào','tên là, gọi là','jiao',''),('名字','míngzi','tên','mingzi',''),
('什么','shénme','gì, cái gì','shenme','g1'),('贵姓','guìxìng','họ (hỏi lịch sự)','guixing','g1'),('学习','xuéxí','học','xuexi',''),
('汉字','hànzì','chữ Hán','hanzi',''),('发音','fāyīn','phát âm','fayin',''),('书','shū','sách','shu',''),
('那','nà','đó, kia','na4',''),('谁','shéi','ai','shei','g1'),('朋友','péngyou','bạn bè','pengyou',''),
('杂志','zázhì','tạp chí','zazhi',''),('请问','qǐngwèn','xin hỏi, cho hỏi','qingwen','g1')]
# ---- nhiễu pinyin: đổi thanh điệu của một âm tiết
TONES = {'a':'aāáǎà','e':'eēéěè','i':'iīíǐì','o':'oōóǒò','u':'uūúǔù','ü':'üǖǘǚǜ'}
REV = {}
for b, s in TONES.items():
    for t, ch in enumerate(s):
        if t: REV[ch] = (b, t)
def retone(syl, t):
    out = []; done = False
    cs = list(syl)
    idx = [i for i, c in enumerate(cs) if c in REV]
    if not idx: return None
    # chọn nguyên âm mang dấu: a/e ưu tiên, ou -> o, còn lại nguyên âm cuối
    pick = None
    for i in idx:
        if REV[cs[i]][0] in 'ae': pick = i; break
    if pick is None:
        for i in idx:
            if REV[cs[i]][0] == 'o': pick = i; break
    if pick is None: pick = idx[-1]
    b = REV[cs[pick]][0]; cs[pick] = TONES[b][t]
    return ''.join(cs)
def dis(py, n=3):
    rnd = random.Random(py)
    cand = []
    for i, c in enumerate(py):
        if c in REV:
            base, orig = REV[c]
            for t in range(1, 5):
                if t != orig: cand.append(py[:i] + TONES[base][t] + py[i+1:])
    cand = list(dict.fromkeys(cand)); rnd.shuffle(cand)
    # lấy trải đều: ưu tiên mỗi vị trí đổi thanh một lần
    seen = set(); first = []; rest = []
    for v in cand:
        pos = next(i for i in range(len(py)) if v[i] != py[i])
        (rest if pos in seen else first).append(v); seen.add(pos)
    return (first + rest)[:n]

GRP_IMG = lambda f: '../img/bai6/%s.jpg' % f
words = []
for cn, py, vi, img, g in W:
    d = {'cn': cn, 'py': py, 'vi': vi, 'dis': dis(py), 'img': GRP_IMG(img)}
    if g: d['grp'] = g
    assert len(d['dis']) == 3, (cn, d['dis'])
    words.append(d)

S = {
1:('中国很大。','Zhōngguó hěn dà.','Trung Quốc rất lớn.'),
2:('你去法国吗？','Nǐ qù Fǎguó ma?','Bạn đi Pháp không?'),
3:('你家有几口人？','Nǐ jiā yǒu jǐ kǒu rén?','Nhà bạn có mấy người?'),
4:('他是中国人。','Tā shì Zhōngguó rén.','Anh ấy là người Trung Quốc.'),
5:('我是越南人。','Wǒ shì Yuènán rén.','Tôi là người Việt Nam.'),
6:('我妈妈在越南工作。','Wǒ māma zài Yuènán gōngzuò.','Mẹ tôi làm việc ở Việt Nam.'),
7:('你是哪国人？','Nǐ shì nǎ guó rén?','Bạn là người nước nào?'),
8:('你朋友是哪国人？','Nǐ péngyou shì nǎ guó rén?','Bạn của bạn là người nước nào?'),
9:('我叫张东。','Wǒ jiào Zhāng Dōng.','Tôi tên là Trương Đông.'),
10:('他叫麦克。','Tā jiào Màikè.','Anh ấy tên là Mike.'),
11:('这是我的名字。','Zhè shì wǒ de míngzi.','Đây là tên của tôi.'),
12:('这是我妈妈的名字。','Zhè shì wǒ māma de míngzi.','Đây là tên của mẹ tôi.'),
13:('这是什么书？','Zhè shì shénme shū?','Đây là sách gì?'),
14:('你叫什么名字？','Nǐ jiào shénme míngzi?','Bạn tên là gì?'),
15:('请问，你贵姓？','Qǐngwèn, nǐ guìxìng?','Xin hỏi, bạn họ gì?'),
16:('老师，您贵姓？','Lǎoshī, nín guìxìng?','Thưa thầy/cô, họ của thầy/cô là gì?'),
17:('我学习汉语。','Wǒ xuéxí Hànyǔ.','Tôi học tiếng Hán.'),
18:('明天我学习英语。','Míngtiān wǒ xuéxí Yīngyǔ.','Ngày mai tôi học tiếng Anh.'),
19:('汉字很难。','Hànzì hěn nán.','Chữ Hán rất khó.'),
20:('这个汉字不太难。','Zhège Hànzì bú tài nán.','Chữ Hán này không quá khó.'),
21:('汉字很难，发音不太难。','Hànzì hěn nán, fāyīn bú tài nán.','Chữ Hán khó, phát âm không quá khó.'),
22:('汉语的发音难吗？','Hànyǔ de fāyīn nán ma?','Phát âm tiếng Hán có khó không?'),
23:('这是书。','Zhè shì shū.','Đây là sách.'),
24:('这是老师的书。','Zhè shì lǎoshī de shū.','Đây là sách của thầy/cô giáo.'),
25:('那是我的书。','Nà shì wǒ de shū.','Kia là sách của tôi.'),
26:('那个人是谁？','Nàge rén shì shéi?','Người kia là ai?'),
27:('这位老师是谁？','Zhè wèi lǎoshī shì shéi?','Thầy/cô giáo này là ai?'),
28:('那是谁的杂志？','Nà shì shéi de zázhì?','Kia là tạp chí của ai?'),
29:('那是我的杂志。','Nà shì wǒ de zázhì.','Kia là tạp chí của tôi.'),
30:('他是我的朋友。','Tā shì wǒ de péngyou.','Anh ấy là bạn của tôi.'),
31:('请问，学校在哪儿？','Qǐngwèn, xuéxiào zài nǎr?','Xin hỏi, trường học ở đâu?'),
32:('请问，这是谁的书？','Qǐngwèn, zhè shì shéi de shū?','Xin hỏi, đây là sách của ai?'),
33:('那是英文杂志。','Nà shì Yīngwén zázhì.','Kia là tạp chí tiếng Anh.'),
34:('我姓张。','Wǒ xìng Zhāng.','Tôi họ Trương.'),
}
SB = [(1,'中国|很|大'),(2,'你|去|法国|吗'),(4,'他|是|中国|人'),(5,'我|是|越南|人'),(6,'我|妈妈|在|越南|工作'),(7,'你|是|哪|国|人'),
(8,'你|朋友|是|哪|国|人'),(9,'我|叫|张东'),(14,'你|叫|什么|名字'),(15,'请问|，|你|贵姓'),(17,'我|学习|汉语'),(19,'汉字|很|难'),
(22,'汉语|的|发音|难|吗'),(24,'这|是|老师|的|书'),(25,'那|是|我的|书'),(26,'那|个|人|是|谁'),(28,'那|是|谁|的|杂志'),
(30,'他|是|我的|朋友'),(31,'请问|，|学校|在|哪儿'),(33,'那|是|英文|杂志')]
sb = []
for n, ch in SB:
    ws = ch.split('|'); ans = S[n][0]
    assert ''.join(ws) == re.sub(r'[。！？]+$', '', ans), (n, ws, ans)
    sb.append({'words': ws, 'answer': ans, 'vi': S[n][2]})

FB = [
('Bạn là người nước nào?','你是','国人？','哪',['谁','那','叫']),
('Tôi là người Việt Nam.','我是越南','。','人',['国','书','叫']),
('Bạn tên là gì?','你叫','名字？','什么',['哪','谁','那']),
('Tôi tên là Trương Đông.','我','张东。','叫',['学习','请问','贵姓']),
('Tôi học tiếng Hán.','我','汉语。','学习',['叫','请问','贵姓']),
('Đây là sách gì?','这是','书？','什么',['哪','谁','那']),
('Kia là sách của tôi.','','是我的书。','那',['谁','哪','什么']),
('Người kia là ai?','那个人是','？','谁',['哪','那','叫']),
('Xin hỏi, bạn họ gì?','','，你贵姓？','请问',['学习','朋友','什么']),
('Chữ Hán khó, phát âm không quá khó.','汉字很难，','不太难。','发音',['杂志','名字','朋友']),
('Kia là tạp chí tiếng Anh.','那是英文','。','杂志',['朋友','叫','学习']),
('Anh ấy là bạn của tôi.','他是我的','。','朋友',['学习','叫','请问']),
('Đây là tên của tôi.','这是我的','。','名字',['学习','叫','请问']),
('Đây là sách của thầy giáo.','这是老师的','。','书',['叫','哪','请问']),
('Mẹ tôi làm việc ở Việt Nam.','我妈妈在','工作。','越南',['汉字','杂志','朋友']),
('Kia là tạp chí của ai?','那是','的杂志？','谁',['哪','叫','那']),
('Phát âm tiếng Hán có khó không?','汉语的','难吗？','发音',['杂志','叫','请问']),
]
fb = [{'hint': h, 'before': b, 'after': a, 'options': [ans] + o, 'a': 0} for h, b, a, ans, o in FB]

TS_SENT = [1,2,3,7,9,13,14,15,17,19,22,25,26,28,30,31,33]
ts = [{'vi': w['vi'], 'cn': w['cn'], 'py': w['py']} for w in words] + [{'vi': S[n][2], 'cn': S[n][0], 'py': S[n][1]} for n in TS_SENT]
SENT8 = [7,9,14,17,22,26,28,31]
FREE = [
(5,[['越南'],['人']]),(7,[['哪'],['人']]),(9,[['叫'],['张东']]),(14,[['什么'],['名字']]),
(15,[['请问'],['贵姓']]),(17,[['学习'],['汉语']]),(26,[['谁'],['那']]),(28,[['谁'],['杂志']])]
cfg = {'word': [{'cn': w['cn'], 'py': w['py'], 'vi': w['vi']} for w in words],
       'sent': [{'cn': S[n][0], 'py': S[n][1], 'vi': S[n][2]} for n in SENT8],
       'free': [{'vi': S[n][2], 'cn': S[n][0], 'py': S[n][1], 'keys': k} for n, k in FREE]}

def J(o, indent=None): return json.dumps(o, ensure_ascii=False, indent=indent)
s = tpl
def sub1(pat, rep, flags=re.S):
    global s
    s, n = re.subn(pat, lambda m: rep, s, count=1, flags=flags)
    assert n == 1, pat
sub1(r'^const WORDS = \[.*?\];$', 'const WORDS = ' + J(words) + ';', re.M)
sub1(r'const SENTENCE_BUILDER = \[.*?\n\];', 'const SENTENCE_BUILDER = ' + J(sb, 1) + ';')
sub1(r'const FILL_BLANK = \[.*?\n\];', 'const FILL_BLANK = ' + J(fb, 1) + ';')
sub1(r'const TRANSLATE_SELFCHECK = \[.*?\n\];', 'const TRANSLATE_SELFCHECK = ' + J(ts, 1) + ';')
sub1(r'var CFG = \{"word":.*?\};\n', 'var CFG = ' + J(cfg) + ';\n')
# ảnh nhiễu: không lấy đáp án nhiễu cùng nhóm hình với từ đúng (vd. 箱子/黑/红, 笔/圆珠笔/铅笔)
old = "shuffle(WORDS.filter(x=>x.cn!==it.word.cn)).slice(0,3)"
assert s.count(old) == 1
s = s.replace(old, "shuffle(WORDS.filter(x=>x.cn!==it.word.cn && !(it.word.grp && x.grp===it.word.grp))).slice(0,3)")
nimg = sum(1 for w in words if w.get('img'))
rp = [
 ('<title>我们明天七点一刻出发 · Ôn tập Bài 21 — Mai 7h15 xuất phát</title>', '<title>我学汉语 · Ôn tập Bài 6 — Tôi học tiếng Hán</title>'),
 ('/* ===== Bài 21 ===== */', '/* ===== Bài 6 ===== */'),
 ('<small>Ôn tập · Bài 21</small>', '<small>Ôn tập · Bài 6</small>'),
 ('<span class="plate">第 21 课</span>ÔN TẬP BÀI 21', '<span class="plate">第 6 课</span>ÔN TẬP BÀI 6'),
 ('<span class="py">Wǒmen míngtiān qī diǎn yí kè chūfā</span>我们明天七点一刻出发', '<span class="py">Wǒ xuéxí Hànyǔ</span>我学汉语'),
 ('Ngày mai chúng ta xuất phát lúc 7h15 — Ôn tập Bài 21', 'Tôi học tiếng Hán — Ôn tập Bài 6'),
 ('Ôn <b>từ mới</b> (起床 半 一刻 差 出发 洗澡 睡觉 锻炼身体 操场 教室 爬山 集合 年级 上班 下班 准时 带 课间…), cách <b>nói giờ</b> 点 · 刻 · 半 · 差, và các đoạn nói về một ngày của bạn.', 'Ôn <b>từ mới</b> (国 人 越南 哪 叫 名字 什么 贵姓 学习 汉字 发音 书 那 谁 朋友 杂志 请问), cách hỏi <b>你是哪国人？</b> · <b>你叫什么名字？</b> · <b>谁的…？</b> và kết cấu <b>的</b>.'),
 ('slide Bài 21', 'slide Bài 6'),
 ('<footer>MiaoChinese — 我们明天七点一刻出发 · Bài 21</footer>', '<footer>MiaoChinese — 我学汉语 · Bài 6</footer>'),
 ('LESSON:21', 'LESSON:6'),
]
for a, b in rp:
    assert a in s, a[:40]
    s = s.replace(a, b)
nw = len(words)
s = s.replace('id="pictureScore">0 / 22<', 'id="pictureScore">0 / %d<' % nimg).replace('id="pinyinScore">0 / 27<', 'id="pinyinScore">0 / %d<' % nw).replace('id="speakWordScore">0 / 27<', 'id="speakWordScore">0 / %d<' % nw)
left = [m for m in re.findall(r'.{30}Bài 21.{20}|.{20}bai21.{20}', s)]
print('còn sót:', left[:5])
open(os.path.join(ROOT, 'lessons/bai6.html'), 'w', encoding='utf-8').write(s)
print('ok', len(words), len(sb), len(fb), len(ts))
