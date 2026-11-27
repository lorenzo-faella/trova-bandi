// Demo di MiSpetta (decisioni 68 e 105). Il profilo vive solo in questa pagina: a ogni risposta lo si manda intero a
// /api/passo, che restituisce esiti aggiornati e prossima domanda. Nessun salvataggio, nemmeno nel browser.
import { el, icona, numeroIt, avviso } from "./dom.js";
import * as api from "./api.js";
import { conta, cambiaVista, osservaEntrate } from "./animazioni.js";
import { mostraDomanda, NON_SO } from "./domanda.js";
import { mostraRisultati, azzera, iniziaStrumenti, STATI, contaVisibili, stampaReport } from "./risultati.js";
import { aggiornaProfilo } from "./profilo.js";
import { scaricaIcs, scadenze } from "./calendario.js";
import { scriviRisposta, testoRisposta } from "./guida.js";
import { disegnaPercorsi } from "./percorsi.js";
import { t, EN, LOCALE, cambiaLingua, traduciPagina } from "./i18n.js";

const stato = { ramo: null, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" };
let richiesta = 0, controller = null, occupato = false, modifica = null, ultimaDomanda = undefined;
// Una domanda nuova (o la pagina finale) si legge dall'inizio: la colonna di sinistra scorre da sola (stile.css).
function inCimaSeNuova(dati) {
  const chiave = dati.domanda ? dati.domanda.campo : guida.attiva && !guida.finale ? "verifiche" : "fine";
  if (chiave !== ultimaDomanda) document.querySelector(".colonna-domanda").scrollTop = 0;
  ultimaDomanda = chiave;
}
// Percorso guidato dei profili d'esempio (decisione 104): una domanda alla volta, con la risposta del profilo.
const guida = { attiva: false, obiettivo: null, nome: "", timer: null, pausa: false, finale: false };
const RITMO = 2600; // millisecondi per passo: il tempo di leggere domanda e risposta
const $ = id => document.getElementById(id);

// ---------- pagina iniziale ----------
async function caricaNumeri() {
  const box = $("numeri");
  const voci = [
    ["persone", t("aiuti per le persone: INPS, borse di studio, casa, comuni", "benefits for people: INPS, scholarships, housing, municipalities")],
    ["imprese_catalogo", t("bandi per le imprese", "calls for businesses")],
    ["documenti", t("documenti letti da regioni, comuni ed enti", "documents read from regions, municipalities and agencies")],
    ["fonti", t("enti pubblici monitorati", "public bodies monitored")],
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

const NOMI_RAMI = { persone: t("Persone", "People"), imprese: t("Imprese", "Businesses") };
// [ramo, elementi] nell'ordine del file: prima le persone, poi le imprese (decisione 106)
function gruppi(voci, ramo) {
  const per = new Map();
  for (const v of voci) { const r = ramo(v) || "persone"; if (!per.has(r)) per.set(r, []); per.get(r).push(v); }
  return [...per];
}

// Confronto dei profili (decisione 104): stesse domande, storie diverse. Ogni carta apre il suo profilo.
function mostraConfronto(voci, profili) {
  const perId = Object.fromEntries(profili.map(p => [p.id, p]));
  const carta = v => el("article", { classe: "confronto-carta" },
    el("div", { classe: "confronto-testa" },
      el("span", { classe: "confronto-icona" }, icona(v.icona)),
      el("div", {}, el("h3", { testo: v.nome }), el("p", { classe: "confronto-descr", testo: v.descrizione }))),
    el("div", { classe: "confronto-numeri" },
      el("span", { classe: "confronto-num st-idoneo" }, el("b", { testo: String(v.spettano) }), v.spettano === 1 ? t(" compatibile", " compatible") : t(" compatibili", " compatible")),
      el("span", { classe: "confronto-num st-verificare" }, el("b", { testo: String(v.possibili) }), v.possibili === 1 ? t(" possibile", " possible") : t(" possibili", " possible"))),
    el("ul", { classe: "confronto-esempi" }, v.titoli.map(x => el("li", { testo: x, title: x }))),
    el("button", { classe: "pulsante secondario confronto-apri", type: "button", onclick: () => provaProfilo(perId[v.id]) },
      v.ramo === "imprese" ? t("Apri l'impresa", "Open the business") : t("Apri questo profilo", "Open this profile")));
  // persone e imprese in due gruppi con un titolo, così le carte non si mescolano
  $("confronto").replaceChildren(...gruppi(voci.filter(v => perId[v.id]), v => v.ramo).flatMap(([ramo, del_ramo]) =>
    [el("h3", { classe: "confronto-gruppo", testo: NOMI_RAMI[ramo] }), ...del_ramo.map(carta)]));
  $("sezione-confronto").hidden = false;
}

async function caricaProfili() {
  const box = $("profili");
  try {
    const profili = await api.profili();
    api.confronto().then(voci => {
      mostraConfronto(voci, profili);
      // il grafico dei percorsi va disegnato con la sezione già visibile (servono le misure del testo)
      return api.percorsi().then(dati => {
        const box = $("percorsi");
        box.hidden = false;
        const perId = Object.fromEntries(profili.map(p => [p.id, p]));
        disegnaPercorsi(box, dati, id => perId[id] && provaProfilo(perId[id]));
      });
    }).catch(() => {});
    box.replaceChildren(...gruppi(profili, p => p.ramo || "persone").map(([ramo, del_ramo]) => el("div", { classe: "profili-gruppo" },
      el("span", { classe: "profili-etichetta", testo: NOMI_RAMI[ramo] }),
      del_ramo.map(p => el("button", { classe: "profilo", type: "button", title: p.descrizione,
        onclick: () => provaProfilo(p) }, el("span", { classe: "profilo-icona" }, icona(p.icona)), p.nome)))));
  } catch { box.closest(".profili").hidden = true; }
}

function mostraHome() {
  spegniGuida();
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
  spegniGuida();
  controller?.abort(); richiesta++; occupato = false; modifica = null; ultimaDomanda = undefined;
  Object.assign(stato, { ramo, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" });
  azzera();
  $("esempio").hidden = true;
  $("avviso-isee").hidden = true;
  $("domanda").replaceChildren();
  entraNelPercorso();
  avanza();
}

function provaProfilo(p) {
  controller?.abort(); richiesta++; occupato = false; modifica = null; ultimaDomanda = undefined;
  // si parte vuoti e si ripercorre il questionario con le risposte del profilo, una alla volta
  spegniGuida();
  Object.assign(guida, { attiva: true, obiettivo: structuredClone(p.profilo), nome: p.nome, pausa: false, finale: false });
  Object.assign(stato, { ramo: p.ramo || "persone", profilo: {}, storia: [], ultimo: null, esempio: p, finito: false, verso: "avanti" });
  azzera();
  $("domanda").replaceChildren();
  $("avviso-isee").hidden = true;
  const box = $("esempio");
  box.replaceChildren(el("span", { classe: "profilo-icona" }, icona(p.icona)),
    el("span", {}, t("Profilo di esempio: ", "Example profile: "), el("strong", { testo: p.nome }), ` · ${p.descrizione}. `,
      el("button", { classe: "link-indietro", type: "button", testo: t("Rispondi tu", "Answer yourself"), onclick: () => inizia(p.ramo || "persone") })));
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
  box.replaceChildren(el("summary", { testo: t(`Le tue risposte (${righe.length})`, `Your answers (${righe.length})`) }),
    el("dl", { classe: "riepilogo-lista" }, righe.flatMap(r => [el("dt", { testo: r.voce }), el("dd", {}, r.valore, r.campo ? el("button", {type:"button", classe:"link-indietro no-stampa", testo:t(" · Modifica", " · Edit"), onclick:()=>modificaCampo(r.campo)}) : null,
      (r.campi_modifica || []).map(c=>el('button',{type:'button',classe:'link-indietro no-stampa',testo:t(` · Modifica ${c.etichetta}`, ` · Edit ${c.etichetta}`),onclick:()=>modificaCampo(c.campo)})))])));
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
    if (dati.domanda && guida.attiva) {
      stato.finito = false;
      mostraPassoGuidato(dati);
    } else if (dati.domanda) {
      stato.finito = false;
      mostraDomanda($("domanda"), dati.domanda, {
        rispondi, indietro, profilo:stato.profilo, puoTornare: stato.storia.length > 0, giorno: dati.giorno, verso: stato.verso,
      });
    } else if (guida.attiva && !guida.finale) mostraUltimoPassoGuidato(dati);
    else { spegniGuida(); mostraFine(dati); }
    inCimaSeNuova(dati);
    modifica = null;
  } catch (e) {
    if (e.name === 'AbortError' || token !== richiesta) return;
    $("domanda").querySelector('.errore-server')?.remove();
    const errore = el('div', {classe:'errore-server', role:'alert', tabindex:'-1'},
      el('p', {classe:'errore', testo:t(`Invio non riuscito: ${e.message}. Le risposte e i controlli sono conservati: puoi correggere e premere Avanti.`, `Sending failed: ${e.message}. Your answers and checks are kept: you can correct them and press Next.`)}),
      el('button', {type:'button',classe:'pulsante secondario',testo:t('Riprova invio', 'Retry'),onclick:()=>avanza(profilo,registra)}));
    $("domanda").append(errore); errore.focus({preventScroll:true});
  } finally { if (token === richiesta) blocca(false); }
}

// ---------- percorso guidato ----------
function fermaTimer() { clearTimeout(guida.timer); guida.timer = null; }
function spegniGuida() { fermaTimer(); Object.assign(guida, { attiva: false, obiettivo: null, finale: false }); }

function barraGuida(passo, risposta, avanti) {
  const pulsantePausa = el("button", { type: "button", classe: "pulsante secondario guida-pausa" });
  const barra = el("div", { classe: "guida-avanzamento" }, el("span"));
  const disegna = () => {
    pulsantePausa.textContent = guida.pausa ? t("▶ Riprendi", "▶ Resume") : t("❚❚ Pausa", "❚❚ Pause");
    barra.classList.toggle("in-corso", !guida.pausa);
  };
  pulsantePausa.addEventListener("click", () => {
    guida.pausa = !guida.pausa;
    if (guida.pausa) fermaTimer(); else guida.timer = setTimeout(avanti, RITMO);
    disegna();
  });
  disegna();
  barra.style.setProperty("--ritmo", `${RITMO}ms`);
  return el("div", { classe: "guida", role: "status" },
    el("div", { classe: "guida-testa" },
      el("span", { classe: "guida-etichetta" }, t("Percorso guidato · ", "Guided path · "), el("strong", { testo: guida.nome })),
      el("span", { classe: "guida-passo", testo: passo })),
    el("p", { classe: "guida-risposta" }, t("Risposta: ", "Answer: "), el("strong", { testo: risposta })),
    barra,
    el("div", { classe: "guida-azioni" }, pulsantePausa,
      el("button", { type: "button", classe: "pulsante primario", testo: t("Avanti →", "Next →"), onclick: () => { fermaTimer(); avanti(); } }),
      el("button", { type: "button", classe: "link-indietro", testo: t("Vai alla fine", "Skip to the end"), onclick: vaiAllaFine })));
}

function vaiAllaFine() {
  fermaTimer();
  guida.finale = true;
  avanza(structuredClone(guida.obiettivo));
}

// Una domanda del questionario con la risposta del profilo già scelta. Se chi guarda risponde da sé, la guida si
// mette in pausa e la sua risposta vale; "Indietro" la spegne.
function mostraPassoGuidato(dati) {
  const d = dati.domanda;
  const scrivi = scriviRisposta(d, guida.obiettivo);
  const anteprima = aggiornaProfilo(stato.profilo, scrivi, dati.dipendenze || {});
  const avanti = () => { fermaTimer(); if (!occupato) rispondi(scrivi); };
  mostraDomanda($("domanda"), d, {
    rispondi: s => { guida.pausa = true; fermaTimer(); rispondi(s); },
    indietro: () => { spegniGuida(); indietro(); },
    profilo: anteprima, puoTornare: stato.storia.length > 0, giorno: dati.giorno, verso: stato.verso,
  });
  $("domanda").firstElementChild?.prepend(barraGuida(t(`Domanda ${stato.storia.length + 1}`, `Question ${stato.storia.length + 1}`), testoRisposta(d, stato.profilo, anteprima), avanti));
  if (!guida.pausa) guida.timer = setTimeout(avanti, RITMO);
}

// Finite le domande: le risposte del profilo alle verifiche finali, poi il profilo completo e la pagina finale.
function mostraUltimoPassoGuidato(dati) {
  const conferme = guida.obiettivo.conferme || {};
  const voci = (dati.verifiche || []).flatMap(v => v.domande.filter(q => q.chiave in conferme)
    .map(q => ({ titolo: v.titolo, testo: q.testo, si: conferme[q.chiave] })));
  if (!voci.length) { vaiAllaFine(); return; }
  const nodo = el("div", { classe: "domanda" },
    el("h2", { classe: "domanda-testo", id: "testo-domanda", tabindex: "-1", testo: t("Ultimo passo: le verifiche finali", "Last step: the final checks") }),
    el("p", { classe: "domanda-aiuto", testo: t("Alcuni aiuti dipendono da condizioni che il questionario non chiede a tutti. Il profilo risponde con i dati della sua storia:", "Some benefits depend on conditions the questionnaire doesn't ask everyone. The profile answers with the facts of its story:") }),
    el("ul", { classe: "guida-verifiche" }, voci.map(v => el("li", { title: v.testo },
      el("span", { classe: v.si ? "guida-si" : "guida-no", testo: v.si ? t("Sì", "Yes") : "No" }), ` ${v.titolo}`))));
  $("domanda").replaceChildren(nodo);
  nodo.prepend(barraGuida(t("Verifiche finali", "Final checks"), `${voci.length} ${voci.length === 1 ? t("risposta", "answer") : t("risposte", "answers")}`, vaiAllaFine));
  if (!guida.pausa) guida.timer = setTimeout(vaiAllaFine, RITMO * 1.5);
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
  $("avanz-etichetta").textContent = dati.domanda ? t(`Domanda ${n + 1}`, `Question ${n + 1}`)
    : n ? `${n} ${n === 1 ? t("risposta", "answer") : t("risposte", "answers")}` : t("Domande completate", "Questions completed");
  $("avanz-decisi").textContent = t(`${numeroIt(tot)} aiuti valutati`, `${numeroIt(tot)} benefits assessed`);
  $("avanz-riempi").style.width = dati.domanda ? '0%' : '100%';
  $("avanz-riempi").parentElement.setAttribute('aria-label', dati.domanda ? t('Questionario in corso; la durata dipende dalle risposte', 'Questionnaire in progress; its length depends on your answers') : t('Domande terminate; restano le incertezze indicate', 'Questions finished; the uncertainties shown remain'));
}

function mostraAvvisoIsee(isee) {
  const box = $("avviso-isee");
  if (!isee) { box.hidden = true; return; }
  const giaVisto = !box.hidden;
  box.replaceChildren(el("span", { classe: "icona-avviso" }, icona("avviso")),
    el("div", {},
      el("p", {}, el("strong", { testo: t(`Il tuo ISEE decide ${isee.decide} ${isee.decide === 1 ? "beneficio" : "benefici"}`, `Your ISEE decides ${isee.decide} ${isee.decide === 1 ? "benefit" : "benefits"}`) }),
        t(" ancora in sospeso. Puoi ottenerlo gratis con la DSU precompilata dell'INPS, accedendo con SPID o CIE.", " still pending. You can get it for free with the INPS pre-filled DSU form, logging in with SPID or CIE (Italian digital ID).")),
      el("p", {}, el("a", { href: isee.link, target: "_blank", rel: "noopener", testo: t("Come ottenere l'ISEE (INPS) ↗", "How to get your ISEE (INPS, in Italian) ↗") }), " · ",
        el("button", { classe: "link-indietro", type: "button", testo: t("Ho il mio ISEE: inseriscilo", "I have my ISEE: enter it"),
          onclick: () => modificaCampo('isee') }))));
  box.hidden = false;
  if (giaVisto) box.style.animation = "none";
  else box.style.animation = "";
}

// "Sono possibili questi": per gli aiuti a cui mancano 1-2 condizioni, una domanda sì/no per ciascuna. Sì a tutte porta
// l'aiuto fra quelli che ti spettano, un no lo esclude (decisione 93).
function sezioneVerifiche(verifiche) {
  if (!verifiche.length) return null;
  const date = stato.profilo.conferme || {};
  const rispondiVerifica = (chiave, valore) => rispondi(p => { p.conferme = { ...(p.conferme || {}), [chiave]: valore }; });
  return el("section", { classe: "verifiche" },
    el("h3", { testo: t("Sono possibili questi: verifica se ti spettano", "These are possible: check whether you qualify") }),
    el("p", { classe: "domanda-aiuto", testo: t("Rispondi solo per gli aiuti che ti interessano. Con un sì a tutte le domande di un aiuto, risulta fra quelli che ti spettano; con un no, è escluso.", "Answer only for the benefits you care about. With a yes to all of a benefit's questions it moves to the ones you qualify for; with a no it is excluded.") }),
    verifiche.map(v => el("div", { classe: "verifica" },
      el("h4", { testo: v.titolo }),
      v.ente ? el("p", { classe: "verifica-ente", testo: v.ente }) : null,
      v.domande.map(q => el("div", { classe: "riga-persona componente" },
        el("span", { classe: "chi", testo: q.testo }),
        el("div", { classe: "segmenti", role: "group", "aria-label": q.testo },
          [[t("Sì", "Yes"), true], ["No", false], [t("Non lo so", "I don't know"), NON_SO]].map(([etichetta, valore]) =>
            el("button", { classe: "segmento", type: "button", "aria-pressed": String(date[q.chiave] === valore), testo: etichetta,
              onclick: () => rispondiVerifica(q.chiave, valore) }))),
        q.citazione ? el("p", { classe: "verifica-citazione", testo: `«${q.citazione}»` }) : null)))));
}

function mostraFine(dati) {
  const ctx = contesto();
  const { conteggi: c, lontani, ignoti } = contaVisibili(dati.risultati, ctx);
  const chiusiVicini = (dati.chiusi_di_recente || []).filter(r => r.gruppo !== "lontano").length;
  const spettano = (c["idoneo"] || 0) + (c["idoneo, salvo eccezioni"] || 0);
  const possibili = c["da verificare"] || 0;
  const quasi = c["quasi idoneo"] || 0;
  const sospesi = c["mancano dati"] || 0;
  const selezionabili = scadenze(dati.risultati, dati.giorno);
  const selezione = new Set();
  const calendario = el('fieldset', {classe:'scelta-calendario'}, el('legend', {testo:t('Scegli le scadenze da esportare (nessuna preselezionata)', 'Choose the deadlines to export (none preselected)')}),
    el('p',{testo:t('Promemoria tre giorni prima della scadenza.', 'Reminder three days before the deadline.')}),
    selezionabili.map(r=>el('label', {},el('input', {type:'checkbox',value:r.id,onchange:e=>{if(e.target.checked)selezione.add(r.id);else selezione.delete(r.id); esporta.disabled=!selezione.size;esporta.textContent=t(`Scarica ${selezione.size} scadenze selezionate`, `Download ${selezione.size} selected deadlines`);} }),` ${r.titolo} · ${new Date(r.chiusura + 'T12:00').toLocaleDateString(LOCALE)}`)));
  const esporta = el('button',{type:'button',classe:'pulsante primario',disabled:true,testo:t('Seleziona le scadenze da esportare', 'Select the deadlines to export'),onclick:()=>{
    const n=scaricaIcs(dati.risultati.filter(r=>selezione.has(r.id)),dati.giorno);avviso(t(`Scaricate ${n} scadenze selezionate`, `Downloaded ${n} selected deadlines`));
  }});
  const daSegnare = selezionabili.length;
  const titolo = spettano ? t(`${spettano} ${spettano === 1 ? "aiuto compatibile" : "aiuti compatibili"} con il tuo profilo`, `${spettano} ${spettano === 1 ? "benefit" : "benefits"} compatible with your profile`)
    : possibili ? t(`${possibili} ${possibili === 1 ? "aiuto possibile" : "aiuti possibili"} per te`, `${possibili} possible ${possibili === 1 ? "benefit" : "benefits"} for you`)
    : t("Abbiamo finito", "All done");
  const box = $("domanda");
  const pillole = ["idoneo", "idoneo, salvo eccezioni", "da verificare", "quasi idoneo", "mancano dati"]
    .filter(s => c[s]).map(s => el("span", { classe: `pillola ${STATI[s].classe}` }, el("b", { testo: String(c[s]) }), ` ${STATI[s].tessera}`));
  const ambitoReport=el('select',{'aria-label':t('Cosa stampare', 'What to print')},el('option',{value:'principali',testo:t('Stampa: i tuoi risultati', 'Print: your results')}),el('option',{value:'tutto',testo:t('Stampa: tutti i bandi valutati', 'Print: all assessed calls')}));
  const nodo = el("div", { classe: "domanda fine" },
    el("div", { classe: "fine-icona" }, icona("spunta", { spessore: "3" })),
    el("h2", { testo: titolo, tabindex: "-1", id: "testo-domanda" }),
    el("p", { testo: possibili && !spettano
      ? t("Niente di quello che ci hai detto ti esclude: apri ogni bando \"possibile\" per vedere cosa resta da verificare.", "Nothing you told us rules you out: open each \"possible\" call to see what is left to check.")
      : sospesi ? t(`Le domande sono finite, ma ${sospesi === 1 ? "1 bando resta" : `${sospesi} bandi restano`} in sospeso: dipendono da risposte date con "Non lo so". Con quei dati (per esempio l'ISEE) si possono decidere.`, `The questions are over, but ${sospesi === 1 ? "1 call is" : `${sospesi} calls are`} still pending: they depend on answers given as "I don't know". With that data (for example your ISEE) they can be decided.`)
      : t("Ecco i tuoi risultati. Prima di fare domanda controlla sempre il bando ufficiale.", "Here are your results. Before applying always check the official call.") }),
    el("div", { classe: "fine-riassunto" }, pillole),
    sezioneVerifiche(dati.verifiche || []),
    lontani || ignoti || chiusiVicini ? el("p", { classe: "domanda-aiuto", testo: [
      ignoti ? t(`${ignoti} ${ignoti === 1 ? "bando" : "bandi"} dove non sappiamo dirlo`, `${ignoti} ${ignoti === 1 ? "call" : "calls"} we can't tell`) : null,
      lontani ? t(`${lontani} di altri comuni o regioni`, `${lontani} from other municipalities or regions`) : null,
      chiusiVicini ? t(`${chiusiVicini} archiviati: nuove edizioni non verificate`, `${chiusiVicini} archived: new editions not verified`) : null].filter(Boolean).join(" · ") + t(": sono in fondo alla lista.", ": they are at the bottom of the list.") }) : null,
    el("div", { classe: "fine-azioni" },
      daSegnare ? el('div',{},calendario,esporta) : el('p',{testo:t('Nessuna scadenza da aggiungere al calendario.', 'No deadline to add to the calendar.')}),
      ambitoReport,
      el("button", { classe: "pulsante secondario", type: "button", onclick: () => stampaReport(ambitoReport.value) }, icona("stampa"), t("Stampa i risultati", "Print the results")),
      el("div", { classe: "azioni-domanda" },
        el("button", { classe: "link-indietro", type: "button", testo: t("← Cambia l'ultima risposta", "← Change the last answer"), disabled: !stato.storia.length, onclick: indietro }),
        el("span", { classe: "spazio" }),
        el("button", { classe: "link-indietro", type: "button", testo: t("Ricomincia", "Start over"), onclick: () => inizia(stato.ramo) }))));
  box.replaceChildren(nodo);
  nodo.querySelector("#testo-domanda").focus({ preventScroll: true });

  stato.finito = true;
}

// ---------- avvio ----------
traduciPagina();
$("lingua").addEventListener("click", () => {
  const nuova = EN ? "it" : "en";
  if (stato.storia.length && !confirm(t("Cambiando lingua la pagina si ricarica e le risposte date si perdono. Continuare?",
    "Switching language reloads the page and your answers are lost. Continue?"))) return;
  cambiaLingua(nuova);
});
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
