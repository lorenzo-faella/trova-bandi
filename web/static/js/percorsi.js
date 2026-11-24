// Grafico dei percorsi (decisione 104): i profili d'esempio partono insieme e a ogni domanda chiave si dividono, chi
// risponde allo stesso modo resta nello stesso gruppo, fino ad arrivare ad aiuti diversi. SVG costruito a mano, nessuna
// libreria; con "riduci movimento" si mostra subito la fine. I dati vengono da /api/percorsi.
const NS = "http://www.w3.org/2000/svg";
const W = 1120, X0 = 78, PASSO_X = 128, X_ARRIVO = 800, RIGA = 84, CIMA = 104;
// distanza fra le faccine di uno stesso gruppo: piccola, così il gruppo si legge come uno solo e poi si apre a ventaglio
const SPAZIO = 13, SPAZIO_PARTENZA = 7, R = 19;
const CARTA_X = X_ARRIVO + 30, CARTA_L = W - CARTA_X - 12, CARTA_A = 66;
const DURATA = 1000, PAUSA = 650;

function nodo(tag, attr = {}, testo) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attr)) n.setAttribute(k, v);
  if (testo !== undefined) n.textContent = testo;
  return n;
}
const attesa = ms => new Promise(r => setTimeout(r, ms));
const morbido = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
function anima(durata, passo, curva = morbido) {
  return new Promise(fine => {
    const inizio = performance.now();
    const giro = ora => {
      const t = Math.min(1, (ora - inizio) / durata);
      passo(curva(t));
      if (t < 1) requestAnimationFrame(giro); else fine();
    };
    requestAnimationFrame(giro);
  });
}
// curva con tangenti orizzontali, come un ramo
const curva = (a, b) => { const m = (a.x + b.x) / 2; return `M${a.x},${a.y} C${m},${a.y} ${m},${b.y} ${b.x},${b.y}`; };
function punto(a, b, t) {
  const m = (a.x + b.x) / 2, u = 1 - t;
  return { x: u ** 3 * a.x + 3 * u * u * t * m + 3 * u * t * t * m + t ** 3 * b.x,
           y: u ** 3 * a.y + 3 * u * u * t * a.y + 3 * u * t * t * b.y + t ** 3 * b.y };
}
const taglia = (s, n) => (s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s);
const chiaro = (colore, alfa) => {  // "#rrggbb" -> rgba con trasparenza
  const v = parseInt(colore.slice(1), 16);
  return `rgba(${v >> 16},${(v >> 8) & 255},${v & 255},${alfa})`;
};

