# trova-bandi

Progetto di Lorenzo Faella ed Edoardo Salvatore Russo per Software Engineering 20875, Bocconi. Consegna: 27 novembre 2026.

**Quali aiuti pubblici ti spettano?** In Italia bonus, contributi e bandi per persone e imprese sono migliaia, sparsi fra INPS, ministeri, Regioni, Comuni, Camere di commercio e finanziarie regionali, e molti non vengono chiesti da chi ne ha diritto (`docs/contesto.md`). trova-bandi raccoglie questi aiuti, ne trasforma i requisiti in regole controllabili e, con un questionario adattivo, dice a una persona o a un'impresa cosa può chiedere. Per ogni esito mostra la frase del bando che lo giustifica, con il link alla fonte.

## A che punto siamo

*Aggiornato al 24/11/2026, ramo `demo`. Numeri con data di valutazione 22/11 (quella della presentazione), calcolati da `statistiche("2026-11-22")` in `web/domande.py`. Le scelte sono in `docs/decisioni.md` (104 decisioni); le cose aperte in `docs/da-fare.md`.*

| Il progetto promette | Oggi | Manca |
|---|---|---|
| Persone e imprese | **Persone:** 340 regole, 16 scritte a mano (etichette e regole di riferimento) e 324 estratte con un LLM; 152 aperte o sempre attive. **Imprese:** 839 regole, 689 dall'open data di incentivi.gov.it e 150 estratte dai bandi che il portale non ha; 546 aperte | Revisione a mano delle 30 regole che la demo mostra più spesso (`docs/da-rivedere-a-mano.md`) |
| Raccolta automatica | 171 fonti (INPS, ministeri, Regioni, Comuni, agenzie per lo studio, la casa e il lavoro, Camere di commercio, finanziarie), 449 schede INPS, circa 2.400 documenti; robots.txt e pause rispettati; aggiornata il 22/11 | Portali che caricano gli elenchi in JavaScript (Veneto, Basilicata, Sardegna) o bloccano i programmi (Roma, Torino, Lazio): salvati a mano dove possibile |
| Estrazione dei requisiti in regole verificabili | Ogni regola estratta passa il controllo dello schema e della **citazione letterale** nel testo della fonte. Due estrazioni indipendenti degli stessi bandi concordano sugli esiti nell'**85%** dei casi (82 regole) e nel **94%** su un campione casuale di 40. Estrazione contro le etichette scritte a mano: 75% sui 9 benefici di Lorenzo | Misura dopo la seconda passata sulle etichette (convenzioni della decisione 67) |
| Questionario adattivo | Circa 15 domande (erano 26-33): prima quelle che decidono più aiuti, quelle di un solo bando solo se quel bando è già probabile. Alla fine "Sono possibili questi": una domanda sì/no per le condizioni aperte degli aiuti più vicini (decisioni 93-96) | Prova con persone vere |
| Citazione dietro ogni risposta | Ogni scheda mostra i requisiti, la frase del bando e il link; il report stampato si apre con le risposte date | Le imprese dell'open data hanno i soli filtri del portale, senza citazione |
| Copertura | Misurata in Lombardia e Sicilia: incentivi.gov.it da solo copre il 25% dei bandi lombardi per i privati (`docs/copertura-regioni.md`, decisione 54) | Una misura nazionale |

### Ultime novità (20-24/11)

- **Più aiuti per le persone** (decisioni 77-89): le etichette scritte a mano entrano nella demo (bonus nido, bonus psicologo, SFL, assegno sociale, congedi…); bonus luce e gas, Carta "Dedicata a te", detrazioni per l'affitto, Fondo prima casa, bandi dei grandi Comuni e DSU lombardi.
- **Imprese** (87-88): 150 bandi raccolti dai siti di Regioni, Camere e finanziarie, che il portale nazionale non ha.
- **Questionario più corto e verifiche finali** (93-96, 101): circa 15 domande; gli aiuti con una condizione già smentita dai dati non compaiono fra i possibili.
- **Rinvii al PDF del bando** (102-103): dalle pagine che annunciano un bando si scarica il PDF con i requisiti.
- **Controlli dell'audit** (83, 86, 90, 92): valori impossibili rifiutati, soglie e periodi di reddito corretti in 17 regole, date e doppioni sistemati (100). I dettagli sono in `docs/dettagli-tecnici.md`.
- **24/11** (decisione 104): i bandi dei Comuni contano solo nel comune dove si vive, si ha il domicilio o si studia; "inattivi" nei bandi comprende studenti e pensionati; profili d'esempio nuovi, con le risposte alle verifiche finali, e un'impresa.

## Come si usa

