/* MiaoChinese — nhớ tiến độ học viên + nhắc nhở / cổ vũ (trang bài ôn tập)
   Dùng dữ liệu đã gửi về Google Sheet (action=me) + bản lưu trên máy. Không cần sửa Apps Script. */
(function(){
  var KEY='mc_student_v1', PK='mc_prog_v1', DK='mc_days_v1', PASS=70;
  function lsget(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
  function lsset(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
  var tr=document.getElementById('mc-tracker'); if(!tr) return;
  var m=/SCRIPT_URL:'([^']+)'[^}]*LESSON:(\d+)/.exec(tr.textContent||''); if(!m) return;
  var SURL=m[1], LESSON=+m[2], who=null, scoreEls=[], best={}, toasted={}, timer=null, inited=false;

  /* ---------- giao diện ---------- */
  var css=document.createElement('style');
  css.textContent=
  '#mcToast{position:fixed;left:50%;bottom:64px;transform:translateX(-50%) translateY(20px);z-index:9998;max-width:min(92vw,460px);background:#111;color:#FFF8E8;border:2px solid #F4C542;border-radius:16px;padding:12px 16px;font:700 .92rem/1.45 Nunito,sans-serif;box-shadow:0 8px 28px rgba(0,0,0,.3);opacity:0;pointer-events:none;transition:.3s;text-align:center}'+
  '#mcToast.on{opacity:1;transform:translateX(-50%) translateY(0);pointer-events:auto}'+
  '#mcToast button{margin-top:8px;border:0;border-radius:10px;background:#F4C542;color:#111;font:800 .85rem Nunito,sans-serif;padding:7px 14px;cursor:pointer}'+
  '#mcResume{background:#FFF8E8;border:2px solid #F4C542;border-radius:16px;padding:14px 16px;margin:0 0 16px;font:600 .95rem/1.55 Nunito,sans-serif;color:#111;position:relative}'+
  '#mcResume b{font-weight:800}#mcResume .rb{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}'+
  '#mcResume button{border:0;border-radius:10px;font:800 .88rem Nunito,sans-serif;padding:9px 16px;cursor:pointer;background:#111;color:#F3E8C8}'+
  '#mcResume button.ghost{background:#fff;color:#111;border:1.5px solid #D9A520}'+
  '#mcResume .x{position:absolute;right:8px;top:6px;background:none;color:#7A5A06;padding:2px 8px;font-size:1.1rem}'+
  '#mcResume .pg{height:8px;border-radius:99px;background:#F3E8C8;overflow:hidden;margin-top:8px}#mcResume .pg i{display:block;height:100%;background:#D9A520;border-radius:99px}'+
  '.mc-tb{display:inline-block;margin-left:6px;font:800 .72rem Nunito,sans-serif;border-radius:99px;padding:1px 7px;background:#F3E8C8;color:#7A5A06}'+
  '.mc-tb.done{background:#1F7A3D;color:#fff}';
  document.head.appendChild(css);

  var toastEl, toastT;
  function toast(msg, btn){
    if(!toastEl){ toastEl=document.createElement('div'); toastEl.id='mcToast'; document.body.appendChild(toastEl); }
    toastEl.innerHTML=''; var s=document.createElement('div'); s.textContent=msg; toastEl.appendChild(s);
    if(btn){ var b=document.createElement('button'); b.textContent=btn.t; b.onclick=function(){ toastEl.classList.remove('on'); btn.f(); }; toastEl.appendChild(b); }
    toastEl.classList.add('on'); clearTimeout(toastT); toastT=setTimeout(function(){ toastEl.classList.remove('on'); }, btn?9000:5500);
  }

  /* ---------- dữ liệu ---------- */
  function pkey(){ return who.s.toLowerCase().replace(/\s+/g,' ')+'|'+who.c.toLowerCase().replace(/\s+/g,' '); }
  function loadLocal(){ try{ var all=JSON.parse(lsget(PK)||'{}'); return ((all[pkey()]||{})[LESSON])||{}; }catch(e){ return {}; } }
  function saveLocal(){ try{ var all=JSON.parse(lsget(PK)||'{}'); var u=all[pkey()]||(all[pkey()]={}); u[LESSON]=best; lsset(PK,JSON.stringify(all)); }catch(e){} }
  function merge(o){ for(var k in o){ if(o[k]>(best[k]||0)) best[k]=o[k]; } }
  function parse(el){ var r=(el.textContent||'').match(/(\d+)\s*\/\s*(\d+)/); return r?{a:+r[1],b:+r[2]}:null; }
  function panelOf(el){ return el.closest('[id^="panel-"]'); }
  function actOf(el){ return el.id.replace(/Score$/,''); }
  function tabLabel(id){ try{ for(var i=0;i<TAB_DEFS.length;i++) if(TAB_DEFS[i].id===id) return TAB_DEFS[i].label.replace(/&amp;/g,'&'); }catch(e){} return id; }
  function days(){ try{ return JSON.parse(lsget(DK)||'[]'); }catch(e){ return []; } }
  function today(){ return new Date(Date.now()+7*3600000).toISOString().slice(0,10); }
  function streak(){
    var d=days(), n=0, t=Date.parse(today()); 
    while(d.indexOf(new Date(t).toISOString().slice(0,10))>-1){ n++; t-=86400000; }
    return n;
  }
  function markToday(){ var d=days(), t=today(); if(d.indexOf(t)<0){ d.push(t); lsset(DK,JSON.stringify(d.slice(-60))); } }
  function firstName(){ var p=who.s.trim().split(/\s+/); return p[p.length-1]; }

  function tabs(){ // {tabId:{label,acts:[act..]}}
    var t={}, order=[];
    scoreEls.forEach(function(el){ var p=panelOf(el); if(!p) return; var id=p.id.replace(/^panel-/,''); if(!t[id]){ t[id]={id:id,label:tabLabel(id),acts:[]}; order.push(id); } t[id].acts.push(actOf(el)); });
    return order.map(function(i){ return t[i]; });
  }
  function status(tb){ var done=0,any=false; tb.acts.forEach(function(a){ if((best[a]||0)>=PASS) done++; if((best[a]||0)>0) any=true; }); return {done:done,total:tb.acts.length,any:any,full:done===tb.acts.length}; }
  function overall(){ var tl=tabs(), d=0,t=0; tl.forEach(function(x){ var s=status(x); d+=s.done; t+=s.total; }); return {done:d,total:t,tabs:tl}; }
  function nextTab(afterId){
    var tl=tabs(), start=0;
    if(afterId){ for(var i=0;i<tl.length;i++) if(tl[i].id===afterId) start=i+1; }
    for(var j=0;j<tl.length;j++){ var x=tl[(start+j)%tl.length]; if(!status(x).full) return x; }
    return null;
  }

  function badges(){
    tabs().forEach(function(tb){
      var btn=document.getElementById('tabbtn-'+tb.id); if(!btn) return;
      var b=btn.querySelector('.mc-tb'); if(!b){ b=document.createElement('span'); b.className='mc-tb'; btn.appendChild(b); }
      var s=status(tb);
      if(s.full){ b.className='mc-tb done'; b.textContent='✓'; }
      else if(s.any){ b.className='mc-tb'; b.textContent=s.done+'/'+s.total; }
      else b.style.display='none';
      if(s.full||s.any) b.style.display='';
    });
  }
  function go(id){ try{ switchPanel(id); }catch(e){} }

  function banner(){
    var old=document.getElementById('mcResume'); if(old) old.remove();
    var o=overall(); var any=o.tabs.some(function(t){ return status(t).any; });
    var wrap=document.querySelector('.wrap'); if(!wrap) return;
    var box=document.createElement('div'); box.id='mcResume';
    var x=document.createElement('button'); x.className='x'; x.textContent='×'; x.onclick=function(){ box.remove(); }; box.appendChild(x);
    var st=streak(), fire=st>=2?' 🔥 Bạn đã ôn '+st+' ngày liên tiếp!':'';
    var nt=nextTab();
    var p=document.createElement('div');
    if(!any){
      p.innerHTML='<b>Chào '+esc(firstName())+'! 👋</b> Bắt đầu ôn bài nào — làm từng phần theo thứ tự, hoặc chọn phần bạn thích.'+esc(fire);
      box.appendChild(p);
    } else if(nt){
      p.innerHTML='<b>Chào mừng '+esc(firstName())+' quay lại! 💛</b> Bài này bạn đã hoàn thành <b>'+o.done+'/'+o.total+'</b> phần. Tiếp tục với phần <b>«'+esc(nt.label)+'»</b> nhé!'+esc(fire);
      box.appendChild(p);
      var pg=document.createElement('div'); pg.className='pg'; pg.innerHTML='<i style="width:'+Math.round(o.done/o.total*100)+'%"></i>'; box.appendChild(pg);
      var rb=document.createElement('div'); rb.className='rb';
      var b1=document.createElement('button'); b1.textContent='▶ Tiếp tục phần này'; b1.onclick=function(){ go(nt.id); box.remove(); };
      var b2=document.createElement('button'); b2.className='ghost'; b2.textContent='Tự chọn phần khác'; b2.onclick=function(){ box.remove(); };
      rb.appendChild(b1); rb.appendChild(b2); box.appendChild(rb);
    } else {
      p.innerHTML='<b>🎉 Giỏi quá '+esc(firstName())+'!</b> Bạn đã hoàn thành tất cả các phần của bài này. Ôn lại thêm một lượt để nhớ lâu hơn, hoặc sang bài mới nhé!'+esc(fire);
      box.appendChild(p);
      var rb2=document.createElement('div'); rb2.className='rb';
      var b3=document.createElement('button'); b3.textContent='📚 Chọn bài khác'; b3.onclick=function(){ location.href='../index.html#level=1'; };
      var b4=document.createElement('button'); b4.className='ghost'; b4.textContent='Ôn lại bài này'; b4.onclick=function(){ box.remove(); };
      rb2.appendChild(b3); rb2.appendChild(b4); box.appendChild(rb2);
    }
    wrap.insertBefore(box, wrap.firstChild);
  }
  function esc(s){ return String(s).replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  /* ---------- theo dõi điểm ngay trên trang ---------- */
  function boxOf(el){ var bar=el.closest('.score-bar'); return (bar&&bar.nextElementSibling)||panelOf(el)||document.body; }
  function check(){
    timer=null; var changed=false;
    scoreEls.forEach(function(el){
      var p=parse(el); if(!p||!p.b) return;
      var cnt=boxOf(el).querySelectorAll('[data-answered="1"]').length;
      var id=actOf(el);
      if(p.a===0 && cnt===0){ delete toasted[id]; return; }
      var pct=Math.round(p.a/p.b*100);
      if(pct>(best[id]||0)){ best[id]=pct; changed=true; }
      var done=(cnt>=p.b)||(p.a>=p.b);
      if(done && toasted[id]!==pct){
        toasted[id]=pct;
        var tb=panelOf(el), tid=tb?tb.id.replace(/^panel-/,''):null, after=(overall().done===overall().total);
        var nt=nextTab(tid);
        if(after && pct>=PASS) toast('🏆 Tuyệt vời! Bạn đã hoàn thành TẤT CẢ các phần của bài này. Hãy tự hào về bản thân nhé!');
        else if(pct===100) toast('🌟 Hoàn hảo! Bạn làm đúng hết rồi!', nt&&nt.id!==tid?{t:'Sang phần «'+nt.label+'» ▶',f:function(){ go(nt.id); }}:null);
        else if(pct>=90) toast('👏 Tuyệt vời! Gần như tuyệt đối rồi!', nt&&nt.id!==tid?{t:'Sang phần «'+nt.label+'» ▶',f:function(){ go(nt.id); }}:null);
        else if(pct>=PASS) toast('🎉 Giỏi lắm! Bạn đã hoàn thành phần này!', nt&&nt.id!==tid?{t:'Sang phần «'+nt.label+'» ▶',f:function(){ go(nt.id); }}:null);
        else toast('💪 Cố lên '+firstName()+'! Bấm “Làm lại” để đạt điểm cao hơn nhé, bạn làm được mà!');
      }
    });
    if(changed){ saveLocal(); badges(); }
  }
  function schedule(){ if(timer) clearTimeout(timer); timer=setTimeout(check,1200); }

  function init(){
    if(inited) return; inited=true;
    try{ who=JSON.parse(lsget(KEY)||'null'); }catch(e){}
    if(!who||!who.s) return;
    scoreEls=[].slice.call(document.querySelectorAll('[id$="Score"]')).filter(function(e){ return parse(e); });
    if(!scoreEls.length) return;
    markToday();
    best=loadLocal(); badges(); banner();           // hiện ngay từ bản lưu trên máy
    fetch(SURL+'?'+new URLSearchParams({action:'me',student:who.s,cls:who.c}).toString()).then(function(r){ return r.json(); }).then(function(res){
      if(!res||!res.ok) return;
      var l=res.lessons&&res.lessons[LESSON];
      if(l&&l.best){ merge(l.best); saveLocal(); badges(); banner(); }
    }).catch(function(){});
    document.addEventListener('click',schedule,true);
    new MutationObserver(schedule).observe(document.body,{subtree:true,characterData:true,childList:true,attributes:true,attributeFilter:['data-answered']});
  }
  // chờ tới khi học viên đã đăng nhập xong (khung đăng nhập biến mất, thẻ tên hiện)
  var tries=0, iv=setInterval(function(){
    tries++;
    if(document.getElementById('mcChip') && !document.getElementById('mcOverlay')){ clearInterval(iv); setTimeout(init,300); }
    else if(tries>240) clearInterval(iv);
  },500);
})();
