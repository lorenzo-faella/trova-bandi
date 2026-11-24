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

**64. Accuratezza degli esiti: domande che non riguardano la persona, segnalazioni automatiche sulle regole** (17/11, Lorenzo; `web/domande.py`, `pipeline/sospette.py`, `docs/regole-sospette.md`).
- **Domande chiuse.** Una domanda con `solo_se` non si fa a chi non c'entra: il tipo di lavoro a chi non lavora, la percentuale di invalidità a chi non ha una disabilità. Le regole che ne avevano bisogno restavano per sempre su "mancano dati" anche quando l'esito era già deciso. Simulando tre profili completi (disoccupato, pensionato, occupato) restavano bloccate 4-9 regole per profilo; dopo la correzione ne resta 1.
  - Adesso `completa` (funzione `non_applicabili`) dà una risposta ovvia alle domande chiuse da una risposta vera: "no" ai sì/no, `non_applicabile` agli elenchi (non è tra i valori ammessi, quindi un requisito `in` risulta falso).
  - I numeri solo dove il valore è ovvio: invalidità 0 per chi non ha una disabilità; `giorni_da_cessazione_lavoro` 99999 per chi non ha perso il lavoro, come `NESSUN_EVENTO`.
  - Reddito, contributi e ISPE restano senza dati: non sono zero solo perché la domanda non si fa.
  - Una domanda chiusa da "non lo so" resta senza dati, come prima.
  - Sostituisce la regola a mano sul permesso per casi speciali, che è un caso particolare.
  - Test: `tests/test_web.py`, `test_domande_che_non_riguardano_la_persona`.
  - Resta bloccata una regola: l'ISPE si chiede solo agli universitari, e un bando di ERGO lo chiede ad altri. Va deciso se togliere il `solo_se` all'ISPE.
