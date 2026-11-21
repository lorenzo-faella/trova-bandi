// Modifiche locali: nessuna persistenza. Una risposta indipendente resta nel profilo.
export const NON_SO = 'non lo so';
const uguali = (a, b) => JSON.stringify(a) === JSON.stringify(b);
export function aggiornaProfilo(prima, scrivi, dipendenze = {}) {
  const p = structuredClone(prima);
  scrivi(p);
  const cambiati = new Set(Object.keys(p).filter(k => !uguali(p[k], prima[k])));
  for (const [regione, comune] of [['regione', 'comune'], ['regione_domicilio', 'comune_domicilio']]) {
    if (cambiati.has(regione) && !cambiati.has(comune)) delete p[comune];
  }
  if (cambiati.has('comune_ateneo') || cambiati.has('regione_ateneo')) {
    delete p.provincia_ateneo;
  }
  if (cambiati.has('nucleo')) {
    delete p.numero_figli; delete p.numero_componenti; delete p.eta;
    if (Array.isArray(p.nucleo)) p.nucleo.forEach((c,i)=>{
      if (c.figlio !== prima.nucleo?.[i]?.figlio && c.figlio !== true) delete c.figlio_a_carico;
    });
    // Il valore individuale di disabilità è l'unico controllo per "Tu".
    if (Array.isArray(p.nucleo) && p.disabile !== undefined) p.nucleo[0].disabile = p.disabile;
  }
  if (cambiati.has('disabile') && Array.isArray(p.nucleo)) p.nucleo[0].disabile = p.disabile;
  if (cambiati.has('domicilio_diverso') && p.domicilio_diverso !== true) {
    delete p.regione_domicilio; delete p.comune_domicilio;
  }
  // Le condizioni complete sono inviate dal servizio: nessuna inferenza da una domanda nascosta.
  let diNuovo = true;
  while (diNuovo) {
    diNuovo = false;
    for (const [campo, condizioni] of Object.entries(dipendenze)) {
      if (campo.startsWith('nucleo.') || !(campo in p)) continue;
      if (Object.entries(condizioni).some(([k, attesa]) => {
        if (!cambiati.has(k)) return false;
        const v = p[k];
        if (v === NON_SO || v === undefined) return true;
        if (Array.isArray(attesa)) return !(Array.isArray(v) ? v : [v]).some(x => attesa.includes(x));
        if (typeof attesa === 'boolean') return v !== attesa;
        return Object.entries(attesa).some(([op, n]) => !({'>=': v >= n, '<=': v <= n, '>': v > n, '<': v < n}[op]));
      })) { delete p[campo]; cambiati.add(campo); diNuovo = true; }
    }
  }
  return p;
}
