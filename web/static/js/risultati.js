// Risultati dal vivo: tessere per esito (anche filtri), schede che si riordinano con FLIP, citazioni e fonte.
import { el, icona } from "./dom.js";
import { conta, flip, apriChiudi } from "./animazioni.js";
import { t, LOCALE, temporale, fonte } from "./i18n.js";

// I sei esiti del motore (pipeline/motore.py) con nomi in linguaggio semplice.
export const STATI = {
  "idoneo": { classe: "st-idoneo", tessera: t("Compatibili", "Compatible"), etichetta: t("Requisiti controllati compatibili", "Checked requirements compatible"), icona: "spunta",
    spiega: t("Confronto dei requisiti rappresentati con le tue risposte; non garantisce assegnazione o pagamento:", "The modelled requirements compared with your answers; this does not guarantee an award or payment:") },
  "idoneo, salvo eccezioni": { classe: "st-salvo", tessera: t("Salvo casi particolari", "Barring special cases"), etichetta: t("Compatibile con riserve specifiche", "Compatible with specific caveats"), icona: "scudo",
    spiega: t("I controlli rappresentati sono compatibili. Verifica le riserve elencate:", "The modelled checks are compatible. Check the caveats listed:") },
  "quasi idoneo": { classe: "st-quasi", tessera: t("Manca un solo requisito", "One requirement missing"), etichetta: t("Ti manca un requisito", "You miss one requirement"), icona: "orologio",
    spiega: t("Questo requisito non è soddisfatto. Cambiarlo può richiedere una modifica sostanziale:", "This requirement is not met. Changing it may take a substantial change:") },
  "da verificare": { classe: "st-verificare", tessera: t("Possibili", "Possible"), etichetta: t("Possibile: da controllare", "Possible: to be checked"), icona: "lente",
    spiega: t("Nessun requisito che sappiamo controllare ti esclude. Resta da verificare sul bando:", "No requirement we can check rules you out. Still to check on the call:") },
  "mancano dati": { classe: "st-mancano", tessera: t("Servono risposte", "Answers needed"), etichetta: t("Serve un'altra risposta", "Another answer needed"), icona: "domanda",
    spiega: t("Per decidere ci serve sapere:", "To decide we need to know:") },
  "non idoneo": { classe: "st-no", tessera: t("Non compatibili", "Not compatible"), etichetta: t("Un requisito controllato non è soddisfatto", "A checked requirement is not met"), icona: "croce",
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
    if (!stato.filtro && date.length) figli.push(gruppoChiuso(t(`Disponibilità non verificata (${date.length}): controlla la finestra della tua edizione`, `Availability not verified (${date.length}): check the window of your edition`),date));
    if (!stato.filtro && futuri.length) figli.push(gruppoChiuso(t(`Aperture future documentate (${futuri.length})`, `Documented future openings (${futuri.length})`),futuri));
    if (!stato.filtro && ignoti.length) {
      figli.push(gruppoChiuso(t(`Non sappiamo dirlo (${ignoti.length}): il requisito decisivo non è tra quelli che sappiamo controllare`, `We can't tell (${ignoti.length}): the deciding requirement is not one we can check`), ignoti));
    }
    // Chiusi da poco (decisione 72): solo vicini, fuori dai conteggi; di solito riaprono l'anno dopo.
    const chiusi = (ultimo.chiusi_di_recente || []).filter(r => posto(r, contesto) !== "lontano"
      && (!q || `${r.titolo} ${r.ente || ""}`.toLowerCase().includes(q)));
    if (!stato.filtro && chiusi.length) {
      figli.push(gruppoChiuso(t(`Chiusi da poco (${chiusi.length}): nuove edizioni non verificate`, `Recently closed (${chiusi.length}): new editions not verified`), chiusi, true));
    }
    if (!stato.filtro && lontani.length) {
      figli.push(gruppoChiuso(t(`In altri comuni o regioni (${lontani.length}): provenienza dell’ente: pertinenza da verificare, non esclusione`, `In other municipalities or regions (${lontani.length}): based on where the body is; relevance to check, not an exclusion`), lontani));
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
  if (r.origine === "estratta") return el("span", { classe: "etichetta estratta", title: t("Requisiti letti da un modello linguistico e non ancora rivisti da noi", "Requirements read by a language model and not yet reviewed by us"), testo: t("estratta automaticamente", "extracted automatically") });
  if (r.origine === "riferimento") return el("span", { classe: "etichetta rivista", testo: r.revisione_umana ? t("revisione umana documentata", "human review documented") : t("regola di riferimento · revisione non attestata", "reference rule · review not attested") });
  if (r.origine === "open data") return el("span", { classe: "etichetta", testo: "incentivi.gov.it" });
  return null;
}

function scheda(r, chiuso = false) {
  const data = r.chiusura ? new Date(`${r.chiusura}T12:00:00`).toLocaleDateString(LOCALE, { day: "numeric", month: "long", year: "numeric" }) : "";
  const info = chiuso
    ? { ...STATI[r.stato], classe: "st-chiuso", etichetta: t(`Chiuso il ${data}: nuove edizioni non verificate`, `Closed on ${data}: new editions not verified`), icona: "calendario",
        spiega: t("Questa edizione è archiviata. Non è verificata una nuova apertura. Requisiti della versione conservata:", "This edition is archived. A new opening is not verified. Requirements of the stored version:") }
    : posto(r, contesto) === "ignoto"
      ? { ...STATI[r.stato], etichetta: t("Non sappiamo dirlo", "We can't tell"), spiega: t("Il requisito che decide non è tra quelli che sappiamo controllare:", "The deciding requirement is not one we can check:") }
      : STATI[r.stato];
  const prima = stato.precedenti.get(r.id);
  const corpoDentro = el("div", { classe: "scheda-corpo-dentro" },
    (r.stato === "idoneo" ? r.requisiti : r.perche).length ? el("p", { classe: "spiega", testo: info.spiega }) : null,
    elencoRequisiti(r.stato === "idoneo" ? r.requisiti : r.perche),
    r.stato === "idoneo, salvo eccezioni" && r.requisiti.length
      ? el("details", {}, el("summary", { testo: t(`Tutti i requisiti (${r.requisiti.length})`, `All requirements (${r.requisiti.length})`) }), elencoRequisiti(r.requisiti)) : null,
    r.avvertenze?.length ? el('div',{classe:'limiti'},el('strong',{testo:t('Perimetro e limiti', 'Scope and limits')}),r.avvertenze.map(t=>el('p',{testo:t}))) : null,
    r.note?.length ? el('details',{},el('summary',{testo:t('Note della fonte e condizioni da approfondire', 'Source notes and conditions to look into (in Italian)')}),r.note.map(t=>el('p',{testo:t}))) : null,
    r.versioni_precedenti?.length ? el('p',{testo:`${t('Versioni conservate', 'Stored versions')}: ${r.versioni_precedenti.map(v=>v.id).join(', ')}`}) : null,
    el('p',{testo:t(`Disponibilità: ${r.stato_temporale}. Data di composizione/aggiornamento regola: ${r.aggiornamento_regola || 'non registrata'}; revisione umana: ${r.revisione_umana || 'non attestata'}.`, `Availability: ${temporale(r.stato_temporale)}. Rule written/updated on: ${r.aggiornamento_regola || 'not recorded'}; human review: ${r.revisione_umana || 'not attested'}.`)}),
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
    v.risposta !== undefined ? el('p',{classe:'confronto',testo:t(`La tua risposta: ${v.risposta}. Confronto: ${v.verificato === true ? 'soddisfatto' : v.verificato === false ? 'non soddisfatto' : 'non determinabile'}.`, `Your answer: ${v.risposta}. Result: ${v.verificato === true ? 'met' : v.verificato === false ? 'not met' : 'cannot be determined'}.`)}) : null,
    v.come_verificare ? el('p',{testo:v.come_verificare}) : null,
    v.figli ? elencoRequisiti(v.figli) : null,
    v.citazione ? el('blockquote',{testo:`«${v.citazione}»`}) : null,
    v.fonte ? el('div',{classe:'da-dove',testo:fonte(v.fonte)}) : null)));
}

