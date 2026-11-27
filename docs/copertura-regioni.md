# Copertura regione per regione: Lombardia e Sicilia

*Generato da `pipeline/copertura.py` (`python -m pipeline.copertura`): non modificare a mano. Metodo e scelte nella decisione 54 di `docs/decisioni.md`.*

**Domanda:** dei bandi aperti per privati (persone, imprese, Terzo settore) di una regione, quanti ne troviamo? Ogni quota ha il suo intervallo di Wilson al 95%: con poche decine di bandi l'incertezza è grande.

## Riepilogo per il report

| regione | riferimento | fonti misurate | bandi di riferimento | trovati | copertura (IC 95%) | metodo |
|---|---|---|---|---|---|---|
| Lombardia | elenco ufficiale (dataset regionale) | incentivi.gov.it | 109 | 27 | 27/109 = **25%** (18%–34%) | confronto con l'elenco |
| Lombardia | elenco ufficiale (dataset regionale) | portale + nostre raccolte | 109 | 106 | 106/109 = **97%** (92%–99%) | confronto con l'elenco ⚠ |
| Sicilia | nessun elenco: totale stimato 122 (72–281) | incentivi.gov.it | ≈122 | 7 | **6%** (2%–10%) | cattura e ricattura ⚠ |
| Sicilia | nessun elenco: totale stimato 122 (72–281) | portale + nostre raccolte | ≈122 | 50 | **41%** (18%–69%) | cattura e ricattura ⚠ |

Date: portale 2026-10-27, nostre raccolte 2026-11-07, dataset lombardo aggiornato al 2026-10-01. Contano i bandi aperti in tutte e due le date.

Come leggerla:
- **incentivi.gov.it da solo non basta nemmeno in Lombardia**, una delle regioni che lo alimentano di più: ha circa 25% dei bandi regionali per privati. In Sicilia ne ha ancora meno, e anche l'estremo alto dell'intervallo resta basso.
- ⚠ La seconda riga lombarda è **alta per costruzione**: la nostra raccolta lombarda legge Bandi e Servizi, lo stesso sistema da cui nasce il dataset. Dice che il raccoglitore funziona, non che abbiamo scovato bandi nascosti. Il dato utile è quanti bandi le nostre raccolte aggiungono al portale: da 27 a 106 su 109.
- ⚠ La stima siciliana regge solo se le due fonti fossero indipendenti, e non lo sono (sezione Sicilia). Con 2 bandi in comune è un ordine di grandezza, non una misura.

## Date

- incentivi.gov.it: export del **2026-10-27**. Nostre raccolte: **2026-11-07**. Dataset lombardo: scaricato il 2026-11-08, ma con le righe aggiornate al **2026-10-01** (campo `rowsUpdatedAt`).
- Per non contare come "mancanti" i bandi chiusi o aperti tra le due date, si tengono solo i bandi **aperti sia il 2026-10-27 sia il 2026-11-07**, secondo le date dell'elenco di riferimento (per il portale siciliano, le date del portale). Il sito siciliano non dà date: lì vale il filtro "non scaduti" del sito.
- Il dataset lombardo è fermo al 2026-10-01: i bandi pubblicati dopo non ci sono, e le proroghe arrivate dopo non si vedono. Il denominatore lombardo è quindi "i bandi già pubblicati a inizio ottobre e ancora aperti".

## Lombardia

**Elenco di riferimento:** "Anagrafica dei bandi regionali" (dati.lombardia.it, `bukx-h2uy`, licenza Creative Commons Attribution 4.0 International, attribuzione: Regione Lombardia), 1934 righe dal 2016. Aperte in tutte e due le date: **201**. Il filtro di rilevanza ne toglie 92 (solo enti pubblici 49, non è un bando 22, gara o fornitura 12, personale o concorso 9): restano **109 bandi per privati**.

**Fonti misurate:** 95 schede di incentivi.gov.it aperte il 2026-10-27 con la sola Lombardia come regione (di ogni ente); 460 voci delle nostre raccolte del 2026-11-07 (Bandi e Servizi 428, Finlombarda 32). Le Camere di commercio non entrano: i loro bandi non sono nel dataset della Regione.

