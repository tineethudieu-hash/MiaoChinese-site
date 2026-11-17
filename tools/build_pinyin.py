#!/usr/bin/env python3
"""Tạo games/pinyin-l1.js: bảng chữ Hán -> pinyin cho mọi chuỗi xuất hiện trong câu hỏi Level 1 của game.
Nguồn: WORDS + TRANSLATE_SELFCHECK trong các bài (pinyin do cô soạn) + bảng MANUAL bên dưới cho chữ chưa có.
Ghép theo từ dài nhất; quy tắc biến điệu 不/一 áp dụng cho chữ đơn. Chữ thiếu dữ liệu in ra khi chạy (MISSING)."""
import re, json, glob, itertools, unicodedata, sys
dec=json.JSONDecoder()
def getc(s,name):
    m=re.search(r'const '+name+r'\s*=\s*',s)
    if not m: return None
    try: return dec.raw_decode(s[m.end():])[0]
    except Exception: return None
HAN=re.compile(r'[一-鿿]')
INIT=['','b','p','m','f','d','t','n','l','g','k','h','j','q','x','zh','ch','sh','r','z','c','s','y','w']
FIN=['a','o','e','ai','ei','ao','ou','an','en','ang','eng','ong','er','i','ia','ie','iao','iu','ian','in','iang','ing','iong','u','ua','uo','uai','ui','uan','un','uang','ueng','ü','üe','üan','ün','ê']
def strip(p): return ''.join(c for c in unicodedata.normalize('NFD',p) if unicodedata.category(c)!='Mn').lower().replace('ü','u').replace('v','u')
SYL=set()
for i,f in itertools.product(INIT,FIN): SYL.add(strip(i+f))
SYL|={'yi','you','yan','yin','ying','yong','wu','wo','wei','wen','weng','wai','wan','wang','ye','yue','yuan','yun','yu','ya','yao','yang','ju','qu','xu','lü','lv','nv','nü','er','r','n','ng','hm','m','dei','nei','lei','shei','de','zhei','ei','o'}
def split_syl(p,n):
    p=unicodedata.normalize('NFC',p).replace(' ','').replace("'",'')
    res=[]
    def rec(i,acc):
        if len(acc)==n: 
            if i==len(p): res.append(list(acc))
            return
        for j in range(i+1,min(len(p),i+7)+1):
            if strip(p[i:j]) in SYL:
                rec(j,acc+[p[i:j]])
                if res: return
    rec(0,[]); return res[0] if res else None
words={}   # cn -> py (không dấu cách)
def addw(cn,py):
    cn=cn.strip(); py=py.strip()
    if not cn or not py or not all(HAN.match(c) or c in '，。？！、' for c in cn): return
    if re.search(r'[^\w\sāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüêĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ\'\-]',py): return
    words.setdefault(cn,py.replace(' ',''))
files=sorted(glob.glob('lessons/bai*.html'))
for f in files:
    s=open(f,encoding='utf-8').read()
    for w in (getc(s,'WORDS') or []): addw(w['cn'],w['py'])
    for w in (getc(s,'TRANSLATE_SELFCHECK') or []):
        if isinstance(w,dict) and 'cn' in w and 'py' in w: addw(w['cn'],w['py'])
MANUAL=json.load(open('tools/pinyin_manual.json',encoding='utf-8')) if glob.glob('tools/pinyin_manual.json') else {}
for k,v in MANUAL.items(): words[k]=v
# bảng chữ đơn suy ra từ từ nhiều chữ (khi tách âm tiết khớp số chữ)
chars={}
for cn,py in list(words.items()):
    if len(cn)==1: chars.setdefault(cn,py); continue
    if not all(HAN.match(c) for c in cn): continue
    sy=split_syl(py,len(cn))
    if sy:
        for c,p in zip(cn,sy): chars.setdefault(c,p)
# chữ đơn có nhiều âm: ưu tiên mục chữ đơn trực tiếp
for cn,py in words.items():
    if len(cn)==1: chars[cn]=py
bank=open('games/slice-bank.js',encoding='utf-8').read()
bank=json.loads(bank[bank.index('['):bank.rindex(']')+1])
texts=set()
for q in bank:
    if q['level']!=1: continue
    for t in [q.get('prompt','')]+q['prompt'].split('____') if q.get('prompt') else []: texts.add(t)
    texts.add(q['correctAnswer']);texts.update(q['distractors'])
    for part in re.split(r'\s*[\(=]\s*',q['completedText'])[:1]: texts.add(part)
    if q.get('audio'): texts.add(q['audio'])
texts={t for t in texts if t and HAN.search(t)}
def tone_of(p):
    for c in unicodedata.normalize('NFD',p):
        if c=='̄':return 1
        if c=='́':return 2
        if c=='̌':return 3
        if c=='̀':return 4
    return 0
LONG=max(map(len,words))
missing={}
def conv(t):
    toks=[];i=0
    while i<len(t):
        ch=t[i]
        if not HAN.match(ch):
            toks.append(['P',ch]);i+=1;continue
        for L in range(min(LONG,len(t)-i),0,-1):
            seg=t[i:i+L]
            if seg in words and not (L==1 and False): toks.append(['W',words[seg],seg]);i+=L;break
            if L==1:
                if seg in chars: toks.append(['W',chars[seg],seg])
                else: missing[seg]=t; toks.append(['W','?',seg])
                i+=1
    # biến điệu 不 / 一 (chữ đơn)
    for k,tk in enumerate(toks):
        if tk[0]!='W' or len(tk[2])!=1: continue
        nxt=next((x for x in toks[k+1:] if x[0]=='W'),None)
        nt=tone_of(nxt[1]) if nxt else 0
        if tk[2]=='不' and tk[1]=='bù' and nt==4: tk[1]='bú'
        if tk[2]=='一' and tk[1]=='yī' and nxt:
            prev=toks[k-1][2] if k and toks[k-1][0]=='W' else ''
            if prev in ('星期','月','号','第','十','二','三','四','五','六','七','八','九'): continue
            tk[1]={4:'yí',1:'yì',2:'yì',3:'yì'}.get(nt,'yī')
    out='';pend=False
    for tk in toks:
        if tk[0]=='P': out+=tk[1]; pend=tk[1] in '，。？！、,.?!'
        else:
            if tk[1]=='r': out+='r'; continue
            if out and not out.endswith(' ') : out+=' '
            out+=tk[1]
    return out.strip()
res={t:conv(t) for t in sorted(texts)}
if missing:
    print('MISSING',len(missing)); print(json.dumps({k:v for k,v in missing.items()},ensure_ascii=False))
open('games/pinyin-l1.js','w',encoding='utf-8').write('/* Tự tạo bởi tools/build_pinyin.py — đừng sửa tay */\nwindow.PINYIN_L1='+json.dumps(res,ensure_ascii=False,separators=(',',':'))+';\n')
print('entries',len(res),'words',len(words),'chars',len(chars))
