# Due estrazioni indipendenti degli stessi bandi

*Generato da `pipeline/confronta.py` il 2026-11-17: non modificare a mano.*

Regole estratte in `data/regole_estratte/seconda-estrazione`, confrontate con `data/regole_estratte/documenti` (21 benefici in comune).

| beneficio | condizioni giuste | precisione | richiamo | non modellabili (rif./estr.) | accordo sugli esiti | più cauta | falsi sì | falsi no | casi non banali |
|---|---|---|---|---|---|---|---|---|---|
| Borse di studio | 3/4 | 100% | 75% | 7/6 | 97% | 0% | 0% | 0% | 3218 |
| Bando di concorso per l’assegnazione di Borse di studio e altri servizi per il diritto allo studio universitario a.a. 2026/2027 | 7/7 | 100% | 100% | 15/13 | 100% | 0% | 0% | 0% | 4054 |
| Bando per la concessione di un assegno di cura forfettario a studenti universitari affetti da disabilità gravissime iscritti presso gli Istituti Universitari con sede in Umbria per l’a.a. 2026-2027 | 3/3 | 100% | 100% | 4/5 | 100% | 0% | 0% | 0% | 2576 |
| BANDO BORSE DI STUDIO A.A. 2026/2027 | 4/5 | 100% | 80% | 6/6 | 97% | 0% | 0% | 0% | 3506 |
| Borsa di Studio Universitaria | 4/5 | 80% | 80% | 9/8 | 97% | 0% | 0% | 0% | 3533 |
| Bando Boves (CN) | 8/8 | 100% | 100% | 6/4 | 50% | 0% | 0% | 42% | 4440 |
| Bando straordinario per l’assegnazione di contributi sulla spesa per le utenze domestiche di residenza a supporto del caro energia | 2/3 | 100% | 67% | 4/4 | 97% | 0% | 0% | 0% | 3303 |
| Contributi economici a familiari delle persone ospiti, o agli stessi ospiti, in strutture residenziali socio-sanitarie e sociali | 2/2 | 100% | 100% | 4/6 | 100% | 0% | 0% | 0% | 5000 |
| Borsa di studio | 8/10 | 100% | 80% | 10/10 | 87% | 0% | 7% | 0% | 4392 |
| Borsa di studio | 4/4 | 100% | 100% | 6/6 | 100% | 0% | 0% | 0% | 3296 |
| Contributi in favore delle figlie e dei figli delle vittime | 5/5 | 83% | 100% | 6/7 | 97% | 0% | 3% | 0% | 4513 |
| Contributi straordinari studenti con invalidità 46% iscritti al collocamento mirato | 6/6 | 100% | 100% | 5/6 | 100% | 0% | 0% | 0% | 3015 |
| Premio di laurea | 0/1 | n/d | 0% | 4/4 | 81% | 0% | 16% | 0% | 5000 |
| In questa sezione trovi le informazioni relative al bando di concorso per richiedere i benefici per il diritto allo studio. | 4/4 | 100% | 100% | 7/9 | 100% | 0% | 0% | 0% | 3268 |
| <>/Metadata 3871 0 R/ViewerPreferences 3872 0 R>> | 2/2 | 67% | 100% | 12/12 | 92% | 0% | 0% | 5% | 4332 |
| Consulta il Bando A.A. 2026/27 | 4/4 | 80% | 100% | 8/8 | 92% | 0% | 0% | 5% | 3443 |
| Bando di concorso per l’attribuzione di borse di studio, altri contributi economici e servizi, per il diritto allo studio universitario per l’A.A. 2026/2027 | 4/4 | 80% | 100% | 9/9 | 93% | 0% | 0% | 4% | 3487 |
| Bando di concorso per l’attribuzione di borse di studio, altri contributi economici e servizi, per il diritto allo studio universitario | 4/5 | 100% | 80% | 7/7 | 97% | 0% | 0% | 0% | 3395 |
| Università di Milano-Bicocca: bando benefici per il diritto allo studio a.a. 2026/2027 | 5/5 | 100% | 100% | 7/8 | 100% | 0% | 0% | 0% | 3071 |
| Università dell'Insubria: bando benefici economici a.a. 2026/2027 | 4/5 | 100% | 80% | 6/6 | 100% | 0% | 0% | 0% | 3072 |
| Università Vita-Salute San Raffaele: bando benefici per il diritto allo studio a.a. 2026/2027 | 4/5 | 100% | 80% | 3/4 | 100% | 0% | 0% | 0% | 3063 |
| **Totale** | **87/97** | **95%** | **90%** | | **93%** | **0%** | **2%** | **3%** | **76977** |