| misura | copertura (IC 95%) |
|---|---|
| **incentivi.gov.it**, schede aperte il 2026-10-27 | 27/109 = **25%** (18%–34%) |
| … solo abbinamenti automatici (zona grigia tutta esclusa) | 20/109 = **18%** (12%–27%) |
| … zona grigia tutta accettata (limite alto) | 31/109 = **28%** (21%–38%) |
| … contando anche le schede che il portale dà per chiuse o future | 32/109 = **29%** (22%–38%) |
| … solo bandi con una data di chiusura | 14/65 = **22%** (13%–33%) |
| … senza le 42 voci provinciali del collocamento mirato (PR_*) | 17/67 = **25%** (16%–37%) |
| … solo le 42 voci provinciali (PR_*) | 10/42 = **24%** (13%–39%) |
| **nostre raccolte** da sole (Bandi e Servizi + Finlombarda) | 104/109 = **95%** (90%–98%) |
| **portale + nostre raccolte** | 106/109 = **97%** (92%–99%) |
| … solo bandi con una data di chiusura | 64/65 = **98%** (92%–100%) |

- Abbinamenti con il portale: 9 per codice del bando nell'indirizzo, gli altri per titolo.
- Le 42 voci "PR_*" sono la stessa misura (Dote Impresa e Dote Unica Lavoro per il collocamento mirato, servizi integrativi) ripetuta per ogni Provincia. Il dataset le conta una per una e così facciamo noi; pesano molto, per questo le due righe separate.
- Le voci senza data di chiusura (44 su 109) sono aperte per il dataset, ma alcune sembrano misure mai chiuse nel sistema (aperte nel 2019-2020). La riga "solo bandi con una data di chiusura" è la più sicura.
- Mancano anche alla nostra raccolta 5 voci: sono aperte per il dataset ma non per il sito, o il raccoglitore le scarta (concorsi, gare). Il dataset fermo al 2026-10-01 spiega una parte della differenza.

**Al contrario** (le nostre voci del 2026-11-07 contro il dataset): delle 295 voci rilevanti raccolte da Bandi e Servizi, nel dataset, aperti 104; nel dataset, ma chiusi o non ancora aperti per il dataset 20; non nel dataset 171. Delle voci assenti, 10 hanno un codice più recente dell'ultimo del dataset (pubblicate dopo l'aggiornamento); le altre sono soprattutto servizi sempre aperti (anagrafi, albi, procedimenti) che il filtro sul titolo non riconosce. Le voci "chiuse per il dataset" ma aperte sul sito sono probabilmente proroghe arrivate dopo il 2026-10-01.

## Sicilia

Non c'è un elenco ufficiale scaricabile. Si stima il totale con la **cattura e ricattura** (il metodo per contare i pesci di un lago): due fonti, A e B; se B ritrova una parte p dei bandi di A, si suppone che anche A abbia una parte p di tutti i bandi esistenti.

- **Popolazione:** bandi aperti per privati della Regione Siciliana o di IRFIS, la sua finanziaria.
- **A, siti della Regione** (2026-11-07): 165 voci (pagina "Bandi" filtrata su "non scaduti" e "Avvisi pubblici", più IRFIS). Il filtro di rilevanza ne toglie 117 (non è un bando 73, gara o fornitura 26, personale o concorso 12, solo enti pubblici 3, titolo senza informazioni 3); 3 sono ripubblicazioni dello stesso avviso. **n₁ = 45**.
- **B, incentivi.gov.it** (2026-10-27): 15 schede aperte in tutte e due le date con la sola Sicilia; 8 sono di altri enti (Comuni, Agenzia delle Entrate, INAIL, Invitalia), che sul sito della Regione non possono esserci, e restano fuori. **n₂ = 7**.
- **In comune:** m = 2. Stimatore di Chapman: N = (n₁+1)(n₂+1)/(m+1) − 1 = **122**; intervallo di Chao al 95%: **72–281**. Bandi visti da almeno una fonte: 50.

| fonte | bandi | quota del totale stimato (IC 95%) |
|---|---|---|
| incentivi.gov.it | 7 | **6%** (2%–10%) |
| siti della Regione e IRFIS | 45 | **37%** (16%–62%) |
| tutte e due | 50 | **41%** (18%–69%) |

Le quote usano l'intervallo del totale, non quello di Wilson. Senza stimare il totale, due quote dirette: il portale ha 2/45 = **4%** (1%–15%) dei bandi dei siti della Regione; i siti della Regione hanno 2/7 = **29%** (8%–64%) delle schede del portale.

Le schede del portale, una per una:

