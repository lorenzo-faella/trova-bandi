// La carta della domanda: una alla volta, con risposta in un clic dove si può, "Non lo so" sempre disponibile.
import { el, icona } from "./dom.js";
import { comuni } from "./api.js";
import { pocoMovimento } from "./animazioni.js";

export const NON_SO = "non lo so";
const SI_NO = [{ valore: true, etichetta: "Sì" }, { valore: false, etichetta: "No" }];
const MAX_TESSERE = 8;

let tastiera = null;

// Mostra la domanda `d` nel box. `azioni`: { rispondi(scrivi), indietro(), puoTornare, numero, giorno, verso }.
export function mostraDomanda(box, d, azioni) {
  const costruisci = () => {
    const corpo = d.per_componente ? campiComponenti(d) : d.tipo === "nucleo" ? campiNucleo()
      : d.tipo === "pagina" ? campiPagina(d) : campiSemplici(d, azioni);
    const invia = () => {
      const v = corpo.leggi();
      if (v !== undefined) azioni.rispondi(p => corpo.scrivi(p, v));
    };
    const perche = d.bandi_interessati
      ? el("p", { classe: "domanda-perche" }, icona("scintilla"),
        `Decide ${d.bandi_interessati} ${d.bandi_interessati === 1 ? "bando" : "bandi"}`)
      : null;
    const nodo = el("div", { classe: "domanda" },
      perche,
      el("h2", { classe: "domanda-testo", id: "testo-domanda", testo: d.testo, tabindex: "-1" }),
      corpo.multipla ? el("p", { classe: "piu-risposte" }, icona("spunta"), "Puoi sceglierne più di una, poi premi Avanti") : null,
      d.aiuto ? el("p", { classe: "domanda-aiuto", testo: d.aiuto }) : null,
      corpo.nodo,
      el("div", { classe: "azioni-domanda" },
        corpo.immediato ? null : el("button", { classe: "pulsante primario", testo: "Avanti →", onclick: invia }),
        el("button", { classe: "pulsante secondario", testo: "Non lo so", onclick: () => azioni.rispondi(p => corpo.scrivi(p, NON_SO)) }),
        el("span", { classe: "spazio" }),
        el("button", { classe: "link-indietro", testo: "← Indietro", disabled: !azioni.puoTornare, onclick: azioni.indietro })));
    // Invio per andare avanti; i numeri 1-9 per le scelte.
    if (tastiera) document.removeEventListener("keydown", tastiera);
    tastiera = e => {
      if (!box.isConnected || box.closest("[hidden]")) return;
      if (e.key === "Enter" && !corpo.immediato && e.target.tagName !== "BUTTON") { e.preventDefault(); invia(); }
      const n = Number(e.key);
      if (corpo.scelte && n >= 1 && n <= corpo.scelte.length && !["INPUT", "SELECT", "TEXTAREA"].includes(e.target.tagName)) corpo.scelte[n - 1].click();
    };
    document.addEventListener("keydown", tastiera);
    return nodo;
  };

  const metti = () => {
    const nodo = costruisci();
    box.replaceChildren(nodo);
    if (!pocoMovimento()) nodo.classList.add(azioni.verso === "indietro" ? "entra-sinistra" : "entra-destra");
    (box.querySelector(".campo input, .riga-persona input, .filtro-scelte") || box.querySelector("#testo-domanda"))?.focus({ preventScroll: true });
  };
  const vecchio = box.firstElementChild;
  if (vecchio && !pocoMovimento()) {
    vecchio.classList.add("esce-sinistra");
    setTimeout(metti, 180);
  } else metti();
}

function sceltaBottone(o, i, al_clic, grande = false) {
  return el("button", { classe: `scelta${grande ? " grande" : ""}`, type: "button", onclick: al_clic },
    i < 9 && !grande ? el("span", { classe: "tasto", testo: String(i + 1) }) : null, o.etichetta);
}

