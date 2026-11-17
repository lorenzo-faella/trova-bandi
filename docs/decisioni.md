# Registro delle decisioni

Formato: decisione, alternative scartate, motivo. Le decisioni con ⚠ sono provvisorie o vanno riviste insieme.

## 27/10/2026

**1. Primo pezzo: le imprese.** ⚠ Il 27/10 era stato scelto come target; il **topic approvato il 29/10 copre persone e imprese**, quindi le persone restano da aggiungere.
- Motivo per partire da qui: per le imprese i requisiti principali sono già campi strutturati negli open data. Per le persone (ISEE, età, residenza) non esiste un campo strutturato.

**2. Fonte principale: export ufficiale di incentivi.gov.it** (IODL 2.0), scaricato con la stessa richiesta del pulsante "Esporta" del portale.
- Scartati: scraper di terzi (attori Apify), scraping delle pagine.
- Motivo: è la fonte ufficiale, una sola GET restituisce tutti i 6.007 incentivi, e la licenza permette il riuso.
- Come la usiamo: al massimo un download al giorno (`pipeline/scarica.py` non riscarica se il file del giorno esiste) e citiamo sempre la fonte.

**3. Seconda fonte: elenco dei comuni ISTAT** (CC BY 4.0).
- Motivo: serve a riconoscere i nomi dei comuni nei bandi e a collegare comune e regione.
- Scartato: dedurre i comuni dai bandi stessi, perché gli elenchi dei bandi sono parziali e contengono nomi vecchi.

**4. Regole come dati: un file YAML per bando, validato da JSON Schema** (`schema/regola.schema.json`).
- Scartati: un unico database; regole scritte in codice.
- Motivo:
  - un file per bando si legge, si confronta con git e si corregge a mano;
  - lo schema ha già fermato un errore reale, cioè codici ATECO duplicati nel testo del bando.
- I file sono **generati**: le correzioni manuali andranno in un livello separato, da decidere.

**5. Motore nostro, non OpenFisca.**
- Motivo:
  - OpenFisca Italia è poco attivo ed è pensato per tasse e benefit;
  - il nostro motore sta in circa 70 righe ed è testato con bandi inventati di cui conosciamo l'esito.

**6. Logica a tre valori: sì, no, non si sa.**
- Un requisito non verificabile (dato mancante, codice ATECO troppo generico, comune fuori da un elenco che contiene comuni soppressi) dà "mancano dati", mai "non idoneo".
- Motivo: un "no" sbagliato detto con sicurezza è il danno peggiore (brief, §8).

**7. "Quasi idoneo" solo per requisiti che l'impresa può cambiare:** tipologia, settore, ATECO.
- Scartato: qualunque requisito singolo mancato.
- Motivo: con la regola generale un'impresa risultava "quasi idonea" a centinaia di bandi di altre regioni.
- ⚠ È discutibile per la sede operativa: aprire un'unità locale in un'altra regione è una strategia reale.

**8. Due versioni di ATECO.**
- I bandi usano sia ATECO 2007 sia ATECO 2025 (in vigore dal 1/4/2025). Quando la versione non è dichiarata, la deduciamo dalla data di apertura.
- Il profilo chiede solo il codice 2025, perché è quello che le imprese hanno oggi. I bandi in ATECO 2007 danno quindi "mancano dati".
- ⚠ Prossimo passo: la tavola di raccordo ISTAT 2007 → 2025.

**9. Interpretazione delle tipologie.**
- "Impresa da costituire - Altro" è letta come "impresa da costituire generica": vale anche per quelle femminili e giovanili.
- Un'impresa da costituire è trattata come **microimpresa**. All'inizio l'avevamo trattata come "non classificabile", ma 43 dei 54 bandi aperti per imprese da costituire elencano solo dimensioni vere. Così il profilo di prova del negozio a Palermo veniva escluso da "ON – Oltre Nuove imprese a tasso zero".
- Una cooperativa è sia "Cooperative/Associazioni Non Profit" sia "Impresa".

**10. Questionario: greedy sui "bandi decisi".**
- A ogni passo si sceglie la domanda che decide più bandi in media. Le risposte possibili si stimano da 1.000 imprese fittizie coerenti con le risposte già date; se ne restano meno di 30, si ignorano le condizioni più recenti.
- Scartati: entropia sul profilo, perché misura quanto sappiamo dell'impresa e non dei bandi; l'albero ottimo, che è NP-difficile.

**11. Esito della misura** (`docs/misura-questionario.md`).
- Sui 7 campi strutturati il questionario adattivo **coincide con il miglior ordine fisso**: regione → settore → tipologia → …
- Rispetto all'ordine dei filtri del portale, dopo una domanda decide l'84% dei bandi invece del 18%. Il merito però è dell'ordine, non dell'adattività.
- Per decidere *tutti* i bandi servono comunque quasi tutte le 7 domande: anche l'oracolo che conosce le risposte ne usa 6,6.
- Conseguenza: l'adattività conta solo con molte domande specifiche, cioè con i requisiti estratti dal testo (de minimis, dipendenti, sede operativa, anni di attività: vedi `docs/fattibilita-dati.md`). La misura va ripetuta dopo l'estrazione.

**12. Popolazione sintetica con distribuzioni approssimate** (`data/profili/distribuzioni.yaml`).
- I comuni sono uniformi dentro la regione, quindi i comuni piccoli sono sovrastimati.
- Gli ambiti (aree interne, ZES) sono indipendenti dal comune, e questo è falso.
- ⚠ Da sostituire con il registro ISTAT ASIA e con gli elenchi ufficiali delle aree interne. Così l'ambito si dedurrebbe dal comune e sparirebbe una domanda.

**13. Stack della fase 0:** Python con le librerie già installate (pandas, numpy, jsonschema, PyYAML, pytest) e make.
- ⚠ Lo stack dell'applicazione (web, database) **non è deciso**.

**14. Commenti normali nel codice, non riga per riga** (deviazione dal brief, §1).
- Motivo: si leggono meglio. Le spiegazioni lunghe stanno in questo file.

**15. Test differenziale.**
- Una seconda implementazione volutamente ingenua, che legge direttamente l'export grezzo, deve trovare gli stessi bandi idonei della pipeline (`tests/test_profili_manuali.py`).
- Ha già trovato un errore nei nostri profili di prova: in YAML `[Agricoltura, silvicoltura e pesca]` diventa una lista di **due** voci.
- Abbiamo controllato che i test falliscano davvero introducendo apposta tre difetti nel motore: li catturano tutti.

## 5/11/2026

**16. Fonte per le persone: le schede INPS.**
- Scartato: incentivi.gov.it. I suoi 31 bandi non chiusi aperti ai "cittadini" sono quasi tutti per aspiranti imprenditori, e nelle descrizioni non compaiono mai ISEE, figli o casa. Non abbiamo trovato un catalogo nazionale dei bonus: `dati.gov.it` non ha dataset per "bonus famiglie".
- Come: dalla sitemap, una pagina alla volta con pausa di un secondo. `robots.txt` lo permette, tranne per i PDF dei moduli, che non scarichiamo.
- ⚠ Il sito non dichiara una licenza. Per l'art. 52, c. 2 del CAD, ciò che una PA pubblica senza licenza si considera dato aperto: citiamo la fonte. Da rileggere prima di rendere pubblico il repository.
- ⚠ INPS copre solo ciò che eroga: restano fuori bonus fiscali e aiuti regionali e comunali.

**17. Le regole sono alberi, non liste.**
- All'inizio pensavamo bastassero confronti numerici e un quantificatore sul nucleo. Leggendo l'ADI: i permessi per "casi speciali" sono esentati da cittadinanza, residenza e requisiti economici, ma non dai limiti sui veicoli. Servono E/O annidati (`almeno_uno_di`, `tutti_di`).
- La logica a tre valori si estende: "o" è vero se almeno un ramo è vero, anche se gli altri non sono noti.

**18. Nuovo esito "da verificare", con `non_modellabile`.**
- Un requisito reale che non sappiamo controllare non deve sparire: altrimenti diremmo "idoneo" con troppa sicurezza. È diverso da "mancano dati", dove c'è ancora una domanda da fare.
- Conseguenza: per ora ADI, Bonus nuovi nati e Assegno di maternità non arrivano mai a "idoneo", al massimo a "da verificare". Lo riteniamo corretto.
- Rimandati i valori derivati previsti dal piano: la scala di equivalenza dell'ADI non sta nella scheda. Si aggiungono quando servono.

**19. Niente dati giudiziari.** Condanne e misure cautelari non si chiedono: diventano "da verificare".

**20. Citazione letterale obbligatoria per le regole sulle persone** (`pipeline/citazioni.py`).
- Una citazione che non si trova nella fonte fa scartare il requisito: è il primo filtro contro le regole inventate dall'LLM.
- Non prova che la regola sia giusta, solo che il testo esiste: la revisione umana resta.
- Un requisito `non_modellabile` può non citare, perché a volte segnala un'assenza (Bonus nuovi nati: la scheda non riporta cittadinanza e residenza).

**21. Etichette a mano su 15 benefici diversi dai 5 di prova, con 3 in comune tra Lorenzo ed Edoardo** (`docs/etichettatura.md`). Servono a misurare sia l'LLM sia l'accordo tra di noi. I 5 di prova li ha scritti Claude, quindi non valgono come verità di riferimento.


## Prese il 5/11/2026, dopo il ramo persone

**26. L'estrazione si misura sia sulla struttura sia sugli esiti, escludendo i casi banali** (`pipeline/confronta.py`).
- Struttura: le condizioni elementari coincidono? Comportamento: sulle stesse persone fittizie, le due regole danno lo stesso esito?
- Scartato: solo la struttura, perché due regole equivalenti scritte diversamente risulterebbero sbagliate.
- Scartato: l'accordo su tutti i profili. Quasi tutti i profili casuali non hanno i requisiti, quindi una regola che esclude sempre tutti sembrerebbe quasi perfetta.
- Il misuratore è provato per mutazione: ogni soglia raddoppiata e ogni requisito tolto che può escludere qualcuno vengono notati. La prima versione falliva questa prova, perché rendeva vere tutte le alternative di un requisito e una nascondeva l'altra.
- Limite: un requisito non modellabile dimenticato spesso non cambia gli esiti, se ne resta un altro. Per questo si riporta anche il loro numero.

**27. Oltre alle citazioni, un avviso sulle soglie assenti dalla scheda** (`soglie_non_trovate`). Una citazione vera può accompagnare un numero inventato, e il controllo delle citazioni non se ne accorge. È un avviso e non un errore: "minorenne" giustifica 18 senza scriverlo.

**28. L'LLM riceve la scheda, il vocabolario e due esempi; il controllo è fatto fuori dal modello** (`pipeline/estrai.py`).
- Risposta in JSON, controllata con il nostro schema e con le citazioni; se viene rifiutata, il modello riceve gli errori e riprova, fino a 3 volte.
- Scartati gli structured output dell'API: non ammettono schemi ricorsivi, e le regole lo sono.
- Dal vocabolario togliamo la colonna "Usato da", che direbbe quali campi servono a quali benefici. Un beneficio non è mai tra i suoi esempi.
- Le regole estratte restano in `data/regole_estratte/`, separate da quelle riviste. È il modo più semplice di avere lo stato `estratto_da_llm` proposto in `docs/fattibilita-persone.md`.

**29. Prima prova dell'estrattore sui 5 benefici di sviluppo (5/11): le differenze si leggono una per una, non dai totali.**
- Eseguita da 5 agenti Claude Code separati (Opus 5.5), che hanno ricevuto solo il prompt, senza API. L'isolamento è un'istruzione, non un vincolo tecnico. Una sola esecuzione.
- Contro il riferimento originale: tutte le regole passano schema e citazioni al primo tentativo; 27 condizioni su 31 trovate, precisione 77%, accordo sugli esiti 64%, più cauta 21%, falsi sì 7%, falsi no 4%. Non modellabili: 7 nel riferimento, 21 nell'estrazione. La colonna "più cauta" è stata aggiunta dopo aver visto questi dati.
- Questi numeri non misurano l'estrattore: leggendo le schede, molte differenze sono errori del riferimento, scritto da Claude. È il motivo della decisione 21.
- Da qui il confronto serve come **revisione a due mani**: ogni differenza è un punto da rileggere nella scheda, chiunque abbia ragione.

**30. Corrette le regole di riferimento dopo aver riletto le schede** (5/11). Ogni differenza è stata controllata a mano nel testo della scheda.
- Aveva ragione l'estrazione, e il riferimento è stato corretto:
  - NASpI: chi conserva un part-time può avere diritto; chi ha contributi sia agricoli sia non agricoli deve avere prevalenti quelli non agricoli. Il riferimento diceva "idoneo" senza riserve.
  - Assegno unico: chi lavora in Italia senza risiedervi deve avere anche iscrizione e regolarità contributiva. Il riferimento aveva tagliato la frase.
  - Assegno di maternità: mancavano i familiari con Carta di soggiorno.
- Aveva torto l'estrazione: Assegno di maternità, `mesi <= 6`. La colpa era del vocabolario, che non diceva se i mesi fossero interi. Ora dice "mesi interi già compiuti": rilanciata la sola estrazione di quel beneficio, il risultato è corretto.
- Restano aperte, da decidere con Edoardo:
  - Bonus nuovi nati: l'estrazione chiede un minore nel nucleo. Regge sulla scheda, ma esclude a torto chi ha il figlio in un altro nucleo.
  - Assegno unico: il riferimento considera ammessi i cittadini italiani e UE, ma la scheda non dà un elenco. L'estrazione, a cui il prompt vieta le conoscenze esterne, dice sempre "da verificare".