| scheda del portale | voce più simile sui siti della Regione | punteggio | stesso bando? |
|---|---|---|---|
| Fondo Sicilia - contributi a fondo perduto alle imprese - Regione Siciliana | Contributo a fondo perduto per i consumatori che accedono alle procedure di sov… | 0.44 | no |
| Azione 2.1.2 - Avviso Pubblico sui progetti innovativi integrati di efficientam… | Avviso Pubblico "Sicilia efficiente: meno consumi, più futuro" - Azione 2.1.2 d… | 0.60 | no (a mano) |
| Contributi a sostegno delle produzioni cinematografiche e audiovisive 2025-2027… | Avviso “DIGIT IMPRESE” - Azione 1.1.2 “Sostegno all’innovazione delle imprese” … | 0.42 | no |
| Regione Siciliana - Bando per la partecipazione a eventi fieristici 2026 - 2027… | Prestito d’onore studenti universitari | 0.45 | no |
| Regione Siciliana - Incentivi a sostegno del lavoro agile - South Working - Art… | Incentivi a sostegno del lavoro agile – South Working Art. 3 L.R. n. 1 del 5 ge… | 1.00 | sì |
| Regione Siciliana - Incentivi a sostegno delle assunzioni a tempo indeterminato… | Avviso Incentivi a sostegno delle assunzioni a tempo indeterminato – Art. 1 L.R… | 1.00 | sì |
| Intervento SRD03 investimenti nelle aziende agricole per la diversificazione in… | Bando per il finanziamento di progetti di riqualificazione dei mercati rionali | 0.42 | no |

