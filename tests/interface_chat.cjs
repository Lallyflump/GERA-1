/* Synthetic interaction tests with DOM doubles; no real browser or provider. */
async function runChatInterfaceTests(source, browniePayload, createHarness) {
  const passed=[];
  const clone=value=>JSON.parse(JSON.stringify(value));
  const assert=(value,message)=>{if(!value)throw Error(message);};
  const reply=(text='Hello! Let’s explore your fictional idea.',status='live')=>({mode:'conversation',chat:{status,model_used:status==='live',read_only:true,reply:text}});
  const response=body=>({ok:true,status:200,json:async()=>clone(body)});
  const setup=options=>{const s=createHarness(source,browniePayload,{fetcher:async()=>response(reply()),...options});s.api.finish();return s;};
  async function test(name,fn){await fn();passed.push(name);}
  await test('Ordinary chat sends only the deliberate message and chat history',async()=>{
    const s=setup();await s.api.sendTobyMessage('Hello Toby');
    assert(s.requests.length===1&&s.requests[0].url==='/api/chat','Wrong endpoint');
    const body=JSON.parse(s.requests[0].options.body);
    assert(Object.keys(body).sort().join()==='history,message','Extra payload fields');
    assert(body.message==='Hello Toby'&&body.history.length===0,'Wrong message/history');
    assert(!s.requests[0].options.body.includes('BROWSER_PRIVATE_SENTINEL'),'Business data sent');
    assert(s.el('messages').textContent.includes('fictional idea'),'Reply missing');
    assert(s.el('chatFoot').textContent.includes('Nemotron reply'),'Missing live label');
    assert(s.cards.size===0&&!s.el('coordView').classList.contains('active'),'Chat triggered delegation');
    assert(JSON.stringify([...s.storage])===s.before,'Browser storage mutated');
    assert(!s.el('chatSend').disabled,'Send stayed disabled');
  });
  await test('The existing form submits to chat without opening the coordination room',async()=>{
    const s=setup();s.el('question').value='Hello from the chat form';
    s.el('chatForm').listeners.submit({preventDefault(){}});
    for(let n=0;n<8;n++)await Promise.resolve();
    assert(s.requests[0]?.url==='/api/chat','Form did not use chat');
    assert(s.el('messages').textContent.includes('fictional idea'),'Form reply missing');
    assert(!s.el('coordView').classList.contains('active'),'Form opened demonstration');
  });
  await test('A follow-up receives recent conversation in the correct order',async()=>{
    const s=setup();await s.api.sendTobyMessage('Compare two fictional picnic ideas');
    await s.api.sendTobyMessage('Which is simpler?');
    const history=JSON.parse(s.requests[1].options.body).history;
    assert(history.length===2&&history[0].role==='user'&&history[1].role==='assistant','Wrong history roles');
    assert(history[0].content.includes('picnic')&&history[1].content.includes('fictional idea'),'Context lost');
  });
  await test('Mentioning brownies is conversation; the explicit button runs the unchanged demo',async()=>{
    const s=setup({fetcher:async url=>response(url==='/api/chat'?reply():browniePayload)});
    await s.api.sendTobyMessage('Why are brownies popular?');
    assert(s.requests[0].url==='/api/chat','Keyword hijacked chat');
    const historyBefore=JSON.stringify(s.api.getChatHistory());
    s.el('runBrownieDemo').click();for(let n=0;n<8;n++)await Promise.resolve();
    assert(s.requests[1].url==='/api/brownie-demo','Explicit demo failed');
    assert(s.el('resultTitle').textContent==='Cannot confirm · no order accepted','Demo decision changed');
    assert(JSON.stringify(s.api.getChatHistory())===historyBefore,'Demo results leaked into chat history');
    await s.api.sendTobyMessage('What did I ask you earlier?');
    assert(!s.requests[2].options.body.includes('recipe_version'),'Demo data sent to chat');
    assert(!s.requests[2].options.body.includes('Review the fixed synthetic'),'Demo prompt entered chat context');
  });
  await test('History trims complete exchanges to six and 8000 characters',async()=>{
    const s=setup();for(let i=0;i<9;i++)await s.api.sendTobyMessage('Fictional idea '+i);
    assert(s.api.getChatHistory().length===12,'More than six exchanges retained');
    assert(s.api.getChatHistory()[0].content==='Fictional idea 3','Old exchanges not removed');
    const large=setup({fetcher:async()=>response(reply('a'.repeat(2500)))});
    for(let i=0;i<8;i++)await large.api.sendTobyMessage('b'.repeat(1000));
    const h=large.api.getChatHistory();assert(h.length%2===0,'Partial exchange retained');
    assert(h.reduce((n,m)=>n+m.content.length,0)<=8000,'History character cap exceeded');
    for(const req of large.requests)assert(JSON.parse(req.options.body).history.reduce((n,m)=>n+m.content.length,0)<=8000,'Oversized history sent');
  });
  await test('Invalid, oversized and sensitive messages stay local',async()=>{
    const s=setup();for(const q of ['', 'x'.repeat(1001), 'Hi\x00', 'NEBIUS_API_KEY=synthetic-secret',
      'sk-syntheticcredential', 'fake@example.test', '+44 7700 900123'])await s.api.sendTobyMessage(q);
    assert(s.requests.length===0,'Rejected input was sent');
    assert(!s.el('messages').textContent.includes('synthetic-secret'),'Secret displayed in transcript');
    assert(s.api.getChatHistory().length===0,'Rejected input retained');
    await s.api.sendTobyMessage('An invented event on 2026-10-29');
    assert(s.requests.length===1,'Synthetic date incorrectly blocked');
  });
  await test('Model text is rendered as plain text without executing actions',async()=>{
    const text='<img src=x onerror=alert(1)> An invented picnic could have a small menu.';
    const s=setup({fetcher:async()=>response(reply(text))});await s.api.sendTobyMessage('Imagine a test');
    const bubble=s.el('messages').children.at(-1);
    assert(bubble.textContent===text&&bubble.innerHTML==='','Unsafe model rendering');
    assert(s.cards.size===0,'Model text triggered specialist cards');
    assert(JSON.stringify([...s.storage])===s.before,'Model text changed data');
    assert(s.el('chatFoot').textContent.includes('read-only'),'Read-only label missing');
  });
  await test('Percival research activity and citations render safely without entering Nemotron history',async()=>{
    const result={mode:'percival_research',status:'complete',agent:'Percival',
      activity:'Toby delegated this public research request to Percival, who searched Tavily.',
      findings:[{title:'Halloween customs',url:'https://example.org/customs',finding:'Guising and souling.'}]};
    const s=setup({fetcher:async()=>response(result)});await s.api.sendTobyMessage('Percival, research traditional Halloween customs in the British Isles and provide sources.');
    const bubble=s.el('messages').children.at(-1),link=bubble.children.find(child=>child.children.some(grandchild=>grandchild.href));
    const anchor=link.children.find(child=>child.href);
    assert(bubble.textContent.includes('Percival · Research specialist'),'Percival activity missing');
    assert(bubble.textContent.includes('Guising and souling.'),'Finding missing');
    assert(anchor.href==='https://example.org/customs'&&anchor.rel==='noopener noreferrer','Source link unsafe or missing');
    assert(s.el('chatFoot').textContent.includes('Tavily sources'),'Research mode missing');
    assert(s.api.getChatHistory().length===0,'Research output entered Nemotron conversation history');
  });
  await test('Montgomery shows a compact card, expands the full draft, and downloads a linked PDF',async()=>{
    const chain={mode:'montgomery_draft',status:'complete',agents:['Percival','Montgomery'],
      activity:['Percival searched Tavily.','Toby passed Percival’s sourced findings to Montgomery for an unpublished draft.'],
      findings:[{title:'Halloween customs',url:'https://example.org/customs',finding:'Guising and souling.'}],
      draft:{status:'offline_preview',label:'Offline draft preview · template · not AI-generated',text:'This Halloween, explore old customs with A Moment of Escape. Discover the curious stories and autumn traditions of the British Isles, and make space for a memorable seasonal escape.'}};
    const s=setup({fetcher:async()=>response(chain)});await s.api.sendTobyMessage('Montgomery please draft this');
    const bubble=s.el('messages').children.at(-1);
    const toggle=bubble.children.find(child=>child.className==='montgomery-draft-toggle');
    const full=bubble.children.find(child=>child.className==='montgomery-draft-full');
    const download=bubble.children.find(child=>child.className==='montgomery-download');
    assert(bubble.textContent.includes('Toby · Percival → Montgomery'),'Handoff activity heading missing');
    assert(bubble.textContent.includes('NOT AI-generated'),'Offline preview was mislabelled');
    assert(bubble.textContent.includes('1 Percival source included in the PDF.'),'Compact source summary missing');
    assert(toggle&&toggle.textContent.includes('Show full draft'),'Draft heading is not clickable');
    assert(full?.hidden===true,'Full draft should start collapsed');
    assert(full.hidden===true,'Full extracts should not be visible by default');
    toggle.click();
    assert(full.hidden===false&&full.textContent.includes(chain.draft.text),'Complete draft was truncated or not expanded');
    assert(s.el('messages').classList.contains('montgomery-expanded'),'Existing conversation panel did not expand for the draft');
    assert(bubble.textContent.includes('Guising and souling.'),'Source finding missing');
    assert(s.el('chatFoot').textContent.includes('not AI-generated'),'Offline mode status unclear');
    assert(download&&download.textContent==='Download PDF','PDF action missing');download.click();
    assert(s.downloads.length===1&&s.downloads[0].filename==='A-Moment-of-Escape-Halloween-Editorial-Draft.pdf','PDF did not download locally');
    assert(s.blobs[0].type==='application/pdf','Export was not a PDF');
    const pdf=s.blobs[0].parts[0];
    for(const marker of ['%PDF-1.4','A MOMENT OF ESCAPE','Traditional Halloween Customs','NOT AI-generated','This Halloween, explore old customs with A Moment of Escape.','memorable','seasonal escape.','Guising and souling.','https://example.org/customs','/Subtype /Link','EDITORIAL REVIEW REQUIRED'])assert(pdf.includes(marker),'PDF missing '+marker);
    assert((pdf.match(/\/Subtype \/Link/g)||[]).length>=1,'Source URL is not a clickable PDF link');
    const xref=Number(pdf.match(/startxref\n(\d+)/)?.[1]);assert(Number.isInteger(xref)&&pdf.slice(xref).startsWith('xref\n'),'PDF cross-reference table is invalid');
    assert(!s.el('chatFoot').textContent.includes('Nemotron reply'),'Draft was misrepresented as ordinary chat');
    assert(s.api.getChatHistory().length===0,'Research/draft result entered Nemotron conversation history');
    const generated={...chain,draft:{...chain.draft,status:'generated'}};
    const generatedUI=setup({fetcher:async()=>response(generated)});await generatedUI.api.sendTobyMessage('Montgomery please draft this');
    assert(generatedUI.el('messages').children.at(-1).children.some(child=>child.className==='montgomery-draft-status'&&child.textContent==='Live Nemotron-generated draft'),'Live draft status missing in card');
    assert(s.requests.length===1,'PDF export caused another API request');
    const multipage={...chain,findings:Array.from({length:5},(_,i)=>({title:`Historical source ${i+1}`,url:`https://example.org/source-${i+1}`,finding:'A historical note about customs across the British Isles. '.repeat(8)}))};
    const pagedPdf=s.api.buildMontgomeryPdf(multipage);assert(pagedPdf.includes('/Count 2'),'Long sources did not flow across PDF pages');assert((pagedPdf.match(/\/Subtype \/Link/g)||[]).length>=5,'A source URL lacks its own clickable annotation');
    for(let i=1;i<=5;i++)assert(pagedPdf.includes(`https://example.org/source-${i}`),'PDF omitted source '+i);
  });
  await test('Offline and fallback responses are explicit and never enter provider history',async()=>{
    for(const status of ['offline','fallback']){
      const s=setup({fetcher:async()=>response(reply('Local help only.',status))});await s.api.sendTobyMessage('Hello');
      assert(s.el('messages').textContent.includes('Offline help: Local help only.'),'Offline reply not labelled');
      assert(s.api.getChatHistory().length===0,'Offline dialogue silently queued for provider');
      assert(s.el('chatFoot').textContent.toLowerCase().includes('offline'),'Status missing');
    }
  });
  await test('file:// chat has useful local help and no network call',async()=>{
    const s=setup({protocol:'file:'});await s.api.sendTobyMessage('Who is Saul?');
    assert(s.requests.length===0,'File preview fetched');
    assert(s.el('messages').textContent.includes('Saul covers finance'),'Local help missing');
    s.api.showView('orders');assert(s.el('dataView').classList.contains('active'),'Offline navigation broke');
  });
  await test('Network failure and busy backend do not retry or leak raw errors',async()=>{
    for(const fetcher of [async()=>{throw Error('PRIVATE_ERROR_SENTINEL');},async()=>({ok:false,status:429,json:async()=>({error:'PRIVATE_ERROR_SENTINEL'})})]){
      const s=setup({fetcher});await s.api.sendTobyMessage('Hello');
      assert(s.requests.length===1,'Automatic retry');
      assert(s.el('messages').textContent.includes('Offline help'),'Fallback missing');
      assert(!s.el('messages').textContent.includes('PRIVATE_ERROR_SENTINEL'),'Raw error leaked');
      assert(s.api.getChatHistory().length===0,'Failed exchange entered history');
    }
  });
  await test('Validation errors and malformed replies never become live successes',async()=>{
    for(const fetcher of [async()=>({ok:false,status:400,json:async()=>({error_code:'sensitive_input',error:'do not echo me'})}),
      async()=>response({...reply(),chat:{...reply().chat,read_only:false}}),
      async()=>response(reply('', 'live')),async()=>response(reply('x'.repeat(2501)))]){
      const s=setup({fetcher});await s.api.sendTobyMessage('Hello');
      assert(s.api.getChatHistory().length===0,'Invalid reply remembered');
      assert(!s.el('chatFoot').textContent.startsWith('Nemotron reply'),'Invalid reply labelled live');
    }
  });
  await test('Repeated sends while pending do not create concurrent requests',async()=>{
    let resolve;const s=setup({fetcher:()=>new Promise(r=>resolve=r)});
    const pending=s.api.sendTobyMessage('First');await s.api.sendTobyMessage('Second');
    assert(s.requests.length===1&&s.el('chatSend').disabled,'Concurrent send permitted');
    resolve(response(reply()));await pending;assert(!s.el('chatSend').disabled,'Send never restored');
  });
  await test('Clearing cancels the request and ignores a late response',async()=>{
    const pending=[];const s=setup({fetcher:()=>new Promise(r=>pending.push(r))});
    const old=s.api.sendTobyMessage('Old conversation');s.el('clearConversation').click();
    assert(s.requests[0].options.signal.aborted,'Old request not cancelled');
    const current=s.api.sendTobyMessage('New conversation');
    pending[1](response(reply('New reply')));await current;
    pending[0](response(reply('Stale reply')));await old;
    assert(!s.el('messages').textContent.includes('Stale reply'),'Late response displayed');
    assert(s.api.getChatHistory()[0].content==='New conversation','Clear failed to reset history');
    assert(JSON.stringify([...s.storage])===s.before,'Clear removed bakery records');
  });
  await test('A 30-second browser timeout aborts once and provides local help',async()=>{
    let reject;const s=setup({fetcher:()=>new Promise((_,r)=>reject=r)});
    const pending=s.api.sendTobyMessage('Hello');s.flush(30000);
    assert(s.requests[0].options.signal.aborted,'Timeout did not abort');
    const error=Error('abort');error.name='AbortError';reject(error);await pending;
    assert(s.el('chatFoot').textContent.includes('timed out'),'Timeout label missing');
    assert(s.requests.length===1,'Timeout retried');
  });
  await test('The explicit handoff preview cancels chat without specialist delegation by chat',async()=>{
    let resolve;const s=setup({fetcher:()=>new Promise(r=>resolve=r)});
    const pending=s.api.sendTobyMessage('Hello');s.el('tryHandoff').click();
    resolve(response(reply('Stale chat')));await pending;s.flush();
    assert(s.requests.length===1,'Preview sent an extra request');
    assert(!s.el('messages').textContent.includes('Stale chat'),'Preview received cancelled chat');
    assert(s.el('coordState').textContent.includes('no live calls made'),'Preview lost its label');
  });
  return passed;
}
if(typeof module!=='undefined')module.exports={runChatInterfaceTests};
if(typeof require!=='undefined'&&require.main===module){
 const fs=require('node:fs'),path=require('node:path');
 const {createInterfaceHarness}=require('./interface_bridge.cjs');
 if(!process.argv[2])throw Error('Pass an offline brownie payload JSON path.');
 runChatInterfaceTests(fs.readFileSync(path.join(__dirname,'../interface/script.js'),'utf8'),JSON.parse(fs.readFileSync(process.argv[2],'utf8')),createInterfaceHarness)
 .then(names=>{names.forEach(n=>console.log('PASS '+n));console.log(names.length+' chat interaction checks passed (DOM doubles).');})
 .catch(e=>{console.error(e);process.exitCode=1;});
}
