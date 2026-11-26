#!/usr/bin/env python3
"""Tạo lessons/bai22.html (Ôn tập Bài 22 我打算请老师教我京剧) từ khung của bài 21 + dữ liệu bên dưới.
   python3 tools/make_bai22.py   (rồi chạy build_game_data.py, build_pinyin.py, build_slice_bank.py)"""
import re, json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'lessons/bai21.html'), encoding='utf-8').read()

W = [('爱好','àihào','sở thích','aihao',''),('京剧','jīngjù','Kinh kịch','jingju','g2'),('电脑','diànnǎo','máy tính','diannao',''),
('玩','wán','chơi','wan',''),('画儿','huàr','bức tranh','huar','g3'),('画','huà','vẽ','hua','g3'),('书法','shūfǎ','thư pháp','shufa','g4'),
('唱','chàng','hát','chang','g2'),('让','ràng','để, cho phép, bảo ai làm gì','rang',''),('心情','xīnqíng','tâm trạng','xinqing',''),
('大家','dàjiā','mọi người, cả lớp','dajia',''),('业余','yèyú','ngoài giờ làm hoặc giờ học','yeyu','g4'),('喜欢','xǐhuan','thích','xihuan','g2'),
('感兴趣','gǎn xìngqù','có hứng thú, quan tâm','ganxingqu','g4'),('非常','fēicháng','rất','feichang','g2'),
('特别','tèbié','đặc biệt, rất','tebie','g4'),('感到','gǎndào','cảm thấy','gandao',''),('愉快','yúkuài','vui vẻ, vui thích','yukuai',''),
('以前','yǐqián','trước đây, trước khi','yiqian',''),('自己','zìjǐ','bản thân, tự mình','ziji',''),('下课','xià kè','tan học, kết thúc tiết học','xiake',''),
('完','wán','xong, hoàn tất','wanle',''),
('惊讶','jīngyà','ngạc nhiên','jingya',''),('老外','lǎowài','người nước ngoài (khẩu ngữ)','laowai',''),('笔记本','bǐjìběn','sổ tay, vở ghi chép','biji',''),
('唱歌','chànggē','ca hát','changge','g2'),('希望','xīwàng','hy vọng','xiwang',''),('演出','yǎnchū','biểu diễn, buổi biểu diễn','yanchu','g2'),
('足球','zúqiú','bóng đá','zuqiu','g6'),('比赛','bǐsài','thi đấu, trận đấu','bisai','g6'),('网球','wǎngqiú','quần vợt','wangqiu','g6'),
('太极拳','tàijíquán','thái cực quyền','taiji','g7'),('武术','wǔshù','võ thuật','wushu','g7'),('打羽毛球','dǎ yǔmáoqiú','chơi cầu lông','caulong','g6'),('打匹克球','dǎ pǐkèqiú','chơi pickleball','pickleball','g6')]
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

GRP_IMG = lambda f: '../img/bai22/%s.jpg' % f
words = []
for cn, py, vi, img, g in W:
    d = {'cn': cn, 'py': py, 'vi': vi, 'dis': dis(py), 'img': GRP_IMG(img)}
    if g: d['grp'] = g
    assert len(d['dis']) == 3, (cn, d['dis'])
    words.append(d)