export function disegnaPercorsi(box, dati, apri) {
  const passi = dati.passi, domande = dati.domande || [], S = passi.length;
  // ordine finale: per risposte, così ogni gruppo resta contiguo e i rami non si incrociano
  const profili = [...dati.profili].sort((a, b) => a.risposte.join("|").localeCompare(b.risposte.join("|")))
    .map(p => ({ ...p, colore: p.colore || "#4f46e5" }));
  const n = profili.length, H = CIMA + n * RIGA + 8;
  const rigaY = i => CIMA + i * RIGA + RIGA / 2;
  const colX = k => X0 + k * PASSO_X;

  // posizioni: colonna 0 = partenza (tutti insieme), 1..S = dopo ogni passo, S+1 = arrivo
  const pos = profili.map(() => []), gruppi = [];
  for (let k = 0; k <= S; k++) {
    const perChiave = new Map();
    profili.forEach((p, i) => {
      const chiave = p.risposte.slice(0, k).join("|");
      if (!perChiave.has(chiave)) perChiave.set(chiave, []);
      perChiave.get(chiave).push(i);
    });
    for (const membri of perChiave.values()) {
      const cy = membri.reduce((s, i) => s + rigaY(i), 0) / membri.length;
      const passo_ = k === 0 ? SPAZIO_PARTENZA : SPAZIO;
      membri.forEach((i, j) => { pos[i][k] = { x: colX(k), y: cy + (j - (membri.length - 1) / 2) * passo_ }; });
      if (k > 0) gruppi.push({ k, membri, cy, testo: profili[membri[0]].risposte[k - 1],
                               y: cy - (membri.length - 1) / 2 * passo_ - R - 13 });
    }
  }
  profili.forEach((p, i) => { pos[i][S + 1] = { x: X_ARRIVO, y: rigaY(i) }; });

  const svg = nodo("svg", { viewBox: `0 0 ${W} ${H}`, class: "pf-svg", role: "img",
    "aria-label": `Percorsi di ${n} profili d'esempio: ${profili.map(p => `${p.nome}, ${p.spettano} aiuti compatibili`).join("; ")}` });
  const pulsante = document.createElement("button");
  pulsante.type = "button"; pulsante.className = "pulsante primario pf-gioca";
  const legenda = document.createElement("div");
  legenda.className = "pf-legenda";
  legenda.innerHTML = '<span><b class="pf-l-num">3</b> aiuti in vista con quello che ha detto finora</span>' +
    '<span><b class="pf-l-num pf-l-si">5</b> aiuti compatibili all\'arrivo</span>' +
    "<span>Passa sopra una faccina per seguire la sua strada · clic sulla scheda per aprire il suo percorso</span>";
  const piede = document.createElement("div");
  piede.className = "pf-piede";
  piede.append(legenda, pulsante);
  box.replaceChildren(svg, piede); // nel documento subito: le misure del testo servono a disegnare le etichette

  const defs = svg.appendChild(nodo("defs"));
  defs.innerHTML = `<filter id="pf-ombra" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0f172a" flood-opacity=".18"/></filter>
    <linearGradient id="pf-banda" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0" stop-color="#4f46e5" stop-opacity=".12"/><stop offset="1" stop-color="#06b6d4" stop-opacity=".03"/></linearGradient>`;

  // la banda che segue il passo in corso
  const banda = svg.appendChild(nodo("rect", { class: "pf-banda", x: -56, y: 4, width: 112, height: H - 8, rx: 16, fill: "url(#pf-banda)" }));
  const mettiBanda = (x, larghezza = 112) => {
    banda.style.transform = `translateX(${x}px)`;
    banda.setAttribute("width", larghezza); banda.setAttribute("x", -larghezza / 2);
    banda.classList.add("visibile");
  };

  // intestazioni: numero, titolo e domanda per ogni passo; guide verticali
  const colonne = [{ x: colX(0), num: "▶", titolo: "Partenza", sotto: "tutti insieme" },
    ...passi.map((t, k) => ({ x: colX(k + 1), num: String(k + 1), titolo: t, sotto: domande[k] || "" })),
    { x: CARTA_X + CARTA_L / 2, num: "★", titolo: "Arrivo", sotto: "gli aiuti trovati" }];
  const intest = colonne.map((c, k) => {
    if (k > 0 && k <= S) svg.appendChild(nodo("line", { x1: c.x, x2: c.x, y1: 84, y2: H - 6, class: "pf-guida" }));
    const g = svg.appendChild(nodo("g", { class: "pf-colonna", transform: `translate(${c.x},0)` }));
    g.appendChild(nodo("circle", { cy: 20, r: 12, class: "pf-num-cerchio" }));
    g.appendChild(nodo("text", { y: 24.5, "text-anchor": "middle", class: "pf-num" }, c.num));
    g.appendChild(nodo("text", { y: 52, "text-anchor": "middle", class: "pf-titolo" }, c.titolo));
    g.appendChild(nodo("text", { y: 69, "text-anchor": "middle", class: "pf-sotto" }, c.sotto));
    return g;
  });
  svg.appendChild(nodo("line", { x1: 18, x2: W - 18, y1: 82, y2: 82, class: "pf-riga" }));

  // scie: per ogni profilo e passo un alone largo e una linea, disegnati quando il passo parte
  const strato = svg.appendChild(nodo("g"));
  const scie = profili.map((p, i) => Array.from({ length: S + 1 }, (_, k) => {
    const d = curva(pos[i][k], pos[i][k + 1]);
    const parti = [strato.appendChild(nodo("path", { d, class: "pf-alone-scia pf-p", stroke: p.colore, "data-ids": ` ${p.id} ` })),
                   strato.appendChild(nodo("path", { d, class: "pf-scia pf-p", stroke: p.colore, "data-ids": ` ${p.id} ` }))];
    for (const s of parti) { const l = s.getTotalLength(); s.style.strokeDasharray = l; s.style.strokeDashoffset = l; s.dataset.l = l; }
    return parti;
  }));

  // stazioni ed etichette dei rami: la risposta del gruppo e quante persone ci camminano
  const idsDi = g => ` ${g.membri.map(i => profili[i].id).join(" ")} `;
  const stazioni = gruppi.map(g => {
    const solo = g.membri.length === 1 ? profili[g.membri[0]] : null;
    return svg.appendChild(nodo("circle", { cx: colX(g.k), cy: g.cy, r: 5, class: "pf-stazione pf-p",
      stroke: solo ? solo.colore : "#94a3b8", "data-k": g.k, "data-ids": idsDi(g) }));
  });
  const etichette = gruppi.map(g => {
    const solo = g.membri.length === 1 ? profili[g.membri[0]] : null;
    const e = svg.appendChild(nodo("g", { class: "pf-etichetta pf-p", transform: `translate(${colX(g.k)},${g.y})`,
      "data-k": g.k, "data-ids": idsDi(g) }));
    const dentro = e.appendChild(nodo("g", { class: "pf-etichetta-dentro" }));
    const t = dentro.appendChild(nodo("text", { "text-anchor": "middle", y: 4 }));
    t.appendChild(nodo("tspan", {}, taglia(g.testo, 21)));
    if (!solo) t.appendChild(nodo("tspan", { class: "pf-quanti" }, ` · ${g.membri.length}`));
    const larghezza = Math.max(44, t.getComputedTextLength() + 18);
    dentro.insertBefore(nodo("rect", { x: -larghezza / 2, y: -11, width: larghezza, height: 22, rx: 11,
      fill: solo ? chiaro(solo.colore, .1) : "#fff", stroke: solo ? chiaro(solo.colore, .55) : "#e2e8f0" }), t);
    return e;
  });

  // arrivi: una scheda per profilo, con aiuti compatibili e i primi nomi; un clic apre il suo percorso guidato
  const arrivi = profili.map((p, i) => {
    const a = svg.appendChild(nodo("g", { class: "pf-arrivo pf-p", transform: `translate(${CARTA_X},${rigaY(i) - CARTA_A / 2})`,
      tabindex: 0, role: "button", "aria-label": `Apri il percorso di ${p.nome}`, "data-ids": ` ${p.id} ` }));
    const dentro = a.appendChild(nodo("g", { class: "pf-arrivo-dentro" }));
    dentro.appendChild(nodo("rect", { width: CARTA_L, height: CARTA_A, rx: 12, class: "pf-carta", stroke: chiaro(p.colore, .45) }));
    dentro.appendChild(nodo("rect", { width: 5, height: CARTA_A - 16, y: 8, x: 0, rx: 2.5, fill: p.colore }));
    dentro.appendChild(nodo("text", { x: 16, y: 22, class: "pf-nome", fill: p.colore }, p.nome));
    if (p.possibili) dentro.appendChild(nodo("text", { x: CARTA_L - 12, y: 22, class: "pf-possibili", "text-anchor": "end" },
      `${p.possibili} ${p.possibili === 1 ? "possibile" : "possibili"}`));
    // sotto: il gettone verde con gli aiuti compatibili, poi i primi nomi e "+N" per gli altri
    let x = 16, nomi = 0;
    const gettone = (testo, si, riserva = 0) => {  // false se non ci sta (lasciando `riserva` px per il "+N")
      const g = dentro.appendChild(nodo("g", { transform: `translate(${x},35)` }));
      const tt = g.appendChild(nodo("text", { x: 8, y: 14, class: si ? "pf-gettone-testo pf-gettone-si" : "pf-gettone-testo" }, testo));
      const l = tt.getComputedTextLength() + 16;
      if (x + l + riserva > CARTA_L - 8) { g.remove(); return false; }
      g.insertBefore(nodo("rect", { width: l, height: 21, rx: 10.5, fill: si ? "#16a34a" : chiaro(p.colore, .1) }), tt);
      x += l + 6;
      return true;
    };
    gettone(`✓ ${p.spettano} ${p.spettano === 1 ? "compatibile" : "compatibili"}`, true);
    for (const t of p.esempi.slice(0, 2)) {  // il nome si accorcia finché ci sta, lasciando posto al "+N"
      const riserva = p.spettano > nomi + 1 ? 34 : 0;
      if (![19, 15, 12].some(n => gettone(taglia(t, n), false, riserva))) break;
      nomi++;
    }
    if (p.spettano > nomi && nomi) gettone(`+${p.spettano - nomi}`, false);
    const vai = () => apri(p.id);
    a.addEventListener("click", vai);
    a.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); vai(); } });
    return a;
  });

  // faccine: alone che pulsa in cammino, emoji, contatore degli aiuti in vista
  const facce = profili.map((p, i) => {
    const f = svg.appendChild(nodo("g", { class: "pf-faccina pf-p", "data-ids": ` ${p.id} `, tabindex: 0, "aria-label": p.nome }));
    f.appendChild(nodo("circle", { r: R + 7, fill: p.colore, class: "pf-alone" }));
    f.appendChild(nodo("circle", { r: R, fill: p.colore, class: "pf-disco" }));
    f.appendChild(nodo("text", { "text-anchor": "middle", y: 8, class: "pf-emoji" }, p.faccina || "🙂"));
    const b = f.appendChild(nodo("g", { class: "pf-badge", transform: "translate(18,14)" }));
    const dentro = b.appendChild(nodo("g", { class: "pf-badge-dentro" }));
    dentro.appendChild(nodo("rect", { x: -12, y: -9, width: 24, height: 17, rx: 8.5, stroke: p.colore }));
    const num = dentro.appendChild(nodo("text", { "text-anchor": "middle", y: 3.5 }, "0"));
    f.appendChild(nodo("title", {}, `${p.nome}: ${p.risposte.join(" → ")}`));
    return { f, b: dentro, num, valore: 0, q: pos[i][0] };
  });
  const sposta = (i, q) => { facce[i].q = q; facce[i].f.setAttribute("transform", `translate(${q.x},${q.y})`); };

  // contatore: conta fino al numero nuovo; se sale, un "+N" verde vola su
  function conta(i, v, subito = false) {
    const fc = facce[i], da = fc.valore;
    fc.valore = v;
    if (subito || da === v) { fc.num.textContent = v; return; }
    fc.b.classList.remove("pf-pop"); void fc.b.getBBox(); fc.b.classList.add("pf-pop");
    anima(600, e => { fc.num.textContent = Math.round(da + (v - da) * e); }, t => t);
    if (v > da) {
      const piu = svg.appendChild(nodo("text", { x: fc.q.x + 18, y: fc.q.y - 16, class: "pf-piu", "text-anchor": "middle" }, `+${v - da}`));
      setTimeout(() => piu.remove(), 1300);
    }
  }
  // coriandoli all'arrivo
  function festa(i) {
    const { x, y } = pos[i][S + 1], colore = profili[i].colore;
    const pezzi = Array.from({ length: 12 }, (_, j) => {
      const a = (j / 12) * Math.PI * 2, d = 30 + (j % 3) * 9;
      return { c: svg.appendChild(nodo("circle", { cx: x, cy: y, r: j % 2 ? 2.6 : 3.6, fill: j % 3 ? colore : "#facc15" })),
               dx: Math.cos(a) * d, dy: Math.sin(a) * d };
    });
    anima(800, e => pezzi.forEach(p => {
      p.c.setAttribute("cx", x + p.dx * e); p.c.setAttribute("cy", y + p.dy * e); p.c.style.opacity = 1 - e;
    }), t => 1 - Math.pow(1 - t, 3)).then(() => pezzi.forEach(p => p.c.remove()));
  }

  // seguire una strada: passando sopra una faccina o una scheda si vede solo il suo percorso
  const perProfilo = [...svg.querySelectorAll(".pf-p")];
  const evidenzia = id => {
    svg.classList.toggle("pf-fuoco", !!id);
    perProfilo.forEach(e => e.classList.toggle("pf-scelto", !!id && e.dataset.ids.includes(` ${id} `)));
  };
  profili.forEach((p, i) => [facce[i].f, arrivi[i]].forEach(e => {
    e.addEventListener("mouseenter", () => evidenzia(p.id));
    e.addEventListener("mouseleave", () => evidenzia(null));
    e.addEventListener("focus", () => evidenzia(p.id));
    e.addEventListener("blur", () => evidenzia(null));
  }));

  let corsa = 0;
  function azzera() {
    profili.forEach((_, i) => { sposta(i, pos[i][0]); conta(i, 0, true); facce[i].b.classList.remove("pf-finale"); });
    scie.flat(2).forEach(s => { s.style.strokeDashoffset = s.dataset.l; });
    [...etichette, ...stazioni, ...arrivi].forEach(e => e.classList.remove("visibile"));
    intest.forEach(t => t.classList.remove("attivo", "fatto"));
    banda.classList.remove("visibile");
    svg.classList.remove("in-viaggio");
  }
  function fine() {
    profili.forEach((p, i) => { sposta(i, pos[i][S + 1]); conta(i, p.spettano, true); facce[i].b.classList.add("pf-finale"); });
    scie.flat(2).forEach(s => { s.style.strokeDashoffset = 0; });
    [...etichette, ...stazioni, ...arrivi].forEach(e => e.classList.add("visibile"));
    intest.forEach((t, k) => { t.classList.toggle("attivo", k === S + 1); t.classList.toggle("fatto", k <= S); });
    mettiBanda(CARTA_X + CARTA_L / 2, CARTA_L + 24);
    pulsante.textContent = "↻ Rivedi i percorsi";
  }
  async function gioca() {
    const mia = ++corsa;
    azzera();
    pulsante.textContent = "Percorsi in corso…";
    intest[0].classList.add("attivo"); mettiBanda(colX(0));
    await attesa(800); // un attimo fermi alla partenza, tutti insieme
    for (let k = 1; k <= S + 1; k++) {
      if (mia !== corsa) return;
      intest.forEach((t, j) => { t.classList.toggle("attivo", j === k); t.classList.toggle("fatto", j < k); });
      mettiBanda(k <= S ? colX(k) : CARTA_X + CARTA_L / 2, k <= S ? 112 : CARTA_L + 24);
      svg.classList.add("in-viaggio");
      await anima(DURATA, e => profili.forEach((_, i) => {
        sposta(i, punto(pos[i][k - 1], pos[i][k], e));
        scie[i][k - 1].forEach(s => { s.style.strokeDashoffset = s.dataset.l * (1 - e); });
      }));
      svg.classList.remove("in-viaggio");
      if (mia !== corsa) return;
      if (k <= S) {
        [...etichette, ...stazioni].filter(e => +e.dataset.k === k).forEach(e => e.classList.add("visibile"));
        profili.forEach((p, i) => conta(i, p.in_vista[k - 1]));
        await attesa(PAUSA);
      }
    }
    // arrivo: le schede una dopo l'altra, con i coriandoli
    for (const [i, p] of profili.entries()) {
      if (mia !== corsa) return;
      conta(i, p.spettano); facce[i].b.classList.add("pf-finale");
      arrivi[i].classList.add("visibile");
      festa(i);
      await attesa(220);
    }
    pulsante.textContent = "↻ Rivedi i percorsi";
  }
  pulsante.addEventListener("click", gioca);

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { fine(); return; }
  azzera();
  pulsante.textContent = "▶ Guarda i percorsi";
  // parte da solo la prima volta che il grafico è ben visibile
  const osserva = new IntersectionObserver(voci => {
    if (voci.some(v => v.isIntersecting)) { osserva.disconnect(); gioca(); }
  }, { threshold: .5 });
  osserva.observe(box); // la scheda, non il disegno: sul telefono il disegno è più largo dello schermo
}
