# Test dell'estrazione

*Generato da `pipeline/confronta.py` il 2026-11-05: non modificare a mano.*

Regole estratte in `data/regole_estratte/sviluppo`, confrontate con `data/regole_persone`.

**Non è la misura finale.** I 5 benefici di sviluppo hanno un riferimento scritto da Claude e sono serviti a provare l'estrattore: vedi `docs/decisioni.md`, decisione 29. La misura vera sarà sulle etichette a mano in `data/gold/`.

| beneficio | condizioni giuste | precisione | richiamo | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | falsi sì | falsi no | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Assegno di Inclusione (ADI) | 11/11 | 73% | 100% | 3/11 | 89% | 0% | 3% | 1% | 4327 |
| Assegno di maternità dello Stato | 3/3 | 100% | 100% | 2/5 | 100% | 0% | 0% | 0% | 3322 |
| Assegno unico e universale per i figli a carico | 8/10 | 89% | 80% | 2/2 | 73% | 25% | 0% | 0% | 3676 |
| Bonus nuovi nati | 2/2 | 67% | 100% | 1/1 | 75% | 0% | 0% | 19% | 3375 |
| NASpI: indennità mensile di disoccupazione | 5/5 | 100% | 100% | 2/2 | 100% | 0% | 0% | 0% | 3174 |
| **Totale** | **29/31** | **83%** | **94%** | | **87%** | **5%** | **1%** | **4%** | **17874** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** il riferimento dice idoneo, l'estrazione da verificare. **Falso sì:** l'estrazione dice idoneo o da verificare, il riferimento non idoneo. **Falso no:** il contrario, ed è l'errore peggiore: la persona non controlla oltre.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Assegno di Inclusione (ADI)

- Sbagliate (campo giusto, valore diverso): `permesso_casi_speciali falso`
- In più (campo assente dal riferimento): `causa_fine_lavoro in ('dimissioni_giusta_causa', 'fine_contratto', 'licenziamento', 'risoluzione_consensuale_tutelata')`, `condizione_lavorativa in ('inattivo', 'occupato', 'pensionato', 'studente')`, `residente_italia vero`

### Assegno di maternità dello Stato

- Nessuna differenza strutturale.

### Assegno unico e universale per i figli a carico

- Sbagliate (campo giusto, valore diverso): `eta <= 20`
- Nel riferimento, scritte in modo diverso: `eta tra (18, 20)`
- Mancate (campo assente dall'estrazione): `cittadinanza in ('italiana', 'ue')`
- Soglie che non compaiono nella scheda, da rileggere: `eta < 18`

### Bonus nuovi nati

- In più (campo assente dal riferimento): `eta <= 17`
- Soglie che non compaiono nella scheda, da rileggere: `eta < 18`

### NASpI: indennità mensile di disoccupazione

- Nessuna differenza strutturale.