function campiSemplici(d, azioni) {
  const scrivi = (p, v) => { p[d.campo] = v; };
  const rispondiSubito = v => azioni.rispondi(p => scrivi(p, v));

  if (d.tipo === "si_no") {
    const scelte = SI_NO.map((o, i) => sceltaBottone(o, i, () => rispondiSubito(o.valore), true));
    return { nodo: el("div", { classe: "risposte due", role: "group", "aria-labelledby": "testo-domanda" }, scelte), scelte, immediato: true, scrivi };
  }
  if (d.tipo === "scelta" && d.opzioni.length <= MAX_TESSERE) {
    const scelte = d.opzioni.map((o, i) => sceltaBottone(o, i, () => rispondiSubito(o.valore)));
    return { nodo: el("div", { classe: "risposte", role: "group", "aria-labelledby": "testo-domanda" }, scelte), scelte, immediato: true, scrivi };
  }
  if (d.tipo === "scelta") {
    // Elenchi lunghi (le regioni): un filtro e una griglia di scelte.
    const griglia = el("div", { classe: "scelte-scorrono" },
      d.opzioni.map(o => el("button", { classe: "scelta", type: "button", "data-testo": o.etichetta.toLowerCase(), onclick: () => rispondiSubito(o.valore) }, o.etichetta)));
    const filtro = el("input", { classe: "filtro-scelte", type: "search", placeholder: "Scrivi per filtrare…", "aria-label": "Filtra le scelte",
      oninput: e => {
        const q = e.target.value.trim().toLowerCase();
        for (const b of griglia.children) b.hidden = q && !b.dataset.testo.includes(q);
      },
      onkeydown: e => { if (e.key === "Enter") { e.preventDefault(); [...griglia.children].find(b => !b.hidden)?.click(); } } });
    return { nodo: el("div", { classe: "risposte" }, filtro, griglia), immediato: true, scrivi };
  }
  if (d.tipo === "multipla") {
    // "nessuna" (situazioni particolari) esclude le altre risposte, e viceversa
    const esclusiva = v => v === "nessuna";
    const scelte = d.opzioni.map((o, i) => {
      const b = sceltaBottone(o, i, () => {
        const premuto = b.getAttribute("aria-pressed") !== "true";
        b.setAttribute("aria-pressed", String(premuto));
        if (premuto) for (const altro of scelte) {
          if (altro !== b && (esclusiva(o.valore) || esclusiva(d.opzioni[Number(altro.dataset.indice)].valore))) altro.setAttribute("aria-pressed", "false");
        }
      });
      b.setAttribute("aria-pressed", "false");
      b.dataset.indice = i;
      return b;
    });
    // persone: frasi lunghe in una colonna sola; imprese (settori, decine di voci brevi): griglia che scorre
    const griglia = scelte.length > MAX_TESSERE && !d.almeno_una;
    const nodo = el("div", { classe: `risposte multipla${griglia ? " scelte-scorrono" : ""}`, role: "group", "aria-labelledby": "testo-domanda" }, scelte);
    const leggi = () => {
      const scelti = scelte.filter(b => b.getAttribute("aria-pressed") === "true").map(b => d.opzioni[Number(b.dataset.indice)].valore);
      return d.almeno_una && !scelti.length ? avvisa(nodo, "Scegli almeno una risposta, oppure \"Non lo so\".") : scelti;
    };
    return { nodo, scelte, scrivi, leggi, multipla: true };
  }
  if (d.tipo === "numero") {
    const input = el("input", { type: "number", min: 0, step: "any", inputmode: "decimal", "aria-labelledby": "testo-domanda", placeholder: "0" });
    const nodo = el("div", { classe: "risposte" }, el("div", { classe: "campo" }, input, d.unita ? el("span", { classe: "unita", testo: d.unita }) : null));
    return { nodo, scrivi, leggi: () => input.value === "" ? avvisa(nodo) : Number(input.value) };
  }
  if (d.tipo === "data") {
    const input = el("input", { type: "date", "aria-labelledby": "testo-domanda", max: azioni.giorno });
    const nessuno = (d.opzioni || []).map((o, i) => sceltaBottone(o, i, () => rispondiSubito(o.valore)));
    const nodo = el("div", { classe: "risposte" }, el("div", { classe: "campo" }, input), nessuno);
    return { nodo, scrivi, leggi: () => input.value === "" ? avvisa(nodo) : input.value };
  }
  if (d.tipo === "comune") {
    const id = `comuni-${Math.random().toString(36).slice(2)}`;
    const lista = el("datalist", { id });
    const input = el("input", { type: "text", list: id, autocomplete: "off", "aria-labelledby": "testo-domanda", placeholder: "Scrivi il nome del comune" });
    comuni(d.regione || "").then(c => lista.replaceChildren(...c.map(nome => el("option", { value: nome })))).catch(() => {});
    const nodo = el("div", { classe: "risposte" }, el("div", { classe: "campo" }, input), lista);
    return { nodo, scrivi, leggi: () => input.value.trim() || avvisa(nodo) };
  }
  const input = el("input", { type: "text", "aria-labelledby": "testo-domanda" });
  const nodo = el("div", { classe: "risposte" }, el("div", { classe: "campo" }, input));
  return { nodo, scrivi, leggi: () => input.value.trim() || avvisa(nodo) };
}

