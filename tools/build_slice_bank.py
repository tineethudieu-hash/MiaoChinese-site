#!/usr/bin/env python3
"""Tạo games/slice-bank.js (ngân hàng câu hỏi MIAO SLICE) từ FILL_BLANK của từng bài.
Mỗi câu: lấy CÂU + ĐÁP ÁN ĐÚNG từ bài học; 2 đáp án sai do người soạn duyệt tay (bảng CUR bên dưới)
sao cho chỉ MỘT đáp án đúng nếu chỉ đọc chữ Hán (game không hiện gợi ý tiếng Việt).
Câu không có trong CUR = bị loại (ghi trong tools/slice_report.txt).
Thêm bài mới: thêm 1 mục vào CUR theo mẫu  số_bài: {chỉ_số_câu: ('sai1','sai2'), ...}  rồi chạy lại script.
Sửa câu: sửa cặp đáp án sai trong CUR (hoặc sửa FILL_BLANK trong bài) rồi chạy lại. Kiểm tra thiếu dữ liệu: xem slice_report.txt."""
import re, json, glob, sys, os, random, unicodedata
S = ('很','太'); 
CUR = {
2:{0:('很','太'),1:('吗','男'),2:('吗','爸爸'),3:('吗','男'),4:('很','太')},
3:{0:('见','对'),1:('学','见'),2:('学','见'),3:('吗','对'),4:('去','见'),5:('银行','英语'),6:('邮局','银行'),7:('吗','对'),8:('六','钱')},
4:{0:('哪','谁'),1:('不','好'),3:('吗','那'),5:('二','五'),6:('再见','昨天'),7:('几','谁'),8:('几','不'),12:('谁','什么'),13:('吗','几')},
5:{0:('很','吗'),3:('谢','吗'),4:('工作','身体'),8:('很','吗'),10:('很忙','请坐'),11:('好久','请'),12:('老师','工作'),13:('忙','好'),14:('老师','工作')},
6:{0:('谁','那'),1:('国','书'),2:('哪','谁'),3:('学习','请问'),4:('叫','请问'),5:('哪','谁'),6:('谁','哪'),7:('哪','那'),8:('学习','朋友'),9:('杂志','名字'),10:('朋友','叫'),11:('学习','叫'),12:('学习','叫'),13:('叫','哪'),14:('汉字','杂志'),15:('哪','叫'),16:('杂志','叫')},
9:{0:('美元','漂亮'),1:('人民币','热情'),2:('美元','漂亮'),4:('先生','漂亮'),5:('先生','漂亮'),6:('一百','一万'),7:('一会儿','漂亮'),8:('美元','银行'),9:('银行','美元'),10:('银行','美元'),11:('银行','美元'),12:('漂亮','热情'),13:('美元','漂亮'),14:('数','换')},
10:{0:('谁','哪儿'),1:('找','住'),2:('找','是'),4:('谁','什么'),5:('是','找'),6:('谁','哪儿'),7:('办公','住'),8:('办公','职员'),10:('房间','手机')},
11:{0:('也','都'),1:('很','吗'),2:('很','吗'),3:('很','吗'),4:('介绍','欢迎'),5:('都','先'),6:('韩国人','教授'),8:('韩国人','留学生'),9:('很','吗'),12:('介绍','欢迎'),13:('介绍','欢迎'),14:('韩国人','教授'),15:('很','吗')},
12:{0:('给','的'),1:('同屋','语法'),2:('语言','文学'),3:('语法','经济'),4:('同学','比较'),5:('但是','的'),6:('但是','说'),7:('的','给'),8:('大学','同屋'),9:('同屋','语法'),10:('同屋','语法'),11:('旧','班'),12:('在','比较'),13:('在','但是'),14:('在','比较'),15:('班','语言')},
13:{0:('瓶','本'),1:('把','本'),2:('瓶','把'),3:('瓶','位'),4:('瓶','位'),5:('瓶','把'),6:('支','瓶'),7:('把','位'),8:('瓶','位'),10:('轻','黑'),13:('雨伞','茶叶'),14:('光盘','词典'),15:('雨伞','椅子'),18:('词典','香水'),20:('衣服','词典')},
17:{0:('挤','远'),1:('课','事'),2:('听力','口语'),3:('录音','出来'),4:('录音','出来'),5:('书店','出来'),6:('书店','出来'),7:('书店','出来'),8:('挤','远'),9:('书店','出来'),10:('挤','事'),11:('书店','录音'),12:('书店','录音'),13:('教','问'),14:('书店','录音')},
18:{0:('翻译','旅行'),1:('参观','旅行'),2:('当','坐'),3:('代表','花'),4:('代表','花'),5:('参观','旅行'),6:('当','坐'),7:('坐','当'),8:('顺便','花'),9:('给','当'),10:('寄','用'),11:('翻译','回来'),12:('旅行','回来'),13:('参观','旅行'),14:('顺便','翻译')},
19:{0:('打折','好看'),1:('很','吗'),2:('瘦','长'),3:('浅','长'),4:('打折','合适'),5:('也','还'),6:('一下','一些'),7:('不','有'),8:('一下','一些'),9:('有点儿','点儿'),10:('和','也'),11:('打折','合适'),12:('打折','试衣服'),13:('卖','买'),14:('什么','几'),15:('什么','几'),16:('怎么样','几'),17:('什么','几'),18:('怎么样','几'),19:('什么','几'),20:('怎么样','几'),21:('展览','机场'),22:('冬天','听说')},
20:{0:('什么','哪儿'),1:('参加','打算'),2:('打算','快乐'),3:('快乐','号'),4:('快乐','毕业'),5:('毕业','属'),6:('毕业','快乐'),7:('参加','毕业'),8:('毕业','快乐'),9:('属','去'),11:('明年','后年'),12:('过','参加'),13:('正好','毕业'),14:('礼物','蛋糕'),15:('生日','春节')},
21:{0:('半','差'),1:('半','差'),2:('差','分'),3:('半','每'),4:('刻','半'),5:('刻','差'),6:('起床','睡觉'),7:('准时','以后'),8:('年级','然后'),9:('操场','年级'),10:('上','洗'),11:('带','洗澡'),12:('以前','每'),13:('以前','然后'),14:('刻','年级'),15:('教室','操场')},
22:{0:('让','以前'),1:('对','让'),2:('对','喜欢'),3:('让','对'),4:('业余','自己'),5:('业余','自己'),6:('让','对'),8:('大家','自己'),9:('让','完'),10:('唱','让'),11:('书法','京剧'),12:('业余','爱好'),13:('大家','让'),14:('让','对'),15:('让','对'),16:('爱好','业余'),17:('爱好','业余'),19:('唱','让'),20:('演出','比赛'),21:('笔记本','足球'),22:('惊讶','笔记本'),23:('希望','惊讶'),24:('惊讶','笔记本'),25:('惊讶','笔记本'),26:('惊讶','希望'),27:('惊讶','演出')},
}
GRAM={'吗','很','太','不','没有','的','给','在','又','点儿','还是','怎么','怎么样','几','什么','哪','哪儿','谁','也','都','先','然后','以前','以后','比较','但是','替','用','坐','当','呢','位','一下儿','有点儿','一点儿','一下','一些','刻','半','差','每','没','有'}
def han_len(t): return len(re.findall(r'[\u4e00-\u9fff]',t))
def ftype(ans,before,after):
    if ans in GRAM: return 'nguphap'
    if han_len(before+ans+after)<=6: return 'ghepcum'
    return 'dienkhuyet'