**Perché l'indipendenza non regge, e in che direzione sbaglia la stima:**
- *Dipendenza positiva:* la Regione carica sul portale gli stessi bandi che pubblica sul suo sito. Un bando visto da A ha più probabilità di essere visto anche da B: m cresce e N **si sottostima**.
- *Eterogeneità:* il portale per legge riguarda le imprese (art. 18-ter D.L. 34/2019). Un bando per le persone (lavastoviglie, donne vittime di violenza, prestito d'onore) non ha quasi nessuna probabilità di stare sul portale. Anche questo fa **sottostimare** N. Il totale va letto come un minimo e le coperture come un massimo.
- *Numeri piccoli:* con m così basso basta un abbinamento in più o in meno per spostare molto N: per questo la tabella delle schede, da controllare.
- Il sito non dà la data di apertura: un bando aperto dopo il 27/10 non poteva stare nell'export del portale. Pochi casi, nella stessa direzione.
- Scartato: stimare la Sicilia dal solo portale con il rapporto della Lombardia. Le regioni alimentano il portale in modo troppo diverso (`docs/copertura-portale.md`).

## Filtro di rilevanza

Regole sul titolo (in Lombardia anche sul tipo "Concorsi Pubblici e Avvisi sul Personale"), in `NON_RILEVANTE` di `pipeline/copertura.py`. Si tolgono: atti che non sono bandi (vendite, locazioni, graduatorie, rettifiche, iscrizioni a elenchi), gare e forniture, personale e concorsi, bandi solo per enti pubblici (enti locali, comuni, università, opere FSC, ordinanze di protezione civile). Un bando "per enti" che nomina anche imprese, famiglie, studenti o privati resta dentro. Il Terzo settore e le associazioni contano come privati.

**Controllo a mano** su campioni fissi (ordinati per hash del titolo, quindi uguali a ogni esecuzione; revisione: coppie: Edoardo, 20/11/2026, aprendo i bandi (4 non decidibili restano con la stima automatica dell'8/11); campioni: stima automatica dell'8/11/2026, dai soli titoli, da confermare):
- Lombardia, voci aperte del dataset: d'accordo 40/40 = **100%** (91%–100%).
- Sicilia, voci dei siti della Regione: d'accordo 40/40 = **100%** (91%–100%).
- ⚠ Questi due campioni vengono dalle stesse liste su cui sono state scritte le regole: l'accordo è ottimista. Per questo un terzo campione da una lista mai guardata prima, la raccolta della Toscana del 2026-11-07 (regole non più toccate dopo averlo visto): d'accordo 18/30 = **60%** (42%–75%). È la stima onesta della qualità del filtro su dati nuovi. Quasi tutti gli errori lasciano dentro voci che non sono bandi per privati.
  - disaccordo: "Riconoscimento dei percorsi formativi degli organismi formativi per Esperta ed Esperto di…": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Avviso pubblico per l'eliminazione delle barriere architettoniche in ambito portuale": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Incarichi vacanti di assistenza primaria e continuità assistenziale-Procedura SISAC 2021": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "2° Bando per accoglienza bambini e bambine nei servizi educativi per la prima infanzia 20…": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Contributi ai datori di lavoro per l'assunzione di donne inserite in percorsi di uscita d…": filtro *personale o concorso*, a mano *rilevante*
  - disaccordo: "Avviso per l'assistenza pediatrica 2026 - Seconda pubblicazione": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Alta formazione e ricerca-azione, bando 2026: finanziamenti per progetti con attivazione …": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Programma europeo sulle malattie rare -JTC 2023": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Contributo ordinario 2021 alle Reti documentarie locali": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Segnala illeciti": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Partenariato europeo per la medicina personalizzata JTC 2027": filtro *rilevante*, a mano *non rilevante*
  - disaccordo: "Bando "Sistemi Museali 2023"": filtro *rilevante*, a mano *non rilevante*

## Abbinamento

1. **Codice:** gli indirizzi di Bandi e Servizi finiscono con il codice del bando, lo stesso del dataset (`...-RLO12023036183`). Quando il portale o la nostra raccolta rimandano lì, l'abbinamento è certo.
2. **Titolo:** minuscole, senza accenti né punteggiatura, senza parole vuote (articoli, "avviso", "bando", nomi della regione). Punteggio = massimo tra somiglianza delle sequenze (`difflib`) e sovrapposizione delle parole (Dice). **Stesso bando da 0.75**; zona grigia tra 0.60 e 0.75, da decidere a mano.
3. **Correzioni**, aggiunte guardando gli errori: luoghi, anni, assi o ordinali diversi ("Provincia di Bergamo" e "di Como", "Brevetti 2021" e "2023", "Asse I" e "Asse II") danno 0; il luogo si legge anche dal nome dell'ente. Un luogo in un titolo solo porta al massimo in zona grigia. Un titolo corto tutto contenuto nell'altro ("Re-Impresa"), o la stessa azione di programma ("Azione 2.1.2"), porta almeno in zona grigia.
4. **Taratura sulle coppie certe:** 50 schede del portale (di ogni stato) hanno il codice di un bando del dataset. Rifacendo l'abbinamento solo per titolo, tra tutte le 605 schede lombarde del portale: automatico e giusto 32, automatico e sbagliato 2, zona grigia con la scheda giusta 10, zona grigia con una sbagliata 1, perso 5. La soglia è prudente: sbaglia di rado da sola, e lascia molto alla revisione a mano.

**Zona grigia: 25 coppie**, decise nel file `data/copertura/revisione.yaml` (revisione: coppie: Edoardo, 20/11/2026, aprendo i bandi (4 non decidibili restano con la stima automatica dell'8/11); campioni: stima automatica dell'8/11/2026, dai soli titoli, da confermare); 0 ancora da fare, che contano come non trovate.

| confronto | voce di riferimento | più simile | punteggio | stesso bando? |
|---|---|---|---|---|
| Lombardia: dataset ↔ portale | Dote Impresa Collocamento Mirato Asse I - Provincia di Monza e Brianza | Dote Impresa Collocamento Mirato - Fondo 2024 - Operatività 2025-2026… | 0.61 | sì |
| Lombardia: dataset ↔ portale | Dote Impresa Collocamento Mirato Asse II - Provincia di Monza e Brian… | Dote Impresa Collocamento Mirato - Fondo 2024 - Operatività 2025-2026… | 0.64 | sì |
| Lombardia: dataset ↔ portale | Dote Impresa Collocamento Mirato - Asse III - Provincia di Monza e Br… | Dote Impresa Collocamento Mirato - Fondo 2024 - Operatività 2025-2026… | 0.61 | sì |
| Lombardia: dataset ↔ portale | Dote Impresa Collocamento Mirato - Asse III - Città metropolitana di … | Regione Lombardia - Dote Impresa Collocamento Mirato – Assi I-II-III | 0.71 | sì |
| Lombardia: dataset ↔ portale | Dote Unica Lavoro Persone con Disabilità - Provincia di Pavia | Dote Impresa Collocamento Mirato Disabili - Annualità 2025 - Provinci… | 0.63 | no |
| Lombardia: dataset ↔ portale | Dote Unica Lavoro Persone con Disabilità - Provincia di Varese | Bando Piano Provinciale Disabili Masterplan 2024 - Provincia di Varese | 0.64 | no |
| Lombardia: dataset ↔ portale | Rafforza&Innova | Bando Rafforza&Innova - PR Lombardia FESR 2021-2027 | 0.62 | sì |
| Lombardia: dataset ↔ portale | QUOTA LOMBARDIA | Avviso "Quota Lombardia" a sostegno delle PMI lombarde | 0.60 | sì |
| Lombardia: dataset ↔ portale | CONTRIBUTI PER LA PARTECIPAZIONE DELLE MPMI A FIERE INTERNAZIONALI IN… | Contributi per la partecipazione delle PMI alle fiere internazionali … | 0.70 | no |
| Lombardia: dataset ↔ portale | Formazione Continua - Quarta Edizione - Voucher aziendali a catalogo … | Formazione Continua - Quarta edizione - Regione Lombardia | 0.61 | sì |
| Lombardia: dataset ↔ portale | Formazione Continua terza edizione - Voucher aziendali a catalogo (PR… | Voucher aziendali per interventi di formazione aggiuntiva in materia … | 0.67 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Bando Dote Impresa Collocamento Mirato Asse I - Provincia di Bergamo | Dote impresa anni - Provincia di Bergamo - 2024/2025 | 0.68 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Bando Dote Impresa Collocamento Mirato Asse II - Provincia di Bergamo | Dote impresa anni - Provincia di Bergamo - 2024/2025 | 0.66 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Bando Dote Impresa Collocamento Mirato Asse III - Provincia di Bergamo | Dote impresa anni - Provincia di Bergamo - 2024/2025 | 0.65 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Dote impresa collocamento mirato ASSE I - Provincia di Brescia | Bando per l’erogazione di contributi alle imprese del settore apistic… | 0.64 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Dote Impresa Collocamento Mirato Asse II - Provincia di Brescia | Bando per l’erogazione di contributi alle imprese del settore apistic… | 0.64 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Dote Impresa Collocamento Mirato Asse III - Provincia di Brescia | Bando per l’erogazione di contributi alle imprese del settore apistic… | 0.63 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Servizi Integrativi - Provincia di Monza e Brianza | Servizi digitali AI generativa - CCIAA Milano Monza Brianza Lodi | 0.67 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Dote Unica Lavoro Persone con Disabilità- Città metropolitana di Mila… | Bando Dote Impresa collocamento mirato - Annualità 2024-2025 - Città … | 0.63 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Servizi Integrativi - Provincia di Pavia | Bando Investimenti Innovativi MPMI - Provincia di Pavia - 2024 | 0.64 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Dote Unica Lavoro Persone con Disabilità - Provincia di Varese | Bando Dote Impresa Masterplan 2021 - Piano Provinciale Disabili - Pro… | 0.69 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Rafforza&Innova | Bando Collabora & Innova | 0.71 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Pacchetto investimenti – Linea sviluppo aziendale | PR FESR Lombardia 2021-2027 - Pacchetto Investimenti - Linea Green | 0.63 | no |
| Lombardia: dataset ↔ schede chiuse del portale | Bando Check-up d'impresa | Bando Musei di Impresa | 0.62 | no |
| Sicilia: portale ↔ siti della Regione | Azione 2.1.2 - Avviso Pubblico sui progetti innovativi integrati di e… | Avviso Pubblico "Sicilia efficiente: meno consumi, più futuro" - Azio… | 0.60 | no |

## Limiti

- **Il filtro di rilevanza è sul titolo**, e su una lista nuova sbaglia 12 voci su 30 (campione toscano). Il dataset lombardo non ha i destinatari, il sito siciliano nemmeno il tipo di atto. Un denominatore che contiene voci non rilevanti fa sembrare la copertura più bassa.
- **Lombardia: "elenco ufficiale" vuol dire "Bandi e Servizi".** Il dataset è della Regione: mancano Camere di commercio, Comuni, ATS e le misure che Finlombarda pubblica solo sul suo sito. Per la Lombardia nel complesso la copertura vera è più bassa di quella in tabella.
- **Il denominatore mescola persone e imprese.** Il portale per legge copre le imprese: una parte della sua bassa copertura è fuori dal suo compito, non un difetto. Per separarle servono i destinatari, che il dataset non ha; le schede di Bandi e Servizi li danno con le icone (nei documenti raccolti, fuori da git): si può aggiungere.
- **Revisione dei campioni:** stimata automaticamente da titoli, enti e date, senza aprire i bandi; le coppie le ha controllate Edoardo aprendo i bandi (20/11).
- **Una sola data, due sole regioni:** il caso migliore e uno dei peggiori del portale (`docs/copertura-portale.md`), non un campione delle regioni.