let ambitoStampa = 'principali';
function preparaReport() {
  document.getElementById('report-stampa')?.remove();
  if (!ultimo) return;
  const voci = ambitoStampa === 'tutto' ? [...ultimo.risultati,...(ultimo.chiusi_di_recente || [])]
    : ultimo.risultati.filter(r=>!r.gruppo && r.stato !== 'non idoneo');
  const report=el('section',{id:'report-stampa'},el('h1',{testo:t('MiSpetta · report dei confronti', 'MiSpetta · comparison report')}),
    el('p',{testo:t(`Valutazione: ${ultimo.giorno}. Perimetro: ${ambitoStampa === 'tutto' ? 'intero catalogo valutato e archivio recente' : 'risultati principali non esclusi'}. ${voci.length} misure, senza paginazione o filtri di ricerca.`, `Assessed on: ${ultimo.giorno}. Scope: ${ambitoStampa === 'tutto' ? 'whole assessed catalogue and recent archive' : 'main results not excluded'}. ${voci.length} benefits, without paging or search filters.`)}),
    el('p',{testo:t('Compatibilità dei requisiti rappresentati, disponibilità della domanda, graduatoria e pagamento sono verifiche distinte. Le citazioni autentiche non certificano completezza o interpretazione delle regole.', 'Matching the modelled requirements, being able to apply, the ranking and payment are separate checks. Genuine quotes do not certify that the rules are complete or correctly read. Call titles, bodies and quotes are in the original Italian.')}),
    el('nav',{'aria-label':t('Indice delle misure nel report', 'Index of the benefits in the report')},el('h2',{testo:t('Indice delle misure', 'Index of benefits')}),
      el('ol',{},voci.map((r,i)=>el('li',{},el('a',{href:`#report-misura-${i}`,testo:`${r.titolo} · ${STATI[r.stato].etichetta} · ${temporale(r.stato_temporale)}`}))))),
    el('h2',{testo:t('Risposte fornite', 'Answers given')}),el('dl',{},(ultimo.riepilogo || []).flatMap(r=>[el('dt',{testo:r.voce}),el('dd',{testo:r.valore})])),
    voci.map((r,i)=>el('article',{classe:'voce-report',id:`report-misura-${i}`},el('h2',{testo:r.titolo}),
      el('p',{testo:`${STATI[r.stato].etichetta}. ${t('Disponibilità', 'Availability')}: ${temporale(r.stato_temporale)}. ${r.ente || ''}`}),
      elencoRequisiti(r.requisiti),el('h3',{testo:t('Limiti, note e prossimo passo', 'Limits, notes and next step')}),
      [...(r.avvertenze || []),...(r.note || []),r.prossimo_passo].filter(Boolean).map(t=>el('p',{testo:t})),
      el('p',{testo:t(`Fonte: ${r.link || 'non disponibile'}. Versione regola: ${r.versione_regola || 'non registrata'}. Revisione umana: ${r.revisione_umana || 'non attestata'}.`, `Source: ${r.link || 'not available'}. Rule version: ${r.versione_regola || 'not recorded'}. Human review: ${r.revisione_umana || 'not attested'}.`)}))));
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
