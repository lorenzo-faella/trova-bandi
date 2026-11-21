// Risultati dal vivo: tessere per esito (anche filtri), schede che si riordinano con FLIP, citazioni e fonte.
import { el, icona } from "./dom.js";
import { conta, flip, apriChiudi } from "./animazioni.js";

// I sei esiti del motore (pipeline/motore.py) con nomi in linguaggio semplice.
export const STATI = {
  "idoneo": { classe: "st-idoneo", tessera: "Compatibili", etichetta: "Requisiti controllati compatibili", icona: "spunta",
    spiega: "Confronto dei requisiti rappresentati con le tue risposte; non garantisce assegnazione o pagamento:" },
  "idoneo, salvo eccezioni": { classe: "st-salvo", tessera: "Salvo casi particolari", etichetta: "Compatibile con riserve specifiche", icona: "scudo",
    spiega: "I controlli rappresentati sono compatibili. Verifica le riserve elencate:" },
  "quasi idoneo": { classe: "st-quasi", tessera: "Requisito non soddisfatto", etichetta: "Ti manca un requisito", icona: "orologio",
    spiega: "Questo requisito non è soddisfatto. Cambiarlo può richiedere una modifica sostanziale:" },
  "da verificare": { classe: "st-verificare", tessera: "Possibili", etichetta: "Possibile: da controllare", icona: "lente",
    spiega: "Nessun requisito che sappiamo controllare ti esclude. Resta da verificare sul bando:" },
  "mancano dati": { classe: "st-mancano", tessera: "Servono risposte", etichetta: "Serve un'altra risposta", icona: "domanda",
    spiega: "Per decidere ci serve sapere:" },
  "non idoneo": { classe: "st-no", tessera: "Requisiti non soddisfatti", etichetta: "Un requisito controllato non è soddisfatto", icona: "croce",
    spiega: "Il bando chiede, e tu non hai:" },
};
const ORDINE = Object.keys(STATI);

// Dove va un risultato nella pagina (decisione 70). "lontano": bando locale di un'altra regione (la regola spesso non
// scrive il vincolo territoriale); "ignoto": da verificare senza nessun requisito già soddisfatto, cioè non sappiamo
// niente. Nessuno dei due conta tra i "possibili".
export function posto(r, ctx) {
  return r.gruppo ?? null;
}

export function contaVisibili(risultati, ctx) {
  const c = Object.fromEntries(ORDINE.map(s => [s, 0]));
  let lontani = 0, ignoti = 0, date = 0, futuri = 0;
  for (const r of risultati) {
    const p = posto(r, ctx);
    if (p === "lontano") lontani++;
    else if (p === "ignoto") ignoti++;
    else if (p === "date") date++;
    else if (p === "futuri") futuri++;
    else c[r.stato]++;
  }
  return { conteggi: c, lontani, ignoti, date, futuri };
}
const PAGINA = 40;

const stato = { conteggi: {}, filtro: null, ricerca: "", limite: PAGINA, nodi: new Map(), precedenti: new Map(), aperti: new Set(), primo: true };
let ultimo = null, contesto = null;

export function azzera() {
  Object.assign(stato, { filtro: null, ricerca: "", limite: PAGINA, nodi: new Map(), precedenti: new Map(), aperti: new Set(), primo: true });
  document.getElementById("tessere").replaceChildren();
  document.getElementById("lista").replaceChildren();
  document.getElementById("cerca").value = "";
}

export function iniziaStrumenti() {
  document.getElementById("cerca").addEventListener("input", e => { stato.ricerca = e.target.value.trim().toLowerCase(); stato.limite = PAGINA; disegnaLista(); });
}

// dati: risposta di /api/passo; ctx: { ramo, regioni }
export function mostraRisultati(dati, ctx) {
  ultimo = dati;
  contesto = ctx;
  document.getElementById("giorno").textContent = `Valutazione al ${new Date(`${dati.giorno}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric" })}`;
  const { conteggi } = contaVisibili(dati.risultati, ctx);
  stato.conteggi = conteggi;
  disegnaTessere(conteggi);
  disegnaLista();
  disegnaRiassuntoMobile(conteggi);
  stato.primo = false;
}

