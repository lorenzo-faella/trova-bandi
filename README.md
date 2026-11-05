# trova-bandi: fase 0 (dati e fattibilità)

Data un'impresa (tipo, dimensione, sede, settore, codice ATECO), stabilisce per ogni bando aperto su incentivi.gov.it se è **idonea**, **quasi idonea**, **non idonea** o se **mancano dati**, e indica il requisito responsabile.

Le domande si fanno nell'ordine che decide più bandi il prima possibile.

Progetto del corso 20875 Software Engineering (Bocconi) di Lorenzo Faella ed Edoardo.

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

## Limiti attuali

- Usa solo i campi strutturati. I requisiti scritti nel testo dei bandi (de minimis, dipendenti, sede operativa…) non sono ancora estratti.
- I bandi in ATECO 2007 danno "mancano dati" finché non usiamo la tavola di raccordo ISTAT.
- Le imprese fittizie usano distribuzioni approssimate (`data/profili/distribuzioni.yaml`).

## Fonti

- incentivi.gov.it, open data, licenza IODL 2.0.
- ISTAT, elenco dei comuni italiani, CC BY 4.0.
