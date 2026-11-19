# trova-bandi

Progetto del corso 20875 Software Engineering (Bocconi) di Lorenzo Faella ed Edoardo Salvatore Russo. Consegna il 27/11/2026.

Topic approvato il 29/10/2026:

> An eligibility engine for Italian public incentives, for both individuals and businesses: it automatically collects grants and benefits from national, regional and municipal sources across Italy and extracts their requirements into verifiable rules, and an adaptive questionnaire tells each user which ones they qualify for, citing the requirement behind every answer.

## A che punto siamo

*Aggiornato il 17/11/2026, ramo `raccolta-regioni` (contiene anche `integrazione-lorenzo`). Cosa è cambiato dal 9/11: `docs/report-13-11.md` e, dopo, le decisioni 58-65 di `docs/decisioni.md` (sotto, "Ultime novità"). Prossimi passi fino alla consegna: `docs/da-fare.md`, sezione 0.*

| Il topic promette | Oggi | Manca |
|---|---|---|
| Persone e imprese | Imprese: 756 regole generate dall'open data (716 aperte l'8/11). Persone: 5 regole di riferimento scritte a mano, più 180 estratte da un LLM e non riviste (50 schede INPS dei lotti 1 e 2, 130 bandi di comuni, diritto allo studio e case popolari) | Rivedere un campione delle estratte e portarle fra le regole riviste (obiettivo: circa 30), partendo da `docs/regole-sospette.md` |
| Raccolta automatica da fonti nazionali, regionali e comunali | incentivi.gov.it, comuni ISTAT, 449 schede INPS e circa 2.300 documenti da regioni, finanziarie, Camere, agenzie per lo studio, la casa e il lavoro, comuni capoluogo (decisioni 31-49). Nelle fonti miste (regioni, finanziarie, agenzie per il lavoro) individuati 233 bandi per le persone su 1.379 documenti (decisione 61) | Estrarre quei 233 bandi; i siti bloccati (Milano, Marche): `docs/da-fare.md`, sezione 5 |
| Estrazione dei requisiti in regole verificabili | Estrattore con controllo automatico di schema e citazioni e misuratore. Estratte tutte le schede INPS che sono benefici (decisione 55) e i bandi delle fonti per le persone (decisioni 56-57): requisiti non esprimibili 69% sulle schede INPS, 54% sui bandi. Etichette a mano: tutte compilate (14 benefici, 3 in comune). Accordo sugli esiti (decisioni 60 e 63): estrazione contro Lorenzo 75%, contro Edoardo 49%, Lorenzo contro Edoardo 46%: le differenze sono soprattutto di convenzione. Sui bandi, due estrazioni indipendenti concordano nel 93% dei casi (`docs/doppia-estrazione.md`, decisione 65) | Secondo passaggio sulle etichette con convenzioni comuni (`docs/seconda-passata-etichette.md`) e misura prima e dopo. L'estrattore non è mai stato eseguito con l'API vera: finora agenti o un server simulato |
| Questionario adattivo | Imprese: greedy sui 7 campi, misurato. Persone: domande con condizioni in `data/domande_persone.yaml`, ordinate da una regola provvisoria (decisione 53); l'età di chi fa domanda si ricava dal nucleo (decisione 58) e le domande che non riguardano la persona hanno una risposta ovvia invece di lasciare l'esito senza dati (decisione 64) | Misurare quello delle persone contro un ordine fisso |
| Citazione del requisito dietro ogni risposta | Nella demo: ogni esito mostra il requisito che lo decide, con il passaggio del testo (persone) o il campo dell'open data (imprese) e il link alla fonte | Le citazioni per le imprese, che oggi usano solo i campi strutturati |
| Copertura | Misurata per Lombardia e Sicilia (`docs/copertura-regioni.md`): incentivi.gov.it da solo copre il 25% in Lombardia e circa il 6% in Sicilia | Confermare a mano la revisione in `data/copertura/revisione.yaml` |

### Ultime novità (15-17/11)

