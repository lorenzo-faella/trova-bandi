// Risultati dal vivo: tessere per esito (anche filtri), schede che si riordinano con FLIP, citazioni e fonte.
import { el, icona } from "./dom.js";
import { conta, flip, apriChiudi } from "./animazioni.js";
import { t, LOCALE, temporale, fonte } from "./i18n.js";

// I sei esiti del motore (pipeline/motore.py) con nomi in linguaggio semplice.
export const STATI = {
  "idoneo": { classe: "st-idoneo", tessera: t("Compatibili", "Compatible"), etichetta: t("Compatibile con il tuo profilo", "Compatible with your profile"), icona: "spunta",
    spiega: t("I requisiti del bando e le tue risposte:", "The requirements of the call and your answers:") },
  "idoneo, salvo eccezioni": { classe: "st-salvo", tessera: t("Salvo casi particolari", "Barring special cases"), etichetta: t("Compatibile, salvo casi particolari", "Compatible, barring special cases"), icona: "scudo",
    spiega: t("Sei in regola con i requisiti principali. Controlla questi casi particolari:", "You meet the main requirements. Check these special cases:") },
  "quasi idoneo": { classe: "st-quasi", tessera: t("Manca un solo requisito", "One requirement missing"), etichetta: t("Ti manca un requisito", "You miss one requirement"), icona: "orologio",
    spiega: t("Ti manca questo requisito:", "You are missing this requirement:") },
  "da verificare": { classe: "st-verificare", tessera: t("Possibili", "Possible"), etichetta: t("Possibile: da verificare", "Possible: to be checked"), icona: "lente",
    spiega: t("Niente di quello che ci hai detto ti esclude. Da verificare sul bando:", "Nothing you told us rules you out. To check on the call:") },
  "mancano dati": { classe: "st-mancano", tessera: t("Servono risposte", "Answers needed"), etichetta: t("Serve un'altra risposta", "Another answer needed"), icona: "domanda",
    spiega: t("Per decidere ci serve sapere:", "To decide we need to know:") },
  "non idoneo": { classe: "st-no", tessera: t("Non compatibili", "Not compatible"), etichetta: t("Non compatibile", "Not compatible"), icona: "croce",
    spiega: t("Il bando chiede, e tu non hai:", "The call requires, and you don't have:") },
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
  document.getElementById("giorno").textContent = `${t("Valutazione al", "Assessed on")} ${new Date(`${dati.giorno}T12:00:00`).toLocaleDateString(LOCALE, { day: "numeric", month: "long", year: "numeric" })}`;
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
      const tessera = el("button", { classe: `tessera ${STATI[s].classe}`, type: "button", "aria-pressed": "false", "data-stato": s,
        onclick: () => { stato.filtro = stato.filtro === s ? null : s; stato.limite = PAGINA; disegnaTessere(stato.conteggi); disegnaLista(); } },
        el("span", { classe: "tessera-num", testo: "0" }), el("span", { classe: "tessera-nome", testo: STATI[s].tessera }));
      box.append(tessera);
    }
  }
  for (const tessera of box.children) {
    const s = tessera.dataset.stato, n = conteggi[s] || 0;
    const num = tessera.querySelector(".tessera-num");
    if (Number(num.dataset.valore || 0) !== n && !stato.primo) {
      tessera.classList.remove("batte"); void tessera.offsetWidth; tessera.classList.add("batte");
    }
    conta(num, n, 700);
    tessera.classList.toggle("spenta", n === 0);
    tessera.setAttribute("aria-pressed", String(stato.filtro === s));
    tessera.setAttribute("aria-label", `${STATI[s].tessera}: ${n}. ${stato.filtro === s ? t("Filtro attivo, premi per toglierlo", "Filter on, press to remove it") : t("Premi per vedere solo questi", "Press to see only these")}`);
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
      figli.push(el("p", { classe: "vuoto", testo: q ? t("Nessun bando corrisponde alla ricerca.", "No call matches your search.") : stato.filtro ? t("Nessun bando con questo esito.", "No call with this outcome.") : t("Rispondi alla prima domanda: i risultati compaiono qui.", "Answer the first question: results appear here.") }));
    }
    if (vicini.length) {
      if (regione) figli.push(el("p", { classe: "gruppo-titolo", testo: t(`Nazionali e in ${regione}`, `National and in ${regione}`) }));
      figli.push(...vicini.slice(0, stato.limite).map(r => scheda(r)));
      if (vicini.length > stato.limite) {
        figli.push(el("button", { classe: "pulsante fantasma altri", type: "button", testo: t(`Mostra altri ${Math.min(PAGINA, vicini.length - stato.limite)} (su ${vicini.length})`, `Show ${Math.min(PAGINA, vicini.length - stato.limite)} more (of ${vicini.length})`),
          onclick: () => { stato.limite += PAGINA; disegnaLista(); } }));
      }
    }
    if (!stato.filtro && date.length) figli.push(gruppoChiuso(t(`Date da confermare (${date.length})`, `Dates to be confirmed (${date.length})`),date));
    if (!stato.filtro && futuri.length) figli.push(gruppoChiuso(t(`Apriranno prossimamente (${futuri.length})`, `Opening soon (${futuri.length})`),futuri));
    if (!stato.filtro && ignoti.length) {
      figli.push(gruppoChiuso(t(`Da verificare con l'ente (${ignoti.length})`, `To check with the body (${ignoti.length})`), ignoti));
    }
    // Chiusi da poco (decisione 72): solo vicini, fuori dai conteggi; di solito riaprono l'anno dopo.
    const chiusi = (ultimo.chiusi_di_recente || []).filter(r => posto(r, contesto) !== "lontano"
      && (!q || `${r.titolo} ${r.ente || ""}`.toLowerCase().includes(q)));
    if (!stato.filtro && chiusi.length) {
      figli.push(gruppoChiuso(t(`Chiusi da poco (${chiusi.length})`, `Recently closed (${chiusi.length})`), chiusi, true));
    }
    if (!stato.filtro && lontani.length) {
      figli.push(gruppoChiuso(t(`In altri comuni o regioni (${lontani.length})`, `In other municipalities or regions (${lontani.length})`), lontani));
    }
    if (!stato.filtro && tutteNo.length) {
      figli.push(gruppoChiuso(t(`Non compatibili (${tutteNo.length})`, `Not compatible (${tutteNo.length})`), tutteNo.sort(ordina)));
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
  const testo = giorni === 0 ? t("chiude oggi", "closes today") : giorni === 1 ? t("chiude domani", "closes tomorrow") : giorni <= 60 ? t(`chiude tra ${giorni} giorni`, `closes in ${giorni} days`)
    : `${t("chiude il", "closes on")} ${new Date(`${chiusura}T12:00:00`).toLocaleDateString(LOCALE, { day: "numeric", month: "short", year: "numeric" })}`;
  return el("span", { classe: `etichetta scade${giorni <= 7 ? " urgente" : ""}` }, icona("orologio"), testo);
}

