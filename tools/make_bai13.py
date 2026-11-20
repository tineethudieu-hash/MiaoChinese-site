#!/usr/bin/env python3
"""Tạo lessons/bai13.html (Ôn tập Bài 13 这是不是中药？) từ khung của bài 21 + dữ liệu bên dưới.
   python3 tools/make_bai13.py   (rồi chạy tools/build_game_data.py)"""
import re, json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'lessons/bai21.html'), encoding='utf-8').read()

# ---- từ mới: (cn, py, vi, ảnh, nhóm ảnh dễ nhầm)
W = [('箱子','xiāngzi','vali, thùng','xiangzi','g1'),('黑','hēi','đen','hei','g1'),('红','hóng','đỏ','hong','g1'),
('重','zhòng','nặng','zhong','g1'),('轻','qīng','nhẹ','qing','g1'),('吃药','chī yào','uống thuốc','chiyao','g3'),
('中药','zhōngyào','thuốc Đông y','zhongyao','g3'),('西药','xīyào','thuốc Tây','xiyao','g3'),('茶叶','cháyè','lá trà','chaye',''),
('日用品','rìyòngpǐn','đồ dùng hằng ngày','riyongpin',''),('衣服','yīfu','quần áo','yifu',''),('雨','yǔ','mưa','yu','g4'),
('雨伞','yǔsǎn','ô, dù','yusan','g4'),('香水','xiāngshuǐ','nước hoa','xiangshui',''),('瓶子','píngzi','chai, lọ','pingzi',''),
('词典','cídiǎn','từ điển','cidian',''),('光盘','guāngpán','đĩa quang, CD/DVD','guangpan',''),('笔','bǐ','bút','bi','g2'),
('包','bāo','túi','bao',''),('圆珠笔','yuánzhūbǐ','bút bi','yuanzhubi','g2'),('铅笔','qiānbǐ','bút chì','qianbi','g2'),
('报纸','bàozhǐ','báo giấy','baozhi',''),('地图','dìtú','bản đồ','ditu',''),('椅子','yǐzi','ghế','yizi',''),
('冰淇淋','bīngqílín','kem','bingqilin',''),('厕所 / 洗手间','cèsuǒ / xǐshǒujiān','nhà vệ sinh','cesuo','')]

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

GRP_IMG = lambda f: '../img/bai13/%s.jpg' % f
words = []
for cn, py, vi, img, g in W:
    d = {'cn': cn, 'py': py, 'vi': vi, 'dis': dis(py), 'img': GRP_IMG(img)}
    if g: d['grp'] = g
    assert len(d['dis']) == 3, (cn, d['dis'])
    words.append(d)

