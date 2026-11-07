# trova-bandi

Progetto del corso 20875 Software Engineering (Bocconi) di Lorenzo Faella ed Edoardo Salvatore Russo. Consegna il 27/11/2026.

Topic approvato il 29/10/2026:

> An eligibility engine for Italian public incentives, for both individuals and businesses: it automatically collects grants and benefits from national, regional and municipal sources across Italy and extracts their requirements into verifiable rules, and an adaptive questionnaire tells each user which ones they qualify for, citing the requirement behind every answer.

## A che punto siamo

| Il topic promette | Oggi | Manca |
|---|---|---|
| Persone e imprese | Imprese: 756 regole generate. Persone: motore pronto e 5 regole scritte a mano | Altre regole per le persone (obiettivo: circa 30) |
| Raccolta automatica da fonti nazionali, regionali e comunali | incentivi.gov.it, comuni ISTAT, 449 schede INPS | Fonti regionali e comunali per le persone |
| Estrazione dei requisiti in regole verificabili | Estrattore con controllo automatico di schema e citazioni, misuratore per struttura ed esiti; 15 benefici da etichettare a mano | Le etichette, l'estrazione sui 15 benefici e la sua misura. Provato sui 5 benefici di sviluppo, senza API (`docs/test-estrazione.md`); con l'API non è ancora stato eseguito: manca la chiave |
| Questionario adattivo | Funziona sui 7 campi delle imprese | Estensione alle persone e nuova misura |
| Citazione del requisito dietro ogni risposta | Persone: passaggio letterale della scheda. Imprese: campo open data | Mostrarla nella demo |

Il motore dice per ogni bando o beneficio se il profilo è **idoneo**, **quasi idoneo**, **non idoneo**, se **mancano dati** o se resta **da verificare** qualcosa che non sa controllare, e indica il requisito responsabile.

La prima domanda è "sei una persona fisica o giuridica?": divide il servizio in due rami, ognuno con i suoi bandi e le sue domande, sullo stesso motore (`docs/decisioni.md`, decisione 22).

## Come si usa

```
make            # dati + test + misura (~40 s la prima volta, poi solo ciò che è cambiato)
make scarica    # nuovo export da incentivi.gov.it e comuni ISTAT (al massimo uno al giorno)
make test
make controlla  # schema e citazioni delle regole per le persone e delle etichette
```

Estrazione dei requisiti con un LLM (richiede `anthropic`, in `requirements.txt`):

```
python -m pipeline.estrai api <obiettivi> <uscita>        # con l'API: serve ANTHROPIC_API_KEY
python -m pipeline.estrai prepara <obiettivi> <lavoro>    # senza API: scrive i prompt
python -m pipeline.estrai importa <obiettivi> <lavoro> <uscita>   # controlla le risposte <id>.risposta.json
```

Il ramo `api` è provato solo con un server simulato: la richiesta passa dall'SDK vero, ma non è mai arrivata all'API reale. Per confrontare il risultato con il riferimento: `make confronta`.

Il `Makefile` usa di default `~/anaconda3/bin/python`. Con un altro Python: `pip install -r requirements.txt`, poi `make PY=python3`.

Raccolta dei bandi regionali (testi in `data/raw/documenti/`, fuori da git: si ricreano così, circa 2 ore in tutto, una volta al giorno al massimo):

