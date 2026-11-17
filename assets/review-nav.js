/* MiaoChinese – bộ chọn "Dạng ôn tập" + bảng "Tùy chọn" cho trang Ôn tập.
   Một nguồn dữ liệu (TAB_DEFS của từng bài) cho cả bottom sheet (màn hẹp) và dropdown (đủ rộng).
   Không đổi logic bài tập: chỉ gọi lại switchPanel() có sẵn; công tắc Pinyin/Việt vẫn là class trên <body>. */
(function(){
  if(window.__nvInit) return; window.__nvInit=1;
  var $=function(id){return document.getElementById(id)};
  var defs; try{defs=TAB_DEFS}catch(e){return}
  var ICONS={match:'🃏',picture:'🖼️',pinyin:'🔤',sentence:'🧩',speak:'🎤'};
  var acts=defs.map(function(t){var l=String(t.label).replace(/&amp;/g,'&'),i=l.indexOf(' ');return {id:t.id,zh:i>0?l.slice(0,i):'',vi:i>0?l.slice(i+1):l,ic:ICONS[t.id]||'📘'}});
  var btnAct=$('nvAct'),btnOpt=$('nvOpt');if(!btnAct)return;
  var mq=window.matchMedia('(min-width:700px)');
  var cur=null,opened=null,opener=null,back=null,pop=null;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function actById(id){for(var i=0;i<acts.length;i++)if(acts[i].id===id)return acts[i];return null}

  /* ----- tiến độ: số liệu hiện có của từng hoạt động ----- */
  function progress(id){
    var a=0,b=0,done=false;
    if(id==='match'){try{a=memState.matched||0;b=memState.total||0}catch(e){}}
    var p=$('panel-'+id);
    if(p&&id!=='match'){[].forEach.call(p.querySelectorAll('[id$="Score"]'),function(el){var m=(el.textContent||'').match(/(\d+)\s*\/\s*(\d+)/);if(m){a+=+m[1];b+=+m[2]}})}
    var tb=$('tabbtn-'+id),badge=tb&&tb.querySelector('.mc-tb');
    if(badge&&badge.textContent.trim()==='✓'&&badge.style.display!=='none')done=true;
    if(b>0&&a>=b)done=true;
    return {a:a,b:b,done:done};
  }
  function pgHtml(id){var p=progress(id);if(p.done)return '<span class="pg done">Đã hoàn thành</span>';if(p.b>0)return '<span class="pg">'+p.a+'/'+p.b+'</span>';return ''}

  /* ----- nút hiện tại ----- */
  function setCurrent(id){
    cur=id;var a=actById(id);if(!a)return;
    btnAct.innerHTML='<span class="nv-ico" aria-hidden="true">'+a.ic+'</span><span class="nv-lbl"><span class="nv-cap">Dạng ôn tập</span>'+esc(a.vi)+'</span><span class="nv-chev" aria-hidden="true">▾</span>';
    btnAct.setAttribute('aria-label','Dạng ôn tập: '+a.vi+'. Bấm để đổi');
  }

  /* ----- công tắc Pinyin / tiếng Việt (class trên body, như trước) ----- */
  var TG=[{cls:'pinyin-hidden',zh:'拼音',name:'Pinyin',sub:'Hiện pinyin trên chữ Hán'},{cls:'meaning-hidden',zh:'VI',name:'Nghĩa tiếng Việt',sub:'Hiện nghĩa tiếng Việt'}];
  function tgOn(cls){return !document.body.classList.contains(cls)}
  function toggle(cls){document.body.classList.toggle(cls);syncTg()}
  function syncTg(){
    TG.forEach(function(t,i){
      var on=tgOn(t.cls),b=$('nvTg'+i);
      if(b){b.classList.toggle('off',!on);b.setAttribute('aria-pressed',on?'true':'false');b.innerHTML=esc(t.zh)+' <span class="st">'+(on?'Bật':'Tắt')+'</span>';b.setAttribute('aria-label',t.name+': '+(on?'đang bật':'đang tắt'))}
    });
    if(opened==='opt'&&pop)[].forEach.call(pop.querySelectorAll('.nv-opt'),function(el,i){var on=tgOn(TG[i].cls);el.setAttribute('aria-checked',on?'true':'false');el.querySelector('.stt').textContent=on?'Bật':'Tắt'});
  }

  /* ----- mở / đóng (chỉ một bảng mở tại một thời điểm) ----- */
  function ensure(){
    if(back)return;
    back=document.createElement('div');back.className='nv-back';back.addEventListener('click',function(){close(true)});
    pop=document.createElement('div');pop.className='nv-pop';pop.addEventListener('keydown',onKey);
    document.body.appendChild(back);document.body.appendChild(pop);
  }
  function place(){
    if(!pop||!pop.classList.contains('drop')||!opener)return;
    var r=opener.getBoundingClientRect(),w=pop.offsetWidth,left=Math.max(10,Math.min(r.left,window.innerWidth-w-10));
    pop.style.left=left+'px';pop.style.top=(r.bottom+6)+'px';pop.style.right='auto';pop.style.bottom='auto';
  }
  function open(kind,from){
    if(opened)close(false);
    ensure();opened=kind;opener=from;openW=window.innerWidth;
    var sheet=!mq.matches;
    pop.className='nv-pop show '+(sheet?'sheet':'drop');pop.removeAttribute('style');
    var title=kind==='act'?'Chọn dạng ôn tập':'Tùy chọn';
    pop.setAttribute('role','dialog');pop.setAttribute('aria-label',title);if(sheet)pop.setAttribute('aria-modal','true');else pop.removeAttribute('aria-modal');
    var h='<div class="nv-hd"><h2 class="nv-ttl">'+title+'</h2><button type="button" class="nv-x" aria-label="Đóng">✕</button></div>';
    if(kind==='act'){
      h+='<div class="nv-list" role="listbox" aria-label="Dạng ôn tập">'+acts.map(function(a){
        var sel=a.id===cur;
        return '<button type="button" class="nv-row" role="option" data-id="'+a.id+'" aria-selected="'+sel+'" tabindex="'+(sel?0:-1)+'"><span class="ic" aria-hidden="true">'+a.ic+'</span><span class="tx"><span class="vi">'+esc(a.vi)+'</span><span class="zh">'+esc(a.zh)+'</span></span>'+pgHtml(a.id)+'<span class="ck" aria-hidden="true">✓</span></button>'}).join('')+'</div>';
    }else{
      h+='<div class="nv-list">'+TG.map(function(t,i){var on=tgOn(t.cls);
        return '<button type="button" class="nv-opt" role="switch" data-i="'+i+'" aria-checked="'+on+'"><span class="tx"><b>'+esc(t.name)+' <span lang="zh">'+esc(t.zh==='VI'?'':t.zh)+'</span></b><span>'+esc(t.sub)+'</span></span><span class="stt">'+(on?'Bật':'Tắt')+'</span><span class="nv-sw" aria-hidden="true"></span></button>'}).join('')+'</div>';
    }
    pop.innerHTML=h;
    pop.querySelector('.nv-x').addEventListener('click',function(){close(true)});
    [].forEach.call(pop.querySelectorAll('.nv-row'),function(b){b.addEventListener('click',function(){choose(b.dataset.id)})});
    [].forEach.call(pop.querySelectorAll('.nv-opt'),function(b){b.addEventListener('click',function(){toggle(TG[+b.dataset.i].cls)})});
    if(sheet){back.classList.add('show');document.body.classList.add('nv-lock')}
    from.setAttribute('aria-expanded','true');
    place();
    var f=pop.querySelector('.nv-row[aria-selected="true"]')||pop.querySelector('.nv-opt')||pop.querySelector('.nv-x');
    if(f)f.focus({preventScroll:true});
  }
  function close(restore){
    if(!opened)return;
    var o=opener;opened=null;
    if(pop)pop.className='nv-pop';if(back)back.classList.remove('show');
    document.body.classList.remove('nv-lock');
    if(o){o.setAttribute('aria-expanded','false');if(restore)o.focus({preventScroll:true})}
    opener=null;
  }
  function choose(id){
    close(true);
    try{switchPanel(id)}catch(e){}
  }
  function onKey(e){
    var k=e.key;
    if(k==='Escape'){e.preventDefault();e.stopPropagation();close(true);return}
    var rows=[].slice.call(pop.querySelectorAll('.nv-row,.nv-opt'));
    if(rows.length&&(k==='ArrowDown'||k==='ArrowUp'||k==='Home'||k==='End')){
      e.preventDefault();var i=rows.indexOf(document.activeElement);
      i=k==='Home'?0:k==='End'?rows.length-1:k==='ArrowDown'?(i+1)%rows.length:(i-1+rows.length)%rows.length;
      rows.forEach(function(r){if(r.classList.contains('nv-row'))r.tabIndex=-1});rows[i].tabIndex=0;rows[i].focus({preventScroll:true});return;
    }
    if(k==='Tab'){
      if(pop.classList.contains('drop')){close(false);return}
      var f=[].slice.call(pop.querySelectorAll('button')),first=f[0],last=f[f.length-1];
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}
    }
  }
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&opened){close(true)}});
  document.addEventListener('pointerdown',function(e){
    if(!opened||!pop)return;
    if(pop.contains(e.target)||(opener&&opener.contains(e.target)))return;
    close(e.target===back);
  },true);
  var openW=0;window.addEventListener('resize',function(){if(opened&&window.innerWidth!==openW)close(false);else if(opened)place()});
  if(mq.addEventListener)mq.addEventListener('change',function(){if(opened)close(false)});

  btnAct.addEventListener('click',function(){if(opened==='act')close(true);else open('act',btnAct)});
  if(btnOpt)btnOpt.addEventListener('click',function(){if(opened==='opt')close(true);else open('opt',btnOpt)});
  TG.forEach(function(t,i){var b=$('nvTg'+i);if(b)b.addEventListener('click',function(){toggle(t.cls)})});

  /* móc vào switchPanel có sẵn để nút luôn đúng, kể cả khi trang/tiện ích khác gọi nó */
  var sp=window.switchPanel;
  if(typeof sp==='function'){window.switchPanel=function(id){var r=sp.apply(this,arguments);setCurrent(id);return r}}
  var act=document.querySelector('.panel.active');
  setCurrent(act?act.id.replace(/^panel-/,''):acts[0].id);
  syncTg();
})();
