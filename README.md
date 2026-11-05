# trova-bandi

Progetto del corso 20875 Software Engineering (Bocconi) di Lorenzo Faella ed Edoardo Salvatore Russo. Consegna il 27/11/2026.

Topic approvato il 29/10/2026:

> An eligibility engine for Italian public incentives, for both individuals and businesses: it automatically collects grants and benefits from national, regional and municipal sources across Italy and extracts their requirements into verifiable rules, and an adaptive questionnaire tells each user which ones they qualify for, citing the requirement behind every answer.

## A che punto siamo

| Il topic promette | Oggi | Manca |
|---|---|---|
| Persone e imprese | Solo imprese | Profilo per le persone (età, ISEE, residenza, famiglia) e regole numeriche |
| Raccolta automatica da fonti nazionali, regionali e comunali | incentivi.gov.it, più l'elenco dei comuni ISTAT | Fonti per i bonus alle persone, portali regionali e comunali |
| Estrazione dei requisiti in regole verificabili | Conversione dei soli campi già strutturati | Estrazione dal testo dei bandi |
| Questionario adattivo | Funziona sui 7 campi strutturati | Misura con i requisiti estratti |
| Citazione del requisito dietro ogni risposta | Cita il campo open data | Citazione del passaggio del bando |

Oggi, data un'impresa (tipo, dimensione, sede, settore, codice ATECO), il codice stabilisce per ogni bando aperto su incentivi.gov.it se è **idonea**, **quasi idonea**, **non idonea** o se **mancano dati**, e indica il requisito responsabile.

## Come si usa

```
make            # dati + test + misura (~40 s la prima volta, poi solo ciò che è cambiato)
make scarica    # nuovo export da incentivi.gov.it e comuni ISTAT (al massimo uno al giorno)
make test
```

Il `Makefile` usa di default `~/anaconda3/bin/python`. Con un altro Python: `pip install -r requirements.txt`, poi `make PY=python3`.

Dopo un clone i file generati (`data/processed`, `data/regole`, `data/leggibili`) non ci sono: li crea `make`. L'Excel per sfogliare i bandi a mano è in `data/leggibili/`.

## Stadi

| stadio | file | produce |
|---|---|---|
| 1. download | `pipeline/scarica.py` | `data/raw/` (export grezzo + metadati) |
| 2. normalizzazione | `pipeline/normalizza.py` | `data/processed/bandi.json` |
| 3. regole | `pipeline/regole.py` + `schema/regola.schema.json` | `data/regole/<id>.yaml`, uno per bando |
| 4. motore | `pipeline/motore.py` | esito per bando, logica a tre valori |
| 4b. questionario | `pipeline/questionario.py` | prossima domanda (greedy) |
| 5. misura | `pipeline/misura.py` + `pipeline/profili.py` | `docs/misura-questionario.md` |
| 6. statistiche | `pipeline/profila.py` | `docs/fattibilita-dati.md` |
| versioni leggibili | `pipeline/leggibili.py` | `data/leggibili/` (Excel e JSON indentato) |

## Da leggere

- `docs/fattibilita-dati.md`: cosa c'è nei dati e quali problemi abbiamo trovato.
- `docs/misura-questionario.md`: quanto presto il questionario decide i bandi.
- `docs/decisioni.md`: tutte le scelte, con le alternative scartate.
- `docs/competitor.md`: i servizi esistenti e lo spazio libero.
- `brief-progetto-bandi.md`: il brief di avvio, con le regole del corso e i compiti ancora aperti.

## Limiti attuali

- Copre solo le imprese e usa solo i campi strutturati. I requisiti scritti nel testo dei bandi (de minimis, dipendenti, sede operativa…) non sono ancora estratti.
- I bandi in ATECO 2007 danno "mancano dati" finché non usiamo la tavola di raccordo ISTAT.
- Le imprese fittizie usano distribuzioni approssimate (`data/profili/distribuzioni.yaml`).

## Fonti

- incentivi.gov.it, [open data](https://www.incentivi.gov.it/it/open-data), licenza IODL 2.0 ([tracciato dei campi](https://www.incentivi.gov.it/sites/default/files/2024-01/Metadati_Scheda_Incentivo_1.pdf)).
- ISTAT, elenco dei comuni italiani, CC BY 4.0.
