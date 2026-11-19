// Chiamate al server (web/server.py). Il profilo vive solo nel browser e viaggia intero a ogni passo.

async function chiedi(url, corpo) {
  const r = await fetch(url, corpo ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo),
  } : undefined);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `errore ${r.status}`);
  return r.json();
}

export const passo = (ramo, profilo) => chiedi("/api/passo", { ramo, profilo, estratte: true });
export const statistiche = () => chiedi("/api/statistiche");
export const profili = () => chiedi("/api/profili");
export const comuni = regione => chiedi(regione ? `/api/comuni?regione=${encodeURIComponent(regione)}` : "/api/comuni");