- **Etichette di Edoardo e misura completa** (decisione 60): l'accordo tra i due etichettatori (42%) è più basso di quello fra estrazione ed etichette di Lorenzo, quindi il riferimento non è ancora stabile. Le differenze sono di convenzione: versione del vocabolario, `lavora_in_italia`, esclusioni che riguardano pochi.
- **Misura più giusta** (decisione 63): le persone fittizie di `pipeline/confronta.py` non hanno più combinazioni impossibili (un tipo di lavoro per chi non lavora, un figlio con età e data di nascita diverse). Accordo 75% / 49% / 46%. Le convenzioni da fissare insieme sono in `docs/seconda-passata-etichette.md`.
- **Bandi delle fonti miste** (decisioni 61-62): 233 bandi per le persone individuati dal titolo e dalla sezione dei destinatari; `pipeline/fonti/sezioni.py` non scambia più le frasi andate a capo per titoli.
- **Accuratezza degli esiti** (decisione 64): le domande che la demo non fa a una persona (il tipo di lavoro a chi è disoccupato) non lasciano più l'esito su "mancano dati". `make sospette` segnala le regole da rileggere per prime: soglie e date assenti dal testo, benefici per chi lavora senza condizioni sul lavoro, regole fatte solo di non modellabili.
- **Due estrazioni indipendenti** (decisione 65): le 23 regole toccate dalla correzione delle sezioni sono state rifatte due volte; le due versioni concordano nel 93% dei casi, e dove non concordano la regola è incerta. Stesso metodo proposto per i 233 bandi nuovi.
- **Esiti più accurati** (decisioni 68-70): nuova demo; risposte multiple per lavoro e studio; due campi nuovi nel vocabolario (situazioni particolari, regione dell'ateneo) e 75 regole rifatte. "Possibile" vuol dire almeno un requisito soddisfatto e nessuno che esclude. Simulazione prima e dopo con una persona estratta a caso: "possibili" da 57 a 6, senza falsi no (`docs/simulazione-demo.md`).
- **Sede e livello del corso** (decisione 73): la demo chiede il comune della sede del corso (provincia e regione si ricavano), il livello del corso e il tempo parziale; rifatte 51 regole dei bandi per il diritto allo studio con il `sezioni.py` corretto da Edoardo (decisione 66).
- **Residenza e domicilio, report con le risposte** (decisione 71): la demo distingue dove si risiede da dove si vive (fuorisede); il comune si sceglie dopo la regione; il report stampato si apre con "Le tue risposte".
- **Contesto** (`docs/contesto.md`): caro vita e aiuti a cui si ha diritto ma che non si chiedono, con le fonti, e sei idee per originalità e utilità.

Il motore dice per ogni bando o beneficio se il profilo è **idoneo**, **idoneo, salvo eccezioni** (restano aperti solo casi particolari di pochi: decisione 52), **quasi idoneo**, **non idoneo**, se **mancano dati** o se resta **da verificare** qualcosa che non sa controllare, e indica il requisito responsabile.

La prima domanda è "sei una persona fisica o giuridica?": divide il servizio in due rami, ognuno con i suoi bandi e le sue domande, sullo stesso motore (`docs/decisioni.md`, decisione 22).

## Come si usa

```
make            # dati + test + misura (~40 s la prima volta, poi solo ciò che è cambiato)
make scarica    # nuovo export da incentivi.gov.it e comuni ISTAT (al massimo uno al giorno)
make test
make controlla  # schema e citazioni delle regole per le persone e delle etichette
make confronta  # misure: estrazione contro le etichette, accordo tra etichettatori, due estrazioni dei bandi
make sospette   # le regole estratte da rileggere per prime (docs/regole-sospette.md)
make demo       # la demo web su http://127.0.0.1:8000
```

Serve Python 3.12 o più recente (alcuni test usano la sintassi delle f-string del 3.12). Il `Makefile` usa di default `~/anaconda3/bin/python`; con un ambiente nella cartella del progetto:

```
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
make dati test PY=.venv/bin/python
```

Con un percorso che contiene spazi, a `PY` va passato il percorso relativo, come qui.

## Demo

```
make demo PY=.venv/bin/python     # poi apri http://127.0.0.1:8000
docker build -t trova-bandi . && docker run -p 8000:8000 trova-bandi   # la stessa demo in un container
```

**Online con un link** (per la presentazione): `render.yaml` descrive il servizio. Da render.com: New → Blueprint → questo repository, ramo `demo`. Il piano gratuito si addormenta dopo 15 minuti senza visite, quindi il link va aperto un paio di minuti prima. Il giorno con cui si decide quali bandi sono aperti si fissa con `TROVA_BANDI_GIORNO=AAAA-MM-GG`, utile per una presentazione ripetibile.

**Cosa fa** (decisione 68):
- La pagina iniziale mostra i numeri del progetto, calcolati dai dati, e il perché: molti aventi diritto non chiedono gli aiuti (`docs/contesto.md`).
- Si sceglie tra persona e impresa, oppure si prova un profilo di esempio del caro vita: studente fuorisede, famiglia monoreddito, lavoratore autonomo, pensionata sola (`web/profili_demo.yaml`).
- Le domande arrivano una alla volta, con "Non lo so" sempre possibile, e i risultati si aggiornano dal vivo nei sei esiti del motore, scritti in linguaggio semplice (ti spetta, possibile, ti manca poco, non ti spetta...).
- Ogni scheda mostra la frase del bando che decide l'esito e il link alla fonte. Ha anche un'etichetta che dice se la regola è stata rivista o estratta automaticamente; le estratte sono incluse di default.
- Per le persone, i bandi locali di altre regioni vanno in fondo, in un gruppo chiuso.
- Se l'ISEE è "non lo so", un avviso dice quanti benefici dipendono da lui e come ottenerlo con la DSU precompilata.
- Alla fine le scadenze dei bandi possibili si scaricano in un calendario (`.ics`) e i risultati si possono stampare.
- Il server non salva le risposte.

Il codice dell'interfaccia è in `web/static/`: HTML, CSS e moduli JavaScript senza passaggi di build. Le animazioni si spengono con l'impostazione di sistema "riduci movimento".

## Estrazione e raccolta

Estrazione dei requisiti con un LLM (richiede `anthropic`, in `requirements.txt`):

```
python -m pipeline.estrai api <obiettivi> <uscita>        # con l'API: serve ANTHROPIC_API_KEY
python -m pipeline.estrai prepara <obiettivi> <lavoro>    # senza API: scrive i prompt
python -m pipeline.estrai importa <obiettivi> <lavoro> <uscita>   # controlla le risposte <id>.risposta.json
```

Il ramo `api` è provato solo con un server simulato: la richiesta passa dall'SDK vero, ma non è mai arrivata all'API reale. Per confrontare il risultato con le etichette: `make confronta` (estrazione contro le etichette di Lorenzo e di Edoardo, e Lorenzo contro Edoardo; le etichette ancora vuote non contano). La prova sui 5 benefici di sviluppo: `make confronta-sviluppo`.

Per i bandi raccolti, con le stesse due fasi (`prepara`, poi le risposte, poi `importa`):

```
python -m pipeline.estrai_documenti prepara <lavoro> <id ...>          # solo le sezioni sui requisiti
python -m pipeline.estrai_documenti importa <lavoro> <uscita> <id ...>
python -m pipeline.estrai_documenti controlla data/regole_estratte/documenti
```

Dove stanno le regole estratte: `data/regole_estratte/lotto-1` e `lotto-2` (schede INPS), `documenti` (bandi), tutte mostrate nella demo solo a richiesta; `gold` (i 14 benefici etichettati, estratti alla cieca, solo per la misura); `seconda-estrazione` (la seconda estrazione indipendente di 23 bandi, solo per il confronto, decisione 65); `da-rifare.txt` (le regole da rifare dopo la decisione 62); `documenti-senza-requisiti` (bandi per enti o imprese, pagine senza testo), che la demo non carica perché una regola vuota dà "idoneo" a tutti (decisione 57).

Raccolta dei bandi regionali. I testi stanno in `data/raw/documenti/`, fuori da git: dopo un clone ci sono solo i 3 documenti di prova e, in `data/raw/elenchi/`, gli elenchi del giorno. Si ricreano così, in qualche ora in tutto, una volta al giorno al massimo:

```
python -m pipeline.fonti.elenchi toscana        # e piemonte-cittadini, piemonte-imprese, sicilia, umbria, calabria, liguria-alfa, marche-fmc, lazio-europa, lazio-innova, abruzzo-coesione, campania-fesr, puglia, valle-aosta-imprese
python -m pipeline.fonti.elenchi finpiemonte    # finanziarie regionali: e finaosta, veneto-innovazione, filse, art-er, sviluppo-toscana, gepafin, sviluppumbria, finmolise, puglia-sviluppo, irfis, sfirs, sardegna-ricerche
python -m pipeline.fonti.elenchi fvg            # e marche-credito-futuro, camera-as, camera-comolecco; lavoro: inail, veneto-lavoro, sardegna-aspal, valle-aosta-lavoro
python -m pipeline.fonti.elenchi trento-portale  # e bolzano-portale: bandi aperti del portale con il link su quei siti (Crawl-delay rispettato)
python -m pipeline.fonti.elenchi ergo           # diritto allo studio: e dsu-toscana, edisu-piemonte, esu-verona, esu-padova, laziodisco, adisu-puglia, erdis-marche, ardis-fvg, adisurc-campania, aliseo-liguria, ersu-palermo, ersu-catania, ersu-messina, ersu-enna, ersu-cagliari, adsu-laquila, adsu-teramo, esu-molise, adisu-umbria, opera-trento
python -m pipeline.fonti.elenchi portale-puglia  # e le altre portale-<regione>: bandi aperti del portale sui siti che non raccogliamo
python -m pipeline.fonti.elenchi fvg --solo-mancanti   # dopo errori di rete: solo le voci dell'ultimo elenco senza documento
python -m pipeline.fonti.api_regioni lombardia   # e sardegna, basilicata, veneto, emilia, finlombarda, trentino-sviluppo, calabria-europa
python -m pipeline.fonti.camere                  # pagine elenco delle Camere di commercio (data/fonti/camere.yaml)
python -m pipeline.fonti.comuni                  # pagine "Avvisi" dei comuni capoluogo (data/fonti/comuni.yaml), poi elenchi comune-<nome>
python -m pipeline.fonti.manuali                 # bandi salvati a mano dal browser per i siti che rifiutano i programmi (data/fonti/manuali.yaml)
python -m pipeline.fonti.elenchi camera-mo      # e le altre camera-* di camere.yaml
python -m pipeline.fonti.doppioni               # bandi raccolti due volte (elenco in data/raw/elenchi/)
python -m pipeline.fonti.conta                  # dopo ogni raccolta: documenti salvati = voci dell'elenco del giorno?
```

Misura della copertura (legge solo file locali):

```
python -m pipeline.copertura                    # rigenera docs/copertura-regioni.md
python -m pipeline.copertura scarica-lombardia  # riscarica il dataset ufficiale lombardo
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
| persone: misura dell'estrazione | `pipeline/confronta.py` | `docs/test-estrazione.md` (contro le etichette), `docs/test-estrazione-sviluppo.md` (i 5 di sviluppo): confronto per struttura e per esiti |
| raccolta dalle altre fonti | `pipeline/fonti/` (`elenchi.py`, `api_regioni.py`, `camere.py`, `comuni.py`, `manuali.py`, `documenti.py`) con `data/fonti/*.yaml` | `data/raw/elenchi/` (in git), `data/raw/documenti/` (fuori da git) |
| estrazione dai documenti | `pipeline/estrai_documenti.py` + `pipeline/fonti/sezioni.py` | regole candidate dalle sole sezioni sui requisiti, in `data/regole_estratte/documenti/` |
| persone: domande | `data/domande_persone.yaml` | testo e condizione (`solo_se`) di ogni domanda |
| copertura | `pipeline/copertura.py` + `data/copertura/revisione.yaml` | `docs/copertura-regioni.md` |
| demo | `web/server.py`, `web/domande.py`, `web/static/` | l'applicazione web |

## Da leggere

- `docs/fattibilita-dati.md`: cosa c'è nei dati e quali problemi abbiamo trovato.
- `docs/copertura-portale.md`: quanto incentivi.gov.it copre davvero i bandi italiani.
- `docs/fattibilita-persone.md` e `docs/prova-download.md`: le prove di estrazione e di download per il ramo persone (`prove/prova_download.py`).
- `docs/misura-questionario.md`: quanto presto il questionario decide i bandi.
- `docs/copertura-regioni.md`: quanti bandi troviamo in Lombardia e Sicilia, con gli intervalli.
- `docs/enti-per-regione.md`: gli enti che pubblicano bandi, regione per regione.
- `docs/test-estrazione.md`: la misura dell'estrazione contro le etichette a mano. Per ora sulle 9 di Lorenzo; con quelle di Edoardo si aggiungono `docs/test-estrazione-edo.md` e `docs/accordo-etichette.md`. La prova sui 5 benefici di sviluppo è in `docs/test-estrazione-sviluppo.md`.
- `docs/simulazione-demo.md`: la demo provata con una persona estratta a caso, prima e dopo la decisione 70, con giudizio alla cieca.
- `docs/pipeline-per-edo.md`: i passi da qui alla consegna, in ordine, con i comandi.
- `docs/regole-sospette.md` (`make sospette`) e `docs/doppia-estrazione.md`: quali regole estratte rileggere per prime, e quanto due estrazioni indipendenti concordano (decisioni 64-65).
- `docs/seconda-passata-etichette.md`: le convenzioni da fissare insieme prima di rifare la misura sulle etichette (decisione 63).
- `docs/contesto.md`: perché conta adesso. Caro vita (inflazione al 5,4% a ottobre 2026), aiuti a cui si ha diritto ma che non si chiedono, cosa il progetto risolve e cosa no.
- `docs/report-13-11.md`: etichette, lotto 2 INPS e bandi per le persone, con i numeri e i limiti (13/11).
- `docs/decisioni.md`: tutte le scelte, con le alternative scartate.
- `docs/da-fare.md`: l'elenco unico delle cose aperte.
- `docs/competitor.md`: i servizi esistenti e lo spazio libero.
- `docs/vocabolario-persone.md`: i dati che il motore può chiedere a una persona.
- `docs/etichettatura.md`: come etichettare a mano i benefici (14 dopo la decisione 40).
- `brief-progetto-bandi.md`: il brief di avvio, con le regole del corso e i compiti ancora aperti.

## Limiti attuali

- Per le imprese usa solo i campi strutturati: i requisiti scritti nel testo dei bandi (de minimis, dipendenti, sede operativa…) non sono ancora estratti.
- Per le persone le regole riviste sono ancora poche: la demo ne usa 5, e altre 180 solo a richiesta, segnate come non riviste.
- L'ordine delle domande per le persone non è misurato (decisione 53). Una domanda chiusa dal suo `solo_se` non si fa: se serve a un beneficio, quello resta su "mancano dati".
- Nelle regole estratte il 54% delle condizioni dei bandi e il 69% di quelle delle schede INPS del lotto 2 restano `non_modellabile` (decisioni 55-56): molti esiti finiscono su "da verificare" o "mancano dati". Mancano soprattutto livello del corso, ateneo, ISEE-ERP, gestione previdenziale, età di chi fa domanda (`docs/report-13-11.md`, sezione 4).
- Un bando ha una sola finestra di domanda (`apertura`/`chiusura`): per i bandi con più scadenze si usa la principale (decisione 56).
- `portata: rara` è applicata a mano a una sola regola di riferimento (NASpI, decisione 52); nelle regole estratte la usano 27 condizioni, non riviste.
- L'estrazione legge una sola scheda: non vede i requisiti che stanno altrove, per esempio in una circolare.
- incentivi.gov.it è incompleto anche per le imprese: copertura irregolare tra regioni e pochissimi comuni (`docs/copertura-portale.md`).
- INPS copre solo ciò che eroga: mancano bonus fiscali e aiuti regionali e comunali.
- I bandi in ATECO 2007 danno "mancano dati" finché non usiamo la tavola di raccordo ISTAT.
- Le imprese fittizie usano distribuzioni approssimate (`data/profili/distribuzioni.yaml`).

## Fonti

- incentivi.gov.it, [open data](https://www.incentivi.gov.it/it/open-data), licenza IODL 2.0 ([tracciato dei campi](https://www.incentivi.gov.it/sites/default/files/2024-01/Metadati_Scheda_Incentivo_1.pdf)).
- ISTAT, elenco dei comuni italiani, CC BY 4.0.
- Regione Lombardia, [Anagrafica dei bandi regionali](https://www.dati.lombardia.it/d/bukx-h2uy), CC BY 4.0: solo per misurare la copertura.
- INPS, schede delle prestazioni: nessuna licenza dichiarata (vedi `docs/decisioni.md`, punto 16).
- Siti di regioni, finanziarie, Camere di commercio, agenzie e comuni: elencati in `data/fonti/`, rispettando robots.txt (decisioni 31, 42, 51).