# ---- câu (cn, pinyin, tiếng Việt)
S = {
1:('这是我的箱子。','Zhè shì wǒ de xiāngzi.','Đây là vali của tôi.'),
2:('你的箱子在哪儿？','Nǐ de xiāngzi zài nǎr?','Vali của bạn ở đâu?'),
3:('我的箱子是黑的。','Wǒ de xiāngzi shì hēi de.','Vali của tôi màu đen.'),
4:('这个黑箱子很重。','Zhège hēi xiāngzi hěn zhòng.','Chiếc vali đen này rất nặng.'),
5:('那个红箱子很轻。','Nàge hóng xiāngzi hěn qīng.','Chiếc vali đỏ kia rất nhẹ.'),
6:('你的箱子重不重？','Nǐ de xiāngzi zhòng bu zhòng?','Vali của bạn có nặng không?'),
7:('你吃药了吗？','Nǐ chī yào le ma?','Bạn uống thuốc chưa?'),
8:('我今天要吃药。','Wǒ jīntiān yào chī yào.','Hôm nay tôi phải uống thuốc.'),
9:('这是不是中药？','Zhè shì bu shì zhōngyào?','Đây có phải thuốc Đông y không?'),
10:('这是中药，不是西药。','Zhè shì zhōngyào, bú shì xīyào.','Đây là thuốc Đông y, không phải thuốc Tây.'),
11:('这是茶叶，不是药。','Zhè shì cháyè, bú shì yào.','Đây là lá trà, không phải thuốc.'),
12:('这些都是日用品。','Zhèxiē dōu shì rìyòngpǐn.','Những thứ này đều là đồ dùng hằng ngày.'),
13:('我有一件衣服。','Wǒ yǒu yí jiàn yīfu.','Tôi có một bộ quần áo.'),
14:('箱子里有两件衣服。','Xiāngzi lǐ yǒu liǎng jiàn yīfu.','Trong vali có hai bộ quần áo.'),
15:('今天下雨了。','Jīntiān xiàyǔ le.','Hôm nay trời mưa rồi.'),
16:('明天会下雨吗？','Míngtiān huì xiàyǔ ma?','Ngày mai trời có mưa không?'),
17:('我有一把雨伞。','Wǒ yǒu yì bǎ yǔsǎn.','Tôi có một cái ô.'),
18:('这两把雨伞是我的。','Zhè liǎng bǎ yǔsǎn shì wǒ de.','Hai cái ô này là của tôi.'),
19:('箱子里有一瓶香水。','Xiāngzi lǐ yǒu yì píng xiāngshuǐ.','Trong vali có một lọ nước hoa.'),
20:('这是谁的瓶子？','Zhè shì shéi de píngzi?','Đây là chai của ai?'),
21:('瓶子里有水。','Píngzi lǐ yǒu shuǐ.','Trong chai có nước.'),
22:('这是一本汉语词典。','Zhè shì yì běn Hànyǔ cídiǎn.','Đây là một cuốn từ điển tiếng Hán.'),
23:('这是一张光盘。','Zhè shì yì zhāng guāngpán.','Đây là một cái đĩa CD.'),
24:('我有一支笔。','Wǒ yǒu yì zhī bǐ.','Tôi có một cây bút.'),
25:('这是一支圆珠笔。','Zhè shì yì zhī yuánzhūbǐ.','Đây là một cây bút bi.'),
26:('这是谁的铅笔？','Zhè shì shéi de qiānbǐ?','Đây là bút chì của ai?'),
27:('我爸爸看报纸。','Wǒ bàba kàn bàozhǐ.','Bố tôi đọc báo.'),
28:('这是一张中国地图。','Zhè shì yì zhāng Zhōngguó dìtú.','Đây là một tấm bản đồ Trung Quốc.'),
29:('你吃不吃冰淇淋？','Nǐ chī bu chī bīngqílín?','Bạn có ăn kem không?'),
30:('厕所在哪儿？','Cèsuǒ zài nǎr?','Nhà vệ sinh ở đâu?'),
31:('洗手间在这儿。','Xǐshǒujiān zài zhèr.','Nhà vệ sinh ở đây.'),
32:('这是我的包。','Zhè shì wǒ de bāo.','Đây là túi của tôi.'),
33:('包里有一本书。','Bāo lǐ yǒu yì běn shū.','Trong túi có một quyển sách.'),
34:('你有没有箱子？','Nǐ yǒu méiyǒu xiāngzi?','Bạn có vali không?'),
}
# ---- sắp xếp câu: (số câu, các cụm)
SB = [(1,'这|是|我的|箱子'),(2,'你的|箱子|在|哪儿'),(3,'我的|箱子|是|黑|的'),(4,'这个|黑|箱子|很|重'),(5,'那个|红|箱子|很|轻'),
(6,'你的|箱子|重|不|重'),(7,'你|吃药|了|吗'),(8,'我|今天|要|吃药'),(9,'这|是|不|是|中药'),(10,'这|是|中药|，|不|是|西药'),
(11,'这|是|茶叶|，|不|是|药'),(13,'我|有|一件|衣服'),(14,'箱子|里|有|两件|衣服'),(15,'今天|下雨|了'),(16,'明天|会|下雨|吗'),
(17,'我|有|一把|雨伞'),(18,'这|两把|雨伞|是|我的'),(19,'箱子|里|有|一瓶|香水'),(20,'这|是|谁|的|瓶子'),(21,'瓶子|里|有|水'),
(22,'这|是|一本|汉语|词典'),(23,'这|是|一张|光盘'),(24,'我|有|一支|笔'),(27,'我|爸爸|看|报纸'),(28,'这|是|一张|中国|地图'),
(29,'你|吃|不|吃|冰淇淋'),(30,'厕所|在|哪儿'),(34,'你|有|没有|箱子')]
sb = []
for n, ch in SB:
    ws = ch.split('|'); ans = S[n][0]
    assert ''.join(ws) == re.sub(r'[。！？]+$', '', ans), (n, ws, ans)
    sb.append({'words': ws, 'answer': ans, 'vi': S[n][2]})

