import { el, icona } from './dom.js';
import { comuni } from './api.js';
import { t } from './i18n.js';
export const NON_SO = 'non lo so';
const SI_NO = [{valore: true, etichetta: t('Sì', 'Yes')}, {valore: false, etichetta: 'No'}];
const noto = v => v !== undefined && v !== null && v !== NON_SO;
let sequenza = 0;
function avvisa(nodo, testo, controllo) {
  nodo.querySelector('.errore')?.remove();
  const id = `errore-${++sequenza}`;
  nodo.append(el('p', {id, classe: 'errore', role: 'alert', testo}));
  const input = controllo || nodo.querySelector('input,select,button');
  if (input) { input.setAttribute('aria-invalid', 'true'); input.setAttribute('aria-describedby', id); input.focus({preventScroll: true}); }
  return undefined;
}
function numero(input, nodo, ignoto = false) {
  if (input.value === '') return ignoto ? NON_SO : avvisa(nodo, t('Inserisci un valore oppure scegli Non lo so.', 'Enter a value or choose I don’t know.'), input);
  if (!input.checkValidity() || !Number.isFinite(Number(input.value))) return avvisa(nodo, input.validationMessage || t('Valore non valido.', 'Invalid value.'), input);
  return Number(input.value);
}
const normalizza = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLocaleLowerCase('it');
function controllo(d, valore, giorno) {
  let v = valore;
  const nodo = el('div', {classe: 'risposte'});
  let input, leggi, parziale;
  if (d.tipo === 'si_no' || d.tipo === 'scelta' || d.tipo === 'multipla') {
    const opzioni = d.tipo === 'si_no' ? SI_NO : d.opzioni || [];
    const multiple = d.tipo === 'multipla';
    let scelti = multiple ? (Array.isArray(v) ? [...v] : noto(v) ? [v] : []) : [v];
    const bottoni = opzioni.map(o => el('button', {type: 'button', classe: 'scelta', testo: o.etichetta,
      'aria-pressed': String(scelti.includes(o.valore)), onclick: () => {
        if (multiple) {
          scelti = scelti.includes(o.valore) ? scelti.filter(x => x !== o.valore) : [...scelti, o.valore];
          if (scelti.includes(o.valore)) scelti = scelti.filter(x => x === o.valore || (x !== 'nessuna' && o.valore !== 'nessuna' && !(d.incompatibili || []).some(g => g.includes(x) && g.includes(o.valore))));
        } else scelti = [o.valore];
        bottoni.forEach((b, i) => b.setAttribute('aria-pressed', String(scelti.includes(opzioni[i].valore))));
      }}));
    if (opzioni.length > 8) nodo.append(el('input', {type: 'search', 'aria-label': t('Filtra le scelte', 'Filter the options'), placeholder: t('Filtra le scelte…', 'Filter the options…'), oninput: e => bottoni.forEach((b,i) => b.hidden = !normalizza(opzioni[i].etichetta).includes(normalizza(e.target.value)))}));
    nodo.append(el('div', {classe: multiple ? 'risposte multipla' : 'risposte', role: 'group', 'aria-label': d.testo}, bottoni));
    parziale = () => (scelti.length || (multiple && !d.almeno_una)) ? (multiple ? scelti : scelti[0]) : undefined;
    leggi = () => parziale() !== undefined ? parziale() : avvisa(nodo, t('Scegli una risposta oppure Non lo so.', 'Choose an answer or I don’t know.'));
  } else if (d.tipo === 'numero') {
    input = el('input', {type: 'number', min: d.minimo ?? 0, ...(d.massimo != null ? {max: d.massimo} : {}), step: d.intero ? 1 : 'any', inputmode: 'decimal', 'aria-label': d.testo});
    if (noto(v)) input.value = v;
    nodo.append(el('div', {classe: 'campo'}, input, d.unita ? el('span', {classe: 'unita', testo: d.unita}) : null));
    leggi = () => numero(input, nodo);
  } else if (d.tipo === 'comune') {
    const id = `comuni-${++sequenza}`;
    const lista = el('datalist', {id});
    input = el('input', {type: 'text', list: id, autocomplete: 'off', 'aria-label': d.testo, placeholder: t('Nome del comune', 'Name of the municipality')});
    if (noto(v)) input.value = v;
    let elenco = null, fallita = false, regione = null, richiesta = 0;
    const stato = el('span', {role: 'status', testo: t('Caricamento comuni…', 'Loading municipalities…')});
    const carica = async r => {
      regione = r; const token = ++richiesta; elenco = null; fallita = false;
      try { const c = await comuni(r || ''); if (token !== richiesta) return; elenco = c; lista.replaceChildren(...c.map(nome => el('option', {value: nome}))); stato.textContent = t('Scegli un comune riconosciuto; puoi rispondere Non lo so.', 'Choose a recognised municipality; you can answer I don’t know.'); }
      catch { if (token !== richiesta) return; fallita = true; stato.textContent = t('Lista non disponibile. Riprova o scegli Non lo so.', 'List unavailable. Try again or choose I don’t know.'); }
    };
    nodo.append(el('div', {classe: 'campo'}, input), lista, stato,
      el('button', {type: 'button', classe: 'link-indietro', testo: t('Ricarica comuni', 'Reload municipalities'), onclick: () => carica(regione)}));
    carica(d.regione || '');
    leggi = () => {
      if (!elenco) return avvisa(nodo, fallita ? t('Ricarica la lista o scegli Non lo so.', 'Reload the list or choose I don’t know.') : t('Attendi il caricamento dei comuni.', 'Wait for the municipalities to load.'), input);
      const corrispondenze = elenco.filter(c => normalizza(c) === normalizza(input.value));
      if (corrispondenze.length !== 1) return avvisa(nodo, t('Scegli un comune dell’elenco, oppure Non lo so. Non correggiamo automaticamente i nomi.', 'Choose a municipality from the list, or I don’t know. We don’t auto-correct names.'), input);
      return corrispondenze[0];
    };
    return {nodo, leggi, valore: () => input.value.trim(), carica, svuota: () => { input.value = ''; }};
  } else {
    input = el('input', {type: d.tipo === 'data' ? 'date' : 'text', ...(d.tipo === 'data' ? {max: giorno} : {}), 'aria-label': d.testo});
    if (noto(v) && v !== 'nessuno') input.value = v;
    nodo.append(el('div', {classe: 'campo'}, input));
    let speciale = v === 'nessuno' ? 'nessuno' : undefined;
    input.addEventListener('input', () => speciale = undefined);
    for (const o of d.opzioni || []) nodo.append(el('button', {type:'button', classe:'scelta', testo:o.etichetta, 'aria-pressed':String(v === o.valore), onclick:e => {speciale=o.valore; input.value=''; e.currentTarget.setAttribute('aria-pressed','true');}}));
    leggi = () => speciale || (input.value && input.checkValidity() ? input.value : avvisa(nodo, t('Indica una risposta valida oppure Non lo so.', 'Give a valid answer or I don’t know.'), input));
  }
  return {nodo, leggi, valore: () => input ? input.value === '' ? undefined : d.tipo === 'numero' ? Number(input.value) : input.value : parziale ? parziale() : leggi()};
}
function nucleo(valore) {
  const persone = Array.isArray(valore) ? structuredClone(valore) : [{}];
  const righe = el('div', {classe:'persone'});
  const disegna = () => {
    righe.replaceChildren(...persone.map((c,i) => {
      const input = el('input', {type:'number', min:0, max:120, step:1, 'aria-label':i===0 ? t('La tua età', 'Your age') : t(`Età persona ${i+1}`, `Age of person ${i+1}`), placeholder:t('Età o vuoto se non nota', 'Age, or empty if unknown'), oninput:()=> { c.eta = input.value === '' ? NON_SO : Number(input.value); }});
      if (noto(c.eta)) input.value=c.eta;
      return el('div', {classe:'riga-persona'}, el('span',{classe:'chi',testo:i===0?t('Tu', 'You'):t(`Persona ${i+1}`, `Person ${i+1}`)}),input,
        i ? el('button',{type:'button',classe:'togli','aria-label':t(`Togli persona ${i+1}`, `Remove person ${i+1}`),testo:'×',onclick:()=>{persone.splice(i,1);disegna();}}):null);
    }));
  };
  disegna();
  const nodo=el('div',{classe:'risposte'},righe,el('p',{testo:t('Puoi lasciare vuota l’età di una singola persona: resterà non nota.', 'You can leave one person’s age empty: it will stay unknown.')}),el('button',{type:'button',classe:'pulsante secondario',testo:t('+ Aggiungi una persona', '+ Add a person'),onclick:()=>{if(persone.length<100){persone.push({});disegna();}}}));
  const leggi = () => {
    for(const input of righe.querySelectorAll('input')) if(input.value !== '' && !input.checkValidity()) return avvisa(nodo,t('L’età deve essere un intero tra 0 e 120.', 'Age must be a whole number between 0 and 120.'), input);
    return persone.map(c=>({...c,eta:c.eta ?? NON_SO}));
  };
  return {nodo,leggi,nonSo:()=>[...righe.querySelectorAll('input')].some(i=>i.value !== '') ? leggi() : NON_SO,scrivi:(p,v)=>{p.nucleo=v;}};
}
function pagina(d, p, giorno) {
  const valori = {...d.valori_attuali, ...p};
  const righe=[];
  const nodo=el('div',{classe:'persone'});
  const visibile=parte=>Object.entries(parte.se || {}).every(([k,v])=>valori[k]===v && (!righe.find(r=>r.parte.campo===k) || visibile(righe.find(r=>r.parte.campo===k).parte)));
  const aggiorna=()=>righe.forEach(r=>{
    r.nodo.hidden=!visibile(r.parte);
    if(r.parte.tipo==='comune') {
      const reg=valori[r.parte.regione_da] || '';
      if(r.regione!==reg){if(r.regione!==undefined){r.c.svuota();delete valori[r.parte.campo];}r.regione=reg;r.c.carica(reg);}
    }
  });
  for(const parte of d.parti){
    const c=controllo({...parte,regione:valori[parte.regione_da]},valori[parte.campo],giorno);
    const n=el('div',{classe:'riga-persona componente'},el('p',{classe:'chi',testo:parte.testo}),c.nodo,
      el('button',{type:'button',classe:'link-indietro',testo:t('Non lo so', 'I don’t know'),onclick:()=>{valori[parte.campo]=NON_SO; n.querySelectorAll('[aria-pressed]').forEach(b=>b.setAttribute('aria-pressed','false')); n.querySelector('input')?.setAttribute('placeholder',t('Non lo so', 'I don’t know')); aggiorna();}}));
    const r={parte,c,nodo:n};righe.push(r);nodo.append(n);
    const cambia=()=>{valori[parte.campo]=c.valore();aggiorna();};
    c.nodo.addEventListener('click',cambia);c.nodo.addEventListener('input',cambia);c.nodo.addEventListener('change',cambia);
  }
  aggiorna();
  const leggi=(ignora=false)=>{
    const out={};
    for(const r of righe){
      if(!visibile(r.parte)){
        // Un dettaglio nascosto non è una risposta: solo la pagina interamente ignota marca i campi non ripetibili.
        if (valori[d.parti[0].campo] === NON_SO) out[r.parte.campo]=NON_SO;
        continue;
      }
      if(valori[r.parte.campo]===NON_SO){out[r.parte.campo]=NON_SO;continue;}
      if(ignora && !noto(valori[r.parte.campo])){out[r.parte.campo]=NON_SO;continue;}
      const v=r.c.leggi();if(v===undefined)return undefined;out[r.parte.campo]=v;
    }
    return out;
  };
  return {nodo,leggi,nonSo:()=>leggi(true),scrivi:(p,v)=>Object.assign(p,v)};
}
function componenti(d,p,giorno){
  const campo=d.campo.split('.')[1];
  const righe=d.componenti.map(c=>{
    const nome=c.indice===0?t('Tu', 'You'):t(`Persona ${c.indice+1}`, `Person ${c.indice+1}`);
    let nonSo=(p.nucleo?.[c.indice]?.[campo]===NON_SO);
    const controllo_=controllo({...d,testo:nome},p.nucleo?.[c.indice]?.[campo],giorno);
    const n=el('div',{classe:'riga-persona componente'},el('p',{classe:'chi',testo:nome}),controllo_.nodo,
      el('button',{type:'button',classe:'link-indietro',testo:t('Non lo so', 'I don’t know'),onclick:e=>{nonSo=true;e.currentTarget.textContent=t('Dato non noto', 'Unknown');}}));
    controllo_.nodo.addEventListener('click',()=>nonSo=false);controllo_.nodo.addEventListener('input',()=>nonSo=false);
    return {c,nodo:n,leggi:(ignora=false)=>nonSo || (ignora && controllo_.valore() === undefined) ? NON_SO : controllo_.leggi()};
  });
  const leggi=(ignora=false)=>{const v=righe.map(r=>r.leggi(ignora));return v.includes(undefined)?undefined:v;};
  return {nodo:el('div',{classe:'persone'},righe.map(r=>r.nodo)),leggi,nonSo:()=>leggi(true),scrivi:(p,v)=>righe.forEach((r,i)=>{p.nucleo[r.c.indice][campo]=v===NON_SO?NON_SO:v[i];})};
}
export function mostraDomanda(box,d,azioni){
  const p=azioni.profilo || {};
  const corpo=d.per_componente?componenti(d,p,azioni.giorno):d.tipo==='nucleo'?nucleo(p.nucleo):d.tipo==='pagina'?pagina(d,p,azioni.giorno):controllo(d,p[d.campo] ?? d.valore_attuale,azioni.giorno);
  const scrivi=corpo.scrivi || ((p,v)=>{p[d.campo]=v;});
  const invia=()=>{const v=corpo.leggi();if(v!==undefined)azioni.rispondi(p=>scrivi(p,v));};
  const nodo=el('div',{classe:'domanda'},
    d.bandi_interessati?el('p',{classe:'domanda-perche',testo:t(`Questa domanda aiuta a valutare ${d.bandi_interessati} ${d.bandi_interessati === 1 ? 'misura' : 'misure'}`, `This question helps assess ${d.bandi_interessati} ${d.bandi_interessati === 1 ? 'benefit' : 'benefits'}`)}) : null,
    el('h2',{id:'testo-domanda',tabindex:'-1',classe:'domanda-testo',testo:d.testo}),
    d.aiuto?el('p',{classe:'domanda-aiuto',testo:d.aiuto}):null,
    corpo.nodo,
    el('div',{classe:'azioni-domanda'},el('button',{type:'button',classe:'pulsante primario',testo:t('Avanti →', 'Next →'),onclick:invia}),
      el('button',{type:'button',classe:'pulsante secondario',testo:d.tipo==='pagina'?t('Prosegui con i dati parziali / non noti', 'Continue with partial / unknown data'):t('Non lo so', 'I don’t know'),onclick:()=>{const v=corpo.nonSo?corpo.nonSo():NON_SO;if(v!==undefined)azioni.rispondi(p=>scrivi(p,v));}}),
      el('button',{type:'button',classe:'link-indietro',testo:t('← Indietro', '← Back'),disabled:!azioni.puoTornare,onclick:azioni.indietro})));
  nodo.addEventListener('keydown',e=>{if(e.key==='Enter'&&e.target.tagName==='INPUT'&&e.target.type!=='search'){e.preventDefault();invia();}});
  box.replaceChildren(nodo);
  (box.querySelector('input') || box.querySelector('h2')).focus({preventScroll:true});
}
