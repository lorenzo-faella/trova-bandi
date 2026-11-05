# Da fare

Elenco unico delle cose aperte. Quando una voce è chiusa, si sposta in fondo con la data, oppure diventa una decisione in `decisioni.md`.
Tra parentesi: da dove viene la voce.

*Aggiornato il 5/11/2026.*

## Scadenze

- **Consegna** su Blackboard (codice, report di circa una pagina, materiale di supporto): ven 27/11, 23:59.
- **Presentazioni** (circa 10 minuti, va bene una demo live): 30/11, 2/12, 4/12.

## 1. Ramo persone

1. **Etichettare a mano i benefici assegnati** (`docs/etichettatura.md`, decisione 21). Edoardo: i 9 file in `data/gold/edo/`, senza LLM e senza guardare quelli di Lorenzo.
2. **Rivedere insieme i campi e le domande** (`docs/vocabolario-persone.md`, "da rivedere insieme"). Edoardo propone i campi che mancano (es. casa in affitto o di proprietà, studio). (decisione 22)
3. **Fonti oltre INPS**: Agenzia delle Entrate, ministeri, le 20 regioni, i comuni. Serve un piano con gli indirizzi da sorvegliare e come trovare i bandi nuovi su ognuno. (decisioni 16, 23, 25)
   - Il robots.txt dell'Agenzia delle Entrate non era leggibile nella prova del 29/10 (`docs/prova-download.md`): ricontrollare.
   - Un PDF comunale era una scansione: per questi serve l'OCR.
4. **Estrazione dei requisiti con l'LLM e sua misura** contro le etichette a mano (brief, task 4.3; estrattore in `pipeline/estrai.py`, misuratore in `pipeline/confronta.py`; manca l'esecuzione sui 15 benefici, dopo le etichette). È la misura chiave del progetto.
5. **Lista finale "da verificare"** con le citazioni, nella demo. (decisione 24)
6. **Agente di raccolta continua**: proposta del 29/10 in `docs/fattibilita-persone.md`, non ancora decisa. Da riprendere dopo il piano delle fonti.

## 2. Copertura

1. **Misurare la copertura regione per regione**: i nostri dati contro gli elenchi ufficiali. Serve un metodo; poi una misura sistematica su 1-2 regioni. (decisione 23)
2. **Leggere gli articoli del D.Lgs. 184/2025** sugli obblighi di pubblicazione (`docs/copertura-portale.md`, §1).
3. **Verifiche sui comuni** elencate nella decisione 25 ⚠: quanta parte passa dalla regione, fondi statali agli ambiti sociali, fondi propri dei comuni, livelli intermedi, aggiornamento della sezione trasparente.

## 3. Da decidere insieme

- **Professionisti con partita IVA:** in quale ramo? Sono persone fisiche, ma il portale li tratta come soggetti economici (124 bandi). Proposta: ramo persone con la domanda "hai una partita IVA?".
- **ISEE:** chiedere il numero, una fascia o proporre una stima. (`docs/vocabolario-persone.md`, scelta 3)
- **Stack dell'applicazione web** (framework, database): non deciso. (decisione 13)
- **"Quasi idoneo" per la sede operativa:** aprire una sede in un'altra regione è una strategia reale. (decisione 7 ⚠)
- **Dove vanno le correzioni manuali alle regole generate.** (decisione 4)
- **Licenza delle schede INPS**, da rileggere prima di rendere pubblico il repository. (decisione 16 ⚠)

## 4. Lavoro tecnico

- Tavola di raccordo ISTAT ATECO 2007 → 2025, così 78 bandi smettono di dare "mancano dati". (decisione 8 ⚠)
- Distribuzioni realistiche per le imprese fittizie: registro ISTAT ASIA ed elenchi ufficiali delle aree interne. (decisione 12 ⚠)
- Ripetere la misura del questionario con i requisiti estratti e con il ramo persone. (decisione 11)

## Chiuse

- 28/10: target esteso a persone fisiche e giuridiche (decisione 22).
- 28/10: prima verifica della copertura di incentivi.gov.it (`docs/copertura-portale.md`).
- 29/10: fattibilità dell'estrazione su 3 documenti reali (`docs/fattibilita-persone.md`) e del download automatico, 7 fonti su 8 (`docs/prova-download.md`).
- 29/10: topic inviato e approvato.
- 5/11: analisi dei concorrenti (`docs/competitor.md`) e brief corretto con i criteri e le scadenze reali del corso (Lorenzo).
- 5/11: fonte INPS, motore esteso alle persone, controllo delle citazioni (decisioni 16-21, Lorenzo).