# ---- điền từ: (gợi ý VN, trước, sau, đáp án, 3 nhiễu)
FB = [
('Một cái ô.','一','雨伞。','把',['瓶','本','位']),
('Hai lọ nước hoa.','两','香水。','瓶',['把','本','位']),
('Ba thầy/cô giáo.','三','老师。','位',['瓶','把','支']),
('Bốn cái vali.','四','箱子。','个',['瓶','位','本']),
('Năm quyển sách.','五','书。','本',['瓶','位','支']),
('Sáu cái đĩa CD.','六','光盘。','张',['瓶','把','位']),
('Bảy quyển từ điển.','七','词典。','本',['支','瓶','位']),
('Tám cây bút.','八','笔。','支',['把','位','瓶']),
('Mười bộ quần áo.','十','衣服。','件',['瓶','位','支']),
('Đây có phải thuốc Đông y không?','这是不是','？','中药',['西药','茶叶','日用品']),
('Vali của bạn có nặng không?','你的箱子','不重？','重',['轻','黑','红']),
('Chiếc vali đỏ kia rất nhẹ.','那个红箱子很','。','轻',['重','黑','红']),
('Vali của tôi màu đen.','我的箱子是','的。','黑',['红','重','轻']),
('Hôm nay trời mưa rồi.','今天下','了。','雨',['雨伞','茶叶','香水']),
('Tôi có một cái ô.','我有一把','。','雨伞',['光盘','词典','香水']),
('Trong vali có một lọ nước hoa.','箱子里有一瓶','。','香水',['雨伞','椅子','衣服']),
('Đây là lá trà, không phải thuốc.','这是','，不是药。','茶叶',['日用品','衣服','香水']),
('Tôi đến cửa hàng mua đồ dùng hằng ngày.','我去商店买','。','日用品',['词典','茶叶','雨伞']),
('Đây là một tấm bản đồ Trung Quốc.','这是一张中国','。','地图',['词典','报纸','光盘']),
('Bố tôi đọc báo.','我爸爸看','。','报纸',['地图','冰淇淋','椅子']),
('Bạn có ăn kem không?','你吃不吃','？','冰淇淋',['衣服','词典','报纸']),
('Nhà vệ sinh ở đâu?','','在哪儿？','厕所',['地图','词典','报纸']),
]
fb = [{'hint': h, 'before': b, 'after': a, 'options': [ans] + o, 'a': 0} for h, b, a, ans, o in FB]

# ---- tự kiểm tra dịch / gõ chữ: từ mới + câu
TS_SENT = [1,2,3,4,5,6,8,9,10,11,14,15,16,18,19,20,22,23,26,28,30,31]
ts = [{'vi': w['vi'], 'cn': w['cn'], 'py': w['py']} for w in words] + [{'vi': S[n][2], 'cn': S[n][0], 'py': S[n][1]} for n in TS_SENT]
SENT8 = [4,6,9,10,15,18,22,30]
FREE = [
(1,[['箱子'],['我的']]),(6,[['箱子'],['重']]),(9,[['中药'],['是不是','是']]),(15,[['下雨'],['今天']]),
(17,[['雨伞'],['一把','把']]),(19,[['香水'],['一瓶','瓶']]),(22,[['词典'],['一本','本']]),(30,[['厕所','洗手间'],['哪儿']])]
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
 ('<title>我们明天七点一刻出发 · Ôn tập Bài 21 — Mai 7h15 xuất phát</title>', '<title>这是不是中药？ · Ôn tập Bài 13 — Đây có phải thuốc Đông y không?</title>'),
 ('/* ===== Bài 21 ===== */', '/* ===== Bài 13 ===== */'),
 ('<small>Ôn tập · Bài 21</small>', '<small>Ôn tập · Bài 13</small>'),
 ('<span class="plate">第 21 课</span>ÔN TẬP BÀI 21', '<span class="plate">第 13 课</span>ÔN TẬP BÀI 13'),
 ('<span class="py">Wǒmen míngtiān qī diǎn yí kè chūfā</span>我们明天七点一刻出发', '<span class="py">Zhè shì bu shì zhōngyào?</span>这是不是中药？'),
 ('Ngày mai chúng ta xuất phát lúc 7h15 — Ôn tập Bài 21', 'Đây có phải thuốc Đông y không? — Ôn tập Bài 13'),
 ('Ôn <b>từ mới</b> (起床 半 一刻 差 出发 洗澡 睡觉 锻炼身体 操场 教室 爬山 集合 年级 上班 下班 准时 带 课间…), cách <b>nói giờ</b> 点 · 刻 · 半 · 差, và các đoạn nói về một ngày của bạn.', 'Ôn <b>từ mới</b> (箱子 黑 红 重 轻 吃药 中药 西药 茶叶 日用品 衣服 雨伞 香水 词典 光盘 笔…), câu hỏi <b>是不是</b> · <b>重不重</b> và các <b>lượng từ</b> 件 · 把 · 瓶 · 本 · 张 · 支.'),
 ('slide Bài 21', 'slide Bài 13'),
 ('<footer>MiaoChinese — 我们明天七点一刻出发 · Bài 21</footer>', '<footer>MiaoChinese — 这是不是中药？ · Bài 13</footer>'),
 ('LESSON:21', 'LESSON:13'),
]
for a, b in rp:
    assert a in s, a[:40]
    s = s.replace(a, b)
nw = len(words)
s = s.replace('id="pictureScore">0 / 22<', 'id="pictureScore">0 / %d<' % nimg).replace('id="pinyinScore">0 / 27<', 'id="pinyinScore">0 / %d<' % nw).replace('id="speakWordScore">0 / 27<', 'id="speakWordScore">0 / %d<' % nw)
left = [m for m in re.findall(r'.{30}Bài 21.{20}|.{20}bai21.{20}', s)]
print('còn sót:', left[:5])
open(os.path.join(ROOT, 'lessons/bai13.html'), 'w', encoding='utf-8').write(s)
print('ok', len(words), len(sb), len(fb), len(ts))
