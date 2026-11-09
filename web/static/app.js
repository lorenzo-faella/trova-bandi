// Demo di trova-bandi. Il profilo vive solo in questa pagina (nessun salvataggio): a ogni risposta lo si manda intero
// a /api/passo, che restituisce gli esiti aggiornati e la prossima domanda.
"use strict";

const NON_SO = "non lo so";
const STATI = {
  "idoneo": { classe: "colore-idoneo", titolo: "Idoneo" },
  "idoneo, salvo eccezioni": { classe: "colore-salvo", titolo: "Idoneo, salvo eccezioni" },
  "quasi idoneo": { classe: "colore-quasi", titolo: "Quasi idoneo: ti manca un requisito" },
  "da verificare": { classe: "colore-verificare", titolo: "Da verificare: c'è un requisito che non sappiamo controllare" },
  "mancano dati": { classe: "colore-mancano", titolo: "Mancano dati" },
  "non idoneo": { classe: "colore-no", titolo: "Non idoneo" },
};
const SPIEGA_PERCHE = {
  "idoneo": null,
  "idoneo, salvo eccezioni": "Hai tutti i requisiti, salvo questi casi particolari: controlla che non ti riguardino.",
  "quasi idoneo": "Il bando chiede, e oggi non hai:",
  "da verificare": "Da controllare sulla fonte:",
  "mancano dati": "Serve sapere:",
  "non idoneo": "Il bando chiede, e non hai:",
};
// Gruppi lunghi (imprese: centinaia di bandi) partono chiusi.
const MAX_APERTI = 12;

const stato = { ramo: null, profilo: {}, storia: [], estratte: false, ultimo: null };

// --- utilità DOM, senza innerHTML con dati: i titoli dei bandi arrivano da siti esterni ---
function el(tag, attributi = {}, ...figli) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attributi)) {
    if (v === null || v === undefined || v === false) continue;
    if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "testo") n.textContent = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const f of figli.flat()) if (f !== null && f !== undefined) n.append(f);
  return n;
}

async function chiedi(url, corpo) {
  const r = await fetch(url, corpo ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo),
  } : undefined);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `errore ${r.status}`);
  return r.json();
}

// --- flusso ---
async function avanza() {
  const domanda = document.getElementById("domanda");
  try {
    const dati = await chiedi("/api/passo", { ramo: stato.ramo, profilo: stato.profilo, estratte: stato.estratte });
    stato.ultimo = dati;
    mostraDomanda(dati.domanda);
    mostraRisultati(dati);
  } catch (e) {
    domanda.replaceChildren(el("p", { class: "errore", testo: `Qualcosa non va: ${e.message}` }),
      el("button", { class: "secondario", testo: "Ricomincia", onclick: ricomincia }));
  }
}

function rispondi(aggiorna) {
  stato.storia.push(structuredClone(stato.profilo));
  aggiorna(stato.profilo);
  avanza();
}

function indietro() {
  if (stato.storia.length) {
    stato.profilo = stato.storia.pop();
    avanza();
  }
}

function ricomincia() {
  Object.assign(stato, { ramo: null, profilo: {}, storia: [], ultimo: null });
  document.getElementById("lavoro").hidden = true;
  document.getElementById("inizio").hidden = false;
}

// --- domanda ---
function mostraDomanda(d) {
  const box = document.getElementById("domanda");
  const n = stato.storia.length;
  const navigazione = el("div", { class: "pulsanti" },
    el("button", { class: "testo", testo: "← Indietro", onclick: indietro, disabled: n === 0 }),
    el("button", { class: "testo", testo: "Ricomincia", onclick: ricomincia }));
  if (!d) {
    box.replaceChildren(
      el("p", { class: "contatore", testo: `${n} ${n === 1 ? "domanda" : "domande"}` }),
      el("h2", { testo: "Fatto" }),
      el("p", { testo: "Non servono altre domande: nessuna risposta in più cambierebbe gli esiti." }),
      navigazione);
    return;
  }
  const contatore = `Domanda ${n + 1} · serve a decidere ${d.bandi_interessati} ${d.bandi_interessati === 1 ? "bando" : "bandi"}`;
  const corpo = d.per_componente ? campiComponenti(d) : d.tipo === "nucleo" ? campiNucleo() : campiSemplici(d);
  box.replaceChildren(
    el("p", { class: "contatore", testo: contatore }),
    el("p", { class: "testo-domanda", testo: d.testo, id: "testo-domanda" }),
    d.aiuto ? el("p", { class: "aiuto", testo: d.aiuto }) : null,
    corpo.nodo,
    el("div", { class: "pulsanti" },
      el("button", { class: "primario", testo: "Avanti", onclick: () => {
        const v = corpo.leggi();
        if (v !== undefined) rispondi(p => corpo.scrivi(p, v));
      } }),
      el("button", { class: "secondario", testo: "Non lo so", onclick: () => rispondi(p => corpo.scrivi(p, NON_SO)) })),
    navigazione);
  box.querySelector("input, select")?.focus();
}

