# Brief di progetto: trova-bandi personalizzato

> Documento di avvio pensato per essere letto da un agente AI (es. Claude Code) che aiuta il team nella **fase 0: raccolta dati e verifica di fattibilità e originalità**. Leggilo tutto prima di iniziare.
>
> **Aggiornato il 5/11/2026.** Lo stato del lavoro è nel `README.md`, le scelte fatte in `docs/decisioni.md`.

## 1. Contesto

- **Chi siamo**: Lorenzo Faella ed Edoardo Salvatore Russo, MSc in Artificial Intelligence (Bocconi). Progetto del corso 20875 Software Engineering (prof. Laurent Poirrier).
- **Topic approvato** (consegnato il 29/10/2026, 2/2; si può cambiare solo con l'approvazione del docente via email): *An eligibility engine for Italian public incentives, for both individuals and businesses: it automatically collects grants and benefits from national, regional and municipal sources across Italy and extracts their requirements into verifiable rules, and an adaptive questionnaire tells each user which ones they qualify for, citing the requirement behind every answer.*
- **Come viene valutato** ([slide 15 dell'introduzione](https://www.poirrier.ca/courses/softeng/slides/p00_intro.pdf)): *Correctness, and (Technical difficulty, or Originality, or Impact and presentation)*.
- **Cosa consegnare** ([linee guida](https://www.poirrier.ca/courses/softeng/ex/guidelines-project.pdf)), su Blackboard: codice, un report di circa una pagina e l'eventuale materiale di supporto. Il report non spiega il codice: racconta soprattutto **gli ostacoli incontrati e le idee**. Un report generico fa sembrare il lavoro a basso sforzo.
- **Scadenze**: consegna **venerdì 27 novembre, 23:59**; presentazioni di circa 10 minuti il **30 novembre, 2 e 4 dicembre** (slide facoltative, va bene una demo live).
- **Uso dell'AI**: è permesso usare agenti AI per programmare e raccogliere dati, **a patto che capiamo cosa facciamo**. Regole per l'agente:
  - Spiega ogni scelta tecnica in italiano semplice, con il *perché*.
  - Commenta il codice dove serve a capire il perché; le spiegazioni lunghe vanno in `docs/decisioni.md`.
  - Annota ogni decisione importante in `docs/decisioni.md` (data, decisione, alternative scartate, motivo). Ci serve per l'orale.
  - Non prendere decisioni irreversibili (stack, dominio, scope) senza chiedercelo.

## 2. L'idea in una frase

Un utente inserisce pochi dati su di sé (chi è, dove vive, che situazione ha) e scopre **quali bandi e agevolazioni regionali e nazionali sono aperti per lui**, con il motivo per cui è idoneo, cosa gli manca e le scadenze.

## 3. Cosa esiste già (ricerca preliminare, da verificare e approfondire)

| Soluzione | Cosa fa | Limite / spazio per noi |
|---|---|---|
| **incentivi.gov.it** (MIMIT) | Catalogo pubblico centrale di incentivi nazionali, regionali e delle Camere di Commercio, con motore di ricerca a filtri e calendario. | Filtri per categoria, non un giudizio di idoneità sul singolo profilo; orientato alle imprese. |
| **Scraper/API di terzi su incentivi.gov.it** (es. attori Apify) | Esportano il catalogo in dati strutturati: scadenze, importi, regioni, dimensione d'impresa, settori. I dati risultano pubblicati con licenza IODL 2.0. | Dimostra che **la fonte dati esiste ed è strutturabile**. Non fanno matching personalizzato. |
| **BonusX** (startup) | Questionario su ISEE e nucleo familiare per i **bonus dei cittadini**, più assistenza nella pratica. Non gestisce bandi per le aziende. | Focalizzato su bonus nazionali per famiglie; modello a servizio umano. |
| **Bonoos**, **PARI (PagoPA + App IO)** | Bonoos: welfare aziendale. PARI: infrastruttura per erogare bonus, non per scoprirli. | Dettagli in `docs/competitor.md`. |
| **OpenFisca** + **Mes Aides** (Francia) | Motore open source "rules as code" in Python; Mes Aides è il simulatore di idoneità francese costruito sopra, da un team di circa 2 persone. Esiste un pacchetto OpenFisca per l'Italia. | Precedente autorevole per l'architettura "regole come codice". Il pacchetto italiano è piccolo e poco attivo. |

**Conclusione provvisoria**: un generico "trova bandi" **non è originale**. L'originalità va cercata nel *come* (sezione 5).

### Task 3.1 per l'agente: analisi competitor
*Prima versione in `docs/competitor.md`.*

Per ognuno dei servizi sopra, più almeno altri 3 trovati cercando (es. "trova bandi", "verifica requisiti bando", "simulatore agevolazioni regione"):
- target, fonti dati, come decide l'idoneità (filtri / questionario / umano / AI), se spiega il motivo, se è gratuito.
- Output: tabella in `docs/competitor.md`, con link. Segnala esplicitamente se trovi qualcuno che fa già **una delle idee della sezione 5**.

## 4. Fonti dati (fase 0, la più critica)

### Task 4.1: verificare la fonte principale
*Fatto: `pipeline/scarica.py` scarica l'intero export ufficiale, le statistiche sono in `docs/fattibilita-dati.md`.*

- Capire se **incentivi.gov.it** offre un **export open data ufficiale** (CSV/JSON/API) e con che licenza. Preferire sempre la fonte ufficiale agli scraper di terzi.
- Elencare i **campi disponibili** e quanti sono strutturati vs solo testo libero (es. regione è un campo? i requisiti sono solo nella descrizione?).
- Scaricare un campione (es. 50 incentivi aperti) in `data/raw/` e produrre statistiche in `docs/fattibilita-dati.md`: quanti nazionali vs regionali, per quali beneficiari (imprese, persone, enti), quanti hanno requisiti leggibili.

### Task 4.2: fonti secondarie
*In corso. Fatto: 449 schede INPS (`pipeline/fonti/inps.py`). Da fare: fonti regionali e comunali. L'export di incentivi.gov.it non basta per le persone: `docs/decisioni.md`, punto 16.*

- Portali regionali dei bandi (almeno Lombardia, Emilia-Romagna, Sicilia).
- Bonus per persone fisiche (INPS, Agenzia delle Entrate).
- Bandi per giovani (es. Dipartimento politiche giovanili), Erasmus/borse, servizio civile.
- Per ognuna: formato, frequenza di aggiornamento, licenza, facilità di estrazione.

### Task 4.3: test di estrazione dei requisiti
*In corso, ora su 15 benefici: `docs/etichettatura.md`.*

Prendere **10 bandi reali** e provare a trasformare i requisiti in formato strutturato (sezione 7):
1. a mano (lo facciamo noi, serve come "verità");
2. con un LLM;
3. confrontare: quanti requisiti l'LLM coglie correttamente, quanti sbaglia, quanti inventa.

Questo numero è la **misura di fattibilità** del progetto. Risultato in `docs/test-estrazione.md`.

## 5. Idee per renderlo originale

Da valutare: non vanno fatte tutte. L'agente deve indicare per ognuna **originalità** (esiste già?) e **costo** (basso / medio / alto).

1. **Questionario adattivo ("decision tree intelligente")**
   Invece di un modulo con 30 domande, il sistema sceglie ogni volta **la domanda che esclude o conferma più bandi** (guadagno di informazione, come negli alberi decisionali del machine learning ma calcolato sui requisiti). L'utente risponde a 5-8 domande invece che a 30. È il cuore algoritmico ed è facile da misurare: numero medio di domande per arrivare al risultato rispetto a un modulo fisso.
   *Misurato finora solo sui 7 campi strutturati: non batte un buon ordine fisso (`docs/misura-questionario.md`). Va rimisurato con i requisiti estratti dal testo.*

2. **"Quasi idoneo": cosa ti manca**
   Oltre ai bandi per cui sei idoneo, mostra quelli per cui ti manca **un solo requisito** e cosa cambierebbe ("se apri la partita IVA si aprono 4 bandi", "questo bando apre a gennaio"). Pochi servizi lo fanno ed è molto utile.

3. **Spiegazione e citazione per ogni esito**
   Ogni "sì" o "no" mostra il requisito che l'ha determinato e il link al passaggio del bando. Riduce il rischio di errori e rende il sistema verificabile.

4. **Cumulabilità tra bandi**
   Segnalare quando due agevolazioni non si possono sommare (es. limiti tipo *de minimis* per le imprese). Da verificare quanto sia fattibile: valore alto, rischio di complessità alto.

5. **Avvisi sui nuovi bandi**
   L'utente salva il profilo (o solo un codice anonimo) e riceve una notifica quando esce un bando compatibile. Tecnicamente semplice, buon valore d'uso.

6. **Profilo senza dati personali**
   Il profilo resta nel browser o viene salvato in forma anonima. Utile come scelta di design e di privacy da raccontare.

7. **Valutazione del sistema con casi di test**
   Un insieme di **profili utente fittizi** con la risposta corretta scritta da noi, eseguito a ogni modifica come test automatico. È poco "originale" ma è esattamente ciò che un corso di software engineering premia.

## 6. Copertura geografica

Il motore deve essere valido per tutta Italia, ma per il progetto basta dimostrarlo su **tutti i bandi nazionali + 2-3 Regioni**. L'estensione alle altre Regioni è una questione di dati, non di codice. Il topic approvato cita anche le fonti comunali: il sottoinsieme esatto è ancora da decidere.

## 7. Architettura proposta (ipotesi, non decisa)

Principio: **separare la logica dai dati**. Il motore si scrive una volta; ogni bando è un file di dati.

```
fonti (incentivi.gov.it, portali regionali)
   -> acquisizione (script / scraper)
   -> estrazione requisiti (LLM, poi revisione umana)
   -> file regole del bando (JSON/YAML, validati da uno schema)
   -> motore di valutazione (deterministico, testato)
   -> questionario adattivo + interfaccia web
```

Bozza del formato regole. Il formato attuale è in `schema/regola.schema.json`, con esempi in `data/regole_persone/` e campi in `docs/vocabolario-persone.md`.

```yaml
id: lombardia-2026-esempio
titolo: "Nome del bando"
ente: "Regione Lombardia"
link: "https://..."
apertura: 2026-11-01
chiusura: 2027-01-31
ultimo_controllo: 2026-10-27   # quando un umano ha verificato il file
requisiti:
  - campo: eta
    operatore: tra
    valore: [18, 35]
    fonte: "Art. 3, comma 1"
  - campo: regione_residenza
    operatore: uguale
    valore: Lombardia
    fonte: "Art. 3, comma 2"
  - campo: isee
    operatore: minore_uguale
    valore: 30000
    fonte: "Art. 4"
```

- Il "decision tree" non si scrive a mano per ogni bando: si **genera** dai requisiti di tutti i bandi.
- Il motore restituisce per ogni bando: idoneo / non idoneo / quasi idoneo / mancano dati, con il requisito responsabile.
- Motore piccolo nostro invece di **OpenFisca**: la scelta è motivata in `docs/decisioni.md`.

Stack indicativo: Python, FastAPI o Django, PostgreSQL o SQLite, frontend semplice. Da confermare.

## 8. Rischi da valutare

- **Dati**: i requisiti sono spesso solo in testo libero o in PDF allegati. Se l'estrazione (task 4.3) funziona male, ridurre il numero di bandi e curarli a mano.
- **Aggiornamento**: i bandi aprono e chiudono di continuo. Servono data di ultimo controllo e scadenza su ogni file.
- **Errori di idoneità**: un esito sbagliato dato con sicurezza è il danno peggiore. Mitigazioni: citazione obbligatoria, stato "non sono sicuro", disclaimer con link alla fonte ufficiale.
- **Privacy**: dati come ISEE o reddito sono sensibili. Preferire profili non salvati o anonimi.
- **Licenze**: usare solo dati con licenza aperta e citare la fonte.
- **Scope**: il rischio maggiore per un team di 2 è voler coprire troppo.

## 9. Output attesi dalla fase 0

Nella cartella `docs/`:
1. `competitor.md`: tabella dei competitor e cosa manca sul mercato. *Prima versione fatta.*
2. `fattibilita-dati.md`: fonti, campi, licenze, statistiche del campione. *Fatto per incentivi.gov.it.*
3. `test-estrazione.md`: risultati sui 10 bandi (precisione dell'LLM rispetto a noi). *Da fare.*
4. `idee-originalita.md`: le idee della sezione 5 con originalità e costo, più eventuali idee nuove. *Da fare.*
5. `decisioni.md`: registro delle decisioni prese. *Aggiornato man mano.*

Chiudi con un **riepilogo di una pagina**: il progetto è fattibile in 2? Con quali fonti e quali 2-3 idee distintive? Cosa resta incerto?

## 10. Cosa NON fare in questa fase

- Non scrivere l'applicazione: prima i dati e la fattibilità.
- Non scaricare dati da siti che non lo permettono, né aggirare blocchi.
- Non promettere copertura di tutta Italia: dimostrare il metodo su un sottoinsieme.
