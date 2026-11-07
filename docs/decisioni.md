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