function campiSemplici(d) {
  const scrivi = (p, v) => { p[d.campo] = v; };
  let nodo, leggi;
  if (d.tipo === "si_no" || (d.tipo === "scelta" && d.opzioni.length <= 8)) {
    const opzioni = d.tipo === "si_no" ? [{ valore: true, etichetta: "Sì" }, { valore: false, etichetta: "No" }] : d.opzioni;
    nodo = el("div", { class: "opzioni", role: "radiogroup", "aria-labelledby": "testo-domanda" },
      opzioni.map((o, i) => el("label", { class: "opzione" },
        el("input", { type: "radio", name: "risposta", value: i }), o.etichetta)));
    leggi = () => {
      const s = nodo.querySelector("input:checked");
      return s ? opzioni[Number(s.value)].valore : avvisa(nodo);
    };
  } else if (d.tipo === "scelta") {
    const select = el("select", { "aria-labelledby": "testo-domanda" }, el("option", { value: "", testo: "Scegli…" }),
      d.opzioni.map((o, i) => el("option", { value: i, testo: o.etichetta })));
    nodo = el("div", { class: "opzioni" }, select);
    leggi = () => select.value === "" ? avvisa(nodo) : d.opzioni[Number(select.value)].valore;
  } else if (d.tipo === "multipla") {
    nodo = el("div", { class: "opzioni" }, d.opzioni.map((o, i) => el("label", { class: "opzione" },
      el("input", { type: "checkbox", value: i }), o.etichetta)));
    leggi = () => [...nodo.querySelectorAll("input:checked")].map(c => d.opzioni[Number(c.value)].valore);
  } else if (d.tipo === "numero") {
    const input = el("input", { type: "number", min: 0, step: "any", inputmode: "decimal", "aria-labelledby": "testo-domanda" });
    nodo = el("div", { class: "campo-riga" }, input, el("span", { class: "unita", testo: d.unita || "" }));
    leggi = () => input.value === "" ? avvisa(nodo) : Number(input.value);
  } else if (d.tipo === "data") {
    const input = el("input", { type: "date", "aria-labelledby": "testo-domanda", max: stato.ultimo?.giorno });
    const extra = (d.opzioni || []).map(o => el("label", { class: "opzione" },
      el("input", { type: "checkbox", value: o.valore, onchange: e => { input.disabled = e.target.checked; } }), o.etichetta));
    nodo = el("div", { class: "opzioni" }, input, extra);
    leggi = () => {
      const s = nodo.querySelector("input[type=checkbox]:checked");
      if (s) return s.value;
      return input.value === "" ? avvisa(nodo) : input.value;
    };
  } else if (d.tipo === "comune") {
    const lista = el("datalist", { id: "comuni" });
    const input = el("input", { type: "text", list: "comuni", autocomplete: "off", "aria-labelledby": "testo-domanda" });
    if (d.regione) chiedi(`/api/comuni?regione=${encodeURIComponent(d.regione)}`)
      .then(c => lista.replaceChildren(...c.map(nome => el("option", { value: nome })))).catch(() => {});
    nodo = el("div", { class: "opzioni" }, input, lista);
    leggi = () => input.value.trim() || avvisa(nodo);
  } else {
    const input = el("input", { type: "text", "aria-labelledby": "testo-domanda" });
    nodo = el("div", { class: "opzioni" }, input);
    leggi = () => input.value.trim() || avvisa(nodo);
  }
  return { nodo, leggi, scrivi };
}

function campiNucleo() {
  const righe = el("div");
  const aggiungi = (eta = "") => {
    const riga = el("div", { class: "campo-riga" },
      el("span", { testo: righe.children.length === 0 ? "Tu" : `Componente ${righe.children.length + 1}` }),
      el("input", { type: "number", min: 0, max: 120, value: eta, "aria-label": "età", placeholder: "età" }),
      el("button", { class: "testo", testo: "Togli", onclick: () => { if (righe.children.length > 1) riga.remove(); } }));
    righe.append(riga);
  };
  aggiungi();
  const nodo = el("div", {}, righe, el("button", { class: "secondario", testo: "+ Aggiungi una persona", onclick: () => aggiungi() }));
  const leggi = () => {
    const eta = [...righe.querySelectorAll("input")].map(i => i.value);
    return eta.some(v => v === "") ? avvisa(nodo) : eta.map(v => ({ eta: Number(v) }));
  };
  return { nodo, leggi, scrivi: (p, v) => { p.nucleo = v; } };
}