function disegnaTessere(conteggi) {
  const box = document.getElementById("tessere");
  if (!box.children.length) {
    for (const s of ORDINE) {
      const t = el("button", { classe: `tessera ${STATI[s].classe}`, type: "button", "aria-pressed": "false", "data-stato": s,
        onclick: () => { stato.filtro = stato.filtro === s ? null : s; stato.limite = PAGINA; disegnaTessere(stato.conteggi); disegnaLista(); } },
        el("span", { classe: "tessera-num", testo: "0" }), el("span", { classe: "tessera-nome", testo: STATI[s].tessera }));
      box.append(t);
    }
  }
  for (const t of box.children) {
    const s = t.dataset.stato, n = conteggi[s] || 0;
    const num = t.querySelector(".tessera-num");
    if (Number(num.dataset.valore || 0) !== n && !stato.primo) {
      t.classList.remove("batte"); void t.offsetWidth; t.classList.add("batte");
    }
    conta(num, n, 700);
    t.classList.toggle("spenta", n === 0);
    t.setAttribute("aria-pressed", String(stato.filtro === s));
    t.setAttribute("aria-label", `${STATI[s].tessera}: ${n}. ${stato.filtro === s ? "Filtro attivo, premi per toglierlo" : "Premi per vedere solo questi"}`);
  }
}

function ordina(a, b) {
  return ORDINE.indexOf(a.stato) - ORDINE.indexOf(b.stato)
    || (a.perche.length - b.perche.length)
    || (a.chiusura || "9999").localeCompare(b.chiusura || "9999")
    || a.titolo.localeCompare(b.titolo, "it");
}

function disegnaLista() {
  if (!ultimo) return;
  const lista = document.getElementById("lista");
  const q = stato.ricerca;
  let voci = ultimo.risultati.filter(r => !q || `${r.titolo} ${r.ente || ""}`.toLowerCase().includes(q));
  const tutteNo = voci.filter(r => r.stato === "non idoneo");
  const lontani = voci.filter(r => posto(r, contesto) === "lontano").sort(ordina);
  const date = voci.filter(r => posto(r,contesto) === 'date').sort(ordina);
  const futuri = voci.filter(r => posto(r,contesto) === 'futuri').sort(ordina);
  const ignoti = voci.filter(r => posto(r, contesto) === "ignoto").sort(ordina);
  voci = voci.filter(r => !posto(r, contesto));
  voci = stato.filtro ? voci.filter(r => r.stato === stato.filtro) : voci.filter(r => r.stato !== "non idoneo");
  voci.sort(ordina);
  const regione = contesto.ramo === "persone" && contesto.regioni?.length ? contesto.regioni.join(", ") : null;
  const vicini = voci;

  flip(lista, () => {
    const figli = [];
    if (!voci.length && !(ignoti.length || lontani.length) || (stato.filtro && !voci.length)) {
      figli.push(el("p", { classe: "vuoto", testo: q ? "Nessun bando corrisponde alla ricerca." : stato.filtro ? "Nessun bando con questo esito." : "Rispondi alla prima domanda: i risultati compaiono qui." }));
    }
    if (vicini.length) {
      if (regione) figli.push(el("p", { classe: "gruppo-titolo", testo: `Nazionali e in ${regione}` }));
      figli.push(...vicini.slice(0, stato.limite).map(r => scheda(r)));
      if (vicini.length > stato.limite) {
        figli.push(el("button", { classe: "pulsante fantasma altri", type: "button", testo: `Mostra altri ${Math.min(PAGINA, vicini.length - stato.limite)} (su ${vicini.length})`,
          onclick: () => { stato.limite += PAGINA; disegnaLista(); } }));
      }
    }
    if (!stato.filtro && date.length) figli.push(gruppoChiuso(`Disponibilità non verificata (${date.length}): controlla la finestra della tua edizione`,date));
    if (!stato.filtro && futuri.length) figli.push(gruppoChiuso(`Aperture future documentate (${futuri.length})`,futuri));
    if (!stato.filtro && ignoti.length) {
      figli.push(gruppoChiuso(`Non sappiamo dirlo (${ignoti.length}): il requisito decisivo non è tra quelli che sappiamo controllare`, ignoti));
    }
    // Chiusi da poco (decisione 72): solo vicini, fuori dai conteggi; di solito riaprono l'anno dopo.
    const chiusi = (ultimo.chiusi_di_recente || []).filter(r => posto(r, contesto) !== "lontano"
      && (!q || `${r.titolo} ${r.ente || ""}`.toLowerCase().includes(q)));
    if (!stato.filtro && chiusi.length) {
      figli.push(gruppoChiuso(`Chiusi da poco (${chiusi.length}): nuove edizioni non verificate`, chiusi, true));
    }
    if (!stato.filtro && lontani.length) {
      figli.push(gruppoChiuso(`In altre regioni (${lontani.length}): provenienza dell’ente: pertinenza da verificare, non esclusione`, lontani));
    }
    if (!stato.filtro && tutteNo.length) {
      figli.push(gruppoChiuso(`Requisiti non soddisfatti (${tutteNo.length})`, tutteNo.sort(ordina)));
    }
    lista.replaceChildren(...figli);
  });
  for (const r of ultimo.risultati) stato.precedenti.set(r.id, r.stato);
}

