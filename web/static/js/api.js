// Chiamate al server (web/server.py). Il profilo vive solo nel browser e viaggia intero a ogni passo.
// Ogni chiamata porta la lingua della pagina (decisione 105): il server risponde in quella lingua.
import { LINGUA } from "./i18n.js";

async function chiedi(url, corpo, signal) {
  const r = await fetch(url, corpo ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo), signal,
  } : { signal });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `${LINGUA === "en" ? "error" : "errore"} ${r.status}`);
  return r.json();
}

export const passo = (ramo, profilo, modifica, signal) => chiedi("/api/passo", { ramo, profilo, estratte: true, modifica, lingua: LINGUA }, signal);
export const statistiche = () => chiedi("/api/statistiche");
export const profili = () => chiedi(`/api/profili?lingua=${LINGUA}`);
export const confronto = () => chiedi(`/api/confronto?lingua=${LINGUA}`);
export const percorsi = () => chiedi(`/api/percorsi?lingua=${LINGUA}`);
export const comuni = regione => chiedi(regione ? `/api/comuni?regione=${encodeURIComponent(regione)}` : "/api/comuni");