S = {
1:('你有什么爱好？','Nǐ yǒu shénme àihào?','Bạn có sở thích gì?'),
2:('我的爱好是看书。','Wǒ de àihào shì kàn shū.','Sở thích của tôi là đọc sách.'),
3:('我妈妈常常看京剧。','Wǒ māma chángcháng kàn jīngjù.','Mẹ tôi thường xem kinh kịch.'),
4:('我们一起去看京剧吧。','Wǒmen yìqǐ qù kàn jīngjù ba.','Chúng ta cùng đi xem kinh kịch nhé.'),
5:('我常常用电脑听音乐。','Wǒ chángcháng yòng diànnǎo tīng yīnyuè.','Tôi thường dùng máy tính nghe nhạc.'),
6:('我喜欢玩电脑。','Wǒ xǐhuan wán diànnǎo.','Tôi thích chơi máy tính.'),
7:('这张画儿真好看！','Zhè zhāng huàr zhēn hǎokàn!','Bức tranh này đẹp thật!'),
8:('你会画猫吗？','Nǐ huì huà māo ma?','Bạn biết vẽ mèo không?'),
9:('我正在学书法。','Wǒ zhèngzài xué shūfǎ.','Tôi đang học thư pháp.'),
10:('我还想学唱京剧。','Wǒ hái xiǎng xué chàng jīngjù.','Tôi còn muốn học hát kinh kịch.'),
11:('老师让我们谈谈爱好。','Lǎoshī ràng wǒmen tántan àihào.','Cô giáo bảo chúng tôi nói về sở thích.'),
12:('你今天心情怎么样？','Nǐ jīntiān xīnqíng zěnmeyàng?','Hôm nay tâm trạng bạn thế nào?'),
13:('请大家一起读这句话。','Qǐng dàjiā yìqǐ dú zhè jù huà.','Mời mọi người cùng đọc câu này.'),
14:('你业余时间常常做什么？','Nǐ yèyú shíjiān chángcháng zuò shénme?','Thời gian rảnh bạn thường làm gì?'),
15:('你喜欢听音乐吗？','Nǐ xǐhuan tīng yīnyuè ma?','Bạn có thích nghe nhạc không?'),
16:('你对京剧感兴趣吗？','Nǐ duì jīngjù gǎn xìngqù ma?','Bạn có hứng thú với kinh kịch không?'),
17:('我对书法非常感兴趣。','Wǒ duì shūfǎ fēicháng gǎn xìngqù.','Tôi rất hứng thú với thư pháp.'),
18:('我对书法特别感兴趣。','Wǒ duì shūfǎ tèbié gǎn xìngqù.','Tôi đặc biệt hứng thú với thư pháp.'),
19:('跟朋友聊天儿，我感到很高兴。','Gēn péngyou liáotiānr, wǒ gǎndào hěn gāoxìng.','Trò chuyện với bạn, tôi thấy rất vui.'),
20:('下课以后，跟朋友聊聊天儿，我感到很愉快。','Xià kè yǐhòu, gēn péngyou liáoliao tiānr, wǒ gǎndào hěn yúkuài.','Sau giờ học, trò chuyện với bạn, tôi cảm thấy rất vui vẻ.'),
21:('祝你周末愉快！','Zhù nǐ zhōumò yúkuài!','Chúc bạn cuối tuần vui vẻ!'),
22:('我来中国以前就喜欢书法。','Wǒ lái Zhōngguó yǐqián jiù xǐhuan shūfǎ.','Trước khi đến Trung Quốc tôi đã thích thư pháp.'),
23:('请说说自己的爱好。','Qǐng shuōshuo zìjǐ de àihào.','Hãy nói về sở thích của bản thân.'),
24:('这张画儿是我自己画的。','Zhè zhāng huàr shì wǒ zìjǐ huà de.','Bức tranh này do tôi tự vẽ.'),
25:('我们今天几点下课？','Wǒmen jīntiān jǐ diǎn xià kè?','Hôm nay mấy giờ chúng ta tan học?'),
26:('我做完作业了。','Wǒ zuòwán zuòyè le.','Tôi làm xong bài tập rồi.'),
27:('看完京剧以后，我们一起去吃饭吧。','Kànwán jīngjù yǐhòu, wǒmen yìqǐ qù chīfàn ba.','Xem xong kinh kịch, chúng ta cùng đi ăn nhé.'),
28:('我特别喜欢这张画儿。','Wǒ tèbié xǐhuan zhè zhāng huàr.','Tôi đặc biệt thích bức tranh này.'),
29:('老师感到很惊讶。','Lǎoshī gǎndào hěn jīngyà.','Cô giáo rất ngạc nhiên.'),
30:('我这个“老外”非常喜欢看京剧。','Wǒ zhège “lǎowài” fēicháng xǐhuan kàn jīngjù.','Tôi là “người nước ngoài” mà rất thích xem kinh kịch.'),
31:('麦克有一台笔记本电脑。','Màikè yǒu yì tái bǐjìběn diànnǎo.','Mike có một chiếc laptop.'),
32:('他喜欢玩电脑。','Tā xǐhuan wán diànnǎo.','Anh ấy thích chơi máy tính.'),
33:('我喜欢唱中文歌。','Wǒ xǐhuan chàng Zhōngwén gē.','Tôi thích hát bài hát tiếng Trung.'),
34:('我希望以后能唱京剧。','Wǒ xīwàng yǐhòu néng chàng jīngjù.','Tôi hy vọng sau này có thể hát kinh kịch.'),
35:('我希望以后能参加演出。','Wǒ xīwàng yǐhòu néng cānjiā yǎnchū.','Tôi hy vọng sau này có thể tham gia biểu diễn.'),
36:('我喜欢看足球。','Wǒ xǐhuan kàn zúqiú.','Tôi thích xem bóng đá.'),
37:('我常常看足球比赛。','Wǒ chángcháng kàn zúqiú bǐsài.','Tôi thường xem trận đấu bóng đá.'),
38:('我下课以后常常打网球。','Wǒ xià kè yǐhòu chángcháng dǎ wǎngqiú.','Sau giờ học tôi thường đánh quần vợt.'),
39:('我喜欢打太极拳。','Wǒ xǐhuan dǎ tàijíquán.','Tôi thích đánh thái cực quyền.'),
40:('我对武术特别感兴趣。','Wǒ duì wǔshù tèbié gǎn xìngqù.','Tôi đặc biệt hứng thú với võ thuật.'),
41:('星期天我常常跟朋友一起打羽毛球。','Xīngqītiān wǒ chángcháng gēn péngyou yìqǐ dǎ yǔmáoqiú.','Chủ nhật tôi thường cùng bạn chơi cầu lông.'),
42:('我也想学打匹克球。','Wǒ yě xiǎng xué dǎ pǐkèqiú.','Tôi cũng muốn học chơi pickleball.'),
}
SB = [(1,'你|有|什么|爱好'),(2,'我的|爱好|是|看书'),(3,'我|妈妈|常常|看|京剧'),(4,'我们|一起|去|看|京剧|吧'),(6,'我|喜欢|玩|电脑'),
(9,'我|正在|学|书法'),(10,'我|还|想|学|唱|京剧'),(11,'老师|让|我们|谈谈|爱好'),(12,'你|今天|心情|怎么样'),(14,'你|业余|时间|常常|做|什么'),
(16,'你|对|京剧|感兴趣|吗'),(17,'我|对|书法|非常|感兴趣'),(22,'我|来|中国|以前|就|喜欢|书法'),(24,'这|张|画儿|是|我|自己|画|的'),
(25,'我们|今天|几点|下课'),(26,'我|做|完|作业|了'),(29,'老师|感到|很|惊讶'),(31,'麦克|有|一|台|笔记本|电脑'),(34,'我|希望|以后|能|唱|京剧'),(37,'我|常常|看|足球|比赛'),(38,'我|下课|以后|常常|打|网球'),(40,'我|对|武术|特别|感兴趣'),(42,'我|也|想|学|打|匹克球')]
sb = []
for n, ch in SB:
    ws = ch.split('|'); ans = S[n][0]
    assert ''.join(ws) == re.sub(r'[。！？]+$', '', ans), (n, ws, ans)
    sb.append({'words': ws, 'answer': ans, 'vi': S[n][2]})

