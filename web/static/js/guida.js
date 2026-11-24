// Percorso guidato dei profili d'esempio (decisione 104): la demo ripercorre il questionario una domanda alla volta,
// con la risposta del profilo già scelta, e i risultati si aggiornano a ogni passo. Qui solo la risposta da dare e il
// suo testo; il ritmo e i pulsanti stanno in app.js. Una risposta che il profilo non ha vale "Non lo so", come in
// prove/simulazione/rigioca.py.
import { numeroIt } from "./dom.js";
import { NON_SO } from "./domanda.js";

const uguale = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const valore = (t, campo) => (t[campo] === undefined ? NON_SO : t[campo]);

// "Sei nato in Italia e ci hai sempre vissuto?": i profili scrivono gli anni di residenza, non questa risposta.
function sempreInItalia(t) {
  const eta = t.nucleo?.[0]?.eta;
  return t.sempre_in_italia ?? (eta !== undefined && t.anni_residenza_continuativa_italia === eta);
}

// La funzione che scrive la risposta del profilo `t` alla domanda `d`, con la stessa forma delle risposte della pagina.
export function scriviRisposta(d, t) {
  if (d.tipo === "pagina") {
    return p => {
      for (const parte of d.parti) {
        if (!Object.entries(parte.se || {}).every(([k, v]) => uguale(p[k], v))) continue;
        p[parte.campo] = parte.campo === "sempre_in_italia" ? sempreInItalia(t) : valore(t, parte.campo);
      }
    };
  }
  if (d.tipo === "nucleo" || d.campo === "nucleo") {
    return p => { p.nucleo = (t.nucleo || []).map(c => ({ eta: c.eta ?? NON_SO })); };
  }
  if (d.campo.startsWith("nucleo.")) {
    const nome = d.campo.split(".")[1];
    return p => {
      p.nucleo = (p.nucleo || []).map(c => ({ ...c }));
      for (const c of d.componenti || []) p.nucleo[c.indice][nome] = t.nucleo?.[c.indice]?.[nome] ?? NON_SO;
    };
  }
  return p => { p[d.campo] = valore(t, d.campo); };
}

function leggibile(v, opzioni, unita) {
  if (v === NON_SO || v === undefined || v === null) return "Non lo so";
  if (v === true) return "Sì";
  if (v === false) return "No";
  if (Array.isArray(v)) return v.length ? v.map(x => leggibile(x, opzioni)).join(", ") : "nessuna";
  if (typeof v === "number") return unita ? `${numeroIt(v)} ${unita}` : numeroIt(v);
  const o = (opzioni || []).find(o => o.valore === v);
  if (o) return o.etichetta;
  const data = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v);
  return data ? `${data[3]}/${data[2]}/${data[1]}` : String(v).replaceAll("_", " ");
}

// I campi in euro (ISEE, redditi, canone, patrimonio): le domande non scrivono l'unità.
const EURO = /isee|ispe|reddito|canone|patrimonio/;
const unita = (campo, u) => u || (EURO.test(campo) ? "€" : "");

// La risposta in parole, per la barra del percorso guidato.
export function testoRisposta(d, prima, dopo) {
  if (d.tipo === "pagina") {
    return d.parti.filter(parte => dopo[parte.campo] !== undefined && !uguale(prima[parte.campo], dopo[parte.campo]))
      .map(parte => `${parte.testo.replace(/\?$/, "")}: ${leggibile(dopo[parte.campo], parte.opzioni, unita(parte.campo, parte.unita))}`).join(" · ");
  }
  if (d.tipo === "nucleo" || d.campo === "nucleo") {
    const n = dopo.nucleo?.length || 0;
    return `${n} ${n === 1 ? "persona" : "persone"} (età ${dopo.nucleo.map(c => leggibile(c.eta)).join(", ")})`;
  }
  if (d.campo.startsWith("nucleo.")) {
    const nome = d.campo.split(".")[1];
    return (d.componenti || []).map(c => `${c.indice === 0 ? "Tu" : `persona ${c.indice + 1}`}: ${leggibile(dopo.nucleo?.[c.indice]?.[nome], d.opzioni)}`).join(" · ");
  }
  return leggibile(dopo[d.campo], d.opzioni, unita(d.campo, d.unita));
}