// Chi fa parte del nucleo: "Tu" per primo, con l'età di ognuno (da lì si ricava anche l'età di chi fa domanda).
function campiNucleo() {
  const righe = el("div", { classe: "persone" });
  const rinomina = () => [...righe.children].forEach((r, i) => { r.querySelector(".chi").textContent = i === 0 ? "Tu" : `Persona ${i + 1}`; });
  const aggiungi = () => {
    const riga = el("div", { classe: "riga-persona" },
      el("span", { classe: "chi" }),
      el("input", { type: "number", min: 0, max: 120, inputmode: "numeric", "aria-label": "età", placeholder: "età (anni)" }),
      el("button", { classe: "togli", type: "button", "aria-label": "Togli questa persona", testo: "×",
        onclick: () => { if (righe.children.length > 1) { riga.remove(); rinomina(); } } }));
    righe.append(riga);
    rinomina();
    riga.querySelector("input").focus();
  };
  aggiungi();
  const nodo = el("div", { classe: "risposte" }, righe,
    el("button", { classe: "pulsante fantasma piccolo", type: "button", testo: "+ Aggiungi una persona", onclick: aggiungi }));
  const leggi = () => {
    const eta = [...righe.querySelectorAll("input")].map(i => i.value);
    return eta.some(v => v === "") ? avvisa(nodo) : eta.map(v => ({ eta: Number(v) }));
  };
  return { nodo, leggi, scrivi: (p, v) => { p.nucleo = v; } };
}

// La stessa domanda per ogni persona del nucleo: pulsanti a un clic accanto a ognuno (i numeri restano un campo).
function campiComponenti(d) {
  const campo = d.campo.split(".")[1];
  const opzioni = d.tipo === "si_no" ? SI_NO : d.opzioni;
  const righe = d.componenti.map(c => {
    const nome = c.indice === 0 ? "Tu" : `Persona ${c.indice + 1}`;
    const etichetta = c.eta === undefined || c.eta === null || c.eta === NON_SO ? nome : `${nome} · ${c.eta} anni`;
    const riga = { c, valore: undefined };
    let controllo;
    if (d.tipo === "numero") {
      controllo = el("input", { type: "number", min: 0, step: "any", "aria-label": etichetta, placeholder: d.unita || "",
        oninput: e => { riga.valore = e.target.value === "" ? undefined : Number(e.target.value); } });
    } else {
      const scelte = [...opzioni.map(o => ({ ...o })), { valore: NON_SO, etichetta: "Non lo so" }];
      controllo = el("div", { classe: "segmenti", role: "group", "aria-label": etichetta },
        scelte.map(o => el("button", { classe: "segmento", type: "button", "aria-pressed": "false", testo: o.etichetta,
          onclick: e => {
            for (const b of controllo.children) b.setAttribute("aria-pressed", "false");
            e.currentTarget.setAttribute("aria-pressed", "true");
            riga.valore = o.valore;
          } })));
      riga.premi = valore => controllo.children[scelte.findIndex(o => o.valore === valore)]?.click();
    }
    riga.nodo = el("div", { classe: "riga-persona componente" }, el("span", { classe: "chi", testo: etichetta }), controllo);
    return riga;
  });
  // Scorciatoia: la stessa risposta per tutti ("nessuno è mio figlio").
  const perTutti = d.tipo === "si_no" && righe.length > 1
    ? el("button", { classe: "pulsante fantasma piccolo", type: "button", testo: "No per tutti", onclick: () => righe.forEach(r => r.premi(false)) })
    : null;
  const nodo = el("div", { classe: "risposte persone" }, righe.map(r => r.nodo), perTutti);
  const leggi = () => {
    const valori = righe.map(r => r.valore);
    return valori.includes(undefined) ? avvisa(nodo, "Rispondi per ogni persona, anche con \"Non lo so\".") : valori;
  };
  const scrivi = (p, v) => {
    p.nucleo = p.nucleo.map(x => ({ ...x }));
    righe.forEach(({ c }, i) => { p.nucleo[c.indice][campo] = v === NON_SO ? NON_SO : v[i]; });
  };
  return { nodo, leggi, scrivi };
}

