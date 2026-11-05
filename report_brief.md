# Report sul brief "trova-bandi personalizzato"

*27 ottobre 2026 · analisi di `brief-progetto-bandi.md`*

Questo report riassume tre cose:
- cosa è cambiato nel brief;
- cosa risulta verificando sul web le sue affermazioni;
- come si colloca l'idea rispetto ai criteri di valutazione del corso.

*Aggiornamento del 27/10 pomeriggio:* il target è deciso (imprese) e la pipeline dati della fase 0 è pronta (vedi §5).

## 1. Modifiche fatte al brief

Ho tolto dal brief tutto ciò che riguardava la scelta del target:

- **§6 "Scelta del target":** tolte le opzioni A/B/C e il compito di confrontarle. Resta solo il paragrafo sulla copertura geografica, che ora è la sezione 6.
- **§3:** la conclusione provvisoria non rimanda più al "*per chi* (sezione 6)". Gli esempi di ricerca dei concorrenti ora sono neutri: "trova bandi", "verifica requisiti bando", "simulatore agevolazioni regione".
- **§9:** tolto l'output `proposta-target.md`; la domanda finale non chiede più "con quale target".

Il resto è invariato. Alla riga 34 la parola "target" è rimasta perché indica a chi si rivolgono i concorrenti, non la nostra scelta.

## 2. Verifiche