FB = [
('Tôi rất hứng thú với văn hóa Trung Quốc.','我','中国文化非常感兴趣。','对',['让','唱','以前']),
('Trước khi đến Trung Quốc, tôi là nhân viên công ty.','我来中国','是公司职员。','以前',['对','让','爱好']),
('Cô giáo cho chúng tôi nói về sở thích của mình.','老师','我们谈谈自己的爱好。','让',['对','唱','喜欢']),
('Tôi thích ăn món Trung Quốc.','我','吃中国菜。','喜欢',['让','对','唱']),
('Bạn có sở thích gì?','你有什么','？','爱好',['心情','业余','电脑']),
('Sở thích của tôi là vẽ tranh.','我的','是画画儿。','爱好',['心情','业余','电脑']),
('Anh ấy rất thích hát kinh kịch.','他非常喜欢','京剧。','唱',['让','对','以前']),
('Tôi đang học thư pháp.','我正在学','。','书法',['京剧','电脑','画儿']),
('Hôm nay tâm trạng bạn thế nào?','你今天','怎么样？','心情',['爱好','业余','大家']),
('Mời mọi người cùng đọc câu này.','请','一起读这句话。','大家',['自己','爱好','心情']),
('Tôi làm xong bài tập rồi.','我做','作业了。','完',['唱','玩','让']),
('Tôi thích chơi máy tính.','我喜欢玩','。','电脑',['书法','京剧','画儿']),
('Hôm nay mấy giờ tan học?','我们今天几点','？','下课',['业余','爱好','心情']),
('Bức tranh này do tôi tự vẽ.','这张画儿是我','画的。','自己',['大家','让','对']),
('Trò chuyện với bạn, tôi cảm thấy rất vui.','跟朋友聊天儿，我','很高兴。','感到',['让','对','喜欢']),
('Tôi đặc biệt thích bức tranh này.','我','喜欢这张画儿。','特别',['让','对','以前']),
('Chúc bạn cuối tuần vui vẻ!','祝你周末','！','愉快',['爱好','业余','心情']),
('Bạn có hứng thú với kinh kịch không?','你对京剧','吗？','感兴趣',['喜欢','爱好','业余']),
('Mẹ tôi thường xem kinh kịch.','我妈妈常常看','。','京剧',['电脑','书法','画儿']),
('Bạn biết vẽ mèo không?','你会','猫吗？','画',['唱','玩','让']),('Cô giáo rất ngạc nhiên.','老师感到很','。','惊讶',['演出','比赛','足球']),
('Tôi hy vọng sau này có thể tham gia biểu diễn.','我希望以后能参加','。','演出',['笔记本','足球','太极拳']),
('Tôi thích xem bóng đá.','我喜欢看','。','足球',['惊讶','笔记本','希望']),
('Tôi thường xem trận đấu bóng đá.','我常常看足球','。','比赛',['希望','惊讶','笔记本']),
('Tôi thích đánh thái cực quyền.','我喜欢打','。','太极拳',['惊讶','笔记本','演出']),
('Tôi đặc biệt hứng thú với võ thuật.','我对','特别感兴趣。','武术',['惊讶','笔记本','希望']),
('Mike có một chiếc laptop.','麦克有一台','电脑。','笔记本',['惊讶','希望','演出']),
('Tôi hy vọng sau này có thể hát kinh kịch.','我','以后能唱京剧。','希望',['惊讶','演出','笔记本']),
]
fb = [{'hint': h, 'before': b, 'after': a, 'options': [ans] + o, 'a': 0} for h, b, a, ans, o in FB]

