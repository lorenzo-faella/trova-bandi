import { t } from './i18n.js';
// Un unico insieme selezionabile con API e lista. Date giornaliere: nessun orario di chiusura inventato.
const testoIcs = s => String(s || '').replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
const dataIcs = iso => iso.replaceAll('-', '');
const giornoDopo = iso => {const d=new Date(`${iso}T00:00:00Z`);d.setUTCDate(d.getUTCDate()+1);return d.toISOString().slice(0,10);};
// RFC 5545: massimo 75 OTTETTI, inclusa la spaziatura di continuazione.
export function piega(riga) {
  const enc=new TextEncoder();let out='',linea='',byte=0;
  for(const c of riga){const n=enc.encode(c).length;if(byte+n>75){out+=linea+'\r\n';linea=' ';byte=1;}linea+=c;byte+=n;}
  return out+linea;
}
export function scadenze(risultati,giorno) {
  return risultati.filter(r=>r.calendario_ammesso === true && r.chiusura && r.chiusura>=giorno);
}
export function generaIcs(risultati,giorno) {
  const voci=scadenze(risultati,giorno);
  const stamp=new Date().toISOString().replace(/[-:]/g,'').slice(0,15)+'Z';
  const righe=['BEGIN:VCALENDAR','VERSION:2.0',`PRODID:-//MiSpetta//demo//${t('IT', 'EN')}`,'CALSCALE:GREGORIAN'];
  for(const r of voci) righe.push('BEGIN:VEVENT',`UID:${r.id}@mispetta`,`DTSTAMP:${stamp}`,
    `DTSTART;VALUE=DATE:${dataIcs(r.chiusura)}`,`DTEND;VALUE=DATE:${dataIcs(giornoDopo(r.chiusura))}`,
    `SUMMARY:${testoIcs(t(`Scade: ${r.titolo}`, `Deadline: ${r.titolo}`))}`,
    `DESCRIPTION:${testoIcs(`${r.ente || ''}\n${t('Controlla il bando ufficiale prima di fare domanda.', 'Check the official call before applying.')}\n${r.link || ''}`)}`,
    ...(r.link ? [`URL:${testoIcs(r.link)}`] : []),'BEGIN:VALARM','ACTION:DISPLAY','TRIGGER:-P3D',`DESCRIPTION:${testoIcs(t(`Tra tre giorni: ${r.titolo}`, `In three days: ${r.titolo}`))}`,'END:VALARM','END:VEVENT');
  return [...righe,'END:VCALENDAR'].map(piega).join('\r\n')+'\r\n';
}
export function scaricaIcs(risultati,giorno) {
  const testo=generaIcs(risultati,giorno);
  const url=URL.createObjectURL(new Blob([testo],{type:'text/calendar;charset=utf-8'}));
  const a=Object.assign(document.createElement('a'),{href:url,download:t('scadenze-mispetta.ics', 'mispetta-deadlines.ics')});document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(url),1000);return scadenze(risultati,giorno).length;
}
