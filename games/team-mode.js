/* MiaoChinese – chế độ "Thi đấu theo đội · 1 thiết bị" dùng chung cho MIAO TILT và MIAO SLICE.
   - Danh sách lớp lấy từ chính máy chủ của website (Apps Script, action=report) bằng PIN giáo viên – không có endpoint mới.
   - Phần LOGIC (chia đội, xếp lượt, bốc câu, tính điểm) là hàm thuần, kiểm thử được bằng Node: TeamMode.logic
   - Phần GIAO DIỆN (bảng cài đặt, bảng điểm, màn đổi người, kết quả) trả về HTML; game chủ gắn vào trang. */
(function(root){
'use strict';
var TEAM_DEF=[
  {name:'Rồng',emoji:'🐲',color:'#E0402F'},
  {name:'Hổ',emoji:'🐯',color:'#F28C1B'},
  {name:'Gấu trúc',emoji:'🐼',color:'#2F6FDE'},
  {name:'Cáo',emoji:'🦊',color:'#2FA84F'}
];
var POINTS={normal:10,double:20,bet:10,betChoices:[0,5]};
var LAST_CLS_KEY='miaochinese_team_lastcls_v1',HIST_KEY='miaochinese_team_v1';

function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function shuffle(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t}return a}
function norm(s){return String(s==null?'':s).normalize('NFC').trim().replace(/\s+/g,' ')}

/* ================= LOGIC ================= */
/* Học sinh nghỉ học (Trạng thái "Nghỉ"…) không vào danh sách thi đấu; người "ngoài danh sách" cũng bỏ. */
function isInactive(status){return /ngh[iỉ]|thôi|bảo lưu|dừng/i.test(norm(status).toLowerCase())}
/* Sổ điểm hiện tại KHÔNG có cột ID/email, nên ID suy ra = lớp|tên|số thứ tự bản trùng tên (theo thứ tự trong danh sách). */
function buildRoster(students){
  var classes={},seen={};
  (students||[]).forEach(function(s){
    if(!s||s.inRoster===false)return;
    var name=norm(s.student),cls=norm(s.cls);if(!name||!cls)return;
    if(isInactive(s.status))return;
    var key=cls+'|'+name.toLowerCase();seen[key]=(seen[key]||0)+1;
    (classes[cls]=classes[cls]||[]).push({id:cls+'|'+name+'|'+seen[key],name:name,cls:cls,group:norm(s.group),k:seen[key],allowed:s.allowed});
  });
  Object.keys(classes).forEach(function(c){
    var cnt={};classes[c].forEach(function(m){var k=m.name.toLowerCase();cnt[k]=(cnt[k]||0)+1});
    classes[c].forEach(function(m){m.dup=cnt[m.name.toLowerCase()]>1;m.disp=m.dup?m.name+' ('+m.k+')':m.name});
  });
  return classes;
}
function classAllowed(members){var a=0;(members||[]).forEach(function(m){if(typeof m.allowed==='number'&&m.allowed>a)a=m.allowed});return a}
/* Chia đội cân bằng: xáo trộn, rải theo nhóm, chia vòng tròn -> chênh lệch tối đa 1 người. */
function autoSplit(ids,groupOf,n){
  var teams=[];for(var i=0;i<n;i++)teams.push([]);
  var byG={};shuffle(ids).forEach(function(id){var g=(groupOf&&groupOf[id])||'';(byG[g]=byG[g]||[]).push(id)});
  var order=[];Object.keys(byG).sort().forEach(function(g){order=order.concat(byG[g])});
  /* bắt đầu từ đội đang ít người nhất để các nhóm cũng đều */
  order.forEach(function(id){var k=0;for(var t=1;t<n;t++)if(teams[t].length<teams[k].length)k=t;teams[k].push(id)});
  return teams;
}
function maxN(n){return Math.max(0,Math.min(4,n))}
function fold(x){return norm(x).toLowerCase().replace(/đ/g,'d').normalize('NFD').replace(/[\u0300-\u036f]/g,'')}
function flatten(classes){var a=[];Object.keys(classes).sort().forEach(function(c){a=a.concat(classes[c])});return a}
/* Tìm không dấu: mọi từ trong ô tìm phải có trong tên. */
function searchStudents(all,q,limit){
  var w=fold(q).split(' ').filter(Boolean);if(!w.length)return [];
  return all.filter(function(m){var f=m._f||(m._f=fold(m.name));return w.every(function(x){return f.indexOf(x)>=0})}).slice(0,limit||30);
}
/* Tên hiển thị trên màn chiếu: chỉ tên; nếu trùng tên trong trận thì thêm lớp (và số nếu vẫn trùng). Không email/tài khoản. */
function displayNames(members){
  var cnt={};members.forEach(function(m){var k=m.name.toLowerCase();cnt[k]=(cnt[k]||0)+1});
  var out={},seen={};
  members.forEach(function(m){
    var k=m.name.toLowerCase();if(cnt[k]<2){out[m.id]=m.name;return}
    var k2=k+'|'+m.cls.toLowerCase();seen[k2]=(seen[k2]||0)+1;
    var same=members.filter(function(x){return x.name.toLowerCase()===k&&x.cls.toLowerCase()===m.cls.toLowerCase()}).length;
    out[m.id]=m.name+' ('+m.cls+(same>1?' #'+seen[k2]:'')+')';
  });
  return out;
}
/* Bốc câu: mỗi vòng, mọi đội nhận câu KHÁC nhau nhưng CÙNG dạng + CÙNG level. */
function drawRounds(pool,nRounds,nTeams){
  var byType={};pool.forEach(function(q){(byType[q.type]=byType[q.type]||[]).push(q)});
  var types=shuffle(Object.keys(byType)),used={},out=[],tp=0;
  function pick(allowReuse){
    for(var k=0;k<types.length;k++){
      var t=types[(tp+k)%types.length];
      var cand=byType[t].filter(function(q){return allowReuse||!used[q.id]});
      var byLv={};cand.forEach(function(q){(byLv[q.level]=byLv[q.level]||[]).push(q)});
      var lv=Object.keys(byLv).filter(function(l){return byLv[l].length>=nTeams});
      if(lv.length){tp=(tp+k+1)%types.length;return shuffle(byLv[shuffle(lv)[0]]).slice(0,nTeams)}
    }
    return null;
  }
  for(var r=0;r<nRounds;r++){
    var p=pick(false);
    if(!p){used={};p=pick(false)}                 /* hết câu mới -> bốc lại từ đầu (vẫn cùng dạng/level) */
    if(!p){var any=shuffle(pool);p=[];for(var i=0;i<nTeams;i++)p.push(any[i%any.length])}  /* pool quá nhỏ */
    p.forEach(function(q){used[q.id]=1});
    out.push(p);
  }
  return out;
}
/* Lịch lượt.  tilt: vòng 1 (đội A,B,C…) rồi vòng 2…  slice: mỗi đội chơi trọn một lượt tiếp sức rồi đến đội kế.
   Số lượt mỗi đội = (số người đông nhất) × cycles. Người chơi = order[round % size] => gọi hết đội rồi mới lặp lại. */
function makeMatch(cfg){
  var n=cfg.teams.length,Rmax=0;cfg.teams.forEach(function(t){Rmax=Math.max(Rmax,t.length)});
  var cycles=Math.max(1,cfg.cycles||1),R=Rmax*cycles;
  var teams=cfg.teams.map(function(ids,i){var d=TEAM_DEF[i];return {idx:i,name:d.name,emoji:d.emoji,color:d.color,members:ids.slice(),order:shuffle(ids),score:0,turns:0}});
  var sr=(cfg.specialRound==null||cfg.specialRound<0||cfg.specialRound>=R)?R-1:cfg.specialRound;
  var special=cfg.special==='double'||cfg.special==='bet'?cfg.special:'none';
  var slots=[];
  function add(round,t){slots.push({i:slots.length,round:round,team:t,player:teams[t].order[round%teams[t].order.length],special:(special!=='none'&&round===sr)?special:'none',res:null})}
  if(cfg.mode==='slice'){for(var c=0;c<cycles;c++)for(var t=0;t<n;t++)for(var j=0;j<Rmax;j++)add(c*Rmax+j,t)}
  else{for(var r=0;r<R;r++)for(var t2=0;t2<n;t2++)add(r,t2)}
  var rounds=drawRounds(cfg.pool,R,n);
  slots.forEach(function(s){s.q=rounds[s.round][s.team]});
  var names={};Object.keys(cfg.names||{}).forEach(function(k){names[k]=cfg.names[k]});
  var M={mode:cfg.mode,cls:cfg.cls||'',teams:teams,slots:slots,names:names,rounds:R,Rmax:Rmax,cycles:cycles,special:special,specialRound:sr,bet:0,stats:{},cfg:cfg};
  cfg.teams.forEach(function(ids){ids.forEach(function(id){M.stats[id]={played:0,correct:0}})});
  M.nameOf=function(id){return M.names[id]||id};
  M.betOptions=function(i){var s=M.slots[i],sc=M.teams[s.team].score;return POINTS.betChoices.filter(function(b){return b<=sc})};
  M.setBet=function(i,b){if(M.slots[i].special!=='bet')return 0;var ok=M.betOptions(i).indexOf(b)>=0?b:0;M.bet=ok;return ok};
  /* Cập nhật điểm ngay sau khi chốt kết quả. status: correct | wrong | timeout */
  M.finish=function(i,status){
    var s=M.slots[i];if(s.res)return s.res;          /* chống tính điểm hai lần */
    var t=M.teams[s.team],ok=status==='correct',bet=s.special==='bet'?M.bet:0,d=0;
    if(s.special==='double')d=ok?POINTS.double:0;
    else if(s.special==='bet')d=ok?POINTS.bet+bet:-bet;
    else d=ok?POINTS.normal:0;
    if(t.score+d<0)d=-t.score;
    t.score+=d;t.turns++;var st=M.stats[s.player]||(M.stats[s.player]={played:0,correct:0});st.played++;if(ok)st.correct++;
    s.res={status:status,delta:d,bet:bet,score:t.score};M.bet=0;return s.res;
  };
  M.next=function(i){return M.slots[i+1]||null};
  M.ranking=function(){return M.teams.slice().sort(function(a,b){return b.score-a.score})};
  return M;
}

/* ================= GIAO DIỆN ================= */
var CSS=[
'.tm .tmbox{background:#FFF8E8;border:1.5px solid #E6D9AE;border-radius:14px;padding:12px;margin-bottom:10px}',
'.tm .tmsel{border:2px solid #E6D9AE;border-radius:12px;padding:9px 10px;font-size:1rem;font-weight:700;background:#fff;min-height:42px;max-width:100%}',
'.tm .tmpin{border:2px solid #E6D9AE;border-radius:12px;padding:10px 12px;font-size:1rem;width:170px}',
'.tm .tmlist{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:6px}',
'.tm .tmst{display:flex;align-items:center;gap:8px;border:1.5px solid #E6D9AE;border-radius:12px;padding:7px 10px;background:#fff;font-weight:700;cursor:pointer;min-height:44px}',
'.tm .tmst.on{background:#FFF1BD;border-color:#111}.tm .tmst.off{background:#f1eee4;color:#8a826a;text-decoration:line-through}',
'.tm .tmst input{width:20px;height:20px}.tm .tmst small{color:#7A5A06;font-weight:700;text-decoration:none}',
'.tm .tmteams{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;margin-top:8px}',
'.tm .tmtm{border:3px solid var(--tc);border-radius:14px;background:#fff;overflow:hidden}',
'.tm .tmtm h4{margin:0;padding:7px 10px;background:var(--tc);color:#fff;font-size:1rem}',
'.tm .tmtm .mb{display:flex;align-items:center;gap:6px;justify-content:space-between;padding:5px 8px;border-top:1px solid #eee;font-weight:700}',
'.tm .tmtm .mb select{border:1.5px solid #E6D9AE;border-radius:10px;padding:4px 6px;font-size:.85rem;background:#fff;min-height:34px}',
'.tm .chip.off{opacity:.4}',
'.tmboard{display:flex;gap:8px;padding:4px 12px 2px;align-items:stretch;flex-wrap:wrap}',
'.tmboard .tc{flex:1;min-width:110px;border:3px solid var(--tc);border-radius:14px;background:rgba(255,255,255,.08);padding:4px 10px;display:flex;justify-content:space-between;align-items:center;gap:8px;font-weight:800;transition:transform .2s,background .2s}',
'.tmboard .tc b{font-size:1.5rem;line-height:1}.tmboard .tc span{font-size:.95rem}',
'.tmboard .tc.act{background:var(--tc);transform:scale(1.04);box-shadow:0 0 0 3px rgba(255,255,255,.7)}',
'.tmboard .tc.pop b{animation:tmpop .7s ease-out}@keyframes tmpop{0%{transform:scale(1)}30%{transform:scale(1.6)}100%{transform:scale(1)}}',
'.tmboard .now{flex-basis:100%;display:flex;gap:14px;justify-content:center;flex-wrap:wrap;font-weight:800;font-size:1rem;padding:2px 0}',
'.tmboard .now em{font-style:normal;color:#FFE066}',
'.tmboard .now .tag{background:#FFE066;color:#111;border-radius:999px;padding:1px 12px}',
'.tmboard .delta{position:absolute;pointer-events:none}',
'.tmov h2{font-size:clamp(1.3rem,4vw,2.2rem)}.tmov .who{font-size:clamp(2.2rem,8vw,5rem);font-weight:800;line-height:1.1;border:5px solid var(--tc);border-radius:22px;padding:6px 26px;background:rgba(255,255,255,.1)}',
'.tmov .tn{font-size:1.4rem;font-weight:800;color:var(--tc);background:#fff;border-radius:999px;padding:2px 16px}',
'.tmov .nx{opacity:.92;font-weight:700}.tmov .sp{background:#FFE066;color:#111;border-radius:14px;padding:8px 16px;font-weight:800;max-width:560px}',
'.tmov .bets{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}',
'.tmov .bets button{border:3px solid #fff;background:rgba(255,255,255,.12);color:#fff;border-radius:16px;font-size:1.3rem;font-weight:800;padding:10px 22px;min-width:96px;min-height:52px}',
'.tmov .bets button.on{background:#FFE066;color:#111}.tmov .bets button:disabled{opacity:.35}',
'.tmboard .tmrelay{flex-basis:100%}.tmrelay{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;padding:2px 12px}.tmrelay .ri{border:2px solid rgba(255,255,255,.5);border-radius:12px;padding:3px 10px;font-weight:800;font-size:.9rem;background:rgba(255,255,255,.08);min-width:88px;text-align:center}.tmrelay .ri.ok{background:#CFF3D3;color:#0B5A1E;border-color:#2FA84F}.tmrelay .ri.bad{background:#FFD6D0;color:#8a1d12;border-color:#E0402F}.tmrelay .ri.cur{background:#FFE066;color:#111;border-color:#fff}.tmrelay .ri small{display:block;font-weight:700;opacity:.85}',
'.tmrank{display:flex;flex-direction:column;gap:8px}.tmrank .rk{display:flex;align-items:center;gap:12px;border:3px solid var(--tc);border-radius:16px;padding:8px 14px;font-weight:800;background:#fff}',
'.tmrank .rk b{font-size:1.8rem;margin-left:auto}.tmrank .rk.win{background:#FFF1BD}'
].join('\n');
function injectCss(){
  if(typeof document==='undefined'||document.getElementById('tmCss'))return;
  var st=document.createElement('style');st.id='tmCss';st.textContent=CSS;document.head.appendChild(st);
}

function create(host){
  injectCss();
  /* sel = danh sách người chơi lập tay cho trận này (ID suy ra); lessonCls chỉ dùng để xác định bài đã mở, tách hẳn với sel */
  var S={pin:'',loading:false,err:'',students:null,classes:null,all:[],byId:{},lessonCls:'',count:0,sel:[],q:'',n:2,teams:[],stale:false,manual:false,cycles:1,special:'none',specialRound:-1,el:null};
  var TM={};
  host=host||{};
  function pick(id){return S.byId[id]||null}
  function selMembers(){return S.sel.map(pick).filter(Boolean)}
  function dispMap(){return displayNames(selMembers())}
  function invalidate(){S.stale=S.teams.length>0;S.teams=[];S.manual=false}
  function split(){S.manual=false;S.stale=false;var ids=S.sel.slice();S.n=Math.max(2,Math.min(S.n,maxN(ids.length)));if(ids.length<2){S.teams=[];return}var g={};selMembers().forEach(function(m){g[m.id]=m.group});S.teams=autoSplit(ids,g,S.n)}
  function setLessonCls(c){
    S.lessonCls=c;
    if(host.onClass)host.onClass(c,classAllowed((S.classes&&S.classes[c])||[]));   /* chỉ đổi bài ôn, không đụng tới danh sách người chơi */
  }
  function load(force){
    if(S.loading)return;if(S.students&&!force)return;
    var pin=S.pin||(host.getPin&&host.getPin())||'';if(!pin)return;
    S.pin=pin;S.loading=true;S.err='';render();
    host.api({action:'report',pin:pin}).then(function(res){
      S.loading=false;
      if(res&&res.ok){
        S.students=res.students||[];S.classes=buildRoster(S.students);S.all=flatten(S.classes);S.byId={};S.all.forEach(function(m){S.byId[m.id]=m});
        var before=S.sel.length;S.sel=S.sel.filter(function(id){return S.byId[id]});if(S.sel.length!==before)invalidate();
        if(host.onTeacher)host.onTeacher(pin);
        var names=Object.keys(S.classes).sort(),mine=host.myClass&&host.myClass();
        if(!S.classes[S.lessonCls]){var c=S.classes[mine]?mine:names[0];if(c)setLessonCls(c)}
      }else{S.pin='';S.err=(res&&res.error)||'PIN chưa đúng.'}
      render();if(host.refresh)host.refresh();
    },function(){S.loading=false;S.err='Không kết nối được máy chủ để lấy danh sách học viên. Kiểm tra mạng rồi thử lại.';render();if(host.refresh)host.refresh()});
  }
  function teamOf(id){for(var t=0;t<S.teams.length;t++)if(S.teams[t].indexOf(id)>=0)return t;return -1}
  function stats(){var sz=S.teams.map(function(t){return t.length}),Rmax=sz.length?Math.max.apply(null,sz):0;return {sizes:sz,Rmax:Rmax,R:Rmax*S.cycles}}
  TM.state=function(){return S};
  TM.canStart=function(){
    if(!S.students)return {ok:false,why:'Nhập PIN để tải danh sách học viên.'};
    if(S.count<2)return {ok:false,why:'Nhập số học viên có mặt (từ 2 trở lên).'};
    if(S.sel.length<S.count)return {ok:false,why:'Cần chọn đủ '+S.count+' bạn (đang '+S.sel.length+'/'+S.count+').'};
    if(S.sel.length>S.count)return {ok:false,why:'Đang chọn nhiều hơn '+S.count+' bạn – bỏ bớt hoặc tăng số có mặt.'};
    if(S.stale||!S.teams.length)return {ok:false,why:'Danh sách đã thay đổi – bấm “Chia đội” lại trước khi bắt đầu.'};
    if(S.teams.length<2||S.teams.some(function(t){return !t.length}))return {ok:false,why:'Mỗi đội cần ít nhất 1 bạn.'};
    var all=[];S.teams.forEach(function(t){all=all.concat(t)});
    if(all.length!==S.sel.length||all.some(function(id){return S.sel.indexOf(id)<0}))return {ok:false,why:'Đội chưa khớp danh sách – bấm “Chia đội”.'};
    return {ok:true,why:''};
  };
  TM.buildMatch=function(pool,mode){return makeMatch({mode:mode,cls:S.lessonCls,teams:S.teams,pool:pool,cycles:S.cycles,special:S.special,specialRound:S.specialRound,names:dispMap()})};
  TM.rebuild=function(M,pool){return makeMatch({mode:M.mode,cls:M.cls,teams:M.cfg.teams,pool:pool,cycles:M.cycles,special:M.special,specialRound:M.specialRound,names:M.names})};
  TM.turnsTotal=function(){var s=stats();return s.R*S.teams.length};

  /* ----- bảng cài đặt ----- */
  function resultsHtml(){
    if(!S.students)return '';
    var q=S.q.trim();if(!q)return '<div class="note">Gõ tên (có dấu hoặc không dấu) để tìm trong toàn bộ danh sách học viên.</div>';
    var r=searchStudents(S.all,q,30);if(!r.length)return '<div class="note warn">Không tìm thấy “'+esc(q)+'”.</div>';
    var full=S.sel.length>=S.count;
    return '<div class="tmlist">'+r.map(function(m){var on=S.sel.indexOf(m.id)>=0;
      return '<button type="button" class="tmst'+(on?' on':'')+'" data-tm-add="'+esc(m.id)+'"'+((!on&&full)?' disabled':'')+'><span>'+(on?'✓ ':'')+esc(m.name)+' <small>· Lớp '+esc(m.cls)+(m.group?' · nhóm '+esc(m.group):'')+'</small></span></button>'}).join('')+'</div>'+(full?'<div class="note">Đã chọn đủ '+S.count+' bạn. Bỏ chọn một bạn nếu muốn đổi.</div>':'');
  }
  function panelInner(){
    var h='';
    if(!S.students){
      if(S.loading)return '<div class="tmbox">⏳ Đang tải danh sách học viên từ máy chủ…</div>';
      h+='<div class="tmbox">🔐 Chế độ thi đấu theo đội lấy danh sách học viên từ sổ học viên nên cần <b>PIN giáo viên</b>.<div class="pin" style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><input class="tmpin" id="tmPin" type="password" inputmode="numeric" placeholder="PIN giáo viên" autocomplete="off"><button class="btn" data-tm="pin">Xác nhận &amp; tải danh sách</button></div>';
      if(S.err)h+='<div class="warn" style="margin-top:6px">'+esc(S.err)+'</div>';
      return h+'</div>';
    }
    if(!S.all.length)return '<div class="tmbox warn">Sổ học viên chưa có học viên nào đang học. <button class="chip" data-tm="reload">↻ Tải lại</button></div>';
    var s=stats(),mem=selMembers(),dm=dispMap();
    h+='<div class="row"><label>1 · Số học viên có mặt hôm nay</label><div class="chips" style="align-items:center"><input class="tmsel" id="tmCount" data-tm-count="1" type="number" inputmode="numeric" min="2" max="40" value="'+(S.count||'')+'" placeholder="vd: 7" style="width:110px"><button class="chip" data-tm="reload">↻ Tải lại danh sách</button></div></div>';
    h+='<div class="row"><label>2 · Tìm và chọn học viên (toàn hệ thống, kể cả lớp khác)</label><input class="tmsel" id="tmQ" data-tm-q="1" type="search" value="'+esc(S.q)+'" placeholder="Tìm theo tên, có dấu hoặc không dấu" autocomplete="off" style="width:100%"><div id="tmRes" style="margin-top:8px">'+resultsHtml()+'</div></div>';
    h+='<div class="row"><label>Đã chọn <span id="tmCnt">'+S.sel.length+'/'+(S.count||'?')+'</span></label>'+(mem.length?'<div class="tmlist">'+mem.map(function(m){return '<div class="tmst on"><span>'+esc(dm[m.id])+(dm[m.id]!==m.name?'':' <small>· Lớp '+esc(m.cls)+'</small>')+'</span><button type="button" class="chip" data-tm-rm="'+esc(m.id)+'" aria-label="Bỏ chọn" style="min-height:32px;padding:2px 10px">✕</button></div>'}).join('')+'</div><div class="chips" style="margin-top:8px"><button class="chip" data-tm="clear">Xoá hết danh sách</button></div>':'<div class="note">Chưa chọn bạn nào.</div>')+'<div class="note" style="margin-top:4px">Danh sách chỉ áp dụng cho trận này, không đổi lớp hay hồ sơ của học viên.</div></div>';
    h+='<div class="row"><label>3 · Chia đội</label><div class="chips">'+[2,3,4].map(function(n){var okN=S.sel.length>=n;return '<button class="chip'+(S.n===n?' on':'')+(okN?'':' off')+'" data-tm="n:'+n+'"'+(okN?'':' disabled')+'>'+n+' đội</button>'}).join('')+'<button class="chip'+(S.stale?' on':'')+'" data-tm="split"'+(S.sel.length>=2&&S.sel.length===S.count?'':' disabled')+'>🎲 Chia đội</button></div>'+(S.stale?'<div class="note warn" style="margin-top:4px">Danh sách đã thay đổi – cần bấm “Chia đội” lại.</div>':'<div class="note" style="margin-top:4px">Chỉ chia được khi đã chọn đủ số người. Mỗi đội cần ít nhất 1 bạn; có thể chuyển bạn giữa các đội bằng ô chọn bên dưới.</div>');
    if(S.teams.length){h+='<div class="tmteams">'+S.teams.map(function(t,i){var d=TEAM_DEF[i];return '<div class="tmtm" style="--tc:'+d.color+'"><h4>'+d.emoji+' Đội '+esc(d.name)+' · '+t.length+' bạn</h4>'+t.map(function(id){return '<div class="mb"><span>'+esc(dm[id]||id)+'</span><select data-tm-mv="'+esc(id)+'" aria-label="Chuyển đội">'+S.teams.map(function(_,k){return '<option value="'+k+'"'+(k===i?' selected':'')+'>'+TEAM_DEF[k].emoji+' '+esc(TEAM_DEF[k].name)+'</option>'}).join('')+'</select></div>'}).join('')+'</div>'}).join('')+'</div>'}
    h+='</div>';
    var names=Object.keys(S.classes).sort();
    h+='<div class="row"><label>Lớp dùng để chọn bài ôn</label><div class="chips" style="align-items:center"><select class="tmsel" data-tm-cls="1">'+names.map(function(c){return '<option value="'+esc(c)+'"'+(c===S.lessonCls?' selected':'')+'>Lớp '+esc(c)+'</option>'}).join('')+'</select></div><div class="note" style="margin-top:4px">Chỉ quyết định bài nào đã mở để ôn. Đổi lớp ở đây không làm mất danh sách người chơi.</div></div>';
    h+='<div class="row"><label>Số lượt mỗi đội</label><div class="chips">'+[1,2].map(function(c){return '<button class="chip'+(S.cycles===c?' on':'')+'" data-tm="cyc:'+c+'">×'+c+(c===1?' (mọi bạn chơi 1 lần)':' (2 vòng)')+'</button>'}).join('')+'</div><div class="note" style="margin-top:4px">'+(s.Rmax?'Mỗi đội nhận <b>'+s.R+'</b> lượt'+(s.sizes.some(function(z){return z<s.Rmax})?' – đội ít người hơn xoay vòng người nhận lượt thêm':'')+'. Tổng '+(s.R*S.teams.length)+' lượt.':'')+'</div></div>';
    h+='<div class="row"><label>Câu đặc biệt</label><div class="chips">'+[['none','Tắt'],['double','✖2 Nhân đôi'],['bet','🎲 Cược điểm']].map(function(x){return '<button class="chip'+(S.special===x[0]?' on':'')+'" data-tm="sp:'+x[0]+'">'+x[1]+'</button>'}).join('')+(S.special!=='none'&&s.R?'<select class="tmsel" data-tm-sr="1" aria-label="Vòng đặc biệt">'+Array.apply(null,Array(s.R)).map(function(_,r){var sel=(S.specialRound<0||S.specialRound>=s.R?s.R-1:S.specialRound)===r;return '<option value="'+r+'"'+(sel?' selected':'')+'>Vòng '+(r+1)+(r===s.R-1?' (cuối)':'')+'</option>'}).join('')+'</select>':'')+'</div><div class="note" style="margin-top:4px">'+(S.special==='double'?'Ở vòng đặc biệt, mỗi đội có một lượt: đúng +20, sai 0.':S.special==='bet'?'Ở vòng đặc biệt, mỗi đội có một lượt: chọn cược 0 hoặc 5 trước khi thấy câu (tối đa bằng số điểm đội đang có). Đúng +10 và cộng mức cược, sai mất mức cược.':'Câu thường: đúng +10, sai 0.')+'</div></div>';
    var c=TM.canStart();h+='<div class="note '+(c.ok?'okc':'warn')+'" id="tmStatus">'+(c.ok?'✔ Sẵn sàng thi đấu: '+S.teams.map(function(t,i){return TEAM_DEF[i].emoji+' '+t.length}).join(' · '):esc(c.why))+'</div>';
    return h;
  };
  function render(){
    if(!S.el)return;var ae=document.activeElement,fid=ae&&S.el.contains(ae)&&(ae.id==='tmCount'||ae.id==='tmQ')?ae.id:'';
    S.el.innerHTML=panelInner();
    if(fid){var n=S.el.querySelector('#'+fid);if(n){n.focus();try{var l=n.value.length;n.setSelectionRange(l,l)}catch(e){}}}
  }
  TM.panelHtml=function(){return '<div class="tm" id="tmPanel">'+panelInner()+'</div>'};
  TM.mount=function(el){
    S.el=el;if(!el)return;
    if(!el.__tmBound){el.__tmBound=true;
      function after(){render();if(host.refresh)host.refresh()}
      el.addEventListener('click',function(e){
        var add=e.target.closest('[data-tm-add]');
        if(add&&!add.disabled){var id=add.getAttribute('data-tm-add'),k=S.sel.indexOf(id);if(k>=0)S.sel.splice(k,1);else if(S.sel.length<S.count)S.sel.push(id);else return;invalidate();after();return}
        var rm=e.target.closest('[data-tm-rm]');
        if(rm){var k2=S.sel.indexOf(rm.getAttribute('data-tm-rm'));if(k2>=0)S.sel.splice(k2,1);invalidate();after();return}
        var b=e.target.closest('button[data-tm]');if(!b||b.disabled)return;var a=b.getAttribute('data-tm');
        if(a==='pin'){var i=el.querySelector('#tmPin');S.pin=(i&&i.value||'').trim();if(!S.pin){S.err='Nhập PIN giáo viên.';render();return}S.students=null;load(true);return}
        if(a==='reload'){S.students=null;load(true);return}
        if(a==='clear'){S.sel=[];invalidate()}
        else if(a==='split')split();
        else if(a.indexOf('n:')===0){S.n=Number(a.slice(2));if(S.teams.length&&!S.stale)split();}
        else if(a.indexOf('cyc:')===0){S.cycles=Number(a.slice(4));S.specialRound=-1}
        else if(a.indexOf('sp:')===0){S.special=a.slice(3)}
        else return;
        after();
      });
      el.addEventListener('input',function(e){
        var t=e.target;if(!t)return;
        if(t.hasAttribute('data-tm-q')){S.q=t.value;var r=el.querySelector('#tmRes');if(r)r.innerHTML=resultsHtml()}
        else if(t.hasAttribute('data-tm-count')){
          var v=Math.max(0,Math.min(40,parseInt(t.value,10)||0));S.count=v;
          if(S.sel.length>v){S.sel=S.sel.slice(0,v)}  /* giảm số có mặt thì cắt bớt cuối danh sách */
          invalidate();
          after();
        }
      });
      el.addEventListener('change',function(e){
        var t=e.target;if(!t)return;
        if(t.hasAttribute('data-tm-count'))return;
        if(t.hasAttribute('data-tm-cls')){setLessonCls(t.value)}
        else if(t.hasAttribute('data-tm-mv')){
          var mid=t.getAttribute('data-tm-mv'),to=Number(t.value),from=teamOf(mid);
          if(from>=0&&to!==from){S.manual=true;S.teams[from]=S.teams[from].filter(function(x){return x!==mid});S.teams[to].push(mid)}
        }
        else if(t.hasAttribute('data-tm-sr')){S.specialRound=Number(t.value)}
        else return;
        after();
      });
      el.addEventListener('keydown',function(e){if(e.key==='Enter'&&e.target&&e.target.id==='tmPin'){var b=el.querySelector('[data-tm="pin"]');if(b)b.click()}});
    }
    if(!S.students&&!S.loading&&(S.pin||(host.getPin&&host.getPin())))load(false);
  };

  /* ----- MIAO SLICE: tiến độ lượt tiếp sức của đội hiện tại (giữ nguyên khi đổi người) ----- */
  TM.relayHtml=function(M,i){
    if(M.mode!=='slice')return '';
    var s=M.slots[Math.min(i,M.slots.length-1)],blk=Math.floor(s.round/M.Rmax),a=blk*M.Rmax;
    var items=M.slots.filter(function(x){return x.team===s.team&&x.round>=a&&x.round<a+M.Rmax});
    return '<div class="tmrelay" aria-label="Tiến độ tiếp sức">'+items.map(function(x,k){
      var cls=x.res?(x.res.status==='correct'?' ok':' bad'):(x.i===s.i?' cur':'');
      var body=x.res?((x.res.status==='correct'?'✓ ':'✗ ')+esc(x.q.correctAnswer.length>8?x.q.correctAnswer.slice(0,8)+'…':x.q.correctAnswer)):(x.i===s.i?'▶ đang tới':'○');
      return '<div class="ri'+cls+'">Mục '+(k+1)+'<small>'+esc(M.nameOf(x.player))+'</small>'+body+'</div>'}).join('')+'</div>';
  };
  /* ----- bảng điểm trên màn chiếu: chỉ tên đội, điểm, tên bạn đang chơi / chuẩn bị ----- */
  TM.boardHtml=function(M,i,opt){
    opt=opt||{};var s=M.slots[Math.min(i,M.slots.length-1)],nx=M.slots[i+1];
    var h=M.teams.map(function(t){return '<div class="tc'+(t.idx===s.team&&!opt.finished?' act':'')+(opt.pop===t.idx?' pop':'')+'" style="--tc:'+t.color+'"><span>'+t.emoji+' '+esc(t.name)+'</span><b>'+t.score+'</b></div>'}).join('');
    if(!opt.finished){
      h+='<div class="now"><span>Đang chơi: <em>'+esc(M.nameOf(s.player))+'</em> ('+M.teams[s.team].emoji+' '+esc(M.teams[s.team].name)+')</span>'+
        (nx?'<span>Chuẩn bị: <em>'+esc(M.nameOf(nx.player))+'</em> ('+M.teams[nx.team].emoji+' '+esc(M.teams[nx.team].name)+')</span>':'<span><em>Lượt cuối</em></span>')+
        (s.special==='double'?'<span class="tag">✖2 NHÂN ĐÔI</span>':s.special==='bet'?'<span class="tag">🎲 CƯỢC '+(M.bet||0)+'</span>':'')+'</div>';
    }
    return h+TM.relayHtml(M,i);
  };
  /* ----- màn "Đang đổi người" ----- */
  TM.handoverHtml=function(M,i,opt){
    opt=opt||{};var s=M.slots[i],t=M.teams[s.team],prev=M.slots[i-1],nx=M.slots[i+1];
    var newTeam=!prev||prev.team!==s.team;
    var title=!prev?'Chuẩn bị bắt đầu':(M.mode==='slice'&&newTeam?'Hết lượt tiếp sức của đội '+M.teams[prev.team].name+' – đổi đội':'Đang đổi người');
    var h='<div class="tmov" style="--tc:'+t.color+';display:flex;flex-direction:column;align-items:center;gap:12px">';
    h+='<h2>⏳ '+esc(title)+'</h2><div class="tn">'+t.emoji+' Đội '+esc(t.name)+'</div><div class="who">'+esc(M.nameOf(s.player))+'</div>';
    h+='<p>'+(opt.cam?'Bạn mới đứng vào vị trí, nhìn thẳng vào camera. Camera đang <b>khóa</b> – chưa nhận đáp án.':'Bạn mới đứng vào vị trí. Đầu vào đang <b>khóa</b> cho tới khi cô bấm nút.')+'</p>';
    if(M.mode==='slice')h+=TM.relayHtml(M,i);
    if(s.special==='double')h+='<div class="sp">✖2 Câu nhân đôi – đúng +20, sai 0</div>';
    if(s.special==='bet'){var bo=M.betOptions(i);h+='<div class="sp">🎲 Câu cược điểm – chọn mức cược trước khi xem câu (tối đa '+t.score+' điểm đang có)</div><div class="bets">'+POINTS.betChoices.map(function(b){return '<button data-tmbet="'+b+'"'+(bo.indexOf(b)<0?' disabled':'')+(M.bet===b?' class="on"':'')+'>Cược '+b+'</button>'}).join('')+'</div>'}
    h+='<button class="btn big" id="tmGo"'+(opt.ready===false?' disabled':'')+'>'+(opt.goLabel||'▶ Bắt đầu lượt')+'</button>';
    if(opt.hint)h+='<div class="nx" id="tmHint">'+esc(opt.hint)+'</div>';
    if(nx)h+='<div class="nx">Kế tiếp: '+esc(M.nameOf(nx.player))+' ('+M.teams[nx.team].emoji+' '+esc(M.teams[nx.team].name)+')</div>';
    return h+'</div>';
  };
  /* ----- màn kết quả ----- */
  TM.resultHtml=function(M){
    var rk=M.ranking(),top=rk[0].score,h='<h2 style="margin:0 0 10px">🏆 Kết quả thi đấu · Lớp '+esc(M.cls)+'</h2><div class="tmrank">';
    rk.forEach(function(t,k){h+='<div class="rk'+(t.score===top?' win':'')+'" style="--tc:'+t.color+'"><span style="font-size:1.6rem">'+t.emoji+'</span><span>Đội '+esc(t.name)+(t.score===top?(rk.filter(function(x){return x.score===top}).length>1?' · đồng hạng nhất':' · 🥇 Nhất'):'')+'</span><b>'+t.score+' điểm</b></div>'});
    h+='</div>';
    M.teams.forEach(function(t){h+='<div class="tmtm" style="--tc:'+t.color+';margin-top:10px"><h4>'+t.emoji+' Đội '+esc(t.name)+'</h4>'+t.members.map(function(id){var st=M.stats[id]||{played:0,correct:0};return '<div class="mb"><span>'+esc(M.nameOf(id))+'</span><span>'+st.correct+'/'+st.played+' đúng</span></div>'}).join('')+'</div>'});
    return h;
  };
  TM.save=function(M){
    try{var a=JSON.parse(localStorage.getItem(HIST_KEY)||'[]');a.unshift({t:new Date().toISOString(),cls:M.cls,mode:M.mode,teams:M.teams.map(function(t){return {name:t.name,n:t.members.length,score:t.score}})});localStorage.setItem(HIST_KEY,JSON.stringify(a.slice(0,20)));return true}catch(e){return false}
  };
  TM.defs=TEAM_DEF;
  return TM;
}

var API={create:create,logic:{buildRoster:buildRoster,autoSplit:autoSplit,drawRounds:drawRounds,makeMatch:makeMatch,isInactive:isInactive,maxN:maxN,fold:fold,flatten:flatten,searchStudents:searchStudents,displayNames:displayNames,POINTS:POINTS,classAllowed:classAllowed}};
if(typeof module!=='undefined'&&module.exports)module.exports=API;else root.TeamMode=API;
})(typeof window!=='undefined'?window:this);
