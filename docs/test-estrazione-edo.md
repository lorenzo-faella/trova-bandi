# Test dell'estrazione

*Generato da `pipeline/confronta.py` il 2026-11-17: non modificare a mano.*

Regole estratte in `data/regole_estratte/gold`, confrontate con `data/gold/edo` (8 benefici in comune).

| beneficio | condizioni giuste | precisione | richiamo | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | falsi sì | falsi no | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Assegno ordinario di invalidità per persone con capacità lavorativa ridotta | 0/2 | n/d | 0% | 0/3 | 0% | 50% | 45% | 0% | 5000 |
| Carta europea della disabilità - Disability Card | 1/1 | 50% | 100% | 0/1 | 50% | 47% | 0% | 0% | 3733 |
| Centri estivi: contributi per minori fino a 14 anni | 1/1 | 50% | 100% | 1/2 | 87% | 0% | 0% | 10% | 4345 |
| Congedo di paternità obbligatorio | 1/3 | 33% | 33% | 1/3 | 56% | 0% | 32% | 0% | 5000 |
| Indennità di congedo parentale per lavoratrici e lavoratori dipendenti | 2/3 | 40% | 67% | 0/2 | 6% | 53% | 6% | 21% | 2362 |
| Indennità di discontinuità a favore dei lavoratori dello spettacolo | 0/2 | 0% | 0% | 1/6 | 50% | 0% | 10% | 26% | 4782 |
| Indennità di maternità/paternità per lavoratrici e lavoratori autonomi | 0/3 | 0% | 0% | 2/4 | 57% | 0% | 25% | 7% | 4517 |
| Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO) | 0/1 | 0% | 0% | 3/10 | 71% | 0% | 0% | 20% | 4256 |
| **Totale** | **5/16** | **26%** | **31%** | | **49%** | **16%** | **17%** | **10%** | **33995** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** l'estrazione mette più riserve del riferimento (idoneo → idoneo salvo eccezioni → da verificare). **Falso sì:** l'estrazione dice idoneo, idoneo salvo eccezioni o da verificare, il riferimento non idoneo. **Falso no:** il contrario, ed è l'errore peggiore: la persona non controlla oltre.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Assegno ordinario di invalidità per persone con capacità lavorativa ridotta

- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `disabile vero`

### Carta europea della disabilità - Disability Card

- In più (campo assente dal riferimento): `percentuale_invalidita >= 67`

### Centri estivi: contributi per minori fino a 14 anni

- In più (campo assente dal riferimento): `figlio vero`

### Congedo di paternità obbligatorio

- In più (campo assente dal riferimento): `figlio vero`, `tipo_lavoro in ('dipendente',)`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `lavora_in_italia vero`

### Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- In più (campo assente dal riferimento): `eta <= 17`, `figlio vero`, `tipo_lavoro in ('dipendente',)`
- Mancate (campo assente dall'estrazione): `lavora_in_italia vero`
- Soglie che non compaiono nella scheda, da rileggere: `mesi_da_evento_figlio < 168`

### Indennità di discontinuità a favore dei lavoratori dello spettacolo

- In più (campo assente dal riferimento): `anni_residenza_continuativa_italia >= 1`, `cittadinanza in ('altro_titolo', 'apolide', 'extra_ue_lungo_periodo', 'familiare_con_diritto_soggiorno', 'italiana', 'protezione_internazionale', 'ue')`, `reddito_richiedente <= 35000`, `residente_italia vero`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `lavora_in_italia vero`

### Indennità di maternità/paternità per lavoratrici e lavoratori autonomi

- In più (campo assente dal riferimento): `tipo_lavoro in ('autonomo',)`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`, `lavora_in_italia vero`, `mesi_da_evento_figlio <= 2`

### Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO)

- In più (campo assente dal riferimento): `reddito_richiedente <= 12000`, `tipo_lavoro in ('autonomo', 'parasubordinato')`
- Mancate (campo assente dall'estrazione): `condizione_lavorativa in ('occupato',)`
