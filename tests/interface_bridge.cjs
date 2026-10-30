function createInterfaceHarness(source, payload, {protocol='http:',reduced=false,fetcher}={}) {
    const clone=value=>JSON.parse(JSON.stringify(value));
    const elements=new Map(), cards=new Map(), timers=new Map(), storage=new Map(), downloads=[],blobs=[];
    let nextTimer=0;
    class Element {
      constructor(id='') { this.id=id;this.children=[];this.listeners={};this.hidden=false;this.value='';this.dataset={};this._text='';this._html='';this.style={setProperty(){},removeProperty(){}};const classes=new Set();this.classList={add(...v){v.forEach(x=>classes.add(x));},remove(...v){v.forEach(x=>classes.delete(x));},contains(v){return classes.has(v);},toggle(v,on){if(on===undefined)on=!classes.has(v);on?classes.add(v):classes.delete(v);return on;}}; }
      set textContent(value) {this._text=String(value);this.children=[];}
      get textContent() {return this._text+this.children.map(e=>e.textContent).join('');}
      set innerHTML(value) {
        this._html=value;
        if(this.id==='handoffGrid') {cards.clear();for(const match of value.matchAll(/data-id="([^"]+)"/g)){const card=new Element(match[1]);cards.set(match[1],card);}}
      }
      get innerHTML() {return this._html;}
      set className(value) {this._className=value;}
      get className() {return this._className||'';}
      appendChild(e) {this.children.push(e);e.parent=this;return e;}
      append(...els) {els.forEach(e=>this.appendChild(e));}
      insertBefore(e) {this.children.push(e);}
      replaceChildren(...els) {this.children=els;this._text='';}
      querySelector(selector) {if(!this.parts)this.parts=new Map();if(!this.parts.has(selector))this.parts.set(selector,new Element());return this.parts.get(selector);}
      addEventListener(name,fn) {this.listeners[name]=fn;}
      click() {if(this.download)downloads.push({href:this.href,filename:this.download});this.listeners.click?.({preventDefault(){}});}
      remove() {if(this.parent)this.parent.children=this.parent.children.filter(e=>e!==this);}
      setAttribute(key,value) {this[key]=value;}
      removeAttribute() {}
      getBoundingClientRect() {return {left:0,top:0,width:100,height:100};}
      scrollIntoView() {}
      showModal() {this.open=true;}
      close() {this.open=false;}
    }
    const el=id=>{if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);};
    const agents=['toby','bobathan','saul','galgali','ivy','thibault'].map(id=>{const e=new Element();e.dataset.agent=id;return e;});
    const nav=['home','front','ingredients','orders','finance','calendar'].map(id=>{const e=new Element();e.dataset.view=id;return e;});
    const document={body:new Element('body'),getElementById:el,createElement:()=>new Element(),
      querySelectorAll(selector){if(selector==='.agent'||selector==='[data-agent]')return agents;if(selector==='.nav'||selector==='[data-view]')return nav;if(selector==='.view')return ['homeView','dataView','calendarView','coordView'].map(el);return [];},
      querySelector(selector){const agent=selector.match(/\.agent\[data-agent="([^"]+)"\]/);if(agent)return agents.find(e=>e.dataset.agent===agent[1]);const card=selector.match(/\.handoff-card\[data-id="([^"]+)"\](.*)/);if(card){const e=cards.get(card[1]);return card[2].trim()?e?.querySelector(card[2].trim()):e;}return null;}};
    const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)};
    storage.set('gera1-bakery-interface-preview-v2',JSON.stringify({orders:[{reference:'BROWSER_PRIVATE_SENTINEL'}]}));
    const before=JSON.stringify([...storage]);
    const requests=[];
    const fetch=async (url,options)=>{requests.push({url,options});return fetcher?fetcher(url,options):{ok:true,status:200,json:async()=>clone(payload)};};
    const setTimeout=(fn,ms)=>{const id=++nextTimer;timers.set(id,{fn,ms});return id;};
    const clearTimeout=id=>timers.delete(id);
    class Controller {constructor(){this.signal={aborted:false};}abort(){this.signal.aborted=true;}}
    class FakeBlob {constructor(parts,options){this.parts=parts;this.type=options.type;blobs.push(this);}}
    function FakeURL(value){const match=String(value).match(/^([a-z][a-z0-9+.-]*):\/\/([^/?#]*)/i);this.protocol=match?match[1].toLowerCase()+':':'';const authority=match?match[2]:'';const parts=authority.split('@');this.username=parts.length>1?parts[0].split(':')[0]:'';this.password=parts.length>1&&parts[0].includes(':')?parts[0].split(':').slice(1).join(':'):'';this.href=String(value)}
    FakeURL.createObjectURL=()=>`blob:montgomery-${blobs.length}`;FakeURL.revokeObjectURL=()=>{};
    const browser={location:{protocol},matchMedia:()=>({matches:reduced}),scrollTo(){},Blob:FakeBlob,URL:FakeURL};
    const api=new Function('document','window','localStorage','fetch','setTimeout','clearTimeout','AbortController','confirm',source+'\nreturn {startCoordination,showView,finish,intro,stopCoordination, getRun:()=>coordRun,sendTobyMessage,cancelChat,getChatHistory:()=>chatHistory,buildMontgomeryPdf,downloadMontgomeryPdf};')(
      document,browser,localStorage,fetch,setTimeout,clearTimeout,Controller,()=>true);
    function flush(limit=Infinity){let count=0;while(true){const entries=[...timers].filter(([,t])=>t.ms<=limit).sort((a,b)=>a[1].ms-b[1].ms);if(!entries.length)return;const [id,t]=entries[0];timers.delete(id);t.fn();if(++count>100)throw Error('Timer loop');}}
    return {api,el,cards,agents,requests,flush,timers,storage,before,downloads,blobs};
  }

/* No dependencies. Run with Node, or call runInterfaceTests(source, payload) in V8.
   DOM doubles test interaction logic; they do not verify browser rendering. */
async function runInterfaceTests(source, payload) {
  const passed=[];
  const clone=value=>JSON.parse(JSON.stringify(value));
  function assert(condition, message) { if(!condition) throw Error(message); }
  const setup=options=>createInterfaceHarness(source,payload,options);
  async function test(name, fn) {await fn();passed.push(name);}
  await test('Model commentary is plain text, decision remains separate, browser records stay local',async()=>{
    const body=clone(payload);body.toby.status='live';body.toby.model_used=true;body.toby.explanation='<img src=x onerror=alert(1)> Approved!';
    const s=setup({fetcher:async()=>({ok:true,status:200,json:async()=>body})});s.api.finish();
    await s.api.startCoordination('Can I order 999 brownies tomorrow?');
    assert(s.el('resultBody').textContent.includes(body.toby.explanation),'Missing model text');
    assert(s.el('resultBody').innerHTML==='','Model text assigned as HTML');
    assert(s.el('resultTitle').textContent==='Cannot confirm · no order accepted','Decision changed');
    assert(s.el('resultDetails').textContent.includes('production capacity'),'Missing checks hidden');
    assert(s.el('resultDetails').textContent.includes('13-piece'),'Fixed scenario not disclosed');
    assert(JSON.parse(s.requests[0].options.body).question.includes('999'),'Question missing');
    assert(Object.keys(JSON.parse(s.requests[0].options.body)).join()==='question','Browser data sent');
    assert(JSON.stringify([...s.storage])===s.before,'Preview storage changed');
    s.flush();assert(!s.cards.has('ivy'),'Ivy falsely called');
    assert(s.cards.get('galgali').querySelector('.handoff-task').textContent.includes('financial calendar'),'Wrong Galgali scope');
    assert(s.cards.get('bobathan').querySelector('.handoff-status').textContent.includes('information missing'),'Unknowns hidden by completion');
  });
  await test('Offline and provider-fallback responses are labelled accurately',async()=>{
    for(const status of ['offline','fallback']){
      const body=clone(payload);body.toby.status=status;body.toby.model_used=false;
      const s=setup({fetcher:async()=>({ok:true,status:200,json:async()=>body})});s.api.finish();await s.api.startCoordination('brownie');
      assert(s.el('coordState').textContent===(status==='offline'?'Offline explanation · no model call':'Model unavailable · offline explanation'),'Wrong fallback label');
    }
  });
  await test('A later question wins over a stale asynchronous response',async()=>{
    const pending=[];const s=setup({fetcher:()=>new Promise(resolve=>pending.push(resolve))});s.api.finish();
    const first=s.api.startCoordination('first brownie');const second=s.api.startCoordination('second brownie');
    assert(s.requests[0].options.signal.aborted,'Old fetch not aborted');
    const latest=clone(payload);latest.toby.explanation='SECOND RESPONSE';
    pending[1]({ok:true,status:200,json:async()=>latest});await second;
    pending[0]({ok:true,status:200,json:async()=>payload});await first;
    assert(s.el('resultBody').textContent.includes('SECOND RESPONSE'),'Stale response overwrote current one');
  });
  await test('Navigation cancels request and suppresses late UI updates',async()=>{
    let resolve;const s=setup({fetcher:()=>new Promise(r=>resolve=r)});s.api.finish();const pending=s.api.startCoordination('brownie');
    s.api.showView('home');const before=s.el('resultBody').textContent;
    resolve({ok:true,status:200,json:async()=>payload});await pending;
    assert(s.requests[0].options.signal.aborted,'Navigation failed to abort');
    assert(s.el('resultBody').textContent===before,'Navigated view received stale update');
  });
  await test('Missing backend stays usable without presenting a successful review',async()=>{
    const s=setup({fetcher:async()=>{throw new TypeError('Failed to fetch');}});s.api.finish();await s.api.startCoordination('brownie');
    assert(s.el('resultTitle').textContent==='No confirmed result','Failure shown as success');
    assert(s.el('resultBody').textContent.includes('browser-only preview'),'Offline path not explained');
    s.api.showView('orders');assert(s.el('dataView').classList.contains('active'),'Navigation broken');
  });
  await test('file:// and non-brownie questions keep the visual preview without fetch',async()=>{
    for(const [protocol,question] of [['file:','brownie'],['http:','Can we afford cupcakes by Friday?']]){
      const s=setup({protocol});s.api.finish();s.api.startCoordination(question);s.flush();
      assert(s.requests.length===0,'Preview unexpectedly called backend');
      assert(s.el('coordState').textContent.includes('no live calls made'),'Preview is not labelled');
      assert(s.el('resultBody').textContent.includes('No live checks'),'Preview fabricated facts');
    }
  });
  await test('Reduced motion returns results without delayed animation',async()=>{
    const s=setup({reduced:true});await s.api.startCoordination('brownie');s.flush(0);
    assert(s.cards.get('saul').classList.contains('is-complete'),'Reduced-motion completion missing');
    assert(s.timers.size===0,'Reduced motion left delayed effects');
  });
  await test('Intro, skip and replay timer logic still runs',async()=>{
    const s=setup();s.flush();assert(s.el('app').classList.contains('ready'),'Intro never finished');
    s.el('replay').click();assert(!s.el('app').classList.contains('ready'),'Replay not reset');
    s.el('skip').click();assert(s.el('app').classList.contains('ready')&&s.timers.size===0,'Skip failed');
  });
  await test('Failed and invalid backend results never complete specialist cards',async()=>{
    for(const body of [{...payload,result:null}, {...payload,toby:{...payload.toby,recommendation:'approved'}}]){
      const s=setup({fetcher:async()=>({ok:true,status:200,json:async()=>body})});s.api.finish();await s.api.startCoordination('brownie');s.flush();
      assert(s.el('resultTitle').textContent==='No confirmed result','Invalid response accepted');
      assert(!s.cards.get('saul').classList.contains('is-complete'),'Invalid response completed card');
    }
  });
  return passed;
}
if(typeof module!=='undefined')module.exports={runInterfaceTests,createInterfaceHarness};
if(typeof require!=='undefined' && require.main===module) {
  const fs=require('node:fs'),path=require('node:path');
  if(!process.argv[2])throw Error('Pass the path to an offline evaluate_brownie JSON response.');
  runInterfaceTests(fs.readFileSync(path.join(__dirname,'../interface/script.js'),'utf8'),
    JSON.parse(fs.readFileSync(process.argv[2],'utf8'))).then(passed=>{
      passed.forEach(name=>console.log('PASS '+name));console.log(passed.length+' interaction checks passed (DOM doubles).');
    }).catch(error=>{console.error(error);process.exitCode=1;});
}
