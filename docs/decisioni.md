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