- **Precisione:** quante condizioni estratte sono anche nel riferimento. **Richiamo:** quante del riferimento sono state trovate. Doppioni contati una volta.
- **Accordo sugli esiti:** su 5.000 persone fittizie costruite per soddisfare le regole e poi spostate a ridosso delle soglie, escluse quelle che entrambe le regole dichiarano non idonee.
- **Più cauta:** l'estrazione mette più riserve del riferimento (idoneo → idoneo salvo eccezioni → da verificare). **Falso sì:** l'estrazione dice idoneo, idoneo salvo eccezioni o da verificare, il riferimento non idoneo. **Falso no:** il contrario, ed è l'errore peggiore: la persona non controlla oltre.
- Le persone fittizie sono scelte apposta a ridosso delle soglie e non sempre coerenti (figlio nato da 10 giorni, nessun minore nel nucleo): le percentuali servono a trovare le differenze, non stimano quante persone reali riceverebbero un esito sbagliato.

## Differenze per beneficio

### Borse di studio

- Mancate (campo assente dall'estrazione): `anno_di_corso <= 1`

### Bando di concorso per l’assegnazione di Borse di studio e altri servizi per il diritto allo studio universitario a.a. 2026/2027

- Nessuna differenza strutturale.

### Bando per la concessione di un assegno di cura forfettario a studenti universitari affetti da disabilità gravissime iscritti presso gli Istituti Universitari con sede in Umbria per l’a.a. 2026-2027

- Nessuna differenza strutturale.

### BANDO BORSE DI STUDIO A.A. 2026/2027

- Mancate (campo assente dall'estrazione): `anno_di_corso <= 1`

### Borsa di Studio Universitaria

- Nel riferimento, scritte in modo diverso: `anno_di_corso <= 1`
- In più (campo assente dal riferimento): `eta <= 34`

### Bando Boves (CN)

- Nessuna differenza strutturale.

### Bando straordinario per l’assegnazione di contributi sulla spesa per le utenze domestiche di residenza a supporto del caro energia

- Mancate (campo assente dall'estrazione): `veicoli_esclusi falso`

### Contributi economici a familiari delle persone ospiti, o agli stessi ospiti, in strutture residenziali socio-sanitarie e sociali

- Nessuna differenza strutturale.

### Borsa di studio

- Mancate (campo assente dall'estrazione): `anno_di_corso <= 1`, `disabile vero`

### Borsa di studio

- Nessuna differenza strutturale.

### Contributi in favore delle figlie e dei figli delle vittime

- Sbagliate (campo giusto, valore diverso): `iscrizione in ('its',)`

### Contributi straordinari studenti con invalidità 46% iscritti al collocamento mirato

- Nessuna differenza strutturale.

### Premio di laurea

- Mancate (campo assente dall'estrazione): `titolo_di_studio in ('dottorato', 'laurea_magistrale', 'laurea_triennale', 'master')`

### In questa sezione trovi le informazioni relative al bando di concorso per richiedere i benefici per il diritto allo studio.

- Nessuna differenza strutturale.

### <>/Metadata 3871 0 R/ViewerPreferences 3872 0 R>>

- In più (campo assente dal riferimento): `titolo_di_studio in ('diploma', 'dottorato', 'laurea_magistrale', 'laurea_triennale', 'master')`

### Consulta il Bando A.A. 2026/27

- In più (campo assente dal riferimento): `titolo_di_studio in ('diploma', 'dottorato', 'laurea_magistrale', 'laurea_triennale', 'master')`

### Bando di concorso per l’attribuzione di borse di studio, altri contributi economici e servizi, per il diritto allo studio universitario per l’A.A. 2026/2027

- In più (campo assente dal riferimento): `titolo_di_studio in ('diploma', 'dottorato', 'laurea_magistrale', 'laurea_triennale', 'master')`

### Bando di concorso per l’attribuzione di borse di studio, altri contributi economici e servizi, per il diritto allo studio universitario

- Mancate (campo assente dall'estrazione): `anno_di_corso <= 1`

### Università di Milano-Bicocca: bando benefici per il diritto allo studio a.a. 2026/2027

- Nessuna differenza strutturale.

### Università dell'Insubria: bando benefici economici a.a. 2026/2027

- Nel riferimento, scritte in modo diverso: `anno_di_corso <= 1`

### Università Vita-Salute San Raffaele: bando benefici per il diritto allo studio a.a. 2026/2027

- Nel riferimento, scritte in modo diverso: `anno_di_corso <= 1`
