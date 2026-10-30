const $=id=>document.getElementById(id);
const assetPath=name=>window.GERA_ASSETS?.[name] || 'assets/'+name;
const timers=[];let introComplete=false;
function later(fn,ms){timers.push(setTimeout(fn,ms))}
function clearTimers(){timers.splice(0).forEach(clearTimeout)}
function settleGem(){const g=$('gem');const r=$('mainPortrait').getBoundingClientRect();g.style.left=(r.left+r.width/2)+'px';g.style.top=(r.top+r.height/2)+'px';g.style.width=r.width+'px';g.style.height=r.height+'px';g.classList.remove('centered');later(()=>{g.classList.add('gone');later(()=>{g.style.display='none';introComplete=true},550)},1150)}
function finish(){clearTimers();$('medalInner').classList.add('turned');$('medal').classList.add('awake','parked');$('intro').classList.add('finished');$('app').classList.add('ready');$('skip').hidden=true;$('gem').className='gem-float gone';$('gem').style.display='none';introComplete=true}
function intro(){clearTimers();introComplete=false;$('intro').classList.remove('finished');$('medal').classList.remove('awake','parked');$('medalInner').classList.remove('turned');$('gem').className='gem-float';$('gem').removeAttribute('style');$('gemInner').classList.remove('revealed');$('app').classList.remove('ready');$('skip').hidden=false;
 later(()=>$('medalInner').classList.add('turned'),850);
 later(()=>$('medal').classList.add('awake'),3450);
 later(()=>$('gem').classList.add('visible'),4100);
 later(()=>{$('medal').classList.add('parked');$('gem').classList.add('centered');$('intro').classList.add('finished');$('app').classList.add('ready')},4700);
 later(()=>$('gemInner').classList.add('revealed'),6200);
 later(settleGem,7800);
 later(()=>$('skip').hidden=true,9000)
}
$('skip').addEventListener('click',finish);$('replay').addEventListener('click',intro);
const agentMap={toby:['Toby','Central Orchestrator','I’m Toby, your orchestrator. We can talk through public information and invented examples. The handoff preview shows how specialist coordination could work.'],saul:['Saul','Finance','Finance specialist. Use the Finance section for your records; Toby can coordinate a wider affordability question once connected.'],bobathan:['Bobathan','Back of House','Ingredient stock and back-of-house operations.'],galgali:['Galgali','Time & Operations','Scheduling, deadlines and capacity.'],ivy:['Ivy','Reception','Enquiries and order intake.'],thibault:['Thibault','Front of House','Finished products and saleable stock.']};
document.querySelectorAll('[data-agent]').forEach(b=>b.addEventListener('click',()=>{const id=b.dataset.agent;if(activeView==='coord' && id!=='toby' && activePlan.some(a=>a.id===id)){const card=document.querySelector(`.handoff-card[data-id="${id}"]`);if(card){card.scrollIntoView({behavior:'smooth',block:'center'});card.classList.add('focus-agent');setTimeout(()=>card.classList.remove('focus-agent'),900)}return}document.querySelectorAll('.agent').forEach(x=>x.classList.toggle('selected',x===b));const a=agentMap[id];$('mainPortrait').src=assetPath(id+'.webp');$('mainPortrait').alt=a[0]+' corporate portrait';$('portraitName').textContent=a[0].toUpperCase();$('portraitRole').textContent=a[1].toUpperCase();$('heroHeading').textContent=id==='toby'?'Welcome to GERA-1':'Meet '+a[0];$('heroBody').textContent=a[2];showView('home')}));
const STORAGE='gera1-bakery-interface-preview-v2';const empty=()=>({front:[],ingredients:[],orders:[],finance:[],events:[]});let data=empty();try{const raw=JSON.parse(localStorage.getItem(STORAGE)||'null');if(raw&&typeof raw==='object')Object.keys(data).forEach(k=>data[k]=Array.isArray(raw[k])?raw[k]:[])}catch(e){};
function save(){try{localStorage.setItem(STORAGE,JSON.stringify(data))}catch(e){}}
const sections={front:{title:'Front of House',eyebrow:'SALEABLE STOCK · THIBAULT',desc:'Your finished products, ready-to-sell quantities and prices.',button:'Add product',fields:[['name','Product name','text',true],['quantity','Quantity available','number',true],['price','Price (£)','number',true]],columns:[['name','Product'],['quantity','Available'],['price','Price']]},ingredients:{title:'Ingredients',eyebrow:'BACK OF HOUSE · BOBATHAN',desc:'Ingredient quantities, units and approximate unit costs.',button:'Add ingredient',fields:[['name','Ingredient','text',true],['quantity','Quantity available','number',true],['unit','Unit (e.g. g, kg, eggs)','text',true],['cost','Unit cost (£)','number',false]],columns:[['name','Ingredient'],['quantity','Quantity'],['unit','Unit'],['cost','Unit cost']]},orders:{title:'Orders',eyebrow:'ORDER BOOK · IVY',desc:'Check orders directly, see what is due and update fulfilment status.',button:'Add order',fields:[['reference','Order reference','text',true],['product','Product / description','text',true],['quantity','Quantity','number',true],['due','Due date','date',true],['status','Status','select',true,['New','Preparing','Ready','Completed']]],columns:[['reference','Reference'],['product','Product'],['quantity','Qty'],['due','Due'],['status','Status']]},finance:{title:'Finance',eyebrow:'MONEY & PLANNING · SAUL',desc:'Track money in and out; live accounting integration is not connected.',button:'Add transaction',fields:[['date','Date','date',true],['description','Description','text',true],['type','Type','select',true,['Income','Expense']],['amount','Amount (£)','number',true]],columns:[['date','Date'],['description','Description'],['type','Type'],['amount','Amount']]}};
let activeView='home',viewRun=0;let calendarDate=new Date();calendarDate=new Date(calendarDate.getFullYear(),calendarDate.getMonth(),1);
function placeChat(v){const target=v==='home'?$('homeView'):v==='calendar'?$('calendarView'):v==='coord'?$('coordView'):$('dataView');const anchor=v==='home'?target.querySelector('.section-heading'):v==='calendar'?target.querySelector('.calendar-toolbar'):v==='coord'?target.querySelector('.coord-stage'):target.querySelector('.stat-row');target.insertBefore($('chatDock'),anchor)}
function showView(v){if(v!==activeView)viewRun++;if(activeView==='coord'&&v!=='coord'){if(delegationUI&&!delegationUI.done)cancelChat();stopCoordination();}activeView=v;placeChat(v);document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.nav').forEach(b=>b.classList.toggle('active',b.dataset.view===v));const titles={home:'Your bakery, at a glance',front:'Front of House',ingredients:'Ingredients',orders:'Orders',finance:'Finance',calendar:'Bakery calendar',coord:'Toby · coordination room'};$('pageTitle').textContent=titles[v]||'GERA-1';if(v==='home')$('homeView').classList.add('active');else if(v==='calendar'){$('calendarView').classList.add('active');renderCalendar()}else if(v==='coord'){$('coordView').classList.add('active')}else{$('dataView').classList.add('active');renderSection(v)};window.scrollTo({top:0,behavior:'smooth'})}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>showView(b.dataset.view)));
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function gbp(n){return new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP'}).format(Number(n)||0)}
function summary(v){const rows=data[v];if(v==='orders')return[['Total orders',rows.length],['Open orders',rows.filter(x=>x.status!=='Completed').length],['Due in next 7 days',rows.filter(x=>x.due&&new Date(x.due+'T12:00:00')>=new Date(new Date().toDateString())&&new Date(x.due+'T12:00:00')<=new Date(Date.now()+7*86400000)).length]];if(v==='front')return[['Products',rows.length],['Items available',rows.reduce((a,b)=>a+Number(b.quantity||0),0)],['Stock retail value',gbp(rows.reduce((a,b)=>a+Number(b.quantity||0)*Number(b.price||0),0))]];if(v==='ingredients')return[['Ingredients tracked',rows.length],['With a cost recorded',rows.filter(x=>x.cost!==''&&x.cost!=null).length],['Inventory lines',rows.length]];return[['Income',gbp(rows.filter(x=>x.type==='Income').reduce((a,b)=>a+Number(b.amount||0),0))],['Expenses',gbp(rows.filter(x=>x.type==='Expense').reduce((a,b)=>a+Number(b.amount||0),0))],['Net',gbp(rows.reduce((a,b)=>a+(b.type==='Income'?1:-1)*Number(b.amount||0),0))]]}
function renderSection(v){const s=sections[v];$('sectionEyebrow').textContent=s.eyebrow;$('sectionTitle').textContent=s.title;$('sectionDescription').textContent=s.desc;$('addRecord').textContent='+ '+s.button;$('sectionSummary').innerHTML=summary(v).map(([k,val])=>`<div class="stat"><small>${esc(k)}</small><strong>${esc(val)}</strong></div>`).join('');const rows=data[v];if(!rows.length){$('sectionContent').innerHTML=`<div class="empty"><strong>No ${esc(s.title.toLowerCase())} records yet</strong><p>Use “${esc(s.button)}” to try this section.<br>These are browser-only preview records, not your live business data.</p></div>`;return}const head=s.columns.map(([k,label])=>`<th>${esc(label)}</th>`).join('');const body=rows.map((r,i)=>'<tr>'+s.columns.map(([k])=>{let value=r[k];if(['price','cost','amount'].includes(k))value=gbp(value);if(k==='status')return `<td><select class="status-select" data-status-index="${i}" aria-label="Order status">${['New','Preparing','Ready','Completed'].map(st=>`<option value="${st}" ${r.status===st?'selected':''}>${st}</option>`).join('')}</select></td>`;return `<td>${esc(value)}</td>`}).join('')+`<td><button class="delete" data-delete="${i}" aria-label="Remove record">Remove</button></td></tr>`).join('');$('sectionContent').innerHTML=`<div class="table-wrap"><table class="data-table"><thead><tr>${head}<th></th></tr></thead><tbody>${body}</tbody></table></div>`;document.querySelectorAll('[data-delete]').forEach(b=>b.addEventListener('click',()=>{data[v].splice(Number(b.dataset.delete),1);save();renderSection(v);if(v==='orders')renderCalendar()}));document.querySelectorAll('[data-status-index]').forEach(s=>s.addEventListener('change',()=>{data.orders[Number(s.dataset.statusIndex)].status=s.value;save();renderSection('orders')}))}
let entryType='orders';function openDialog(type){entryType=type;const s=type==='events'?{title:'Calendar event',fields:[['title','Event title','text',true],['date','Date','date',true],['notes','Notes','text',false]]}:sections[type];$('dialogTitle').textContent=type==='events'?'Add calendar event':s.button;$('dialogEyebrow').textContent='BROWSER PREVIEW · NOT LIVE';$('entryFields').innerHTML=s.fields.map(([key,label,t,required,options])=>`<div class="field"><label for="field-${key}">${esc(label)}</label>${t==='select'?`<select id="field-${key}" name="${key}">${options.map(o=>`<option>${esc(o)}</option>`).join('')}</select>`:`<input id="field-${key}" name="${key}" type="${t}" ${t==='number'?'step="any" min="0"':''} ${required?'required':''}>`}</div>`).join('');$('entryDialog').showModal()}
$('addRecord').addEventListener('click',()=>openDialog(activeView));$('addEvent').addEventListener('click',()=>openDialog('events'));$('closeDialog').addEventListener('click',()=>$('entryDialog').close());$('cancelDialog').addEventListener('click',()=>$('entryDialog').close());$('entryForm').addEventListener('submit',e=>{e.preventDefault();const values=Object.fromEntries(new FormData(e.target).entries());data[entryType].push({id:Date.now(),...values});save();$('entryDialog').close();if(activeView==='calendar')renderCalendar();else renderSection(activeView)});
function pad(n){return String(n).padStart(2,'0')};function iso(d){return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`};function monthEntries(){const key=calendarDate.getFullYear()+'-'+pad(calendarDate.getMonth()+1);return [...data.orders.filter(x=>x.due?.startsWith(key)).map(x=>({date:x.due,title:x.reference+' · '+x.product,kind:'order'})),...data.events.filter(x=>x.date?.startsWith(key)).map(x=>({date:x.date,title:x.title,kind:'event'}))].sort((a,b)=>a.date.localeCompare(b.date))}
function renderCalendar(){$('monthTitle').textContent=calendarDate.toLocaleDateString('en-GB',{month:'long',year:'numeric'});const first=new Date(calendarDate.getFullYear(),calendarDate.getMonth(),1),days=new Date(first.getFullYear(),first.getMonth()+1,0).getDate(),offset=(first.getDay()+6)%7,events=monthEntries();let out=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d=>`<div class="day-label">${d}</div>`).join('');for(let n=0;n<Math.ceil((offset+days)/7)*7;n++){const day=n-offset+1;if(day<1||day>days){out+='<div class="day muted-day"></div>';continue}const date=iso(new Date(first.getFullYear(),first.getMonth(),day));const es=events.filter(x=>x.date===date);out+=`<div class="day ${date===iso(new Date())?'today':''}"><span class="day-number">${day}</span>${es.slice(0,2).map(x=>`<span class="day-event ${x.kind==='order'?'order-event':''}" title="${esc(x.title)}">${esc(x.title)}</span>`).join('')}${es.length>2?`<span class="day-event">+${es.length-2} more</span>`:''}</div>`}$('calendarGrid').innerHTML=out;$('calendarAgenda').innerHTML=events.length?events.map(x=>`<div class="agenda-item"><b>${esc(x.date)}</b>${x.kind==='order'?'Order: ':''}${esc(x.title)}</div>`).join(''):'<p class="agenda-empty">No orders or events scheduled this month. Add an event or an order to see it here.</p>'}
$('prevMonth').addEventListener('click',()=>{calendarDate.setMonth(calendarDate.getMonth()-1);renderCalendar()});$('nextMonth').addEventListener('click',()=>{calendarDate.setMonth(calendarDate.getMonth()+1);renderCalendar()});$('todayMonth').addEventListener('click',()=>{calendarDate=new Date(new Date().getFullYear(),new Date().getMonth(),1);renderCalendar()});
$('sampleData').addEventListener('click',()=>{if(Object.values(data).some(a=>a.length)&&!confirm('Replace your current browser preview entries with illustrative sample records?'))return;const tomorrow=new Date(Date.now()+86400000);const laterDate=new Date(Date.now()+4*86400000);data={front:[{id:1,name:'7-cupcake bouquet',quantity:'2',price:'35'},{id:2,name:'Brownie box (6)',quantity:'3',price:'20'}],ingredients:[{id:3,name:'Plain flour',quantity:'2000',unit:'g',cost:'0.002'},{id:4,name:'Butter',quantity:'1000',unit:'g',cost:'0.009'},{id:5,name:'Eggs',quantity:'12',unit:'each',cost:'0.3'}],orders:[{id:6,reference:'DEMO-001',product:'7-cupcake bouquet',quantity:'1',due:iso(tomorrow),status:'New'},{id:7,reference:'DEMO-002',product:'Brownie box (6)',quantity:'2',due:iso(laterDate),status:'Preparing'}],finance:[{id:8,date:iso(new Date()),description:'Sample sale',type:'Income',amount:'35'},{id:9,date:iso(new Date()),description:'Sample ingredient purchase',type:'Expense',amount:'12.5'}],events:[{id:10,title:'Sample baking preparation',date:iso(tomorrow),notes:''}]};save();if(activeView==='calendar')renderCalendar();else if(activeView!=='home')renderSection(activeView);$('sampleData').textContent='Reload sample data'});
$('clearData').addEventListener('click',()=>{if(!confirm('Clear all entries stored in this browser preview?'))return;data=empty();save();if(activeView==='calendar')renderCalendar();else if(activeView!=='home')renderSection(activeView)});
function addMessage(text,who){const e=document.createElement('div');e.className='bubble '+who;e.textContent=text;$('messages').appendChild(e);$('messages').scrollTop=$('messages').scrollHeight}
function pdfAscii(value){return String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[’‘]/g,"'").replace(/[“”]/g,'"').replace(/[–—]/g,'-').replace(/…/g,'...').replace(/[^\x20-\x7e]/g,'?')}
function pdfLiteral(value){return '('+pdfAscii(value).replace(/([\\()])/g,'\\$1').replace(/[\r\n]/g,' ')+')'}
function buildMontgomeryPdf(result){
 if(!result||result.mode!=='montgomery_draft'||result.status!=='complete'||!result.draft||!['generated','offline_preview'].includes(result.draft.status)||typeof result.draft.text!=='string'||!Array.isArray(result.findings)||result.findings.length<1||result.findings.length>5)throw Error('No complete Montgomery result to export');
 const draftStatus=result.draft.status==='generated'?'Live Nemotron-generated draft':'Offline template preview - NOT AI-generated';
 const sources=result.findings.map(source=>{if(!source||typeof source.title!=='string'||typeof source.finding!=='string'||typeof source.url!=='string'||source.title.length>300||source.finding.length>600||source.url.length>2000)throw Error('Invalid source');const u=new window.URL(source.url);if(u.protocol!=='https:'||u.username||u.password)throw Error('Invalid source URL');return {...source,pdfUrl:encodeURI(u.href)}});
 const pages=[];let page,y;
 const color={navy:'0.055 0.105 0.17',gold:'0.76 0.59 0.32',ink:'0.12 0.16 0.21',muted:'0.36 0.40 0.45',blue:'0.10 0.34 0.59',cream:'0.98 0.97 0.94'};
 const rect=(x0,y0,w,h,fill,stroke)=>page.ops.push(`q ${fill?fill+' rg ':''}${stroke?stroke+' RG 0.7 w ':''}${x0} ${y0} ${w} ${h} re ${fill&&stroke?'B':fill?'f':'S'} Q`);
 const text=(x0,y0,size,font,value,tint=color.ink)=>page.ops.push(`BT /${font} ${size} Tf ${tint} rg ${x0} ${y0} Td ${pdfLiteral(value)} Tj ET`);
 function newPage(first=false){page={ops:[],links:[]};pages.push(page);rect(0,758,595,84,color.navy);rect(0,754,595,4,color.gold);text(46,805,19,'F2','A MOMENT OF ESCAPE','1 1 1');text(47,779,8,'F1','PUBLIC RESEARCH  /  EDITORIAL DRAFT','0.82 0.86 0.90');rect(42,38,511,31,'0.98 0.95 0.86');text(54,51,9,'F2','EDITORIAL REVIEW REQUIRED  -  NOT PUBLISHED',color.navy);text(47,23,8,'F1','A Moment of Escape  |  GERA-1',color.muted);y=first?727:727}
 function wrap(value,max){const words=pdfAscii(value).trim().split(/\s+/).filter(Boolean),lines=[];let line='';for(let word of words){while(word.length>max){if(line){lines.push(line);line=''}lines.push(word.slice(0,max));word=word.slice(max)}if(!word)continue;if(line&&line.length+1+word.length>max){lines.push(line);line=word}else line=line?line+' '+word:word}if(line)lines.push(line);return lines.length?lines:['']}
 function ensure(height){if(y-height<88)newPage()}
 function flow(value,{size=10,font='F1',max=94,leading=14,tint=color.ink,x0=50,href=null}={}){for(const line of wrap(value,max)){ensure(leading);text(x0,y,size,font,line,tint);if(href){const w=Math.min(500,line.length*size*.53);page.ops.push(`q ${tint} RG 0.5 w ${x0} ${y-1} m ${x0+w} ${y-1} l S Q`);page.links.push({x:x0,y:y-3,w,h:leading,uri:href})}y-=leading}}
 newPage(true);
 text(47,y,17,'F2','Traditional Halloween Customs');y-=22;
 text(47,y,10,'F1','British Isles  |  Social media draft for A Moment of Escape',color.muted);y-=23;
 rect(46,y-8,4,17,color.gold);text(58,y-3,9,'F2',draftStatus,color.navy);y-=28;
 text(47,y,11,'F2',"MONTGOMERY'S COMPLETE DRAFT",color.navy);y-=16;
 const draftLines=wrap(result.draft.text,86),boxHeight=draftLines.length*15+18;ensure(boxHeight+10);rect(42,y-boxHeight+5,511,boxHeight,color.cream,'0.86 0.82 0.74');y-=12;
 for(const line of draftLines){text(55,y,10,'F1',line);y-=15}y-=19;
 text(47,y,11,'F2',"PERCIVAL'S RESEARCH SOURCES",color.navy);y-=20;
 sources.forEach((source,i)=>{ensure(65);flow(`${i+1}. ${source.title}`,{size:10,font:'F2',max:88,leading:14,tint:color.ink});flow(source.finding,{size:9,max:98,leading:12,tint:color.muted});flow(source.pdfUrl,{size:8,max:88,leading:12,tint:color.blue,href:source.pdfUrl});y-=8});
 const objects=[];const setObject=(id,body)=>{objects[id]=body};setObject(1,'<< /Type /Catalog /Pages 2 0 R >>');setObject(3,'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>');setObject(4,'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>');
 const pageIds=pages.map((_,i)=>5+i*2),annotationIds=[];let nextId=5+pages.length*2;
 pages.forEach((p,i)=>{const annots=p.links.map(link=>{const id=nextId++;annotationIds.push(id);setObject(id,`<< /Type /Annot /Subtype /Link /Rect [${link.x.toFixed(1)} ${link.y.toFixed(1)} ${(link.x+link.w).toFixed(1)} ${(link.y+link.h).toFixed(1)}] /Border [0 0 0] /A << /S /URI /URI ${pdfLiteral(link.uri)} >> >>`);return `${id} 0 R`});const pageId=pageIds[i],contentId=pageId+1,stream=p.ops.join('\n');setObject(pageId,`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ${contentId} 0 R /Annots [${annots.join(' ')}] >>`);setObject(contentId,`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`)});
 setObject(2,`<< /Type /Pages /Kids [${pageIds.map(id=>id+' 0 R').join(' ')}] /Count ${pages.length} >>`);
 let pdf='%PDF-1.4\n',offsets=[0];for(let id=1;id<objects.length;id++){if(!objects[id])throw Error('Invalid PDF object map');offsets[id]=pdf.length;pdf+=`${id} 0 obj\n${objects[id]}\nendobj\n`}const xref=pdf.length;pdf+=`xref\n0 ${objects.length}\n0000000000 65535 f \n`;for(let id=1;id<objects.length;id++)pdf+=String(offsets[id]).padStart(10,'0')+' 00000 n \n';pdf+=`trailer\n<< /Size ${objects.length} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF`;
 return pdf;
}
function downloadMontgomeryPdf(result){try{const blob=new window.Blob([buildMontgomeryPdf(result)],{type:'application/pdf'}),url=window.URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='A-Moment-of-Escape-Halloween-Editorial-Draft.pdf';document.body.appendChild(link);link.click();link.remove();setTimeout(()=>window.URL.revokeObjectURL(url),1000)}catch(_error){$('chatFoot').textContent='PDF unavailable · source data could not be verified'}}
function showPercivalResearch(result){
 if(!result||result.mode!=='percival_research'||!['complete','empty','unavailable'].includes(result.status)
    ||result.agent!=='Percival'||!Array.isArray(result.findings)||result.findings.length>5
    ||typeof result.activity!=='string'||result.activity.length>240)throw Error('Invalid research response');
 $('chatFoot').textContent=result.status==='complete'?'Percival research · Tavily sources · read-only':result.status==='empty'?'Percival research · no usable sources returned':'Percival research unavailable · no source claims made';
 const bubble=document.createElement('div');bubble.className='bubble bot';
 const heading=document.createElement('strong');heading.textContent='Percival · Research specialist';bubble.appendChild(heading);
 const activity=document.createElement('p');activity.textContent=result.activity;bubble.appendChild(activity);
 if(result.status==='complete'){
  const label=document.createElement('p');label.textContent='Findings from public search results:';bubble.appendChild(label);
  result.findings.forEach(source=>{
   if(!source||typeof source.title!=='string'||source.title.length>300||typeof source.finding!=='string'||source.finding.length>600
      ||typeof source.url!=='string'||source.url.length>2000||!source.url.startsWith('https://'))throw Error('Invalid research source');
   const item=document.createElement('p');const link=document.createElement('a');link.textContent=source.title;link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';
   const finding=document.createElement('span');finding.textContent=' — '+source.finding;item.appendChild(link);item.appendChild(finding);bubble.appendChild(item);
  });
 }
 $('messages').appendChild(bubble);$('messages').scrollTop=$('messages').scrollHeight;
}
function showMontgomeryDraft(result){
 if(!result||result.mode!=='montgomery_draft'||!['complete','empty','unavailable'].includes(result.status)
    ||!Array.isArray(result.activity)||result.activity.length>3||!Array.isArray(result.findings)||result.findings.length>5
    ||(result.draft!==null&&(!result.draft||!['generated','offline_preview'].includes(result.draft.status)
       ||typeof result.draft.label!=='string'||typeof result.draft.text!=='string'||result.draft.text.length>700)))throw Error('Invalid Montgomery response');
 $('chatFoot').textContent=result.draft?.status==='generated'?'Montgomery AI draft · sources included · editorial review only':
  result.draft?.status==='offline_preview'?'Montgomery offline preview · not AI-generated · editorial review only':'Montgomery draft unavailable · no sourced findings';
 const bubble=document.createElement('div');bubble.className='bubble bot montgomery-result-card';
 const heading=document.createElement('strong');heading.textContent='Toby · Percival → Montgomery';bubble.appendChild(heading);
 result.activity.forEach(message=>{if(typeof message!=='string'||message.length>240)throw Error('Invalid activity');const line=document.createElement('p');line.textContent=message;bubble.appendChild(line)});
 result.findings.forEach(source=>{
  if(!source||typeof source.title!=='string'||source.title.length>300||typeof source.finding!=='string'||source.finding.length>600
     ||typeof source.url!=='string'||source.url.length>2000||!source.url.startsWith('https://'))throw Error('Invalid research source');
 });
 if(result.draft){
  const kind=result.draft.status==='generated'?'Live Nemotron-generated draft':'Offline template preview · NOT AI-generated';
  const status=document.createElement('p');status.className='montgomery-draft-status';status.textContent=kind;bubble.appendChild(status);
  const meta=document.createElement('p');meta.className='montgomery-draft-meta';meta.textContent=`${result.findings.length} Percival source${result.findings.length===1?'':'s'} included in the PDF.`;bubble.appendChild(meta);
  const download=document.createElement('button');download.type='button';download.className='montgomery-download';download.textContent='Download PDF';download.addEventListener('click',()=>downloadMontgomeryPdf(result));bubble.appendChild(download);
  const toggle=document.createElement('button');toggle.type='button';toggle.className='montgomery-draft-toggle';
  toggle.textContent='Show full draft';toggle.setAttribute('aria-expanded','false');
  const full=document.createElement('div');full.className='montgomery-draft-full';full.hidden=true;
  const draft=document.createElement('p');draft.textContent=result.draft.text;full.appendChild(draft);
  const sourceTitle=document.createElement('strong');sourceTitle.textContent="Percival's sources";full.appendChild(sourceTitle);
  result.findings.forEach(source=>{const item=document.createElement('p');const link=document.createElement('a');link.textContent=source.title;link.href=source.url;link.target='_blank';link.rel='noopener noreferrer';const finding=document.createElement('span');finding.textContent=' — '+source.finding;item.appendChild(link);item.appendChild(finding);full.appendChild(item)});
  toggle.addEventListener('click',()=>{const expanded=full.hidden;full.hidden=!expanded;toggle.setAttribute('aria-expanded',String(expanded));toggle.textContent=expanded?'Hide full draft':'Show full draft';$('messages').classList.toggle('montgomery-expanded',expanded);if(expanded){$('messages').scrollTop=$('messages').scrollHeight;full.scrollIntoView({block:'nearest'})}});
  bubble.appendChild(toggle);bubble.appendChild(full);
 }
 $('messages').appendChild(bubble);$('messages').scrollTop=$('messages').scrollHeight;
}
$('toggleChat').addEventListener('click',()=>{const show=$('messages').hidden;$('messages').hidden=!show;$('toggleChat').textContent=show?'Hide conversation ↓':'Show conversation ↑';$('toggleChat').setAttribute('aria-expanded',String(show))});
$('chatForm').addEventListener('submit',e=>{e.preventDefault();const q=$('question').value.trim();if(q)sendTobyMessage(q)});

// Demonstration-only coordination: the visual sequence represents future backend events.
const agentStyles={
 toby:{color:'#8fc9ff',halo:'rgba(115,178,255,.33)'},
 bobathan:{color:'#50c9a6',halo:'rgba(70,209,157,.30)'},
 saul:{color:'#e7b66d',halo:'rgba(238,178,79,.30)'},
 galgali:{color:'#bd91ff',halo:'rgba(173,110,249,.32)'},
 ivy:{color:'#f5a6c2',halo:'rgba(239,132,185,.30)'},
 thibault:{color:'#55d6d3',halo:'rgba(73,217,213,.32)'}
};
const agentTasks={
 bobathan:{role:'Ingredients & recipes',task:'Request recipe quantities and ingredient availability.',done:'Ingredient requirements requested · awaiting a real stock result.'},
 saul:{role:'Finance & costs',task:'Request ingredient costs and available budget.',done:'Finance inputs requested · awaiting real account figures.'},
 galgali:{role:'Time & operations',task:'Request baking capacity, timing and deadlines.',done:'Schedule inputs requested · awaiting real calendar data.'},
 ivy:{role:'Orders & enquiries',task:'Request order details, customer requirements and due dates.',done:'Order details requested · awaiting real order records.'},
 thibault:{role:'Front of house',task:'Request finished products and saleable stock.',done:'Finished stock requested · awaiting real inventory data.'}
};
let activePlan=[],currentQuestion='',coordTimers=[],coordRun=0,activeRequest=null;
function laterCoord(fn,ms){coordTimers.push(setTimeout(fn,ms))}
function stopCoordination(){coordRun++;if(activeRequest){activeRequest.abort();activeRequest=null;}coordTimers.splice(0).forEach(clearTimeout);document.querySelectorAll('.agent').forEach(b=>{b.classList.remove('working','complete','flipped');b.style.removeProperty('--glow');b.style.removeProperty('--glow-soft')})}
function choosePlan(q){const t=q.toLowerCase(),p=[];const add=id=>{if(!p.includes(id))p.push(id)};
 const money=/afford|budget|cost|price|money|finance|profit|fund|pay|spend|cash/.test(t),
 food=/bouquet|cupcake|brownie|ingredient|recipe|bake|make|flour|butter|egg|stock/.test(t),
 orders=/order|customer|deliver|fulfil|fulfill|dispatch|collection/.test(t),
 schedule=/calendar|time|when|deadline|schedule|friday|tomorrow|next week|capacity|ready by/.test(t),
 finished=/front of house|finished|saleable|product stock|display|ready to sell/.test(t);
 if(orders)add('ivy');if(food)add('bobathan');if(money)add('saul');if(schedule)add('galgali');if(finished)add('thibault');
 if(food&&money)add('galgali');if(orders&&!p.includes('galgali'))add('galgali');
 // General questions can be handled by Toby without specialist delegation.
 // For the preview, do not pretend to call unrelated specialists.

 return p.map(id=>({id,...agentTasks[id]}));
}
function logCoord(title,body){const li=document.createElement('li');const b=document.createElement('strong');b.textContent=title;const s=document.createElement('span');s.textContent=body;li.append(b,s);$('activityList').appendChild(li);}
function setAgentState(id,state){const b=document.querySelector(`.agent[data-agent="${id}"]`),card=document.querySelector(`.handoff-card[data-id="${id}"]`);if(!b||!card)return;
 b.classList.toggle('working',state==='working');b.classList.toggle('complete',state==='complete');b.classList.toggle('flipped',state!=='idle');b.style.setProperty('--glow',agentStyles[id].color);b.style.setProperty('--glow-soft',agentStyles[id].halo);
 card.classList.toggle('is-working',state==='working');card.classList.toggle('is-complete',state==='complete');
 const status=card.querySelector('.handoff-status');status.textContent=state==='working'?'◆ Gem illuminated · working':state==='complete'?'✓ Handoff shown · awaiting live data':'○ Waiting for Toby';
}
function startCoordination(q){
 cancelChat();
 if (q.toLowerCase().includes('brownie') && window.location.protocol.startsWith('http')) {
   return runRealSyntheticBrownie(q);
 }
 stopCoordination();currentQuestion=q;activePlan=choosePlan(q);showView('coord');setCoordMode(false);$('coordQuestion').textContent='“'+q+'”';$('coordNarrative').textContent='I’ll bring in the specialists who can help answer that.';$('coordState').textContent='Visual handoff demonstration · not live';$('resultTitle').textContent='Gathering the pieces…';$('resultBody').textContent='Watch the specialist buttons on the left: each portrait will turn into its gemstone when Toby calls that specialist.';$('resultDetails').replaceChildren();$('activityList').replaceChildren();
 $('handoffGrid').innerHTML=activePlan.length?activePlan.map(a=>{const s=agentStyles[a.id];return `<article class="handoff-card" data-id="${a.id}" style="--agent-color:${s.color};--agent-halo:${s.halo}"><div class="handoff-avatar"><div class="handoff-avatar-inner"><img src="${assetPath(a.id+'.webp')}" alt="${a.id} portrait"><img class="jewel" src="${assetPath(a.id+'-jewel.png')}" alt="${a.id} gemstone"></div></div><h4>${agentMap[a.id][0]}</h4><div class="role">${a.role}</div><div class="handoff-task">${a.task}</div><div class="handoff-status">○ Waiting for Toby</div></article>`}).join(''):'<div class="no-handoff">Toby can handle this directly. No specialist handoff is needed in this preview.</div>';
 logCoord('Toby receives your question','Planning which specialist information would be needed.');
 const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 activePlan.forEach((a,i)=>{
  const start=550+i*1150;
  laterCoord(()=>{setAgentState(a.id,'working');$('coordNarrative').textContent=`I’m asking ${agentMap[a.id][0]} to help with ${a.role.toLowerCase()}.`;logCoord(`${agentMap[a.id][0]} is called`,a.task);$('coordState').textContent=`Demonstrating handoff ${i+1} of ${activePlan.length}`;},reduced?0:start);
  laterCoord(()=>{setAgentState(a.id,'complete');logCoord(`${agentMap[a.id][0]}: handoff demonstrated`,a.done)},reduced?0:start+900);
 });
 laterCoord(()=>{const names=activePlan.map(a=>agentMap[a.id][0]);$('coordState').textContent='Visual demonstration complete · no live calls made';$('coordNarrative').textContent='That’s how I’ll bring the team together when the backend is connected.';$('resultTitle').textContent=names.length?'Here is what I would need to answer':'Toby can answer directly';$('resultBody').textContent=names.length?`For this question, I would coordinate ${names.join(', ')}. Their real responses will be collected here, with the figures and evidence used to reach a recommendation. No live checks have happened in this preview.`:'This appears to be a direct question for Toby. Once connected, he can answer without delegating unless the real reasoning engine identifies a need for a specialist.';
 const box=$('resultDetails');box.replaceChildren();activePlan.forEach(a=>{const d=document.createElement('div');d.textContent=agentMap[a.id][0]+' — '+a.done;box.appendChild(d)});logCoord('Toby prepares the response','Awaiting backend connection for actual results and evidence.');addMessage(names.length?'I would consult '+names.join(', ')+'. This is a visual demonstration only; I have not checked your real stock, money or calendar.':'This looks like a question for me directly. I am only a visual preview until the backend is connected.','bot');},reduced?0:1250+activePlan.length*1150);
}
$('backFromCoord').addEventListener('click',()=>showView('home'));
$('rerunCoord').addEventListener('click',()=>{if(currentQuestion)startCoordination(currentQuestion)});
$('tryHandoff').addEventListener('click',()=>{const q='Can we afford the ingredients for a seven-cupcake bouquet and make it by Friday?';if($('messages').hidden)$('toggleChat').click();addMessage(q,'me');startCoordination(q)});

placeChat('home');if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)finish();else intro();

// The existing visual preview remains available offline. Only this path uses Python.
function setCoordMode(backend){
 $('rerunCoord').disabled=false;
 $('activityNote').textContent=backend?'Synthetic workflow results. Animations replay returned stages; they are not live progress events.':'This is a visual simulation of the handoff. No backend or model call is made for this preview.';
 $('coordTipTitle').textContent=backend?'Read-only synthetic review':'When connected';
 $('coordTipBody').textContent=backend?'Python owns the decision and missing checks. Model commentary cannot accept an order or change records.':'Each step will display the real agent request, its result and the evidence Toby used.';
 $('chatFoot').textContent=backend?'Fixed 13-piece synthetic brownie example · no real bakery data or order actions.':'Visual preview · no backend or model calls for this question.';
 $('activityList').setAttribute('aria-label',backend?'Synthetic workflow activity':'Demonstration activity');
}
const browniePlan=[
 {id:'bobathan',role:'Ingredient & finished stock',stages:['finished_stock','ingredients']},
 {id:'thibault',role:'Front of house · Tibbi',stages:['tibbi']},
 {id:'saul',role:'Finance · separate proposal',stages:['finance']},
 {id:'galgali',role:'Financial calendar only',stages:['financial_calendar']}
];
async function runRealSyntheticBrownie(q){
 cancelChat();
 stopCoordination();const run=coordRun;currentQuestion=q;activePlan=browniePlan;showView('coord');setCoordMode(true);
 const controller=new AbortController();activeRequest=controller;
 const timeout=setTimeout(()=>controller.abort(),30000);
 $('coordQuestion').textContent='“'+q+'”';
 $('coordNarrative').textContent='Toby is requesting the audited synthetic brownie review.';
 $('coordState').textContent='Waiting for local backend · SYNTHETIC DATA';
 $('resultTitle').textContent='Checking the fixed 13-piece brownie example…';
 $('resultBody').textContent='Typed quantities and dates are not interpreted. No browser records are sent; this uses synthetic fixtures only.';
 $('resultDetails').replaceChildren();$('activityList').replaceChildren();
 $('handoffGrid').innerHTML=activePlan.map(a=>{const s=agentStyles[a.id];return `<article class="handoff-card" data-id="${a.id}" style="--agent-color:${s.color};--agent-halo:${s.halo}"><div class="handoff-avatar"><div class="handoff-avatar-inner"><img src="${assetPath(a.id+'.webp')}" alt="${a.id} portrait"><img class="jewel" src="${assetPath(a.id+'-jewel.png')}" alt="${a.id} gemstone"></div></div><h4>${agentMap[a.id][0]}</h4><div class="role">${a.role}</div><div class="handoff-task">Synthetic workflow result pending</div><div class="handoff-status">○ Awaiting backend</div></article>`}).join('');
 logCoord('Toby requests a review','Fixed synthetic example; the backend controls whether model explanations are enabled.');
 try {
  const response=await fetch('/api/brownie-demo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q}),signal:controller.signal});
  const body=await response.json();
  if(run!==coordRun)return;
  if(!response.ok)throw Error(response.status===429?'A review is already running. Please wait before retrying.':'The audited backend review is unavailable. No order was accepted.');
  const result=body.result, answer=body.toby;
  if(!result?.data || !answer || !['offline','live','fallback'].includes(answer.status)
     || answer.model_used!==(answer.status==='live') || answer.recommendation!=='cannot_confirm'
     || result.data.recommendation!=='cannot_confirm' || result.data.order_accepted!==false
     || typeof answer.explanation!=='string' || answer.explanation.length>2500
     || !Array.isArray(result.data.stages) || !Array.isArray(result.missing))throw Error('Invalid backend response; no confirmed result is available.');
  const data=result.data, stages=data.stages;
  const labels={offline:'Offline explanation · no model call',live:'Nemotron response received · synthetic data',fallback:'Model unavailable · offline explanation'};
  $('coordState').textContent=labels[answer.status];
  $('coordNarrative').textContent='Toby has the audited synthetic review. The cards replay its returned stages.';
  $('chatFoot').textContent=labels[answer.status]+' · fixed synthetic example · no order actions.';
  $('resultTitle').textContent='Cannot confirm · no order accepted';
  const prefix=answer.model_used?'Toby’s model commentary (not an approval): ':'Toby’s offline explanation: ';
  $('resultBody').textContent=prefix+answer.explanation;
  const details=$('resultDetails');
  const addDetail=(k,v)=>{if(v!==undefined){const el=document.createElement('div');el.textContent=k+': '+v;details.appendChild(el)}};
  [['Scenario',body.scenario],['Request ID',result.request_id],['Workflow status',result.status],['Product',data.product_id],['Recipe version',data.recipe_version],['Decision','cannot_confirm'],['Order accepted','No'],['Explanation',labels[answer.status]],['Data source','Synthetic fixtures; not current bakery records']].forEach(([k,v])=>addDetail(k,v));
  result.missing.forEach(v=>addDetail('Outstanding',String(v).replaceAll('_',' ')));
  (result.evidence||[]).forEach(v=>addDetail('Evidence',v));
  for(const [name,status] of stages)logCoord(String(name).replaceAll('_',' '),String(status));
  logCoord('Toby’s explanation',labels[answer.status]);
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  activePlan.forEach((a,i)=>{
   const returned=stages.filter(([name])=>a.stages.includes(name));
   const checked=returned.filter(([,status])=>['ok','needs_information'].includes(status));
   const card=document.querySelector(`.handoff-card[data-id="${a.id}"]`);
   card.querySelector('.handoff-task').textContent=returned.length?returned.map(([name,status])=>name.replaceAll('_',' ')+': '+status).join(' · '):'No completed stage returned';
   if(!checked.length){card.querySelector('.handoff-status').textContent='○ Not checked';return}
   laterCoord(()=>{if(run!==coordRun)return;setAgentState(a.id,'working');card.querySelector('.handoff-status').textContent='◆ Replaying returned check';},reduced?0:550+i*1150);
   laterCoord(()=>{if(run!==coordRun)return;setAgentState(a.id,'complete');card.querySelector('.handoff-status').textContent=checked.length<a.stages.length?'✓ Partial checks returned · see outstanding items':checked.some(([,status])=>status==='needs_information')?'✓ Check returned · information missing':'✓ Check returned · synthetic data';},reduced?0:1450+i*1150);
  });
  addMessage('Synthetic example: cannot confirm; no order accepted. '+prefix+answer.explanation,'bot');
 }catch(err){
  if(run!==coordRun)return;
  $('coordState').textContent='Backend review unavailable';$('resultTitle').textContent='No confirmed result';
  const message=err.name==='AbortError'?'The request timed out. No confirmed response was received.':err instanceof TypeError?'Could not reach the local backend. Open the interface through local_bridge.py at http://127.0.0.1:8765.':err.message;
  $('resultBody').textContent=message+' The browser-only preview and bakery sections remain available.';
  logCoord('Review unavailable',message);addMessage(message,'bot');
 }finally{clearTimeout(timeout);if(activeRequest===controller)activeRequest=null;}
}


// Conversation is isolated from demonstration messages and browser bakery records.
const CHAT_GREETING='Hello, I’m Toby. We can discuss public information and invented examples. I can coordinate a fixed synthetic brownie check with Bobathan and Saul through the local backend. I cannot read real business records or take actions.';
const MONTGOMERY_TRIGGER='Toby, ask Percival to research traditional Halloween customs in the British Isles, then ask Montgomery to draft a short, engaging social media post for A Moment of Escape. Include the sources for editorial review.';
let chatHistory=[],chatRequest=null,chatTimer=null,chatRun=0;
let delegationUI=null;
// Early convenience check only; Python repeats validation before any provider call.
const sensitiveChat=/(?:\b(?:sk-|nvapi-)[A-Za-z0-9_-]{8,}|\bBearer\s+\S+|\b(?:[A-Z][A-Z0-9]*_)*(?:api[ _-]?key|access[ _-]?token|password|secret)\s*[:=]\s*\S+|-----BEGIN [A-Z ]*PRIVATE KEY-----|\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9-]+(?:\.[A-Z0-9-]+)+|(?:^|[^\w])\+?(?:\d[ ()-]*){9,}\d(?!\w))/i;
function cancelChat(){
 interruptDelegation();
 chatRun++;if(chatRequest)chatRequest.abort();chatRequest=null;
 if(chatTimer!==null)clearTimeout(chatTimer);chatTimer=null;
 $('chatSend').disabled=false;$('chatForm').setAttribute('aria-busy','false');
}
function rememberChat(message,reply){
 chatHistory.push({role:'user',content:message},{role:'assistant',content:reply});
 while(chatHistory.length>12 || chatHistory.reduce((n,m)=>n+m.content.length,0)>8000)chatHistory.splice(0,2);
}
function localChatHelp(q){
 const t=q.toLowerCase();
 if(/brownies?/.test(t)&&/afford|cost|budget/.test(t))return 'The local backend is needed to ask Bobathan and Saul about one synthetic brownie batch. No assessment was obtained here. Start the local server and ask: Can we afford to make a batch of brownies? This cannot approve spending.';
 if(/\b(order|buy|purchase|publish|send|reserve|delegate|ask saul|check stock)\b/.test(t))return 'I can help discuss a public or invented example, but this chat cannot take actions, read business records or consult specialists. Nothing has been changed. Run brownie demo is a separate worked example.';
 if(/brownie|demo/.test(t))return 'Use Run brownie demo for the fixed 13-piece synthetic review. Mentioning brownies in conversation does not run it, and the demo cannot accept an order.';
 if(/\b(saul|galgali|bobathan|ivy|tibbi|thibault|team|specialist)\b/.test(t))return 'Saul covers finance, Galgali time and operations, Bobathan physical stock, Ivy reception, and Tibbi (Thibault here) Front of House. I cannot consult them in this chat. The handoff preview is a simulation.';
 return 'I’m using local offline help. I can explain Toby’s role, the team and the brownie demo, but cannot generate a full conversational answer without the backend and Nebius. Your bakery sections remain available. Use public or invented examples only.';
}
function showLocalChat(q,label){
 const reply=localChatHelp(q);$('chatFoot').textContent=label+' · read-only conversation';
 addMessage('Offline help: '+reply,'bot');
 // Do not replay messages from failed/offline requests to the provider later.
}
async function sendTobyMessage(q){
 if(chatRequest)return;
 if($('messages').hidden)$('toggleChat').click();
 if(!q.trim() || q.length>1000 || /[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(q)){
  $('chatFoot').textContent='Use a message of 1–1000 characters.';return;
 }
 if(sensitiveChat.test(q)){
  $('chatFoot').textContent='Not sent: remove credentials or contact details and use an invented example.';
  return;
 }
 // Only backend events can start specialist activity; the browser never plans calls.
 stopCoordination();cancelChat();const run=chatRun,view=viewRun;
 addMessage(q,'me');$('question').value='';
 if(!window.location.protocol.startsWith('http')){showLocalChat(q,'Offline · browser-only help');return;}
 const controller=new AbortController();chatRequest=controller;
 $('chatSend').disabled=true;$('chatForm').setAttribute('aria-busy','true');
 $('chatFoot').textContent='Toby is preparing a reply · public/synthetic and read-only';
 chatTimer=setTimeout(()=>controller.abort(),q.trim().toLowerCase()===MONTGOMERY_TRIGGER.toLowerCase()?40000:30000);
 try{
  const response=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/x-ndjson, application/json'},body:JSON.stringify({message:q,history:chatHistory}),signal:controller.signal});
  if(run!==chatRun)return;
  if(response.ok && response.headers?.get('Content-Type')?.startsWith('application/x-ndjson')){
   await receiveDelegation(response,q,run,view);return;
  }
  const body=await response.json();if(run!==chatRun)return;
  if(!response.ok){
   if(response.status===400 || response.status===413){
    $('chatFoot').textContent=body.error_code==='sensitive_input'?'Not sent to Nebius: remove credentials/contact details; clear conversation if they are in history.':'Request rejected: use a shorter message or clear conversation history.';
    addMessage($('chatFoot').textContent,'bot');return;
   }
   showLocalChat(q,response.status===429?'Backend busy · no automatic retry':'Backend unavailable');return;
  }
  if(body.mode==='percival_research'){
   showPercivalResearch(body);return;
  }
  if(body.mode==='montgomery_draft'){
   showMontgomeryDraft(body);return;
  }
  const answer=body.chat;
  if(body.mode!=='conversation' || !answer || !['live','offline','fallback','scope'].includes(answer.status)
     || answer.model_used!==(answer.status==='live') || answer.read_only!==true
     || typeof answer.reply!=='string' || !answer.reply.trim() || answer.reply.length>2500
     || sensitiveChat.test(answer.reply))throw Error('Invalid conversation response');
  const labels={scope:'Supported scope · no specialist or model call',live:'Nemotron reply · read-only conversation',offline:'Offline help · no model call',fallback:'Nemotron reply unavailable · offline help'};
  $('chatFoot').textContent=labels[answer.status];
  addMessage((answer.model_used||answer.status==='scope'?'':'Offline help: ')+answer.reply,'bot');
  if(answer.model_used)rememberChat(q,answer.reply);
 }catch(error){
  if(run!==chatRun)return;
  interruptDelegation();
  showLocalChat(q,error.name==='AbortError'?'Request timed out · no automatic retry':'Backend unavailable or invalid response');
 }finally{
  if(run===chatRun){if(chatTimer!==null)clearTimeout(chatTimer);chatTimer=null;chatRequest=null;$('chatSend').disabled=false;$('chatForm').setAttribute('aria-busy','false');}
 }
}
$('clearConversation').addEventListener('click',()=>{
 cancelChat();chatHistory=[];$('messages').replaceChildren();$('question').value='';
 addMessage(CHAT_GREETING,'bot');$('chatFoot').textContent='Conversation cleared · public/synthetic messages only';
});
$('runBrownieDemo').addEventListener('click',()=>{
 const q='Review the fixed synthetic brownie demo';
 if($('messages').hidden)$('toggleChat').click();addMessage(q,'me');startCoordination(q);
});

// Actual synthetic activity has its own event path. No coordination timers are used.
function beginDelegation(question){
 activePlan=['bobathan','saul'].map(id=>({id}));
 delegationUI={done:false,states:{bobathan:'skipped',saul:'skipped'}};
 currentQuestion='';showView('coord');$('rerunCoord').disabled=true;
 $('coordQuestion').textContent='“'+question+'”';
 $('coordState').textContent='Synthetic backend assessment · awaiting checks';
 $('coordNarrative').textContent='Toby is coordinating one synthetic batch of 12 pieces.';
 $('resultTitle').textContent='Assessment pending · no financial approval';
 $('resultBody').textContent='Only validated backend findings will appear here.';
 $('resultDetails').replaceChildren();$('activityList').replaceChildren();
 $('activityNote').textContent='Actual local specialist events on synthetic data. These are not a replay or Nemotron activity.';
 $('activityList').setAttribute('aria-label','Actual synthetic specialist activity');
 $('coordTipTitle').textContent='Read-only synthetic delegation';
 $('coordTipBody').textContent='Checks use historical invented records. No purchase, stock adjustment or financial approval is possible.';
 $('chatFoot').textContent='Synthetic backend assessment · no model call';
 $('handoffGrid').innerHTML=['bobathan','saul'].map(id=>{const s=agentStyles[id];return `<article class="handoff-card" data-id="${id}" style="--agent-color:${s.color};--agent-halo:${s.halo}"><div class="handoff-avatar"><div class="handoff-avatar-inner"><img src="${assetPath(id+'.webp')}" alt="${id} portrait"><img class="jewel" src="${assetPath(id+'-jewel.png')}" alt="${id} gemstone"></div></div><h4>${agentMap[id][0]}</h4><div class="role">${id==='saul'?'Finance':'Back of House'}</div><div class="handoff-task">${id==='saul'?'Separate synthetic proposal · not batch costing':'Recipe ingredient availability'}</div><div class="handoff-status">○ Not invoked</div></article>`}).join('');
 logCoord('Toby received the assessment request','Fixed synthetic scope; no specialist has started yet.');
}
function interruptDelegation(){
 if(!delegationUI||delegationUI.done)return;
 delegationUI.done=true;
 for(const id of ['bobathan','saul']){
  setAgentState(id,'idle');
  const card=document.querySelector(`.handoff-card[data-id="${id}"]`);
  if(card)card.querySelector('.handoff-status').textContent='○ Assessment interrupted · see recorded events';
 }
 $('coordState').textContent='Assessment interrupted · no final result';
 $('resultTitle').textContent='No confirmed assessment';
 $('resultBody').textContent='The response was interrupted or invalid. Earlier recorded checks do not constitute a complete assessment or financial approval. No automatic retry was made.';
}
async function receiveDelegation(response,question,run,view){
 if(!response.body?.getReader)throw Error('Streaming unavailable');
 const reader=response.body.getReader();
 let buffer='',bytes=0,sequence=0,requestId=null,final=null,ended=false;
 function event(e){
  if(final||!e||e.sequence!==sequence+1||++sequence>8||typeof e.request_id!=='string'||!/^synthetic-chat-[a-f0-9]{32}$/.test(e.request_id))throw Error('Invalid activity envelope');
  if(!requestId){
   if(e.event!=='begin'||e.mode!=='synthetic_delegation')throw Error('Missing beginning');
   requestId=e.request_id;beginDelegation(question);return;
  }
  if(e.request_id!==requestId)throw Error('Wrong request');
  if(e.event==='final'){
   const a=e.assessment,states=delegationUI.states;
   if(!a||a.mode!=='synthetic_delegation'||a.read_only!==true||a.model_used!==false||a.recommendation!=='cannot_confirm'
      ||!['blocked','incomplete'].includes(a.status)||!a.specialists||!a.findings||!Array.isArray(a.missing)
      ||a.missing.length>100||a.missing.some(item=>typeof item!=='string'||item.length>200)
      ||typeof a.reply!=='string'||!a.reply.trim()||a.reply.length>2500||sensitiveChat.test(a.reply))throw Error('Invalid assessment');
   for(const id of ['bobathan','saul']){
    if(states[id]==='started'||a.specialists[id]!==states[id])throw Error('Unfinished specialist');
    const success=['ok','needs_information'].includes(states[id]);
    if(success&&(typeof a.findings[id]?.audit_id!=='string'||!/^[a-f0-9-]{36}$/.test(a.findings[id].audit_id)||!Array.isArray(a.findings[id]?.evidence)))throw Error('Missing receipt');
    if(!success&&a.findings[id])throw Error('Unverified finding');
   }
   const complete=Object.values(states).every(s=>['ok','needs_information'].includes(s));
   if((a.status==='incomplete')!==complete)throw Error('Contradictory assessment');
   final=a;return;
  }
  if(!['bobathan','saul'].includes(e.agent))throw Error('Unexpected specialist');
  const id=e.agent,prior=delegationUI.states[id];
  if(id==='saul'&&!['ok','needs_information'].includes(delegationUI.states.bobathan))throw Error('Invalid handoff order');
  let label;
  if(e.event==='specialist_started'&&prior==='skipped'){
   delegationUI.states[id]='started';setAgentState(id,'working');
   label='◆ Authorised backend check started';
  }else if(e.event==='specialist_result'&&['skipped','started'].includes(prior)&&['ok','needs_information','error','denied'].includes(e.status)){
   const success=['ok','needs_information'].includes(e.status);
   if(success&&prior!=='started')throw Error('Result without invocation');
   delegationUI.states[id]=e.status;setAgentState(id,success?'complete':'idle');
   label=e.status==='ok'?'✓ Check returned · not approval':e.status==='needs_information'?'✓ Check returned · information missing':e.status==='denied'?'○ Access denied · no findings':'○ Check unavailable · no findings';
  }else throw Error('Invalid activity transition');
  document.querySelector(`.handoff-card[data-id="${id}"]`).querySelector('.handoff-status').textContent=label;
  logCoord(agentMap[id][0],label);
 }
 try{
  while(true){
   const part=await reader.read();if(run!==chatRun)return;
   // Navigation may precede the first event, even if the user has since returned.
   // Cancel only the late delegation; ordinary conversational replies keep their behaviour.
   if(!requestId&&view!==viewRun){
    cancelChat();$('chatFoot').textContent='Assessment cancelled after navigation · no automatic retry';return;
   }
   if(part.done){ended=true;break;}
   bytes+=part.value.length;if(bytes>32768)throw Error('Activity limit');
   // Server sends ensure_ascii JSON, so chunk boundaries cannot split a UTF-8 character.
   for(const byte of part.value){if(byte>127)throw Error('Invalid encoding');buffer+=String.fromCharCode(byte);}
   let split;
   while((split=buffer.indexOf('\n'))!==-1){
    if(split>16384)throw Error('Event limit');
    const line=buffer.slice(0,split);buffer=buffer.slice(split+1);event(JSON.parse(line));
   }
   if(buffer.length>16384)throw Error('Event limit');
  }
  if(buffer||!final)throw Error('Incomplete activity stream');
  delegationUI.done=true;
  $('coordState').textContent=final.status==='blocked'?'Assessment blocked or partial · no approval':'Checks returned · affordability incomplete';
  $('coordNarrative').textContent='Toby has combined only validated synthetic findings.';
  $('resultTitle').textContent='Cannot confirm batch affordability · no financial approval';
  $('resultBody').textContent=final.reply;
  $('chatFoot').textContent='Synthetic specialist assessment · deterministic summary · no model call';
  for(const item of final.missing){
   const row=document.createElement('div');row.textContent=item.replaceAll('_',' ');$('resultDetails').appendChild(row);
  }
  for(const id of ['bobathan','saul'])if(final.findings[id]){
   const row=document.createElement('div');row.textContent=agentMap[id][0]+' · synthetic audit receipt: '+final.findings[id].audit_id;$('resultDetails').appendChild(row);
  }
  addMessage(final.reply,'bot'); // Deliberately excluded from model history; not model-authored evidence.
 }finally{
  if(!ended)await reader.cancel().catch(()=>{});
  reader.releaseLock?.();
 }
}
