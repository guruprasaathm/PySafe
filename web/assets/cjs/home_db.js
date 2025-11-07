// web/assets/cjs/home_db.js
(function () {
  const $ = (s) => document.querySelector(s);

  async function safeCall(fn, ...args) {
    if (!window.eel || !window.eel[fn]) return null;
    try { return await window.eel[fn](...args)(); } catch { return null; }
  }

  async function refreshDbCard() {
    const s = await safeCall('db_status'); // { connected, dbName, filesCount, textsCount, storageMB }
    const status = $('#db-status'), files = $('#db-files'), texts = $('#db-texts'), storage = $('#db-storage');
    if (!s || !s.connected) {
      status?.classList.remove('status-on'); status?.classList.add('status-off');
      if (status) status.title = 'Disconnected';
      if (files) files.textContent = '—'; if (texts) texts.textContent = '—'; if (storage) storage.textContent = '—';
      return;
    }
    status?.classList.remove('status-off'); status?.classList.add('status-on');
    status.title = `Connected to ${s.dbName}`;
    if (files) files.textContent = s.filesCount ?? 0;
    if (texts) texts.textContent = s.textsCount ?? 0;
    if (storage) storage.textContent = s.storageMB ? `${s.storageMB} MB` : '—';
  }

  function headersFor(type){return type==='auth'?['Time','User','Action','Success','IP','Device','Reason']:['Time','User','Library','Action','Bytes','Latency (ms)','Success','Error'];}
  function toLocal(ts){try{return new Date(ts).toLocaleString();}catch{return ts;}}
  function renderHead(type){const tr=$('#logs-head'); tr.innerHTML=''; for(const h of headersFor(type)){const th=document.createElement('th'); th.textContent=h; tr.appendChild(th);}}
  function renderRows(type,rows){const tb=$('#logs-rows'); tb.innerHTML=''; (rows||[]).forEach(r=>{const tr=document.createElement('tr'); tr.innerHTML=(type==='auth')?
    `<td>${toLocal(r.ts)}</td><td>${r.username??''}</td><td>${r.action}</td><td>${r.success?'✔':'✖'}</td><td>${r.ip??''}</td><td>${r.deviceId??''}</td><td>${r.reason??''}</td>`:
    `<td>${toLocal(r.ts)}</td><td>${r.userId?.slice(0,8)??''}</td><td>${(r.libraryId||'').toString().slice(0,8)}</td><td>${r.action}</td><td>${r.bytes??''}</td><td>${r.latencyMs??''}</td><td>${r.success?'✔':'✖'}</td><td>${r.error??''}</td>`; tb.appendChild(tr);});}
  async function renderLogs(){const type=$('#logs-type').value; const limit=parseInt($('#logs-limit').value,10)||200; renderHead(type); const rows=await safeCall('fetch_logs',type,limit)||[]; renderRows(type,rows);}

  function exportCSV(){const type=$('#logs-type').value; const head=headersFor(type); const rows=Array.from($('#logs-rows').querySelectorAll('tr')).map(tr=>Array.from(tr.children).map(td=>`"${(td.textContent||'').replace(/"/g,'""')}"`).join(',')); const csv=[head.join(','),...rows].join('\n'); const blob=new Blob([csv],{type:'text/csv'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=`pysafe_${type}_logs.csv`; a.click(); URL.revokeObjectURL(url);}

  document.addEventListener('DOMContentLoaded',()=>{
    $('#btn-open-logs')?.addEventListener('click',()=>{$('#logs-modal').classList.remove('hidden'); renderLogs();});
    $('#logs-close')?.addEventListener('click',()=>$('#logs-modal').classList.add('hidden'));
    $('#logs-refresh')?.addEventListener('click',renderLogs);
    $('#logs-export')?.addEventListener('click',exportCSV);
    refreshDbCard(); setInterval(refreshDbCard, 20000);
  });
})();
