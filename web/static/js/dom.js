import { LOCALE } from "./i18n.js";

// Costruzione del DOM senza innerHTML: titoli, enti e citazioni arrivano da siti esterni e vanno sempre come testo.

export function el(tag, attributi = {}, ...figli) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attributi)) {
    if (v === null || v === undefined || v === false) continue;
    if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else if (k === "testo") n.textContent = v;
    else if (k === "classe") n.className = v;
    else n.setAttribute(k, v === true ? "" : v);
  }
  for (const f of figli.flat()) if (f !== null && f !== undefined && f !== false) n.append(f);
  return n;
}

// Icone: tracciati SVG nostri (costanti), costruiti con createElementNS.
const TRACCIATI = {
  persona: ["M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z", "M4 21c0-4 3.6-7 8-7s8 3 8 7"],
  impresa: ["M3 21h18", "M5 21V8l7-4 7 4v13", "M9 21v-5h6v5", "M9 11h.01M15 11h.01"],
  studente: ["M2 9l10-5 10 5-10 5z", "M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5", "M22 9v6"],
  famiglia: ["M8 10a3 3 0 1 0 0-6 3 3 0 0 0 0 6z", "M17 11a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z", "M2 21c0-3.5 2.7-6 6-6s6 2.5 6 6", "M14 21c0-2.5 1.3-4.5 3-4.5s4 1.5 4 4.5"],
  autonomo: ["M4 7h16v12H4z", "M9 7V5h6v2", "M4 12h16"],
  mamma: ["M5 10a7 7 0 0 1 7-7v7", "M4 10h15", "M19 10l1.5-3", "M5.5 10l1.8 5.5h9.4l1.8-5.5", "M9 21a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5z", "M15.5 21a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5z"],
  pensionata: ["M12 3a3 3 0 1 0 0 6 3 3 0 0 0 0-6z", "M8 21l1-7-3-2 3-3h6l2 4", "M17 12v9"],
  spunta: ["M5 12.5l4.5 4.5L19 7.5"],
  croce: ["M6 6l12 12M18 6L6 18"],
  punto: ["M12 8v5", "M12 16h.01", "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z"],
  domanda: ["M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6V14", "M12 17h.01", "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z"],
  lente: ["M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z", "M20 20l-4-4"],
  scudo: ["M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z", "M9 12l2 2 4-4"],
  orologio: ["M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z", "M12 7v5l3 2"],
  calendario: ["M4 6h16v14H4z", "M4 10h16", "M8 3v4M16 3v4"],
  stampa: ["M7 9V3h10v6", "M7 17H4v-7h16v7h-3", "M7 14h10v7H7z"],
  freccia: ["M6 9l6 6 6-6"],
  avviso: ["M12 3l10 18H2z", "M12 10v4", "M12 17h.01"],
  scintilla: ["M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"],
};

export function icona(nome, attributi = {}) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("fill", "none");
  svg.setAttribute("stroke", "currentColor");
  svg.setAttribute("stroke-width", attributi.spessore || "2");
  svg.setAttribute("stroke-linecap", "round");
  svg.setAttribute("stroke-linejoin", "round");
  svg.setAttribute("aria-hidden", "true");
  for (const d of TRACCIATI[nome] || []) {
    const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
    p.setAttribute("d", d);
    svg.append(p);
  }
  return svg;
}

export const numeroIt = n => new Intl.NumberFormat(LOCALE).format(n);

export function avviso(testo, durata = 3200) {
  const box = document.getElementById("avvisi");
  const a = el("div", { classe: "avviso", testo });
  box.append(a);
  setTimeout(() => { a.classList.add("via"); setTimeout(() => a.remove(), 320); }, durata);
}
