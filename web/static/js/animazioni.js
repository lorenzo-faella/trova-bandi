// Animazioni: Web Animations API e CSS. Con prefers-reduced-motion niente movimento, stessi contenuti.

export const pocoMovimento = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Un numero che sale (o scende) fino al valore, con il formato italiano.
export function conta(nodo, verso, durata = 900) {
  const da = Number(nodo.dataset.valore || 0);
  nodo.dataset.valore = verso;
  const fmt = new Intl.NumberFormat("it-IT");
  if (pocoMovimento() || da === verso) { nodo.textContent = fmt.format(verso); return; }
  const inizio = performance.now();
  const passo = ora => {
    const t = Math.min(1, (ora - inizio) / durata);
    const e = 1 - Math.pow(1 - t, 3);
    nodo.textContent = fmt.format(Math.round(da + (verso - da) * e));
    if (t < 1) requestAnimationFrame(passo);
  };
  requestAnimationFrame(passo);
}

// FLIP: si annotano le posizioni, si cambia il DOM, poi ogni elemento parte da dove era e scivola dove è ora.
export function flip(contenitore, cambia) {
  const prima = new Map();
  for (const n of contenitore.querySelectorAll("[data-chiave]")) prima.set(n.dataset.chiave, n.getBoundingClientRect());
  cambia();
  if (pocoMovimento()) return;
  for (const n of contenitore.querySelectorAll("[data-chiave]")) {
    const p = prima.get(n.dataset.chiave);
    if (!p) continue;
    const d = n.getBoundingClientRect();
    const dy = p.top - d.top;
    if (Math.abs(dy) < 2) continue;
    n.animate([{ transform: `translateY(${dy}px)` }, { transform: "none" }],
      { duration: 550, easing: "cubic-bezier(.2,.8,.2,1)" });
  }
}

// Cambio di schermata con la View Transitions API dove c'è, altrimenti una dissolvenza.
export function cambiaVista(cambia) {
  if (document.startViewTransition && !pocoMovimento()) return document.startViewTransition(cambia).finished;
  cambia();
  return Promise.resolve();
}

// Altezza animata per aprire e chiudere un pannello.
export function apriChiudi(corpo, apri) {
  const dentro = corpo.firstElementChild;
  if (pocoMovimento()) { corpo.style.height = apri ? "auto" : "0"; return; }
  const da = corpo.getBoundingClientRect().height;
  const a = apri ? dentro.getBoundingClientRect().height : 0;
  corpo.style.height = `${da}px`;
  requestAnimationFrame(() => {
    corpo.style.height = `${a}px`;
    if (apri) corpo.addEventListener("transitionend", () => { if (corpo.style.height !== "0px") corpo.style.height = "auto"; }, { once: true });
  });
}

// Gli elementi .entra-scorrendo compaiono quando arrivano nello schermo.
export function osservaEntrate() {
  const nodi = document.querySelectorAll(".entra-scorrendo");
  if (!("IntersectionObserver" in window) || pocoMovimento()) { nodi.forEach(n => n.classList.add("visto")); return; }
  const oss = new IntersectionObserver(voci => voci.forEach(v => {
    if (v.isIntersecting) { v.target.classList.add("visto"); oss.unobserve(v.target); }
  }), { threshold: .15 });
  nodi.forEach(n => oss.observe(n));
}
