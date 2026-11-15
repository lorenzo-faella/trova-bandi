# Test dell'estrazione

*Generato da `pipeline/confronta.py` il 2026-11-15: non modificare a mano.*

Regole estratte in `data/regole_estratte/gold`, confrontate con `data/gold/lorenzo` (9 benefici in comune).

| beneficio | condizioni giuste | precisione | richiamo | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | falsi sì | falsi no | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Assegno sociale | 4/4 | 100% | 100% | 1/1 | 100% | 0% | 0% | 0% | 2916 |
| Bonus asilo nido e forme di supporto presso la propria abitazione | 2/2 | 100% | 100% | 1/2 | 99% | 0% | 0% | 0% | 3952 |
| Congedo di paternità obbligatorio | 2/3 | 67% | 67% | 1/3 | 58% | 0% | 34% | 0% | 5000 |
| Contributo per sostenere le spese relative a sessioni di psicoterapia - Bonus psicologo | 2/2 | 100% | 100% | 1/2 | 100% | 0% | 0% | 0% | 2759 |
| DIS-COLL: indennità mensile di disoccupazione | 2/2 | 50% | 100% | 3/5 | 71% | 0% | 15% | 9% | 4026 |
| Indennità di congedo parentale per lavoratrici e lavoratori dipendenti | 3/4 | 60% | 75% | 3/2 | 71% | 0% | 0% | 24% | 3858 |
| Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO) | 1/3 | 50% | 33% | 9/10 | 72% | 0% | 24% | 0% | 3481 |
| Nuovo Bonus mamme 2026 | 2/3 | 40% | 67% | 3/3 | 32% | 0% | 33% | 0% | 4382 |
| Supporto per la Formazione e il Lavoro (SFL) | 7/7 | 58% | 100% | 6/6 | 87% | 0% | 5% | 3% | 3572 |
| **Totale** | **25/30** | **64%** | **83%** | | **74%** | **0%** | **14%** | **4%** | **33946** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** l'estrazione mette più riserve del riferimento (idoneo → idoneo salvo eccezioni → da verificare). **Falso sì:** l'estrazione dice idoneo, idoneo salvo eccezioni o da verificare, il riferimento non idoneo. **Falso no:** il contrario, ed è l'errore peggiore: la persona non controlla oltre.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Assegno sociale

- Nessuna differenza strutturale.

### Bonus asilo nido e forme di supporto presso la propria abitazione

- Nessuna differenza strutturale.

### Congedo di paternità obbligatorio

- In più (campo assente dal riferimento): `figlio vero`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`

### Contributo per sostenere le spese relative a sessioni di psicoterapia - Bonus psicologo

- Nessuna differenza strutturale.

### DIS-COLL: indennità mensile di disoccupazione

- In più (campo assente dal riferimento): `causa_fine_lavoro in ('dimissioni_giusta_causa', 'dimissioni_periodo_tutelato', 'risoluzione_consensuale_tutelata')`, `causa_fine_lavoro in ('fine_contratto', 'licenziamento')`

### Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- Sbagliate (campo giusto, valore diverso): `eta <= 17`
- Nel riferimento, scritte in modo diverso: `eta <= 13`
- In più (campo assente dal riferimento): `mesi_da_evento_figlio <= 167`
- Soglie che non compaiono nella scheda, da rileggere: `mesi_da_evento_figlio < 168`

### Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO)

- Sbagliate (campo giusto, valore diverso): `tipo_lavoro in ('autonomo', 'parasubordinato')`
- Nel riferimento, scritte in modo diverso: `tipo_lavoro in ('autonomo',)`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`

### Nuovo Bonus mamme 2026

- Sbagliate (campo giusto, valore diverso): `numero_figli <= 2`, `tipo_lavoro in ('autonomo', 'parasubordinato')`, `tipo_lavoro in ('autonomo',)`
- Nel riferimento, scritte in modo diverso: `tipo_lavoro in ('autonomo', 'dipendente')`
- Più sicura del riferimento in 1423 casi su 4382.

### Supporto per la Formazione e il Lavoro (SFL)

- Sbagliate (campo giusto, valore diverso): `eta >= 30`
- In più (campo assente dal riferimento): `causa_fine_lavoro in ('dimissioni_giusta_causa', 'fine_contratto', 'licenziamento', 'risoluzione_consensuale', 'risoluzione_consensuale_tutelata')`, `causa_fine_lavoro in ('dimissioni_periodo_tutelato',)`, `condizione_lavorativa in ('inattivo', 'occupato', 'pensionato', 'studente')`, `giorni_da_cessazione_lavoro >= 366`
- Soglie che non compaiono nella scheda, da rileggere: `giorni_da_cessazione_lavoro > 365`