- **Segnalazioni automatiche** (`make sospette`, `docs/regole-sospette.md`). Non correggono niente: ordinano le regole da rileggere per prime. Cercano gli errori già visti:
  - soglie che nel testo non compaiono;
  - date di apertura o chiusura che nel testo non compaiono, o invertite;
  - benefici per chi lavora senza condizioni sul lavoro (l'errore più frequente nella misura, decisioni 59-60);
  - regole fatte solo di requisiti non modellabili.

  Sulle 180 regole estratte che la demo può mostrare: 61 segnalate, di cui 49 solo non modellabili, 8 con una soglia assente, 5 per chi lavora senza condizioni e 3 con una data assente. Restano falsi allarmi noti: "minorenne" giustifica 18 senza scriverlo, "primo anno di vita" giustifica 12 mesi.
- **Correzioni collegate.**
  - `forme` (`pipeline/citazioni.py`) riconosce i decimali con il punto delle migliaia ("19.837,92", "77.010,60"): prima 36 soglie ISEE e ISPE dei bandi DSU risultavano assenti per errore.
  - `pipeline/confronta.py` cerca le soglie nel testo del documento per i bandi, non solo nelle schede INPS.
- Scartato: correggere le regole segnalate in automatico. Una segnalazione dice dove guardare, non cosa scrivere, e una correzione automatica sarebbe un'altra estrazione non rivista.

**65. Due estrazioni indipendenti per misurare l'affidabilità sui bandi, senza etichette; rifatte le 23 regole della decisione 63** (17/11, Lorenzo; `data/regole_estratte/seconda-estrazione`, `docs/doppia-estrazione.md`).
- **Metodo.** Le 23 regole da rifare dopo la correzione delle sezioni (decisione 62) sono state estratte due volte, A e B, da agenti separati con gli stessi prompt. Nessuno vedeva l'altra estrazione né le regole vecchie. Il confronto usa lo stesso `pipeline/confronta.py` delle etichette. Sui bandi non abbiamo etichette a mano, quindi l'accordo fra due estrazioni è la misura disponibile, ed è un limite superiore: due errori uguali non si vedono.
- **Risultato.** 46 risposte su 46 accettate al primo tentativo (schema e citazioni). Sulle 21 regole con requisiti:
  - condizioni uguali 87/97;
  - accordo sugli esiti 93%, falsi sì 2%, falsi no 3%.

  Sull'INPS la misura contro le etichette dà 49-75% (decisioni 60 e 63). Sui bandi l'estrazione è più stabile, almeno con sé stessa: sono testi lunghi ma con requisiti espliciti (ISEE, ISPE, iscrizione).
- **Dove non concordano, la regola è incerta.** Boves (ATC Piemonte Sud, case popolari): accordo 50%. In B "non possedere un'altra casa" è un requisito secco; in A sta in alternativa con le eccezioni del bando (nuda proprietà, alloggio inagibile, assegnato al coniuge). A è la più fedele al testo, B dà falsi no.
- **Quale si usa.** A in `data/regole_estratte/documenti` (e `documenti-senza-requisiti` per i due bandi per enti: Mantova e Piemonte cooperazione). B in `data/regole_estratte/seconda-estrazione`, che la demo non carica e che serve solo al confronto (`make confronta`).
- **Effetto della correzione delle sezioni**, regole vecchie contro A: accordo sugli esiti 90%. Il caso più chiaro è Lucca (caro energia): prima nessun requisito modellabile, ora residenza e ISEE.
- **Vocabolario.** In entrambe le estrazioni i limiti d'età di chi fa domanda ("sotto i 40 anni", "maggiorenne") sono finiti in `non_modellabile`, perché `docs/vocabolario-persone.md` elencava `eta` solo per i componenti. Il motore e la demo la gestiscono per chi fa domanda dalla decisione 58: aggiunta la riga nella sezione "Il richiedente". Vale dalle prossime estrazioni.
- **Proposta per i 233 bandi della decisione 61:** stesso metodo, due estrazioni e il confronto. Le regole su cui A e B non concordano vanno rilette per prime, insieme a quelle di `docs/regole-sospette.md` (decisione 64). Costa il doppio solo in quel lotto.

## 18/11/2026

**66. Sezioni dei bandi: il sommario non è un elenco di titoli, e le tabelle richiamate arrivano al modello** (18/11, Edoardo con Claude; `pipeline/fonti/sezioni.py`, decisioni 32 e 62; nasce dall'analisi dei requisiti non modellabili dei 130 bandi estratti, `docs/da-fare.md`, sezione 0).
- **Problema 1: il sommario.** Nei bandi lunghi le righe dell'indice ("ART. 8 REQUISITI ECONOMICO-PATRIMONIALI ........ 17", "Art.4 Destinatari dei benefici 14") sembravano titoli: aprivano decine di sezioni di una riga, il loro testo faceva scegliere l'inizio del documento e, con "Art. N", richiamava quasi tutti gli articoli. Colpiva 156 documenti su 1.495 con estratto: 16 delle regole estratte (quasi tutti i grandi bandi del diritto allo studio) e 26 dei 233 bandi della decisione 61. Il caso peggiore è **LazioDisco**: l'estratto cominciava con l'indice e il modello ha concluso "la pagina è un indice del bando", lasciando la regola senza requisiti, anche se la soglia ISEE (28.339,88 €) era nel testo inviato.
- **Problema 2: le tabelle in appendice.** Gli articoli rimandano a tabelle in fondo al bando ("i cui limiti massimi sono riportati nella tab. 6"), che non venivano mandate. A **ERSU Catania** la regola non ha nessuna soglia economica (ISEE 25.000 €, ISPE 60.000 € stanno nella tab. 6), e l'elenco degli atenei (tab. 1) manca anche a Catania e Messina.
- **Correzione:**
  1. una riga è del sommario se ha i puntini ("........ 17") e senza puntini è un titolo o finisce con un numero; oppure se finisce con un numero di pagina, è un titolo senza quel numero e sulla stessa pagina ce ne sono almeno tre. Le righe del sommario non aprono sezioni e non si mandano (le citazioni si controllano comunque su tutto il testo);
  2. come per "di cui all'art. N", si seguono i rimandi a "tab. N" / "tabella N": la tabella va dal suo titolo ("Tab. 6 – Requisito economico-patrimoniale", con la maiuscola e il trattino) alla tabella dopo, al prossimo articolo o a 80 righe, e si aggiunge in fondo all'estratto. "tab. 5" porta anche 5.1, 5.2...;
  3. due correzioni collegate. "Criteri di de**termin**azione degli importi" contava come sezione sui termini (ora `\btermin`) e faceva mandare le tabelle degli importi. L'inizio del documento si manda anche se nomina ISEE o residenza ("persone fisiche con ISEE inferiore ad Euro 30.000,00, residenti in Sicilia", IRFIS; UniMiB), perché prima passava solo grazie alle parole del sommario; questo però non basta a dire che il bando ha una sezione sui requisiti.
- **Effetto sui 2.298 documenti** (versione vecchia contro nuova): 2.019 estratti uguali, 279 cambiati. Caratteri mandati -2,4% (30,8 → 30,1 milioni), quasi tutto sommario. Nessun documento passa da "tutto il testo" a "estratto" o viceversa. Le soglie ISEE/ISPE in euro arrivano ora a Catania, Enna e Messina (da 1 a 16 righe); le righe sui requisiti "perse" guardate una per una sono righe del sommario, sezioni sugli importi (UniMi: fasce della borsa, non requisiti) e obblighi delle strutture (ASPAL, un avviso per enti). A IRFIS e UniMiB le soglie restano nell'estratto.
- **Regole da rifare:** 24 delle 130 hanno un estratto diverso, in `data/regole_estratte/da-rifare-66.txt`. Subito le 4 che ricevono un requisito nuovo (LazioDisco, Catania, Messina, Enna), con il metodo A/B della decisione 65; le altre 20 ricevono solo meno rumore e si rifanno con i 233. Sono regole estratte da Lorenzo: chi le rifà è da decidere con lui.
- **Scartato:**
  - riconoscere il sommario solo dopo una riga "INDICE" o "SOMMARIO": molti PDF non la hanno o la perdono nell'estrazione del testo;
  - trattare i titoli delle tabelle come titoli di sezione: una tabella a metà articolo taglierebbe il resto dell'articolo;
  - seguire anche "allegato A": nei bandi "Allegato A" è spesso l'intestazione di ogni pagina o il modulo di domanda, quindi costa molto e porta poco. Le tabelle sono il caso che si è visto davvero.
- Test: `tests/test_sezioni.py`, 4 nuovi (sommario con puntini e numeri, titolo vero che finisce con un numero, tabelle richiamate, "tab. 5" e "tabella" a inizio frase). In tutto 302 test passati.

**67. Convenzioni comuni per il secondo passaggio sulle etichette: A-F** (18/11, Edoardo su proposta di Lorenzo, `docs/seconda-passata-etichette.md`; risponde ai punti "da decidere" delle decisioni 60 e 63). A-E sono le proposte di Lorenzo, accettate da Edoardo; F era "da discutere": la scelta qui sotto è di Edoardo, ⚠ da confermare con Lorenzo.
- **A. Vocabolario del 9/11 per tutti: sì.** Dove oggi c'è un campo si usa quello: `tipo_lavoro` invece di `condizione_lavorativa: occupato` o di un `non_modellabile`, `reddito_richiedente` per i tetti al reddito di chi fa domanda, componente con `figlio: vero` per i figli.
- **B. `lavora_in_italia`: no, salvo che la scheda lo dica.** Le schede non lo scrivono, né Lorenzo né l'estrazione lo usano, e il questionario lo chiede solo a chi è occupato: in un beneficio per chi ha perso il lavoro lascerebbe l'esito su "mancano dati" per sempre. Edoardo lo toglie dalle sue 4 etichette che lo hanno (congedo di paternità, congedo parentale, discontinuità, maternità degli autonomi). Il campo resta nello schema per le schede che lo chiedono davvero (Assegno unico).
- **C. Esclusioni che riguardano un gruppo ristretto → `portata: rara`: sì** (è già la regola di `docs/etichettatura.md`). "Esclusi i lavoratori domestici" dà "idoneo, salvo eccezioni", non "da verificare". Un requisito centrale che il vocabolario non copre resta `non_modellabile` senza `portata`. Lato Lorenzo: congedo parentale e Bonus mamme.
- **D. Niente requisito "pigliatutto": sì.** "Gli altri requisiti vanno verificati caso per caso" diventa un `non_modellabile` per condizione, ognuno con la sua citazione, oppure va nelle `note`. Lato Edoardo: maternità degli autonomi e ISCRO.
- **E. Età del figlio: età del componente.** "Entro i 14 anni del bambino" è un componente con `figlio: vero` ed `eta < 14`; `mesi_da_evento_figlio` resta per i termini che partono dalla nascita o dall'ingresso in famiglia ("entro 5 mesi dal parto"). Lato Edoardo: congedo parentale.
- **F. Incompatibilità con altri benefici: nelle `note`, non nei requisiti.** "Incompatibile con NASpI" o "non ricevere l'ADI" vuol dire che i due benefici non si cumulano, non che non se ne ha diritto: chi ha la NASpI può comunque scegliere l'ISCRO. Come `non_modellabile` darebbe "da verificare" a tutti. Lato Lorenzo: ISCRO e SFL, dove oggi sta nei requisiti.
- **Come si applica:** ognuno corregge solo le proprie etichette, a mano e senza LLM, e scrive ogni correzione nelle `note` del file ("corretto il .../11 per la convenzione X"). Poi `make controlla` e `make confronta`; nel report vanno le misure prima (75 / 49 / 46%, decisione 63) e dopo.
- **Scartato:** tenere `lavora_in_italia` e aggiungerlo anche alle etichette di Lorenzo (nessuna scheda lo scrive: sarebbe conoscenza esterna, vietata dalle istruzioni di etichettatura); per F, un `non_modellabile` con `portata: rara` (chi riceve già un beneficio incompatibile non è un sottogruppo raro tra chi chiede l'ISCRO o l'SFL).

**68. Nuova demo: interfaccia rifatta sopra lo stesso motore, regole estratte incluse di default, online con un link** (18/11, Lorenzo; `web/static/`, `web/domande.py`, `web/server.py`, `web/profili_demo.yaml`, `Dockerfile`, `render.yaml`).
- **Perché.** La demo di prima era funzionale ma spoglia e ferma a prima delle decisioni 58-65. Per la presentazione serve un'interfaccia chiara a chi non conosce il progetto, che spieghi da sola gli esiti, e raggiungibile da un link.
- **Cosa resta uguale.** Motore, questionario e API `/api/passo`. Si rifà solo l'interfaccia: HTML, CSS e moduli JavaScript senza build e senza dipendenze obbligatorie (il font si carica da Google Fonts, con un'alternativa locale). Nessun `innerHTML` con testi presi dai siti dei bandi.
- **Esiti in linguaggio semplice.**
  - "idoneo" → "ti spetta"; "da verificare" → "possibile: da controllare";
  - "quasi idoneo" → "ti manca un requisito"; "mancano dati" → "serve un'altra risposta".

  Con le regole di oggi quasi nessun profilo arriva a "idoneo": quasi ogni regola ha almeno un requisito non modellabile. "Da verificare" vuol dire che nessun requisito controllabile esclude la persona, e la scheda dice cosa resta da controllare. Va presentato così, non come un fallimento.
- **Regole estratte accese di default**, con l'etichetta "estratta automaticamente". Sono 180 delle 185 regole per le persone: spente, la demo mostrerebbe quasi niente.
- **Regione del bando** (`territorio` in `web/domande.py`): la regione della fonte, da `data/fonti/`. Delle 122 regole aperte, 52 bandi locali non scrivono il vincolo territoriale (un comune vale per i residenti, una borsa DSU per chi studia lì). L'esito non cambia: la demo li raggruppa soltanto, e quelli di altre regioni finiscono in fondo, chiusi.
- **Novità richieste da `docs/contesto.md`:**
  - avviso ISEE (`isee` nella risposta di `/api/passo`), con il link alla scheda INPS del Portale unico ISEE;
  - profili del caro vita (`/api/profili`, esempi inventati e verificati nei test);
  - calendario delle scadenze generato nel browser (le date oltre due anni sono il segnaposto 2050 dell'open data e si scartano).
- **Correzione collegata:** due regole del lotto 2 mettono `mesi_da_evento_figlio` dentro un componente del nucleo; la demo chiedeva per ognuno una domanda che non esiste. Ora `da_porre` non fa domande su campi che il componente non ha.
- **Online.** `Dockerfile` (genera alla build solo bandi e regole delle imprese) e `render.yaml` (servizio gratuito Render). GitHub Pages non basta, perché il motore è Python. Build provata in locale: stessi numeri di `/api/statistiche`.
- **Claude Design** era previsto solo come esplorazione visiva facoltativa (fase 0 del piano). Un prototipo fatto lì non sarebbe collegato al motore e andrebbe riscritto. La direzione grafica si può ancora cambiare dai token in `web/static/css/stile.css`.
- **Verifica:**
  - un percorso completo in Chrome senza interfaccia: persona da zero (14 domande fino alla fine), i profili, l'avviso ISEE, le imprese, il `.ics` (14 scadenze), mobile a 390 px, "riduci movimento";
  - nessun errore in console;
  - test in `tests/test_web.py` per statistiche, profili, avviso ISEE, regione e regole estratte di default.
- **Scartato:**
  - un framework con build (React o simili): un passaggio in più da mantenere e da far girare il giorno della presentazione;
  - spostare il motore nel browser (Pyodide): pesante, e la logica esiste già in Python.

**69. Risposte multiple per lavoro e studio; risposte per ogni persona del nucleo a un clic** (18/11, Lorenzo, dalla prova della demo; `data/domande_persone.yaml`, `pipeline/motore.py`, `web/domande.py`, `web/static/js/domanda.js`).
- **Problema 1.** "Qual è la tua situazione lavorativa?" ammetteva una sola risposta, ma si può studiare e lavorare insieme. Lo stesso per il tipo di lavoro: si può essere dipendente e avere una partita IVA.
- **Correzione 1.** Nel questionario c'è un nuovo tipo, `elenco multiplo`, usato per `condizione_lavorativa` e `tipo_lavoro`. La risposta è una lista. Il motore (`verifica`, operatore `in`) considera soddisfatto un requisito se una delle scelte è nell'elenco: chi studia e lavora passa sia "occupato" sia "studente". Anche i `solo_se` accettano liste, quindi a chi lavora e studia si chiede il tipo di lavoro. Le regole e lo schema non cambiano: una risposta singola resta una stringa. Test: `test_studio_e_lavoro_insieme`.
- **Problema 2.** Le domande da ripetere per ogni persona del nucleo ("È tuo figlio?") avevano un menu a tendina per persona. Erano lente da usare, e bastava lasciarne una su "Scegli…" perché la risposta venisse rifiutata. Dalla prova è sembrato che "No" non si potesse scegliere.
- **Correzione 2.** Ogni persona ha pulsanti "Sì / No / Non lo so" a un clic, e c'è "No per tutti" quando le persone sono più di una. L'errore dice di rispondere per ogni persona.
- **Restano a scelta singola, di proposito:**
  - cittadinanza, titolo di studio (il più alto), iscrizione (il corso principale), abitazione e causa di fine lavoro;
  - `attivita` di ogni componente, che per l'Assegno unico è una condizione alternativa: renderla multipla richiede una riga di scelte per persona, da fare se la prova lo chiede.

**70. Esiti più accurati: gruppi ristretti e sede dell'ateneo nel vocabolario, 75 regole rifatte, "possibile" solo con un indizio a favore** (18/11, Lorenzo, dalla prova della demo; `schema/regola.schema.json`, `docs/vocabolario-persone.md`, `data/domande_persone.yaml`, `web/`, `docs/simulazione-demo.md`).
- **Problema.** Un profilo del Lazio senza condizioni particolari aveva 66 "possibili". Le cause, misurate:
  - bandi locali di altre regioni la cui regola non scrive il vincolo territoriale (37 dei 66);
  - benefici INPS per gruppi ristretti (ex IPOST, Gestione Magistrale, figli di dipendenti pubblici, superstiti, TBC, lavoratori domestici e agricoli, forze armate), il cui requisito decisivo non era nel vocabolario e quindi non escludeva nessuno;
  - bandi DSU che chiedono la sede dell'ateneo.

  Molti "possibili" non avevano nessun requisito soddisfatto: volevano dire solo "non sappiamo niente".
- **Vocabolario.** Due campi nuovi:
  - `situazioni_particolari`, a scelta multipla, nelle regole con `interseca`; "nessuna di queste" esclude da quei benefici;
  - `regione_ateneo`, chiesto solo a chi è iscritto a università, AFAM o ITS.

  In più, nelle istruzioni per i bandi: se il bando è riservato ai residenti, il vincolo con `comune` o `regione` va scritto sempre.
- **Regole rifatte**: 75 (38 INPS, 37 bandi). Sono quelle aperte il 18/11 con un `non_modellabile` coperto dai campi nuovi o dall'età, più i bandi comunali senza vincolo territoriale. Stesso metodo dei lotti: agenti separati che vedono solo il prompt, istruzioni comuni lette una volta per gruppo. 75 su 75 accettate al primo tentativo.

  Su un campione di 20 una seconda estrazione indipendente: accordo sugli esiti 97%, falsi no 1%. Su tutte le 41 regole estratte due volte, 94% (`docs/doppia-estrazione.md`; `confronta.py` accetta ora più cartelle separate da virgola).

  Le regole di `data/regole_estratte/gold` non sono state rifatte: la misura sulle etichette (decisioni 60 e 63) resta confrontabile e non cambia.
- **Presentazione** (`posto` e `contaVisibili` in `web/static/js/risultati.js`; `a_favore` in `risultato`):
  - i bandi di altre regioni non contano più fra i "possibili";
  - un "da verificare" senza nessun requisito soddisfatto diventa "Non sappiamo dirlo", in un gruppo chiuso.

  Il motore non cambia.
- **Motore**: `interseca` tratta una risposta singola (stringa) come una lista di un elemento. Prima `set("occupato")` era l'insieme delle lettere.
- **Effetto**, nella simulazione con una persona estratta a caso e risposte fissate prima (`docs/simulazione-demo.md`):
  - "possibili" mostrati da 57 a 6;
  - pertinenti, giudicati alla cieca sulla versione, da 1 su 20 a 2 su 6 (le due indennità ai superstiti: la persona è vedova);
  - 25 passaggi da "possibile" a "non ti spetta", tutti corretti per quella persona.

  Peggioramento noto: gli ANF per dipendenti privati, rifatti, non escludono più un autonomo e finiscono in "Non sappiamo dirlo".
- **Rischio**: chi risponde male a "Ti riguarda una di queste situazioni?" (non sa che un genitore era dipendente pubblico) perde quei benefici. Per questo le opzioni sono scritte in linguaggio semplice e c'è sempre "Non lo so".
- **Scartato:**
  - aggiungere in automatico un vincolo di residenza a tutti i bandi comunali: alcuni valgono per chi ha un immobile o un'attività nel comune, non per chi ci risiede;
  - nascondere del tutto i "Non sappiamo dirlo": è un'informazione vera, va solo separata dai possibili.

**71. Residenza e domicilio, il comune dopo la regione, le risposte nel report** (18/11, Lorenzo, dalla prova della demo con un profilo come quello di Edoardo; `data/domande_persone.yaml`, `web/domande.py`, `web/static/`).
- **Problema.** Con un profilo da studente siciliano che vive e studia a Milano:
  - la demo conosceva solo la residenza, quindi i bandi lombardi finivano fra quelli "di altre regioni";
  - alla domanda sul comune l'elenco proponeva solo i comuni della regione di residenza, e "Mi…" non trovava Milano;
  - il report stampato non diceva con quali risposte era stato ottenuto.
- **Residenza e domicilio.**
  - `regione` e `comune` sono ora esplicitamente quelli di residenza ("In che regione hai la residenza?").
  - Subito dopo si chiede `domicilio_diverso` ("Vivi abitualmente in un altro comune, per esempio per studio o lavoro?") e, se sì, `regione_domicilio` e `comune_domicilio`. Chi vive dove risiede ha domicilio = residenza (`completa`).
  - La domanda sul domicilio si fa sempre appena nota la residenza, anche se nessuna regola la usa, perché decide quali bandi locali sono vicini.
  - Nella pagina sono "vicini" i bandi delle regioni di residenza, di domicilio e dell'università.
  - Le 5 regole aperte che nominano il domicilio sono state rifatte con i campi nuovi.
- **Comune.** Si chiede dopo la regione corrispondente (`da_porre`). Con la regione "non lo so", l'elenco propone tutti i comuni d'Italia (`/api/comuni` senza regione).
- **Report.** `riepilogo` (in `web/domande.py`, nella risposta di `/api/passo`): le risposte in forma leggibile, nell'ordine del questionario. Sulla pagina sono chiuse in "Le tue risposte"; in stampa si aprono da sole e vengono prima degli esiti.
- **"Troppo severo?"**: con quel profilo restavano 2 "possibili". Controllate una per una, le esclusioni erano corrette: chiedono di lavorare, di avere figli, una disabilità o di far parte di gruppi particolari. I pochi possibili dipendono dal calendario: il 18/11 le borse per il diritto allo studio lombarde sono chiuse (UniMiB il 30/9), e i bandi chiusi non si mostrano. Uno dei due "possibili" era un errore: l'avviso per ispettori ambientali volontari del Comune di Caltanissetta non è un aiuto, ed è passato in `documenti-senza-requisiti` (decisione 57).
- **Da valutare**: mostrare in un gruppo a parte i bandi chiusi da poco che di solito riaprono ogni anno (borse DSU, contributi affitto), per chi prova la demo fuori stagione.

**72. "Chiusi da poco: di solito riaprono ogni anno"; quanti bandi per le persone mancano** (18/11, Lorenzo; `web/domande.py`, `web/static/js/risultati.js`).
- **Copertura, misurata il 18/11:**
  - 184 regole per le persone: 55 benefici INPS nazionali (tutti aperti, quasi tutti per lavoratori, genitori o gruppi particolari) e 129 bandi locali, di cui 66 aperti;
  - per regione i bandi aperti sono pochi: Emilia-Romagna 15, Toscana 8, Abruzzo 8, Piemonte 7, Sicilia 3, Lombardia 1;
  - 55 bandi sono chiusi negli ultimi 12 mesi;
  - mancano ancora i 233 bandi per le persone delle fonti miste (decisione 61) e i benefici nazionali che non vengono dall'INPS (ministeri, carte, bonus). Chi prova la demo fuori stagione vede pochi bandi aperti soprattutto per questo.
- **Chiusi da poco.** `passo` valuta anche i bandi chiusi negli ultimi 365 giorni (`chiusi_di_recente`, senza quelli che risultano "non ti spetta"). La pagina li mostra in un gruppo chiuso, fuori dai conteggi, solo per le regioni vicine, con "Chiuso il …: di solito riapre". Per uno studente siciliano a Milano ci sono le borse DSU di Statale, Bicocca, Insubria, San Raffaele e LIUC (chiuse il 30/9) e quelle siciliane. Spesso risultano "servono risposte", perché per i bandi chiusi il questionario non fa domande: la scheda dice cosa controllare quando il bando riapre.
- **Dati**: il titolo della regola di ERSU Catania veniva dai metadati del PDF ("<>/Metadata 3871 0 R…"); è stato scritto a mano.
- Scartato: "riapre il …" con una data presunta: non sappiamo se e quando un bando riaprirà, si dice solo che di solito succede.

**73. Sede e livello del corso nel vocabolario; rifatte le 24 regole della decisione 66 e altre 27; nomi delle regioni ufficiali** (19/11, Lorenzo; risponde alle proposte di Edoardo in `docs/da-fare.md`, sezione 0, punto 3, e alla decisione 66).
- **Campi nuovi** (`schema/regola.schema.json`, `docs/vocabolario-persone.md`, `data/domande_persone.yaml`):
  - `livello_corso` (triennale, magistrale, ciclo unico, dottorato, specializzazione, master, ITS, AFAM di primo e secondo livello);
  - `comune_ateneo`, cioè il comune della sede del corso, da cui `completa` ricava `provincia_ateneo` e `regione_ateneo` con l'elenco ISTAT (`sedi_istat`). Così una domanda sola basta anche per gli ERSU siciliani, divisi per provincia;
  - `tempo_parziale`.

  La regione dell'ateneo non si chiede più: si ricava. Sono le tre proposte di Edoardo: livello del corso (98 condizioni non modellabili nei 130 bandi), sede degli studi (32), tempo parziale (9).
- **Regole rifatte: 51.** Sono le 24 di `data/regole_estratte/da-rifare-66.txt`, con il `sezioni.py` corretto da Edoardo (decisione 66), più 27 aperte o chiuse da meno di un anno che citano livello, sede o tempo parziale. Stesso metodo: agenti separati che vedono solo il prompt. 51 su 51 accettate, una (EDISU borsa) al secondo tentativo per una `fonte` mancante.
  - **Seconda estrazione sulle 4 urgenti** (LazioDisco, Catania, Messina, Enna): sulle 3 con requisiti, accordo sugli esiti 67%, Enna 86%, Catania 48%. Le differenze vengono dalla regola del "titolo di pari livello" e dalla classificazione dei corsi AFAM. Su LazioDisco B non trova requisiti: la pagina presenta solo il bando, che sta in un PDF non raccolto (la pagina indice della proposta di Edoardo).
  - **Effetto sull'accordo**: la doppia estrazione complessiva scende dal 94% al 77% (`docs/doppia-estrazione.md`). Regole più dettagliate (crediti per anno e per livello, sede, titolo già posseduto) sono anche meno stabili fra due letture. Vecchie contro nuove: accordo 65%, con il 23% di casi in cui la nuova esclude dove la vecchia non sapeva. È l'effetto voluto dei campi nuovi, ma va riletto.
  - **Soglie calcolate**: in 22 regole compaiono soglie di crediti che non sono nel testo. Gli estrattori hanno tolto il bonus dalla soglia del bando, quindi sono soglie più basse del requisito vero. Chi sta sotto non arriva nemmeno con il bonus massimo: il rischio è qualche "da verificare" in più, non un falso no. Sono tutte in `docs/regole-sospette.md`, da rileggere per prime.
  - Regole sostituite: la versione A; la B delle 4 urgenti è in `data/regole_estratte/seconda-estrazione`.
- **Nomi delle regioni**: 10 fonti scrivono "Valle d'Aosta" e "Trentino-Alto Adige" senza la parte bilingue dell'elenco ISTAT. La demo metteva i loro bandi fra quelli "di altre regioni" anche per chi ci vive. Ora `regione_ufficiale` riconduce il nome, senza toccare i file delle fonti.

  Corretti a mano tre valori nelle regole che non sarebbero mai stati soddisfatti: "Trentino-Alto Adige" (seconda estrazione di Trento), "Fubine" → "Fubine Monferrato" (ATC Piemonte Sud), "Bolzano/Bozen" → "Bolzano" (ARDiS FVG). `make sospette` ora segnala ogni regione, provincia o comune fuori dagli elenchi ISTAT.
- **Effetto sulla demo:**
  - **Studente siciliano che studia a Milano:** i "chiusi da poco" vicini scendono da 12 a 6. Le borse degli ERSU siciliani spariscono, perché sono per chi studia in Sicilia, e restano quelle lombarde.
  - **Salvatore** (`docs/simulazione-demo.md`): i "possibili" mostrati scendono da 6 a 4, e i due pertinenti restano.
  - **Restano imprecisioni note**: ERSU Enna tratta come incerta, invece che esclusa, una sede fuori dall'elenco; la maternità della Gestione Separata compare anche a chi non può averla, perché il vocabolario non ha il sesso.
- **Ancora da decidere**:
  - la convenzione F della decisione 67 resta da confermare con Lorenzo;
  - se togliere le pagine che annunciano soltanto un bando (proposta di Edoardo).

## 20/11/2026

**74. Estrazione dei bandi per le persone delle fonti miste (passata A); seconda passata di Edoardo; coppie della copertura riviste** (18-20/11, Edoardo con Claude; decisioni 61, 65, 66, 67).
- *Numerazione: questa decisione è la 68 su `raccolta-regioni`; su `demo` è la 74, perché i numeri 68-73 erano già usati dal 19/11.*
- **Estrazione A.** I 233 bandi stimati "persone" delle fonti miste (decisione 61), più le 4 regole urgenti della decisione 66 (LazioDisco, ERSU Catania, Messina, Enna), meno 3 scansioni: 234 prompt con `pipeline.estrai_documenti prepara` e le sezioni corrette della decisione 66. Agenti separati che vedevano solo le istruzioni comuni e i propri documenti, gruppi per sito. **233 su 234 accettati al primo tentativo** (schema e citazioni); manca ASPAL Sardegna, tirocini di formazione (`sardegna-aspal-avviso-pubblico-tirocini-di-formazione-e-ddc132`), fermato per il limite di uso.
- **Dove sono.** 196 regole nuove: 103 con requisiti in `data/regole_estratte/documenti`, 93 vuote (bandi per enti o imprese, pagine senza testo) in `documenti-senza-requisiti` (decisione 57). Le 4 urgenti sostituiscono quelle del 13/11. In tutto 135 delle 233 hanno requisiti: coerente con la precisione del 70% del campione (decisione 61).
- **33 bandi dei Comuni erano già stati estratti il 13/11** (decisione 56): le fonti comunali non hanno `pubblico` e sono finite anche fra le fonti miste. Si tengono le regole del 13/11; le nuove servono solo come **seconda estrazione indipendente**: accordo sugli esiti **89%** (27 regole con requisiti), condizioni uguali 53/60, stessa decisione "per le persone / per enti" in 31 su 33. Con il 93% della decisione 65, l'estrazione sui bandi risulta stabile. ⚠ È un limite superiore: due errori uguali non si vedono.
- **Passata B** (seconda estrazione di tutti i 233): non fatta. Il 18/11 20 agenti in parallelo hanno esaurito il limite di 5 ore dopo 157 documenti; tutta B costerebbe più di un limite. Proposta: B solo su un campione di 40 regole con requisiti, o fatta da Lorenzo con il suo account.
- **Segnalazioni** (`make sospette`, `docs/regole-sospette.md`): 80 regole su 283 da rileggere per prime. 5 regole del 13/11 (LazioDisco borse, alloggio, mobilità, premio di laurea; ADSU L'Aquila semestre filtro) hanno citazioni che non si trovano più nel testo riscaricato: le pagine sono cambiate. Da rifare.
- **Da ricontrollare dopo l'estrazione** (note degli agenti): Dote Unica Lavoro disabili di alcune province senza l'avviso provinciale (Lecco, Bergamo, Como, Monza, Pavia, Cremona); "Inclusione scolastica, enti erogatori" estratta per gli studenti; un documento dell'albo famiglie affidatarie con una pagina di un altro avviso; date in conflitto (Varese, orfani di femminicidio); la regione scritta "Friuli-Venezia Giulia".
- **Seconda passata di Edoardo** (decisione 67), scelte fatte a mano su una pagina di lavoro e trascritte da Claude, con una nota in ogni file: `tipo_lavoro` in 6 etichette; `reddito_richiedente` ≤ 35.000 € (discontinuità) e ≤ 12.000 € (ISCRO); tolti i "serve sapere se dipendente/autonomo". Centri estivi: il requisito sui figli dei dipendenti pubblici resta non modellabile (è centrale). Congedo parentale: resta `mesi_da_evento_figlio` (Edoardo non applica E). ⚠ I due "caso per caso" (maternità degli autonomi, ISCRO) sono nelle note: così le etichette danno "idoneo" senza i requisiti veri della scheda, e l'accordo sugli esiti scende (prova del 20/11: estrazione contro Edoardo 20%, Edoardo contro Lorenzo 8%, con condizioni giuste salite a 10/20 e 8/10). **La misura "dopo" non è valida** finché quei due non sono divisi in requisiti e Lorenzo non ha fatto la sua passata; i documenti della misura non sono stati riscritti.
- **Copertura** (decisione 54): le 25 coppie in zona grigia riviste da Edoardo aprendo i bandi. 4 non decidibili restano con la stima di Claude; le 2 che Edoardo aveva cambiato (5 e 13) le ha ricontrollate e sono diverse. La copertura del portale in Lombardia resta **27/109 = 25%**, ora con la revisione di una persona. I campioni del filtro (110) restano quelli di Claude dell'8/11.
- **Scartato:** tenere le nuove estrazioni dei 33 Comuni al posto di quelle del 13/11 (sono regole di Lorenzo, e come confronto valgono di più); fare tutta la passata B (costo); applicare la scelta "nelle note" per il requisito centrale dei Centri estivi (darebbe "idoneo" a tutti i genitori).

**75. Il lavoro di Edoardo del 20/11 unito in `demo`; rifatte 60 regole delle fonti miste con il vocabolario nuovo; passata B su un campione di 40; la regione dei bandi raccolti dalle API** (20/11, Lorenzo; decisioni 65, 70-74).
- **Unione.** `raccolta-regioni` (`e32e5b6`) unito in `demo` con un merge, senza riscrivere il lavoro di Edoardo. La sua decisione 68 è qui la 74. Per le 4 regole urgenti (LazioDisco, ERSU Catania, Messina, Enna) restano le versioni di `demo`, che usano i campi della decisione 73. Le versioni di Edoardo sono in `data/regole_estratte/seconda-estrazione-edoardo/`.
- **Testi delle fonti.** `data/raw/documenti` non è in git. Su questa macchina mancavano i testi delle regole nuove. Sono stati riscaricati con il raccoglitore del progetto (robots.txt e pause, `pipeline/fonti/elenchi.py`), e ora 102 regole su 103 hanno il loro testo. Il Comune di Como resta senza testo perché il suo robots.txt blocca il download, quindi la sua regola non si controlla qui. Le 5 regole del 13/11 che sulla macchina di Edoardo avevano citazioni introvabili (decisione 74) qui passano: i testi locali sono più vecchi. Vanno rifatte quando qualcuno riscarica quelle pagine.
- **Regole rifatte: 60.** Sono le regole delle fonti miste con requisiti non modellabili che i campi delle decisioni 70-73 potevano coprire: domicilio, situazioni particolari, sede e livello del corso, età di chi fa domanda. Il metodo è quello della decisione 73: prompt rifatti con `pipeline.estrai_documenti prepara`, 5 agenti separati che vedono solo il prompt. **60 su 60 accettate al primo tentativo.** 4 diventano senza requisiti, perché sono avvisi per gli enti erogatori o pagine senza requisiti, e passano in `documenti-senza-requisiti`.
  - **Non modellabili** nelle 60: dal 53% (232 su 437 condizioni) al 48% (177 su 366). È meno di quanto ci si aspettava. I campi nuovi compaiono 10 volte, quasi tutte come `regione_domicilio`.
  - **Cosa resta non modellabile** nelle 60:
    - corsi e titoli specifici: 29;
    - iscrizione al centro per l'impiego, DID, GOL: 22;
    - immobili e mutui: 14;
    - liste della L. 68/99: 12;
    - "donne": 10, perché manca il sesso;
    - attività d'impresa: 10.
  - Sulle regole delle fonti miste i non modellabili sono ora il 51% (279 su 543), su tutti i bandi il 31% (781 su 2.480), sulle schede INPS il 59%.
  - **Vecchie contro nuove**: accordo sugli esiti 86%. Nel 9% dei casi la nuova esclude dove la vecchia diceva "da verificare". Sulle 8 persone di prova (`prove/simulazione/persone.yaml` e `web/profili_demo.yaml`) ci sono 12 passaggi da "da verificare" a "non idoneo", controllati uno per uno. 11 sono corretti: serve una laurea, serve un ateneo in Sicilia, la Dote Unica Lavoro non è per i pensionati. Uno è dubbio, il voucher "Just in time" della Toscana: è per "disoccupati, inoccupati, inattivi", e lo studente fuorisede ne resta escluso perché il vocabolario tiene `studente` separato da `inattivo`.
- **Passata B su un campione di 40** (proposta della decisione 74). Seme `20112026`, scelte fra le 98 regole delle fonti miste con requisiti e con il testo sul disco; 25 delle 40 sono fra le 60 rifatte. 4 agenti separati con gli stessi prompt di A, 40 su 40 accettate al primo tentativo. Le regole sono in `data/regole_estratte/seconda-estrazione/`.
  - **Sul campione: accordo sugli esiti 94%, condizioni uguali 84 su 94, falsi no 4%.** 28 regole su 40 sono uguali negli esiti, 6 sotto l'80%.
  - Il disaccordo più forte viene da come si legge "inattivi" o "non occupati": per il servizio civile toscano B conta anche gli studenti, A no. Poi età e residenza riferite a una data passata (Master and Back) e titoli di studio AFAM senza un valore proprio.
  - `docs/doppia-estrazione.md`, su tutte le 82 regole estratte due volte: **85%**, era il 77% su 42.
- **Regione dei bandi raccolti con le API** (`web/domande.py`, `territori`). I bandi di Lombardia ed Emilia-Romagna presi dalle API regionali (`pipeline/fonti/api_regioni.py`) non hanno una voce in `elenchi.yaml`. La demo li trattava come nazionali: per un residente a Palermo "Candidatura Esperto d'area" dell'Emilia-Romagna era fra i "possibili". Ora la regione arriva anche da `api_regioni.FONTI`. 27 regole non sono più nazionali, e nessuna regola fuori dall'INPS resta senza regione.
- **Effetto sulla demo** (`docs/simulazione-demo.md`, giorno 20/11). Salvatore ha 6 "possibili" invece di 4. Si aggiungono due contributi siciliani, l'acquisto di lavastoviglie e gli interessi sui prestiti al consumo, che vale la pena controllare; le due indennità ai superstiti restano.
- **Misure sulle etichette non riscritte.** Con la seconda passata di Edoardo `make confronta` darebbe 20% e 8% (decisione 74). Finché quella misura non è valida, `docs/test-estrazione-edo.md` e `docs/accordo-etichette.md` restano quelli del 19/11: 50% e 51%.
- **Da decidere** (`docs/da-fare.md`):
  - cosa vuol dire `inattivo`. Nei bandi del lavoro "inattivi" comprende di solito studenti e pensionati; nel vocabolario sono valori separati. 7 regole usano `inattivo`;
  - un campo per l'iscrizione al centro per l'impiego, con la DID: è il non modellabile più frequente nei bandi del lavoro.
- **Scartato:** rifare le 60 senza le regole urgenti di `demo` (le versioni di Edoardo non conoscono i campi della decisione 73); fare la passata B su tutte le 98 (costo).

**76. Dopo l'estrazione A: il FERAU non è un beneficio, un test sui nomi delle regioni, le note degli agenti, il territorio dentro una regione** (20/11, Edoardo con Claude; decisioni 57, 70, 71, 73-75).
- *Numerazione: su `raccolta-regioni` è la 69. La 70 di quel ramo (un passo che aggiungeva alle regole la residenza nella regione della fonte) non entra in `demo`: contraddice le decisioni 70 e 71, che hanno scartato il vincolo automatico (alcuni bandi comunali valgono per chi ha una casa o un'attività nel comune) e guardano anche domicilio e ateneo, mentre quel requisito guardava solo la residenza. Il campione B di quel ramo (seme 68) non serve più: la passata B l'ha fatta Lorenzo (decisione 75).*
- **FERAU in `documenti-senza-requisiti`** (decisione 57): è l'autorizzazione per gli impianti a fonti rinnovabili, non un beneficio. Le due pagine "enti erogatori" le ha già spostate la decisione 75.
- **Test** `tests/test_regioni_nelle_regole.py`: ogni `regione` scritta nelle regole deve stare in `REGIONI`, così un nome breve ("Valle d'Aosta") non torna. Completa la decisione 73.
- **Note degli agenti lasciate così:** orfani di femminicidio (2010 o 2020: la data sta in un requisito non modellabile, l'esito non cambia); Dote Unica Lavoro disabili di Varese (2027 o 2028: aperto in tutti e due i casi); le Doti di Lecco, Bergamo e Como senza l'avviso provinciale (danno "da verificare": più caute, non sbagliate); albo delle famiglie affidatarie (già senza requisiti; la pagina mescolata è un problema della raccolta).
- **⚠ Territorio dentro una regione, da decidere insieme.** Fra regioni la demo sposta i bandi locali in "In altre regioni" (decisioni 70 e 75). Resta il caso dentro una regione: a chi abita a Terni un contributo del Comune di Perugia che non scrive il vincolo compare come "possibile". Per esempio: per i soli bandi dei Comuni, considerare "vicini" solo quelli del comune di residenza o di domicilio.


**77. Rifatte le 6 regole con citazioni introvabili; estratto l'ultimo bando, ASPAL tirocini** (20/11, Edoardo con Claude; decisioni 74-76).
- **Quali.** Sui testi riscaricati da Edoardo l'8/11, `pipeline.estrai_documenti controlla` dava citazioni introvabili in 6 regole del 13/11, non 5: LazioDisco borse, alloggio, mobilità, premio di laurea; ADSU L'Aquila semestre filtro e, in più, sussidi straordinari. Le pagine sono cambiate. Il Comune di Como, che sulla macchina di Lorenzo non ha testo (decisione 75), qui passa: non serve rifarlo.
- **Metodo**, come nelle decisioni 73 e 75: prompt da `pipeline.estrai_documenti prepara` (solo le sezioni sui requisiti), 2 agenti separati che vedono solo il prompt, poi `importa`. **7 su 7 accettate al primo tentativo.**
- **Contributi alloggio rifatto con `--tutto`.** Il testo intero è di 2.500 caratteri. Le sezioni ne tenevano il 75% e lasciavano fuori la prima frase ("studenti universitari fuori sede per contribuire alle spese di affitto"), così l'estrazione aveva perso il requisito `abitazione` = `affitto`, che la regola vecchia aveva. Con il testo intero torna, e "fuori sede" resta non modellabile. *Lezione:* sulle pagine brevi le sezioni possono tagliare la frase che dice a chi è rivolto il beneficio.
- **Semestre filtro ADSU L'Aquila → `documenti-senza-requisiti`.** La pagina oggi è solo un elenco di notizie che rimandano all'ordinanza: niente requisiti, niente date. La regola vecchia aveva 4 requisiti e le date di marzo 2026.
- **Vecchie contro nuove** (5 regole con requisiti, `pipeline.confronta` sulle persone fittizie): accordo sugli esiti 82%, condizioni uguali 11 su 18. Differenze:
  - *Mobilità internazionale:* le nuove chiedono residenza o domicilio nel Lazio e un ateneo nel Lazio. La pagina di oggi lo scrive, la vecchia regola no: dove la vecchia diceva "da verificare", ora per chi è di fuori il risultato è "non idoneo".
  - *Sussidi straordinari L'Aquila:* `comune_ateneo` "L'Aquila" al posto di `regione_ateneo` Abruzzo. È più preciso: il bando è per gli iscritti a Università, Accademia e Conservatorio dell'Aquila. Più l'ISPE, che prima mancava.
  - *Premio di laurea:* tolto `titolo_di_studio` laurea. La laurea si consegue con il premio, non prima: la vecchia regola escludeva chi stava per laurearsi.
  - *Borse di studio:* uguali.
- **ASPAL Sardegna, tirocini di formazione e orientamento (Sulcis Iglesiente, JTF):** 9 requisiti, aperto dall'1/10/2026 al 30/4/2029. I requisiti: domicilio in uno dei 23 comuni del Sulcis (`comune_domicilio`, nomi uguali all'elenco ISTAT), almeno 18 anni, cittadinanza UE o extra UE con titolo di soggiorno, e disoccupato oppure occupato. Restano non modellabili 5 requisiti: l'iscrizione al CPI di Carbonia o Iglesias (di nuovo il campo che manca, decisione 75), il non aver già fatto un tirocinio su questo avviso, la L.R. 5/2016 art. 14 e le incompatibilità con l'ospitante e con il profilo. Il TFO "High Competence" chiede anche la laurea, ed è finito nelle note. Ora **234 su 234** bandi delle fonti miste sono estratti.
- **Macchina di Lorenzo.** Le citazioni nuove vengono dai testi di Edoardo: sui testi più vecchi di Lorenzo possono non trovarsi. Per controllarle lì bisogna riscaricare queste 6 pagine.
- **Scartato:** correggere a mano la regola dell'alloggio aggiungendo l'affitto (le regole estratte si cambiano solo rifacendole o rivedendole); rifare tutte e 6 con `--tutto` (le altre 5 non perdevano nulla).

**78. Nella demo le etichette scritte a mano; i requisiti generici non rendono "possibile" un beneficio** (20/11, Edoardo con Claude; tocca `web/domande.py` e `tests/test_web.py`, codice di Lorenzo: Edoardo ha detto di procedere e lo avvisa lui; decisioni 59, 68, 70).
- **Il problema, visto provando la demo.** Un ragazzo di 22 anni senza figli vedeva fra i "possibili" la maternità della Gestione Separata. Una famiglia con ISEE basso non vedeva né il bonus nido né il bonus psicologo né l'SFL. Sulle 4 persone di `prove/simulazione/persone.yaml`, 5-7 dei 7-9 "possibili" erano gli stessi benefici INPS per gruppi ristretti: fondi di solidarietà del credito, richiamati alle armi, talassemia, maternità della Gestione Separata. Non era un problema dei singoli bandi, ma due difetti generali.
- **1. Le etichette scritte a mano non erano nella demo.** I 14 benefici etichettati da Lorenzo e da Edoardo (decisione 59) sono stati tenuti fuori dalle estrazioni apposta, per avere una misura alla cieca, e la demo legge solo `data/regole_persone` (5 regole) e le regole estratte. Così bonus asilo nido, bonus psicologo, SFL, assegno sociale, bonus mamme, congedi, ISCRO, DIS-COLL e centri estivi non comparivano mai. Ora `web/domande.py` (`etichette()`) li legge da `data/gold` come regole riviste.
  - Si usa l'etichetta di Lorenzo dove ci sono le due; dove c'è solo quella di Edoardo, si usa quella. In tutto sono 12.
  - Due restano fuori finché non sono corrette a mano. La **discontinuità** di Edoardo non ha il requisito "lavoratore dello spettacolo" e dava "ti spetta" a chiunque lavori con meno di 35.000 €. La **maternità degli autonomi** ha ancora il "caso per caso" nelle note (decisione 74).
- **2. I requisiti generici non contano "a favore".** "Possibile" voleva dire almeno un requisito soddisfatto e nessuno che esclude (decisione 70). Nelle schede INPS però la condizione che definisce il gruppo (gravidanza, iscrizione al fondo, richiamo alle armi) è spesso non modellabile, e l'unico requisito verificato è "sei occupato" o "sei dipendente". Ora non contano come "a favore" lavoro, età, cittadinanza, residenza in Italia e anni di residenza (`GENERICI`), nemmeno dentro un'alternativa. Una regola che ha solo questi requisiti finisce in "Non sappiamo dirlo".
  - *Scartato:* una soglia sulla quota di requisiti soddisfatti. Sulle persone di prova non separa i casi: la talassemia, che è sbagliata, ha 4 requisiti su 6; l'indennità ai superstiti, che è giusta, 1 su 5.
- **Effetto** sulle 4 persone di prova e sui 4 profili della demo. Prima i "possibili" vicini erano 7-11 per persona, quasi tutti di nicchia; ora sono 2-11 e plausibili.
  - L'operaia di Bari (ISEE 11.500 €, due figli): assegno unico, abbonamento ai bus di Bari, bonus mamme, congedo parentale, centri estivi, bonus psicologo.
  - La famiglia monoreddito: assegno unico, ADI, assegno di maternità, bonus nido, bonus mamme, congedi, SFL.
  - Spariscono dappertutto la maternità della Gestione Separata, i fondi del credito, i richiamati alle armi e la talassemia.
  - Nessun "non ti spetta" nuovo: cambia solo il gruppo in cui la demo mostra una regola.
- **Test:** quelli di `tests/test_web.py` che contavano 5 regole di riferimento ora contano 5 più le etichette. Un test nuovo controlla che "sei occupato" da solo non basti per "possibile". 316 test passano.
- **Restano fuori**, perché non sono nelle schede INPS: bonus sociale per luce e gas (ARERA), Carta "Dedicata a te", contributo affitto regionale e comunale, detrazione per l'affitto dei giovani. Sono il passo successivo.
- **Limite:** l'etichetta dei centri estivi (Edoardo) tiene non modellabile il requisito "figlio di un dipendente pubblico", quindi compare a tutte le famiglie con figli sotto i 14 anni. Oggi c'è il campo `situazioni_particolari: genitore_dipendente_pubblico` (decisione 70): l'etichetta va aggiornata a mano.

**79. Due benefici nazionali che non sono schede INPS: bonus sociale luce e gas, Carta "Dedicata a te"** (20/11, Edoardo con Claude; decisione 78).
- **Perché.** Dopo la decisione 78 a una famiglia con ISEE basso mancavano ancora gli aiuti più comuni: non sono schede INPS e nessuna fonte li raccoglieva. Aggiunti a `data/fonti/documenti.yaml` come documenti nazionali, con gli indirizzi trovati con una ricerca web: la pagina dei requisiti ARERA e la pagina MASAF della Carta 2026. Scaricati con `pipeline.fonti.documenti`, che rispetta il robots.txt, ed estratti come le altre fonti miste: `prepara --tutto` (sono pagine brevi), un agente che vede solo il prompt, `importa`. **2 su 2 accettate al primo tentativo**, in `data/regole_estratte/documenti` con il badge "non rivista".
  - *Bonus sociale:* ISEE fino a 9.796 €, oppure fino a 20.000 € con almeno 4 figli; resta da verificare la fornitura intestata al nucleo.
  - *Carta:* residenza in Italia e ISEE fino a 15.000 €; restano da verificare "nessun altro aiuto contro la povertà" e "almeno 3 componenti con almeno un minore". Non si fa domanda: i beneficiari li individua l'INPS.
- **Codifica delle pagine** (`pipeline/fonti/documenti.py`). Il sito del MASAF serve le pagine in ISO-8859-1, e lette come UTF-8 le lettere accentate diventavano "�". Ora, se il testo non è UTF-8 valido, si rilegge come cp1252.
- **Effetto** sui 4 profili della demo e sulle 4 persone di prova.
  - La famiglia monoreddito (ISEE 8.500 €) e la pensionata sola (7.000 €) hanno tutti e due i benefici fra i "possibili".
  - L'operaia di Bari (11.500 €), il commerciante di Palermo (13.000 €), lo studente (14.000 €) e l'autonomo (11.000 €) hanno la Carta; il bonus sociale per loro è "non ti spetta", ed è giusto perché hanno un ISEE sopra 9.796 €.
- **Limite:** la Carta compare anche a chi vive da solo, perché manca un campo con il numero di componenti del nucleo. Proposta: `numero_componenti`, ricavato dal nucleo come `numero_figli`. Cambia lo schema, quindi va deciso insieme.
- **Scartato:**
  - la detrazione IRPEF per chi è in affitto (giovani 20-30 anni, inquilini con reddito basso): la tabella dell'Agenzia delle Entrate non si scarica, perché il suo robots.txt risponde 403;
  - un contributo affitto nazionale: non esiste, lo fanno regioni e comuni. Fra le regole ce ne sono 4 (Toscana, Veneto, Lombardia, Emilia-Romagna), 3 già chiuse.

**80. Questionario: residenza e domicilio in due pagine, "è tuo figlio?" solo a chi può esserlo, numero dei componenti** (20/11, Edoardo con Claude; tocca `web/domande.py`, `web/static/js/domanda.js`, lo schema e i test di Lorenzo, su richiesta di Edoardo, che lo avvisa; decisioni 50, 71, 79).
- **Cosa non andava**, provando la demo:
  - Chi dice di avere 22 anni si sentiva chiedere se le persone di 50 e 51 anni del nucleo fossero suoi figli.
  - Le domande "Da quanti anni risiedi in Italia, in totale?" e "Da quanti anni senza interruzioni?" arrivavano separate, anche a chi è nato in Italia e ci ha sempre vissuto.
  - Regione, comune, residenza in Italia e domicilio erano 6 domande in pagine diverse.
- **"È tuo figlio?"** si chiede solo per chi ha almeno 12 anni meno di chi risponde (`ETA_MINIMA_GENITORE`). Agli altri `completa` dà "no", come già faceva per chi risponde.
- **Pagina della residenza**, la prima del questionario:
  - "Hai la residenza in Italia?";
  - se sì, regione e comune insieme (il comune si cerca fra quelli della regione scelta) e "Sei nato in Italia e ci hai sempre vissuto?";
  - se no a quest'ultima, "Da quanti anni vivi in Italia senza interruzioni?".

  Chi ci ha sempre vissuto ha gli anni di residenza in Italia, totali e continuativi, uguali alla sua età. Chi non risiede in Italia non ha regione né comune di residenza (`non_applicabile`). Gli anni totali si chiedono da soli, e solo se una regola li usa davvero.
- **Pagina del domicilio**, la seconda: "Vivi in un comune diverso da quello di residenza?"; se sì, regione e comune nella stessa pagina.
- **Implementazione:** un tipo di domanda nuovo, `pagina` (`pagina_persone` in `web/domande.py`, `campiPagina` in `domanda.js`). Ogni parte compare solo quando c'è la risposta da cui dipende (`se`). `sempre_in_italia` è una risposta del questionario, non un campo delle regole, come `data_evento_figlio`.
- **`numero_componenti`** (nuovo nello schema e nel vocabolario): si conta dal nucleo, come `numero_figli`. Serve per "nuclei di almeno 3 componenti" (Carta Dedicata a te, decisione 79).
- **Test:** 2 nuovi (le età dei figli, le due pagine). Aggiornati `rispondi_a_tutto` in `tests/test_web.py` e `prove/simulazione/rigioca.py`, che ora rispondono anche alle pagine. 318 test passano.
- **Scartato:** chiedere solo "sei nato in Italia?". Chi è nato in Italia ma ha vissuto all'estero non ha la residenza continuativa che chiedono ADI e Assegno sociale: per questo la domanda è "nato e sempre vissuto".

**81. Bandi salvati a mano (Milano), PDF con le legature rotte, Carta rifatta con `numero_componenti`, guida per le prove con un altro chatbot** (20/11, Edoardo con Claude; decisioni 49, 79, 80).
- **Bandi salvati a mano da Edoardo** (`Desktop/nuovi bandi`, 8 PDF). Ne entrano 2, in `data/fonti/manuali.yaml` e con `python -m pipeline.fonti.manuali`:
  - il **sostegno affitto per giovani lavoratori** del Comune di Milano (14 requisiti: residenza a Milano, affitto, ISEE fino a 26.000 €, età fino a 35 anni, lavoro);
  - la **morosità incolpevole** 2026 (12 requisiti, scade il 31/12/2026).

  Restano fuori, con il motivo in `manuali.yaml`: il sostegno affitto genitori del 2023 (chiuso), la guida "Salva Affitto" (non è un bando), l'avviso Demenze (per gli enti del Terzo settore) e i tre PDF della Regione Marche (incentivi alle imprese; il ramo imprese della demo legge incentivi.gov.it, e uno è del 2018).
  - Gli indirizzi esatti delle due pagine non si trovano con una ricerca: per ora il collegamento è il sito di Milano Abitare, da sostituire.
  - `territori()` (`web/domande.py`) ora legge anche `manuali.yaml`: senza, i bandi salvati a mano sarebbero stati trattati come nazionali.
- **Legature** (`pipeline/fonti/documenti.py`, `ripara_legature`). I PDF esportati da Word possono avere "ti", "tt", "fi" e "ffi" mappati su caratteri cinesi, l'apostrofo sul "9" e le virgolette su "<" e "=": "l9a昀케琀琀o" sta per "l'affitto". Con quel testo nessuna citazione si poteva controllare. Ora si ripara, ma solo se nel testo ci sono quei caratteri, così gli altri documenti non cambiano.
- **Estrazione:** con il documento intero (`--tutto`), perché le sezioni tenevano il 22-24% del testo; un agente, 3 su 3 accettate.
  - La **Carta "Dedicata a te"** è rifatta con `numero_componenti` (decisione 80): "almeno 3 componenti con almeno un minore" ora è un requisito controllato, in alternativa a un "da verificare", perché le fonti non sono d'accordo. Per il MASAF è un "criterio di priorità", e il messaggio INPS sulle modalità operative non lo nomina proprio. Il messaggio INPS dice invece che sono esclusi i nuclei con ADI, NASpI, DIS-COLL o CIG: va in una revisione a mano.
- **Effetto:** alla studentessa lavoratrice di Milano compaiono tutti e due i contributi per l'affitto. La morosità incolpevole però vale solo per chi ha un'intimazione di sfratto, che resta non modellabile: è lo stesso difetto delle schede INPS (decisione 78), una condizione centrale che il questionario non chiede.
- **Guida** `docs/prova-con-un-altro-chatbot.md`: prompt e 10 persone per far provare la demo a un chatbot con un browser. Il chatbot annota domande senza senso, aiuti non plausibili e aiuti che mancano, e non tocca il codice.

**82. Grandi comuni: i bandi per le persone di Napoli, Palermo, Genova e Bologna** (20/11, Edoardo con Claude; decisioni 72, 80, 81).
- **Perché.** Per una persona di una grande città la demo non mostrava quasi nessun aiuto del suo comune. Napoli, Torino e Palermo erano già fonti, ma con la sola prima pagina degli avvisi e i filtri sul titolo ne usciva poco; Roma, Genova, Bologna e Firenze non c'erano. Cercati con una ricerca web i bandi per le persone più usati (affitto, morosità, emergenza abitativa) e aggiunti a `data/fonti/documenti.yaml`.
- **Entrati: 6 regole**, estratte con `prepara --tutto` e 4 agenti; accettate tutte al primo tentativo.
  - **Napoli:** fondo per gli inquilini morosi incolpevoli 2026 e fondo regionale contro l'emergenza abitativa, aperti tutti e due fino al 31/12/2026. Le pagine sono notizie: i requisiti veri sono nei PDF allegati, che il robots.txt di `static-www.comune.napoli.it` vieta. Per questo le due regole hanno un "da verificare" che rimanda all'avviso.
  - **Palermo:** contributo di 3.000 € per l'affitto (art. 57 della L.R. 1/2026): nuclei di almeno 3 persone (`numero_componenti`, decisione 80), ISEE fino a 10.000 €. Si è chiuso il 10/6/2026, quindi la demo lo mostra fra i "chiusi di recente, di solito riaprono" (decisione 72).
  - **Genova:** Fondo Sociale Affitti 2026, 15 requisiti (ISEE fino a 9.000 €, canone fino a 6.000 €, contratto registrato…), chiuso il 15/4.
  - **Bologna:** contributi 2026 per le vacanze delle persone con disabilità (ISEE fino a 7.000 €), chiuso il 15/5. Il link trovato cercando "contributo affitto" portava a questo avviso: il bando affitto di Bologna 2026 non risulta pubblicato.
- **Non entrati:**
  - Roma (il robots.txt non risponde, e per lo standard vale come divieto) e Torino (403): aggiunti a quelli da salvare a mano in `manuali.yaml`, con l'ultimo contributo affitto di Roma (25/5-24/7/2026, ISEE fino a 14.000 €).
  - Firenze: la pagina del bando affitto 2026 è un annuncio senza requisiti.
  - I centri estivi 2026 di Napoli: concluso, ma la pagina non ha una data di chiusura, e la demo l'avrebbe mostrato come aperto.
- **Prova:** una famiglia di tre persone in affitto con ISEE 8.000 €.
  - A Napoli vede i due fondi fra i "possibili".
  - A Palermo vede il contributo da 3.000 € fra i chiusi di recente.
  - A Genova vede il Fondo Sociale Affitti fra i chiusi di recente.
- **Corretto anche** il titolo del bando DSU dell'ERSU Catania, che nella demo era un pezzo dei metadati del PDF ("<>/Metadata 3871 0 R…"). Ora è preso dalla prima pagina del bando.

**83. Correzioni dall'audit indipendente del 20/11** (20/11, Edoardo con Claude; `docs/audit-2026-11-20/`, scritta da un altro chatbot che ha esaurito i limiti prima del rapporto; decisioni 78-80).
- **L'audit:** 9 persone inventate (adulto a Milano, invalidità al 33%, studente fuorisede, famiglia senza IRPEF, part-time perso, pensionato senza ISEE, residente all'estero, tutto "non lo so", famiglia con un figlio incerto), più prove dell'API con valori impossibili. Restano lì `riproduci.py`, i dati e le schermate.
- **Corretto:**
  - **Assegno sociale nascosto.** La decisione 78 contava l'età fra i requisiti generici, così "almeno 67 anni" non era "a favore" e l'Assegno sociale finiva in "Non sappiamo dirlo" anche per un pensionato. Ora l'età conta quando sceglie un gruppo: almeno 60 anni, oppure al massimo 36 (`eta_che_decide`). "Maggiorenne" resta generico.
  - **"Paghi le imposte sul reddito in Italia?"** Chi ha un reddito basso, e quindi non paga niente, rispondeva no e perdeva l'Assegno unico. Il requisito è essere soggetti alle imposte, non pagarle: la domanda ora lo dice.
  - **Figli incerti.** Con 3 figli e un "non lo so" il numero dei figli era 3, e "almeno 4 figli" (bonus sociale) dava un no. Ora con un "non lo so" il numero dei figli resta "non lo so".
  - **Valori impossibili** (`controlla_valori`): ISEE negativo, 999 anni, invalidità al 140%, "false" scritto come testo (veniva letto come sì) e un nucleo che non è un elenco di persone (dava un errore 500). Ora l'API risponde 422.
  - **"Abbiamo finito"** con 182 bandi ancora in sospeso: chi risponde sempre "non lo so" leggeva che nessuna risposta avrebbe cambiato gli esiti. Ora la pagina dice che i bandi restano in sospeso per le risposte date con "Non lo so".
- **Tolta dalla demo:** l'etichetta della **Carta europea della disabilità** (Edoardo). Chiede solo "disabilità: sì" e dava "ti spetta" con un'invalidità del 33%; va corretta a mano con le categorie della scheda.
- **Restano aperti:**
  - chi ha perso un part-time ma ne conserva un altro ha "non ti spetta" per la NASpI, mentre la regola valutata a parte dà "da verificare": il questionario forza la condizione lavorativa;
  - l'Assegno ordinario di invalidità non considera i collaboratori della Gestione Separata;
  - mancano la Carta acquisti, l'Assegno di maternità dei Comuni e l'Assegno mensile di assistenza.
- **Test:** 2 nuovi, uno per ogni caso dell'audit corretto qui. 320 test passano.

**84. Detrazioni IRPEF per chi paga un affitto: tre regole scritte leggendo la tabella dell'Agenzia delle Entrate** (20/11, Edoardo con Claude; decisioni 79, 81).
- **Fonte.** La tabella "Detrazioni per canoni di locazione" dell'Agenzia delle Entrate (2 pagine) l'ha salvata a mano Edoardo, perché il robots.txt del sito blocca i programmi (decisione 79). È in `data/fonti/manuali.yaml` ed è stata importata con `pipeline.fonti.manuali`.
- **Scritte da Claude leggendo la tabella, senza un agente**, come chiesto da Edoardo: è una tabella a colonne e da una lettura automatica è difficile ricavare i requisiti. Le citazioni sono controllate sul testo come per le altre regole (`pipeline.estrai_documenti controlla`: 239 valide su 239). Nella demo hanno il badge "non rivista".
  - `entrate-detrazioni-affitto-2026-inquilini` (righe 1 e 2 della tabella, stessi requisiti e importi diversi): in affitto, reddito complessivo fino a 30.987,41 €. Restano da verificare il contratto secondo la L. 431/1998 e l'abitazione principale.
  - `-giovani` (riga 3): età fra 20 e 30 anni, in affitto, reddito fino a 15.493,71 €. Restano da verificare la casa diversa da quella dei genitori e i primi 4 anni del contratto.
  - `-fuori-sede` (riga 4): iscritto all'università, con un domicilio diverso dalla residenza. Restano da verificare i 100 km, l'altra provincia e il tipo di contratto. Il reddito non è un requisito, perché la detrazione la può fare il genitore e si azzera solo a 240.000 €.
- **Domanda sul reddito anche a studenti e disoccupati** (`data/domande_persone.yaml`). Prima si chiedeva solo a chi lavora o è in pensione, e per uno studente le detrazioni restavano in sospeso per sempre.
- **Prova:**
  - studente fuori sede di 22 anni, da Palermo a Milano: tutte e tre fra i "possibili";
  - lavoratore di 27 anni con 14.000 €: "inquilini" e "giovani";
  - inquilino di 45 anni con 25.000 €: solo "inquilini".
- **Limite:** le detrazioni non si cumulano, ma la demo le mostra tutte; lo dicono le note di ogni regola.

**85. Smistati i documenti rimasti "dubbio" ed estratti i bandi per le persone che mancavano** (21/11, Edoardo con Claude; decisioni 61, 74).
- **Perché.** Dei 2.308 documenti raccolti, 361 erano rimasti "dubbio" dopo la classificazione per regole del 15/11 (decisione 61) e nessuno li aveva più guardati. Altri 80 erano "persone" ma senza regola. Edoardo ne ha fatto la priorità: tutti i bandi raccolti devono arrivare nella demo.
- **Smistamento con un LLM.** La decisione 61 aveva scelto di classificare senza LLM; qui si cambia, su richiesta di Edoardo, solo per i 386 documenti rimasti. 3 agenti vedevano titolo, ente, inizio del testo e passaggio sui destinatari, e per ognuno dicevano pubblico (persone, imprese, enti, non bando), stato al 21/11 (aperto, chiuso, non so) e motivo. Il risultato è in `data/pubblico/smistamento-2026-11-21.yaml`: 145 non bandi, 100 per enti, 76 per imprese, 65 per persone (50 aperti o incerti). Va rivisto a campione.
- **Scartati prima di estrarre:** le procedure che non sono aiuti (equivalenza dei titoli sanitari, autorizzazioni per i medici esteri, tirocinio forense, maestri di sci, offerte di stage) e 4 pagine di Bolzano senza testo ("Loading...").
- **Estratti 35** con il metodo solito: `prepara` con il documento intero sotto i 20.000 caratteri e a sezioni oltre, 6 agenti. **35 su 35 accettate al primo tentativo.**
  - 27 con requisiti vanno in `documenti`.
  - 6 senza requisiti vanno in `documenti-senza-requisiti`: le domande le fanno gli operatori o i comuni, oppure la pagina ha solo il titolo (Sardegna, contributi affitto) o il menu (Puglia, CIG).
  - Non importati: un doppione di "Io Viaggio" (due pagine della stessa misura) e una pagina informativa di ARPAL Umbria del 2020.
- **Nuovi nella demo:**
  - Lombardia: buono scuola 2026/27 (scade il 10/12), contributi per gli ausili a persone con disabilità o DSA, bonus assistenti familiari, sostegno ai genitori separati e vedovi, voucher di cura "Lombardia per le donne", abbonamento agevolato "Io Viaggio", contributo parrucche per i pazienti oncologici, inclusione scolastica, servizi per persone con disabilità in 5 province;
  - Sicilia: contributo IRFIS ai consumatori sovraindebitati;
  - Veneto: voucher patente per persone con disabilità;
  - borse e misure ESU Padova e Università di Bergamo;
  - Sardegna: misure ASPAL per i lavoratori di bacini in crisi.
- **Problemi della raccolta trovati dallo smistamento**, da sistemare nei raccoglitori di `pipeline/fonti/`: le pagine di Bolzano si caricano con JavaScript ("Loading..."); il portale della Lombardia a volte risponde con la pagina anti-bot; le pagine di Sistema Puglia usano i frame e restituiscono solo il menu.
- **Ancora da fare:**
  - i 76 documenti per imprese dello smistamento e i circa 230 bandi per imprese non chiaramente chiusi e assenti da incentivi.gov.it, che la demo delle imprese non vede (legge solo il portale);
  - i 100 per enti restano fuori di proposito.

**86. Correzioni dell'audit del 21/11: fatti, perimetro e prove riproducibili** (21/11, Codex su richiesta degli autori; non è una revisione normativa umana).

- **Richiesta e stato iniziale.** Rapporto `docs/audit-2026-11-21/LEGGIMI.md` letto integralmente. Le correzioni parziali già presenti sono state controllate: 310 test passati e 10 falliti all'arrivo, rispetto ai 320 dell'audit precedente. Diff iniziale e nuove prove sono in `docs/verifica-2026-11-21/`; gli originali dell'audit non sono stati sovrascritti.
- **Supera le decisioni 64 e 80 sulle deduzioni generali.** Un cancello `solo_se` chiuso non prova falso. Restano soltanto inferenze esplicite giustificate; assente, ignoto e non applicabile sono distinti. Anche l'assenza di figli nel nucleo attuale non dimostra assenza di una nascita/adozione recente. Parentela mai dedotta universalmente dall'età.
- **NASpI.** Rapporto terminato indipendente da studio/lavoro attuale; altri lavori e loro redditi hanno una verifica specifica. Checklist delle categorie escluse, disponibilità al lavoro, precedenti cessazioni volontarie da indeterminato nei 12 mesi e contributi successivi. L'eccezione sulle dimissioni è distinta dal caso ordinario. Oltre 68 giorni, un No alle fattispecie particolari permette l'esclusione ordinaria; Sì o non noto impediscono una conclusione automatica sul termine. Risoluzione consensuale generica e casi tutelati richiedono controllo del caso concreto. La riserva sui contributi agricoli include la possibile verifica degli ultimi 12 mesi. Non attribuiamo a una persona una revisione mai effettuata.
- **ADI.** Due fatti distinti: auto/moto oltre soglia senza agevolazione per disabilità; barche/aerei. Un bene agevolato non cancella un bene escludente. Il vecchio sì aggregato senza dettaglio rimane incerto. Il sì generico sulla disabilità non certifica automaticamente la categoria ISEE richiesta dalla misura.
- **Identità e ruoli.** Una sola misura/edizione toscana 2026, versioni precedenti e impronte conservate; nessuna deduplicazione generale per URL (le tre detrazioni affitto restano distinte). Fonte regionale e allegato letti: iscrizione alla scuola e ISEE minorenni contano, il solo titolo 3–6 non giustifica un no per anticipatari; tempi e disponibilità delle famiglie richiedono il Comune. Contributo al maestro artigiano sospeso dal catalogo pubblico con motivazione tracciata: la regola descrive i tirocinanti.
- **Date e promesse.** Cinque stati temporali; entrambe le date assenti non significano aperto. Il Bonus psicologo resta con disponibilità corrente non verificata: la fonte consultata riporta il 2025. Nessuna riapertura annuale presunta. Le etichette della demo descrivono confronti dei requisiti, non diritti certi. Il ramo imprese dichiara il solo perimetro dei filtri. «Quasi» non viene presentato come uno sforzo piccolo.
- **Interfaccia e validazione.** Tipi prima delle inferenze, valori finiti, interi dove necessari, enumerazioni e coerenza tra campi in entrambi i rami. Comuni riconosciuti, omonimi distinti per regione e codici ISTAT; nessuna correzione fuzzy. Richiedente unico per età/disabilità. Errori inline, invio ripetibile, blocco doppi invii, annullamento delle richieste superate. Modifica dal riepilogo con controlli precompilati e invalidazione dei soli dipendenti incoerenti. Parziali e singole età ignote conservati.
- **Spiegazioni ed esportazioni.** Alberi AND/OR annidati, risposta pertinente, confronto e fonte; note e limiti inviati alle schede. La provenienza territoriale è un indizio condiviso, non esclusione. Calendario selezionato esplicitamente fra risultati ammessi; ICS piegato per ottetti UTF-8, date giornaliere senza ora inventata. Report stampabile indipendente da gruppi chiusi, filtri e paginazione, con scelta del perimetro.
- **Provenienza.** Nuove estrazioni: hash di fonte/schema/prompt, snapshot, data di estrazione, acquisizione/versione soltanto se note; revisione umana separata e nulla se non attestata. Gli input vecchi non ricevono metadati di provenienza inventati. Il prompt mancante in un'importazione non viene ricostruito e dichiarato certo. Font remoti rimossi; il prodotto spiega che ogni passo trasmette il profilo completo al server.
- **Misure e limiti.** Report principali ricalcolati: 20% estrazione/Edoardo, 8% Edoardo/Lorenzo, 75% estrazione/Lorenzo, rispettivamente su 8/3/9 benefici. Nessuna etichetta o campione cambiato. Divergenze sintetiche e precisione delle foglie non sono errori normativi o accuratezza sui cittadini. Misura persone contro ordine fisso in `docs/misura-questionario-persone.md`; vantaggio piccolo. Avvio da copia pulita, installazione nuova e fascicolo offline verificati; non Docker/deploy, revisione umana completa, lettore di schermo o utenti reali. Stato ed evidenza di tutti i 27 rilievi nel rapporto delle correzioni.

**87. Bandi per imprese assenti da incentivi.gov.it: estrazione leggera, 174 regole fuori dalla demo per ora** (21/11, Edoardo con Claude; decisioni 61, 85).
- **Perché.** La demo delle imprese legge solo l'open data del portale. Fra i documenti raccolti dai siti di regioni, finanziarie regionali e Camere di commercio, 227 bandi per imprese non chiaramente chiusi non hanno un titolo simile né lo stesso link sul portale. Altri 269 ci sono già, quindi sono già nella demo. Edoardo vuole tutti i bandi nella demo, ma non quelli chiusi.
- **Chiuso o aperto:** si guardano le date nel testo. È chiuso se tutte le date scritte sono passate; è "non so" se non ci sono date. Per i documenti dello smistamento (decisione 85) vale lo stato dato lì.
- **Estrazione leggera** (`pipeline/estrai_imprese.py`, istruzioni in `docs/estrazione-imprese.md`). L'LLM legge al massimo 5.000 caratteri, cioè le sezioni su beneficiari e termini scelte da `pezzi()`. Scrive i requisiti con i campi delle imprese (tipologia, dimensione, settore, regione, comune, ambito, ATECO 2025), ognuno con la sua citazione, più al massimo 3 condizioni non modellabili e le date. 6 agenti per 227 documenti.
- **Risultato:** 174 regole con requisiti e 7 senza, **0 rifiutate** dal controllo di schema e citazioni (`python -m pipeline.estrai_imprese controlla`). Dopo la lettura, 46 documenti si sono rivelati non bandi (modulistica, pagine istituzionali, gare per fornitori) o bandi per le persone, e non sono stati scritti come regole.
- **Fuori dalla demo per ora.** Le regole sono in `data/regole_imprese_documenti/`, che `web/domande.py` non legge. Si collegano alla demo in un secondo momento, quando il codice della demo è fermo, per non lavorare in due sugli stessi file. Collegarle vuol dire aggiungerle a `ramo_imprese` e controllare che il questionario delle imprese le regga: il campione di imprese fittizie è costruito sul portale.
- **Ancora da fare:**
  - i 172 bandi aperti per gli enti, con lo stesso metodo (le tipologie "Ente Pubblico", "Cooperative/Associazioni Non Profit", "Università/Ente di Ricerca"); sono rimandati per non superare il 50% della finestra di 5 ore;
  - rivedere a campione le 174 regole.
- **Test:** `tests/test_regole_imprese_documenti.py`, che controlla lo schema e che le regole usino solo i campi delle imprese.

**88. Le regole dei bandi per imprese dai documenti entrano nella demo** (21/11, Edoardo con Claude; tocca `web/domande.py`; decisione 87).
- **Collegamento.** `ramo_imprese` ora legge, oltre al portale, `data/regole_imprese_documenti/` (`regole_imprese_documenti()`), con origine "estratta". Una regola estratta non dà mai "ti spetta", al massimo "da verificare", e mostra l'avvertenza.
  - Il questionario delle imprese, costruito sui filtri del portale, riceve solo i requisiti su un campo (`solo_campi`). Le condizioni non modellabili e le alternative restano nella regola intera, che decide l'esito.
  - `opzioni_imprese` non presume più che ogni requisito abbia un campo.
- **Territorio.** Se un bando regionale o camerale non scrive dove deve stare la sede, si aggiunge la regione dell'ente che lo pubblica. Per le persone la decisione 71 aveva scartato questo vincolo automatico, perché alcuni bandi comunali valgono anche per chi non risiede. Per le imprese invece la sede o l'unità locale nel territorio è quasi sempre richiesta, e senza il vincolo un bando della Camera di Bergamo comparirebbe a un'impresa di Palermo.
- **Tolte 10 regole** dopo un controllo dei titoli:
  - 4 pagine-elenco: "Bandi chiusi" della Camera di Brescia, due volte, e "Bandi 2025" e "Bandi 2026" del FVG;
  - 3 bandi 2025 della Camera di Lecce senza date, titolati "Scarica il testo del bando";
  - 3 doppioni della stessa misura su due siti ("Atelier dell'Immaginario", "Rafforza & Innova", "Lombardia Venture Step"): resta la copia con più date.

  Restano 164 regole con requisiti.
- **Effetto** (giorno 21/11). Le regole delle imprese aperte passano da 689 a 828. Ai bandi del portale si aggiungono quelli dai documenti, per esempio:
  - 23 per una microimpresa del commercio di Bergamo;
  - 6 per una cooperativa di Modena;
  - 1 per una piccola impresa turistica di Palermo, perché quasi tutti i documenti vengono dal Centro-Nord.
- **Test:** `test_la_demo_delle_imprese_le_legge`. 397 test passano.
- **Ancora da fare:** i 172 bandi aperti per gli enti (decisione 87) e una revisione a campione. Fra le regole rimaste c'è "bando ITS borse di studio" della Camera di Brescia, che probabilmente non è per le imprese.

**89. Fonti per le persone che mancavano: misure nazionali e bandi DSU della Lombardia** (21/11, Edoardo con Claude; decisioni 79, 82, 85).
- **Il buco**, regole aperte per le persone per regione al 21/11: Lombardia 41, Emilia-Romagna 19, Toscana 14, FVG 13, Umbria 10, Lazio e Piemonte 9, … Campania 4, Calabria, Liguria e Trentino 3, Marche e Molise 1, **Basilicata 0**. Per Veneto, Campania, Calabria, Molise, Sardegna e Lazio raccogliamo i fondi europei o le agenzie per il lavoro, non i bandi regionali per le famiglie.
- **Portali regionali: non raccolti.**
  - Le pagine elenco di Veneto (scadenzario), Basilicata, Sardegna e Calabria (bandi per la scuola) caricano l'elenco con JavaScript, e il raccoglitore vede la pagina vuota. Il portale della Basilicata è un sito WordPress, ma i bandi non stanno nei suoi contenuti pubblici.
  - Il portale del Lazio ha il robots.txt irraggiungibile, che per lo standard vale come divieto.
  - Della Campania si legge solo la pagina del territorio, che ha bandi per i comuni.
  - Una ricerca web dei bandi regionali per le famiglie ancora aperti a fine novembre ha trovato quasi solo bandi chiusi.
- **Aggiunti come documenti singoli** (`data/fonti/documenti.yaml`) ed estratti con 2 agenti, 6 su 6 accettati:
  - misure nazionali sempre aperte: **assegno di maternità dei Comuni** e **pensione di inabilità agli invalidi civili** (schede INPS che mancavano fra le 449 scaricate), **Fondo garanzia prima casa** (Consap);
  - bandi DSU 2026/27 di **Politecnico di Milano**, **Bocconi** e **Università di Brescia**: sono chiusi, ma la demo li mostra fra i "chiusi di recente, di solito riaprono" (decisione 72), e senza di loro uno studente di questi atenei non vedeva nessuna borsa.
- **Non aggiunti:**
  - l'avviso Alisei della Sardegna: `files.regione.sardegna.it` non risponde al robots.txt;
  - il contributo del Lazio per gli alunni con disabilità nelle scuole paritarie: estratto, ma chiuso il 13/11;
  - la Carta famiglia nazionale, che non esiste più dal 2022;
  - la Carta della cultura e la Carta del merito (MiC): robots vietato, vanno salvate a mano;
  - ERSU Sassari, ADSU Chieti-Pescara, ATER Roma: i siti provati non rispondono, gli indirizzi vanno verificati.
- **Ancora da fare:** gli elenchi delle Regioni in JavaScript (Veneto, Basilicata, Sardegna) richiedono di ricostruire per ognuna da dove il portale prende i dati, oppure il salvataggio a mano dei bandi aperti.

**90. Completamento mirato dei rilievi dopo cc097ba, preservando decisioni 87–89** (21/11, Codex su richiesta degli autori; nessuna revisione normativa umana attribuita).

- **Base e continuità.** Inizio su `23e9fe7`, suite iniziale 397 passati. Durante il lavoro è arrivato `8cf8088` con sei documenti persone: preservato e compreso nella suite finale. Prove nuove in `docs/completamento-2026-11-21/`, senza riscrivere audit o verifica precedenti. PDF utente e file concorrenti estranei lasciati intatti.
- **Rettifica della decisione 88.** Ritirato il requisito di regione derivato dal solo ente; conservati tutti i 164 YAML, 62 senza vincolo geografico rappresentato. Regione dell’ente solo per pertinenza e ordinamento. Questionario imprese: dati e opzioni delle alternative annidate, criterio finale dalla regola completa. Lista/conteggi/calendario condividono classificazione e gestione delle date. ITS Brescia: ruolo ITS e scadenza 16/11; Rinnova veicoli: finestre distinte e alternative PMI/ETS; Finaosta: destinatari alternativi; Erasmus Bolzano: residenza personale distinta da sede dell’impresa. Documenti e versioni precedenti con impronte conservati.
- **Regole persone.** NASpI chiede contribuzione agricola e prevalenza, distingue reddito autonomo presunto (soglia 5.500 nella fonte) e comunica i limiti di part-time/misti; letta la circolare 98/2025 completa con eccezioni da trasferimento e periodo dall’ultimo evento volontario. Buoni Toscana: ruolo, bambino, iscrizione e retta espliciti, ISEE minorenni e finestra comunale distinti. Psicologo: riacquisita fonte ufficiale, nessuna finestra 2026 verificata; non si deduce apertura dal 2025. Sede del corso: regione/comune/ISTAT per omonimi; istituzione e sede legale non inferite. ERDIS/ER.GO rettificati sui documenti completi disponibili.
- **Adjudicazione.** Fascicolo di 14 benefici, originali e differenze, 42 scenari proposti e decisioni da compilare. Etichette gold immutate. L’utente ha risposto «Si mette in da verificare» per co.co.co senza partita IVA/ISCRO: comportamento applicato alla sola demo e registrato in `data/indicazioni_autori_demo.yaml`. Fonte e nome del revisore normativo non forniti, quindi A23 resta aperto; nessun consenso più ampio attribuito.
- **Verifiche effettive.** 427 test passati; schema/citazioni 22 persone/gold, 272 documenti persone e 171 file imprese, zero errori. Offline storico: 8 snapshot, 5 regole e 5 casi NASpI con fatti agricoli ora espliciti. Nuove prove con hash e copie dei documenti mirati. Chrome: Castro/Puglia e Lombardia, modifica, report con indice di 269 voci; zero errori JS. Axe locale: zero violazioni nei tre stati finali dopo correzioni del contrasto, un controllo incompleto ciascuno. Non è VoiceOver. Gzip: 1.360.746 → 223.050 byte (−83,6%), JSON identico, mediana locale 64,3 → 76,4 ms su 20 richieste per codifica.
- **Metriche e limiti.** Profili del questionario immutati: 30,000 domande adattive contro 30,125 fisse; equivalenza 8/8 adattivo/fisso e stessi fatti, 5/8 contro modelli completi, differenze ERDIS conservate e analizzate. Confronti 20%/8%/75% riusati dal checkpoint, non ricalcolati né chiamati accuratezze sui cittadini. Registro finale: 16 risolti, 10 mitigati, A23 aperto. Docker assente; infrastruttura pubblicata, lettore di schermo e utenti reali non verificati. Nessuna nuova installazione pulita ripetuta per confermare il passato.

La descrizione storica della decisione 89 su «sempre aperte» e «di solito riaprono» non descrive il comportamento corrente: permanenza soltanto se documentata, archivio senza previsione di nuove edizioni. Le sei regole aggiunte restano preservate, con i limiti dei loro dati e i controlli di schema/citazioni effettivamente eseguiti.

**91. Controllo delle regole vecchie e dei doppioni; simulazione della demo del 21/11** (21/11, Edoardo con Claude).
- **`pipeline/vecchie.py`** scrive `docs/regole-vecchie.md` e non cancella niente: decide una persona. Segnala:
  - le regole senza una chiusura futura che nel titolo hanno solo anni passati ("a.a. 2025/2026" vale 2026);
  - quelle aperte da più di due anni senza chiusura;
  - le coppie di titoli quasi uguali nella stessa regione.

  Al 21/11, su 436 regole (persone dai documenti e imprese dai documenti): 36 probabilmente scadute e 10 possibili doppioni. Ci sono falsi allarmi, previsti: alcune misure della Lombardia sono servizi sempre aperti, "SALGO" e "RI-SALGO" sono due misure diverse. Test in `tests/test_vecchie.py`.
- **`prove/simulazione/riepilogo.py`** fa rispondere al questionario le 4 persone di prova, senza server, e valuta i 4 profili della demo. Il risultato è in `docs/simulazione-2026-11-21.md`, con l'elenco dei "possibili" da giudicare a mano (pertinente sì o no).
  - Persone di prova: **26-33 domande** (erano 13-21 il 20/11), 0-1 "ti spetta", 4-10 "possibili".
  - Profili della demo: 4-15 "possibili".
- **Da decidere:** l'aumento delle domande viene dai campi aggiunti il 21/11 per singoli bandi (`reddito_locazione_2025`, `eta_giovani_locazione_2025`, `iscrizione_postlaurea_ergo`, `isee_prestazioni_familiari_2026`, `isee_minorenni`, `genitore_tutore_buoni_toscana`, `lavoro_terminato`). Ognuno rende un bando più preciso, ma allunga il questionario per tutti. Proposta: chiederli solo dopo le domande generali e solo se il bando è ancora "possibile", oppure trasformarli in domande di conferma sul singolo bando.

**92. Rettifiche di soglie, periodi del reddito e indicatori ISEE** (21/11, Codex su richiesta dell’utente; revisione normativa umana non attestata).

- **Due false esclusioni corrette.** ISCRO: reddito autonomo dell’anno precedente e soglia 2026 di 12.749,18 euro, invece del limite storico di 12.000 sul reddito IRPEF generico. Pensione di inabilità: prima liquidazione sul presunto corrente; successive su pensioni correnti più altre tipologie dell’anno precedente. I due casi 12.500 ISCRO e 30.000 passato/zero corrente inabilità passano da non idoneo a da verificare, con le altre riserve conservate.
- **Controllo esteso.** Censiti 146 confronti economici in 98 regole; 17 regole rettificate in totale. Correzioni di periodi fiscali/età per detrazioni affitto, canone/ISEE/IMU Genova, ISEE minorenni FVG, indicatori specifici Lombardia/Pescara/Perugia/FILSE, nuovo ISEE familiare/inclusione ADI/SFL/Nuovi nati; tolte deduzioni di proprietà dal patrimonio ISEE Palermo e soglia tampone inventata ERSU Catania. Non è una certificazione semantica dell’intero corpus.
- **Versioni e fonti.** Gold preservato; sostituzioni operative ISCRO/SFL separate. Originali e impronte delle 17 rettifiche, 12 acquisizioni ufficiali nuove e 12 copie integrali locali in `docs/verifica-economia-2026-11-21/`. Perugia live ha risposto 403: usata la copia locale completa, limite dichiarato. Le ambiguità richiedono verifica specifica con ente/CAF; non sono risolte per inferenza. Co.co.co ISCRO resta da verificare secondo l’indicazione utente già registrata.
- **Protezione annuale e domande.** `anno_soglia` richiede contesto concordante, derivato dalla data server e non iniettabile. Somma dei redditi per rinnovo derivata, non input API. Il misuratore sintetico accetta un anno esplicito e lo dichiara nel report. Domande e aiuti distinguono periodo, documento e indicatore; importi leggibili con centesimi.
- **Verifiche effettive.** 482 test passati, inclusi 52 casi economici nuovi e un controllo del misuratore annuale. Schema/citazioni: 24 persone/gold/revisioni e 272 documenti, zero errori. Offline storico e integrità del fascicolo precedente verificati; nuove fonti/versioni verificate per hash. Chrome: due percorsi di 24 e 27 risposte, correzioni oltre soglia e ritorno, prima liquidazione/rinnovo, zero errori JS.
- **Costo e limiti.** Fixture storiche immutate: 34,875 domande adattive contro 35,000 fisse; equivalenza 8/8 adattivo/fisso e stessi fatti, 5/8 modelli completi. Più dati corretti comportano più domande; la proposta della decisione 91 resta da valutare con utenti. Registro invariato: 16 risolti, 10 mitigati, A23 aperto. Non ripetute installazione pulita/accessibilità/stampa, non verificata infrastruttura pubblicata. Dettagli, limiti e riproduzione nel nuovo rapporto.

**93. Questionario più corto e verifiche finali sugli aiuti possibili** (21/11, Edoardo con Claude; tocca `web/domande.py`, `web/validazione.py` e `web/static/js/app.js`, su richiesta di Edoardo; decisioni 70, 78, 80, 92).
- **Il problema** (simulazione del 21/11, decisione 91). Le persone di prova rispondevano a 26-33 domande e avevano 0-1 "ti spetta". La causa dei pochi "ti spetta": quasi ogni aiuto possibile ha 1-2 condizioni che il questionario non chiede (contratto registrato, figlio al nido, ansia o stress per il bonus psicologo, nessun altro sostegno contro la povertà). Il motore non le conosce e l'esito resta "possibile" per sempre. Il limite sulle regole estratte ne bloccava una sola.
- **Questionario** (`prossima_persone`):
  - contano solo gli aiuti nazionali e quelli delle regioni vicine: i bandi di altre regioni non fanno domande;
  - una domanda specifica, che serve a meno di 3 aiuti (`MIN_USI`), si fa solo se quell'aiuto è probabile, cioè è una regola rivista a mano (gli aiuti principali) oppure ha già un requisito a favore;
  - prima le domande generali, poi quelle specifiche;
  - l'età nel 2025 per la detrazione affitto giovani si ricava dall'età di oggi quando è certa (`ricava_doppioni`). Il reddito per le detrazioni e l'ISEE per le prestazioni familiari invece no: non coincidono sempre con il reddito IRPEF e l'ISEE ordinario, e i test della decisione 92 lo fissano.
- **Verifiche finali** (`verifiche`, `applica_conferme`). Per gli aiuti possibili della zona, con almeno un requisito a favore e al massimo 2 condizioni aperte, la pagina finale mostra "Sono possibili questi: verifica se ti spettano", con una domanda Sì / No / Non lo so per ogni condizione e la citazione. Prima gli aiuti a cui manca una sola risposta, poi le regole riviste; al massimo 10.
  - Sì a tutte porta l'aiuto a "ti spetta", anche se la regola è estratta (resta l'avvertenza). Un no lo esclude.
  - Le risposte stanno nel profilo come `conferme` e sono controllate da `web/validazione.py`.
- **Effetto** (`docs/simulazione-2026-11-21.md`):
  - persone di prova: **20-24 domande** (erano 26-33);
  - "ti spetta" confermando tutte le verifiche: **5, 3, 8, 6** (erano 1, 0, 0, 1);
  - profili della demo: 3, 10, 8, 10.

  Sono massimi: chi risponde no a una condizione perde quell'aiuto.
- **Obiettivo non ancora raggiunto:** circa 15 domande. Le domande specifiche delle regole riviste (NASpI, ISCRO, ADI) ne aggiungono ancora 5-8; il passo successivo è spostarle fra le verifiche finali quando l'aiuto non ha ancora niente a favore.
- **Test:** `test_verifiche_finali_portano_a_ti_spetta` e `test_domande_specifiche_solo_per_bandi_probabili`. 484 test passano.

**94. Le domande specifiche degli aiuti principali passano alle verifiche finali: questionario a circa 15 domande** (21/11, Edoardo con Claude; tocca `web/domande.py`; decisioni 78, 93).
- **Domande specifiche.** Una domanda che serve a meno di 3 aiuti si fa nel questionario solo se uno di quegli aiuti ha già un requisito a favore, anche per le regole riviste a mano. Le condizioni che restano aperte arrivano alla fine, fra le verifiche (decisione 93), che ora comprendono anche gli aiuti principali senza niente a favore, per esempio l'assegno unico prima di sapere se un figlio è a carico.
- **Cosa conta "a favore"** (`a_favore`, decisione 78). Nella condizione lavorativa e nel tipo di lavoro conta un valore che sceglie una minoranza: "disoccupato", "studente", "pensionato", "autonomo", "parasubordinato". Non conta un valore che vale per metà della popolazione: "occupato", "dipendente". Così per un disoccupato la NASpI resta probabile e fa le sue domande nel questionario, mentre congedi e fondi per i dipendenti non le fanno a chi lavora.
- **Prove.** `risposte_vere` risponde alle verifiche con i dati della persona di prova; le condizioni che nessun dato dice valgono sì (simulazione, per misurare il massimo) oppure "non lo so" (test).
- **Effetto** (`docs/simulazione-2026-11-21.md`):
  - persone di prova: **14-15 domande** (26-33 prima della decisione 93);
  - "ti spetta" dopo le verifiche, rispondendo con i loro dati: **5, 3, 8, 6**;
  - profili della demo: 3, 10, 8, 10.
- 484 test passano.

**95. Le misure nazionali senza date sono permanenti: tornano fra i possibili e possono diventare "ti spetta"** (21/11, Edoardo con Claude; tocca `web/domande.py` e un test di `tests/test_economia.py`; decisioni 92-94).
- **Il problema, visto provando la demo nel browser.** `gruppo_risultato` (decisione 92) mette nel gruppo "date da verificare" ogni regola senza apertura né chiusura. Quel gruppo non conta fra i possibili e non riceve l'esito pieno. Le prestazioni INPS e le misure nazionali (assegno unico, bonus nido, bonus psicologo, bonus luce e gas, detrazioni, Fondo prima casa) non hanno date perché si chiedono tutto l'anno, quindi sparivano proprio gli aiuti principali. Alla famiglia monoreddito la pagina mostrava 2 possibili, mentre il motore ne trovava 15.
- **Correzione** (`permanente_se_nazionale`, al caricamento delle regole). Una regola senza date, INPS o di una fonte nazionale, ha `disponibilita: permanente`, il valore che `stato_temporale` già prevede. I bandi locali senza date restano "da verificare". I file delle etichette non cambiano.
- **Prova nel browser,** profilo "Famiglia monoreddito", "Non lo so" alle 3 domande rimaste: 15 possibili. Con un "Sì" alle verifiche di assegno unico, bonus nido e bonus psicologo, la pagina mostra **3 misure compatibili** e 12 possibili.
- **Prova** con uno studente di 22 anni senza figli a Milano: nessun aiuto per figli, maternità o congedi fra i possibili o fra le verifiche.
- Il test `test_api_non_riproduce_le_due_false_esclusioni` ora accetta "permanente" per la pensione di inabilità agli invalidi civili, che è una prestazione INPS senza scadenza. Il resto del controllo resta uguale: niente calendario, niente "ti spetta" automatico. 484 test passano.

**96. Ordine delle verifiche finali** (22/11, Edoardo con Claude; `web/domande.py`, `verifiche`; decisione 93). Prima gli aiuti a cui manca una sola risposta. Poi quelli con più requisiti già a favore, senza contare il territorio, che è a favore di tutti i residenti. Poi le regole riviste. Per uno studente di 22 anni a Milano il bonus psicologo passa davanti a "orfani di femminicidio".

**97. Materiale per la consegna: lista di revisione, bozza del report, percorso della presentazione** (22/11, Claude per Edoardo e Lorenzo).
- `prove/simulazione/da_rivedere.py` scrive `docs/da-rivedere-a-mano.md`: le 30 regole che compaiono più spesso alle 8 persone di prova, con link e colonna per l'esito. In cima: bonus psicologo (8 su 8), Carta Dedicata a te (6), detrazione inquilini (5), Fondo prima casa (4), assegno unico (3). Va fatta a mano, senza LLM, e dà il numero di revisione del report.
- `docs/report-bozza.md`: bozza di una pagina con lo schema dell'architettura, la tabella delle misure e i limiti. I due numeri che mancano (misura dopo la seconda passata, revisione a mano) sono segnati fra parentesi quadre.
- `docs/presentazione.md`: percorso di circa 10 minuti con data fissa (`TROVA_BANDI_GIORNO=2026-11-22`), la famiglia monoreddito, uno studente dal vivo e un'impresa.

**98. Raccolta dei comuni aggiornata al 22/11** (22/11, Claude). Rilanciati i raccoglitori dei 47 comuni (`pipeline.fonti.elenchi`, robots.txt e pause): 35 documenti nuovi. 8 sono bandi per le persone senza regola; estratti con 2 agenti, tutti accettati. Restano fuori "Dopo di noi" di Perugia, chiuso, e i contributi per lo sport di Prato, che sono per le associazioni e vanno fra le regole senza requisiti. Entrano:
- patto di cura e sostegno familiare 2027-28 per persone non autosufficienti (Andria e Trani, regione Puglia, fino al 17/12);
- rimborso delle spese veterinarie per famiglie con ISEE basso (Massa, fino al 7/12);
- rimborso dei libri di testo 2026/27 (Teramo, fino al 31/1/2027).

Gli altri documenti nuovi sono avvisi per enti, gare, eventi e sponsorizzazioni, oppure bandi che avevano già una regola dalla raccolta dell'8/11.

**99. Raccolta delle regioni e delle altre fonti aggiornata al 22/11, solo i bandi nuovi** (22/11, Claude). La prima passata sulle 82 fonti non comunali riscaricava ogni bando già salvato: con 3 secondi di pausa per pagina e per PDF, circa 9 secondi a bando, in un'ora e mezza aveva finito 12 fonti (Toscana e Sicilia da sole hanno più di 150 bandi). Nuova opzione `--nuovi` in `pipeline/fonti/elenchi.py`: rilegge l'elenco ma scarica solo i bandi senza documento. Le 71 fonti restanti sono andate 5 alla volta su siti diversi, e le 21 che passano dal portale una alla volta. Alternative scartate: ridurre la pausa (scortese verso i siti); aspettare la fine (ore, per bandi che avevamo già). In tutto 76 documenti nuovi senza regola, smistati in `data/pubblico/smistamento-2026-11-22.yaml`: 4 bandi aperti per le persone (case popolari a Cassine, Pianiga e Stra; agenzia per l'affitto e mutuatari di Alessandria), estratti con un agente e tutti accettati. Altri 13 bandi per le imprese non sono sul portale (FILSE, Sviluppo Toscana, Piemonte agricoltura e turismo, Umbria vino, Lazio "Giovani attività professionali" e CES, Sicilia pesca e turismo): estratti con `pipeline/estrai_imprese.py`, tutti accettati. Il resto: bandi per enti (31, non estratti come già deciso), concorsi e avvisi che non sono bandi, doppioni e chiusi. Non raccolta l'agenzia per lo studio della Toscana: la pagina dell'elenco dà 404. Il test che contava 164 regole per le imprese ora conta i file della cartella. Simulazione rifatta: invariata, salvo l'operaia di Bari (16 domande invece di 15).

**100. Bandi scaduti e doppioni: date corrette, scaduti e doppioni messi da parte** (22/11, Claude, su richiesta di Edoardo). `docs/regole-vecchie.md` segnalava 36 regole probabilmente scadute e 10 coppie di possibili doppioni. Ho letto le date nel testo di ognuna e controllato anche tutte le altre regole senza data di chiusura. Risultato:
- **Date corrette in 11 regole**, ognuna con una nota che riporta la frase del bando. Fra queste: gli orfani di femminicidio in Lombardia (chiuso nel 2021, usciva fra le verifiche finali) e il contributo per le lavastoviglie in Sicilia (chiuso il 31/12/2025, usciva come possibile ai siciliani). Una era al contrario: l'apprendistato del Piemonte risultava chiuso, ma il testo lo proroga al 31/12/2026.
- **3 regole scadute senza data** spostate in `scadute/`: la TARI 2025 di Prato, il bando FVG sulle assicurazioni della casa del 2025 (c'è quello del 2026) e un concorso per medici del 2023 che non è un bando. **3 doppioni per le imprese** spostati in `doppioni/`: la stessa misura pubblicata da Finpiemonte e dalla Regione, o da Lazio Innova e Lazio Europa. Si tiene la copia con le date. La demo non legge le sottocartelle.
- **24 regole controllate e ancora aperte, o coppie che non sono doppioni**, scritte con il perché in `data/pubblico/vecchie-controllate.yaml`. Per esempio "L.R. 34/2004", dove l'anno è quello della legge; ERSU Messina e ERSU Palermo, che hanno lo stesso titolo ma sono enti diversi. I buoni scuola della Toscana restano due file: la demo ne mostra già uno solo.
- **`pipeline/vecchie.py` più preciso.** Ora legge anche il testo: "Data scadenza: 31/12/2025" passata è il segnale più affidabile, e da solo ha trovato 4 casi che il titolo non mostrava. Non segnala più le regole che hanno già una chiusura (la demo le nasconde) né quelle controllate. Restano 6 casi da decidere a mano, perché il testo non basta (Fondo imprese femminili della Calabria, microcredito adozioni del Lazio, mutuo prima casa del FVG, patenti in Sardegna, due bandi agricoli del FVG).
Alternative scartate: cancellare le regole (si perde la storia e non si torna indietro facilmente); togliere tutte le 36 segnalate (circa 20 sono ancora aperte); inventare una data di chiusura per le scadute senza data. Simulazione: la studentessa di Milano e il commerciante di Palermo perdono ciascuno un possibile che non era più aperto.

**101. Verifiche finali e "possibili" pertinenti: niente aiuti con a favore solo il territorio o con una condizione contraddetta dai dati già noti; numeri del report ricalcolati** (22/11, Claude, su richiesta di Edoardo; tocca `web/domande.py`, `tests/test_web.py`, `docs/report-bozza.md`; decisioni 70, 78, 93-96).
- **Il problema, visto nella demo.** Fra le verifiche finali ("Sono possibili questi") e fra i "possibili" uscivano aiuti che non c'entrano: allo studente universitario di 22 anni a Milano il buono scuola della Lombardia, il contributo per chi fa la chemioterapia, "Io viaggio" per gli over 65; a chi vive solo la Carta "Dedicata a te" per i nuclei di almeno 3 persone; a una pensionata di Alessandria le case popolari di Boves. Due difetti generali, non dei singoli bandi:
  1. **Il territorio contava "a favore".** La decisione 96 lo toglieva solo dall'ordine; per entrare bastava abitare in Lombardia. Ora, per le persone, non conta né per entrare fra le verifiche né per essere "possibile" (`a_favore(..., conta_territorio=False)`), come già la residenza in Italia (decisione 78). Per le imprese resta come prima.
  2. **Le condizioni scritte a parole non si confrontavano con i dati.** `contraddetto` scarta una condizione aperta quando i dati noti la rendono impossibile:
     - una frase su nido o scuola dell'infanzia senza nessuno di 6 anni o meno nel nucleo; su scuola primaria o secondaria, alunni, carriera scolastica senza nessuno di 20 anni o meno; che comincia con "il figlio" o "il minore" senza figli né minori; su anziani o over 65 senza nessuno di almeno 60 anni; su persone non autosufficienti se nessuno nel nucleo ha una disabilità (`PERSONA_RICHIESTA`). Un'età o una disabilità non note non escludono niente;
     - nelle regole estratte, un'alternativa la cui via con i dati è già esclusa e che resta aperta solo per un'eccezione scritta a parole (nucleo di almeno 3 persone per chi vive solo; "residente nei comuni elencati, o lavora lì" per chi abita altrove). Non vale per le vie sulla cittadinanza, perché il vocabolario non ha tutti i titoli di soggiorno e la via "stranieri con permesso" è vera (assegno di maternità dei Comuni per la famiglia extra UE della demo), e non vale per le regole riviste a mano.
  Un aiuto contraddetto non viene escluso: esce dalle verifiche e da "possibili" e finisce in "Non sappiamo dirlo", con i suoi requisiti visibili.
- **La domanda di verifica mostra solo la parte aperta** (`ancora_aperto`): in un'alternativa si tolgono le vie già escluse. Alla famiglia extra UE l'assegno unico chiede solo dei titoli di soggiorno, non più "cittadinanza italiana o UE".
- **Alternative scartate:** un'eccezione per bando (la regola è generale, e i bandi nuovi ne avrebbero bisogno ogni volta); cercare "figli" in ogni frase (compare anche in "non spetta ai nuclei con figli"); escludere gli aiuti contraddetti ("non ti spetta"), perché una frase a parole non è una prova; "asilo" fra i segnali, perché vale anche per il diritto d'asilo.
- **Effetto**, verifiche finali prima → dopo: studente di 22 anni a Milano 8 → 2 (bonus psicologo, detrazione affitto); lavoratore autonomo 8 → 2; pensionata sola 10 → 7; studente fuorisede 3 → 2; famiglia monoreddito 10 → 10, invariata, con assegno unico, nido, congedi, centri estivi e assegno di maternità. "Possibili" in `docs/simulazione-2026-11-22.md`: operaia 6 → 5, infermiere 4 → 3, studentessa 9 → 4, commerciante 6 → 5, studente 4 → 2, famiglia 15 → 14, autonomo 7 → 1, pensionata 14 → 10. Il profilo dell'autonomo ora ha un solo possibile: è un motivo in più per cambiare i profili d'esempio (`docs/da-fare.md`, punto 8).
- **Prova nella demo** (`TROVA_BANDI_GIORNO=2026-11-22`): lavoratore autonomo e famiglia monoreddito fino alla pagina finale, nessun errore nella console.
- **Test:** `test_verifiche_contraddette_dai_dati_noti`, `test_verifiche_pertinenti_per_studente_famiglia_pensionata`, `test_via_della_cittadinanza_non_chiude_alternativa`. 489 test passano.
- **Report** (`docs/report-bozza.md`): numeri ricalcolati al 22/11 con il comando accanto a ognuno. Le regole per le persone sono 343 caricate, di cui 152 aperte o permanenti; per le imprese 839, di cui 546 aperte. La bozza diceva "336 / 831 aperte", ma erano le regole caricate. Inoltre 2.397 documenti, 101 decisioni e 489 test. Restano fra parentesi quadre la misura dopo la seconda passata e la revisione a mano.

**102. Pagine di annuncio: si segue il rinvio al PDF del bando dello stesso ente; 11 regole rifatte** (22/11, Claude, su richiesta di Edoardo; tocca `pipeline/fonti/elenchi.py`, `pipeline/fonti/documenti.py`, `tests/test_elenchi.py`; decisioni 57, 99, 101).
- **Il problema.** Molte regole vengono da pagine web brevi che annunciano il bando e rimandano al PDF con i requisiti (`docs/da-fare.md`, sezione 0, punto 6). Nella demo restano sempre "da verificare", con condizioni come "i requisiti sono nell'avviso allegato". Al 22/11 erano 54 le regole aperte per le persone che lo dicono esse stesse; 41 con meno di 10.000 caratteri di testo. Il raccoglitore scaricava il PDF solo per le fonti con una regola `allegato` in `elenchi.yaml`, e a Cassine aveva preso il "manifesto" invece del bando.
- **Regola generale** (`segui_rinvio`). Su una pagina di annuncio si prende il PDF del bando:
  - dentro il contenuto principale e sullo stesso sito, anche un sottodominio dello stesso ente;
  - il cui nome o link dice bando, avviso, regolamento, criteri, delibera, determina o disposizione;
  - scartando moduli, graduatorie, elenchi, informative, manifesti, FAQ, guide ISEE e versioni in inglese.

  Se la pagina non ha PDF, si segue una volta un link "Leggi il bando" o "avviso" dello stesso sito e si cerca lì. Valgono robots.txt e le stesse pause della raccolta. La raccolta lo fa da sola per le pagine nuove sotto 3.000 caratteri senza allegato. Per quelle già salvate si usa `python -m pipeline.fonti.elenchi --rinvii <id ...>`, che rilegge la copia locale della pagina o, se manca, la scarica. Il PDF si aggiunge alle pagine del documento (`rinvio`, `pagine_rinvio`).
- **Applicata a 21 dei 25 candidati con un link utile.** Ne ho tolti 4 a mano: l'assegno di maternità dei Comuni (il PDF trovato era una tabella INPS dei tempi), il microcredito adozioni del Lazio (uno dei 6 casi dubbi di `docs/regole-vecchie.md`, da non toccare), ESU Molise ed ESU Verona (il link portava a un altro avviso). Risultato:
  - **PDF del bando trovato per 11.** Gli id: adisu-puglia-bando-orfani-0d8702 adisurc-campania-borse-di-studio-865c7f adsu-teramo-contributi-tesi-di-laurea-f588bb adsu-teramo-diversamente-abili-contributi-8889d4 atc-piemonte-sud-bando-generale-di-concorso-per-il-comune-61ec81 atc-piemonte-sud-bando-generale-di-concorso-per-il-comune-ce1e62 ater-vicenza-bandi-edilizia-residenziale-pubblica-f3e1d2 ergo-collaborazioni-studentesche-0a8332 laziodisco-premio-di-laurea-1959c9 lombardia-dote-unica-lavoro-persone-con-disabilita-bdd558 lombardia-servizi-integrativi-prov-mantova-ffc3da 
  - **Nessun PDF riconoscibile per 9** (Finaosta, Piacenza, Umbria, Lecco, ERDIS, LazioDisco alloggio).
  - **Napoli non scaricata:** il sito dei PDF ha robots.txt protetto (403).
- **Estrazione:** `pipeline.estrai_documenti prepara` (solo le sezioni sui requisiti), 3 agenti separati che vedono solo i prompt (circa 530.000 token in tutto), `importa`. **11 su 11 accettate al primo tentativo**, citazioni parola per parola.
- **Effetto.**
  - Le condizioni controllabili con i dati aumentano: per esempio ATER Vicenza da 0 a 7, Cassine e Carentino da 5 a 9, ADSU Teramo disabili da 3 a 11, ADISU Campania da 1 a 49.
  - Il rinvio a un documento mancante sparisce in 8 regole su 11. Restano Mantova e Bergamo (il PDF è la determina, non l'avviso) e LazioDisco premio di laurea (i requisiti ISEE stanno nel bando dell'anno prima).
  - Tre bandi ora hanno le date del PDF e risultano chiusi: orfani ADISU Puglia (11/6/2026), borse ADISU Campania (10/9/2026), collaborazioni ERGO (24/8/2026). Prima, senza date, sembravano aperti.
  - In tutto le regole aperte che rimandano a un documento mancante passano da 54 a 48; fra quelle con poco testo, da 41 a 31.
  - Nella demo, a chi abita nell'ambito di Cassine il bando ha 3 requisiti a favore, fra cui l'ISEE; alla pensionata di Torino va in "Non sappiamo dirlo".
  - La simulazione delle 8 persone non cambia: nessuna abita in quei comuni o studia in quegli atenei.
- **Alternative scartate:**
  - prendere qualsiasi PDF della pagina: spesso il primo è il modulo di domanda;
  - seguire link verso altri siti: non è lo stesso ente, e il bando regionale non è quello comunale;
  - più di un passaggio fra pagine: diventa una navigazione del sito;
  - rifare le 16 regole senza link utile cercando il bando a mano: fuori dalla regola generale.
- **Limite:** `data/raw/documenti` non è in git. Su un'altra macchina le 11 regole passano il controllo delle citazioni solo dopo aver rifatto il download con `--rinvii` sugli stessi id.
- 490 test passano. Controlli: 282 regole dai documenti, 184 per le imprese e 24 fra regole scritte a mano, etichette e revisioni, 0 errori.

**103. Rinvio al PDF più preciso: prima il bando poi l'atto, pagine intermedie con parole del titolo, file su un altro sito solo se si chiamano "bando"; 5 regole rifatte** (22/11, Claude, su richiesta di Edoardo; tocca `pipeline/fonti/elenchi.py`, `tests/test_elenchi.py`; decisione 102).
- **Perché.** Dopo la decisione 102 restavano 31 regole aperte, con poco testo, che rimandano a un documento non ricevuto. Guardandole una per una, i casi recuperabili avevano tre difetti generali della regola:
  - **Nomi dei file.** In "LC_Allegato A_Bando" il trattino basso conta come lettera, quindi `\bbando` non riconosceva la parola. Ora si usa "non preceduto da una lettera".
  - **Il primo PDF che citava il bando.** Spesso era il decreto che "approva lo schema di bando" (Lecco, Como, Mantova, Bergamo). Ora c'è un ordine: prima bando, avviso, allegato A, regolamento, criteri, foglio informativo; poi delibera, determina, decreto, disposizione. A pari livello, prima lo stesso sito.
  - **La prima pagina intermedia con "avviso".** All'ESU Molise era quella della mensa. Ora la pagina va seguita solo se il link ha almeno due parole in comune con il titolo del bando, oppure è un "Leggi il bando" generico, oppure è un link senza testo all'Amministrazione trasparente, dove gli enti pubblici devono pubblicare gli avvisi. I link a un anno accademico già finito ("2025/2026" a novembre 2026) si saltano.
- **Nuovo:** un PDF su un altro sito si accetta solo se sia il testo del link sia il nome del file dicono "bando" o "avviso". È il caso del Comune di Taranto, che tiene gli allegati sul servizio esterno del suo portale. Non si seguono link a pagine di altri enti, come il bando del Ministero dell'Interno citato da Forlì.
- **Applicata alle 31 regole.** Ne restano fuori 7: l'assegno di maternità dei Comuni e il microcredito adozioni, come nella decisione 102; Napoli, per robots.txt; le 3 pagine dell'Umbria, che non sono aiuti per le persone (corso per direttori del servizio sanitario, equivalenza di titoli, apicoltura). La prova trova un documento per 7 regole:
  - **ASLO Alessandria:** la pagina della trasparenza rimanda in cerchio (redirect infinito, probabilmente vuole una sessione del browser), quindi non scaricata;
  - **ESU Molise:** la pagina del bando 2026/2027 non ha PDF;
  - **5 PDF scaricati:** Taranto (avviso buoni libro), Finaosta (foglio informativo del mutuo prima casa, DGR 369/2026), Lecco, Mantova e Bergamo (Allegato A o avviso al posto della determina presa con la decisione 102).
- **Estrazione:** 1 agente per i 5 prompt, perché il limite di 5 ore era al 65%; circa 150.000 token. 5 su 5 accettate.
  - Due correzioni a mano, senza toccare le citazioni. Nella regola Finaosta la regione diventa il nome ISTAT "Valle d'Aosta/Vallée d'Aoste", come vuole `test_regioni_nelle_regole`.
  - A Lecco e Mantova rimesse le date dello sportello (17/12/2025-26/02/2027), con una nota. Le date stanno nella pagina web, che è ancora nel documento, ma l'Allegato A non le ripete e la nuova estrazione le aveva perse.
- **Effetto:**
  - Le regole aperte che rimandano a un documento mancante passano da 48 a 44; fra quelle con poco testo, da 31 a 28.
  - Bergamo passa da 1 a 4 condizioni controllabili (inserimento per i disoccupati del collocamento mirato, mantenimento per gli occupati); Finaosta da 1 a 4; Lecco da 1 a 3.
  - Simulazione invariata; 491 test passano; controlli con 0 errori.
- **Alternative scartate:** cercare a mano il bando delle 28 regole rimaste (fuori dalla regola generale); seguire i link a pagine di altri enti; aggirare il redirect di Alessandria con i cookie.
- **Da ricordare:** quando si rifà l'estrazione con il PDF, le date che stavano solo nella pagina web possono andare perse. Controllare `apertura` e `chiusura` prima e dopo, come qui.

## 24/11/2026

**104. Allineamento del 24/11: i bandi dei Comuni contano solo nel proprio comune, "inattivi" comprende studenti e pensionati, profili d'esempio nuovi, README di nuovo una panoramica** (24/11, Lorenzo; risponde alle decisioni 75, 76, 97 e 103 e al punto 8 di `docs/da-fare.md`; tocca `web/domande.py`, `web/static/js/`, `web/profili_demo.yaml`, i test, `prove/simulazione/`).
- **Allineamento.** I 31 commit di Edoardo del 20-22/11 (decisioni 76-103) arrivano qui con un fast-forward. Sulla macchina di Lorenzo mancavano i testi delle regole nuove, che non sono in git. 58 sono stati riscaricati con il raccoglitore del progetto, poi i rinvii al PDF con `--rinvii`. Restano 19 regole che qui non si controllano:
  - 12 senza testo: 7 siti con robots.txt irraggiungibile o vietato (ESU Padova ×3, UniBg, UniBs, Bologna, Como) e i 5 PDF salvati a mano da Edoardo (detrazioni affitto ×3, Milano ×2);
  - 7 con citazioni che non si trovano sulla pagina di oggi (LazioDisco ×4, ADISU Puglia, ADISU Campania, ERGO): le pagine sono cambiate, o il rinvio non trova più il PDF.

  Sono state controllate sui testi di Edoardo. **Proposta:** mettere in git i testi citati dalle regole, qualche decina di MB invece delle centinaia scartate il 7/11, così chiunque può rifare il controllo.
- **Test che dipendeva dai testi** (`tests/test_economia.py`): ora salta il controllo delle citazioni se i testi non ci sono, come gli altri test che richiedono `make dati`. Prima falliva su ogni macchina diversa da quella di Edoardo, quindi anche su quella di chi corregge. Il controllo dell'etichetta originale e dello schema resta sempre attivo.
- **Bandi dei Comuni, solo nel proprio comune** (decisione 76, scelta di Lorenzo). `comune_ente` dà il Comune che pubblica il bando (dalle fonti `comunale` di `elenchi.yaml`, `documenti.yaml`, `manuali.yaml`). `fuori_zona` lo considera lontano se non è il comune di residenza, di domicilio o della sede del corso. Lontano vuol dire che:
  - non fa domande;
  - non entra nelle verifiche finali;
  - va nel gruppo chiuso, ora "In altri comuni o regioni".

  Non cambia l'esito, e un bando che scrive il vincolo e lo vede soddisfatto ("compatibile") resta vicino. Con il comune "non lo so" non si filtra. "Reggio Calabria" della fonte diventa il nome ISTAT "Reggio di Calabria". Anche i "chiusi da poco" seguono lo stesso filtro. Effetto alla data del 22/11: l'operaia di Bari fa 14 domande invece di 16, e la pensionata di Torino non vede più fra le verifiche l'agenzia per l'affitto di Alessandria. Test: `test_bandi_di_un_altro_comune_della_stessa_regione`.
- **"Inattivi"** (decisione 75, scelta di Lorenzo). Nel vocabolario `inattivo` vuol dire "né lavora né cerca lavoro, e non è studente né pensionato". Nei bandi "inattivi" comprende anche studenti e pensionati, "non occupati" vuol dire tutto tranne `occupato`, "inoccupati" vuol dire `disoccupato`. Le 7 regole in uso che scrivevano `inattivo` sono state rifatte con un agente che vede solo il prompt (Urbino, Toscana ×4, ERDIS Marche ×2): 7 su 7 accettate.
  - Vecchie contro nuove: accordo sugli esiti 88%.
  - Sulle persone di prova la studentessa lavoratrice di Milano non è più esclusa da tre bandi del lavoro (ora "serve una risposta").
  - Lo studente residente a Palermo ora è escluso dal servizio civile toscano, che chiede residenza o domicilio in Toscana.

  Le regole di `gold`, `sviluppo` e `seconda-estrazione` non cambiano: servono alle misure.
- **3 regole dell'Umbria fuori dalle persone** (decisione 103): corso per direttori sanitari, equivalenza dei titoli, apicoltura. Vanno in `documenti-senza-requisiti`, come il FERAU (decisione 76). Restano "da verificare" le 28 regole che rimandano a un documento non ricevuto (scelta di Lorenzo).
- **Profili d'esempio** (punto 8 di `docs/da-fare.md`, deciso da Edoardo). I profili di prima non rispondevano alle domande aggiunte il 21/11 (lavoro terminato, ISEE per le prestazioni familiari, reddito per le detrazioni), quindi la pagina chiedeva ancora qualcosa, e nessuno arrivava a "ti spetta". Ora:
  - ognuno risponde a tutto il questionario;
  - le **verifiche finali** hanno le risposte **vere** della sua storia (`conferme`). Esempi: la pensionata non è cieca, quindi dice no alle due indennità per i ciechi; lo studente residente a Palermo non ha in affitto la sua abitazione principale, quindi dice no alla detrazione per gli inquilini. Dove la storia non dice niente (bonus psicologo, nido) la verifica resta aperta.
  - Il lavoratore autonomo, con un solo possibile, è sostituito da un giovane dipendente in affitto a Milano.
  - C'è un'impresa: un negozio di abbigliamento a Bergamo, microimpresa, ATECO 47.71.10 (`ramo: imprese`).

  Risultato alla data del 22/11, compatibili e possibili: studente fuorisede 1 e 3, famiglia monoreddito 6 e 9, giovane in affitto 2 e 3, pensionata 3 e 6, negozio 30 e 10. Provati nella pagina con Chrome, senza errori in console. Test: risposte valide, nessuna domanda aperta, conferme che puntano a requisiti esistenti, almeno un "ti spetta" per profilo.
- **Mamma sola e confronto dei profili** (richiesta di Lorenzo: mostrare casi diversi nella presentazione).
  - *Profilo "Mamma sola":* 32 anni, separata, due figli di 6 e 1 anno, dipendente part-time, in affitto, ISEE 9.000 €. Provato in 7 città con le stesse risposte: Milano dà più aiuti (13 possibili e 10 verifiche, contro 10 e 7 altrove).
  - *Risposte alle verifiche, vere per la storia:*
    - no ad "Accanto", che è per il genitore che non vive più con i figli;
    - no ai centri estivi, perché non è dipendente pubblica;
    - no al Buono Scuola, perché la scuola statale non chiede rette;
    - no al voucher "Lombardia per le donne", perché lavora da più di 180 giorni;
    - sì a Carta, detrazione per l'affitto, bonus luce e gas e congedo parentale.

    Il bonus nido resta aperto apposta, per rispondere dal vivo nella presentazione. Risultato: 5 compatibili e 6 possibili, che diventano 6 compatibili con il sì al nido.
  - *Confronto* (`confronto_profili` in `web/domande.py`, `/api/confronto`, sezione "Stesse domande, storie diverse" della pagina iniziale): una carta per profilo con compatibili, possibili, i primi nomi e un pulsante che apre il profilo. Si conta come nella pagina. Il calcolo costa circa 5 secondi, quindi si fa all'avvio del server, in un thread. Provato in Chrome su computer e telefono, senza scorrimento orizzontale né errori. Test: `test_confronto_dei_profili`.
  - `docs/presentazione.md` è riscritto intorno al confronto: studente dal vivo, mamma sola con la verifica del nido, impresa. Fra i report di riserva c'è anche quello della mamma sola.
- **Grafico dei percorsi** (richieste di Lorenzo: "i candidati con delle faccine si muovono insieme e a ogni step prendono direzioni diverse fino a riscuotere bandi diversi", poi "un centinaio di rami, più focus sulle separazioni").
  - *Forma:* è un diagramma alluvionale. Ogni linea è una persona, e ci sono sei colonne di "porte", una per domanda chiave:
    - Dove: le cinque aree;
    - Età: quattro fasce;
    - Lavoro: studia, dipendente, autonomo, senza lavoro, pensione;
    - Famiglia: da solo, in coppia, con figli, genitore solo;
    - Casa: affitto o proprietà;
    - ISEE: quattro fasce.

    All'arrivo le persone si raggruppano per aiuti in vista: 0-2, 3-5, 6-9, 10 o più. Le porte sono alte quanto le persone che ci passano. Ogni linea entra nella porta della sua risposta: dentro una porta le persone restano nell'ordine in cui arrivano, ma fra una colonna e l'altra i fasci si separano e si incrociano.
  - *La folla:* 95 persone simulate (`prove/simulazione/folla.py`, seme fisso). Sono inventate, con proporzioni plausibili ma approssimate: regioni pesate per abitanti; lavoro secondo l'età; famiglia, casa e ISEE coerenti con età e lavoro. Per ognuna il motore calcola gli aiuti in vista alla data del 22/11 (`web/folla_demo.json`, circa 3 secondi). Hanno 84 percorsi diversi e da 0 a 13 aiuti in vista. Non è un campione della popolazione, e la pagina lo dice.
  - *I 5 profili d'esempio delle persone:* hanno linea spessa, faccina, contatore degli aiuti in vista dopo ogni colonna (con i soli campi rivelati fin lì) e, all'arrivo, un'etichetta con gli stessi numeri del confronto. Il negozio non c'è, perché le domande delle imprese sono altre; resta fra le carte.
  - *Animazione* (`web/static/js/percorsi.js`, SVG senza librerie): la folla parte compatta da un punto. Colonna per colonna, i puntini scorrono lungo le linee con un leggero sfasamento, le linee si disegnano e le porte si aprono con il loro numero. All'arrivo i profili d'esempio escono verso le loro etichette, con i coriandoli. Le intestazioni sono numerate, con la domanda, e una banda segue il passo in corso. Il colore è l'area geografica, così si vede la folla mescolarsi.
  - *Interazione:* passando sopra una porta si accendono solo le persone che ci passano; sopra una faccina, la sua strada. Un clic sull'etichetta apre il percorso guidato. Con "riduci movimento" si mostra subito la fine.
  - *Prova in Chrome:* 665 tratti, 28 porte, i 5 arrivi, l'evidenziazione di una porta e di una faccina, il clic, il telefono (il grafico scorre dentro la sua scheda), nessun errore. Test: `test_percorsi_dei_profili`.
  - *Scartato:*
    - un albero con i soli profili d'esempio (prima versione): con sei persone i rami sono per forza pochi;
    - calcolare la folla a ogni avvio del server: con un file a data fissa il grafico è uguale in ogni presentazione;
    - colori per esito: con l'area si vedono meglio le separazioni.
- **Percorso guidato dei profili** (richiesta di Lorenzo: "che mostri ogni passo, non solo la fine"). Prima un clic su un profilo riempiva tutto e mostrava subito la pagina finale.
  - *Come funziona:* ora la pagina riparte da un profilo vuoto e ripercorre il questionario una domanda alla volta. Mostra la domanda vera con la risposta del profilo già scelta, scritta anche in parole in una barra ("Percorso guidato · Mamma sola · Domanda 6 · Risposta: 3 persone (età 32, 6, 1)").
  - *I passi:* ogni risposta passa da `rispondi`, come quelle di una persona, quindi risultati, avanzamento e "Le tue risposte" si aggiornano a ogni passo. Dopo l'ultima domanda un passo mostra le risposte del profilo alle verifiche finali. Poi si applica il profilo completo, e la pagina finale coincide con la carta del confronto.
  - *Comandi:* il ritmo è di 2,6 secondi a passo, con Pausa/Riprendi, Avanti e "Vai alla fine". Se chi guarda risponde da sé la guida si mette in pausa, "Indietro" la spegne, "Rispondi tu" ricomincia da zero.
  - *Dove sta:* la risposta da dare e il suo testo sono in `web/static/js/guida.js`. Una risposta che il profilo non ha vale "Non lo so", come in `prove/simulazione/rigioca.py`.
  - *Prova in Chrome:* la mamma sola fa 21 domande più le verifiche, in circa un minuto, e arriva a 5 compatibili. Il negozio resta fermo in pausa e "Vai alla fine" porta ai 30 compatibili. Nessun errore in console.
  - *Scartato:* animare solo la pagina finale; saltare le domande con risposta "Non lo so" (mostrerebbe un percorso diverso da quello di una persona).
- **Simulazione e lista di revisione** (`prove/simulazione/`). I "possibili" si contano come nella pagina, cioè fuori dai gruppi a parte (altre zone, date da verificare, futuri). Prima si contavano per regione, e due bandi con le date da verificare (Milano affitto giovani, IRFIS sovraindebitati) contavano anche se la pagina non li mostra. Le conferme dei profili si sommano a quelle simulate. `docs/simulazione-2026-11-22.md` e `docs/da-rivedere-a-mano.md` sono rigenerati.
- **README.** Il README del 21/11 era un elenco di cautele tecniche: utili, ma non dicevano cosa fa il progetto e a che punto è. Torna una panoramica (cosa fa, a che punto siamo, come si usa, misure, limiti), con i numeri del 22/11. Il testo di prima è in `docs/dettagli-tecnici.md`, senza modifiche.
- **Tessere degli esiti.** "Requisito non soddisfatto" (quasi idoneo) e "Requisiti non soddisfatti" (non idoneo) stavano una accanto all'altra e si confondevano. Ora sono "Manca un solo requisito" e "Non compatibili". Non dicono "quasi", come voleva la decisione 86.
- **Prove per la presentazione.** Lo studente dal vivo di `docs/presentazione.md`, rigiocato con l'API: 14 domande, niente su figli o maternità; fra i possibili bonus psicologo e detrazioni per l'affitto. I report stampati di due profili sono in `docs/riserva-presentazione/`. La build Docker è provata in locale (Docker 29.9.3): l'immagine si costruisce in circa un minuto, genera le 756 regole delle imprese e, con `TROVA_BANDI_GIORNO=2026-11-22`, dà gli stessi numeri della demo locale (340 regole per le persone, 839 per le imprese). Grafico, profili e percorso guidato funzionano anche in Chrome. Render costruisce per linux/amd64: le dipendenze sono solo Python, quindi non dovrebbe cambiare niente, ma la prima build su Render è la verifica vera.
- **Napoli, morosi incolpevoli: regola rifatta sull'avviso in PDF** (dalla revisione a mano, regola 23 "sbagliata"). La pagina del Comune rimandava all'avviso, che il raccoglitore non poteva scaricare (robots.txt). Lorenzo l'ha salvato a mano (`data/fonti/manuali.yaml`, `napoli-morosi-incolpevoli-2026-avviso`, decisione 49); l'estrazione alla cieca, con il documento intero, è stata accettata al primo tentativo.
  - *La regola:* 11 requisiti. Controllati: residenza a Napoli, ISEE fino a 26.000 (in alternativa all'ISE fino a 35.000, non modellabile), affitto con contratto registrato, cittadinanza o titolo di soggiorno, nessun'altra casa. Restano da verificare: morosità incolpevole e sue cause, sfratto con citazione per la convalida, alloggio non ERP e non A/1, A/8, A/9, un anno di residenza nell'alloggio.
  - *Il link* nella demo ora porta al PDF dell'avviso, non alla notizia. La regola di prima (`napoli-morosi-incolpevoli-2026`) è sostituita.
  - *Effetto:* con un contratto non registrato l'esito è "non ti spetta", prima era "possibile". Alla famiglia monoreddito di Napoli resta fra i possibili ma esce dalle verifiche finali (da 4 a 3), perché ha più di due condizioni aperte. La folla simulata non cambia.
- **Seconda passata di Lorenzo sulle etichette** (convenzioni C ed F della decisione 67, F confermata da Lorenzo con questa passata). Sei correzioni in 4 file, ognuna scritta nelle `note`:
  - *C, `portata: rara`:* congedo parentale (domestici o a domicilio) e Bonus mamme (lavoratrici domestiche; madri con tre o più figli a tempo indeterminato con esonero IVS);
  - *F, dai requisiti alle note:* ISCRO (Assegno di inclusione; NASpI, DIS-COLL, ALAS, discontinuità, cariche elettive) e SFL (RdC, PdC e altri sostegni alla disoccupazione).

  Sulle madri con tre o più figli si era valutata un'alternativa più precisa, che controllava numero di figli e lavoro dipendente; Lorenzo ha scelto di restare sulla convenzione.
  - **Effetto sulla misura** (`docs/test-estrazione.md`): estrazione contro Lorenzo dal **75% al 69%**. Falsi sì (10%) e falsi no (6%) non cambiano; sale "più cauta" (dallo 0% al 6%), soprattutto nel congedo parentale (dal 57% al 9%). Le etichette ora dicono "idoneo, salvo eccezioni" dove l'estrazione, fatta alla cieca prima delle convenzioni, dice "da verificare". Nel report vanno le due misure, prima e dopo, con questa spiegazione.
  - Le misure con le etichette di Edoardo (`docs/test-estrazione-edo.md`, `docs/accordo-etichette.md`) si rifanno dopo la sua passata.
  - Effetto sulla demo: all'operaia di Bari (dipendente) il congedo parentale ora risulta "idoneo, salvo eccezioni" (`docs/simulazione-2026-11-22.md`).
- **Scartato:**
  - un gruppo "In altri comuni" separato da "In altre regioni": un'altra sezione chiusa, per lo stesso significato;
  - rispondere sì a tutte le verifiche dei profili: darebbe alla pensionata l'indennità per i ciechi;
  - correggere a mano le 7 regole con `inattivo`: le regole estratte si cambiano rifacendole.

**105. La demo si chiama MiSpetta e ha una versione in inglese; la colonna delle domande scorre da sola** (24/11, Lorenzo; tocca `web/lingua.py`, `web/server.py`, `web/domande.py`, `data/traduzioni_en.yaml`, `web/static/`, `tests/test_web.py`)
- **Il nome.** "trova-bandi" descrive il codice, non quello che chiede chi usa la demo ("cosa mi spetta?"). Il nuovo nome compare solo dove si vede: titolo e marchio della pagina, report stampato, calendario delle scadenze, README, bozza del report, percorso della presentazione. Repository, pacchetti, comandi e la variabile `TROVA_BANDI_GIORNO` restano come sono: rinominarli a tre giorni dalla consegna rischierebbe di rompere Docker, Render e i comandi già scritti nei documenti.
- **Inglese, completo.** Il pulsante IT/EN in alto (oppure `?lang=en`) traduce interfaccia, domande e aiuti, opzioni, requisiti, "La tua risposta", esiti, verifiche finali, profili d'esempio, confronto e grafico dei percorsi. Il browser ricorda la lingua; cambiarla a metà questionario ricarica la pagina, quindi prima chiede conferma.
- **Cosa resta in italiano, e la pagina lo dice.** Titoli dei bandi, enti, citazioni, note e testi scritti nelle regole (le condizioni "da verificare a mano"). Sono le fonti: tradurle significherebbe mostrare una frase che il bando non contiene, mentre la citazione letterale è la prova dell'esito (decisione 20). Sotto "Your results" e nel piè di pagina una riga lo spiega.
- **Come funziona.**
  - *Server:* ogni richiesta porta la lingua; `web/lingua.py` la tiene in una variabile di contesto. I testi fissi (domande, aiuti, etichette, avvertenze, profili, colonne del grafico: 497 voci) si traducono alla fine, per corrispondenza esatta, con `data/traduzioni_en.yaml`. Le frasi composte (requisiti, risposte, riepilogo, numeri) nascono già in inglese in `web/domande.py`.
  - *Codici e fonti intoccabili:* esiti, campi, valori, link, titoli ed enti non si traducono mai, anche quando coincidono con una voce del dizionario (un bando intitolato "Ristorazione" restava "Food service": trovato dai test).
  - *Pagina:* `web/static/js/i18n.js` ha `t(italiano, inglese)` per i testi dei moduli; quelli di `index.html` hanno l'attributo `data-en`.
- **Prova.** Due test nuovi: la stessa richiesta in italiano e in inglese dà gli stessi esiti, titoli e citazioni, e la lingua non resta appesa fra una richiesta e l'altra; il dizionario conserva i segnaposto (`{anno}`). In Chrome, in entrambe le lingue, la mamma sola arriva a 5 compatibili e 6 possibili e il ramo imprese funziona, senza errori in console.
- **Colonna delle domande che scorre da sola** (dalla simulazione a mano di Lorenzo). La colonna di sinistra resta fissa mentre si scorrono i risultati, ma quando era più alta dello schermo il fondo (il comune, "Avanti") si raggiungeva solo dopo aver scorso tutta la lista di destra. Succedeva nella pagina della residenza (circa 2.600 pixel con l'elenco delle regioni), nella pagina finale (verifiche e calendario) e nelle domande con molte opzioni. Ora la colonna ha l'altezza dello schermo e scorre per conto suo; a ogni domanda nuova riparte dall'alto. Sotto i 980 pixel di larghezza (telefono) la colonna non è fissa e non cambia niente. È l'unico elemento fisso alto della pagina: la barra in alto è bassa e le altre zone che scorrono (scelte filtrabili, grafico sul telefono) sono dentro la pagina.
  - *Prova in Chrome a 1366×768:* "Avanti" della residenza e "Ricomincia" della pagina finale si raggiungono scorrendo sopra la colonna; finita la colonna, scorre la pagina.
- **Scartato:**
  - tradurre i titoli dei bandi con un modello linguistico: non verificabile, e lo stesso bando avrebbe due nomi;
  - una libreria di traduzione: per due lingue bastano un dizionario e una funzione;
  - rinominare il repository.

**106. Cinque profili d'impresa e 20 bandi per le imprese da rivedere a mano** (24/11, Lorenzo; tocca `web/profili_demo.yaml`, `prove/simulazione/imprese.yaml`, `prove/simulazione/da_rivedere_imprese.py`, `docs/da-rivedere-a-mano-imprese.md`, `docs/revisione-a-mano-imprese-{lorenzo,edoardo}.md`, `tests/test_web.py`)
- **Profili.** Le imprese avevano un solo esempio, il negozio, contro cinque persone. Se ne aggiungono quattro, inventati ma plausibili, con regioni, settori e tipi di soggetto diversi:

  | profilo | compatibili | possibili |
  |---|---|---|
  | Startup del software (Torino; startup innovativa, giovanile) | 12 | 8 |
  | Agriturismo in Val d'Orcia (Montalcino; femminile, area interna) | 18 | 8 |
  | Officina meccanica (Mirandola; piccola impresa, cratere del sisma 2012) | 12 | 3 |
  | Pizzeria a Napoli (giovanile, ZES unica) | 4 | 0 |

  Ognuno risponde a tutto il questionario delle imprese, con soli valori del catalogo, e ha esiti diversi dagli altri: lo controlla il test dei profili, che prima guardava solo il negozio. Sono tradotti anche in inglese (decisione 105). Il grafico dei percorsi resta delle sole persone, perché le sue colonne sono domande del questionario delle persone.
- **Pagina iniziale.** Con dieci profili i chip e le carte si mescolavano, e la pizzeria restava da sola in fondo. Ora sono in due gruppi, "Persone" e "Imprese", ognuno con il suo titolo; i chip di un gruppo stanno su una riga. Sul telefono la pagina non scorre di lato.
- **Quali bandi rivedere.** Gli stessi criteri delle persone (decisione 97): i più visti, cioè quelli che risultano compatibili o possibili nella zona dell'impresa. Si usano 15 imprese di prova: 10 in `prove/simulazione/imprese.yaml` (regioni, dimensioni e settori diversi, dalla farmaceutica di Milano alla segheria di Trento) più i 5 profili. Se ne prendono 20: 10 fra le regole dell'open data di incentivi.gov.it e 10 fra quelle estratte dai bandi.
  - *Estratte:* le 10 scelte sono le sole viste da due imprese; le altre 25 sono viste una volta. Sono soprattutto lombarde, perché fra le imprese di prova due sono in Lombardia e molte regole estratte sono lombarde.
  - *Open data:* sei nazionali viste da molte imprese (Fondo di garanzia 14/15, cloud e cyber security 14/15, Fondo salvaguardia 13/15, Confidi, Voucher 3I). Fra le 27 viste due volte, a pari merito, la precedenza va a enti non ancora in lista. "Quota Lombardia" c'è in entrambe le origini e si rivede una volta sola (estratta).
- **Chi rivede cosa.** Divisione incrociata, come per le persone. Le regole estratte per le imprese le ha fatte Edoardo, e le rivede Lorenzo. Quelle dell'open data vengono dalla conversione scritta da Lorenzo (`pipeline/normalizza.py`), e le rivede Edoardo. Per l'open data la domanda principale è se il bando ha condizioni che il portale non scrive. Per esempio "Contratti di sviluppo - semiconduttori" risulta compatibile anche a una pizzeria, perché il portale filtra solo tipo di soggetto e dimensione.
- **Esiti di Lorenzo (24/11 sera), le 10 estratte:** 8 giuste, 2 con errori piccoli, nessuna sbagliata. Errori piccoli: Bando Sicurezza 2026 della Camera di Cremona-Mantova-Pavia, dove manca lo scopo del contributo (sistemi di sicurezza contro la microcriminalità); Quota Lombardia, dove manca che la quotazione preveda un aumento di capitale pari almeno al 50% dell'IPO. Le due manifestazioni di interesse senza contributo (filiere, Opportunity Lombardy) restano giuste: sono comunque bandi, e possono portare ad aiuti in futuro. Le 10 dell'open data spettano a Edoardo.
- **Scartato:** scegliere a mano i bandi da rivedere (si sceglierebbero quelli che si sa già essere giusti); 10 per origine a ciascuno, perché romperebbe la divisione incrociata.

**107. I link dell'open data al vecchio sito del Ministero (mise.gov.it) puntano a quello nuovo (mimit.gov.it)** (24/11, Edoardo con Claude; tocca `pipeline/normalizza.py`, `tests/test_normalizza.py`)
- **Il problema.** Nella revisione a mano delle imprese il link del bando dei Confidi non si apriva. Nell'export di incentivi.gov.it 45 bandi hanno ancora il link a `www.mise.gov.it`, il nome di prima del Ministero. Quel sito rimanda alla stessa pagina su `mimit.gov.it`, ma passando per un indirizzo `http://` non sicuro: i browser che accettano solo `https://` si fermano lì, e chi apre il bando dalla demo non arriva da nessuna parte.
- **La correzione, generale.** `link()` in `pipeline/normalizza.py` riscrive `mise.gov.it` e `www.mise.gov.it` in `https://www.mimit.gov.it`, con lo stesso percorso: è proprio la pagina a cui il vecchio sito rimanda. Toglie anche gli spazi ai bordi. Gli altri siti del Ministero con un nome proprio (`uibm.mise.gov.it`, `ecobonus.mise.gov.it`) funzionano ancora e non si toccano. La lista `SITI_SPOSTATI` può accogliere altri siti che cambiano nome.
- **Effetto.** Dopo `make dati` nessuna delle 756 regole dell'open data ha più un link a `mise.gov.it`, e 30 puntano a `mimit.gov.it`. I link non entrano nel calcolo degli esiti, quindi la simulazione non cambia. Provati i link nuovi delle 6 regole del Ministero fra le 10 da rivedere: si aprono tutti. Test: `test_link_del_vecchio_sito_del_ministero`.
- **Scartato:** correggere a mano solo i due link della revisione (gli altri 43 restavano rotti nella demo); cambiare l'export grezzo in `data/raw` (deve restare com'è stato scaricato); seguire i rinvii scaricando ogni pagina (troppe richieste per un problema di un solo dominio).

**108. I bandi delle Camere di commercio valgono solo per le imprese della loro provincia; per le imprese regione e comune sono quelli della sede** (24/11, Edoardo con Claude; tocca `pipeline/regole.py`, `web/domande.py`, `tests/test_regole.py`, `tests/test_web.py`, `tests/test_profili_manuali.py`)
- **Il problema, trovato nella revisione a mano delle imprese** (decisione 106). Due bandi su 10 dell'open data (19, Camera di Bergamo; 20, Camera di Brescia) avevano errori piccoli per la stessa ragione: il bando è per le imprese della provincia, ma incentivi.gov.it scrive solo la regione. Un'impresa di Bergamo risultava compatibile con i bandi delle Camere di Brescia, Varese o Milano. Le Camere di commercio sono provinciali (o di più province, se accorpate), e lo dice il nome dell'ente.
- **La correzione, generale.** Per un bando di una Camera di commercio che non ha già l'elenco dei comuni, `pipeline/regole.py` ricava le province dal nome dell'ente (`province_della_camera`): i nomi delle province ISTAT delle regioni del bando, più un piccolo elenco per le Camere accorpate che non li contengono (Maremma e Tirreno, Venezia Giulia, Gran Sasso, Irpinia Sannio, dell'Emilia, Monza). Il requisito è `comune` fra tutti i comuni di quelle province, con la fonte "campo Soggetto_Concedente". Le unioni regionali delle Camere, e le Camere che coprono tutta la regione (Marche, Basilicata), restano con la sola regione. Controllati a mano i 43 enti camerali dei bandi aperti: province giuste per tutti.
- **Come si legge nella demo.** Un elenco di comuni che coincide con province intere si scrive "uno della provincia di Bergamo", invece di "uno dei 243 elencati". Per le imprese regione e comune si chiamano "della sede" e non "di residenza", come già nelle domande.
- **Effetto.** 34 bandi aperti su 839 hanno il requisito nuovo. Alle 15 imprese di prova (decisione 106) i compatibili passano da 708 a 688: escono bandi di Camere di altre province (la farmaceutica di Milano 67 → 56). Il negozio d'esempio di Bergamo ha 25 compatibili. I due bandi della revisione ora sono giusti: nella tabella di `docs/da-rivedere-a-mano-imprese.md` resta l'esito di Edoardo, con la correzione accanto. Persone e simulazione non cambiano.
- **Test.** `test_camera_di_commercio_vale_per_la_sua_provincia`, `test_regola_della_camera_ha_i_comuni_della_provincia`, `test_comuni_di_una_provincia_intera_e_sede_per_le_imprese`. Il test differenziale sull'export grezzo (`tests/test_profili_manuali.py`) ha la stessa regola scritta in modo indipendente, che legge direttamente il CSV ISTAT.
- **Scartato:**
  - un campo nuovo "provincia della sede" nello schema e nel questionario: il comune della sede si chiede già, e la provincia si ricava;
  - correggere a mano solo i due bandi della revisione: gli altri 32 restavano sbagliati;
  - cercare la provincia nel titolo del bando: non tutti la scrivono, il nome della Camera sì.