- Dopo le correzioni: 29 condizioni su 31, accordo sugli esiti 87%, falsi no 4% (quasi tutti dal Bonus nuovi nati, il resto dall'ADI). **Non è una stima della qualità:** il riferimento è stato corretto guardando l'estrazione, e l'autore è lo stesso modello. Vale solo la misura sulle etichette a mano.
- Limiti: un'estrazione da una sola scheda non vede ciò che la scheda non dice (cittadinanza e residenza del Bonus nuovi nati stanno in una circolare), e il controllo delle citazioni non se ne può accorgere. Le regole ADI e Assegno di maternità restano una lettura di Claude, non riviste da una persona.

## Prese il 28-29/10/2026, registrate il 5/11

Erano nella cartella condivisa su iCloud. Le numeriamo dopo la 21 per non toccare le 16-21. Completano quelle decisioni, senza contraddirle.

**22. Due rami, persone fisiche e giuridiche; la prima domanda li divide** (decisione di Edoardo, 28/10). Completa la decisione 1, che parte dalle imprese.
- La prima domanda del questionario è "sei una persona fisica o giuridica?". Ogni ramo ha i suoi bandi e le sue domande, ma il motore è lo stesso (decisioni 5, 6 e 17).
- Scartato: un questionario unico per tutti. Persone e imprese hanno requisiti quasi disgiunti (ISEE e nucleo da una parte, ATECO e dimensione dall'altra), quindi la prima domanda elimina subito metà delle domande possibili.
- Motivo: è l'idea originale del progetto. La decisione 1 era nata da quali dati erano disponibili, non da una scelta di prodotto.
- Con molte più domande possibili, il ramo persone è il caso in cui l'adattività del questionario può contare (decisione 11).

**23. Obiettivo: tutti i bandi aperti in Italia, con copertura misurata** (decisione di Edoardo, 29/10). Completa la 16: incentivi.gov.it non basta nemmeno per le imprese, oltre a non coprire le persone.
- Incompletezze trovate il 28/10 (`docs/copertura-portale.md`):
  - copertura irregolare tra regioni: Trentino-Alto Adige 129 bandi aperti, Lombardia 99, Sicilia 21, Lazio 19, Campania 18;
  - su un campione di bandi reali 2025-2026, 9 trovati su 13 verificati; mancano tutti e 4 i bandi FESR siciliani di ottobre 2025 e Valore artigiano 2026 del Lazio;
  - pubblicano solo 56 comuni su circa 7.900;
  - per legge il portale raccoglie le misure per il "tessuto produttivo" (art. 18-ter D.L. 34/2019); la pubblicità legale resta sui siti dei singoli enti (art. 8, c. 3, L. 160/2023);
  - nessun grande bonus per i cittadini nell'intero catalogo, anche tra i chiusi.
- Quindi si aggiungono altre fonti (INPS come da decisione 16, poi Agenzia delle Entrate, regioni, comuni, Camere di Commercio).
- Scartato: "copriamo tutto" come affermazione. Dichiariamo sempre quali fonti copriamo e misuriamo la copertura regione per regione, confrontando i nostri dati con gli elenchi ufficiali.
- Motivo: così "tutti" diventa un numero verificabile, e la copertura incompleta è un ostacolo vero da raccontare nel report.

**24. "Da verificare": il dettaglio diventa una lista finale, non domande** (decisione di Edoardo, 29/10). Integra la 18, il punto è lo stesso.
- Le domande coprono i requisiti principali (età, ISEE, residenza…). I requisiti di dettaglio (metri quadri dell'alloggio, categoria catastale, contratto registrato) restano `non_modellabile`.
- Per ogni bando "da verificare", alla fine compare l'elenco di questi requisiti, ognuno con la sua citazione, da controllare di persona.
- Scartato: trasformarli tutti in domande. Il questionario diventerebbe lunghissimo, e la maggior parte delle domande servirebbe a un solo bando.

**25. Bandi comunali: prima gli schemi regionali, poi "Amministrazione trasparente"** (decisione di Edoardo, 29/10).
- Molti contributi comunali nascono da fondi stanziati dalla regione (es. fondo affitti): si estrae lo schema regionale una volta e si registra quali comuni lo applicano, con le loro varianti.
- I bandi restanti si cercano nella sezione "Amministrazione trasparente → Sovvenzioni, contributi, sussidi, vantaggi economici", obbligatoria per legge (D.Lgs. 33/2013, art. 26).
- Scartato: sorvegliare a mano i siti di circa 7.900 comuni.
- ⚠ Da controllare:
  - quanta parte dei bandi comunali passa davvero dalla regione;
  - i fondi statali che arrivano agli ambiti sociali senza passare dalla regione;
  - i contributi pagati con il bilancio del comune;
  - i livelli intermedi: unioni di comuni, ambiti territoriali sociali;
  - la sezione trasparente non è sempre aggiornata, e spesso pubblica i contributi già erogati, non i bandi aperti.

## 7/11/2026

**31. Fonte generica per i bandi fuori da INPS e incentivi.gov.it, con moduli nostri accanto a quelli esistenti** (decisione di Edoardo; ⚠ provvisoria).
- `pipeline/fonti/documenti.py` scarica i documenti elencati in `data/fonti/documenti.yaml` (pagina web o PDF) e ne salva il testo, pagina per pagina, in `data/raw/documenti/<id>.json`. `pipeline/estrai_documenti.py` li passa all'estrattore.
- Si riusano istruzioni, vocabolario, schema e controllo delle citazioni di `pipeline/estrai.py` e `pipeline/citazioni.py`, importandoli: quei file non cambiano. Cambiano solo la fonte da citare (ente e pagina), le date del bando (`apertura`, `chiusura`) e il caso dei bandi non rivolti alle persone.
- Scartato: modificare `pipeline/estrai.py` per farlo leggere anche i documenti. Avrebbe toccato codice di Lorenzo già misurato (decisioni 28-30).
- Scartato: un modulo per ogni sito. Le pagine dei bandi hanno strutture diverse, ma al testo bastano due casi, HTML e PDF.
- Cortesia: robots.txt rispettato (401/403 = vietato), una richiesta al giorno per documento (copia in `data/cache/documenti/`), pause tra un sito e l'altro.
- I PDF richiedono `pypdf`: aggiunto a `requirements.txt` il 7/11 (⚠ da verificare con Lorenzo). I PDF scansionati vengono segnati `ocr_necessario` e saltati.
- Prima prova (7/11) su 3 bandi aperti: Toscana biotrituratori elettrici (PDF), Provincia di Trento prima casa 2026 (pagina web), Toscana buoni scuola infanzia (pagina web). Tutte le regole passano schema e citazioni al primo tentativo: `data/regole_estratte/documenti/`, non riviste.
- Cosa abbiamo imparato:
  - la lettura dei PDF spezza alcune parole ("QUALIT À", "esclusivam ente"): una citazione che cade lì viene rifiutata, quindi l'LLM deve scegliere un passaggio su una riga sola (è scritto nelle istruzioni aggiunte);
  - anche qui la maggior parte dei requisiti è `non_modellabile`: età del richiedente a una data fissa, numero di figli, provincia, indicatori locali come l'ICEF trentino, proprietà di casa o terreni;
  - i buoni scuola toscani sono uno "schema regionale" (decisione 25): la domanda si presenta al Comune, e le scadenze per le famiglie sono nei bandi comunali.

**32. All'LLM si mandano solo le sezioni del bando sui requisiti** (proposta di Edoardo, 7/11; `pipeline/fonti/sezioni.py`).
- Idea: quasi ogni bando ha una parte con i requisiti ("Beneficiari", "Requisiti di ammissione"…). Mandare solo quella costa meno, è più rapido e lascia fuori spese, procedure e privacy, dove l'LLM rischia di trovare falsi requisiti.
- Come si riconosce un titolo: "Art. N"; una riga numerata; una riga breve, senza punteggiatura finale, che comincia con una parola tipica dei titoli dei bandi. Le intestazioni ripetute in cima o in fondo alle pagine ("Allegato A") non contano come titoli.
- Cosa si tiene: le sezioni su requisiti, beneficiari ed esclusioni; quelle sui termini (per le date); gli articoli che queste richiamano ("di cui all'articolo 1.1": in Toscana l'elenco dei comuni sta lì); l'inizio del testo, se parla di requisiti (Genova non ha titoli). Si scartano le sezioni sul dopo ("Obblighi dei beneficiari").
- Se non c'è una sezione sui requisiti, si manda tutto il documento. Le citazioni si controllano sempre su tutto il testo.
- Scartato: usare solo l'indice del PDF. Nessuno dei tre PDF provati aveva segnalibri.
- Scartato: chiedere all'LLM di trovare la sezione. Costa quanto leggere tutto il documento, e la scelta non si potrebbe controllare.
- Prima misura (7/11, 3 bandi): si manda il 30-49% del testo. Su 17 citazioni trovate leggendo tutto il documento, 16 cadono nelle sezioni scelte. Quella persa è la categoria catastale della prima casa di Trento, che stava nella sezione "Descrizione".
- ⚠ È una misura piccola e di parte: le 17 citazioni le ha scelte lo stesso modello leggendo tutto il documento. Va ripetuta su più bandi, estraendo due volte (solo sezioni / `--tutto`) e confrontando con `pipeline/confronta.py`.

**33. Prima raccogliere tutti i bandi, poi estrarre** (decisione di Edoardo, 7/11; `pipeline/fonti/elenchi.py`).
- Il collo di bottiglia sono i dati, non il programma. La raccolta (trovare i bandi, scaricarli, salvarne il testo) non dipende dal vocabolario: si fa subito, per tutte le regioni. L'estrazione si rifà in blocco quando il vocabolario sarà sistemato, dopo le etichette; rifarla costa poco.
- Scartato: estrarre ogni bando appena raccolto. Con il vocabolario di oggi quasi tutti i requisiti risultano `non_modellabile` (lotto INPS del 7/11: 40 su 42), e il lavoro andrebbe rifatto.
- Ogni fonte è qualche riga in `data/fonti/elenchi.yaml`: indirizzo dell'elenco (con il numero di pagina), come si riconoscono i link ai bandi, e in che ordine cercare il PDF del testo ufficiale. Aggiungere una regione non richiede codice, se il suo elenco è una pagina HTML normale.
- Ogni giorno si salva l'elenco dei bandi di ogni fonte (`data/raw/elenchi/<fonte>_<giorno>.json`): confrontando due giorni si trovano i bandi nuovi. È il primo pezzo della sorveglianza continua, senza ancora un agente.
- Filtri dei siti usati quando ci sono: Piemonte per stato "Aperto" e per destinatari (cittadini, imprese); Sicilia "non scaduti" e solo "Avvisi pubblici" (niente gare d'appalto né concorsi).
- Stato al 7/11:
  - funzionano con una pagina HTML normale: Toscana, Piemonte, Sicilia;
  - caricano l'elenco con JavaScript, e per loro serve trovare l'indirizzo da cui il sito prende i dati: Veneto, Emilia-Romagna, Umbria, Lazio, Puglia, Basilicata, Sardegna (che usa `POST /api/search`);
  - FVG: la pagina "bandi e avvisi" ha solo avvisi sulle concessioni d'acqua; i contributi stanno nelle pagine di settore;
  - Lombardia: ha il dataset ufficiale "Anagrafica dei bandi regionali" (`docs/proposte-fase-2.md`, parte 3), che però non ha gli indirizzi dei bandi.
- ⚠ Da decidere: il testo di ogni bando pesa circa 50 KB. Fino a qualche centinaio di bandi sta in git; con migliaia conviene tenerlo fuori (come `data/cache/`) e rigenerarlo.
- Prima raccolta (7/11): **349 bandi aperti**. Toscana 156 (99 con il PDF ufficiale), Piemonte 41 (10 per cittadini e 31 per imprese, 33 con PDF), Sicilia 152 (128 con PDF). 24 PDF sono scansioni (20 siciliani): servirà l'OCR. Il testo pesa 12 MB.
- Errore trovato e corretto: l'id nasceva dal titolo tagliato a 50 caratteri, e 51 bandi con lo stesso inizio del titolo si erano sovrascritti. Ora l'id finisce con 6 cifre ricavate dall'indirizzo del bando, che sono uniche e non cambiano da un giorno all'altro. Contare i file contro le voci dell'elenco è il controllo che l'ha fatto vedere: va ripetuto a ogni raccolta.
- In Sicilia i link agli allegati sono scritti senza virgolette e si chiamano tutti "Scarica Allegato": si prende il primo.
- Seconda tornata (7/11), solo ricerche pubbliche e gratuite dei siti, senza chiavi né servizi a pagamento (`pipeline/fonti/api_regioni.py` per quelle con risposta JSON):
  - Sardegna: la pagina "Bandi" interroga `POST /api/search?index=contentrepository` (Elasticsearch). Si chiedono i contenuti BANDO con scadenza futura: 65, di cui 28 gare d'appalto (con CIG) scartate subito. I PDF stanno su `files.regione.sardegna.it`.
  - Basilicata: sito WordPress, con l'interfaccia standard `/wp-json/wp/v2/avvisi-e-bandi` (9.707 voci dal primo giorno). Si guardano le voci dell'ultimo anno e si tengono quelle con la "Scadenza" scritta nella pagina ancora futura.
  - Umbria: la pagina del sito è una cornice dell'applicazione `applicazioni.regione.umbria.it` (24 bandi aperti). Dagli indirizzi si toglie il codice di sessione (`jsessionid`), che cambia a ogni visita.
  - Veneto: le pagine dei bandi si leggono (`bandi.regione.veneto.it/Public/Dettaglio?idAtto=...`, con categoria e destinatari), ma l'elenco arriva solo ai browser. Il sito usa un sistema anti-robot (cookie OPLON-ADC): come per le Marche, non lo aggiriamo. ⚠ Chiedere alla Regione un elenco o un feed.
  - Emilia-Romagna: l'interfaccia Plone (`++api++/@search?portal_type=Bando`) funziona, ma il sito principale ha 0 bandi aperti oggi. I bandi veri stanno nei siti di settore (agricoltura, formazione e lavoro, imprese…): da trovare.
  - Lazio: la pagina "Avvisi e bandi" ha solo gare, concorsi e aste. I contributi stanno in Lazio Innova, Lazio Europa e nelle pagine "cittadini": da trovare. Puglia: la pagina "Bandi e avvisi" non ha un elenco leggibile: da trovare.
- Totale al 7/11: **419 bandi aperti da 6 regioni** (Toscana 156, Sicilia 152, Piemonte 41, Sardegna 37, Umbria 24, Basilicata 9), 315 con il PDF ufficiale, 25 scansioni da passare all'OCR. Il testo pesa 15 MB.
- Terza tornata (7/11):
  - Lombardia: il portale "Bandi e Servizi" riempie la lista con `POST /servizi/servizio/catalogo/ricerca` (modulo con `stato[0]=APERTO`, 100 schede per pagina, cookie di sessione). 428 voci aperte dopo aver tolto concorsi, avvisi sul personale e gare. I destinatari si leggono dalle icone della scheda (`citizen`, `factory`, `ente`), perché con più destinatari il testo non c'è: 166 bandi riguardano anche le persone.
  - Calabria: pagina filtrata sugli "avvisi", 11 voci, soprattutto elenchi di professionisti. I fondi europei stanno su un sito a parte, da trovare.
  - Corretto: un errore di rete su un bando (connessione chiusa dal server) fermava tutta la raccolta. Ora il bando viene segnato `NO` e si va avanti; rilanciando si riprende dalla copia del giorno.
- Totale: **858 bandi aperti da 8 regioni**, 540 con il PDF ufficiale. Il testo pesa 35 MB.
- **I testi dei bandi stanno fuori da git** (decisione di Edoardo, 7/11): `data/raw/documenti/` è in `.gitignore`, tranne i 3 documenti di prova citati dalle regole di `data/regole_estratte/documenti/`. In git restano gli elenchi del giorno (`data/raw/elenchi/`), che dicono cosa c'era e quando. Scartato: tenerli in git, perché con tutta Italia sarebbero centinaia di MB e restano per sempre nella storia. Il prezzo: per ricrearli servono circa 2 ore di scaricamento. I 15 MB caricati prima di questa decisione restano nella storia dei commit del 7/11.
- Veneto, Marche e Liguria (7/11): niente mail alle Regioni (decisione di Edoardo). I bandi sono pubblici, e una richiesta per un progetto universitario avrebbe ottenuto al massimo una scorciatoia, probabilmente con un no. Alternative cercate, senza aggirare protezioni:
  - **incentivi.gov.it** copre già una parte dei bandi per le imprese: aperti il 27/10 Veneto 36, Marche 23, Liguria 11. Mancano quelli per le persone.
  - **Liguria:** ALFA (agenzia regionale per formazione e lavoro) ha 9 avvisi, quasi tutti consultazioni di mercato. I bonus per le persone (nidi, caregiver, centri estivi, bonus sport, non autosufficienza) li gestisce FILSE, ma `bandifilse.regione.liguria.it` serve solo a fare domanda con SPID/CIE: l'elenco pubblico sta su regione.liguria.it, vietato dal robots.txt.
  - **Marche:** Fondazione Marche Cultura (1 bando aperto). ERDIS (diritto allo studio) da aggiungere. Il Bollettino (norme.marche.it) non risponde con un certificato valido.
  - **Veneto:** le pagine dei singoli bandi sono pubbliche e numerate (`Dettaglio?idAtto=13407`), ma l'elenco arriva solo ai browser. AVEPA (agricoltura) e Veneto Innovazione caricano gli elenchi con JavaScript. **Si leggono le pagine per numero** (decisione di Edoardo, 7/11): i bandi sono pubblici e le singole pagine sono accessibili a tutti. Si parte dal numero più alto visibile nella home e si scende di 650, una pagina per numero al giorno, con il nome del programma dichiarato e le pause. Scartato: rinunciare al Veneto, che non è coperto da nessuna fonte alternativa. Il limite, da dire: il sito ha scelto di non dare l'elenco ai programmi, e così lo ricostruiamo. Risultato: 38 bandi aperti (20 per le persone, 26 con PDF), tolti concorsi, gare, affidamenti diretti e ordini di fornitura.
- Corretto: gli indirizzi con caratteri non ASCII (l'apostrofo ’ negli indirizzi di ALFA) fermavano lo scaricamento. Ora si codificano come fa il browser.
- Totale al 7/11 sera: **909 bandi aperti da 11 regioni** (Lombardia 428, Toscana 156, Sicilia 152, Piemonte 41, Veneto 38, Sardegna 37, Umbria 24, Calabria 11, Liguria 9, Basilicata 9, Marche 1), 572 con PDF. Testi fuori da git, 37 MB.
- Quarta tornata (7/11 sera). I domini a cui puntano i link di incentivi.gov.it dicono dove le Regioni pubblicano davvero i bandi:
  - Emilia-Romagna: 8 siti di settore in Plone (agricoltura, formazione e lavoro, imprese, Agenzia lavoro, FESR, ambiente, sociale, parità), stessa ricerca `++api++/@search?portal_type=Bando` con scadenza futura: 93 bandi.
  - Lazio: Lazio Europa (41) e Lazio Innova (8), WordPress con filtro `stati`. Tra questi "Valore Artigiano 2026", che il 28/10 mancava su incentivi.gov.it.
  - Abruzzo: Coesione Abruzzo, 6 avvisi aperti (lo stato "Chiuso" è scritto prima del link: opzione `escludi_contesto`). Campania: PR FESR 2021-2027, 23 voci senza stato.
  - Raccoglitore: intestazione `Accept` standard (Sistema Puglia senza risponde 406), 404 dopo l'ultima pagina = fine elenco, più pagine fisse per fonte, titoli "Leggi tutto" puliti.
- **Doppioni** (`pipeline/fonti/doppioni.py`): stesso titolo normalizzato (almeno 4 parole) e stessa regione. Non si cancella niente: l'elenco dei gruppi va in `data/raw/elenchi/doppioni_<giorno>.json`, con primo l'id da tenere. Il 7/11: 14 doppioni, 3 tra i due siti del Lazio. Gli altri sono titoli uguali nella stessa fonte (Sicilia, Toscana), che potrebbero anche essere atti diversi: da controllare all'estrazione.
- Totale al 7/11 sera: **1.077 bandi raccolti da 15 regioni** (1.063 diversi tolti i doppioni), 668 con PDF. 196 dichiarano fra i destinatari le persone (solo Lombardia, Piemonte e Veneto lo dicono in modo leggibile; per gli altri lo dirà l'estrazione). Testi fuori da git, 44 MB.
- Mancano: Puglia (Sistema Puglia risponde, portale complesso), Valle d'Aosta (pagine "avvisi attivi" del lavoro), Molise (Finmolise), FVG, Trento e Bolzano (incentivi.gov.it ne copre già 122 per le imprese); Marche e Liguria solo in parte.
- Quinta tornata (7/11 notte): Puglia da Sistema Puglia, fase "Aperti" (15 misure, tra cui N.I.D.I., TecnoNidi, Maestro Artigiano; i PDF non si riconoscono ancora dal nome); Valle d'Aosta da imprese.regione.vda.it (9 misure per le imprese). Totale **1.101 bandi raccolti da 17 regioni**, 1.090 diversi tolti i doppioni.
- Restano senza raccolta diretta, ma con i bandi per le imprese già su incentivi.gov.it:
  - FVG (68 aperti il 27/10): il portale linka soprattutto leggi e pagine sparse;
  - Molise (11): Finmolise ha pagine di prodotto, non bandi con una scadenza;
  - Trentino-Alto Adige (122): il catalogo "Servizi" di Trento si carica con JavaScript, `civis.bz.it` risponde 403.
  Per le persone in queste regioni non abbiamo ancora fonti.

**34. Inventario degli enti che pubblicano bandi, dai dati e non a memoria** (richiesta di Edoardo, 7/11; `pipeline/fonti/inventario.py`, risultato in `docs/enti-per-regione.md`).
- Motivo: per ogni regione avevamo una sola fonte, e la consideravamo "fatta". Per difendere "tutti i bandi" serve sapere quali enti pubblicano e quali copriamo.
- Come: dall'export completo di incentivi.gov.it (6.007 incentivi, tutti gli anni) si prendono, per ogni regione, gli enti concedenti dei bandi regionali, il loro tipo (Regione, Camera di commercio, Comune, finanziaria, lavoro, agricoltura…) e i siti dove pubblicano. Un bando aperto è "coperto" se il suo sito è tra le pagine che raccogliamo da una fonte regolare (non bastano un allegato o un documento di prova).
- Scartato: un elenco di enti scritto a mano. Non si può dimostrare completo, e non dice quanti bandi ha ogni ente.
- Risultato (7/11): 1.567 enti in 20 regioni, 1.182 dei quali Comuni. Dei 680 bandi regionali aperti sul portale, 77 rimandano a un sito che raccogliamo.
- ⚠ Le due misure che abbiamo sbagliano in direzioni diverse. Il confronto per sito è troppo severo: il portale rimanda spesso a `regione.lombardia.it` o al Bollettino, mentre noi raccogliamo da `bandi.regione.lombardia.it`. Il confronto per titolo (67 ritrovati) lo è per un altro motivo: lo stesso bando ha titoli diversi. La copertura vera va misurata unendo le due e controllando a mano i casi incerti.
- Buchi sicuri, per tipo: **Camere di commercio** (100 enti, 110 bandi aperti, nessuno coperto), **Comuni** (74 aperti), **finanziarie regionali** (30 aperti, 5 coperti), **agenzie lavoro e formazione** (41 aperti, 3 coperti).
- Limite: il portale riguarda le imprese. Gli enti che fanno bandi solo per le persone (diritto allo studio, casa, servizi sociali, agenzie per il lavoro, Comuni capoluogo) vanno cercati a parte in ogni regione.

**35. Camere di commercio: pagine elenco ricavate dai link del portale** (7/11; `pipeline/fonti/camere.py`, risultato in `data/fonti/camere.yaml`).
- Non esiste un elenco nazionale dei bandi camerali: ogni Camera pubblica sul proprio sito (115 domini sul portale).
- Come: per ogni Camera con bandi dal 2025, la cartella che contiene le pagine dei suoi bandi sul portale è di solito la pagina elenco. Se non lo è (cartella sparita, trasparenza, gare), si segue il link "Bandi"/"Contributi" della home. Si apre la pagina, si contano i link ai bandi e la Camera entra nella configurazione generata. Quando i bandi stanno in un'altra cartella, si prendono i link del contenuto principale (`solo_contenuto`).
- Controlli, aggiunti guardando i risultati: solo siti camerali (non aziende speciali né associazioni), niente doppioni (`bs.` = `www.bs.`), niente concorsi, gare o trasparenza, niente pagine di un singolo bando, al massimo 60 link nel contenuto (a Cosenza erano 318: tutto il sito).
- Scartato: 100 configurazioni scritte a mano. Sono lente, non si possono rifare quando i siti cambiano, e non dimostrano di non aver dimenticato nessuno.
- Risultato: 40 Camere su 60, **306 bandi** (160 con PDF; 9 non scaricati per errori dei siti). I bandi camerali aperti sul portale coperti passano **da 0 a 68 su 110**.
- ⚠ Restano da fare a mano 20 Camere, tra cui Milano, Napoli, Salerno, Verona, Sassari, Caserta, Cosenza, Trapani, Padova e Bolzano: non hanno una cartella riconoscibile né un link "Bandi" leggibile nella home.
- Totale: **1.410 documenti, 1.390 bandi diversi** tolti i doppioni. Testi fuori da git, 57 MB.

**36. Perché i bandi delle Regioni sul portale risultano così poco coperti, e cosa fare** (7/11).
- Dei 382 bandi aperti delle Regioni e Province autonome, ne ritroviamo 88: 54 per titolo, 66 per sito, contando una volta sola quelli trovati in tutti e due i modi. Dei 294 che mancano, **circa la metà sta in tre territori che non abbiamo ancora raccolto**: Trentino-Alto Adige (≈87: Provincia di Trento, portale civis di Bolzano, Bollettino), Friuli-Venezia Giulia (≈36: protezione civile, pagine regionali, testi di legge) e Marche (18, dietro captcha). Le altre 17 regioni hanno sul portale pochi bandi "della Regione": il conteggio "17 regioni su 20" sopravvalutava la copertura.
- Il resto è in siti regionali che non leggiamo (`regione.puglia.it`, Calabria Europa, `regione.lombardia.it`, sportello SUS della Sardegna, `regione.vda.it`, `regione.toscana.it`) e nelle finanziarie.
- **Le finanziarie regionali sono una priorità** (osservazione di Edoardo): hanno spesso i bandi più interessanti per le imprese, e sul portale stanno quasi tutti a nome della Regione, quindi dal nome dell'ente non si vedono (l'inventario ne riconosce solo 53, con 30 bandi aperti). Elenco verificato il 7/11 in `docs/da-fare.md`, sezione 5.

**37. Finanziarie regionali: 16 fonti, una per sito, con il filtro "aperto" del sito quando c'è** (7/11; `data/fonti/elenchi.yaml`, `pipeline/fonti/api_regioni.py`, controllo in `pipeline/fonti/conta.py`).
- Per ognuna delle 19 finanziarie verificate (decisione 36) si è cercata la pagina dei bandi aperti. Se è HTML normale basta una voce in `elenchi.yaml` (13 fonti); se si carica con JavaScript si interroga la stessa richiesta che fa la pagina (3 fonti in `api_regioni.py`):
  - **Finlombarda**: `ajax-filter-prodotti`, stato aperto o in apertura, pubblico imprese e professionisti (non PA). Risponde solo con l'intestazione `X-Requested-With`, come la manda jQuery;
  - **Trentino Sviluppo**: POST a `/it/getjson/list/callForTenders` con i parametri scritti nella pagina; dà anche il PDF del bando;
  - **Calabria Europa**: la pagina "Bandi" di Fincalabra legge un file JSON pubblico con tutto il catalogo di `calabriaeuropa.regione.calabria.it` (299 voci, ognuna con il suo stato). Copre anche un buco di da-fare (Calabria Europa, 13 bandi aperti sul portale).
- Filtri usati quando il sito li ha: Finpiemonte stato "Aperto" (20 su 222), Sviluppo Toscana "aperto" senza le fasi di varianti e rendicontazione (7 su 40), ART-ER "procedure in corso", IRFIS "Avvisi aperti", Sardegna Ricerche "in corso", Calabria Europa aperti/pubblicati/pre-informazione. Gare, selezioni di personale ed elenchi di fornitori si scartano.
- Finaosta e Finmolise non hanno bandi a scadenza ma prodotti sempre aperti (mutui agevolati prima casa, imprese, agricoltura; garanzie, microcredito): si raccolgono le pagine dei prodotti, che per le persone e le imprese sono incentivi veri.
- Veneto Sviluppo: dal 2026 le agevolazioni le gestisce Veneto Innovazione (`agevolazioni.venetoinnovazione.it`), che si raccoglie al suo posto.
- Scartate, con il motivo: Sviluppo Basilicata (robots.txt), Sviluppo Campania (il 7/11 "Bandi aperti" ha solo selezioni di personale e albi), Friulia (partecipazioni e microcredito, nessun bando), FIRA (notizie su bandi di altri enti, non bandi suoi), SVEM per le Marche (pubblica sul portale della Regione, dietro captcha).
- Parziali: FILSE (l'elenco si carica da `/components/`, vietato da robots.txt: si leggono i bandi in evidenza nella home) e Sviluppumbria (elenco in JavaScript: si legge la home). ART-ER mette gli avvisi su Google Drive, che dà un'anteprima e non il PDF.
- Opzioni nuove del raccoglitore, ognuna con un test: i testi di link generici ("DETTAGLI", "Per maggiori informazioni", un indirizzo) non valgono come titolo, e tra più link allo stesso bando vale il testo più lungo (prima vinceva l'ultimo: con Finpiemonte tutti i titoli sarebbero stati "DETTAGLI"); `titolo_da` (dove sta il titolo, nel `<title>` o nel testo: Gepafin, FILSE, Sardegna Ricerche); `allegato_nome_file` (il PDF si riconosce dal nome del file quando i link dicono solo "Download": FILSE, Finmolise); gli allegati `/attachments/` di Finlombarda contano come documenti. Corretto anche il salvataggio dei PDF con caratteri spezzati (Calabria Europa si fermava al quinto bando).
- Scartato: una configurazione scritta a mano con l'elenco dei bandi di ogni finanziaria. Non vedrebbe i bandi nuovi, ed è proprio la sorveglianza quotidiana che vogliamo.
- Controllo: dopo ogni raccolta `python -m pipeline.fonti.conta` confronta l'elenco del giorno con i file salvati. Le 16 fonti nuove tornano tutte (file = voci, nessun id doppio). 7 pagine elenco di Camere hanno 1-3 bandi non salvati per errori dei siti già visti il 7/11.
- Risultato: **266 documenti nuovi** (Finlombarda 32, Veneto Innovazione 27, Sardegna Ricerche 23, Gepafin 21, Finpiemonte 20, Calabria Europa 48, Finaosta 15, SFIRS 14, IRFIS 13, ART-ER 12, Puglia Sviluppo 10, Trentino Sviluppo 8, FILSE 7, Sviluppo Toscana 7, Sviluppumbria 5, Finmolise 4), 204 con il PDF del testo ufficiale. Totale: 1.676 documenti, **1.648 bandi diversi** (prima 1.390).
- Copertura per sito dei bandi regionali aperti sul portale: **da 146 a 192 su 680**. Bandi delle Regioni coperti da 66 a 101 su 382, delle finanziarie da 5 a 16 su 30: conferma che sul portale i bandi delle finanziarie stanno a nome della Regione. Le regioni che guadagnano di più sono Calabria (da 3 a 16), Sardegna (da 3 a 13), Umbria (da 0 a 5), Veneto (da 4 a 8).
- ⚠ Sardegna Ricerche, Gepafin, SFIRS e Calabria Europa mescolano bandi vecchi o hanno stati poco affidabili: lo dirà l'estrazione dalla scadenza. Puglia Sviluppo ha una pagina per tipo di impresa con 1-3 misure ciascuna (PIA, MiniPIA…), non una per bando.

**38. Regioni senza raccolta e agenzie per il lavoro: cosa si può leggere** (7/11, richiesta di Edoardo: continuare a raccogliere, per farsi anche un'idea dei requisiti).
- **Friuli-Venezia Giulia** (`fvg`): non c'è un elenco unico dei bandi; ogni settore del sito (38 pagine, da "artigianato" a "politiche per la famiglia") elenca le sue "foglie". Si tengono solo quelle il cui titolo nomina un bando, un avviso, un anno dal 2025 o il programma 2021-2027, e non dice "chiuso" o "graduatoria" (opzione nuova `testo_bando`, con test): **142 foglie**.
  - Scartato: il filtro largo ("contributi", "incentivi"), che dava 541 foglie: circa un'ora di download su un solo sito, troppo (Edoardo). Le altre si possono aggiungere a lotti nei giorni successivi.
  - Non letti: `bandiformazione.regione.fvg.it` risponde 403; i 15 rimandi del portale a testi di legge (`lexview-int`) non sono un elenco; la protezione civile ha pagine per emergenza, non un elenco di bandi.
- **Provincia di Bolzano**: `civis.bz.it` oggi risponde (il 7/11 mattina dava 403), ma il catalogo dei servizi si carica da `/_services/search`, e robots.txt vieta tutto ciò che comincia con `/_`. Il nuovo `provincia.bz.it` è un'applicazione JavaScript che arriva vuota. **Nessuna strada permessa trovata**, come per Trento (vedi da-fare).
- **Marche**: il Fondo Nuovo Credito della Regione ha un sito suo, Credito Futuro Marche (`marche-credito-futuro`). Oggi "Nessun bando attivo": si tiene per accorgersi quando riapre. Il resto della Regione resta dietro captcha.
- **Agenzie per il lavoro e la formazione**: delle 41 voci aperte sul portale, 20 sono lo stesso bando nazionale INAIL ISI ripetuto in ogni regione, 11 sono foglie FVG (ora raccolte). Aggiunte: **INAIL** (ISI 2024, ISI 2025, bando formazione; livello nazionale, un documento per bando), **Veneto Lavoro** (voucher e bandi del Fondo regionale disabili, 6), **ASPAL** Sardegna (ultimi 40 avvisi, tolti albo pretorio e indagini di mercato: 31, tutti con PDF). ASPAL non ha uno stato: lo dirà l'estrazione.
- Durante la raccolta FVG (7/11 sera) la rete è caduta: 46 foglie non scaricate per errori di DNS. Si sono riprese l'8/11 con l'opzione nuova `--solo-mancanti` (riusa l'ultimo elenco e scarica solo le voci senza documento, con test), senza rileggere l'elenco né riscaricare le 96 già salvate. Ne resta una, per un errore 500 del sito.
- Risultato: FVG 141 foglie su 142, ASPAL 31, Veneto Lavoro 6, INAIL 3, Credito Futuro Marche 1. Totale **1.858 documenti, 1.830 bandi diversi** (prima 1.648).
- Copertura per sito dei bandi regionali aperti sul portale: **da 192 a 220 su 680**. FVG da 1 a 25 su 68, lavoro e formazione da 3 a 17 su 41, Regioni da 101 a 111 su 382. Trentino-Alto Adige resta a 1 su 122 (robots.txt, vedi da-fare).

**39. I buchi più facili: siti citati dal portale che rispondono e hanno un elenco** (8/11, richiesta di Edoardo; Trento e Bolzano dopo, partendo dagli indirizzi del portale).
- Metodo: i bandi regionali aperti sul portale, raggruppati per il sito a cui rimandano, tolti i siti che raccogliamo già. Si prendono quelli che robots.txt permette e che hanno una pagina elenco leggibile, partendo dai più citati.
- Aggiunti:
  - **Valle d'Aosta Lavoro** (`valle-aosta-lavoro`): l'elenco dei bandi aperti ha link `href="#"` con l'indirizzo dentro un comando JavaScript. L'opzione nuova `link_js` (con test) legge l'indirizzo dal testo del comando, senza eseguire niente. Concorsi e selezioni di personale si scartano dal titolo;
  - **Camera di Arezzo-Siena** (`camera-as`) e **Camera di Como-Lecco** (`camera-comolecco`): non le trovava il metodo automatico di camere.yaml.
- Scartati, con il motivo:
  - `regione.lombardia.it` (20): rimanda in gran parte agli stessi bandi di `bandi.regione.lombardia.it`, che raccogliamo;
  - `regione.puglia.it` (15): nessun elenco leggibile (decisione 33);
  - `sus.regione.sardegna.it` (11): applicazione JavaScript con indirizzi `#/`;
  - `bur.regione.veneto.it` (15), Bollettini, testi di legge: non sono elenchi di bandi;
  - `regione.lazio.it` (5): documenti sparsi, senza elenco;
  - `lavoro.regione.campania.it`: "Avvisi e Bandi" è il servizio per presentare domanda, con registrazione.
  - Il portale rimanda ancora a vecchi indirizzi di `imprese.regione.vda.it` (`bandi-e-avvisi/...`) che oggi danno 404: quei bandi li raccogliamo già con il nuovo indirizzo.
- Risultato: Valle d'Aosta Lavoro 7, Camera Arezzo-Siena 4, Camera Como-Lecco 6. Totale **1.875 documenti, 1.847 bandi diversi**. Copertura per sito dei bandi regionali aperti sul portale: **da 220 a 234 su 680** (Camere da 68 a 80 su 110, Lombardia da 32 a 38, Toscana da 25 a 31, Valle d'Aosta da 10 a 12).

## 8/11/2026

**40. Tolto il Congedo per le donne vittime di violenza dalle etichette** (8/11, scelta di Edoardo).
- Il requisito centrale è essere vittima di violenza di genere. Il sito non può chiederlo, nemmeno come "da verificare": è una domanda di cattivo gusto e un dato che non vogliamo trattare, come i dati giudiziari (vocabolario persone, scelta 1).
- Alternative scartate: tenerlo con un `non_modellabile` (misura un requisito che non chiederemo mai); sostituirlo subito con un'altra scheda INPS (meglio decidere insieme se usare il posto per un bando regionale, da-fare sezione 3).
- Le etichette a mano passano da 15 a 14 benefici. Resta da decidere se il beneficio va escluso anche dal sito o mostrato solo come informazione, senza domande.

**41. Due campi nuovi per le persone: tipo di lavoro e reddito del richiedente** (8/11, decisione di Edoardo dopo la prima misura dell'estrazione).
- `tipo_lavoro` (`dipendente`, `autonomo`, `parasubordinato`) e `reddito_richiedente` (reddito complessivo IRPEF dell'anno prima, in euro).
- Motivo: molte prestazioni INPS si dividono fra lavoratori dipendenti e autonomi, e alcune hanno una soglia sul reddito personale invece che sull'ISEE. Senza questi campi, la condizione diventa "da verificare" sia nelle etichette sia nelle estrazioni (3 etichette su 8 per il tipo di lavoro).
- Alternative scartate: lasciarli `non_modellabile` (l'esito resta "da verificare" proprio sul requisito che decide); dedurre il tipo di lavoro da `ultimo_lavoro_subordinato` (vale solo per chi ha perso il lavoro).
- Da fare: lo schema e il vocabolario sono di Lorenzo (da-fare, sezione 1). Dopo, le etichette che oggi hanno questi `non_modellabile` vanno riscritte con i campi nuovi.

**42. Trento e Bolzano dai link del portale; il diritto allo studio universitario; il Crawl-delay** (8/11, richiesta di Edoardo: "dobbiamo avere quasi tutti i bandi aperti in Italia").
- **Crawl-delay:** prima la pausa era sempre 3 secondi. Ora `documenti.attesa` legge il `Crawl-delay` di robots.txt e aspetta il più lungo tra quello, i 3 secondi e la `pausa` della fonte (opzione nuova di elenchi.yaml). Vale per elenchi.py e documenti.py, con test. A Trento il `Crawl-delay: 10` è scritto ma commentato: si rispetta lo stesso, con `pausa: 10`.
- **Trento e Bolzano** (possibilità a della decisione 38, scelta di Edoardo): il catalogo dei servizi passa da indirizzi vietati da robots.txt, le pagine dei singoli servizi no. L'opzione nuova `dal_portale` (con test) prende dall'export di incentivi.gov.it i bandi aperti oggi con il link su quei siti, e scarica le loro pagine come se venissero da un elenco. Esclusi: il Bollettino regionale (`/pdf` vietato da robots.txt), le pagine di ricerca delle delibere e le home.
  - Risultato: Trento 39 su 42 (3 pagine non esistono più, "410 Gone": bandi chiusi), Bolzano 33 su 33 (2 recuperati con `--solo-mancanti` dopo errori di rete).
  - Limite: si vedono solo i bandi che il portale conosce, non quelli nuovi né quelli per le persone che il portale non elenca. Per questo l'inventario li conta in una colonna a parte, "presi dal portale", e non come sito coperto: altrimenti la copertura sarebbe circolare (misurata sul portale con dati presi dal portale).
- **Diritto allo studio universitario** (borse di studio, alloggi, contributi agli studenti): sono bandi per le persone, il portale non li elenca. Aggiunte 9 agenzie: ER.GO (Emilia-Romagna), DSU Toscana, EDISU Piemonte, ESU Verona, DiSCo Lazio, ADISU Puglia, ERDIS Marche, ARDiS FVG, ADISURC Campania. Ogni agenzia ha una pagina per beneficio, stabile da un anno all'altro: si raccolgono quelle, e il PDF del bando quando la pagina lo collega. Bandi di gara, graduatorie, mensa e pagine di servizio si scartano.
  - Risultato: 42 documenti, tutti scaricati. Il PDF del bando c'è per EDISU, ADISU, ARDiS e DiSCo; per ER.GO, ESU Verona, DSU Toscana e ADISURC c'è solo il testo della pagina (da completare, da-fare sezione 5).
- Alternative scartate: per Trento e Bolzano, scrivere alle Province (possibilità b, più lenta, resta aperta); per il diritto allo studio, cercare un elenco nazionale (non esiste: ogni regione ha la sua agenzia, e in Lombardia lo gestiscono le università).
- Totale: **1.989 documenti, 1.960 bandi diversi** (prima 1.847). Bandi regionali aperti sul portale: **234 con il sito coperto + 83 presi dal portale, su 680** (prima 234). Trentino-Alto Adige da 1 a 84 su 122.

**43. Tutto il diritto allo studio raggiungibile, e i buchi delle regioni dai link del portale** (8/11, richiesta di Edoardo: "inizia con tutti i diritti allo studio universitario e su ciò che ci manca delle regioni").
- **Diritto allo studio, seconda parte:** 12 agenzie in più, ESU Padova, ALiSEO Liguria, ERSU Palermo, Catania, Messina, Enna e Cagliari, ADSU L'Aquila e Teramo, ESU Molise, ADiSU Umbria, Opera Universitaria di Trento: 35 documenti. In tutto 21 agenzie e 79 documenti. Molte pubblicano i bandi tra le notizie: graduatorie, pagamenti, errata corrige e avvisi di servizio si scartano dal titolo o dall'indirizzo.
  - Completati i PDF del bando per ER.GO (338 pagine), DSU Toscana e ADISURC: le pagine dei benefici non lo collegano, la pagina del bando sì. Per ER.GO il link dice solo "Scarica": conta il nome del file (`allegato_nome_file`).
  - Testi di link nuovi trattati come generici (con test): "Vai alla pagina", "Visita", "link", "Leggi il bando >>". Tolto dai titoli il resto di un commento HTML (". -->", ERSU Cagliari).
  - Non raccolte: ESU Venezia (applicazione JavaScript), ERSU Sassari e ADSU Chieti-Pescara (certificato HTTPS non valido: non lo si scavalca), ARDSU Basilicata (la home non risponde con una pagina), Calabria (le borse le danno le università), Lombardia (università), Valle d'Aosta e Bolzano (uffici della Regione e della Provincia).
- **Buchi delle regioni:** come per Trento e Bolzano (decisione 42), una fonte `portale-<regione>` per ognuna delle 19 regioni con i bandi aperti oggi del portale sui siti che non raccogliamo. Opzione nuova `solo_regione` (con test): lo stesso sito può avere bandi di più regioni (albocamerale.camcom.it), e si tengono solo quelli della regione della fonte. Fuori: enti nazionali (INAIL, MIMIT, SIMEST), link rotti o accorciati, il portale delle Marche (captcha), le home page.
  - Risultato: 149 pagine su 167. Le 18 mancanti: 11 link morti (404 o 410: bandi chiusi o spostati), 5 certificati HTTPS non validi, 2 siti che non rispondono (anche al secondo tentativo).
- Alternative scartate: aggirare i certificati non validi (no: è una protezione); per i buchi regionali, scrivere un elenco per ogni sito (troppi siti con 1-2 bandi ciascuno).
- Totale: **2.175 documenti, 2.145 bandi diversi** (prima 1.960). Bandi regionali aperti sul portale (680 al 27/10, di cui 649 ancora aperti l'8/11): **234 con il sito coperto + 279 presi dal portale = 513**. Quelli che restano sono soprattutto su siti che non si possono leggere (captcha, robots.txt, certificati) o non hanno più la pagina.

**44. Agenzie per il lavoro: solo ARPAL Umbria per ora** (8/11).
- Aggiunta ARPAL Umbria (`arpal-umbria`): le pagine degli avvisi ATTIVI per le persone (lavoro e formazione), 2 avvisi (RE-WORK, voucher formativi).
- Guardate e non aggiunte: Agenzia del Lavoro di Trento e Agenzia regionale per il lavoro dell'Emilia-Romagna (l'elenco degli avvisi si carica con JavaScript, nell'HTML non ci sono i link), ARPAL Liguria (in home solo i concorsi per il personale), AFOL Metropolitana (selezioni e avviamenti a selezione, non bandi per le persone), Calabria Lavoro (applicazione JavaScript).
- Università lombarde (borse di studio, decisione 43): gli indirizzi delle pagine sul diritto allo studio non si indovinano (404 quasi ovunque). Meglio trovarle a mano che fare richieste a caso ai loro siti.
- Totale: 2.177 documenti.

**45. Case popolari: 6 aziende per la casa, 17 documenti** (8/11, richiesta di Edoardo).
- I bandi per l'assegnazione degli alloggi E.R.P. li fanno i comuni; alcune aziende per la casa li ripubblicano, insieme ai loro avvisi per le persone (canone concordato o calmierato, fondo affitto, morosità incolpevole, contributi). Aggiunte: ATER Venezia (2 bandi E.R.P. di comuni), ARTE Genova (2 PDF: un bando E.R.P. e posti letto), ALER Milano (contributo per il riscaldamento), ATC Piemonte Sud (3 bandi di comuni), ATER Vicenza (2 avvisi a canone agevolato e la pagina dei bandi E.R.P.), ACER Ferrara (6 avvisi: fondo affitto 2026, rinegoziazione degli affitti, morosità incolpevole, alloggi a canone calmierato).
- Si scartano aste e vendite, gare, lavori, graduatorie, selezioni di personale, chiusure degli sportelli e avvisi degli anni passati. Tolto dai titoli il prefisso "su:" (ACER Ferrara), con test.
- Guardate e non aggiunte, con il motivo: ACER Bologna, ATC Torino, AREA Sardegna, ATERP Calabria, Casa SpA Firenze (gli elenchi si caricano con JavaScript o non collegano i bandi); ACER Modena (aste e una pagina sul canone concordato); ACER Campania (solo locali commerciali); ATER Verona (la pagina dei bandi dei comuni non ha i link nell'HTML); ATER Roma e ITEA Trento (certificato HTTPS non valido); ERAP Marche e ATER Umbria (non rispondono); IPES Bolzano (applicazione JavaScript). Per ATER Padova, Treviso, Trieste, Udine, Pordenone, ARCA Puglia e ACER Reggio Emilia l'indirizzo provato non esiste: vanno trovati gli indirizzi giusti.
- Il resto delle case popolari passa dai comuni (decisione 25): è il buco più grande della raccolta per le persone.
- Totale: **2.194 documenti**.

**46. Comuni capoluogo, primo giro: 17 comuni, 38 documenti** (8/11, richiesta di Edoardo).
- Quasi tutti i capoluoghi hanno il sito del modello nazionale per i comuni (Designers Italia), con una pagina "Avvisi" tra le notizie. Lì i bandi per le persone (contributi, bonus, voucher, nidi, libri di testo, affitti) stanno insieme a viabilità, scioperi, elezioni, gare, concorsi e graduatorie. Per tutti la stessa regola: si tengono le notizie il cui titolo parla di bandi, contributi, bonus, voucher, sostegni, rimborsi; si scartano le altre dal titolo. Si legge solo la prima pagina, cioè le notizie più recenti.
- Raccolti (con bandi pertinenti oggi): Napoli, Torino, Bari, Aosta, Perugia, Livorno, Prato, Lucca, Salerno, Taranto, Foggia, Messina, Catania, Reggio Calabria, Pescara. Tenuti anche Palermo e Rimini: si leggono, ma oggi non hanno avvisi di questo tipo.
- Non raccolti, con il motivo:
  - l'elenco si carica con JavaScript: Roma, Genova, Cagliari, Trento, Brescia, Modena, Verona, Vicenza, Sassari, Parma, Reggio Emilia, Ravenna, Ferrara, Pisa, Udine, Novara, Monza (questi ultimi con zero risultati, da verificare uno per uno);
  - robots.txt vieta tutto il sito: Milano, Bolzano;
  - certificato HTTPS non valido: Lecce;
  - l'indirizzo provato non esiste o la home è vuota: Ancona, Bologna, Firenze, Venezia, Padova, Treviso, Trieste, L'Aquila, Potenza, Campobasso, Bergamo.
- **Siti in JavaScript: si possono leggere, ma non tutti.** Il browser esegue un programma che chiede l'elenco al server in un formato per i programmi (JSON); noi scarichiamo solo la pagina, che arriva vuota. Si può chiedere direttamente quel JSON, come si fa già per Lombardia, Finlombarda, Trentino Sviluppo e Calabria Europa, se robots.txt lo permette. Prova dell'8/11: Modena (sito Plone/Volto, come molti comuni dell'Emilia-Romagna) risponde in JSON all'indirizzo `/++api++/novita/avvisi`, e il suo robots.txt non vieta niente. Invece i siti OpenCity (Trento, Verona e altri) vietano `/api/` in robots.txt: lì no. Alternativa scartata per ora: un browser automatico (Playwright o Selenium) che esegue il JavaScript. È una dipendenza pesante (un browser intero da installare), quindi è una scelta di stack da fare insieme (decisione 13), e non cambierebbe niente dove robots.txt vieta gli indirizzi dell'elenco.
- Totale: **2.232 documenti, 2.202 bandi diversi**.

**47. I comuni capoluogo dal generatore; prima misura di cosa il vocabolario non copre** (8/11, Edoardo: "prima quelli che vengono più semplici", e "con quel breve dizionario riusciremo a indirizzarli tutti?").
- **Generatore** `pipeline/fonti/comuni.py` (con test), come `camere.py` per le Camere: per ogni comune di `data/fonti/capoluoghi.yaml` apre la home, trova il link "Avvisi", controlla che la pagina elenchi almeno 3 notizie leggibili nell'HTML e scrive la fonte in `data/fonti/comuni.yaml`, con gli stessi filtri sul titolo dei capoluoghi della decisione 46. I comuni che non vanno si scrivono in fondo, con il motivo. `elenchi.py` legge `comuni.yaml` come `camere.yaml`.
  - Risultato su 63 capoluoghi di provincia: 30 con una fonte, 60 documenti, tutti scaricati. Gli altri 33: 13 senza link "Avvisi" nella home (home vuota o fatta con JavaScript), 16 con l'elenco caricato con JavaScript, Varese (robots.txt vieta il sito), Savona e Trapani (la home non risponde o certificato non valido).
- **Il vocabolario basta?** Conteggio delle parole chiave nei 279 documenti per le persone raccolti finora (bandi dei comuni, diritto allo studio, case popolari e le fonti segnate "persone"). È una stima per eccesso: una parola può comparire senza essere un requisito.
  - Coperti dai campi di oggi: ISEE (28% dei documenti), cittadinanza e permesso (19%), età (20%, ma solo dei componenti del nucleo), stato occupazionale (7%).
  - Coperti a metà: **residenza (40%)**: regione e comune ci sono già (il prompt dei documenti li usa per la residenza), manca da quanti anni (correzione dell'8/11, dopo la misura 48); **disabilità (33%)**, che nel vocabolario è solo dei componenti del nucleo; figli (14%).
  - Senza campo: **studente iscritto** (università, scuola, ITS: 14%), merito (crediti, voti: 14%), **affitto o contratto di locazione (13%)**, lavoro dipendente o autonomo (6%, già deciso nella 41), reddito personale (5%, già deciso), morosità o sfratto (6%), proprietà della casa (3%).
  - Quindi no, con il vocabolario di oggi i bandi regionali e comunali per le persone finirebbero quasi tutti in "da verificare". La proposta di campi nuovi è in da-fare, sezione 1. Schema e vocabolario sono di Lorenzo: si decidono insieme, poi si rifà la misura.
- Totale: **2.292 documenti, 2.261 bandi diversi**.

**48. Misura sui bandi per le persone: 74% dei requisiti "non modellabile"** (8/11, richiesta di Edoardo: "misura").
- 10 documenti per le persone presi dalla raccolta, di tipi diversi: 3 comuni (Perugia famiglie numerose, Lucca caro energia, Bari abbonamento bus), 2 case popolari (ACER Ferrara fondo affitto, bando E.R.P. di Dolo), 2 diritto allo studio (ERSU Palermo, DiSCo Lazio), FVG mutuo prima casa, FILSE voucher master, Veneto Lavoro voucher disabilità. Estrazione alla cieca con `pipeline/estrai_documenti.py` (prompt di oggi, sezioni sui requisiti), fatta da agenti che vedevano solo il prompt. Tutte le risposte passano schema e citazioni.
- Risultato: **58 condizioni, 43 non modellabili (74%)**. Campi usati: ISEE 5, regione 3, cittadinanza 3, comune 2, età 1, mesi dall'evento 1. Per confronto, sulle 5 schede INPS di sviluppo le estrazioni ne avevano 21 e il riferimento a mano 10 (decisione 30).
- I 43 per motivo:
  - **un campo nuovo li coprirebbe (circa 17):** ISEE specifici (ISEE universitario, ISPE, ISEE-ERP: 4), titolo di studio posseduto (3), proprietà o affitto della casa e contratto registrato (3), iscrizione all'università (2), numero e età dei figli (2), domicilio senza residenza (2), anni di residenza nella regione (1);
  - **restano "da verificare" anche con campi nuovi (circa 26):** merito e carriera universitaria (crediti, ripetenze, durata), benefici già avuti, debiti verso l'ente, condanne, durata del permesso di soggiorno, Carta famiglia, dettagli del singolo bando (date d'esame, abbonamenti annullati). Sono requisiti veri ma troppo specifici per una domanda: vanno nella lista finale "da verificare" con la citazione (decisione 24).
  - Stima: con 6-7 campi nuovi i non modellabili scenderebbero da 74% a circa 45%. Va verificata rifacendo l'estrazione sugli stessi 10 documenti dopo aver aggiunto i campi.
- Due problemi trovati:
  - Lucca: l'estratto delle sezioni sui requisiti (`pipeline/fonti/sezioni.py`, decisione 32) ha tenuto il titolo dell'articolo 1 ma non il suo testo, e il modello non ha trovato i requisiti. Da correggere prima dell'estrazione in blocco;
  - Veneto Lavoro: l'avviso è rivolto agli enti che erogano i servizi, non alle persone. Il modello l'ha riconosciuto (nessun requisito, con la spiegazione): va tolto dai bandi per le persone.
- Risposte e regole in `scratchpad/misura3` (fuori dal repository); da rifare in `data/regole_estratte/documenti/` quando i campi ci sono.

**49. Lombardia: le università dalla ricerca web, e una strada "a mano" per i siti che rifiutano i programmi** (9/11, richiesta di Edoardo: "in Lombardia avere così pochi accessi è un problema").
- **Perché Milano non si legge.** Il Comune di Milano e Milano Abitare (l'agenzia del Comune per l'affitto) rispondono 403 a ogni richiesta del nostro programma, anche a robots.txt: è un filtro che blocca i programmi, non un errore. Una persona col browser invece entra. Fingersi un browser per passare quel filtro vorrebbe dire aggirare una protezione anti-robot: è escluso dalle regole del progetto (brief) e lo blocca anche il controllo automatico dei comandi. Anche `dati.comune.milano.it` risponde 403.
- **Strade permesse, usate:**
  - **università lombarde**, che in Lombardia danno da sole le borse (non c'è un'agenzia regionale): gli indirizzi dei bandi 2026/2027 trovati con una ricerca web, e robots.txt li permette. Aggiunti come documenti singoli (`data/fonti/documenti.yaml`): Milano-Bicocca, Statale, Insubria, Bergamo, LIUC, San Raffaele (6 PDF, 196 pagine). Mancano Politecnico, Pavia, Brescia e Cattolica: la ricerca non ha trovato il bando DSU;
  - **open data della Regione** (`dati.lombardia.it`, robots.txt permette l'API): c'è l'"Anagrafica dei bandi regionali", ma sono i bandi regionali che raccogliamo già dall'API della Regione. Non aggiunge bandi.
- **Strada nuova per i siti bloccati: il salvataggio a mano** (`pipeline/fonti/manuali.py`, con test). Una persona apre il bando nel suo browser, salva il PDF o la pagina in `data/raw/manuali/` (fuori da git) e lo descrive in `data/fonti/manuali.yaml`; il modulo ne estrae il testo come per gli altri documenti, con `fonte_elenco: manuale`. L'inventario li conta a parte, come quelli presi dal portale: non sono un sito sorvegliato. Vale anche per le Marche (captcha).
- **Restano da provare:** scrivere al Comune di Milano per chiedere di lasciar passare il nostro programma o un export dei bandi aperti (open data). Va fatto da una persona.
- Alternative scartate: fingersi un browser o usare un browser automatico per passare il filtro (aggira una protezione); copiare i bandi da siti di notizie (non sono il testo ufficiale, e le citazioni devono venire dalla fonte).

**50. Campi nuovi per le persone e questionario adattivo: i non modellabili scendono dal 74% al 43%** (9/11, Edoardo: "casa, studio, tipologia di ISEE, numero ed età dei figli e da quanti anni si risiede nella regione: le puoi già inserire").
- **Campi aggiunti** a `schema/regola.schema.json` e `docs/vocabolario-persone.md` (lo schema è di Lorenzo: aggiunte autorizzate da Edoardo, da rivedere insieme):
  - casa: `abitazione` (affitto, proprietà, altro), `contratto_locazione_registrato`, `canone_annuo`, `mutuo_prima_casa`, `proprieta_altra_abitazione`;
  - studio: `titolo_di_studio`, `iscrizione` (università, AFAM, ITS, scuola superiore, nessuna), `anno_di_corso`, `fuori_corso_o_ripetente`, `crediti_conseguiti`;
  - ISEE specifici: `isee_universitario`, `ispe`;
  - famiglia: `figlio` per ogni componente e `numero_figli`, che non si chiede ma si conta dai componenti. Si è scelto un numero invece di una regola nuova del motore ("almeno N componenti che…"): niente da cambiare nel motore;
  - residenza e permesso: `anni_residenza_regione`, `mesi_validita_permesso`;
  - persona: `disabile` anche per chi fa domanda (il motore lo leggeva già), `percentuale_invalidita`;
  - lavoro: `tipo_lavoro` e `reddito_richiedente` (decisione 41).
- **Questionario adattivo:** `data/domande_persone.yaml` elenca ogni domanda con la condizione che la apre (`solo_se`). Per esempio crediti e ISEE universitario solo a chi è iscritto all'università, contratto e canone solo a chi è in affitto, tipo di lavoro solo a chi è occupato. Test: ogni campo dello schema per le persone ha la sua domanda, e ogni condizione usa una domanda fatta prima.
- **Prompt dei documenti** (`pipeline/estrai_documenti.py`, modulo nostro): scadenze e modo di fare domanda non sono requisiti; "almeno N figli" si scrive con `numero_figli`.
- **Misura** sugli stessi 10 documenti della decisione 48, stessa procedura alla cieca: **69 condizioni, 30 non modellabili (43%)**, prima 58 e 43 (74%). Le condizioni sono di più perché il modello ora scrive come campo quello che prima riassumeva in un "da verificare". Campi nuovi usati: 16 su 22.
- **I 30 che restano**, per motivo:
  - circa 18 si coprirebbero con altre domande adattive: dove si studia (regione o città dell'ateneo, 3); livello del corso (triennale, magistrale, ciclo unico, dottorato), da cui dipendono crediti minimi, durata massima e "titolo di pari livello" (6); ripetente separato da fuori corso (2); comune di domicilio, diverso dalla residenza (1); ISEE-ERP (1); figli sotto i 26 anni conviventi (1); Carta famiglia FVG (1); incidenza dell'affitto sul reddito, che si calcola da canone e ISEE (1); proprietà della prima casa nella regione e dimora nell'immobile, già esprimibili ma non usati dal modello (2);
  - circa 12 restano: benefici già avuti, debiti o revoche con l'ente, condanne, comportamenti passati come assegnatario, eccezioni che il documento non riporta, e il caso di Lucca (estratto delle sezioni sbagliato, decisione 48).
  - Con le domande del primo gruppo si arriverebbe intorno al 17%. Il resto si può trasformare in **domande di conferma per bando**: quando un bando risulta "probabilmente idoneo", l'app chiede in fondo "confermi di non aver già avuto questo beneficio quest'anno?". Non diventano domande del profilo, ma l'esito smette di essere "da verificare" e diventa "idoneo se confermi".


**51. robots.txt irraggiungibile vale come divieto** (9/11, Lorenzo con Claude; da rivedere con Edoardo: tocca il raccoglitore; `pipeline/fonti/documenti.py`).
- Completa la decisione 42, che ha aggiunto il `Crawl-delay` con `documenti.attesa`: quella parte resta com'è.
- Prima, se robots.txt non si riusciva a leggere (rete giù, errore del sito), si scaricava lo stesso annotandolo. Il brief (§10) dice di non scaricare da siti che non lo permettono, e in quel caso non lo sapevamo.
- Ora `ammesso(url)` segue RFC 9309 (lo standard di robots.txt, §2.3.1): 404 o altro 4xx = nessuna regola, si scarica ("robots.txt assente"); errore di rete, timeout o 5xx = irraggiungibile, **vale come divieto**. 401/403 restano un divieto, come prima (lo standard li tratta come assenza di regole: noi restiamo più prudenti).
- `attesa` legge il ritardo solo da un robots.txt letto davvero, quindi gli stati "vietato" e "irraggiungibile" danno la pausa normale, senza errori.
- Effetto: una voce su un sito con robots.txt instabile quel giorno risulta non scaricata invece di essere presa alla cieca; si riprende con `--solo-mancanti`.
- Scartato: considerare un robots.txt irraggiungibile come "nessuna regola", come si faceva. È più comodo, ma è proprio il caso in cui non sappiamo cosa il sito vieta.

**52. Eccezioni rare: `portata: rara` e il nuovo esito "idoneo, salvo eccezioni"** (proposta di Edoardo in `docs/proposte-fase-2.md`, parte 1; implementata da Lorenzo con Claude l'8/11, portata sull'ultimo lavoro di Edoardo il 9/11; da confermare con Edoardo). Risolve il "quasi nessuno è idoneo" di `docs/da-fare.md`, sezione 3, e della decisione 30.
- Un `non_modellabile` può avere `portata: rara`: un caso particolare che riguarda un sottogruppo dei beneficiari ("purché", "salvo", "ad eccezione di"). Senza `portata` resta trattato come prima: di default si resta prudenti.
- Motore (`pipeline/motore.py`): se l'esito sarebbe "da verificare", si rilegge la regola presumendo vere le eccezioni rare; se così tutto torna sì, l'esito è **"idoneo, salvo eccezioni"** e `Esito.eccezioni` elenca le eccezioni con la loro citazione, per la lista finale della decisione 24. Un requisito fallito vince sempre (non idoneo) e un dato da chiedere pure (mancano dati); basta una riserva generale per restare "da verificare".
- **Mai dentro `almeno_uno_di`.** Lì presumere vero un requisito aprirebbe la via alternativa a tutti: NASpI, "chi conserva un part-time può avere diritto" è una via alternativa, non un'eccezione. Il motore non la presume e `pipeline/citazioni.py` la segnala come errore. Un'eccezione rara deve anche avere la citazione: è il passaggio che la persona leggerà.
- Misura (`pipeline/confronta.py`): "idoneo, salvo eccezioni" conta tra gli esiti possibili; "più cauta" e "troppo sicura" ora seguono l'ordine idoneo → salvo eccezioni → da verificare; nuova misura `falsi_si_da_rare`, i falsi sì dovuti a un'eccezione segnata rara (il rischio della decisione), riportata nei dettagli per beneficio.
- Applicata per ora a una sola regola di riferimento: NASpI, contributi agricoli prevalenti (l'esempio di Edoardo). Ora chi ha tutti gli altri requisiti risulta "idoneo, salvo eccezioni" invece di "da verificare". Le altre riserve dei 5 benefici di sviluppo sono generali (cittadinanza, contributi, titoli di soggiorno) o vie alternative, e restano come sono.
- Effetto sulla misura dei 5 benefici di sviluppo (oggi `docs/test-estrazione-sviluppo.md`): l'estrazione del 5/11 non conosceva `portata`, quindi sulla NASpI risulta "più cauta" nel 42% dei casi non banali (accordo dal 100% al 58%; totale dall'87% all'80%). Non è un peggioramento dell'estrattore: le istruzioni (`pipeline/prompt_estrazione.md`) e la guida all'etichettatura ora spiegano `portata`, e la misura vera sarà sulle etichette.
- Scartato (come nella proposta): lasciare com'è (corretto ma inutile), trasformare ogni eccezione in una domanda (allunga il questionario per pochi), un punteggio di probabilità (non abbiamo le frequenze).
- Test: `tests/test_eccezioni_rare.py` (10) e i casi NASpI in `tests/test_persone.py`.
- **Rapporto con la decisione 50.** Edoardo propone domande di conferma per bando ("idoneo se confermi"). Le due idee si completano: qui l'eccezione rara si presume senza chiedere e resta visibile con la citazione; là la riserva diventa una domanda per quel bando. Quali requisiti vanno da una parte e quali dall'altra è **da decidere insieme**. La misura del 43% di non modellabili (decisione 50) è stata fatta prima di `portata`: non cambia il conteggio, perché un'eccezione rara resta un `non_modellabile`.

**53. Demo web: FastAPI e una pagina HTML, profilo solo nel browser; per le persone una scelta delle domande più semplice** (8/11, Lorenzo con Claude; collegata il 9/11 alle domande della decisione 50; da rivedere con Edoardo. Chiude lo "stack dell'applicazione" della decisione 13).
- **Stack:** FastAPI (`web/server.py`) sopra il motore, più una pagina in HTML, CSS e JavaScript senza librerie né compilazione (`web/static/`). `make demo`.
  - Scartato Streamlit: più veloce da scrivere, ma l'interfaccia e la logica si mescolano e l'API non si può provare da sola. Scartato Flask con pagine generate dal server: per un'API JSON FastAPI scrive meno codice e valida le richieste da sé (422 su un ramo sconosciuto o un numero scritto come testo).
  - Niente database: non c'è niente da salvare.
- **Privacy** (vocabolario delle persone, scelta 2): il profilo vive nella pagina e arriva intero a ogni passo; il server non lo salva e non lo scrive nei log. Ricaricando la pagina si cancella.
- **Imprese:** il questionario greedy della decisione 10, invariato, con lo stesso campione di 1.000 imprese fittizie; si costruisce in meno di 2 secondi all'avvio.
- **Persone:** il questionario delle imprese non regge gli alberi (decisione 17) né il nucleo. Le domande, con la loro condizione `solo_se`, sono quelle di `data/domande_persone.yaml` (decisione 50). Quale fare per prima lo decide `prossima_persone` in `web/domande.py`: ogni beneficio ancora "mancano dati" dà a ognuna delle sue domande mancanti 1/k punti (k = domande che gli mancano), e vince la domanda con più punti. Se una domanda dipende da una risposta che manca, si fa prima quella. ⚠ Non è misurata: va confrontata con un ordine fisso, come per le imprese (da-fare, sezione 4).
- **La data del figlio** è una domanda sola; giorni e mesi interi si ricavano lì (vocabolario, scelta 4). "Nessun figlio negli ultimi due anni" vale un numero di giorni che nessun termine raggiunge.
- **Le domande sui componenti del nucleo** si fanno per tutti i componenti insieme, in una schermata.
- **Ogni esito mostra il perché:** il requisito che lo decide (fallito, mancante, eccezione rara), con la citazione letterale e la fonte; chi è idoneo vede tutti i requisiti. Per le imprese la fonte è il campo dell'open data, che non ha una citazione.
- **Le regole estratte dall'LLM** (lotto INPS e i 3 bandi regionali) si vedono solo attivando l'opzione e hanno l'etichetta "estratta da un LLM, non rivista". Di default solo le 5 regole di riferimento.
- **Provata nel vero browser** (Chrome, con Playwright): i due percorsi completi, chiaro e scuro, schermo largo e telefono (390 px, nessuno scorrimento orizzontale), nessun errore nella console. Test automatici: `tests/test_web.py` (17), senza rete. Playwright non è tra i requisiti: serve solo per questa prova a mano.
- **Ciò che si ricava senza chiedere** (`completa`): `numero_figli` dai componenti; chi fa domanda non è figlio di sé stesso; chi non è figlio non è un figlio a carico; un permesso per casi speciali non può averlo chi ha un altro stato; senza figli i termini dalla nascita non valgono. Una domanda chiusa dal `solo_se` non si fa e non si inventa un valore: il requisito resta "mancano dati", se nessun altro lo esclude (esempio: la NASpI per chi lavora).
- ⚠ **Due `solo_se` tolti da `data/domande_persone.yaml`, da rivedere con Edoardo.** `soggetto_irpef_italia` era solo per chi lavora o è in pensione, ma l'Assegno unico lo chiede a tutti; `patrimonio_immobiliare` era solo per chi ha "un'altra casa adatta", ma contano anche terreni e altri immobili (ADI). Con quelle condizioni questi due benefici restavano su "mancano dati" per sempre.

**54. Copertura misurata in Lombardia e Sicilia: il portale da solo, e il portale più le nostre raccolte** (proposta, da rivedere con Edoardo e Lorenzo; `pipeline/copertura.py`, risultato in `docs/copertura-regioni.md`). Applica il metodo di `docs/proposte-fase-2.md`, §3.5, e chiude la voce 2.1 di `docs/da-fare.md`.
- **Cosa si misura.** Non "i nostri dati contro l'elenco ufficiale" e basta: in Lombardia la nostra raccolta legge Bandi e Servizi, lo stesso sistema da cui nasce il dataset regionale, quindi sarebbe alta per costruzione. Si misurano due cose: (1) quanto copre **incentivi.gov.it da solo**, che è la domanda del progetto (il portale ufficiale basta?); (2) quanto copre **il portale più le nostre raccolte**, che dice quanto aggiunge il nostro lavoro.
- **Lombardia** (elenco ufficiale: dataset "Anagrafica dei bandi regionali", dati.lombardia.it `bukx-h2uy`, CC BY 4.0, righe aggiornate al 2026-10-01): 109 bandi per privati aperti sia il 27/10 sia il 7/11. Portale da solo **27/109 = 25% (18%-34%)**; portale più raccolte **106/109 = 97% (92%-99%)**, alto per costruzione, come detto.
- **Sicilia** (nessun elenco ufficiale): cattura e ricattura tra i siti della Regione e IRFIS (45 bandi) e il portale (7), 2 in comune. Stimatore di Chapman **N ≈ 122 (72-281**, intervallo di Chao). Portale da solo **6% (2%-10%)**, tutte e due le fonti **41% (18%-69%)**. ⚠ Le fonti non sono indipendenti e il portale riguarda per legge le imprese: N è sottostimato, le coperture vanno lette come un massimo. Con m = 2 è un ordine di grandezza.
- **Filtro di rilevanza sul titolo** (regole in `NON_RILEVANTE`): toglie atti che non sono bandi, gare, concorsi, bandi solo per enti pubblici. Su campioni delle stesse liste usate per scrivere le regole va d'accordo con la revisione 40/40; su una lista mai vista (Toscana) **18/30 = 60% (42%-75%)**. È il punto debole: quasi tutti gli errori lasciano dentro voci che non sono bandi per privati, e abbassano la copertura apparente.
- **Abbinamento:** codice del bando nell'indirizzo quando c'è, altrimenti titolo normalizzato con un punteggio (massimo tra `difflib` e Dice); stesso bando da 0,75, zona grigia tra 0,60 e 0,75. Luoghi, anni, assi o ordinali diversi danno 0. Tarato sulle 50 coppie certe per codice: per titolo 32 giusti automatici, 2 sbagliati, 11 in zona grigia, 5 persi.
- ⚠ **Revisione da confermare:** le 25 coppie in zona grigia e i campioni del filtro (`data/copertura/revisione.yaml`) li ha decisi Claude leggendo titoli, enti e date, senza aprire i bandi. Vanno ricontrollati da uno di noi prima di citare i numeri nel report.
- Scartato: stimare la Sicilia con il rapporto lombardo (le regioni alimentano il portale in modo troppo diverso); l'LLM come filtro di rilevanza (costa, e un giudizio del modello non si corregge come una regola).
- Riproducibile: `python -m pipeline.copertura` rigenera il documento identico; `python -m pipeline.copertura scarica-lombardia` riscarica il dataset. Test: `tests/test_copertura.py` (30).
- **Rispetto al lavoro successivo di Edoardo** (decisioni 42-49). Le raccolte sono ferme al 7/11: i bandi aggiunti dopo (per esempio le università lombarde della decisione 49) non contano qui, e il documento lo dice con la sua data. Tra le fonti misurate non ci sono quelle "prese dal portale", così la copertura non è circolare, come chiede la decisione 42. La decisione 49 arriva alla stessa conclusione sul dataset lombardo: sono i bandi che raccogliamo già dalla Regione.

## 13/11/2026

**55. Lotto 2: tutte le schede INPS rimaste tra i benefici, con il metodo del lotto 1** (13/11, Lorenzo; da rivedere con Edoardo; `data/obiettivi/lotto-2`, `data/regole_estratte/lotto-2`, `docs/report-13-11.md`).
- 48 benefici INPS senza regola (su 77 schede segnate `beneficio`); estratti 40 con `pipeline.estrai prepara`/`importa`, agenti che ricevono solo il prompt, come il lotto 1. Tutte accettate al primo tentativo: 205 condizioni, 141 non modellabili (69%).
- Esclusi 8, con i criteri del lotto 1 e della decisione 40: domande chiuse o misure non più erogate (genitori separati, transito navi a Venezia, mobilità ordinaria e in deroga), misure abolite (Reddito e Pensione di Cittadinanza), doppioni (Bonus mamme 2025), adempimenti che non sono benefici (dichiarazioni di responsabilità dell'Assegno sociale), il congedo per le vittime di violenza (decisione 40).
- Id della maternità della Gestione Separata: `inps-indennita-di-maternita-paternita-gestione-separata`. Con il troncamento a 50 caratteri coincideva con l'id della maternità degli autonomi in `data/gold/edo/`, un'altra scheda.
- La demo le mostra con le altre regole estratte, solo a richiesta (`web/domande.py`, `DIR_ESTRATTE`).
- Scartato: estrarre anche i servizi (372 schede non `beneficio`): non danno diritto a una prestazione, e il motore non saprebbe che farne.

**56. Bandi per le persone: riscaricati dalle fonti "persone" ed estratti con il metodo dei documenti di prova** (13/11, Lorenzo; da rivedere con Edoardo; `data/regole_estratte/documenti`).
- Fonti: le 75 con `pubblico: persone` o comuni, più i bandi DSU delle università lombarde (`data/fonti/documenti.yaml`). Testi con `pipeline.fonti.elenchi --solo-mancanti` sugli elenchi del 7-9/11, senza rileggere le pagine elenco: 204 documenti, 8 non scaricati (robots.txt, 403, 410), 4 scansioni saltate.
- Estrazione con `pipeline.estrai_documenti` (solo le sezioni sui requisiti), agenti che vedono solo il prompt, controllo su tutto il testo: 197 su 197 accettati. Le istruzioni comuni, identiche per tutti i documenti, sono state lette una volta per gruppo invece che una volta per documento: il modello vede lo stesso testo, a una frazione del costo.
- 127 regole con requisiti: 706 condizioni, 381 non modellabili (54%), 69 bandi aperti il 13/11.
- Bandi con più finestre di domanda: si usa la finestra principale (o quella complessiva) e le altre vanno nelle note. ⚠ Da rivedere: una persona può vedere aperto un bando la cui finestra per lei è chiusa (EDISU Piemonte).
- Scartato per ora: le fonti miste (regioni, finanziarie, agenzie per il lavoro), dove i bandi per le persone vanno prima separati da quelli per le imprese; i bandi per le imprese, per cui manca un vocabolario dei requisiti scritti nel testo.

**57. Le regole estratte senza requisiti non vanno nella demo** (13/11, Lorenzo; `data/regole_estratte/documenti-senza-requisiti`).
- Una regola con `requisiti: []` dà "idoneo" a chiunque (`pipeline/motore.py`, `valuta`): per un avviso rivolto alle imprese o per una pagina senza testo sarebbe un falso sì per tutti, l'errore peggiore.
- Vanno in una cartella che `web/domande.py` non legge: 67 regole vuote (bandi per enti, imprese, associazioni; pagine che rimandano a un allegato; pagine vuote) e tre con requisiti che non danno un esito utile: la tassa regionale DSU di ALiSEO (un tributo, non un beneficio) e le pagine indice dei servizi abitativi di Opera Trento ed ESU Verona (unico requisito "essere studente", senza ateneo).
- Dove il bando è per le persone ma i requisiti stanno in un allegato che non abbiamo, gli estrattori hanno scritto un `non_modellabile` "requisiti non riportati" invece di `[]`: l'esito è "da verificare", che è corretto.
- Scartato: cancellarle (sono dati utili per la raccolta: dicono quali fonti "persone" pubblicano soprattutto avvisi per enti); tenerle con un'etichetta "non per le persone" nella demo (il motore non ha un esito per questo).

**58. L'età di chi fa domanda è quella del primo componente del nucleo** (13/11, Lorenzo; `web/domande.py`, `completa` e `RICAVATI`).
- Le regole usano `eta` al primo livello per chi fa domanda (Assegno sociale, SFL, 17 regole della demo tra lotti e bandi). Il questionario chiede già l'età di ogni componente, e il primo è "Tu" (`web/static/app.js`): `completa` la copia in `eta`; con "non lo so" sul nucleo anche `eta` è "non lo so".
- Prima la demo, non trovando `eta` tra le domande, la chiedeva a parte con un generico "Età?", dopo averla già avuta nel nucleo.
- Scartato: una domanda separata "Quanti anni hai?" (la stessa risposta due volte, e le due potrebbero non coincidere).

**59. Prima misura dell'estrazione sulle etichette a mano** (13/11, Lorenzo; `data/obiettivi/gold`, `data/regole_estratte/gold`, `docs/test-estrazione.md`).
- Estratti alla cieca i 14 benefici di `data/gold/`: obiettivi con solo id, titolo, ente e link; stessi prompt e controlli dei lotti 1 e 2; 4 agenti, ciascuno con i soli prompt dei suoi 3-4 benefici, senza accesso al repository né alle etichette. 13 accettate al primo tentativo, DIS-COLL al secondo (una citazione con il punto e virgola al posto del punto).
- Misurate per ora contro le 9 etichette di Lorenzo: 25 condizioni giuste su 30 (richiamo 83%, precisione 64%), accordo sugli esiti 74% sui casi non banali, falsi sì 14%, falsi no 4%. Sui 5 benefici di sviluppo era 80%, ma lì il riferimento l'aveva scritto lo stesso modello (decisione 29).
- `pipeline/confronta.py` ignora le etichette ancora vuote, da entrambe le parti: `make confronta` scrive la misura su Edoardo e l'accordo tra i due solo quando le sue etichette sono compilate. La prova di sviluppo è passata in `docs/test-estrazione-sviluppo.md` (`make confronta-sviluppo`).
- ⚠ È una misura parziale: 9 benefici, un solo etichettatore. Il numero per il report è quello sui 14, con l'accordo tra i due etichettatori come tetto.

## 15/11/2026

**60. Etichette di Edoardo su GitHub, unione del branch di Lorenzo e prima misura sulle 14 etichette** (15/11, Edoardo con Claude; `data/gold/edo/`, `docs/test-estrazione-edo.md`, `docs/accordo-etichette.md`; da discutere con Lorenzo).
- **Etichette:** le 8 di Edoardo committate il 15/11 (`068d471`), dopo che Lorenzo aveva finito le sue (da-fare, sezione 0). Committate prima di vedere la misura, così non si possono più aggiustare guardando i numeri; da allora non sono state toccate.
- **Unione:** `integrazione-lorenzo` (decisioni 51-59) unito in `raccolta-regioni` (`ceb788d`), senza conflitti: il suo branch partiva dall'ultimo commit di Edoardo, e le etichette sono file che Lorenzo non tocca. `main` e i branch di Lorenzo non sono stati toccati.
- **Risultati** (`make confronta`, casi non banali):
  - estrazione contro Lorenzo (9 benefici): accordo sugli esiti 74%, falsi sì 14%, falsi no 4%, condizioni giuste 25/30 (come nella decisione 59);
  - estrazione contro Edoardo (8 benefici): accordo 44%, falsi sì 19%, falsi no 12%, condizioni giuste 5/16;
  - Edoardo contro Lorenzo (3 benefici in comune, il "tetto"): accordo 42%, falsi sì 18%, falsi no 9%, condizioni giuste 4/10.
- **Come leggerli.** Il tetto (42%) è sotto la misura dell'estrazione contro Lorenzo (74%): il riferimento non è ancora stabile, e il 74% non si può presentare da solo. Le differenze viste nei file sono soprattutto di convenzione, non di lettura della scheda:
  1. *Versione del vocabolario.* Le etichette di Edoardo sono del 7-8/11, prima che `tipo_lavoro`, `reddito_richiedente` e `figlio` entrassero nello schema (decisione 50, 9/11). Dove oggi c'è un campo, Edoardo aveva scritto `condizione_lavorativa: occupato` (6 etichette su 8) o un `non_modellabile` (ISCRO: 9 non modellabili contro 3). Lorenzo e l'estrazione hanno usato il vocabolario nuovo.
  2. *`lavora_in_italia`* (proposta di Edoardo dell'8/11, da-fare sezione 3): c'è in 4 etichette di Edoardo su 8, in nessuna di Lorenzo né dell'estrazione.
  3. *Lo stesso requisito con campi diversi.* "Figlio sotto i 14 anni" scritto come `eta` del componente oppure come `mesi_da_evento_figlio < 168`. Le persone fittizie di `pipeline/confronta.py` non tengono coerenti i due campi, quindi la misura li conta come diversi (congedo parentale: accordo 3% tra noi, 5% con l'estrazione).
- Due etichette di Edoardo erano state riviste l'8/11 dopo aver visto una prima estrazione (lo dicono le loro `note`): su quelle due la misura è meno alla cieca.
- **Scartato:** correggere le etichette prima di misurare (la misura da riportare è quella fatta prima delle correzioni, da-fare sezione 3); aspettare Lorenzo per l'unione (il piano chiede la misura entro il 18/11 e l'unione era pulita); presentare nel report solo il 74% (sarebbe la metà favorevole dei dati).
- **Da decidere con Lorenzo:**
  - un secondo passaggio sulle etichette di entrambi con le stesse convenzioni (vocabolario del 9/11, sì o no a `lavora_in_italia`), e nel report la misura prima e dopo, con le correzioni scritte nelle `note`;
  - in `pipeline/confronta.py` (codice di Lorenzo): riconoscere i campi equivalenti, o rendere coerenti le persone fittizie (età del figlio e mesi dalla nascita).

**61. A chi si rivolge un bando delle fonti miste: regole sul titolo e sulla sezione dei destinatari** (15/11, Edoardo con Claude; `pipeline/fonti/pubblico.py`, `data/pubblico/`; prima parte del punto 9 della sezione 0 di `docs/da-fare.md`).
- **Problema.** 1.379 documenti raccolti su 2.298 vengono da fonti miste (regioni, finanziarie regionali, agenzie per il lavoro) e non hanno `pubblico`. Lorenzo ha estratto solo i bandi delle fonti "persone" (decisione 56), quindi i bandi per le persone pubblicati dalle regioni non sono mai arrivati all'estrazione.
- **Metodo**, in quest'ordine, sul testo già raccolto (nessun nuovo scaricamento):
  1. titolo che dice da solo "persone" (borse di studio, alloggi, affitto, ERP, nidi, buoni scuola, caregiver...), purché non nomini anche imprese o enti;
  2. titolo che dice "non è un bando per qualcuno" (gare, forniture, incarichi, albi, elenchi, graduatorie, rendicontazioni);
  3. la sezione sui destinatari ("Beneficiari", "Destinatari", "A chi è rivolto", "Chi può partecipare"): nei 600 caratteri dopo l'intestazione vince il gruppo nominato per primo, gli altri vanno in `anche`;
  4. senza sezione, le parole dei gruppi nel titolo;
  5. altrimenti `dubbio`.
- **Risultato sui 1.379:** persone 233 (più 53 dove le persone sono un gruppo secondario), imprese 423, enti 271, non bandi 91, dubbi 361. Il file è `data/pubblico/classificazione.yaml` (tutti i 2.298 documenti, in git: 630 KB); i documenti in `data/raw/documenti` non si toccano.
- **Misura grezza** (`python -m pipeline.fonti.pubblico misura`), contro il pubblico delle fonti che ce l'hanno: dei documenti delle fonti "persone" ne manda alle persone il 63% (118/188); di quelle "imprese" il 7% (43/579), di quelle "enti" l'11% (16/152). Il riferimento è sporco: guardando i casi, buona parte del 37% "perso" sono albi, elenchi di commissari e pagine di servizi che stanno nelle fonti Lombardia e Piemonte "cittadini" ma non sono bandi per le persone. Le regole sono state ritoccate guardando questi stessi casi, quindi il numero è ottimista per costruzione.
- **La misura vera** è il campione da rivedere a mano: 40 documenti senza `pubblico` (20 stimati "persone", 20 no, seme 61) in `data/pubblico/revisione.yaml`, con `giusto` e `corretto` da compilare. Dalla prova a occhio sui primi casi la precisione su "persone" non è alta (centri estivi per gli enti, offerta formativa per gli organismi di formazione): l'estrazione la corregge in parte, perché i bandi senza requisiti per le persone finiscono in `documenti-senza-requisiti` (decisione 57), ma costa.
- **Scartato:**
  - il filtro di rilevanza di `pipeline/copertura.py` (decisione 54): è tarato sulle imprese e scarta "bando di concorso", "iscrizione", "università" e "locazione", che per le persone sono borse di studio, nidi, diritto allo studio e case. Con il filtro, il 35% dei documenti delle fonti "persone" diventava "non bando" o "enti";
  - un LLM che classifica: costa, e un giudizio del modello non si corregge come una regola (stessa scelta della decisione 54);
  - parole come "lavoratori", "università", "scuole" tra le parole che decidono: compaiono nei bandi di tutti e tre i gruppi (un'impresa che assume lavoratori svantaggiati).
- **Prossimi passi:** rivedere il campione; correggere `pipeline/fonti/sezioni.py` (il bando di Lucca che perde l'articolo 1) prima di estrarre; poi estrarre i 233 come la decisione 56. Test: `tests/test_pubblico.py` (7).

**62. Sezioni dei bandi: le frasi andate a capo non sono titoli** (15/11, Edoardo con Claude; `pipeline/fonti/sezioni.py`, decisione 32; chiude il problema di Lucca della decisione 48).
- **Problema.** Nei PDF una frase va a capo a metà, e se la riga comincia con una parola da titolo ("Possono", "presentazione", "soggetti", "contributo") ed è breve, `sezioni.py` la prendeva per un titolo e apriva lì una sezione nuova. A Lucca "Possono partecipare al bando per l'erogazione dei contributi i nuclei" staccava il testo dell'articolo 1 dal suo titolo, e la parola "erogazione" faceva scartare quel pezzo come sezione "del dopo": il modello ha ricevuto il titolo dell'articolo 1 senza i requisiti. Non era un caso isolato: su tutti i 2.298 documenti c'erano 12.795 "titoli" che cominciano con la minuscola.
- **Correzione**, quattro regole:
  1. un titolo senza numero di articolo comincia con la maiuscola;
  2. una riga seguita da una riga che comincia con una parola minuscola è una frase andata a capo, non un titolo. Non vale per gli elenchi ("a) Forma giuridica"), per le righe tutte in maiuscolo, per le righe numerate ("1. Requisiti del soggetto proponente e dell'eventuale" / "aderente") e per i titoli sui requisiti spezzati ("Chi può" / "partecipare");
  3. la riga subito dopo un "ART. 6" rimasto da solo è il seguito del suo titolo e gli si aggiunge ("ART. 6 REQUISITI DI PARTECIPAZIONE"), invece di aprire una sezione a parte che lascia l'articolo senza nome;
  4. "Requisiti per l'erogazione" resta una sezione sui requisiti: si scarta come sezione "del dopo" solo se la parola del dopo (erogazione, obblighi, revoca) viene prima di quella sui requisiti.
- **Effetto sui 2.298 documenti** (vecchia e nuova versione a confronto, contando le righe con parole come requisiti, ISEE, residenza, reddito, nucleo): 1.638 estratti uguali; 190 guadagnano righe sui requisiti, 131 ne perdono; in tutto 1.035 righe guadagnate e 744 perse. Le perse le ho guardate a campione: quasi tutte (626 su 744) stavano in "sezioni" aperte da una frase in minuscolo che la vecchia versione sceglieva per caso (perché cominciava con "soggetti" o "requisiti"); le altre sono soprattutto revoche, graduatorie e punteggi. Il caso di Lucca ora passa: l'estratto contiene l'articolo 1 con residenza e ISEE.
- **Regole già estratte da rifare:** 24 delle 200 estratte da Lorenzo il 13/11 (decisione 56) avevano un estratto con meno righe sui requisiti, quasi tutte bandi del diritto allo studio: ERGO, ADISU Umbria (borse e assegno), ERSU Messina, Enna, Catania e Palermo, EDISU Piemonte (4), Comune di Lucca, UniMiB, UniSR, Uninsubria, DSU Toscana, ADSU L'Aquila, ADISU Puglia, ALiSEO, LazioDisco, ATC Piemonte Sud, Comune di Urbino, più due tra quelle senza requisiti (Piemonte cooperazione, Comune di Mantova). Proposta: rifarle insieme ai 233 bandi della decisione 61. Sono regole estratte da Lorenzo: va deciso con lui.
- **Scartato:** mandare sempre tutto il documento (costa da 2 a 10 volte di più sui bandi lunghi del diritto allo studio, che sono proprio quelli colpiti); riconoscere i titoli dal formato del PDF (grassetto, dimensione): `pypdf` dà solo il testo, servirebbe un'altra libreria e rifare la raccolta.
- Test: `tests/test_sezioni.py`, 3 nuovi (Lucca, titoli veri che vanno a capo, "requisiti per l'erogazione").

**63. Misura: persone fittizie coerenti, secondo passaggio sulle etichette preparato, 23 regole da rifare** (17/11, Lorenzo; risponde ai tre punti "da decidere con Lorenzo" delle decisioni 60 e 62).
- **Persone fittizie coerenti** (`pipeline/confronta.py`, `rendi_coerente`). Le persone generate per confrontare due regole potevano avere combinazioni impossibili, e la misura contava come disaccordi casi che nessuno può avere. Adesso:
  - `tipo_lavoro` (dipendente, autonomo, parasubordinato) solo per chi è `occupato`;
  - `lavora_in_italia: vero` solo per chi è occupato (nel questionario si chiedono solo a lui);
  - giorni e mesi dall'ultima nascita o adozione dalla stessa data;
  - l'età del figlio più giovane uguale ai mesi diviso 12.

  Quando due campi dicono la stessa cosa, se ne tiene uno a caso e l'altro si ricava, così le soglie di entrambi restano provate. Test: `tests/test_confronta.py`, `test_persone_fittizie_coerenti`.
- **Effetto** (stesso seme, casi non banali):

  | | prima | dopo |
  |---|---|---|
  | estrazione contro Lorenzo (9) | 74% (falsi sì 14%, falsi no 4%) | 75% (10%, 6%) |
  | estrazione contro Edoardo (8) | 44% (19%, 12%) | 49% (17%, 10%) |
  | Edoardo contro Lorenzo (3) | 42% (18%, 9%) | 46% (12%, 11%) |

  La correzione sposta poco: le differenze vere sono di convenzione. Nel congedo parentale (accordo fra le etichette 3%) le etichette di Lorenzo danno "da verificare" e quelle di Edoardo "idoneo", perché Lorenzo segna come non modellabili le esclusioni che riguardano pochi. Le correzioni proposte sono in `docs/seconda-passata-etichette.md` (convenzioni A-F), da decidere insieme. Nel report vanno le due colonne, prima e dopo.
- **Regole da rifare dopo la decisione 62**: 23 (`data/regole_estratte/da-rifare.txt`), calcolate confrontando, per ognuno dei 200 documenti estratti il 13/11, le righe sui requisiti dell'estratto vecchio e di quello nuovo. Sono le stesse 24 di Edoardo meno una: LazioDisco ha lo stesso estratto con le due versioni. I prompt sono pronti fuori da git e partono con i 233 bandi della decisione 61, dopo la revisione del campione.
- **Scartato:**
  - riconoscere i campi equivalenti nella misura della struttura (`mesi_da_evento_figlio < 168` uguale a `eta < 14`): l'equivalenza vale solo per le nascite, e con persone coerenti la misura sugli esiti la tratta già bene;
  - rendere coerente anche `numero_figli` con il nucleo: servirebbe aggiungere componenti alle persone fittizie, e nessuna differenza osservata dipende da questo.
