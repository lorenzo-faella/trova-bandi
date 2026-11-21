// Demo di trova-bandi (decisione 68). Il profilo vive solo in questa pagina: a ogni risposta lo si manda intero a
// /api/passo, che restituisce esiti aggiornati e prossima domanda. Nessun salvataggio, nemmeno nel browser.
import { el, icona, numeroIt, avviso } from "./dom.js";
import * as api from "./api.js";
import { conta, cambiaVista, coriandoli, osservaEntrate } from "./animazioni.js";
import { mostraDomanda, NON_SO } from "./domanda.js";
import { mostraRisultati, azzera, iniziaStrumenti, STATI, contaVisibili, stampaReport } from "./risultati.js";
import { aggiornaProfilo } from "./profilo.js";
import { scaricaIcs, scadenze } from "./calendario.js";

const stato = { ramo: null, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" };
let richiesta = 0, controller = null, occupato = false, modifica = null;
const $ = id => document.getElementById(id);

// ---------- pagina iniziale ----------
async function caricaNumeri() {
  const box = $("numeri");
  const voci = [
    ["persone", "aiuti per le persone: INPS, borse di studio, casa, comuni"],
    ["imprese_catalogo", "bandi imprese valutati · apertura da verificare nella scheda"],
    ["documenti", "documenti letti da regioni, comuni ed enti"],
    ["fonti", "enti pubblici monitorati"],
  ];
  try {
    const s = await api.statistiche();
    box.replaceChildren(...voci.filter(([k]) => s[k] !== null && s[k] !== undefined).map(([k, testo]) => {
      const v = el("span", { classe: "numero-valore", testo: "0" });
      setTimeout(() => conta(v, s[k], 1400), 250);
      return el("div", { classe: "numero" }, v, el("div", { classe: "numero-etichetta", testo: testo }));
    }));
  } catch { box.hidden = true; }
}

async function caricaProfili() {
  const box = $("profili");
  try {
    const profili = await api.profili();
    box.replaceChildren(...profili.map(p => el("button", { classe: "profilo", type: "button", title: p.descrizione,
      onclick: () => provaProfilo(p) }, el("span", { classe: "profilo-icona" }, icona(p.icona)), p.nome)));
  } catch { box.closest(".profili").hidden = true; }
}

function mostraHome() {
  cambiaVista(() => {
    $("percorso").hidden = true;
    $("home").hidden = false;
    $("ricomincia").hidden = true;
    $("link-come").hidden = false;
  }).then(() => window.scrollTo({ top: 0 }));
}

function entraNelPercorso() {
  return cambiaVista(() => {
    $("home").hidden = true;
    $("percorso").hidden = false;
    $("ricomincia").hidden = false;
    $("link-come").hidden = true;
    window.scrollTo({ top: 0 });
  });
}

function inizia(ramo) {
  controller?.abort(); richiesta++; occupato = false; modifica = null;
  Object.assign(stato, { ramo, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" });
  azzera();
  $("esempio").hidden = true;
  $("avviso-isee").hidden = true;
  $("domanda").replaceChildren();
  entraNelPercorso();
  avanza();
}

function provaProfilo(p) {
  controller?.abort(); richiesta++; occupato = false; modifica = null;
  Object.assign(stato, { ramo: "persone", profilo: structuredClone(p.profilo), storia: [], ultimo: null, esempio: p, finito: false, verso: "avanti" });
  azzera();
  $("domanda").replaceChildren();
  $("avviso-isee").hidden = true;
  const box = $("esempio");
  box.replaceChildren(el("span", { classe: "profilo-icona" }, icona(p.icona)),
    el("span", {}, "Profilo di esempio: ", el("strong", { testo: p.nome }), ` · ${p.descrizione}. `,
      el("button", { classe: "link-indietro", type: "button", testo: "Rispondi tu", onclick: () => inizia("persone") })));
  box.hidden = false;
  entraNelPercorso();
  avanza();
}

// ---------- percorso ----------
// Le regioni "vicine" alla persona: residenza, domicilio (se diverso) e università.
function contesto() {
  // il server le calcola dal profilo completo: la regione dell'università si ricava dal comune della sede
  return { ramo: stato.ramo, regioni: stato.ultimo?.regioni_vicine || [] };
}

// Le risposte date: chiuse sullo schermo, sempre stampate nel report.
function mostraRiepilogo(righe) {
  const box = $("riepilogo");
  if (!righe || !righe.length) { box.hidden = true; return; }
  const aperto = box.open;
  box.replaceChildren(el("summary", { testo: `Le tue risposte (${righe.length})` }),
    el("dl", { classe: "riepilogo-lista" }, righe.flatMap(r => [el("dt", { testo: r.voce }), el("dd", {}, r.valore, r.campo ? el("button", {type:"button", classe:"link-indietro no-stampa", testo:" · Modifica", onclick:()=>modificaCampo(r.campo)}) : null,
      (r.campi_modifica || []).map(c=>el('button',{type:'button',classe:'link-indietro no-stampa',testo:` · Modifica ${c.etichetta}`,onclick:()=>modificaCampo(c.campo)})))])));
  box.open = aperto;
  box.hidden = false;
}
window.addEventListener("beforeprint", () => { $("riepilogo").open = true; });
function blocca(v) {
  occupato = v;
  $("domanda").setAttribute("aria-busy", String(v));
  $("domanda").querySelectorAll("button").forEach(b => { if (v) {b.dataset.eraDisabilitato=String(b.disabled); b.disabled=true;} else if ('eraDisabilitato' in b.dataset) {b.disabled=b.dataset.eraDisabilitato==='true';delete b.dataset.eraDisabilitato;} });
}
async function avanza(profilo = stato.profilo, registra = null) {
  controller?.abort(); controller = new AbortController();
  const token = ++richiesta;
  blocca(true);
  try {
    const dati = await api.passo(stato.ramo, profilo, modifica, controller.signal);
    if (token !== richiesta) return;
    if (registra) stato.storia.push(registra);
    stato.profilo = profilo;
    stato.ultimo = dati;
    mostraRisultati(dati, contesto());
    mostraRiepilogo(dati.riepilogo);
    aggiornaAvanzamento(dati);
    mostraAvvisoIsee(dati.isee);
    if (dati.domanda) {
      stato.finito = false;
      mostraDomanda($("domanda"), dati.domanda, {
        rispondi, indietro, profilo:stato.profilo, puoTornare: stato.storia.length > 0, giorno: dati.giorno, verso: stato.verso,
      });
    } else mostraFine(dati);
    modifica = null;
  } catch (e) {
    if (e.name === 'AbortError' || token !== richiesta) return;
    $("domanda").querySelector('.errore-server')?.remove();
    const errore = el('div', {classe:'errore-server', role:'alert', tabindex:'-1'},
      el('p', {classe:'errore', testo:`Invio non riuscito: ${e.message}. Le risposte e i controlli sono conservati: puoi correggere e premere Avanti.`}),
      el('button', {type:'button',classe:'pulsante secondario',testo:'Riprova invio',onclick:()=>avanza(profilo,registra)}));
    $("domanda").append(errore); errore.focus({preventScroll:true});
  } finally { if (token === richiesta) blocca(false); }
}

function rispondi(scrivi) {
  if (occupato) return;
  const candidato = aggiornaProfilo(stato.profilo, scrivi, stato.ultimo?.dipendenze || {});
  stato.verso = "avanti";
  avanza(candidato, stato.ultimo?.domanda?.campo || null);
}
function modificaCampo(campo) {
  if (occupato) return;
  modifica = ['residente_italia','regione','comune','sempre_in_italia','anni_residenza_continuativa_italia'].includes(campo)?'residenza'
    : ['domicilio_diverso','regione_domicilio','comune_domicilio'].includes(campo)?'domicilio':campo;
  avanza();
  $("domanda").scrollIntoView({behavior:'auto',block:'start'});
}
function indietro() {
  if (!stato.storia.length || occupato) return;
  stato.verso = 'indietro';
  modificaCampo(stato.storia.pop());
}

function aggiornaAvanzamento(dati) {
  const tot = dati.risultati.length || 1;
  const decisi = ['idoneo','non idoneo','quasi idoneo'].reduce((n,s)=>n+(dati.conteggi[s]||0),0);
  const n = stato.storia.length;
  $("avanz-etichetta").textContent = dati.domanda ? `Domanda ${n + 1}` : `${n} ${n === 1 ? "risposta" : "risposte"}`;
  $("avanz-decisi").textContent = `${numeroIt(decisi)} confronti determinati · ${numeroIt(tot-decisi)} con riserve o dati mancanti`;
  $("avanz-riempi").style.width = dati.domanda ? '0%' : '100%';
  $("avanz-riempi").parentElement.setAttribute('aria-label', dati.domanda ? 'Questionario in corso; la durata dipende dalle risposte' : 'Domande terminate; restano le incertezze indicate');
}

function mostraAvvisoIsee(isee) {
  const box = $("avviso-isee");
  if (!isee) { box.hidden = true; return; }
  const giaVisto = !box.hidden;
  box.replaceChildren(el("span", { classe: "icona-avviso" }, icona("avviso")),
    el("div", {},
      el("p", {}, el("strong", { testo: `Il tuo ISEE decide ${isee.decide} ${isee.decide === 1 ? "beneficio" : "benefici"}` }),
        " ancora in sospeso. Puoi ottenerlo gratis con la DSU precompilata dell'INPS, accedendo con SPID o CIE."),
      el("p", {}, el("a", { href: isee.link, target: "_blank", rel: "noopener", testo: "Come ottenere l'ISEE (INPS) ↗" }), " · ",
        el("button", { classe: "link-indietro", type: "button", testo: "Ho il mio ISEE: inseriscilo",
          onclick: () => modificaCampo('isee') }))));
  box.hidden = false;
  if (giaVisto) box.style.animation = "none";
  else box.style.animation = "";
}

function mostraFine(dati) {
  const ctx = contesto();
  const { conteggi: c, lontani, ignoti } = contaVisibili(dati.risultati, ctx);
  const chiusiVicini = (dati.chiusi_di_recente || []).filter(r => !r.regione || ctx.regioni.includes(r.regione) || !ctx.regioni.length).length;
  const spettano = (c["idoneo"] || 0) + (c["idoneo, salvo eccezioni"] || 0);
  const possibili = c["da verificare"] || 0;
  const quasi = c["quasi idoneo"] || 0;
  const sospesi = c["mancano dati"] || 0;
  const selezionabili = scadenze(dati.risultati, dati.giorno);
  const selezione = new Set();
  const calendario = el('fieldset', {classe:'scelta-calendario'}, el('legend', {testo:'Scegli le scadenze da esportare (nessuna preselezionata)'}),
    el('p',{testo:'Eventi giornalieri: l’orario di chiusura non è verificato. Promemoria tre giorni prima.'}),
    selezionabili.map(r=>el('label', {},el('input', {type:'checkbox',value:r.id,onchange:e=>{if(e.target.checked)selezione.add(r.id);else selezione.delete(r.id); esporta.disabled=!selezione.size;esporta.textContent=`Scarica ${selezione.size} scadenze selezionate`;} }),` ${r.titolo} · ${r.chiusura}`)));
  const esporta = el('button',{type:'button',classe:'pulsante primario',disabled:true,testo:'Seleziona le scadenze da esportare',onclick:()=>{
    const n=scaricaIcs(dati.risultati.filter(r=>selezione.has(r.id)),dati.giorno);avviso(`Scaricate ${n} scadenze selezionate`);
  }});
  const daSegnare = selezionabili.length;
  const titolo = spettano ? `${spettano} ${spettano === 1 ? "misura compatibile" : "misure compatibili"} con i requisiti controllati`
    : possibili ? `${possibili} ${possibili === 1 ? "aiuto possibile" : "aiuti possibili"} per te`
    : "Abbiamo finito";
  const box = $("domanda");
  const pillole = ["idoneo", "idoneo, salvo eccezioni", "da verificare", "quasi idoneo", "mancano dati"]
    .filter(s => c[s]).map(s => el("span", { classe: `pillola ${STATI[s].classe}` }, el("b", { testo: String(c[s]) }), ` ${STATI[s].tessera}`));
  const ambitoReport=el('select',{'aria-label':'Perimetro del report stampato'},el('option',{value:'principali',testo:'Report: risultati principali non esclusi'}),el('option',{value:'tutto',testo:'Report: tutto il catalogo e archivio recente'}));
  const nodo = el("div", { classe: "domanda fine" },
    el("div", { classe: "fine-icona" }, icona("spunta", { spessore: "3" })),
    el("h2", { testo: titolo, tabindex: "-1", id: "testo-domanda" }),
    el("p", { testo: possibili && !spettano
      ? "Nessun requisito che sappiamo controllare ti esclude: apri ogni bando \"possibile\" per vedere cosa resta da verificare."
      : sospesi ? `Le domande sono finite, ma ${sospesi === 1 ? "1 bando resta" : `${sospesi} bandi restano`} in sospeso: dipendono da risposte date con "Non lo so". Con quei dati (per esempio l'ISEE) si possono decidere.`
      : "Domande terminate. Consulta le riserve nelle schede: compatibilità dei requisiti, presentazione della domanda e assegnazione sono verifiche distinte." }),
    el("div", { classe: "fine-riassunto" }, pillole),
    lontani || ignoti || chiusiVicini ? el("p", { classe: "domanda-aiuto", testo: [
      ignoti ? `${ignoti} ${ignoti === 1 ? "bando" : "bandi"} dove non sappiamo dirlo` : null,
      lontani ? `${lontani} di altre regioni` : null,
      chiusiVicini ? `${chiusiVicini} archiviati: nuove edizioni non verificate` : null].filter(Boolean).join(" · ") + ": sono in fondo alla lista." }) : null,
    el("div", { classe: "fine-azioni" },
      daSegnare ? el('div',{},calendario,esporta) : el('p',{testo:'Nessuna scadenza verificata esportabile con i fatti e il territorio indicati.'}),
      ambitoReport,
      el("button", { classe: "pulsante secondario", type: "button", onclick: () => stampaReport(ambitoReport.value) }, icona("stampa"), "Stampa report completo del catalogo valutato"),
      el("div", { classe: "azioni-domanda" },
        el("button", { classe: "link-indietro", type: "button", testo: "← Cambia l'ultima risposta", disabled: !stato.storia.length, onclick: indietro }),
        el("span", { classe: "spazio" }),
        el("button", { classe: "link-indietro", type: "button", testo: "Ricomincia", onclick: () => inizia(stato.ramo) }))));
  box.replaceChildren(nodo);
  nodo.querySelector("#testo-domanda").focus({ preventScroll: true });

  stato.finito = true;
}

// ---------- avvio ----------
document.querySelectorAll(".ramo").forEach(b => {
  b.querySelector(".ramo-icona").append(icona(b.dataset.ramo === "persone" ? "persona" : "impresa"));
  b.addEventListener("click", () => inizia(b.dataset.ramo));
  b.addEventListener("pointermove", e => {
    const r = b.getBoundingClientRect();
    b.style.setProperty("--mx", `${e.clientX - r.left}px`);
    b.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
});
$("vai-home").addEventListener("click", mostraHome);
$("ricomincia").addEventListener("click", () => inizia(stato.ramo || "persone"));
$("link-come").addEventListener("click", e => {
  if (!$("home").hidden) return;
  e.preventDefault();
  mostraHome();
});
$("riassunto-mobile").addEventListener("click", () => $("risultati").scrollIntoView({ behavior: "smooth" }));
iniziaStrumenti();
caricaNumeri();
caricaProfili();
osservaEntrate();
