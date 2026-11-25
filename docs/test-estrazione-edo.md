# Test dell'estrazione

*Generato da `pipeline/confronta.py` il 2026-11-25: non modificare a mano.*

Regole estratte in `data/regole_estratte/gold`, confrontate con `data/gold/edo` (8 benefici in comune).

Anno di valutazione delle soglie annuali: non specificato; i vincoli annuali restano da verificare.

| beneficio | foglie coincidenti | precisione delle foglie | richiamo delle foglie | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | divergenze favorevoli | divergenze sfavorevoli | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Assegno ordinario di invalidità per persone con capacità lavorativa ridotta | 0/3 | n/d | 0% | 0/3 | 0% | 61% | 33% | 0% | 5000 |
| Carta europea della disabilità - Disability Card | 1/1 | 50% | 100% | 0/1 | 50% | 47% | 0% | 0% | 3733 |
| Centri estivi: contributi per minori fino a 14 anni | 1/1 | 50% | 100% | 1/2 | 87% | 0% | 0% | 10% | 4345 |
| Congedo di paternità obbligatorio | 2/3 | 67% | 67% | 0/3 | 4% | 60% | 28% | 0% | 5000 |
| Indennità di congedo parentale per lavoratrici e lavoratori dipendenti | 3/3 | 60% | 100% | 0/2 | 9% | 65% | 0% | 17% | 2055 |
| Indennità di discontinuità a favore dei lavoratori dello spettacolo | 1/3 | 25% | 33% | 0/6 | 2% | 60% | 7% | 18% | 4373 |
| Indennità di maternità/paternità per lavoratrici e lavoratori autonomi | 1/3 | 100% | 33% | 0/4 | 3% | 72% | 18% | 0% | 3807 |
| Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO) | 1/3 | 50% | 33% | 0/10 | 6% | 81% | 10% | 0% | 3206 |
| **Totale** | **10/20** | **53%** | **50%** | | **20%** | **54%** | **14%** | **5%** | **31519** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** più riserve rispetto al riferimento. **Divergenza favorevole:** estrazione idonea, salvo eccezioni o da verificare contro riferimento non idoneo; **sfavorevole:** il contrario. I contatori interni storici si chiamano falsi_si/falsi_no: senza adjudicazione questi non sono errori normativi dimostrati.
- Il riferimento umano non è condiviso e stabile: occorre leggere fonti complete e allegati e risolvere i disaccordi. Non è accuratezza sui cittadini; il complemento dell'accordo non è una percentuale di errori reali. Accordo fra LLM, coincidenza delle foglie e correttezza dell'esito sono misure distinte.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Assegno ordinario di invalidità per persone con capacità lavorativa ridotta

- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `disabile vero`, `tipo_lavoro in ('autonomo', 'dipendente')`

### Carta europea della disabilità - Disability Card

- In più (campo assente dal riferimento): `percentuale_invalidita >= 67`

### Centri estivi: contributi per minori fino a 14 anni

- In più (campo assente dal riferimento): `figlio vero`

### Congedo di paternità obbligatorio

- In più (campo assente dal riferimento): `figlio vero`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`

### Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- In più (campo assente dal riferimento): `eta <= 17`, `figlio vero`
- Soglie che non compaiono nella scheda, da rileggere: `mesi_da_evento_figlio < 168`

### Indennità di discontinuità a favore dei lavoratori dello spettacolo

- In più (campo assente dal riferimento): `anni_residenza_continuativa_italia >= 1`, `cittadinanza in ('altro_titolo', 'apolide', 'extra_ue_lungo_periodo', 'familiare_con_diritto_soggiorno', 'italiana', 'protezione_internazionale', 'ue')`, `residente_italia vero`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `tipo_lavoro in ('autonomo', 'dipendente')`

### Indennità di maternità/paternità per lavoratrici e lavoratori autonomi

- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `mesi_da_evento_figlio <= 2`

### Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO)

- Sbagliate (campo giusto, valore diverso): `tipo_lavoro in ('autonomo', 'parasubordinato')`
- Nel riferimento, scritte in modo diverso: `tipo_lavoro in ('autonomo',)`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`
