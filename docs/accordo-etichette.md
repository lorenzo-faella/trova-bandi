# Accordo tra etichette

*Generato da `pipeline/confronta.py` il 2026-11-15: non modificare a mano.*

Regole in `data/gold/edo`, confrontate con `data/gold/lorenzo` (3 benefici in comune).

| beneficio | condizioni giuste | precisione | richiamo | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | falsi sì | falsi no | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Congedo di paternità obbligatorio | 2/3 | 67% | 67% | 1/1 | 68% | 0% | 13% | 13% | 3577 |
| Indennità di congedo parentale per lavoratrici e lavoratori dipendenti | 1/4 | 33% | 25% | 3/0 | 3% | 0% | 8% | 15% | 4426 |
| Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO) | 1/3 | 100% | 33% | 9/3 | 61% | 0% | 33% | 0% | 4047 |
| **Totale** | **4/10** | **57%** | **40%** | | **42%** | **0%** | **18%** | **9%** | **12050** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** l'estrazione mette più riserve del riferimento (idoneo → idoneo salvo eccezioni → da verificare). **Falso sì:** l'estrazione dice idoneo, idoneo salvo eccezioni o da verificare, il riferimento non idoneo. **Falso no:** il contrario, ed è l'errore peggiore: la persona non controlla oltre.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Congedo di paternità obbligatorio

- In più (campo assente dal riferimento): `lavora_in_italia vero`
- Mancate (campo assente dall'estrazione): `tipo_lavoro in ('dipendente',)`

### Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- In più (campo assente dal riferimento): `lavora_in_italia vero`, `mesi_da_evento_figlio <= 167`
- Mancate (campo assente dall'estrazione): `eta <= 13`, `figlio vero`, `tipo_lavoro in ('dipendente',)`
- Soglie che non compaiono nella scheda, da rileggere: `mesi_da_evento_figlio < 168`
- Più sicura del riferimento in 2710 casi su 4426.

### Indennità Straordinaria di Continuità Reddituale e Operativa (ISCRO)

- Mancate (campo assente dall'estrazione): `reddito_richiedente <= 12000`, `tipo_lavoro in ('autonomo',)`