function campiComponenti(d) {
  const campo = d.campo.split(".")[1];
  const opzioni = d.tipo === "si_no" ? [{ valore: true, etichetta: "Sì" }, { valore: false, etichetta: "No" }] : d.opzioni;
  const righe = d.componenti.map(c => {
    const nome = c.indice === 0 ? "Tu" : `Componente ${c.indice + 1}`;
    const input = d.tipo === "numero"
      ? el("input", { type: "number", min: 0, step: "any", "aria-label": nome })
      : el("select", { "aria-label": nome }, el("option", { value: "", testo: "Scegli…" }),
        opzioni.map((o, i) => el("option", { value: i, testo: o.etichetta })),
        el("option", { value: "?", testo: "Non lo so" }));
    return { c, input, nodo: el("div", { class: "campo-riga" },
      el("span", { testo: c.eta === undefined || c.eta === null ? nome : `${nome} (${c.eta} anni)` }), input,
      el("span", { class: "unita", testo: d.unita || "" })) };
  });
  const nodo = el("div", { class: "opzioni" }, righe.map(r => r.nodo));
  const leggi = () => {
    const valori = righe.map(({ input }) => {
      if (input.value === "") return undefined;
      if (input.value === "?") return NON_SO;
      return d.tipo === "numero" ? Number(input.value) : opzioni[Number(input.value)].valore;
    });
    return valori.includes(undefined) ? avvisa(nodo) : valori;
  };
  const scrivi = (p, v) => {
    p.nucleo = p.nucleo.map(x => ({ ...x }));
    righe.forEach(({ c }, i) => { p.nucleo[c.indice][campo] = v === NON_SO ? NON_SO : v[i]; });
  };
  return { nodo, leggi, scrivi };
}

function avvisa(nodo) {
  nodo.querySelector(".errore")?.remove();
  nodo.append(el("p", { class: "errore", testo: "Rispondi, oppure scegli \"Non lo so\"." }));
  return undefined;
}

// --- risultati ---
function mostraRisultati(dati) {
  const box = document.getElementById("risultati");
  const conteggi = el("div", { class: "conteggi" }, Object.entries(dati.conteggi).filter(([, n]) => n > 0)
    .map(([s, n]) => el("span", { class: `chip ${STATI[s].classe}` }, el("b", { testo: n }), ` ${s}`)));
  const gruppi = Object.keys(STATI).map(s => {
    const voci = dati.risultati.filter(r => r.stato === s);
    if (!voci.length) return null;
    const titolo = `${STATI[s].titolo} (${voci.length})`;
    const schede = () => voci.map(scheda);
    if (s === "non idoneo" || voci.length > MAX_APERTI) {
      const d = el("details", { class: "gruppo" }, el("summary", { testo: titolo }));
      d.addEventListener("toggle", () => { if (d.open && d.children.length === 1) d.append(...schede()); }, { once: true });
      return d;
    }
    return el("div", { class: "gruppo" }, el("p", { class: "gruppo-titolo", testo: titolo }), schede());
  });
  box.replaceChildren(el("h2", { class: "visually-hidden", testo: "Esiti" }), conteggi, ...gruppi.filter(Boolean),
    el("p", { class: "fonte", testo: `Bandi aperti il ${dati.giorno}.` }));
}

function scheda(r) {
  const info = STATI[r.stato];
  const meta = [r.ente, r.chiusura ? `scade il ${r.chiusura}` : null].filter(Boolean).join(" · ");
  const etichette = [];
  if (r.origine === "estratta") etichette.push(el("span", { class: "etichetta avviso", testo: "estratta da un LLM, non rivista" }));
  if (r.origine === "open data") etichette.push(el("span", { class: "etichetta", testo: "incentivi.gov.it" }));
  const perche = r.perche.length && SPIEGA_PERCHE[r.stato]
    ? [el("p", { class: "meta", testo: SPIEGA_PERCHE[r.stato] }), elencoRequisiti(r.perche)] : [];
  const requisiti = r.requisiti.length
    ? el("details", {}, el("summary", { testo: r.requisiti.length === 1 ? "Perché sì: il requisito, con la fonte" : `Perché sì: i ${r.requisiti.length} requisiti, con la fonte` }), elencoRequisiti(r.requisiti))
    : null;
  return el("article", { class: `bando ${info.classe}` },
    el("h3", { testo: r.titolo }, ...etichette),
    el("p", { class: "meta" }, el("span", { class: "stato", testo: r.stato }), meta ? ` · ${meta}` : ""),
    ...perche, requisiti,
    r.link ? el("p", { class: "fonte" }, el("a", { href: r.link, target: "_blank", rel: "noopener", testo: "Fonte ufficiale ↗" })) : null);
}

function elencoRequisiti(voci) {
  return el("ul", { class: "perche" }, voci.map(v => el("li", {},
    v.testo,
    v.citazione ? el("blockquote", { testo: `«${v.citazione}»` }) : null,
    v.fonte ? el("div", { class: "fonte", testo: v.fonte }) : null)));
}

// --- avvio ---
document.querySelectorAll(".ramo").forEach(b => b.addEventListener("click", () => {
  stato.ramo = b.dataset.ramo;
  stato.estratte = document.getElementById("estratte").checked;
  document.getElementById("inizio").hidden = true;
  document.getElementById("lavoro").hidden = false;
  avanza();
}));
