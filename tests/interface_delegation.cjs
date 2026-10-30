/* Synthetic streamed events with DOM doubles; no browser or provider requests. */
async function runDelegationInterfaceTests(source,browniePayload,events,createHarness){
 const passed=[],question='Can we afford to make a batch of brownies?';
 const clone=v=>JSON.parse(JSON.stringify(v));
 const assert=(v,m)=>{if(!v)throw Error(m);};
 const ascii=v=>JSON.stringify(v).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))+'\n';
 const bytes=s=>Uint8Array.from(Array.from(s,c=>c.charCodeAt(0)));
 function stream(records,{chunkSize,beforeRead,rawTail='',failAt}={}){
  const strings=records.map(ascii);if(rawTail)strings.push(rawTail);
  const text=strings.join('');
  const chunks=chunkSize?Array.from({length:Math.ceil(text.length/chunkSize)},(_,i)=>text.slice(i*chunkSize,(i+1)*chunkSize)):strings;
  let index=0;const state={cancelled:false,released:false};
  return {state,ok:true,status:200,headers:{get:()=> 'application/x-ndjson; charset=utf-8'},body:{getReader:()=>({
   async read(){await beforeRead?.(index);if(index===failAt)throw Error('synthetic stream failure');return index<chunks.length?{done:false,value:bytes(chunks[index++])}:{done:true};},
   async cancel(){state.cancelled=true;},releaseLock(){state.released=true;}
  })}};
 }
 const setup=(fetcher,options={})=>{const s=createHarness(source,browniePayload,{fetcher,...options});s.api.finish();return s;};
 const agent=(s,id)=>s.agents.find(a=>a.dataset.agent===id);
 const working=s=>s.agents.some(a=>a.classList.contains('working'));
 async function test(name,fn){await fn();passed.push(name);}

 await test('Only actual received starts illuminate the corresponding gemstone',async()=>{
  let s;
  const response=stream(events,{beforeRead:async i=>{
   if(i===1)assert(!working(s),'Planning illuminated a gem');
   if(i===2){assert(agent(s,'bobathan').classList.contains('working'),'Bobathan did not light');assert(!agent(s,'saul').classList.contains('working'),'Saul lit before invocation');}
   if(i===3){assert(agent(s,'bobathan').classList.contains('complete'),'Bobathan result missing');assert(!agent(s,'saul').classList.contains('working'),'Finance started early');}
   if(i===4)assert(agent(s,'saul').classList.contains('working'),'Saul did not light');
  }});
  s=setup(async()=>response);await s.api.sendTobyMessage(question);
  assert(s.requests.length===1&&s.requests[0].url==='/api/chat','Wrong request path');
  assert(s.el('resultTitle').textContent.includes('Cannot confirm batch affordability'),'Wrong conclusion');
  assert(s.el('chatFoot').textContent.includes('no model call'),'Mislabelled as Nemotron');
  assert(s.el('messages').textContent.includes('not financial approval'),'Approval boundary missing');
  assert(s.cards.size===2&&!s.cards.has('galgali'),'Uninvoked specialists shown');
  assert(s.timers.size===0,'Timed animation/replay scheduled');
  assert(s.api.getChatHistory().length===0,'Specialist evidence entered model history');
  assert(!s.requests[0].options.body.includes('BROWSER_PRIVATE_SENTINEL'),'Browser records sent');
  assert(JSON.stringify([...s.storage])===s.before,'Browser records changed');
  assert(response.state.released,'Reader lock retained');
 });
 await test('JSON lines split across arbitrary network chunks preserve Unicode and results',async()=>{
  const s=setup(async()=>stream(events,{chunkSize:3}));await s.api.sendTobyMessage(question);
  assert(s.el('resultBody').textContent===events.at(-1).assessment.reply,'Chunk parser damaged text');
  assert(s.cards.get('bobathan').querySelector('.handoff-status').textContent.includes('information missing'),'Unknowns lost');
 });
 await test('Pending chat and generated claims never light a specialist without events',async()=>{
  let resolve;const s=setup(()=>new Promise(r=>resolve=r));
  const pending=s.api.sendTobyMessage(question);assert(!working(s)&&s.cards.size===0,'Browser inferred delegation');
  resolve({ok:true,status:200,json:async()=>({mode:'conversation',chat:{status:'live',model_used:true,read_only:true,reply:'Bobathan says all done.'}})});
  await pending;assert(!working(s)&&s.cards.size===0,'Model text drove gemstone');
 });
 await test('Unsupported scope remains useful without fabricating activity',async()=>{
  const s=setup(async()=>({ok:true,status:200,json:async()=>({mode:'conversation',chat:{status:'scope',model_used:false,read_only:true,reply:'Only one synthetic batch is supported. No specialists were invoked.'}})}));
  await s.api.sendTobyMessage('Can we afford two batches of brownies?');
  assert(s.el('chatFoot').textContent.includes('no specialist or model call'),'Scope label wrong');
  assert(s.cards.size===0&&!working(s),'Scope response lit specialists');
 });
 await test('Denied checks have no working or completed glow and no fabricated finance',async()=>{
  const last=clone(events.at(-1));last.sequence=3;
  Object.assign(last.assessment,{status:'blocked',specialists:{bobathan:'denied',saul:'skipped'},findings:{},reply:'The stock check was denied. No finance assessment or approval was obtained.'});
  const records=[events[0],{...events[1],event:'specialist_result',status:'denied'},last];
  const s=setup(async()=>stream(records));await s.api.sendTobyMessage(question);
  assert(!working(s)&&!s.agents.some(a=>a.classList.contains('complete')),'Denied check illuminated a gem');
  assert(s.el('coordState').textContent.includes('blocked or partial'),'Denial hidden');
  assert(!agent(s,'saul').classList.contains('flipped'),'Uninvoked finance displayed a gemstone');
 });
 await test('A failed finance check retains only the actual earlier stock check',async()=>{
  const records=clone(events);records[4].status='error';
  Object.assign(records[5].assessment,{status:'blocked',specialists:{bobathan:'needs_information',saul:'error'},reply:'Bobathan returned stock findings. Saul was unavailable. No financial approval.'});
  delete records[5].assessment.findings.saul;
  const s=setup(async()=>stream(records));await s.api.sendTobyMessage(question);
  assert(agent(s,'bobathan').classList.contains('complete'),'Actual returned check lost');
  assert(!agent(s,'saul').classList.contains('complete')&&!working(s),'Failed check shown complete');
  assert(s.el('resultBody').textContent.includes('unavailable'),'Failure hidden');
 });
 await test('Missing final, stream failure and malformed JSON cannot leave gems working',async()=>{
  for(const response of [stream(events.slice(0,2)),stream(events,{failAt:2}),stream(events.slice(0,2),{rawTail:'not json\n'})]){
   const s=setup(async()=>response);await s.api.sendTobyMessage(question);
   assert(!working(s),'Interrupted activity remained working');
   assert(s.el('resultTitle').textContent==='No confirmed assessment','Interrupted stream claimed success');
   assert(s.requests.length===1&&!s.el('chatSend').disabled,'Retried or disabled chat');
  }
 });
 await test('Wrong request, sequence, agent, premature completion and fake findings are rejected',async()=>{
  const cases=[];
  for(const mutation of [r=>r[2].request_id='synthetic-chat-'+'b'.repeat(32),r=>r[2].sequence=7,r=>r[1].agent='ivy',r=>r[1]={...r[2],sequence:2},r=>r[5].assessment.recommendation='approved',r=>delete r[5].assessment.findings.saul.audit_id,r=>r[5].assessment.missing=[{}]]){
   const records=clone(events);mutation(records);cases.push(records);
  }
  cases.push([...clone(events),clone(events.at(-1))]);
  for(const records of cases){
   const s=setup(async()=>stream(records));await s.api.sendTobyMessage(question);
   assert(!working(s),'Invalid stream left working gem');
   assert(s.el('resultTitle').textContent==='No confirmed assessment','Invalid stream accepted');
   assert(s.api.getChatHistory().length===0,'Invalid result entered context');
  }
 });
 await test('Oversized streams fail safely',async()=>{
  const s=setup(async()=>stream(events.slice(0,2),{rawTail:'x'.repeat(33000)}));await s.api.sendTobyMessage(question);
  assert(!working(s)&&s.el('resultTitle').textContent==='No confirmed assessment','Stream limit ignored');
 });
 await test('Clear and navigation cancel activity and discard late stream events',async()=>{
  for(const action of [s=>s.el('clearConversation').click(),s=>s.api.showView('home')]){
   let resume,paused;const reached=new Promise(r=>paused=r),gate=new Promise(r=>resume=r);
   const response=stream(events,{beforeRead:async i=>{if(i===2){paused();await gate;}}});
   const s=setup(async()=>response);const pending=s.api.sendTobyMessage(question);await reached;
   action(s);const before=s.el('messages').textContent;resume();await pending;
   assert(s.requests[0].options.signal.aborted,'Pending request not aborted');
   assert(!working(s),'Cancelled gem remained working');
   assert(s.el('messages').textContent===before,'Late response overwrote conversation');
   assert(response.state.cancelled,'Reader not cancelled');
  }
 });
 await test('Timeout interrupts once without retry or late completion',async()=>{
  let resume,paused;const reached=new Promise(r=>paused=r),gate=new Promise(r=>resume=r);
  let s;const response=stream(events,{beforeRead:async i=>{if(i===2){paused();await gate;if(s.requests[0].options.signal.aborted){const e=Error('aborted');e.name='AbortError';throw e;}}}});
  s=setup(async()=>response);const pending=s.api.sendTobyMessage(question);await reached;s.flush(30000);resume();await pending;
  assert(!working(s)&&s.requests.length===1,'Timeout leaked work or retried');
  assert(s.el('chatFoot').textContent.includes('timed out'),'Timeout not explained');
 });
 await test('Reduced motion uses the same genuine events without replay timers',async()=>{
  const s=createHarness(source,browniePayload,{reduced:true,fetcher:async()=>stream(events)});s.api.finish();await s.api.sendTobyMessage(question);
  assert(agent(s,'saul').classList.contains('complete')&&!working(s),'Reduced motion lost results');
  assert(s.timers.size===0,'Delayed simulation created');
 });
 await test('Brownie demonstration still runs independently after delegation',async()=>{
  const s=setup(async url=>url==='/api/chat'?stream(events):{ok:true,status:200,json:async()=>clone(browniePayload)});
  await s.api.sendTobyMessage(question);s.el('runBrownieDemo').click();for(let n=0;n<12;n++)await Promise.resolve();
  assert(s.requests[1].url==='/api/brownie-demo','Demo rerouted');
  assert(s.el('activityNote').textContent.includes('replay'),'Demo replay not labelled');
  assert(!s.el('rerunCoord').disabled,'Demo rerun disabled');
  assert(s.el('resultTitle').textContent==='Cannot confirm · no order accepted','Demo decision changed');
 });
 await test('Both specialist buttons focus their current assessment without cancelling, including reduced motion',async()=>{
  for(const reduced of [false,true]){
   let s;
   const response=stream(events,{beforeRead:async i=>{
    if(i!==2&&i!==4)return; // After each real started event, before its result.
    for(const id of ['bobathan','saul']){
     const card=s.cards.get(id);let focused=false;card.scrollIntoView=()=>{focused=true;};
     agent(s,id).click();
     assert(focused&&card.classList.contains('focus-agent'),'Specialist button did not focus its card');
     assert(s.el('coordView').classList.contains('active'),'Specialist click left the assessment');
     assert(!s.requests[0].options.signal.aborted,'Specialist click cancelled the workflow');
    }
    assert(agent(s,i===2?'bobathan':'saul').classList.contains('working'),'Focus changed actual activity state');
    if(i===2)assert(!agent(s,'saul').classList.contains('flipped'),'Focus fabricated a Saul invocation');
   }});
   s=setup(async()=>response,{reduced});await s.api.sendTobyMessage(question);s.flush(900);
   assert(s.el('resultTitle').textContent.includes('Cannot confirm batch affordability'),'Assessment did not finish');
   assert(s.requests.length===1&&!working(s),'Extra request or unfinished gemstone');
  }
 });
 await test('Navigation before response headers suppresses late delegation, even after returning to the original view',async()=>{
  for(const reduced of [false,true])for(const returnHome of [false,true]){
   let resolve;const response=stream(events);
   const s=setup(()=>new Promise(r=>resolve=r),{reduced});
   const pending=s.api.sendTobyMessage(question);
   s.api.showView('calendar');if(returnHome)s.api.showView('home');
   const view=returnHome?'homeView':'calendarView',before=s.el('messages').textContent;
   resolve(response);await pending;
   assert(s.el(view).classList.contains('active')&&!s.el('coordView').classList.contains('active'),'Late response hijacked navigation');
   assert(s.cards.size===0&&!working(s),'Cancelled response displayed specialist activity');
   assert(s.el('messages').textContent===before,'Late assessment entered conversation');
   assert(s.requests[0].options.signal.aborted&&response.state.cancelled,'Late delegation was not cancelled');
   assert(!s.el('chatSend').disabled&&s.requests.length===1,'Send disabled or request retried');
  }
 });
 await test('Navigation after headers but before the first event also suppresses delegation',async()=>{
  for(const reduced of [false,true]){
   let resume,paused;const reached=new Promise(r=>paused=r),gate=new Promise(r=>resume=r);
   const response=stream(events,{beforeRead:async i=>{if(i===0){paused();await gate;}}});
   const s=setup(async()=>response,{reduced});const pending=s.api.sendTobyMessage(question);await reached;
   s.api.showView('calendar');resume();await pending;
   assert(s.el('calendarView').classList.contains('active')&&s.cards.size===0,'First event overrode navigation');
   assert(!working(s)&&s.requests[0].options.signal.aborted&&response.state.cancelled,'Stream was not interrupted safely');
  }
 });
 await test('After focusing a specialist, clear and navigation still interrupt correctly in both motion modes',async()=>{
  for(const reduced of [false,true])for(const action of [s=>s.el('clearConversation').click(),s=>s.api.showView('calendar')]){
   let resume,paused;const reached=new Promise(r=>paused=r),gate=new Promise(r=>resume=r);
   const response=stream(events,{beforeRead:async i=>{if(i===2){paused();await gate;}}});
   const s=setup(async()=>response,{reduced});const pending=s.api.sendTobyMessage(question);await reached;
   agent(s,'bobathan').click();assert(!s.requests[0].options.signal.aborted,'Focus interrupted the request');
   action(s);const before=s.el('messages').textContent;resume();await pending;s.flush(900);
   assert(s.requests[0].options.signal.aborted&&response.state.cancelled,'User cancellation failed');
   assert(!working(s)&&s.el('messages').textContent===before,'Stale event survived cancellation');
   assert(s.el('resultTitle').textContent==='No confirmed assessment','Interrupted result shown complete');
   assert(!s.el('chatSend').disabled,'Send stayed disabled');
  }
 });
 await test('Ordinary conversation still returns across navigation without opening specialist activity',async()=>{
  for(const reduced of [false,true]){
   let resolve;const s=setup(()=>new Promise(r=>resolve=r),{reduced});
   const pending=s.api.sendTobyMessage('Hello Toby');s.api.showView('calendar');
   resolve({ok:true,status:200,json:async()=>({mode:'conversation',chat:{status:'live',model_used:true,read_only:true,reply:'Hello! Let’s discuss an invented example.'}})});
   await pending;
   assert(s.el('calendarView').classList.contains('active'),'Ordinary reply changed the view');
   assert(!s.requests[0].options.signal.aborted&&s.api.getChatHistory().length===2,'Ordinary conversation was cancelled or lost context');
   assert(s.cards.size===0&&!working(s),'Ordinary reply fabricated activity');
  }
 });
 return passed;
}
if(typeof module!=='undefined')module.exports={runDelegationInterfaceTests};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const {createInterfaceHarness}=require('./interface_bridge.cjs');
 if(!process.argv[2]||!process.argv[3])throw Error('Pass offline brownie payload and synthetic delegation event JSON paths.');
 runDelegationInterfaceTests(fs.readFileSync(path.join(__dirname,'../interface/script.js'),'utf8'),JSON.parse(fs.readFileSync(process.argv[2],'utf8')),JSON.parse(fs.readFileSync(process.argv[3],'utf8')),createInterfaceHarness)
 .then(passed=>{passed.forEach(name=>console.log('PASS '+name));console.log(passed.length+' delegation checks passed (DOM doubles).');})
 .catch(error=>{console.error(error);process.exitCode=1;});
}
