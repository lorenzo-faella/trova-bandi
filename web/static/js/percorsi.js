// Grafico dei percorsi (decisione 104): una folla di persone attraversa sei colonne di "porte", una per domanda chiave,
// e arriva a un numero di aiuti. Ogni linea è una persona: entra nella porta della sua risposta, quindi i fasci si
// separano e si incrociano. I profili d'esempio hanno faccina, linea spessa e contatore. SVG a mano, nessuna libreria;
// con "riduci movimento" si mostra subito la fine. Dati da /api/percorsi (folla in web/folla_demo.json).
import { t as L } from "./i18n.js";

const NS = "http://www.w3.org/2000/svg";
const W = 1170, X0 = 40, X1 = 150, PASSO_X = 122, CIMA = 104, UNITA = 4.2, GAP = 16, R = 14, USCITA = 112;
const DURATA = 1050, SFASAMENTO = 380, PAUSA = 420;
// un colore per area, nell'ordine della prima colonna (Nord-Ovest, Nord-Est, Centro, Sud, Isole): i nomi arrivano tradotti
const COLORI_AREE = ["#4f46e5", "#0891b2", "#f59e0b", "#e11d48", "#7c3aed"];
const COLORI_ARRIVO = ["#cbd5e1", "#86efac", "#22c55e", "#15803d"];

function nodo(tag, attr = {}, testo) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attr)) n.setAttribute(k, v);
  if (testo !== undefined) n.textContent = testo;
  return n;
}
const attesa = ms => new Promise(r => setTimeout(r, ms));
const morbido = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
function anima(durata, passo) {
  return new Promise(fine => {
    const inizio = performance.now();
    const giro = ora => {
      const t = Math.min(1, (ora - inizio) / durata);
      passo(t);
      if (t < 1) requestAnimationFrame(giro); else fine();
    };
    requestAnimationFrame(giro);
  });
}
const curva = (a, b) => { const m = (a.x + b.x) / 2; return `M${a.x},${a.y} C${m},${a.y} ${m},${b.y} ${b.x},${b.y}`; };
function punto(a, b, t) {
  const m = (a.x + b.x) / 2, u = 1 - t;
  return { x: u ** 3 * a.x + 3 * u * u * t * m + 3 * u * t * t * m + t ** 3 * b.x,
           y: u ** 3 * a.y + 3 * u * u * t * a.y + 3 * u * t * t * b.y + t ** 3 * b.y };
}