```
python -m pipeline.fonti.elenchi toscana        # e piemonte-cittadini, piemonte-imprese, sicilia, umbria, calabria, liguria-alfa, marche-fmc, lazio-europa, lazio-innova, abruzzo-coesione, campania-fesr, puglia, valle-aosta-imprese
python -m pipeline.fonti.elenchi finpiemonte    # finanziarie regionali: e finaosta, veneto-innovazione, filse, art-er, sviluppo-toscana, gepafin, sviluppumbria, finmolise, puglia-sviluppo, irfis, sfirs, sardegna-ricerche
python -m pipeline.fonti.elenchi fvg            # e marche-credito-futuro; lavoro: inail, veneto-lavoro, sardegna-aspal
python -m pipeline.fonti.elenchi fvg --solo-mancanti   # dopo errori di rete: solo le voci dell'ultimo elenco senza documento
python -m pipeline.fonti.api_regioni lombardia   # e sardegna, basilicata, veneto, emilia, finlombarda, trentino-sviluppo, calabria-europa
python -m pipeline.fonti.camere                  # pagine elenco delle Camere di commercio (data/fonti/camere.yaml)
python -m pipeline.fonti.elenchi camera-mo      # e le altre camera-* di camere.yaml
python -m pipeline.fonti.doppioni               # bandi raccolti due volte (elenco in data/raw/elenchi/)
python -m pipeline.fonti.conta                  # dopo ogni raccolta: documenti salvati = voci dell'elenco del giorno?
```

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
| persone: raccolta | `pipeline/fonti/inps.py` | `data/raw/inps_schede_*.json` |
| persone: regole | scritte a mano, per ora | `data/regole_persone/<id>.yaml` |
| persone: controllo | `pipeline/citazioni.py` | errori di schema e citazioni, soglie assenti dalla scheda |
| persone: estrazione | `pipeline/estrai.py` + `pipeline/prompt_estrazione.md` | regole candidate, rifiutate se schema o citazioni non tornano |
| persone: misura dell'estrazione | `pipeline/confronta.py` | `docs/test-estrazione.md`: confronto per struttura e per esiti con le regole di riferimento |

## Da leggere

- `docs/fattibilita-dati.md`: cosa c'è nei dati e quali problemi abbiamo trovato.
- `docs/copertura-portale.md`: quanto incentivi.gov.it copre davvero i bandi italiani.
- `docs/fattibilita-persone.md` e `docs/prova-download.md`: le prove di estrazione e di download per il ramo persone (`prove/prova_download.py`).
- `docs/misura-questionario.md`: quanto presto il questionario decide i bandi.
- `docs/test-estrazione.md`: confronto tra regole estratte e di riferimento. Per ora solo sui 5 benefici di sviluppo: non è ancora la misura finale.
- `docs/decisioni.md`: tutte le scelte, con le alternative scartate.
- `docs/da-fare.md`: l'elenco unico delle cose aperte.
- `docs/competitor.md`: i servizi esistenti e lo spazio libero.
- `docs/vocabolario-persone.md`: i dati che il motore può chiedere a una persona.
- `docs/etichettatura.md`: come etichettare a mano i 15 benefici.
- `brief-progetto-bandi.md`: il brief di avvio, con le regole del corso e i compiti ancora aperti.

## Limiti attuali

- Per le imprese usa solo i campi strutturati: i requisiti scritti nel testo dei bandi (de minimis, dipendenti, sede operativa…) non sono ancora estratti.
- Per le persone le regole sono ancora poche e il questionario non le usa ancora.
- Sui 5 benefici di sviluppo quasi nessun profilo può arrivare a "idoneo": basta un'eccezione rara per lasciare tutti su "da verificare" (`docs/da-fare.md`, sezione 3).
- L'estrazione legge una sola scheda: non vede i requisiti che stanno altrove, per esempio in una circolare.
- incentivi.gov.it è incompleto anche per le imprese: copertura irregolare tra regioni e pochissimi comuni (`docs/copertura-portale.md`).
- INPS copre solo ciò che eroga: mancano bonus fiscali e aiuti regionali e comunali.
- I bandi in ATECO 2007 danno "mancano dati" finché non usiamo la tavola di raccordo ISTAT.
- Le imprese fittizie usano distribuzioni approssimate (`data/profili/distribuzioni.yaml`).

## Fonti

- incentivi.gov.it, [open data](https://www.incentivi.gov.it/it/open-data), licenza IODL 2.0 ([tracciato dei campi](https://www.incentivi.gov.it/sites/default/files/2024-01/Metadati_Scheda_Incentivo_1.pdf)).
- ISTAT, elenco dei comuni italiani, CC BY 4.0.
- INPS, schede delle prestazioni: nessuna licenza dichiarata (vedi `docs/decisioni.md`, punto 16).
