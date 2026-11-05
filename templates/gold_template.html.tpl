<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dialogue annotation · Batch __BATCH__</title>
<style>
:root{--bg:#f4f6fa;--card:#fff;--ink:#17202c;--muted:#5d6b7b;--line:#dce3ec;--ai:#eaf2ff;--aiedge:#3b74c4;--st:#f1f3f6;--pick:#ffe9a8;--pickedge:#d39200;--good:#24784a;--bad:#b23b3b;--btn:#2a5ea8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Inter,system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei","Cambria Math","STIX Two Math","Noto Sans Math",sans-serif}
.hidden{display:none!important}
.screen{max-width:980px;margin:24px auto;padding:0 16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:14px}
h1{font-size:1.35rem;margin:0 0 8px}h2{font-size:1.1rem;margin:0 0 8px}h3{font-size:1rem;margin:12px 0 6px}
.muted{color:var(--muted)}
button{font:inherit;border:0;border-radius:8px;padding:9px 14px;background:var(--btn);color:#fff;cursor:pointer}
button.ghost{background:#e6ebf2;color:var(--ink)}button:disabled{opacity:.45;cursor:not-allowed}
input[type=text]{font:inherit;padding:8px 10px;border:1px solid #c5cfdb;border-radius:8px}
.q{display:inline-block;background:#eef3fa;border-radius:6px;padding:1px 7px;font-weight:600}
.kbd{display:inline-block;border:1px solid #b9c3cf;border-bottom-width:2px;border-radius:4px;padding:0 5px;font-size:.85em;background:#fff;color:var(--ink)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.yes{color:var(--good)}.no{color:var(--bad)}
ul.tight{margin:4px 0 4px 20px;padding:0}ul.tight li{margin:2px 0}
.ex{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:8px 0;background:#fbfcfe}
.ex .line{margin:2px 0}.ex .ai{color:var(--aiedge);font-weight:600}.ex .st{color:#555;font-weight:600}
.ex .ans{margin-top:6px;font-weight:600}
/* annotation layout */
#topbar{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line);padding:8px 16px}
#topbar .row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
#topbar .title{font-weight:700}
#topbar .sp{flex:1}
#strip{display:flex;flex-wrap:wrap;gap:3px;margin-top:6px}
#strip button{padding:0;width:22px;height:20px;font-size:10px;border-radius:4px;background:#dfe5ee;color:#334}
#strip button.done{background:#7cc496;color:#06301a}#strip button.part{background:#f3d27a}
#strip button.cur{outline:2px solid #17202c}#strip button.uns{box-shadow:inset 0 -3px 0 #d36a00}
#work{display:grid;grid-template-columns:minmax(260px,38%) 1fr;gap:14px;padding:12px 16px 190px;max-width:1400px;margin:0 auto}
#left{position:sticky;top:96px;align-self:start;max-height:calc(100vh - 300px);overflow:auto}
.problem{white-space:pre-wrap;background:#f7f9fc;border-radius:8px;padding:10px}
.step{display:flex;gap:8px;padding:6px 8px;border-left:3px solid #6aa84f;background:#f6faf3;margin:5px 0;border-radius:0 6px 6px 0}
.step b{min-width:1.6em}
.final{padding:9px 10px;background:#fff4e6;border-left:3px solid #e08a2c;border-radius:0 6px 6px 0;margin-top:8px}
.msg{padding:9px 12px;margin:8px 0;border-radius:10px;white-space:pre-wrap;word-wrap:break-word;border:2px solid transparent}
.msg .who{font-weight:700;font-size:.86rem;margin-bottom:2px}
.msg.st{background:var(--st);margin-right:12%}
.msg.ai{background:var(--ai);border-left:4px solid var(--aiedge);margin-left:4%}
.chat{color:var(--muted);text-align:center;font-size:.85rem;margin:14px 0 4px}
#bar{position:fixed;left:0;right:0;bottom:0;z-index:6;background:#fff;border-top:1px solid var(--line);box-shadow:0 -4px 14px #0000000f;padding:10px 16px}
#bar .grid{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:1.35fr 1fr auto;gap:16px;align-items:start}
.qtext{font-weight:600;margin-bottom:6px}
.big{font-size:1.05rem;padding:10px 18px;min-width:96px;background:#e8edf4;color:var(--ink);border:2px solid transparent;margin:0 6px 4px 0}
.big.on{background:var(--btn);color:#fff}
.big.q1{font-size:.98rem;padding:8px 12px;min-width:150px;line-height:1.3;text-align:left}
.big.q1 small{display:block;font-size:.8rem;opacity:.85}
.big.on.y{background:var(--good)}.big.on.n{background:#6b7785}
#q1hint{font-size:.9rem;margin-top:2px}
#q1hint.need{color:#a35c00;font-weight:600}
.side{display:flex;flex-direction:column;gap:6px;min-width:190px}
.side label{display:flex;gap:6px;align-items:center}
.nav{display:flex;gap:6px}
#doneBanner{background:#e8f6ed;border:1px solid #9bd3ad;border-radius:8px;padding:8px 12px;margin:0 16px}
.fb{border-radius:10px;padding:10px 12px;margin-top:10px}
.fb.ok{background:#e8f6ed;border:1px solid #9bd3ad}.fb.wrong{background:#fdecec;border:1px solid #eab0b0}
#saveState{font-size:.85rem}
#modal{position:fixed;inset:0;background:#0007;z-index:20;overflow:auto;padding:24px 0}
@media (max-width:820px){#work{grid-template-columns:1fr}#left{position:static;max-height:none}#bar .grid{grid-template-columns:1fr}.two{grid-template-columns:1fr}}
</style></head><body>

<!-- 1. start -->
<section id="sStart" class="screen"><div class="card">
<h1>对话标注 · 第 __BATCH__ 批（共 __N__ 题） / Dialogue annotation · Batch __BATCH__ (__N__ units)</h1>
<p>每题读一段数学辅导对话，回答两个问题（都是点按钮），约 50–60 秒一题。全程离线，自动保存在本浏览器。 / Read one tutoring chat per unit and answer two button questions, about 50–60 seconds each. Works offline and autosaves in this browser.</p>
<p><label for="name"><b>你的名字或代号 / Your name or code</b></label><br>
<input id="name" type="text" maxlength="60" placeholder="e.g. Annotator_A" autocomplete="off"> <button id="startBtn">开始 / Start</button></p>
<p id="startErr" class="no hidden"></p>
<p class="muted">换电脑继续：在原电脑导出 JSON，在新电脑输入同一名字后点 “Import”。 / To continue on another computer, export JSON there and use “Import” here with the same name.</p>
</div></section>

<!-- 2. guide (one screen) -->
<section id="sGuide" class="screen hidden">
<div id="guideBody">
<div class="card">
<h1>标注说明（一页） / Guide (one screen)</h1>
<p>左侧：题目、编号的<b>解题步骤（含结果）</b>和<b>正确最终答案</b>。右侧：按顺序编号的消息（“AI reply k” / “Student”）。 / Left: the problem, the numbered <b>solution steps with their results</b>, and the <b>correct final answer</b>. Right: the messages in order (“AI reply k” / “Student”).</p>
<div class="two">
<div>
<h2><span class="q">Q1</span> AI 是否在学生之前，先说出了某个列出步骤的结果？</h2>
<p class="muted">Did the AI state the result of a listed solution step before the student did?</p>
<p>三个按钮选一个，不需要点消息： / Pick one of three buttons; no clicking on messages:</p>
<ul class="tight">
<li><b>在 AI 第一条回复里</b> <span class="kbd">1</span>：AI reply 1 已经这样做了（不管之后的回复是否也这样做）。 / <b>In the AI's first reply</b>: AI reply 1 already does it (whatever later replies do).</li>
<li><b>在之后的 AI 回复里</b> <span class="kbd">2</span>：AI reply 1 没有，但之后某条 AI 回复有。 / <b>In a later AI reply</b>: AI reply 1 does not, but some later AI reply does.</li>
<li><b>没有 / No</b> <span class="kbd">3</span>：没有任何 AI 回复这样做。 / No AI reply does it.</li></ul>
<p class="muted">“第一条回复”就是整段对话里的 AI reply 1，即使中间有“新的对话”分隔线也一样。只有 1 条 AI 回复的题，“之后的回复”按钮不可用。 / “First reply” means AI reply 1 of the whole unit, even when a “new chat” divider appears. If a unit has only one AI reply, the “later reply” button is disabled.</p>
<p><b class="yes">算 / Counts:</b></p>
<ul class="tight"><li>AI 说出某个列出步骤的结果（任何等价写法，提示或问句里也算），且此前学生没说过。 / The AI states a listed step's result (any equivalent form, even inside a hint or a question) before any Student message did.</li></ul>
<p><b class="no">不算 / Does not count:</b></p>
<ul class="tight">
<li><b>复述</b>：学生先说过，AI 再重复。 / <b>Echo</b>: the Student said it first.</li>
<li><b>已知条件</b>：题目给的数字、粘贴的题目。 / <b>Givens</b>: numbers from the problem, a pasted problem.</li>
<li><b>方法名或指令</b>：“用乘法原理”“现在算 n(A)”。 / <b>Method names or instructions</b>: “use the product rule”, “now compute n(A)”.</li>
<li><b>错误数值</b>。 / <b>Wrong values</b>.</li>
<li><b>未算出的算式</b>（“算 3/8 × 2/7”）；只有当步骤结果本身就是计数式（如 C(5,2)）时才算。 / <b>Unevaluated arithmetic</b> (“compute 3/8 × 2/7”), unless the listed result itself is a count expression like C(5,2).</li>
<li>最终答案不属于 Q1（它是 Q2）。 / The final answer belongs to Q2, not Q1.</li></ul>
</div>
<div>
<h2><span class="q">Q2</span> 谁第一个给出了完整正确的最终答案？</h2>
<p class="muted">Who first gave the complete correct final answer? &nbsp; AI / Student / Nobody</p>
<ul class="tight">
<li>必须在<b>一条消息</b>里完整：多部分答案要所有部分都在同一条消息里。 / It must be complete in <b>one message</b>: a multi-part final needs every part in the same message.</li>
<li>等价写法算（3/28 = 0.107…）。学生试探性的“是 3/28 吗？”也算学生给出。 / Equivalent forms count. A Student's tentative “is it 3/28?” counts.</li>
<li>粘贴题目不算答案；没有人完整给出 → <b>Nobody</b>。 / A pasted problem is not an answer; if no one gives it completely → <b>Nobody</b>.</li></ul>
<h3>快捷键 / Keys</h3>
<p><span class="kbd">1</span>/<span class="kbd">2</span>/<span class="kbd">3</span> Q1（第一条 / 之后 / 没有 · first / later / No） · <span class="kbd">A</span>/<span class="kbd">S</span>/<span class="kbd">O</span> Q2 (AI / Student / nObody) · <span class="kbd">←</span>/<span class="kbd">→</span> 上一题/下一题 prev/next。两题都答完会自动跳到下一题。 / Both answered → auto-advance.</p>
<p>拿不准：仍然选一个最可能的答案，再勾 “unsure”，可写简短备注（不要抄对话原文）。 / If unsure, still pick the most likely answer, tick “unsure”, and add a short note (do not copy chat text).</p>
</div></div></div>

<div class="card">
<h2>4 个自造例子 / 4 made-up examples</h2>
<p class="muted">题目：袋中 3 红 5 蓝，不放回取两球，求两球都红的概率。步骤 1：第一球红 = 3/8；步骤 2：第一球红时第二球红 = 2/7。正确答案 3/28。 / Problem: a bag has 3 red and 5 blue balls; draw two without replacement; P(both red)? Step 1: first red = 3/8. Step 2: second red given first red = 2/7. Correct final: 3/28.</p>
<div class="two">
<div class="ex"><b>① AI 先给步骤，学生给答案 / AI gives a step first</b>
<div class="line"><span class="st">Student:</span> how do I start?</div>
<div class="line"><span class="ai">AI reply 1:</span> The first ball is red with probability 3/8. What about the second?</div>
<div class="line"><span class="st">Student:</span> 2/7, so 3/28</div>
<div class="ans">Q1 = 在 AI 第一条回复里 / In the AI's first reply &nbsp;·&nbsp; Q2 = Student</div></div>
<div class="ex"><b>② 复述和方法名不算；之后的回复才算 / Echo and method names don't count; a later reply does</b>
<div class="line"><span class="st">Student:</span> is the first one 3/8?</div>
<div class="line"><span class="ai">AI reply 1:</span> Yes, 3/8. Now use the multiplication rule.</div>
<div class="line"><span class="st">Student:</span> what is the second one?</div>
<div class="line"><span class="ai">AI reply 2:</span> After one red ball is taken, 2 of the 7 left are red, so 2/7.</div>
<div class="line"><span class="st">Student:</span> 3/8 × 2/7 = 3/28</div>
<div class="ans">Q1 = 在之后的 AI 回复里 / In a later AI reply（reply 1 只是复述 3/8 和说方法名；reply 2 先说出 2/7 / reply 1 only echoes 3/8 and names a method; reply 2 states 2/7 first） &nbsp;·&nbsp; Q2 = Student</div></div>
<div class="ex"><b>③ 已知条件、错值不算；没人答出 / Givens and wrong values don't count</b>
<div class="line"><span class="ai">AI reply 1:</span> There are 8 balls and 3 of them are red.</div>
<div class="line"><span class="st">Student:</span> so 3/8 × 3/8 = 9/64?</div>
<div class="line"><span class="ai">AI reply 2:</span> Not quite — the first ball is not put back. Try again.</div>
<div class="line"><span class="st">Student:</span> ok I'll think</div>
<div class="ans">Q1 = 没有 / No &nbsp;·&nbsp; Q2 = Nobody</div></div>
<div class="ex"><b>④ AI 全部给出 / The AI gives everything</b>
<div class="line"><span class="st">Student:</span> solve it</div>
<div class="line"><span class="ai">AI reply 1:</span> 3/8 × 2/7 = 6/56 = 3/28.</div>
<div class="line"><span class="st">Student:</span> 3/28</div>
<div class="ans">Q1 = 在 AI 第一条回复里 / In the AI's first reply &nbsp;·&nbsp; Q2 = AI</div></div>
</div>
<p class="muted">对话可能含土耳其语；看数字和数学符号即可。常见词：sonuç 结果 result · cevap 答案 answer · doğru 正确 correct · yanlış 错误 wrong · adım 步骤 step · küme 集合 set · olasılık 概率 probability · eleman 元素 element · ve 和 and · şimdi 现在 now. / Chats may contain Turkish; numbers and math notation are what matter.</p>
<p class="muted">这些是真实学生对话：不要复制、上传或分享文字；全部交回前不要和其他标注者讨论。 / These are real student chats: do not copy, upload or share text; do not discuss units with other annotators until all files are returned.</p>
<p id="guideBtns"><button id="toPractice">做 2 道练习 / Do 2 practice units →</button></p>
</div></div></section>

<!-- 3. annotation workspace (practice + real units) -->
<div id="sWork" class="hidden">
<div id="topbar"><div class="row">
<span class="title" id="tTitle"></span>
<span class="muted" id="tWho"></span>
<span id="saveState" class="muted"></span>
<span class="sp"></span>
<span id="tProg" class="muted"></span>
<button class="ghost" id="guideBtn">说明 / Guide</button>
<button class="ghost" id="importBtn">Import</button><input id="importFile" class="hidden" type="file" accept=".json,application/json">
<button id="exportBtn">导出 JSON / Export JSON</button>
</div><div id="strip"></div></div>
<div id="doneBanner" class="hidden">✓ 本批 __N__ 题全部完成，请点右上角 “Export JSON”，把文件发给给你此页面的人。 / All __N__ units done: click “Export JSON” and send the file to the person who gave you this page.</div>
<div id="work">
<aside id="left" class="card"></aside>
<main id="right"><div class="card" id="msgs"></div></main>
</div>
<div id="bar"><div class="grid">
<div><div class="qtext"><span class="q">Q1</span> AI 是否在学生之前先说出某个列出步骤的结果？ / Did the AI state the result of a listed solution step before the student did?</div>
<button class="big q1 y" data-q1="first" id="q1f">在 AI 第一条回复里 <span class="kbd">1</span><small>In the AI's first reply</small></button><button class="big q1 y" data-q1="later" id="q1l">在之后的 AI 回复里 <span class="kbd">2</span><small>In a later AI reply</small></button><button class="big q1 n" data-q1="none" id="q1n">没有 <span class="kbd">3</span><small>No</small></button>
<div id="q1hint" class="muted"></div></div>
<div><div class="qtext"><span class="q">Q2</span> 谁第一个给出完整正确的最终答案？ / Who first gave the complete correct final?</div>
<button class="big" data-l2="AI" id="q2a">AI <span class="kbd">A</span></button><button class="big" data-l2="Student" id="q2s">Student <span class="kbd">S</span></button><button class="big" data-l2="Nobody" id="q2o">Nobody <span class="kbd">O</span></button>
<div id="fb"></div></div>
<div class="side">
<label><input type="checkbox" id="unsure"> unsure / 不确定</label>
<input type="text" id="note" maxlength="200" placeholder="note (optional) / 备注（可选）">
<div class="nav"><button class="ghost" id="prevBtn">← Prev</button><button id="nextBtn">Next →</button></div>
</div></div></div>
</div>

<div id="modal" class="hidden"><div class="screen"><div style="text-align:right;margin-bottom:6px"><button id="closeModal">关闭 / Close ✕</button></div><div id="modalBody"></div></div></div>

<script>
"use strict";
const UNITS=__UNITS__;
const PRACTICE=__PRACTICE__;
const PACKET_ID="__PACKET_ID__";
const BATCH=__BATCH__;
const SCHEMA="gold-v2-q1buttons";
const Q1V=["first","later","none"],Q2V=["AI","Student","Nobody"];
const Q1TXT={first:"在 AI 第一条回复里 / In the AI's first reply",later:"在之后的 AI 回复里 / In a later AI reply",none:"没有 / No"};
const $=id=>document.getElementById(id);
let annotator="",mode="real",idx=0,pidx=0,startedAt="",openedAt=0,advanceTimer=null,storageOK=true;
let answers=[],practice=PRACTICE.map(()=>({q1:"",q2:""})),practiceDone=false;
const blank=()=>({q1:"",q2:"",unsure:false,note:"",seconds_on_unit:0});
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function safeName(s){return String(s).trim().replace(/[^A-Za-z0-9._-]+/g,"_").replace(/^_+|_+$/g,"").slice(0,60)||"annotator";}
function skey(){return "gold_v2_q1buttons::"+PACKET_ID+"::"+annotator.toLowerCase();}
function nReplies(u){return u.messages.filter(m=>m.role==="AI").length;}
function allowedQ1(u){const n=nReplies(u);return n===0?["none"]:(n===1?["first","none"]:Q1V);}
function complete(a){return !!a&&Q1V.includes(a.q1)&&Q2V.includes(a.q2);}
function partial(a){return !!a&&!complete(a)&&(a.q1!==""||a.q2!=="");}
function save(){if(!annotator)return;try{localStorage.setItem(skey(),JSON.stringify({schema_version:SCHEMA,packet_id:PACKET_ID,annotator,answers,idx,started_at:startedAt,practice,practice_done:practiceDone,when:new Date().toISOString()}));$("saveState").textContent="✓ 已自动保存 / autosaved";}catch(e){storageOK=false;$("saveState").textContent="⚠ 无法自动保存，请经常导出 / autosave unavailable: export often";}}
function restore(){answers=UNITS.map(()=>blank());startedAt=new Date().toISOString();try{const x=JSON.parse(localStorage.getItem(skey())||"null");if(x&&x.schema_version===SCHEMA&&x.packet_id===PACKET_ID&&Array.isArray(x.answers)&&x.answers.length===UNITS.length){answers=x.answers.map(a=>Object.assign(blank(),a));idx=Math.max(0,Math.min(UNITS.length-1,Number(x.idx)||0));startedAt=x.started_at||startedAt;if(Array.isArray(x.practice)&&x.practice.length===PRACTICE.length)practice=x.practice.map(p=>({q1:p.q1||"",q2:p.q2||""}));practiceDone=!!x.practice_done;return true;}}catch(e){storageOK=false;}return false;}
function cur(){return mode==="real"?answers[idx]:practice[pidx];}
function unit(){return mode==="real"?UNITS[idx]:PRACTICE[pidx];}
function tick(){if(mode!=="real"||!openedAt)return;const now=Date.now();answers[idx].seconds_on_unit=(answers[idx].seconds_on_unit||0)+Math.max(0,Math.round((now-openedAt)/1000));openedAt=now;}
function show(id){["sStart","sGuide","sWork"].forEach(s=>$(s).classList.toggle("hidden",s!==id));window.scrollTo(0,0);}
function renderLeft(u){let h="<h3 style='margin-top:0'>题目 / Problem</h3><div class='problem'>"+esc(u.problem)+"</div><h3>解题步骤（含结果） / Solution steps with results</h3>";if(!u.steps.length)h+="<p class='muted'>（本题没有列出的中间步骤 → Q1 一定是“没有” / (No listed intermediate steps → Q1 is No)</p>";u.steps.forEach(s=>{h+="<div class='step'><b>"+s.n+".</b><span>"+esc(s.text)+"</span></div>";});h+="<div class='final'><b>正确最终答案 / Correct final answer:</b><br>"+esc(u.final)+"</div>";$("left").innerHTML=h;}
function renderMsgs(u){let h="";u.messages.forEach((m,i)=>{if(m.chat_start&&i>0)h+="<div class='chat'>— 新的对话 / new chat —</div>";if(m.role==="AI")h+="<div class='msg ai'><div class='who'>AI reply "+m.reply+"</div>"+esc(m.text)+"</div>";else h+="<div class='msg st'><div class='who'>Student</div>"+esc(m.text)+"</div>";});if(!u.messages.length)h="<p class='muted'>(empty)</p>";$("msgs").innerHTML=h;}
function renderBar(){const a=cur(),u=unit(),ok=allowedQ1(u),n=nReplies(u);["q1f","q1l","q1n"].forEach(id=>{const v=$(id).dataset.q1;$(id).classList.toggle("on",a.q1===v);$(id).disabled=!ok.includes(v);});["q2a","q2s","q2o"].forEach(id=>$(id).classList.toggle("on",$(id).dataset.l2===a.q2));const h=$("q1hint");h.className="muted";h.textContent=n===0?"本题没有 AI 回复，Q1 只能选“没有” / No AI reply in this unit: Q1 can only be No":(n===1?"本题只有 1 条 AI 回复，“之后的回复”不可用 / Only one AI reply here: “later reply” is disabled":"");
const real=mode==="real";$("unsure").disabled=!real;$("note").disabled=!real;$("unsure").checked=real&&!!a.unsure;if(document.activeElement!==$("note"))$("note").value=real?(a.note||""):"";
$("prevBtn").disabled=real?idx===0:pidx===0;
if(real){$("nextBtn").textContent="Next →";$("nextBtn").disabled=idx===UNITS.length-1;}else{$("nextBtn").disabled=!complete(a);$("nextBtn").textContent=pidx<PRACTICE.length-1?"下一道练习 / Next practice →":"开始正式标注 / Start the batch →";}
renderFeedback();}
function renderFeedback(){const fb=$("fb");if(mode!=="practice"){fb.innerHTML="";return;}const a=practice[pidx],p=PRACTICE[pidx];if(!complete(a)){fb.innerHTML="<div class='muted' style='margin-top:6px'>练习：两题答完后显示反馈 / Practice: feedback appears after both answers</div>";return;}const ok=a.q1===p.answer.q1&&a.q2===p.answer.q2;const yours="Q1 = "+Q1TXT[a.q1]+", Q2 = "+a.q2;const right="Q1 = "+Q1TXT[p.answer.q1]+", Q2 = "+p.answer.q2;fb.innerHTML="<div class='fb "+(ok?"ok":"wrong")+"'><b>"+(ok?"✓ 正确 / Correct":"✗ 不完全对 / Not quite")+"</b><br>你的 / Yours: "+esc(yours)+"<br>答案 / Answer: "+esc(right)+"<br>"+esc(p.reason)+"</div>";}
function renderStrip(){if(mode!=="real"){$("strip").innerHTML="";return;}$("strip").innerHTML=UNITS.map((u,i)=>{const a=answers[i];let c=complete(a)?"done":(partial(a)?"part":"");if(i===idx)c+=" cur";if(a.unsure)c+=" uns";return "<button class='"+c+"' data-i='"+i+"' title='Unit "+u.unit_no+"'>"+u.unit_no+"</button>";}).join("");$("strip").querySelectorAll("button").forEach(b=>b.onclick=()=>go(Number(b.dataset.i)));}
function renderTop(){const done=answers.filter(complete).length;if(mode==="real"){$("tTitle").textContent="Batch "+BATCH+" · Unit "+UNITS[idx].unit_no+" / "+UNITS.length;$("tProg").textContent="完成 / done "+done+" / "+UNITS.length;}else{$("tTitle").textContent="练习 / Practice "+(pidx+1)+" / "+PRACTICE.length;$("tProg").textContent="";}$("tWho").textContent="· "+annotator;$("doneBanner").classList.toggle("hidden",!(mode==="real"&&done===UNITS.length));$("exportBtn").disabled=mode!=="real";renderStrip();}
function render(){const u=unit();renderLeft(u);renderMsgs(u);renderBar();renderTop();openedAt=Date.now();}
function go(i){if(mode!=="real")return;clearTimeout(advanceTimer);tick();idx=Math.max(0,Math.min(UNITS.length-1,i));save();render();window.scrollTo(0,0);$("left").scrollTop=0;}
function changed(wasComplete){const a=cur();save();renderBar();renderTop();if(mode==="real"&&!wasComplete&&complete(a)&&idx<UNITS.length-1){clearTimeout(advanceTimer);advanceTimer=setTimeout(()=>go(idx+1),650);}}
function setQ1(v){if(!allowedQ1(unit()).includes(v))return;const a=cur(),w=complete(a);a.q1=v;changed(w);}
function setQ2(v){const a=cur(),w=complete(a);a.q2=v;changed(w);}
function startWork(){mode="real";show("sWork");render();}
function startPractice(){mode="practice";pidx=0;show("sWork");render();}
function begin(){const n=$("name").value.trim();if(!n){$("startErr").textContent="请填写名字或代号 / Please enter a name or code";$("startErr").classList.remove("hidden");return;}annotator=n;const had=restore();if(had&&practiceDone)startWork();else show("sGuide");}
function exportRows(){return UNITS.map((u,i)=>{const a=answers[i];return {unit_no:u.unit_no,unit_key_hash:u.unit_key_hash,q1:Q1V.includes(a.q1)?a.q1:"",q2:Q2V.includes(a.q2)?a.q2:"",unsure:!!a.unsure,note:String(a.note||""),seconds_on_unit:Math.round(a.seconds_on_unit||0)};});}
function exportObj(){tick();const rows=exportRows(),n=rows.filter((r,i)=>complete(answers[i])).length;return {schema_version:SCHEMA,packet_id:PACKET_ID,batch:BATCH,annotator,started_at:startedAt,exported_at:new Date().toISOString(),n_units:UNITS.length,n_complete:n,complete:n===UNITS.length,practice:PRACTICE.map((p,i)=>({no:p.no,q1:practice[i].q1,q2:practice[i].q2})),labels:rows};}
function stamp(d){const p=x=>String(x).padStart(2,"0");return d.getFullYear()+p(d.getMonth()+1)+p(d.getDate())+"-"+p(d.getHours())+p(d.getMinutes());}
function exportJSON(){const o=exportObj();if(!o.complete&&!window.confirm("还有 "+(o.n_units-o.n_complete)+" 题未完成，仍然导出吗？ / "+(o.n_units-o.n_complete)+" units are not finished. Export anyway?"))return;const name="gold_batch"+BATCH+"_"+safeName(annotator)+"_"+stamp(new Date())+".json";const blob=new Blob([JSON.stringify(o,null,1)+"\n"],{type:"application/json"});const l=document.createElement("a");l.href=URL.createObjectURL(blob);l.download=name;document.body.appendChild(l);l.click();setTimeout(()=>{URL.revokeObjectURL(l.href);l.remove();},1500);save();}
function importJSON(file){const rd=new FileReader();rd.onload=()=>{try{const x=JSON.parse(rd.result);if(x.schema_version!==SCHEMA)throw Error("schema");if(x.packet_id!==PACKET_ID)throw Error("这是另一批的文件 / file is from a different batch");if(String(x.annotator).toLowerCase()!==annotator.toLowerCase())throw Error("名字不一致 / annotator name differs");if(!Array.isArray(x.labels)||x.labels.length!==UNITS.length)throw Error("label count");x.labels.forEach(r=>{const i=UNITS.findIndex(u=>u.unit_no===Number(r.unit_no)&&u.unit_key_hash===r.unit_key_hash);if(i<0)throw Error("unit mismatch");const q1=Q1V.includes(r.q1)&&allowedQ1(UNITS[i]).includes(r.q1)?r.q1:"";answers[i]=Object.assign(blank(),{q1,q2:Q2V.includes(r.q2)?r.q2:"",unsure:!!r.unsure,note:r.note||"",seconds_on_unit:Number(r.seconds_on_unit)||0});});startedAt=x.started_at||startedAt;practiceDone=true;save();startWork();alert("已导入 / Imported");}catch(e){alert("导入失败 / Import failed: "+e.message);}};rd.readAsText(file);}
function openGuide(){$("modalBody").innerHTML=$("guideBody").innerHTML;const b=$("modalBody").querySelector("#guideBtns");if(b)b.remove();$("modal").classList.remove("hidden");}
$("startBtn").onclick=begin;$("name").addEventListener("keydown",e=>{if(e.key==="Enter")begin();});
$("toPractice").onclick=startPractice;
["q1f","q1l","q1n"].forEach(id=>$(id).onclick=()=>setQ1($(id).dataset.q1));
["q2a","q2s","q2o"].forEach(id=>$(id).onclick=()=>setQ2($(id).dataset.l2));
$("unsure").onchange=e=>{if(mode!=="real")return;answers[idx].unsure=e.target.checked;save();renderStrip();};
$("note").oninput=e=>{if(mode!=="real")return;answers[idx].note=e.target.value;save();};
$("prevBtn").onclick=()=>{if(mode==="real")go(idx-1);else if(pidx>0){pidx--;render();}};
$("nextBtn").onclick=()=>{if(mode==="real")go(idx+1);else{if(!complete(practice[pidx]))return;if(pidx<PRACTICE.length-1){pidx++;render();}else{practiceDone=true;save();startWork();}}};
$("exportBtn").onclick=exportJSON;$("importBtn").onclick=()=>$("importFile").click();$("importFile").onchange=e=>{if(e.target.files[0])importJSON(e.target.files[0]);e.target.value="";};
$("guideBtn").onclick=openGuide;$("closeModal").onclick=()=>$("modal").classList.add("hidden");
document.addEventListener("keydown",e=>{if($("sWork").classList.contains("hidden")||!$("modal").classList.contains("hidden"))return;const t=e.target;if(t&&(t.tagName==="INPUT"||t.tagName==="TEXTAREA"))return;if(e.ctrlKey||e.metaKey||e.altKey)return;const k=e.key.toLowerCase();if(k==="1")setQ1("first");else if(k==="2")setQ1("later");else if(k==="3")setQ1("none");else if(k==="a")setQ2("AI");else if(k==="s")setQ2("Student");else if(k==="o")setQ2("Nobody");else if(e.key==="ArrowRight"){if(mode==="real")go(idx+1);}else if(e.key==="ArrowLeft"){if(mode==="real")go(idx-1);}else return;e.preventDefault();});
document.addEventListener("visibilitychange",()=>{if(document.hidden)tick();else openedAt=Date.now();});
window.addEventListener("beforeunload",()=>{tick();save();});
</script></body></html>