Python 3.12 o successivo.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
make dati test        # genera le regole delle imprese dall'open data, poi i test
make demo             # http://127.0.0.1:8000
```

Con una data fissa i bandi aperti e i risultati restano gli stessi, anche se la demo si apre giorni dopo:

```sh
TROVA_BANDI_GIORNO=2026-11-22 make demo
```

`make controlla` verifica schema e citazioni delle regole scritte a mano; `python -m pipeline.estrai_documenti controlla data/regole_estratte/documenti` quelle dei bandi. I testi dei bandi (`data/raw/documenti/`) non sono in git: le citazioni si controllano solo dopo averli riscaricati (`pipeline/fonti/`), e una pagina cambiata nel frattempo può non contenerle più.

## La demo

- **Due rami.** "Sono una persona" e "Ho un'impresa", sullo stesso motore.
- **Profili d'esempio.** Studente fuorisede, famiglia monoreddito, giovane in affitto, pensionata sola, negozio di quartiere: un clic riempie il questionario e mostra gli esiti (`web/profili_demo.yaml`).
- **Esiti** in linguaggio semplice: compatibile ("ti spetta"), possibile, serve una risposta, manca un solo requisito, non compatibile. Le regole estratte e non riviste hanno l'etichetta "estratta automaticamente".
- **Gruppi a parte**, chiusi: bandi di altre regioni o di altri Comuni, "non sappiamo dirlo", date da verificare, chiusi da poco.
- **Avviso ISEE** ("il tuo ISEE decide N benefici"), calendario delle scadenze scelte, report da stampare.
- Percorso per la presentazione: `docs/presentazione.md`.

## Come funziona

```
fonti (robots.txt) → documenti e schede INPS → smistamento persone / imprese / enti
  → estrazione dei requisiti (LLM, vocabolario chiuso) → controllo di schema e citazione → regole YAML
  → motore a tre valori (sì / no / non si sa) → questionario adattivo e verifiche finali → demo
```

- **Regole** (`schema/regola.schema.json`, vocabolario in `docs/vocabolario-persone.md`): ogni requisito è un campo del profilo con un operatore, oppure un requisito "non modellabile" con la spiegazione, e porta sempre la citazione del testo.
- **Motore** (`pipeline/motore.py`): logica a tre valori. Un dato che manca non esclude: lascia l'esito in sospeso e diventa una domanda.
- **L'LLM legge, non decide.** Serve a smistare i documenti e a estrarre i requisiti; l'esito lo calcola il motore, in modo deterministico e spiegabile.

## Misure

| misura | valore | dove |
|---|---|---|
| Citazioni trovate parola per parola nel testo | tutte le regole accettate (il controllo rifiuta le altre) | `pipeline.estrai_documenti controlla`, `make controlla` |
| Due estrazioni indipendenti, accordo sugli esiti | 85% su 82 regole; 94% su un campione casuale di 40 | `docs/doppia-estrazione.md`, decisione 75 |
| Estrazione contro etichette scritte a mano | 75% (9 benefici di Lorenzo); la misura completa dopo la seconda passata | `docs/test-estrazione*.md`, `docs/accordo-etichette.md` |
| Domande del questionario, 4 persone di prova | 14-15 | `docs/simulazione-2026-11-22.md` |
| Test automatici | 492 | `make test` |

## Limiti

- **Regole non riviste.** Quasi tutte le regole sono estratte e non rilette da una persona: la demo lo dice su ogni scheda. Una citazione vera prova che la frase c'è, non che la regola sia completa.
- **Condizioni non modellabili.** Contratto registrato, figlio al nido, iscrizione al centro per l'impiego, sesso: restano "da verificare" o diventano verifiche finali.
- **Copertura disomogenea.** Molti bandi in Lombardia, nessuno aperto in Basilicata; mancano i portali che non si lasciano leggere.
- **Non è un parere.** La demo dice cosa vale la pena chiedere e perché; l'ammissione, la graduatoria e il pagamento li decide l'ente.

## Da leggere

- `docs/decisioni.md`: tutte le scelte, con le alternative scartate.
- `docs/da-fare.md`: cosa resta, in ordine.
- `docs/report-bozza.md`: la bozza del report di una pagina.
- `docs/presentazione.md`: il percorso della presentazione.
- `docs/dettagli-tecnici.md`: validazioni, esportazioni, provenienza delle estrazioni, verifiche offline e audit del 20-21/11.
- `docs/contesto.md`: caro vita e aiuti non richiesti, con le fonti.

## Fonti

incentivi.gov.it (open data, IODL 2.0); ISTAT, elenco dei comuni (CC BY 4.0); INPS, schede e circolari; siti di Regioni, Comuni ed enti configurati in `data/fonti/`.
