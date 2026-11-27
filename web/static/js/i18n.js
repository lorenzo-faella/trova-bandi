// Lingua della demo (decisione 105): italiano o inglese. Si sceglie con ?lang=en o con il pulsante in alto, e il
// browser se la ricorda. Il server traduce domande, etichette ed esiti; qui i testi dell'interfaccia. Titoli dei bandi,
// enti, citazioni e testi delle regole restano in italiano, come nelle fonti.
const LINGUE = ["it", "en"];

function salvata() {
  try { return localStorage.getItem("lingua"); } catch { return null; }
}

const richiesta = new URLSearchParams(location.search).get("lang");
export const LINGUA = LINGUE.includes(richiesta) ? richiesta : salvata() === "en" ? "en" : "it";
export const EN = LINGUA === "en";
export const LOCALE = EN ? "en-GB" : "it-IT";

// Il testo nella lingua della pagina: t("Ricomincia", "Start over").
export const t = (italiano, inglese) => (EN ? inglese : italiano);

// Si ricarica la pagina nella nuova lingua: le risposte date si perdono (non sono salvate da nessuna parte).
export function cambiaLingua(lingua) {
  try { localStorage.setItem("lingua", lingua); } catch { /* senza memoria del browser vale il parametro */ }
  const url = new URL(location.href);
  url.searchParams.set("lang", lingua);
  location.href = url.toString();
}

// I testi fissi di index.html: data-en ha il contenuto inglese, data-en-<attributo> l'attributo inglese.
// Sono costanti scritte da noi, mai testi delle fonti.
export function traduciPagina() {
  document.documentElement.lang = LINGUA;
  if (!EN) return;
  for (const n of document.querySelectorAll(".solo-en")) n.hidden = false;
  for (const n of document.querySelectorAll("[data-en]")) n.innerHTML = n.dataset.en;
  for (const n of document.querySelectorAll("*")) {
    for (const a of [...n.attributes]) {
      if (a.name.startsWith("data-en-")) n.setAttribute(a.name.slice(8), a.value);
    }
  }
}

// "Comune di Milano, pagina 2" -> "Comune di Milano, page 2": l'ente resta com'è, la posizione si traduce.
export const fonte = s => (EN && s ? s.replace(/, pagina web$/, ", web page").replace(/, pagina (\d+)$/, ", page $1")
  .replace(/, documento$/, ", document").replace(/, campo (\S+)$/, ", field $1") : s);