| Tema | Cosa risulta |
|---|---|
| **Open data di incentivi.gov.it** | Esistono: CSV e JSON ufficiali con licenza **IODL 2.0** ([pagina open data](https://www.incentivi.gov.it/it/open-data)). Il catalogo ha più di 1.000 incentivi da 374 amministrazioni ([MIMIT](https://www.mimit.gov.it/it/notizie-stampa/portale-incentivi-gov-it-oltre-1000-gli-incentivi-pubblicati-e-374-le-amministrazioni-coinvolte)). Non servono scraper di terzi. *Aggiornato:* il pulsante "Esporta" interroga un indice Solr pubblico del portale. La stessa richiesta, fatta da script, restituisce tutti i 6.007 incentivi in pochi secondi (`pipeline/scarica.py`, al massimo una volta al giorno). |
| **Campi strutturati** | Dal [tracciato ufficiale](https://www.incentivi.gov.it/sites/default/files/2024-01/Metadati_Scheda_Incentivo_1.pdf). Strutturati: regioni, comuni, dimensione d'impresa, tipo di soggetto beneficiario, codici ATECO, date di apertura e chiusura, spesa e agevolazione minima e massima, forma dell'agevolazione, costi ammessi, obiettivi. In testo libero: i requisiti, dentro "Descrizione" ("Cos'è, a chi si rivolge, cosa prevede"). **Non esistono campi** per età, ISEE o residenza delle persone fisiche. |
| **BonusX** | Cittadini. Questionario su famiglia, reddito e patrimonio, ISEE simulato, preselezione dei bonus. Informazioni gratuite, pratiche assistite in abbonamento ([PartitaIVA](https://www.partitaiva.it/bonusx/), [TuttoAndroid](https://www.tuttoandroid.net/news/2025/04/09/bonusx-bonus-statali-agevolazioni-isee-730-1088602/)). |
| **Bonoos** | Welfare aziendale: le imprese lo offrono ai dipendenti. Mappa i bonus statali, regionali e comunali per categoria di bisogno ([StartupItalia](https://startupitalia.eu/?p=472779)). |
| **PARI (PagoPA + App IO)** | Non serve a scoprire i bandi: è l'infrastruttura con cui le amministrazioni **erogano** bonus e contributi, partita con il bonus elettrodomestici ([InformazioneFiscale](https://www.informazionefiscale.it/Bonus-elettrodomestici-PARI-piattaforma-PagoPA-AppIO)). |
| **Bando Easy, Bandit** | Imprese. Bando Easy dichiara più di 2.400 bandi monitorati con abbinamento AI per profilo d'impresa; Bandit automatizza la documentazione ([StartupGeeks](https://www.startupgeeks.it/bandi-startup/), [Bandit](https://www.landing.getbandit.it/blog/bandi-startup)). Sono affermazioni dei venditori, non verificate. |
| **1jeune1solution (Francia)** | Più vicino a noi di Mes Aides: simulatore pubblico di aiuti per under 30, con questionario, lanciato nel 2021; oggi più di 700 aiuti e circa 80.000 utenti al mese ([OCSE](https://oecd-opsi.org/?p=35328), [Ministero](https://www.enseignementsup-recherche.gouv.fr/fr/1jeune1solution-lancement-du-simulateur-d-aides-destination-des-jeunes-45946)). Non ho trovato un equivalente italiano, ma la ricerca su questo punto è stata breve. |
| **OpenFisca Italia** | Piccolo e poco attivo: 8 stelle, 5 fork, licenza AGPL. Le fonti consultate (mirror, non GitHub) danno date dell'ultima attività incoerenti tra loro ([mirror](https://repos.data.code.gouv.fr/hosts/GitHub/repositories/openfisca%2Fopenfisca-italy)). Il motore è pensato per tasse e benefit, non per i requisiti dei bandi. |

## 3. Dove sta lo spazio libero

Esistono servizi con questionario (BonusX) e servizi con abbinamento AI (Bando Easy). Nessuno di quelli verificati unisce queste quattro cose:

1. **domande scelte in modo adattivo**, misurando quante domande si risparmiano rispetto a un modulo fisso;
2. **"quasi idoneo"**, cioè il minimo cambiamento che sblocca più bandi;
3. **la citazione del requisito** dietro ogni esito;
4. **regole aperte e verificabili** invece di una scatola nera.

È il "come" della sezione 5 del brief: la conclusione provvisoria regge.

## 4. Punti del brief da correggere

1. **§1, valutazione.** Le linee guida ufficiali di Poirrier ([pagina del corso](https://www.poirrier.ca/courses/softeng/), [linee guida](https://www.poirrier.ca/courses/softeng/ex/guidelines-project.pdf)) sono diverse da quanto riportato.
   - **Criteri:** *Correctness AND (Technical difficulty OR Originality OR Impact+presentation)*.
   - **Consegna:** codice, report di circa una pagina e materiale di supporto. Il report non deve spiegare il codice: deve raccontare **gli ostacoli incontrati e le idee**. Il docente scrive che un report generico, "in stile LLM", fa sembrare il lavoro a basso sforzo.
   - **Presentazione:** circa 10 minuti in aula; le slide non sono obbligatorie, va bene anche una demo live.
   - **Scadenze:** topic entro **venerdì 30 ottobre, 23:59** (provvisorio, modificabile con approvazione via email); consegna **venerdì 27 novembre, 23:59**; presentazioni **30 novembre, 2 e 4 dicembre**.
   - **Open source:** per contattare gli sviluppatori di un progetto open source serve prima l'approvazione del docente.
2. **Fase 0 troppo pesante.** Cinque documenti più 10 bandi estratti a mano non stanno nei tempi prima del topic. Per il 30 basta l'idea; la fase 0 va concentrata nella prima settimana di lavoro (30 ottobre – 6 novembre).
3. **Rendere esplicito il cuore tecnico.** Senza, il progetto rischia di sembrare una normale web app con database. Il materiale c'è già nel brief:
   - **questionario adattivo:** costruire l'albero di domande ottimo è un problema NP-difficile; la scelta greedy per guadagno di informazione ha garanzie di approssimazione note ed è facile da misurare;
   - **"quasi idoneo":** trovare il minimo insieme di cambiamenti che sblocca più bandi è un piccolo problema di ottimizzazione. Poirrier fa ricerca su questi temi;
   - **logica a tre stati** (sì / no / dato mancante), formalizzata e testata.
4. **Motore proprio invece di OpenFisca**, per i motivi del punto 2: più semplice da spiegare e da testare.
5. **Cumulabilità (§5.4) da rimandare.** Valore alto ma complessità molto alta, e riguarda soprattutto le imprese (*de minimis*).
6. **Commenti "riga per riga".** Utili per imparare, ma nel codice consegnato rischiano di far sembrare tutto generato da un LLM. Meglio commenti normali, con le spiegazioni dettagliate in `docs/decisioni.md`.

## 5. Target: imprese (deciso il 27/10)

Pipeline, risultati e problemi trovati sono nel `README.md` e in `docs/`: `fattibilita-dati.md`, `misura-questionario.md`, `decisioni.md`. Restano qui sotto i fatti che hanno portato alla scelta:

- **Dati strutturati:** esistono solo per gli incentivi alle **imprese** (incentivi.gov.it). Per i bandi rivolti alle **persone** i requisiti vanno estratti da testi e PDF, a mano o con un LLM. In quel caso il test di estrazione (task 4.3) diventa la misura chiave del progetto.
- **Concorrenti:** ce ne sono su entrambi i fronti: BonusX e Bonoos per i cittadini, Bando Easy e Bandit per le imprese.
- **Originalità:** in ogni caso sta nel "come" (sezione 3 di questo report), non nel pubblico scelto.

## 6. Valutazione rispetto ai criteri del corso

| Criterio | Giudizio | Perché |
|---|---|---|
| Correttezza | forte | Motore deterministico, citazione del requisito per ogni esito, test con profili fittizi di cui si conosce la risposta |
| Difficoltà tecnica | media; alta con il punto 4.3 | Questionario adattivo e "quasi idoneo" trattati come problemi di ottimizzazione, estrazione LLM misurata |
| Originalità | media | Il "trova bandi" in sé non è originale; la combinazione della sezione 3 sì |
| Impatto e presentazione | buono | Demo naturale: "rispondi a 6 domande e scopri quali bandi ti spettano e perché" |

## 7. Prossimi passi

1. **Entro il 30 ottobre:** inviare il topic. La bozza è in `proposta_topic.md`.
2. **Prima settimana:** test di estrazione su 10 bandi, prima a mano e poi con un LLM. I dati scaricati, le regole sui campi strutturati e la misura del questionario sono già pronti (`make`).
3. **Correggere il §1 del brief** con i criteri e le scadenze reali.