function gruppoChiuso(titolo, voci, chiusi = false) {
  const d = el("details", { classe: "gruppo-chiuso" }, el("summary", { testo: titolo }));
  d.addEventListener("toggle", () => { if (d.open && d.children.length === 1) d.append(...voci.map(r => scheda(r, chiusi))); });
  return d;
}

function quando(chiusura) {
  if (!chiusura || !ultimo) return null;
  const giorni = Math.round((new Date(`${chiusura}T12:00:00`) - new Date(`${ultimo.giorno}T12:00:00`)) / 86400000);
  if (giorni < 0 || giorni > 730) return null;  // l'open data mette 2050 ai bandi senza scadenza
  const testo = giorni === 0 ? "chiude oggi" : giorni === 1 ? "chiude domani" : giorni <= 60 ? `chiude tra ${giorni} giorni`
    : `chiude il ${new Date(`${chiusura}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "short", year: "numeric" })}`;
  return el("span", { classe: `etichetta scade${giorni <= 7 ? " urgente" : ""}` }, icona("orologio"), testo);
}

function origine(r) {
  if (r.origine === "estratta") return el("span", { classe: "etichetta estratta", title: "Requisiti letti da un modello linguistico e non ancora rivisti da noi", testo: "estratta automaticamente" });
  if (r.origine === "riferimento") return el("span", { classe: "etichetta rivista", testo: r.revisione_umana ? "revisione umana documentata" : "regola di riferimento · revisione non attestata" });
  if (r.origine === "open data") return el("span", { classe: "etichetta", testo: "incentivi.gov.it" });
  return null;
}

function scheda(r, chiuso = false) {
  const data = r.chiusura ? new Date(`${r.chiusura}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long", year: "numeric" }) : "";
  const info = chiuso
    ? { ...STATI[r.stato], classe: "st-chiuso", etichetta: `Chiuso il ${data}: nuove edizioni non verificate`, icona: "calendario",
        spiega: "Questa edizione è archiviata. Non è verificata una nuova apertura. Requisiti della versione conservata:" }
    : posto(r, contesto) === "ignoto"
      ? { ...STATI[r.stato], etichetta: "Non sappiamo dirlo", spiega: "Il requisito che decide non è tra quelli che sappiamo controllare:" }
      : STATI[r.stato];
  const prima = stato.precedenti.get(r.id);
  const corpoDentro = el("div", { classe: "scheda-corpo-dentro" },
    (r.stato === "idoneo" ? r.requisiti : r.perche).length ? el("p", { classe: "spiega", testo: info.spiega }) : null,
    elencoRequisiti(r.stato === "idoneo" ? r.requisiti : r.perche),
    r.stato === "idoneo, salvo eccezioni" && r.requisiti.length
      ? el("details", {}, el("summary", { testo: `Tutti i requisiti (${r.requisiti.length})` }), elencoRequisiti(r.requisiti)) : null,
    r.avvertenze?.length ? el('div',{classe:'limiti'},el('strong',{testo:'Perimetro e limiti'}),r.avvertenze.map(t=>el('p',{testo:t}))) : null,
    r.note?.length ? el('details',{},el('summary',{testo:'Note della fonte e condizioni da approfondire'}),r.note.map(t=>el('p',{testo:t}))) : null,
    r.versioni_precedenti?.length ? el('p',{testo:`Versioni conservate: ${r.versioni_precedenti.map(v=>v.id).join(', ')}`}) : null,
    el('p',{testo:`Disponibilità: ${r.stato_temporale}. Data di composizione/aggiornamento regola: ${r.aggiornamento_regola || 'non registrata'}; revisione umana: ${r.revisione_umana || 'non attestata'}.`}),
    r.prossimo_passo ? el('p',{classe:'prossimo-passo',testo:r.prossimo_passo}) : null,
    r.link ? el("a", { classe: "pulsante secondario piccolo apri-fonte", href: r.link, target: "_blank", rel: "noopener" }, "Apri il bando ufficiale ↗") : null);
  const corpo = el("div", { classe: "scheda-corpo" }, corpoDentro);
  const aperta = stato.aperti.has(r.id);
  const nodo = el("article", { classe: `scheda ${info.classe}`, "data-chiave": r.id, "aria-expanded": String(aperta) });
  const testa = el("button", { classe: "scheda-testa", type: "button", "aria-expanded": String(aperta),
    onclick: () => {
      const apri = nodo.getAttribute("aria-expanded") !== "true";
      nodo.setAttribute("aria-expanded", String(apri));
      testa.setAttribute("aria-expanded", String(apri));
      if (apri) stato.aperti.add(r.id); else stato.aperti.delete(r.id);
      apriChiudi(corpo, apri);
    } },
    el("span", { classe: "scheda-icona" }, icona(info.icona)),
    el("span", {},
      el("span", { classe: "scheda-stato", testo: info.etichetta }),
      el("span", { classe: "scheda-titolo", testo: r.titolo }),
      el("span", { classe: "scheda-meta" },
        r.ente ? el("span", { testo: r.ente }) : null,
        r.regione ? el("span", { classe: "etichetta", testo: r.regione }) : null,
        quando(r.chiusura), origine(r))),
    el("span", { classe: "scheda-freccia" }, icona("freccia")));
  nodo.append(testa, corpo);
  if (aperta) corpo.style.height = "auto";
  if (!stato.primo && prima === undefined) nodo.classList.add("nuova");
  else if (prima && prima !== r.stato) nodo.classList.add("cambiata");
  return nodo;
}

