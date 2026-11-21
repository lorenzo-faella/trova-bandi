# Accordo tra etichette

*Generato da `pipeline/confronta.py` il 2026-11-21: non modificare a mano.*

Regole in `data/gold/edo`, confrontate con `data/gold/lorenzo` (3 benefici in comune).

| beneficio | foglie coincidenti | precisione delle foglie | richiamo delle foglie | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | divergenze favorevoli | divergenze sfavorevoli | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Congedo di paternità obbligatorio | 3/3 | 100% | 100% | 1/0 | 10% | 0% | 0% | 0% | 3085 |
| Indennità di congedo parentale per lavoratrici e lavoratori dipendenti | 2/4 | 67% | 50% | 3/0 | 5% | 0% | 0% | 16% | 4154 |
| Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO) | 3/3 | 100% | 100% | 9/0 | 9% | 0% | 0% | 0% | 2985 |
| **Totale** | **8/10** | **89%** | **80%** | | **8%** | **0%** | **0%** | **7%** | **10224** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** più riserve rispetto al riferimento. **Divergenza favorevole:** estrazione idonea, salvo eccezioni o da verificare contro riferimento non idoneo; **sfavorevole:** il contrario. I contatori interni storici si chiamano falsi_si/falsi_no: senza adjudicazione questi non sono errori normativi dimostrati.
- Il riferimento umano non è condiviso e stabile: occorre leggere fonti complete e allegati e risolvere i disaccordi. Non è accuratezza sui cittadini; il complemento dell'accordo non è una percentuale di errori reali. Accordo fra LLM, coincidenza delle foglie e correttezza dell'esito sono misure distinte.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Congedo di paternità obbligatorio

- Più sicura del riferimento in 2788 casi su 3085.

### Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- In più (campo assente dal riferimento): `mesi_da_evento_figlio <= 167`
- Mancate (campo assente dall'estrazione): `eta <= 13`, `figlio vero`
- Soglie che non compaiono nella scheda, da rileggere: `mesi_da_evento_figlio < 168`
- Più sicura del riferimento in 2883 casi su 4154.

### Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO)

- Più sicura del riferimento in 2714 casi su 2985.
