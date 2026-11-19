// Demo di trova-bandi (decisione 68). Il profilo vive solo in questa pagina: a ogni risposta lo si manda intero a
// /api/passo, che restituisce esiti aggiornati e prossima domanda. Nessun salvataggio, nemmeno nel browser.
import { el, icona, numeroIt, avviso } from "./dom.js";
import * as api from "./api.js";
import { conta, cambiaVista, coriandoli, osservaEntrate } from "./animazioni.js";
import { mostraDomanda, NON_SO } from "./domanda.js";
import { mostraRisultati, azzera, iniziaStrumenti, STATI, contaVisibili } from "./risultati.js";
import { scaricaIcs, scadenze } from "./calendario.js";

const stato = { ramo: null, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" };
const $ = id => document.getElementById(id);

// ---------- pagina iniziale ----------
async function caricaNumeri() {
  const box = $("numeri");
  const voci = [
    ["persone", "aiuti per le persone: INPS, borse di studio, casa, comuni"],
    ["imprese_aperte", "bandi per le imprese aperti oggi"],
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
  Object.assign(stato, { ramo, profilo: {}, storia: [], ultimo: null, esempio: null, finito: false, verso: "avanti" });
  azzera();
  $("esempio").hidden = true;
  $("avviso-isee").hidden = true;
  $("domanda").replaceChildren();
  entraNelPercorso();
  avanza();
}

function provaProfilo(p) {
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
  const p = stato.profilo;
  const regioni = [p.regione, p.domicilio_diverso === true ? p.regione_domicilio : null, p.regione_ateneo]
    .filter(r => r && r !== NON_SO && r !== "non_applicabile");
  return { ramo: stato.ramo, regioni: [...new Set(regioni)] };
}

// Le risposte date: chiuse sullo schermo, sempre stampate nel report.
function mostraRiepilogo(righe) {
  const box = $("riepilogo");
  if (!righe || !righe.length) { box.hidden = true; return; }
  const aperto = box.open;
  box.replaceChildren(el("summary", { testo: `Le tue risposte (${righe.length})` }),
    el("dl", { classe: "riepilogo-lista" }, righe.flatMap(r => [el("dt", { testo: r.voce }), el("dd", { testo: r.valore })])));
  box.open = aperto;
  box.hidden = false;
}
window.addEventListener("beforeprint", () => { $("riepilogo").open = true; });
async function avanza() {
  try {
    const dati = await api.passo(stato.ramo, stato.profilo);
    stato.ultimo = dati;
    mostraRisultati(dati, contesto());
    mostraRiepilogo(dati.riepilogo);
    aggiornaAvanzamento(dati);
    mostraAvvisoIsee(dati.isee);
    if (dati.domanda) {
      stato.finito = false;
      mostraDomanda($("domanda"), dati.domanda, {
        rispondi, indietro, puoTornare: stato.storia.length > 0, giorno: dati.giorno, verso: stato.verso,
      });
    } else mostraFine(dati);
  } catch (e) {
    $("domanda").replaceChildren(el("div", { classe: "domanda" },
      el("p", { classe: "errore", testo: `Qualcosa non va: ${e.message}` }),
      el("button", { classe: "pulsante secondario", testo: "Ricomincia", onclick: () => inizia(stato.ramo || "persone") })));
  }
}

function rispondi(aggiorna) {
  stato.storia.push(structuredClone(stato.profilo));
  aggiorna(stato.profilo);
  stato.verso = "avanti";
  avanza();
}

function indietro() {
  if (!stato.storia.length) return;
  stato.profilo = stato.storia.pop();
  stato.verso = "indietro";
  avanza();
}

function aggiornaAvanzamento(dati) {
  const tot = dati.risultati.length || 1;
  const decisi = tot - (dati.conteggi["mancano dati"] || 0);
  const n = stato.storia.length;
  $("avanz-etichetta").textContent = dati.domanda ? `Domanda ${n + 1}` : `${n} ${n === 1 ? "risposta" : "risposte"}`;
  $("avanz-decisi").textContent = `${numeroIt(decisi)} di ${numeroIt(tot)} bandi decisi`;
  $("avanz-riempi").style.width = `${Math.round(100 * decisi / tot)}%`;
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
          onclick: () => { stato.storia.push(structuredClone(stato.profilo)); delete stato.profilo.isee; stato.verso = "avanti"; avanza(); } }))));
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
  const daSegnare = scadenze(dati.risultati, dati.giorno).length;
  const titolo = spettano ? `Ti ${spettano === 1 ? "spetta 1 aiuto" : `spettano ${spettano} aiuti`}`
    : possibili ? `${possibili} ${possibili === 1 ? "aiuto possibile" : "aiuti possibili"} per te`
    : "Abbiamo finito";
  const box = $("domanda");
  const pillole = ["idoneo", "idoneo, salvo eccezioni", "da verificare", "quasi idoneo", "mancano dati"]
    .filter(s => c[s]).map(s => el("span", { classe: `pillola ${STATI[s].classe}` }, el("b", { testo: String(c[s]) }), ` ${STATI[s].tessera}`));
  const nodo = el("div", { classe: "domanda fine" },
    el("div", { classe: "fine-icona" }, icona("spunta", { spessore: "3" })),
    el("h2", { testo: titolo, tabindex: "-1", id: "testo-domanda" }),
    el("p", { testo: possibili && !spettano
      ? "Nessun requisito che sappiamo controllare ti esclude: apri ogni bando \"possibile\" per vedere cosa resta da verificare."
      : "Non servono altre domande: nessuna risposta in più cambierebbe gli esiti." }),
    el("div", { classe: "fine-riassunto" }, pillole),
    lontani || ignoti || chiusiVicini ? el("p", { classe: "domanda-aiuto", testo: [
      ignoti ? `${ignoti} ${ignoti === 1 ? "bando" : "bandi"} dove non sappiamo dirlo` : null,
      lontani ? `${lontani} di altre regioni` : null,
      chiusiVicini ? `${chiusiVicini} chiusi da poco che di solito riaprono` : null].filter(Boolean).join(" · ") + ": sono in fondo alla lista." }) : null,
    el("div", { classe: "fine-azioni" },
      daSegnare ? el("button", { classe: "pulsante primario", type: "button", onclick: () => {
        const n = scaricaIcs(dati.risultati, dati.giorno);
        avviso(`Scaricato il calendario con ${n} ${n === 1 ? "scadenza" : "scadenze"}`);
      } }, icona("calendario"), `Aggiungi ${daSegnare} ${daSegnare === 1 ? "scadenza" : "scadenze"} al calendario`) : null,
      el("button", { classe: "pulsante secondario", type: "button", onclick: () => window.print() }, icona("stampa"), "Stampa i risultati"),
      el("div", { classe: "azioni-domanda" },
        el("button", { classe: "link-indietro", type: "button", testo: "← Cambia l'ultima risposta", disabled: !stato.storia.length, onclick: indietro }),
        el("span", { classe: "spazio" }),
        el("button", { classe: "link-indietro", type: "button", testo: "Ricomincia", onclick: () => inizia(stato.ramo) }))));
  box.replaceChildren(nodo);
  nodo.querySelector("#testo-domanda").focus({ preventScroll: true });
  if (!stato.finito && (spettano || possibili || quasi)) coriandoli(box);
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