dec=json.JSONDecoder()
def getc(s,name):
    m=re.search(r'const '+name+r'\s*=\s*',s)
    if not m: return None
    try: return dec.raw_decode(s[m.end():])[0]
    except Exception: return None
def toneless(p):
    return ''.join(c for c in unicodedata.normalize('NFD',p) if unicodedata.category(c)!='Mn').replace(' ','').lower()
def level_of(n): return 1 if n<=15 else 2
bank=[]; rep=[]
files=sorted(glob.glob('lessons/bai*.html'),key=lambda f:int(re.findall(r'\d+',f)[0]))
for f in files:
    n=int(re.findall(r'\d+',f)[0]); s=open(f,encoding='utf-8').read()
    m=re.search(r'const FILL_BLANK\s*=\s*(\[.*?\n?\]);',s,re.S)
    fb=json.loads(m.group(1)) if m else []
    cur=CUR.get(n,{}); kept=0
    if not fb: rep.append(f'Bài {n}: chưa có dữ liệu điền khuyết')
    for i,x in enumerate(fb):
        o=x['options']; ans=o[x['a']]; tag=f'b{n}-q{i+1:02d}'
        if i not in cur:
            rep.append(f'{tag} LOẠI: {x["before"]}[{ans}]{x["after"]}  (không chắc chỉ có 1 đáp án đúng khi chỉ đọc chữ Hán / đáp án pinyin / cần gợi ý tiếng Việt)'); continue
        d=list(cur[i])
        ok = len(d)==2 and d[0]!=d[1] and ans not in d and all(re.search(re.escape(w),s) for w in d)
        if not ok: rep.append(f'{tag} LỖI dữ liệu đáp án sai {d}'); sys.exit('bad '+tag)
        bank.append({'id':tag,'lesson':n,'level':level_of(n),'type':ftype(ans,x['before'],x['after']),'prompt':x['before']+'____'+x['after'],
          'correctAnswer':ans,'distractors':d,'completedText':x['before']+ans+x['after'],'optLang':'han','source':f'lessons/bai{n}.html FILL_BLANK #{i+1}'})
        kept+=1
    if fb: rep.append(f'Bài {n}: {kept}/{len(fb)} câu điền khuyết/ngữ pháp/cụm từ dùng được')
    # ----- các dạng theo từ vựng / câu dịch -----
    W=getc(s,'WORDS') or []; T=getc(s,'TRANSLATE_SELFCHECK') or []
    rnd=random.Random(1000+n)
    vis=[w['vi'].strip().lower() for w in W]
    cnt={}
    def add(q): bank.append(q); cnt[q['type']]=cnt.get(q['type'],0)+1
    for i,w in enumerate(W):
        vl=w['vi'].strip().lower()
        if vis.count(vl)>1: rep.append(f'b{n}-w{i+1:02d} LOẠI các dạng từ vựng: nghĩa "{w["vi"]}" trùng với từ khác'); continue
        others=[o for o in W if o['cn']!=w['cn'] and o['vi'].strip().lower()!=vl]
        # nghĩa: khác nghĩa, không chứa nhau
        c1=[o for o in others if vl not in o['vi'].lower() and o['vi'].lower() not in vl and vis.count(o['vi'].strip().lower())==1]
        if len(c1)>=2:
            d=rnd.sample(c1,2)
            add({'id':f'b{n}-w{i+1:02d}-m','lesson':n,'level':level_of(n),'type':'chonnghia','prompt':w['cn'],'correctAnswer':w['vi'],'distractors':[x['vi'] for x in d],'optLang':'vi','completedText':w['cn']+' = '+w['vi'],'source':f'lessons/bai{n}.html WORDS #{i+1}'})
        # đáp án chữ Hán: khác nghĩa, không chung chữ, phiên âm không dấu khác
        c2=[o for o in others if not set(o['cn'])&set(w['cn']) and toneless(o['py'])!=toneless(w['py']) and vis.count(o['vi'].strip().lower())==1 and o['cn'] not in w['cn'] and w['cn'] not in o['cn'] and not (w.get('grp') and o.get('grp')==w.get('grp'))]
        if len(c2)>=2:
            d=rnd.sample(c2,2); full=w['cn']+' ('+w['py']+') = '+w['vi']
            if w.get('img') and os.path.exists(os.path.normpath(os.path.join('lessons',w['img']))):
                add({'id':f'b{n}-w{i+1:02d}-h','lesson':n,'level':level_of(n),'type':'hinh','img':w['img'],'prompt':'','correctAnswer':w['cn'],'distractors':[x['cn'] for x in d],'optLang':'han','completedText':full,'source':f'lessons/bai{n}.html WORDS #{i+1}'})
            add({'id':f'b{n}-w{i+1:02d}-n','lesson':n,'level':level_of(n),'type':'nghe','audio':w['cn'],'prompt':'','correctAnswer':w['cn'],'distractors':[x['cn'] for x in d],'optLang':'han','completedText':full,'source':f'lessons/bai{n}.html WORDS #{i+1}'})
    sents=[t for t in T if re.search('[。！？]',t['cn'])]
    if len(sents)>=3:
        for i,t in enumerate(sents):
            al=t.get('alt') or []; al=[a['cn'] if isinstance(a,dict) else a for a in (al if isinstance(al,list) else [al])]
            forb={t['cn']}|set(al)|{re.sub('[。！？]','',t['cn'])}
            c=[o for o in sents if o['cn'] not in forb and o['vi'].strip().lower()!=t['vi'].strip().lower()]
            if len(c)<2: continue
            d=rnd.sample(c,2)
            add({'id':f'b{n}-s{i+1:02d}','lesson':n,'level':level_of(n),'type':'chondungcau','prompt':t['vi'],'correctAnswer':t['cn'],'distractors':[x['cn'] for x in d],'optLang':'han','completedText':t['cn']+' = '+t['vi'],'source':f'lessons/bai{n}.html TRANSLATE_SELFCHECK #{i+1}'})
    else: rep.append(f'Bài {n}: dưới 3 câu dịch → không có dạng "Chọn câu đúng"')
    rep.append(f'Bài {n}: thêm '+', '.join(f'{k}={v}' for k,v in sorted(cnt.items())))
open('games/slice-bank.js','w',encoding='utf-8').write('/* MIAO SLICE – ngân hàng câu hỏi (tạo bởi tools/build_slice_bank.py, đừng sửa tay) */\nwindow.SLICE_BANK = '+json.dumps(bank,ensure_ascii=False,indent=0)+';\n')
open('tools/slice_report.txt','w',encoding='utf-8').write('\n'.join(rep)+'\n')
print('\n'.join(r for r in rep if r.startswith('Bài')), len(bank))