// Più domande in una pagina (residenza, domicilio): ognuna compare quando è stata data la risposta da cui dipende, per
// esempio regione e comune solo a chi ha la residenza in Italia (decisione 80).
function campiPagina(d) {
  const valori = {};
  const righe = d.parti.map(parte => {
    const riga = { parte, regione: null };
    let controllo;
    if (parte.tipo === "si_no") {
      const scelte = [...SI_NO, ...(parte.non_so ? [{ valore: NON_SO, etichetta: "Non lo so" }] : [])];
      controllo = el("div", { classe: "segmenti", role: "group", "aria-label": parte.testo },
        scelte.map(o => el("button", { classe: "segmento", type: "button", "aria-pressed": "false", testo: o.etichetta,
          onclick: e => {
            for (const b of controllo.children) b.setAttribute("aria-pressed", "false");
            e.currentTarget.setAttribute("aria-pressed", "true");
            valori[parte.campo] = o.valore;
            aggiorna();
          } })));
    } else if (parte.tipo === "scelta") {
      controllo = el("select", { "aria-label": parte.testo, onchange: e => { valori[parte.campo] = e.target.value || undefined; aggiorna(); } },
        el("option", { value: "", testo: "Scegli…" }), parte.opzioni.map(o => el("option", { value: o.valore, testo: o.etichetta })));
    } else if (parte.tipo === "comune") {
      const id = `comuni-${Math.random().toString(36).slice(2)}`;
      riga.lista = el("datalist", { id });
      controllo = el("input", { type: "text", list: id, autocomplete: "off", "aria-label": parte.testo, placeholder: "Scrivi il nome del comune",
        oninput: e => { valori[parte.campo] = e.target.value.trim() || undefined; } });
    } else {
      controllo = el("input", { type: "number", min: 0, step: "any", inputmode: "decimal", "aria-label": parte.testo, placeholder: "0",
        oninput: e => { valori[parte.campo] = e.target.value === "" ? undefined : Number(e.target.value); } });
    }
    riga.nodo = el("div", { classe: "riga-persona componente" }, el("span", { classe: "chi", testo: parte.testo }),
      el("div", { classe: "campo" }, controllo, parte.unita ? el("span", { classe: "unita", testo: parte.unita }) : null), riga.lista || null);
    return riga;
  });
  const perCampo = Object.fromEntries(righe.map(r => [r.parte.campo, r.parte]));
  const visibile = parte => Object.entries(parte.se || {}).every(([c, v]) => valori[c] === v && visibile(perCampo[c]));
  function aggiorna() {
    for (const r of righe) {
      r.nodo.hidden = !visibile(r.parte);
      if (r.parte.tipo === "comune") {
        const regione = valori[r.parte.regione_da] || "";
        if (regione !== r.regione) {
          r.regione = regione;
          comuni(regione).then(c => r.lista.replaceChildren(...c.map(nome => el("option", { value: nome })))).catch(() => {});
        }
      }
    }
  }
  aggiorna();
  const nodo = el("div", { classe: "risposte persone" }, righe.map(r => r.nodo));
  const leggi = () => {
    const out = {};
    for (const r of righe) {
      if (!visibile(r.parte)) continue;
      const v = valori[r.parte.campo];
      if (v !== undefined) out[r.parte.campo] = v;
      else if (r.parte.tipo === "comune") out[r.parte.campo] = NON_SO;  // la regione basta per i bandi regionali
      else return avvisa(nodo, `Rispondi a "${r.parte.testo}", oppure scegli "Non lo so".`);
    }
    return out;
  };
  const scrivi = (p, v) => {
    if (v === NON_SO) p[d.parti[0].campo] = NON_SO;
    else Object.assign(p, v);
  };
  return { nodo, leggi, scrivi };
}

function avvisa(nodo, testo = "Rispondi, oppure scegli \"Non lo so\".") {
  nodo.querySelector(".errore")?.remove();
  nodo.append(el("p", { classe: "errore", testo }));
  return undefined;
}