function elencoRequisiti(voci) {
  if (!voci?.length) return null;
  return el('ul',{classe:'requisiti'},voci.map(v=>el('li',{},
    el('span',{testo:v.testo}),
    v.risposta !== undefined ? el('p',{classe:'confronto',testo:`La tua risposta: ${v.risposta}. Confronto: ${v.verificato === true ? 'soddisfatto' : v.verificato === false ? 'non soddisfatto' : 'non determinabile'}.`}) : null,
    v.come_verificare ? el('p',{testo:v.come_verificare}) : null,
    v.figli ? elencoRequisiti(v.figli) : null,
    v.citazione ? el('blockquote',{testo:`«${v.citazione}»`}) : null,
    v.fonte ? el('div',{classe:'da-dove',testo:v.fonte}) : null)));
}

let ambitoStampa = 'principali';
function preparaReport() {
  document.getElementById('report-stampa')?.remove();
  if (!ultimo) return;
  const voci = ambitoStampa === 'tutto' ? [...ultimo.risultati,...(ultimo.chiusi_di_recente || [])]
    : ultimo.risultati.filter(r=>!r.gruppo && r.stato !== 'non idoneo');
  const report=el('section',{id:'report-stampa'},el('h1',{testo:'trova-bandi · report dei confronti'}),
    el('p',{testo:`Valutazione: ${ultimo.giorno}. Perimetro: ${ambitoStampa === 'tutto' ? 'intero catalogo valutato e archivio recente' : 'risultati principali non esclusi'}. ${voci.length} misure, senza paginazione o filtri di ricerca.`}),
    el('p',{testo:'Compatibilità dei requisiti rappresentati, disponibilità della domanda, graduatoria e pagamento sono verifiche distinte. Le citazioni autentiche non certificano completezza o interpretazione delle regole.'}),
    el('nav',{'aria-label':'Indice delle misure nel report'},el('h2',{testo:'Indice delle misure'}),
      el('ol',{},voci.map((r,i)=>el('li',{},el('a',{href:`#report-misura-${i}`,testo:`${r.titolo} · ${STATI[r.stato].etichetta} · ${r.stato_temporale}`}))))),
    el('h2',{testo:'Risposte fornite'}),el('dl',{},(ultimo.riepilogo || []).flatMap(r=>[el('dt',{testo:r.voce}),el('dd',{testo:r.valore})])),
    voci.map((r,i)=>el('article',{classe:'voce-report',id:`report-misura-${i}`},el('h2',{testo:r.titolo}),
      el('p',{testo:`${STATI[r.stato].etichetta}. Disponibilità: ${r.stato_temporale}. ${r.ente || ''}`}),
      elencoRequisiti(r.requisiti),el('h3',{testo:'Limiti, note e prossimo passo'}),
      [...(r.avvertenze || []),...(r.note || []),r.prossimo_passo].filter(Boolean).map(t=>el('p',{testo:t})),
      el('p',{testo:`Fonte: ${r.link || 'non disponibile'}. Versione regola: ${r.versione_regola || 'non registrata'}. Revisione umana: ${r.revisione_umana || 'non attestata'}.`}))));
  document.body.append(report);
}
window.addEventListener('beforeprint',preparaReport);
window.addEventListener('afterprint',()=>document.getElementById('report-stampa')?.remove());
export function stampaReport(ambito = 'principali') {ambitoStampa=ambito;preparaReport();window.print();}

function disegnaRiassuntoMobile(conteggi) {
  const b = document.getElementById("riassunto-mobile");
  const voci = ORDINE.filter(s => s !== "non idoneo" && conteggi[s]).slice(0, 3);
  const pillole = voci.map(s => el("span", { classe: `pillola ${STATI[s].classe}` }, el("b", { testo: String(conteggi[s]) }), ` ${STATI[s].tessera}`));
  b.replaceChildren(...(pillole.length ? pillole : [el("span", { testo: "Vai ai risultati" })]));
}