TS_SENT = [1,2,4,6,9,10,11,12,14,16,17,19,20,21,22,24,25,26,27,29,31,34,37,38,41,42]
ts = [{'vi': w['vi'], 'cn': w['cn'], 'py': w['py']} for w in words] + [{'vi': S[n][2], 'cn': S[n][0], 'py': S[n][1]} for n in TS_SENT]
SENT8 = [2,4,11,14,16,20,24,27]
FREE = [
(2,[['爱好'],['看书']]),(6,[['玩'],['电脑']]),(9,[['书法'],['正在']]),(11,[['让'],['爱好']]),
(16,[['感兴趣'],['京剧']]),(22,[['以前'],['书法']]),(24,[['自己'],['画儿']]),(25,[['下课'],['几点']])]
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
 ('<title>我们明天七点一刻出发 · Ôn tập Bài 21 — Mai 7h15 xuất phát</title>', '<title>我打算请老师教我京剧 · Ôn tập Bài 22 — Tôi định mời giáo viên dạy tôi kinh kịch</title>'),
 ('/* ===== Bài 21 ===== */', '/* ===== Bài 22 ===== */'),
 ('<small>Ôn tập · Bài 21</small>', '<small>Ôn tập · Bài 22</small>'),
 ('<span class="plate">第 21 课</span>ÔN TẬP BÀI 21', '<span class="plate">第 22 课</span>ÔN TẬP BÀI 22'),
 ('<span class="py">Wǒmen míngtiān qī diǎn yí kè chūfā</span>我们明天七点一刻出发', '<span class="py">Wǒ dǎsuàn qǐng lǎoshī jiāo wǒ jīngjù</span>我打算请老师教我京剧'),
 ('Ngày mai chúng ta xuất phát lúc 7h15 — Ôn tập Bài 21', 'Tôi định mời giáo viên dạy tôi kinh kịch — Ôn tập Bài 22'),
 ('Ôn <b>từ mới</b> (起床 半 一刻 差 出发 洗澡 睡觉 锻炼身体 操场 教室 爬山 集合 年级 上班 下班 准时 带 课间…), cách <b>nói giờ</b> 点 · 刻 · 半 · 差, và các đoạn nói về một ngày của bạn.', 'Ôn <b>từ mới</b> (爱好 京剧 电脑 玩 画儿 书法 唱 让 心情 大家 业余 喜欢 感兴趣 非常 特别 感到 愉快 以前 自己 下课 完…), mẫu câu <b>对…感兴趣</b>, <b>让</b>, kết quả bổ ngữ <b>完</b> và đoạn nói về sở thích của bạn.'),
 ('slide Bài 21', 'slide Bài 22'),
 ('<footer>MiaoChinese — 我们明天七点一刻出发 · Bài 21</footer>', '<footer>MiaoChinese — 我打算请老师教我京剧 · Bài 22</footer>'),
 ('LESSON:21', 'LESSON:22'),
]
for a, b in rp:
    assert a in s, a[:40]
    s = s.replace(a, b)
nw = len(words)
s = s.replace('id="pictureScore">0 / 22<', 'id="pictureScore">0 / %d<' % nimg).replace('id="pinyinScore">0 / 27<', 'id="pinyinScore">0 / %d<' % nw).replace('id="speakWordScore">0 / 27<', 'id="speakWordScore">0 / %d<' % nw)
left = [m for m in re.findall(r'.{30}Bài 21.{20}|.{20}bai21.{20}', s)]
print('còn sót:', left[:5])
open(os.path.join(ROOT, 'lessons/bai22.html'), 'w', encoding='utf-8').write(s)
print('ok', len(words), len(sb), len(fb), len(ts))