function origine(r) {
  return null;  // la provenienza della regola resta nei dati, non nella pagina (decisione 110)
  return null;
}

function scheda(r, chiuso = false) {
  const data = r.chiusura ? new Date(`${r.chiusura}T12:00:00`).toLocaleDateString(LOCALE, { day: "numeric", month: "long", year: "numeric" }) : "";
  const info = chiuso
    ? { ...STATI[r.stato], classe: "st-chiuso", etichetta: t(`Chiuso il ${data}`, `Closed on ${data}`), icona: "calendario",
        spiega: t("Questa edizione è chiusa; di solito il bando riapre l'anno dopo. Requisiti dell'ultima edizione:", "This edition is closed; the call usually reopens the following year. Requirements of the last edition:") }
    : posto(r, contesto) === "ignoto"
      ? { ...STATI[r.stato], etichetta: t("Da verificare con l'ente", "To check with the body"), spiega: t("Il requisito che decide va verificato con l'ente:", "The deciding requirement must be checked with the body:") }
      : STATI[r.stato];
  const prima = stato.precedenti.get(r.id);
  const corpoDentro = el("div", { classe: "scheda-corpo-dentro" },
    (r.stato === "idoneo" ? r.requisiti : r.perche).length ? el("p", { classe: "spiega", testo: info.spiega }) : null,
    elencoRequisiti(r.stato === "idoneo" ? r.requisiti : r.perche),
    r.stato === "idoneo, salvo eccezioni" && r.requisiti.length
      ? el("details", {}, el("summary", { testo: t(`Tutti i requisiti (${r.requisiti.length})`, `All requirements (${r.requisiti.length})`) }), elencoRequisiti(r.requisiti)) : null,
    r.prossimo_passo ? el('p',{classe:'prossimo-passo',testo:r.prossimo_passo}) : null,
    r.link ? el("a", { classe: "pulsante secondario piccolo apri-fonte", href: r.link, target: "_blank", rel: "noopener" }, t("Apri il bando ufficiale ↗", "Open the official call (in Italian) ↗")) : null);
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
    v.risposta !== undefined ? el('p',{classe:'confronto',testo:t(`La tua risposta: ${v.risposta} · ${v.verificato === true ? 'requisito rispettato' : v.verificato === false ? 'requisito non rispettato' : 'da verificare'}`, `Your answer: ${v.risposta} · ${v.verificato === true ? 'requirement met' : v.verificato === false ? 'requirement not met' : 'to be checked'}`)}) : null,
    v.come_verificare ? el('p',{testo:v.come_verificare}) : null,
    v.figli ? elencoRequisiti(v.figli) : null,
    v.citazione ? el('blockquote',{testo:`«${v.citazione}»`}) : null,
    v.citazione && v.fonte && !/campo|revisione a mano|ente del bando/i.test(v.fonte) ? el('div',{classe:'da-dove',testo:fonte(v.fonte)}) : null)));
}