export function disegnaPercorsi(box, dati, apri) {
  const colonne = dati.colonne, C = colonne.length;           // 6 colonne di domande, poi l'arrivo
  const COLORI_AREA = Object.fromEntries(colonne[0].porte.map((a, i) => [a, COLORI_AREE[i]]));
  const porteDi = [...colonne.map(c => c.porte), dati.arrivi];  // C+1 colonne di porte
  // persone: prima i profili d'esempio (sopra, nel disegno), poi la folla simulata
  const persone = [...dati.esempi.map(e => ({ ...e, esempio: true, porte: [...e.porte, e.arrivo] })),
                   ...dati.folla.map(f => ({ porte: [...f.porte, f.arrivo], aiuti: f.aiuti }))];
  const N = persone.length;
  const colX = k => (k === 0 ? X0 : X1 + (k - 1) * PASSO_X);    // k = 0 partenza, 1..C+1 colonne
  const altezzaMax = Math.max(...porteDi.map(p => N * UNITA + (p.length - 1) * GAP));
  const H = CIMA + altezzaMax + 34, MEZZO = CIMA + altezzaMax / 2;

  // posizioni: alla partenza tutti in un mucchio; in ogni colonna, dentro la porta, nell'ordine in cui arrivano
  // (così le linee di una porta non si incrociano fra loro, ma i fasci fra porte diverse sì)
  const ordine0 = persone.map((_, i) => i).sort((a, b) => persone[a].porte.join("|").localeCompare(persone[b].porte.join("|")));
  const pos = persone.map(() => []);
  ordine0.forEach((i, r) => { pos[i][0] = { x: X0, y: MEZZO + (r - N / 2) * .35 }; });
  const porte = [];  // { k, nome, y, h, membri }
  for (let k = 1; k <= C + 1; k++) {
    const nomi = porteDi[k - 1].filter(n => persone.some(p => p.porte[k - 1] === n));
    const totale = N * UNITA + (nomi.length - 1) * GAP;
    let y = MEZZO - totale / 2;
    for (const nome of nomi) {
      const membri = persone.map((_, i) => i).filter(i => persone[i].porte[k - 1] === nome)
        .sort((a, b) => pos[a][k - 1].y - pos[b][k - 1].y);
      membri.forEach((i, j) => { pos[i][k] = { x: colX(k), y: y + (j + .5) * UNITA }; });
      porte.push({ k, nome, y, h: membri.length * UNITA, membri });
      y += membri.length * UNITA + GAP;
    }
  }
  // i profili d'esempio, all'arrivo, escono a destra verso la loro etichetta, senza sovrapporsi
  const esempi = persone.map((p, i) => i).filter(i => persone[i].esempio).sort((a, b) => pos[a][C + 1].y - pos[b][C + 1].y);
  let ultimo = -Infinity;
  for (const i of esempi) {
    const y = Math.max(pos[i][C + 1].y, ultimo + 34);
    pos[i][C + 2] = { x: colX(C + 1) + USCITA, y };
    ultimo = y;
  }
  const scarto = Math.max(0, ultimo - (H - 24));  // se l'ultima etichetta esce in basso, si risale
  if (scarto) esempi.forEach(i => { pos[i][C + 2].y -= scarto; });

  const svg = nodo("svg", { viewBox: `0 0 ${W} ${H}`, class: "pf-svg", role: "img",
    "aria-label": L(`Percorsi di ${N} persone attraverso ${C} domande: ${dati.esempi.map(e => `${e.nome}, ${e.spettano} aiuti compatibili`).join("; ")}`,
      `Paths of ${N} people through ${C} questions: ${dati.esempi.map(e => `${e.nome}, ${e.spettano} compatible benefits`).join("; ")}`) });
  const pulsante = document.createElement("button");
  pulsante.type = "button"; pulsante.className = "pulsante primario pf-gioca";
  const legenda = document.createElement("div");
  legenda.className = "pf-legenda";
  legenda.append(...Object.entries(COLORI_AREA).map(([a, c]) => {
    const s = document.createElement("span"); s.innerHTML = `<i style="background:${c}"></i>${a}`; return s;
  }));
  const nota = document.createElement("p");
  nota.className = "pf-nota";
  const giornoFolla = dati.giorno_folla ? dati.giorno_folla.split("-").reverse().join("/") : "";
  nota.textContent = L(`Ogni linea è una persona: ${dati.folla.length} simulate (inventate, con proporzioni plausibili) e i ${dati.esempi.length} profili d'esempio, con la faccina. ` +
    `Il colore è l'area in cui vivono; all'arrivo, gli aiuti in vista (compatibili e possibili)${giornoFolla ? ` al ${giornoFolla}` : ""}. ` +
    "Passa sopra una porta per vedere chi ci passa, sopra una faccina per seguire la sua strada.",
    `Each line is a person: ${dati.folla.length} simulated (made up, with plausible proportions) and the ${dati.esempi.length} example profiles, with a face. ` +
    `The colour is the area where they live; at the finish, the benefits in sight (compatible and possible)${giornoFolla ? ` on ${giornoFolla}` : ""}. ` +
    "Hover over a gate to see who goes through it, over a face to follow its path.");
  const piede = document.createElement("div");
  piede.className = "pf-piede";
  piede.append(legenda, pulsante);
  box.replaceChildren(svg, piede, nota);  // nel documento subito: servono le misure del testo

  const defs = svg.appendChild(nodo("defs"));
  defs.innerHTML = `<filter id="pf-ombra" x="-40%" y="-40%" width="180%" height="180%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity=".25"/></filter>
    <linearGradient id="pf-banda" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#4f46e5" stop-opacity=".12"/><stop offset="1" stop-color="#06b6d4" stop-opacity=".03"/></linearGradient>`;

  // banda del passo in corso e intestazioni (numero, titolo, domanda)
  const banda = svg.appendChild(nodo("rect", { class: "pf-banda", x: -62, y: 4, width: 124, height: H - 8, rx: 16, fill: "url(#pf-banda)" }));
  const mettiBanda = x => { banda.style.transform = `translateX(${x}px)`; banda.classList.add("visibile"); };
  const testate = [{ x: X0 + 22, num: "▶", titolo: L("Partenza", "Start"), sotto: L(`${N} persone`, `${N} people`) },
    ...colonne.map((c, k) => ({ x: colX(k + 1), num: String(k + 1), titolo: c.nome, sotto: c.domanda })),
    { x: colX(C + 1), num: "★", titolo: L("Arrivo", "Finish"), sotto: L("aiuti in vista", "benefits in sight") }];
  const intest = testate.map(c => {
    const g = svg.appendChild(nodo("g", { class: "pf-colonna", transform: `translate(${c.x},0)` }));
    g.appendChild(nodo("circle", { cy: 20, r: 12, class: "pf-num-cerchio" }));
    g.appendChild(nodo("text", { y: 24.5, "text-anchor": "middle", class: "pf-num" }, c.num));
    g.appendChild(nodo("text", { y: 52, "text-anchor": "middle", class: "pf-titolo" }, c.titolo));
    g.appendChild(nodo("text", { y: 69, "text-anchor": "middle", class: "pf-sotto" }, c.sotto));
    return g;
  });
  svg.appendChild(nodo("line", { x1: 18, x2: W - 18, y1: 84, y2: 84, class: "pf-riga" }));

  // linee: un tratto per persona e colonna; la folla sottile e colorata per area, i profili d'esempio spessi
  const stratoFolla = svg.appendChild(nodo("g", { class: "pf-strato-folla" }));
  const stratoPorte = svg.appendChild(nodo("g"));
  const stratoEsempi = svg.appendChild(nodo("g"));
  const tratti = persone.map((p, i) => {
    const colore = p.esempio ? p.colore : COLORI_AREA[p.porte[0]] || "#64748b";
    const fino = p.esempio ? C + 2 : C + 1;
    return Array.from({ length: fino }, (_, k) => {
      const d = curva(pos[i][k], pos[i][k + 1]);
      const parti = p.esempio
        ? [stratoEsempi.appendChild(nodo("path", { d, class: "pf-alone-scia", stroke: colore })),
           stratoEsempi.appendChild(nodo("path", { d, class: "pf-scia-esempio", stroke: colore }))]
        : [stratoFolla.appendChild(nodo("path", { d, class: "pf-filo", stroke: colore }))];
      for (const s of parti) {
        const l = s.getTotalLength(); s.style.strokeDasharray = l; s.style.strokeDashoffset = l; s.dataset.l = l; s.dataset.i = i;
      }
      return parti;
    });
  });

  // porte: barre alte quanto le persone che ci passano, con nome e numero
  const barre = porte.map(pt => {
    const arrivo = pt.k === C + 1;
    const colore = pt.k === 1 ? COLORI_AREA[pt.nome] : arrivo ? COLORI_ARRIVO[dati.arrivi.indexOf(pt.nome)] : "#1e293b";
    const g = stratoPorte.appendChild(nodo("g", { class: "pf-porta", "data-k": pt.k }));
    const dentro = g.appendChild(nodo("g", { class: "pf-porta-dentro" }));
    dentro.appendChild(nodo("rect", { x: colX(pt.k) - 5, y: pt.y - 1, width: 10, height: pt.h + 2, rx: 4, fill: colore }));
    const t = dentro.appendChild(nodo("text", { x: colX(pt.k) + 11, y: pt.y + pt.h / 2 + 4, class: "pf-porta-nome" }));
    t.appendChild(nodo("tspan", {}, pt.nome));
    t.appendChild(nodo("tspan", { class: "pf-porta-num" }, ` ${pt.membri.length}`));
    g.appendChild(nodo("title", {}, `${colonne[pt.k - 1]?.nome || L("Arrivo", "Finish")}: ${pt.nome}, ${pt.membri.length} ${L("persone", "people")}`));
    g.addEventListener("mouseenter", () => evidenzia(new Set(pt.membri)));
    g.addEventListener("mouseleave", () => evidenzia(null));
    return g;
  });

  // puntini della folla e faccine dei profili d'esempio
  const puntini = persone.map((p, i) => p.esempio ? null
    : svg.appendChild(nodo("circle", { r: 2.4, class: "pf-puntino", fill: COLORI_AREA[p.porte[0]] || "#64748b" })));
  const facce = persone.map((p, i) => {
    if (!p.esempio) return null;
    const f = svg.appendChild(nodo("g", { class: "pf-faccina", tabindex: 0, "aria-label": p.nome }));
    f.appendChild(nodo("circle", { r: R + 6, fill: p.colore, class: "pf-alone" }));
    f.appendChild(nodo("circle", { r: R, fill: p.colore, class: "pf-disco" }));
    f.appendChild(nodo("text", { "text-anchor": "middle", y: 6, class: "pf-emoji" }, p.faccina || "🙂"));
    const b = f.appendChild(nodo("g", { class: "pf-badge", transform: "translate(14,11)" }));
    const dentro = b.appendChild(nodo("g", { class: "pf-badge-dentro" }));
    dentro.appendChild(nodo("rect", { x: -11, y: -8, width: 22, height: 15, rx: 7.5, stroke: p.colore }));
    const num = dentro.appendChild(nodo("text", { "text-anchor": "middle", y: 3 }, "0"));
    f.appendChild(nodo("title", {}, `${p.nome}: ${p.porte.join(" → ")}`));
    f.addEventListener("mouseenter", () => evidenzia(new Set([i])));
    f.addEventListener("mouseleave", () => evidenzia(null));
    f.addEventListener("click", () => apri(p.id));
    return { f, b: dentro, num, valore: 0 };
  });
  // etichette d'arrivo dei profili d'esempio: nome e aiuti compatibili; un clic apre il loro percorso guidato
  const arrivi = persone.map((p, i) => {
    if (!p.esempio) return null;
    const q = pos[i][C + 2];
    const a = svg.appendChild(nodo("g", { class: "pf-arrivo", transform: `translate(${q.x + R + 10},${q.y})`, tabindex: 0,
      role: "button", "aria-label": L(`Apri il percorso di ${p.nome}`, `Open ${p.nome}'s path`) }));
    const dentro = a.appendChild(nodo("g", { class: "pf-arrivo-dentro" }));
    dentro.appendChild(nodo("text", { y: -2, class: "pf-nome", fill: p.colore }, p.nome));
    const r = dentro.appendChild(nodo("text", { y: 13, class: "pf-totale" }));
    r.appendChild(nodo("tspan", { class: "pf-si" }, `✓ ${p.spettano}`));
    r.appendChild(nodo("tspan", {}, L(` compatibili · ${p.possibili} poss.`, ` compatible · ${p.possibili} poss.`)));
    a.addEventListener("click", () => apri(p.id));
    a.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); apri(p.id); } });
    a.addEventListener("mouseenter", () => evidenzia(new Set([i])));
    a.addEventListener("mouseleave", () => evidenzia(null));
    return a;
  });

  // evidenziare: le persone di una porta, o la strada di un profilo
  const tuttiTratti = tratti.flat(2);
  function evidenzia(scelti) {
    svg.classList.toggle("pf-fuoco", !!scelti);
    tuttiTratti.forEach(s => s.classList.toggle("pf-scelto", !!scelti && scelti.has(+s.dataset.i)));
    facce.forEach((f, i) => f && f.f.classList.toggle("pf-scelto", !!scelti && scelti.has(i)));
    arrivi.forEach((a, i) => a && a.classList.toggle("pf-scelto", !!scelti && scelti.has(i)));
  }

  const spostaPersona = (i, q) => {
    if (puntini[i]) { puntini[i].setAttribute("cx", q.x); puntini[i].setAttribute("cy", q.y); }
    else facce[i].f.setAttribute("transform", `translate(${q.x},${q.y})`);
  };
  function conta(i, v, subito = false) {
    const fc = facce[i]; if (!fc) return;
    const da = fc.valore; fc.valore = v;
    if (subito || da === v) { fc.num.textContent = v; return; }
    fc.b.classList.remove("pf-pop"); void fc.b.getBBox(); fc.b.classList.add("pf-pop");
    anima(550, e => { fc.num.textContent = Math.round(da + (v - da) * e); });
  }
  function festa(i) {
    const { x, y } = pos[i][C + 2], colore = persone[i].colore;
    const pezzi = Array.from({ length: 12 }, (_, j) => {
      const a = (j / 12) * Math.PI * 2, d = 24 + (j % 3) * 8;
      return { c: svg.appendChild(nodo("circle", { cx: x, cy: y, r: j % 2 ? 2.2 : 3.2, fill: j % 3 ? colore : "#facc15" })),
               dx: Math.cos(a) * d, dy: Math.sin(a) * d };
    });
    anima(750, t => { const e = 1 - Math.pow(1 - t, 3); pezzi.forEach(p => {
      p.c.setAttribute("cx", x + p.dx * e); p.c.setAttribute("cy", y + p.dy * e); p.c.style.opacity = 1 - t; }); })
      .then(() => pezzi.forEach(p => p.c.remove()));
  }

  // ritardo di ogni persona nel passo: la folla scorre, non si muove a blocco
  const ritardo = persone.map((_, i) => (ordine0.indexOf(i) / N) * SFASAMENTO);
  let corsa = 0;
  function azzera() {
    persone.forEach((_, i) => { spostaPersona(i, pos[i][0]); conta(i, 0, true); facce[i]?.b.classList.remove("pf-finale"); });
    tuttiTratti.forEach(s => { s.style.strokeDashoffset = s.dataset.l; });
    puntini.forEach(p => p && p.classList.remove("nascosto"));
    [...barre, ...arrivi.filter(Boolean)].forEach(e => e.classList.remove("visibile"));
    intest.forEach(t => t.classList.remove("attivo", "fatto"));
    banda.classList.remove("visibile");
    svg.classList.remove("in-viaggio", "finito");
  }
  function fine() {
    persone.forEach((p, i) => {
      spostaPersona(i, pos[i][p.esempio ? C + 2 : C + 1]);
      if (p.esempio) { conta(i, p.spettano, true); facce[i].b.classList.add("pf-finale"); }
    });
    tuttiTratti.forEach(s => { s.style.strokeDashoffset = 0; });
    puntini.forEach(p => p && p.classList.add("nascosto"));
    [...barre, ...arrivi.filter(Boolean)].forEach(e => e.classList.add("visibile"));
    intest.forEach((t, k) => { t.classList.toggle("attivo", k === C + 1); t.classList.toggle("fatto", k <= C); });
    mettiBanda(colX(C + 1)); svg.classList.add("finito");
    pulsante.textContent = L("↻ Rivedi i percorsi", "↻ Replay the paths");
  }
  async function passo(k, verso) {  // tutti dalla colonna k-1 alla k (i profili d'esempio anche nel tratto finale)
    const totale = DURATA + SFASAMENTO;
    svg.classList.add("in-viaggio");
    await anima(totale, t => persone.forEach((p, i) => {
      if (!verso(i)) return;
      const e = morbido(Math.min(1, Math.max(0, (t * totale - ritardo[i]) / DURATA)));
      spostaPersona(i, punto(pos[i][k - 1], pos[i][k], e));
      tratti[i][k - 1].forEach(s => { s.style.strokeDashoffset = s.dataset.l * (1 - e); });
    }));
    svg.classList.remove("in-viaggio");
  }
  async function gioca() {
    const mia = ++corsa;
    azzera();
    pulsante.textContent = L("Percorsi in corso…", "Paths in progress…");
    intest[0].classList.add("attivo"); mettiBanda(X0 + 22);
    await attesa(900);  // tutti insieme alla partenza
    for (let k = 1; k <= C + 1; k++) {
      if (mia !== corsa) return;
      intest.forEach((t, j) => { t.classList.toggle("attivo", j === k); t.classList.toggle("fatto", j < k); });
      mettiBanda(colX(k));
      barre.filter(b => +b.dataset.k === k).forEach(b => b.classList.add("visibile"));
      await passo(k, () => true);
      if (mia !== corsa) return;
      persone.forEach((p, i) => { if (p.esempio && k <= C) conta(i, p.in_vista[k - 1]); });
      await attesa(PAUSA);
    }
    // arrivo: la folla si posa sulle porte d'arrivo; i profili d'esempio escono verso la loro etichetta
    puntini.forEach(p => p && p.classList.add("nascosto"));
    await passo(C + 2, i => persone[i].esempio);
    for (const i of esempi) {
      if (mia !== corsa) return;
      conta(i, persone[i].spettano); facce[i].b.classList.add("pf-finale");
      arrivi[i].classList.add("visibile");
      festa(i);
      await attesa(200);
    }
    svg.classList.add("finito");
    pulsante.textContent = L("↻ Rivedi i percorsi", "↻ Replay the paths");
  }
  pulsante.addEventListener("click", gioca);

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { fine(); return; }
  azzera();
  pulsante.textContent = L("▶ Guarda i percorsi", "▶ Watch the paths");
  const osserva = new IntersectionObserver(voci => {
    if (voci.some(v => v.isIntersecting)) { osserva.disconnect(); gioca(); }
  }, { threshold: .4 });
  osserva.observe(box);  // la scheda, non il disegno: sul telefono il disegno è più largo dello schermo
}
