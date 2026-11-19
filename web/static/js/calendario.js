// Promemoria delle scadenze (docs/contesto.md, idea 3): un file .ics generato nel browser, niente passa dal server.

const testoIcs = s => String(s || "").replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\r?\n/g, "\\n");
const dataIcs = iso => iso.replaceAll("-", "");
const giornoDopo = iso => {
  const d = new Date(`${iso}T12:00:00`);
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
};

// Le righe di un .ics vanno spezzate a 75 caratteri (RFC 5545).
const piega = riga => riga.length <= 74 ? riga : riga.match(/.{1,74}/g).join("\r\n ");

export function scadenze(risultati, giorno) {
  // oltre due anni è la data segnaposto dell'open data (2050) per i bandi senza scadenza
  const limite = `${Number(giorno.slice(0, 4)) + 2}${giorno.slice(4)}`;
  return risultati.filter(r => r.chiusura && r.chiusura >= giorno && r.chiusura <= limite && r.stato !== "non idoneo");
}

export function scaricaIcs(risultati, giorno) {
  const voci = scadenze(risultati, giorno);
  const adesso = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  const righe = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//trova-bandi//demo//IT", "CALSCALE:GREGORIAN"];
  for (const r of voci) {
    righe.push("BEGIN:VEVENT",
      `UID:${r.id}@trova-bandi`,
      `DTSTAMP:${adesso}`,
      `DTSTART;VALUE=DATE:${dataIcs(r.chiusura)}`,
      `DTEND;VALUE=DATE:${dataIcs(giornoDopo(r.chiusura))}`,
      `SUMMARY:${testoIcs(`Scade: ${r.titolo}`)}`,
      `DESCRIPTION:${testoIcs(`${r.ente || ""}\nEsito su trova-bandi: ${r.stato}.\nControlla i requisiti sulla fonte ufficiale: ${r.link || ""}`)}`,
      r.link ? `URL:${r.link}` : null,
      "BEGIN:VALARM", "ACTION:DISPLAY", `DESCRIPTION:${testoIcs(`Mancano 3 giorni: ${r.titolo}`)}`, "TRIGGER:-P3D", "END:VALARM",
      "END:VEVENT");
  }
  righe.push("END:VCALENDAR");
  const testo = righe.filter(Boolean).map(piega).join("\r\n") + "\r\n";
  const url = URL.createObjectURL(new Blob([testo], { type: "text/calendar;charset=utf-8" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: "scadenze-trova-bandi.ics" });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return voci.length;
}