let ambitoStampa = 'principali';
function preparaReport() {
  document.getElementById('report-stampa')?.remove();
  if (!ultimo) return;
  const voci = ambitoStampa === 'tutto' ? [...ultimo.risultati,...(ultimo.chiusi_di_recente || [])]
    : ultimo.risultati.filter(r=>!r.gruppo && r.stato !== 'non idoneo');
  const report=el('section',{id:'report-stampa'},el('h1',{testo:t('MiSpetta · i tuoi risultati', 'MiSpetta · your results')}),
    el('p',{testo:t(`Risultati al ${ultimo.giorno}: ${voci.length} aiuti.`, `Results on ${ultimo.giorno}: ${voci.length} benefits.`)}),
    el('p',{testo:t('Prima di fare domanda controlla sempre il bando ufficiale: l\'esito non sostituisce la valutazione dell\'ente.', 'Before applying always check the official call: this result does not replace the body\'s assessment. Call titles and quotes are in the original Italian.')}),
    el('nav',{'aria-label':t('Indice delle misure nel report', 'Index of the benefits in the report')},el('h2',{testo:t('Indice delle misure', 'Index of benefits')}),
      el('ol',{},voci.map((r,i)=>el('li',{},el('a',{href:`#report-misura-${i}`,testo:`${r.titolo} · ${STATI[r.stato].etichetta}`}))))),
    el('h2',{testo:t('Risposte fornite', 'Answers given')}),el('dl',{},(ultimo.riepilogo || []).flatMap(r=>[el('dt',{testo:r.voce}),el('dd',{testo:r.valore})])),
    voci.map((r,i)=>el('article',{classe:'voce-report',id:`report-misura-${i}`},el('h2',{testo:r.titolo}),
      el('p',{testo:`${STATI[r.stato].etichetta}. ${r.ente || ''}`}),
      elencoRequisiti(r.requisiti),el('h3',{testo:t('Prossimo passo', 'Next step')}),
      [r.prossimo_passo].filter(Boolean).map(x=>el('p',{testo:x})),
      r.link ? el('p',{testo:t(`Bando ufficiale: ${r.link}`, `Official call: ${r.link}`)}) : null)));
  document.body.append(report);
}
window.addEventListener('beforeprint',preparaReport);
window.addEventListener('afterprint',()=>document.getElementById('report-stampa')?.remove());
export function stampaReport(ambito = 'principali') {ambitoStampa=ambito;preparaReport();window.print();}

function disegnaRiassuntoMobile(conteggi) {
  const b = document.getElementById("riassunto-mobile");
  const voci = ORDINE.filter(s => s !== "non idoneo" && conteggi[s]).slice(0, 3);
  const pillole = voci.map(s => el("span", { classe: `pillola ${STATI[s].classe}` }, el("b", { testo: String(conteggi[s]) }), ` ${STATI[s].tessera}`));
  b.replaceChildren(...(pillole.length ? pillole : [el("span", { testo: t("Vai ai risultati", "Go to results") })]));
}
