# Schede per la revisione a mano

*Generato da `prove/simulazione/schede_revisione.py`. Per ogni regola: cosa dice la regola, da confrontare con il bando aperto dal link. L'esito (giusta / errori piccoli / sbagliata) si segna in `docs/da-rivedere-a-mano.md`. Niente LLM nel giudizio (decisione 97).*

## 1. Contributo per sostenere le spese relative a sessioni di psicoterapia - Bonus psicologo

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.contributo-per-sostenere-le-spese-relative-a-sessioni-di-psicoterapia-bonus-psicologo.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-contributo-per-sostenere-le-spese-relative-a`

**Requisiti della regola:**

- *controllato:* residenza in Italia: sì
  > «residenza in Italia;»
- *controllato:* ISEE al massimo 50.000
  > «ISEE in corso di validità, con valore non superiore a 50mila euro.»
- *da verificare a mano:* Condizione di ansia, stress, depressione o fragilità psicologica e volontà di seguire un percorso di psicoterapia: è un dato sanitario che il sito non chiede.
  > «in condizione di ansia, stress, depressione e fragilità psicologica;»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 2. Fondo di garanzia per la prima casa (Consap)

- **Link:** https://www.consap.it/fondo-prima-casa/
- **Ente:** Consap · **origine:** estratta · **date:** nessuna data · **file:** `consap-fondo-prima-casa`

**Requisiti della regola:**

- *da verificare a mano:* Non essere proprietari, alla data della domanda di mutuo, di altri immobili a uso abitativo anche all'estero (salvo quelli ereditati e concessi in uso gratuito a genitori o fratelli): il campo proprieta_altra_abitazione riguarda solo case adatte al nucleo e anche i familiari, quindi non corrisponde.
  > «non siano proprietari di altri immobili a uso abitativo, anche all’estero.»
- **almeno una di queste:** «l’accesso al Fondo è riservato ai soggetti appartenenti alle seguenti categorie:»
  - **tutte queste:** «giovani coppie coniugate o conviventi more uxorio il cui nucleo familiare sia stato costituito da almeno due anni»
    - **almeno una persona del nucleo:**
      - *controllato:* età meno di 36
    - *da verificare a mano:* Coppia coniugata o convivente more uxorio con nucleo costituito da almeno due anni: manca il campo.
  - **tutte queste:** «nuclei familiari monogenitoriali con figli minori»
    - **almeno una persona del nucleo:**
      - *controllato:* figlio: sì
      - *controllato:* età meno di 18
    - *da verificare a mano:* Nucleo monogenitoriale: manca il campo.
  - **tutte queste:** «conduttori di alloggi di proprietà degli istituti autonomi per le case popolari»
    - *controllato:* abitazione: in affitto
    - *da verificare a mano:* Alloggio di proprietà degli istituti autonomi per le case popolari: manca il campo.
  - *controllato:* età meno di 36
    > «giovani che non abbiano compiuto trentasei anni»
  - **tutte queste:** «nuclei familiari con tre figli di età inferiore a ventuno anni e con ISEE non superiore a 40.000 euro annui;»
    - *controllato:* numero di figli almeno 3
    - *controllato:* ISEE al massimo 40.000
    - *da verificare a mano:* I figli devono avere meno di 21 anni: numero_figli conta tutti i figli, senza limite di età.
  - **tutte queste:** «nuclei familiari con quattro figli di età inferiore a ventuno anni e con ISEE non superiore a 45.000 euro annui;»
    - *controllato:* numero di figli almeno 4
    - *controllato:* ISEE al massimo 45.000
    - *da verificare a mano:* I figli devono avere meno di 21 anni: numero_figli conta tutti i figli, senza limite di età.
  - **tutte queste:** «nuclei familiari con cinque o più figli di età inferiore a ventuno anni e con ISEE non superiore a 50.000 euro annui.»
    - *controllato:* numero di figli almeno 5
    - *controllato:* ISEE al massimo 50.000
    - *da verificare a mano:* I figli devono avere meno di 21 anni: numero_figli conta tutti i figli, senza limite di età.
  - **tutte queste:** «le persone con disabilità permanente accertata ai sensi dell’articolo 3, comma 3, della legge 5 febbraio 1992, n. 104;»
    - *controllato:* disabilità: sì
    - *da verificare a mano:* Disabilità permanente accertata ai sensi dell'art. 3, comma 3, legge 104/1992: la risposta generica non identifica questa categoria.
  - **tutte queste:** «i componenti di un nucleo familiare al quale appartenga da almeno due anni un familiare convivente, figlio, figlia, fratello o sorella del richiedente»
    - **almeno una persona del nucleo:**
      - *controllato:* disabilità: sì
    - *da verificare a mano:* Familiare convivente (figlio, figlia, fratello o sorella del richiedente) nel nucleo da almeno due anni, con disabilità permanente accertata ai sensi dell'art. 3, comma 3, legge 104/1992: mancano i campi su parentela, durata e tipo di accertamento.
- *da verificare a mano:* Mutuo di importo non superiore a 250.000 euro, destinato all'acquisto (anche con ristrutturazione per efficienza energetica o accollo da frazionamento) dell'abitazione principale: mancano i campi sul mutuo.
  > «L’importo del finanziamento non può essere superiore a 250.000 euro.»
- *da verificare a mano:* Immobile da destinare ad abitazione principale, non di categoria catastale A/1, A/8 o A/9 e senza caratteristiche di lusso (d.m. 2 agosto 1969): requisito di dettaglio sull'immobile.
  > «L’immobile acquistato mediante il finanziamento garantito dal Fondo deve essere destinato ad abitazione principale del mutuatario.»

**Note:** La pagina dice che l'accesso è 'riservato' alle categorie elencate, ma altrove le chiama 'categorie prioritarie' e parla di garanzia 'ordinariamente' al 50%: non è chiaro se chi non rientra in nessuna categoria sia escluso o solo non prioritario. Le categorie sono state trattate come requisito, seguendo la parola 'riservato'. · Categorie per numero di figli: scritte come 'almeno N figli' con la soglia ISEE della categoria; chi ha più figli rientra comunque nella soglia più alta. · Le categorie sulla disabilità valgono dal 3 agosto 2026. · La concessione del mutuo resta a giudizio della banca; la domanda si presenta alla banca contestualmente alla domanda di mutuo. Il termine del 31 dicembre 2027 riguarda solo la garanzia elevata, non l'accesso al Fondo.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 3. Detrazione IRPEF per gli inquilini con reddito fino a 30.987 euro (300 o 150 euro; 495,80 o 247,90 con canone concordato)

- **Link:** https://www.agenziaentrate.gov.it/portale/documents/20143/5629825/Detrazioni+per+canoni+di+locazione_tabella_aggiornata.pdf/f76fe2b8-ecab-9d12-1986-752885a8b95a
- **Ente:** Agenzia delle Entrate · **origine:** estratta · **date:** nessuna data · **file:** `entrate-detrazioni-affitto-2026-inquilini`

**Requisiti della regola:**

- *controllato:* abitazione: in affitto
  > «Inquilini che utilizzano l’immobile come abitazione principale»
- *controllato:* reddito complessivo 2025 inclusa cedolare secca per detrazioni affitto al massimo 30.987,41
  > «150 euro per Reddito complessivo superiore a 15.493,71 ma fino a 30.987,41 euro.»
- *da verificare a mano:* Il contratto deve essere stipulato o rinnovato secondo la Legge 431/1998 e l'immobile deve essere la tua abitazione principale.
  > «Tutti i contratti stipulati o rinnovati (Legge 431/1998)»

**Note:** Importi: con contratto libero 300 euro fino a 15.493,71 euro di reddito complessivo e 150 euro fino a 30.987,41; con canone concordato 495,80 e 247,90 euro. · Si chiede con la dichiarazione dei redditi; se l'imposta non basta, dà un rimborso: vale anche per chi non paga IRPEF. · Le detrazioni per l'affitto non si cumulano e si rapportano ai giorni in cui l'immobile è abitazione principale. · Perimetro esplicito: dichiarazione 2026, spese e redditi del periodo d’imposta 2025. Reddito complessivo aumentato dei redditi dei fabbricati assoggettati a cedolare secca (istruzioni ufficiali 730/2026); non reddito corrente o solo IRPEF ordinario. Età e durata del contratto da verificare nel periodo delle spese.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 4. Assegno unico e universale per i figli a carico

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.assegno-unico-e-universale-per-i-figli-a-carico-55984.assegno-unico-e-universale-per-i-figli-a-carico.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-assegno-unico`

**Requisiti della regola:**

- **almeno una persona del nucleo:** «L’Assegno unico e universale spetta alle famiglie in cui ricorrono le seguenti condizioni:»
  - *controllato:* figlio a carico: sì
  - **almeno una di queste:**
    - *controllato:* età meno di 18
      > «per ogni figlio minorenne a carico»
    - *controllato:* disabilità: sì
      > «per ogni figlio con disabilità a carico, senza limiti di età»
    - **tutte queste:** «fino al compimento dei 21 anni, con un reddito complessivo inferiore a 8mila euro annui»
      - *controllato:* età tra 18 e 20
      - *controllato:* reddito annuo meno di 8.000
      - *controllato:* attività: studia, tirocinio o lavoro a basso reddito, disoccupato, iscritto al centro per l'impiego, servizio civile
- **almeno una di queste:** «cittadinanza o titolo di soggiorno»
  - *controllato:* cittadinanza: italiana, di un altro paese dell'unione europea
  - *da verificare a mano:* Altri titoli di soggiorno: la scheda non dice quali sono validi.
- *controllato:* soggetto alle imposte sul reddito in Italia: sì
  > «assoggettamento all’imposta sul reddito in Italia»
- **almeno una di queste:** «residenza in Italia oppure svolgimento di attività lavorativa in Italia, con iscrizione a una gestione previdenziale obbligatoria e regolarità contributiva»
  - *controllato:* residenza in Italia: sì
  - **tutte queste:**
    - *controllato:* lavoro in Italia: sì
    - *da verificare a mano:* Iscrizione a una gestione previdenziale obbligatoria e regolarità contributiva: mancano i campi. Riferita solo a chi lavora in Italia, ma la frase ammette anche l'altra lettura.

**Note:** L'ISEE non decide l'idoneità, solo l'importo: anche senza ISEE si riceve il minimo.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 5. Carta "Dedicata a te" 2026

- **Link:** https://www.masaf.gov.it/Carta_Dedicata_a_te_2026-info
- **Ente:** Ministero dell'agricoltura, della sovranità alimentare e delle foreste · **origine:** estratta · **date:** nessuna data · **file:** `masaf-carta-dedicata-a-te-2026`

**Requisiti della regola:**

- *controllato:* residenza in Italia: sì
  > «Saranno coinvolti 1.177.597 nuclei familiari residenti in Italia, composti»
- **almeno una di queste:** «da almeno tre persone con almeno un minore, con ISEE inferiore a 15.000 euro e»
  - **tutte queste:**
    - *controllato:* componenti del nucleo almeno 3
    - **almeno una persona del nucleo:**
      - *controllato:* età meno di 18
  - *da verificare a mano:* La pagina presenta la composizione (almeno 3 componenti con almeno un minore) anche come 'criterio di priorità': non è chiaro se i nuclei diversi siano esclusi o solo in coda.
- *controllato:* ISEE al massimo 15.000
  > «Requisiti principali: Indicatore ISEE fino a 15.000 euro»
- *da verificare a mano:* Il nucleo non deve ricevere altri strumenti di inclusione sociale o di sostegno alla povertà, nazionali o locali: la pagina non dice quali e manca il campo.
  > «privi di altri strumenti di inclusione sociale o sostegno alla povertà.»

**Note:** Non c'è domanda: l'INPS individua direttamente i beneficiari, quindi non ci sono date di apertura e chiusura. · Soglia ISEE scritta in due modi: 'ISEE inferiore a 15.000 euro' e 'Indicatore ISEE fino a 15.000 euro'. Ho usato <= 15000, la lettura che non esclude chi ha esattamente 15.000 euro. · La composizione del nucleo (almeno tre persone con almeno un minore) compare sia tra le caratteristiche dei beneficiari sia come 'Criterio di priorità': l'ho resa come requisito con un'alternativa da verificare. · La carta va attivata con un primo acquisto entro il 16 dicembre 2026, pena la perdita di validità: è una condizione successiva all'assegnazione, non un requisito di accesso. · È una pagina web informativa (comunicato), non il decreto: mancano i dettagli, per esempio quali misure di sostegno escludono dalla carta.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 6. Indennità di congedo parentale per lavoratrici e lavoratori dipendenti

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.50583.indennit-di-congedo-parentale-per-lavoratrici-e-lavoratori-dipendenti.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-indennita-di-congedo-parentale-per-lavoratric`

**Requisiti della regola:**

- *controllato:* situazione lavorativa: lavoro
  > «Le lavoratrici e i lavoratori dipendenti devono avere un rapporto di lavoro in corso.»
- *controllato:* tipo di lavoro: dipendente
  > «Il congedo parentale è rivolto a lavoratrici e lavoratori dipendenti»
- **almeno una di queste:** «entro i primi 14 anni di vita del bambino»
  - **almeno una persona del nucleo:**
    - *controllato:* figlio: sì
    - *controllato:* età meno di 14
  - *da verificare a mano:* Figlio adottivo o affidatario: il congedo spetta entro 14 anni dall'ingresso in famiglia e fino ai 18 anni, ma manca la data di ingresso del minore nel nucleo.
    > «entro i primi 14 anni dall'ingresso del minore nella famiglia, indipendentemente dall'età del bambino all'atto dell'adozione o affidamento, e non oltre il compimento della sua maggiore età.»
- *da verificare a mano:* Esclusi i genitori lavoratori domestici o a domicilio: manca il settore o la modalità del lavoro.
  > «genitori lavoratori domestici; genitori lavoratori a domicilio.»
- *da verificare a mano (eccezione rara):* Lavoratori agricoli a tempo determinato: servono almeno 51 giornate di lavoro in agricoltura nell'anno precedente, e mancano settore, tipo di contratto e giornate lavorate.
  > «Le lavoratrici e i lavoratori agricoli a tempo determinato possono fare richiesta di congedo parentale, se hanno prestato 51 giornate di lavoro in agricoltura nell'anno precedente l'evento»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 7. Nuovo Bonus mamme 2026

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.nuovo-bonus-mamme-2026.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-nuovo-bonus-mamme-2026`

**Requisiti della regola:**

- *controllato:* situazione lavorativa: lavoro
  > «Il contributo è rivolto alle madri lavoratrici, escluse le lavoratrici domestiche»
- *controllato:* tipo di lavoro: dipendente, autonomo
  > «dipendente o attività autonoma»
- *controllato:* numero di figli almeno 2
  > «con due o più figli»
- *da verificare a mano:* Deve essere la madre dei figli: il vocabolario non ha il sesso di chi fa domanda.
  > «alle madri lavoratrici»
- *da verificare a mano:* Escluse le lavoratrici domestiche: manca il settore del lavoro (lavoro domestico sì/no).
  > «escluse le lavoratrici domestiche»
- *da verificare a mano:* Escluse le madri con tre o più figli, dipendenti a tempo indeterminato, che possono avere l'esonero contributivo IVS: mancano il tipo di contratto (tempo indeterminato) e l'accesso all'esonero.
  > «Sono escluse le lavoratrici madri con tre o più figli titolari di contratto di lavoro dipendente a tempo indeterminato che possono accedere all’esonero contributivo previdenziale per l’invalidità, la vecchiaia e i superstiti (IVS)»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 8. Contributi agli inquilini morosi incolpevoli nel libero mercato (Comune di Milano), scadenza 31/12/2026

- **Link:** https://www.milanoabitare.org/#morosita-incolpevole-2026
- **Ente:** Comune di Milano · **origine:** estratta · **date:** chiusura 2026-12-31 · **file:** `milano-morosita-incolpevole-2026`

**Requisiti della regola:**

- *controllato:* comune di residenza: Milano
  > «del Comune di Milano dove il richiedente ha la propria residenza»
- *controllato:* cittadinanza: uno dei 7 elencati (per esempio italiana, di un altro paese dell'unione europea, familiare di un cittadino ue, con diritto di soggiorno)
  > «a) cittadinanza italiana o appartenenza ad uno Stato dell’Unione Europea o appartenenza ad uno Stato esterno»
- **almeno una di queste:** «b) reddito I.S.E. non superiore ad € 35.000,00 o reddito derivante da regolare attività lavorativa con un valore»
  - *da verificare a mano:* Reddito I.S.E. non superiore a 35.000 euro: il vocabolario ha l'ISEE ma non l'ISE.
  - **tutte queste:**
    - *controllato:* ISEE al massimo 26.000
    - *da verificare a mano:* Il reddito deve derivare da regolare attività lavorativa: manca il campo sulla fonte del reddito.
- *da verificare a mano:* Essere destinatari di un atto di intimazione di sfratto per morosità (non ancora convalidato) o di un provvedimento di rilascio esecutivo: manca il campo.
  > «c) essere destinatari di un atto di intimazione di sfratto per morosità;»
- *da verificare a mano:* Morosità incolpevole: mancato pagamento del canone dovuto a una delle cause elencate (licenziamento, cassa integrazione, malattia grave, nascita di figli, separazione…), verificatasi dal 2021 in poi, prima dell'inizio della morosità e dopo la stipula del contratto: mancano i campi.
  > «Sono morosi incolpevoli gli inquilini che non hanno potuto provvedere al pagamento del canone locativo a»
- *da verificare a mano:* Incidenza del canone sul reddito complessivo IRPEF superiore al 30% in almeno una delle cinque annualità precedenti il bando: il vocabolario non ha il reddito del nucleo per anno.
  > «La verifica si riterrà conclusa positivamente qualora l’incidenza canone/reddito risulti superiore al 30 % in almeno»
- *controllato:* abitazione: in affitto
  > «d) titolarità di un contratto di locazione di unità immobiliare ad uso abitativo regolarmente registrato (sono»
- *controllato:* contratto di affitto registrato: sì
  > «d) titolarità di un contratto di locazione di unità immobiliare ad uso abitativo regolarmente registrato (sono»
- *da verificare a mano:* Contratto sul libero mercato (anche canone calmierato) per un immobile non di categoria catastale A1, A8 o A9; esclusi gli alloggi di Comune o Aler a canone sociale, moderato o concordato, salvo che siano nella disponibilità di terzi: mancano tipo di contratto e categoria catastale.
  > «Sono esclusi, altresì, gli inquilini titolari di contratto di locazione per alloggi di proprietà del Comune o dell’Aler a»
- *da verificare a mano:* Residenza nell'alloggio oggetto della procedura di rilascio da almeno un anno alla data dell'atto di intimazione di sfratto: manca il campo.
  > «procedura di rilascio da almeno un anno.»
- **almeno una di queste:** «Il richiedente che sia titolare, o che abbia nel proprio nucleo un componente che sia titolare, di diritto di»
  - *controllato:* proprietà di un'altra casa: no
  - *da verificare a mano:* Chi possiede una casa adeguata fuori dalla provincia di residenza non è escluso: il vocabolario non distingue dove si trova l'altra casa.
- *da verificare a mano:* Non aver già beneficiato dei contributi del D.M. 202/2014 e del D.M. 30/03/2016 in bandi precedenti: manca il campo.
  > «Sono esclusi i richiedenti che abbiano già beneficiato dei contributi di cui al D.M. n. 202 del 14.05.2014 e del»

**Note:** Le domande si presentano al Municipio di residenza dalla data di pubblicazione (non indicata nel testo) fino al 31 dicembre 2026, fa fede la data di protocollo. · Requisito di reddito: 'reddito I.S.E. non superiore ad € 35.000,00 o reddito derivante da regolare attività lavorativa con un valore I.S.E.E. non superiore ad € 26.000,00'. Ho letto le due soglie come alternative; il vocabolario non ha l'ISE, quindi il requisito resta quasi sempre da verificare. · La residenza a Milano è ricavata dal fatto che la domanda va al Municipio di residenza e il contributo è del Comune: il testo non lo dice come requisito esplicito. · La presenza nel nucleo di ultrasettantenni, minori, invalidi almeno al 74% o persone in carico ai servizi è solo un criterio preferenziale, non un requisito. · Il contributo si eroga fino a esaurimento delle risorse regionali trasferite.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 9. Bonus sociale per disagio economico: luce, gas e acqua (ARERA)

- **Link:** https://www.arera.it/consumatori/bonus-sociale/bonus-sociale-per-disagio-economico/quali-sono-i-requisiti
- **Ente:** ARERA - Autorità di Regolazione per Energia Reti e Ambiente · **origine:** estratta · **date:** nessuna data · **file:** `arera-bonus-sociale-luce-gas-2026`

**Requisiti della regola:**

- **almeno una di queste:** «Il cittadino o il nucleo familiare ha diritto al bonus se:»
  - *controllato:* ISEE al massimo 9.796
    > «non è superiore a 9.796 euro per famiglie con massimo 3 figli a carico»
  - **tutte queste:** «non è superiore a 20.000 euro per le famiglie numerose con almeno 4 figli a carico»
    - *controllato:* numero di figli almeno 4
    - *controllato:* ISEE al massimo 20.000
- *da verificare a mano:* Serve una fornitura di luce, gas o acqua con requisiti propri: diretta (intestata a un componente del nucleo ISEE, per uso domestico, attiva o sospesa per morosità; per il gas anche uso riscaldamento/cottura/acqua calda e contatore non oltre G6) oppure condominiale di gas o acqua (attiva, in locali abitativi; per l'acqua anche un contratto elettrico domestico intestato al nucleo). Il vocabolario non ha campi sulle forniture.
  > «la fornitura (ossia il contratto elettrico/gas/idrico) è intestata a uno dei componenti il nucleo ISEE.»

**Note:** Il testo estratto ha perso la frase che introduce le soglie: si legge solo 'non è superiore a 9.796 euro'. Le ho lette come soglie ISEE perché il documento parla di nucleo ISEE e DSU, ma il campo non è nominato esplicitamente accanto alle cifre. · La soglia di 20.000 euro vale per 'almeno 4 figli a carico': numero_figli conta i figli anche non a carico, quindi il requisito può risultare più largo del vero. · Il documento descrive tre bonus distinti (luce, gas, acqua), ciascuno legato a una propria fornitura: ho raccolto tutte le condizioni sulle forniture in un solo requisito da verificare. · Il documento non indica date di apertura o chiusura delle domande, né requisiti di cittadinanza o residenza.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 10. Assegno di Inclusione (ADI)

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.assegno-di-inclusione-adi.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-adi`

**Requisiti della regola:**

- **almeno una di queste:** «L’ADI è riconosciuto ai nuclei familiari nei quali risulti presente almeno un componente:»
  - *controllato:* permesso per casi speciali: sì
    > «L’ADI è, altresì, riconosciuto ai soggetti titolari di permesso di soggiorno per “casi speciali”»
  - **almeno una persona del nucleo:**
    - **almeno una di queste:**
      - *controllato:* disabilità: sì
      - *controllato:* età meno di 18
      - *controllato:* età almeno 60
      - *controllato:* seguito dai servizi socio-sanitari: sì
- **almeno una di queste:** «Il richiedente deve essere, alternativamente:»
  - *controllato:* permesso per casi speciali: sì
  - *controllato:* cittadinanza: italiana, di un altro paese dell'unione europea, familiare di un cittadino ue, con diritto di soggiorno, extra ue, con permesso di lungo periodo, protezione internazionale (rifugiato o sussidiaria), apolide
- **almeno una di queste:** «deve essere residente in Italia da almeno cinque anni, di cui gli ultimi due in modo continuativo»
  - *controllato:* permesso per casi speciali: sì
  - **tutte queste:**
    - *controllato:* anni di residenza in Italia almeno 5
    - *controllato:* anni di residenza continuativa in Italia almeno 2
- **almeno una di queste:** «un valore dell’ISEE, in corso di validità non superiore a 10.140 euro»
  - *controllato:* permesso per casi speciali: sì
  - *controllato:* ISEE 2026 per specifiche prestazioni familiari e inclusione al massimo 10.140
- **almeno una di queste:** «moltiplicata per il corrispondente parametro della scala di equivalenza ADI»
  - *controllato:* permesso per casi speciali: sì
  - *da verificare a mano:* Reddito familiare sotto una soglia moltiplicata per la scala di equivalenza ADI, che la scheda non riporta.
- **almeno una di queste:** «non superiore a 150.000 euro, non superiore a 30.000 euro»
  - *controllato:* permesso per casi speciali: sì
  - *controllato:* valore degli immobili al massimo 30.000
- **almeno una di queste:** «6.000 euro per i nuclei composti da un solo componente»
  - *controllato:* permesso per casi speciali: sì
  - *da verificare a mano:* Patrimonio mobiliare: la soglia dipende da numero di componenti, figli e disabilità.
- *controllato:* auto/moto oltre soglia senza agevolazioni per disabilità: no
  > «esclusi gli autoveicoli e i motoveicoli per cui è prevista una agevolazione fiscale per le persone con disabilità»
- *controllato:* barche o aeromobili: no
  > «navi o imbarcazioni da diporto»
- *da verificare a mano:* Assenza di condanne e misure cautelari, dimissioni recenti, strutture a carico pubblico, obbligo di istruzione. Scelta: non chiediamo dati giudiziari.
  > «non essere sottoposto a misura cautelare personale»
- *da verificare a mano:* Disabilità: la risposta generica non identifica automaticamente le categorie ISEE previste per ADI. Verificare il verbale e la categoria con INPS/CAF.

**Note:** La continuità della residenza ha eccezioni (assenze per salute) che qui non controlliamo: si chiedono solo gli anni. · I titolari di permesso per casi speciali hanno altre condizioni, descritte nella circolare INPS 20 maggio 2026, n. 58. · Per il 2026 usare l’ISEE per specifiche prestazioni familiari e per l’inclusione (messaggio INPS 102/2026), non quello ordinario: non ne deduciamo il valore dal precedente indicatore. Fonte: https://www.inps.it/content/dam/inps-site/it/scorporati/circolari-e-messaggi/2026/01/Circolare_15133/Allegati/16520_Messaggio-numero-102-del-12-01-2026.pdf

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 11. Detrazione IRPEF per i giovani in affitto fra 20 e 30 anni con reddito fino a 15.494 euro (da 991,60 a 2.000 euro)

- **Link:** https://www.agenziaentrate.gov.it/portale/documents/20143/5629825/Detrazioni+per+canoni+di+locazione_tabella_aggiornata.pdf/f76fe2b8-ecab-9d12-1986-752885a8b95a
- **Ente:** Agenzia delle Entrate · **origine:** estratta · **date:** nessuna data · **file:** `entrate-detrazioni-affitto-2026-giovani`

**Requisiti della regola:**

- *controllato:* età fra 20 e 30 anni nel periodo di locazione 2025: sì
  > «20 e i 31 anni non compiuti»
- *controllato:* abitazione: in affitto
  > «Inquilini di età compresa tra i 20 e 30 anni che utilizzano l’immobile come abitazione principale»
- *controllato:* reddito complessivo 2025 inclusa cedolare secca per detrazioni affitto al massimo 15.493,71
  > «complessivo fino a 15.493,71 euro. L’agevolazione spetta»
- *da verificare a mano:* La casa in affitto deve essere diversa da quella in cui risiedono i genitori.
  > «se l’immobile è diverso da quello in cui risiedono i genitori»
- *da verificare a mano:* Spetta per i primi 4 anni del contratto e non oltre i 31 anni: manca la data del contratto.
  > «per i primi 4 anni di durata del contratto nel limite del compimento dei 31 anni»

**Note:** Importo: il maggiore fra il 20% del canone annuo e 991,60 euro, fino a 2.000 euro. Si chiede con la dichiarazione dei redditi e può dare un rimborso. · Vale anche per una porzione di immobile (per esempio una stanza). · Perimetro esplicito: dichiarazione 2026, spese e redditi del periodo d’imposta 2025. Reddito complessivo aumentato dei redditi dei fabbricati assoggettati a cedolare secca (istruzioni ufficiali 730/2026); non reddito corrente o solo IRPEF ordinario. Età e durata del contratto da verificare nel periodo delle spese.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 12. Bonus asilo nido e forme di supporto presso la propria abitazione

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.bonus-asilo-nido-e-forme-di-supporto-presso-la-propria-abitazione-51105.bonus-asilo-nido-e-forme-di-supporto-presso-la-propria-abitazione.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-bonus-asilo-nido-e-forme-di-supporto-presso-l`

**Requisiti della regola:**

- **almeno una persona del nucleo:** «Spetta alle famiglie con figli: di età inferiore a tre anni»
  - *controllato:* figlio: sì
  - *controllato:* età meno di 3
- *da verificare a mano:* Il figlio deve frequentare una struttura educativa autorizzata (nidi, micronidi, sezioni primavera, spazi gioco, servizi educativi domiciliari) oppure non poterla frequentare per gravi patologie croniche certificate: mancano la frequenza del nido e la patologia del bambino.
  > «che frequentano una struttura educativa (contributo asilo nido) in possesso di regolare titolo abilitativo»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 13. Centri estivi: contributi per minori fino a 14 anni

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.centri-estivi-contributi-per-minori-fino-a-14-anni-52818.centri-estivi-contributi-per-minori-fino-a-14-anni.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-centri-estivi-contributi-per-minori-fino-a-14`

**Requisiti della regola:**

- **almeno una persona del nucleo:** «Possono partecipare al concorso i minori di età compresa tra i 3 e i 14 anni compiuti alla data del 30 giugno.»
  - *controllato:* età tra 3 e 14
- *da verificare a mano:* Il minore deve essere figlio, orfano o equiparato di un dipendente o pensionato della pubblica amministrazione iscritto alla Gestione Unitaria: nel vocabolario non c'è un campo sul lavoro pubblico.
  > «figli o orfani ed equiparati di dipendenti o pensionati della pubblica amministrazione iscritti alla Gestione Unitaria delle prestazioni creditizie e sociali»

**Note:** Rivista l'8/11/2026 dopo aver visto l'estrazione: l'età passa da < 14 a tra 3 e 14 compiuti, come dice la citazione; aggiunto il requisito del genitore dipendente o pensionato della pubblica amministrazione, che mancava.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 14. Borse di studio per master universitari “executive” Gestione Unitaria delle prestazioni creditizie e sociali

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.52356.borse-di-studio-per-master-universitari-executive-gestione-unitaria-delle-prestazioni-creditizie-e-sociali.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-borse-di-studio-per-master-universitari-execu`

**Requisiti della regola:**

- *controllato:* situazioni particolari: sono dipendente o pensionato pubblico
  > «Le borse di studio sono rivolte ai dipendenti della pubblica amministrazione:»
- **tutte queste:** «essere dipendente della pubblica amministrazione a tempo indeterminato in servizio»
  - *controllato:* situazione lavorativa: lavoro
  - *controllato:* tipo di lavoro: dipendente
- *da verificare a mano:* Contratto a tempo indeterminato e iscrizione alla Gestione Unitaria delle prestazioni creditizie e sociali da almeno un anno: mancano i campi su tipo di contratto e anzianità di iscrizione.
  > «iscritti alla Gestione Unitaria delle prestazioni creditizie e sociali (Fondo Credito) da almeno un anno»
- *controllato:* titolo di studio: laurea triennale, laurea magistrale, master, dottorato
  > «essere in possesso del titolo di studio di livello universitario»
- *da verificare a mano:* Non avere già ottenuto dall'Istituto borse di studio per master executive o corsi di aggiornamento professionale: manca il campo.
  > «non avere già ottenuto dall’Istituto borse di studio per master “executive” e/o corsi di aggiornamento professionale»

**Note:** Per il master di II livello serve la laurea magistrale, specialistica o del vecchio ordinamento: riguarda la scelta del master, non l'ammissione al concorso, quindi non è stata scritta come requisito. · L'obbligo di restare dipendente pubblico per due anni dopo il master è una condizione di restituzione, non di accesso.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 15. Contributi a fondo perduto per l’abbattimento degli interessi sui prestiti al consumo per l’acquisto di beni durevoli – Annualità 2026

- **Link:** https://www.irfis.it/contributi-a-fondo-perduto-per-labbattimento-degli-interessi-sui-prestiti-al-consumo-per-lacquisto-di-beni-durevoli-annualita-2026/
- **Ente:** IRFIS FinSicilia · **origine:** estratta · **date:** apertura 2025-12-31, chiusura 2027-01-20 · **file:** `irfis-contributi-a-fondo-perduto-per-labbattim-e64124`

**Requisiti della regola:**

- *da verificare a mano:* Essere intestatario di un prestito al consumo attivato tra il 1° gennaio 2025 e il 31 dicembre 2026 per l'acquisto di beni di consumo durevoli non di lusso: il vocabolario non ha campi sui prestiti.
  > «abbiano attivato un prestito finalizzato all’acquisto di beni di consumo durevoli non di lusso»
- *controllato:* regione di residenza: Sicilia
  > «essere residente in Sicilia;»
- *controllato:* ISEE meno di 30.000
  > «inferiore a 30.000 (trentamila) euro;»
- *da verificare a mano:* Assenza di misure di prevenzione definitive (d.lgs. 159/2011) e di condanne definitive per i reati dell'art. 94, comma 1, d.lgs. 36/2023. Scelta: non chiediamo dati giudiziari.
  > «non essere stato condannato con sentenza definitiva per i reati»

**Note:** L'ISEE può essere il 2025 oppure il 2026 vigente alla presentazione della domanda. · Sono esclusi i prestiti per beni non durevoli, semidurevoli o di lusso (gioielli, opere d'arte, auto oltre 1.600 cc, moto oltre 250 cc, barche, ecc.); ammessi sempre i prestiti per protesi e dispositivi medici. · Una sola domanda per richiedente, presentata dall'intestatario del prestito (anche tramite tutore, curatore o amministratore di sostegno). Contributo minimo 150 euro: sotto questa soglia non è concesso.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 16. Indennità per morte ai superstiti

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.indennit-per-morte-ai-superstiti-50303.indennit-per-morte-ai-superstiti.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-indennita-per-morte-ai-superstiti`

**Requisiti della regola:**

- *controllato:* situazioni particolari: sono vedovo/a od orfano/a di un lavoratore o pensionato
  > «L’indennità per morte è una prestazione economica in favore del coniuge superstite di un assicurato iscritto in una delle gestioni previdenziali INPS.»
- **almeno una di queste:** «Al coniuge superstite dell'assicurato (la cui pensione è calcolata con il sistema retributivo o misto)»
  - *da verificare a mano:* Essere il coniuge superstite e non avere diritto, alla data della morte, alla pensione indiretta: il vocabolario non distingue il coniuge dal figlio superstite né il diritto alla pensione indiretta.
    > «nel caso in cui, alla data della morte del defunto, non abbia diritto alla pensione indiretta»
  - **tutte queste:**
    - *da verificare a mano:* Figlio dell'assicurato, in mancanza del coniuge, a carico del genitore al momento del decesso: manca il campo.
      > «In mancanza del coniuge, l’indennità spetta ai figli:»
    - **almeno una di queste:**
      - *controllato:* età meno di 18
        > «se di età inferiore ai 18 anni o se inabili al lavoro;»
      - *da verificare a mano:* Figlio inabile al lavoro: il vocabolario ha la disabilità ma non l'inabilità al lavoro.
      - **tutte queste:** «Per i figli studenti che non lavorano o percepiscono un piccolo reddito da lavoro e sono a carico del genitore al momento della morte, il limite di 18 anni è elevato:»
        - **almeno una di queste:**
          - **tutte queste:** «a 21 anni, in caso di frequenza di scuola media o professionale;»
            - *controllato:* età meno di 21
            - *controllato:* iscrizione a un corso: scuola superiore
          - **tutte queste:** «a 26 anni, in caso di frequenza dell’Università.»
            - *controllato:* età meno di 26
            - *controllato:* iscrizione a un corso: università
        - *da verificare a mano:* Lo studente non deve lavorare o deve percepire solo un piccolo reddito da lavoro: la scheda non indica la soglia.
- *da verificare a mano:* La pensione dell'assicurato deceduto deve essere calcolata con il sistema retributivo o misto: manca il campo.
  > «la cui pensione è calcolata con il sistema retributivo o misto»
- *da verificare a mano:* Alla morte dell'assicurato deve risultare versato o accreditato almeno un anno di contribuzione nella relativa gestione: manca il campo sulla contribuzione del defunto.
  > «risulti versato o accreditato almeno un anno di contribuzione nella relativa gestione»
- *da verificare a mano:* Domanda entro un anno dalla data della morte dell'assicurato, pena la decadenza: manca il campo sulla data del decesso.
  > «La domanda deve essere presentata entro un anno dalla data della morte dell’assicurato, pena il decadimento del diritto.»

**Note:** "Scuola media o professionale" è letta come scuola secondaria superiore, l'unica del vocabolario compatibile con il limite di 21 anni. · I limiti di 21 e 26 anni sono scritti come età inferiore, per analogia con "età inferiore ai 18 anni".

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 17. Indennità una tantum ai superstiti

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.indennit-una-tantum-ai-superstiti-50620.indennit-una-tantum-ai-superstiti.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-indennita-una-tantum-ai-superstiti`

**Requisiti della regola:**

- *controllato:* situazioni particolari: sono vedovo/a od orfano/a di un lavoratore o pensionato
  > «È rivolta ai familiari degli assicurati deceduti»
- *da verificare a mano:* Il trattamento pensionistico dell'assicurato deceduto sarebbe stato liquidato esclusivamente con il sistema contributivo: manca il campo.
  > «il cui trattamento pensionistico sarebbe stato liquidato esclusivamente secondo il sistema contributivo»
- *da verificare a mano:* Mancano i requisiti assicurativi e contributivi dell'assicurato per la pensione indiretta ai superstiti: manca il campo sulla contribuzione del defunto.
  > «mancano i requisiti assicurativi e contributivi per la pensione indiretta;»
- *da verificare a mano:* Non avere diritto a rendite per infortunio sul lavoro o malattia professionale in conseguenza della morte dell'assicurato: manca il campo.
  > «non si ha diritto a rendite per infortunio sul lavoro o malattia professionale in conseguenza della morte dell'assicurato;»
- *da verificare a mano:* Condizioni reddituali alla data del decesso previste dall'art. 3, comma 6, legge 335/1995: la scheda non riporta la soglia.
  > «ci sono le condizioni reddituali alla data del decesso dell’assicurato, di cui all'articolo 3, comma 6, legge 335/1995;»
- *da verificare a mano:* Non avere diritto alla pensione supplementare indiretta: manca il campo.
  > «non si ha diritto alla pensione supplementare indiretta»

**Note:** I superstiti sono quelli individuati per la pensione ai superstiti, che la scheda non elenca: la situazione superstite è usata come approssimazione.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 18. Contributo a fondo perduto per i consumatori che accedono alle procedure di sovraindebitamento

- **Link:** https://www.irfis.it/contributo-a-fondo-perduto-per-i-consumatori-che-accedono-alle-procedure-di-sovraindebitamento/
- **Ente:** IRFIS FinSicilia · **origine:** estratta · **date:** nessuna data · **file:** `irfis-contributo-a-fondo-perduto-per-i-consuma-623bed`

**Requisiti della regola:**

- *controllato:* regione di residenza: Sicilia
  > «D.lgs. 12/01/2019 n. 14 , residente in Sicilia, che propone per il tramite di un»
- *da verificare a mano:* Essere un consumatore sovraindebitato ai sensi dell'art. 2, comma 1, lettera e) del D.Lgs. 14/2019: manca un campo sulla situazione di sovraindebitamento.
  > «Destinatari Consumatore sovraindebitato come definito dall’art. 2, comma 1, lettera e) del»
- *da verificare a mano:* Proporre, tramite un Organismo di Composizione della Crisi, una procedura di ristrutturazione dei debiti, di liquidazione controllata o di esdebitazione del debitore incapiente: manca un campo sulle procedure di sovraindebitamento avviate.
  > «Organismo di Composizione della Crisi una procedura di ristrutturazione dei»
- *controllato:* ISEE al massimo 40.000
  > «comprovata, attestata dalla certificazione ISEE non superiore a euro 40.000,00,»

**Note:** La domanda all'IRFIS la presenta l'OCC per conto del debitore; la procedura è a sportello fino a esaurimento delle risorse, senza date di apertura e chiusura indicate. · Il deposito della domanda in Tribunale entro 180 giorni e l'ottenimento del decreto di ammissione (o della sentenza di apertura della liquidazione o del decreto di esdebitazione) sono condizioni di validità e di erogazione successive alla richiesta: non sono state modellate come requisiti di partenza. · I requisiti dell'OCC (iscrizione al registro, almeno 8 gestori residenti in Sicilia, polizza assicurativa) riguardano l'organismo, non il debitore. · Il limite de minimis vale 'ove applicabile' e riguarda il cumulo con altre agevolazioni: non modellato.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 19. Detrazione IRPEF del 19% dell'affitto per gli studenti universitari fuori sede (spesa fino a 2.633 euro)

- **Link:** https://www.agenziaentrate.gov.it/portale/documents/20143/5629825/Detrazioni+per+canoni+di+locazione_tabella_aggiornata.pdf/f76fe2b8-ecab-9d12-1986-752885a8b95a
- **Ente:** Agenzia delle Entrate · **origine:** estratta · **date:** nessuna data · **file:** `entrate-detrazioni-affitto-2026-fuori-sede`

**Requisiti della regola:**

- *controllato:* iscrizione a un corso: università
  > «Studenti universitari fuori sede»
- *controllato:* domicilio in un altro comune: sì
  > «l’Università sia ubicata in un Comune diverso da quello in cui lo studente ha la propria residenza»
- *da verificare a mano:* L'università deve essere ad almeno 100 km dal comune di residenza e in un'altra provincia, e l'alloggio nel comune dell'università o in uno vicino: il questionario non conosce le distanze.
  > «distante da quest’ultimo almeno 100 chilometri, sito in un’altra provincia rispetto a quella di residenza.»
- *da verificare a mano:* Contratto secondo la Legge 431/1998, oppure di ospitalità o assegnazione con enti per il diritto allo studio, università, collegi o enti senza fini di lucro; la sublocazione è esclusa.
  > «La detrazione (esclusa per la sublocazione) compete a condizione»

**Note:** Il contratto può essere intestato ai genitori, che allora fanno la detrazione per il figlio a carico. Spetta per intero fino a 120.000 euro di reddito complessivo di chi la chiede e si azzera a 240.000 euro: per questo il reddito non è fra i requisiti. · Importo: 19% dei canoni pagati, su una spesa massima di 2.633 euro per contribuente.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 20. Congedo di paternità obbligatorio

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.congedo-di-paternit-obbligatorio-58988.congedo-di-paternit-obbligatorio.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-congedo-di-paternita-obbligatorio`

**Requisiti della regola:**

- *controllato:* situazione lavorativa: lavoro
  > «Il padre o la madre intenzionale devono essere titolari di un rapporto di lavoro dipendente.»
- *controllato:* tipo di lavoro: dipendente
  > «Il padre o la madre intenzionale devono essere titolari di un rapporto di lavoro dipendente.»
- *controllato:* mesi dalla nascita o dall'ingresso del figlio meno di 5
  > «due mesi prima la data presunta del parto fino ai cinque mesi successivi alla nascita»
- *da verificare a mano:* Deve essere il padre (anche adottivo o affidatario) oppure la madre intenzionale in una coppia di donne registrate come genitori: il vocabolario non ha il ruolo di genitore né il sesso.
  > «i padri lavoratori dipendenti, privati e pubblici, anche adottivi e affidatari; le madri intenzionali in una coppia di donne che risultano genitori nei registri dello stato civile.»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 21. Assegno di maternità dei Comuni

- **Link:** https://www.inps.it/it/it/dettaglio-approfondimento.schede-informative.assegno-di-maternit--dei-comuni.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-assegno-maternita-comuni`

**Requisiti della regola:**

- **almeno una persona del nucleo:** «Il diritto all'assegno, nei casi di parto, adozione o affidamento preadottivo»
  - *controllato:* figlio: sì
  - *controllato:* età meno di 18
- *controllato:* mesi dalla nascita o dall'ingresso del figlio meno di 6
  > «entro sei mesi dalla nascita del bambino o dall'effettivo ingresso in famiglia del minore adottato o in affido preadottivo»
- *controllato:* residenza in Italia: sì
  > «spetta a cittadini residenti italiani, comunitari o stranieri in possesso di titolo di soggiorno»
- **almeno una di queste:** «per la specifica della tipologia di permesso di soggiorno utile per la concessione del beneficio è necessario rivolgersi al proprio comune di residenza»
  - *controllato:* cittadinanza: italiana, di un altro paese dell'unione europea
  - *da verificare a mano:* Stranieri con titolo di soggiorno: la scheda non dice quali permessi sono validi e rimanda al comune di residenza.
- *da verificare a mano:* Limiti di reddito: la scheda non riporta la soglia (fissata annualmente).
  > «L'assegno spetta solo entro determinati limiti di reddito.»
- *da verificare a mano:* Assenza di copertura previdenziale o copertura entro un importo fissato annualmente: manca il campo e la scheda non riporta l'importo.
  > «I richiedenti non devono avere alcuna copertura previdenziale oppure devono averla entro un determinato importo fissato annualmente.»
- *da verificare a mano:* Non essere già beneficiari di altro assegno di maternità INPS (legge 488/1999): manca il campo.
  > «non devono essere già beneficiari di altro assegno di maternità INPS ai sensi della legge 23 dicembre 1999, n. 488»

**Note:** Il termine di sei mesi dalla nascita o dall'ingresso in famiglia è trattato come requisito perché, scaduto, la domanda non è più possibile. · La condizione sul figlio (minore nato, adottato o in affido preadottivo) è resa con figlio vero ed eta < 18; la scheda non distingue chi tra madre e padre può chiedere. · La non cumulabilità con altri trattamenti previdenziali (salvo quota differenziale) è una regola di cumulo e non è stata trattata come requisito, se non nella parte sulla copertura previdenziale.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 22. Assegno di maternità dello Stato

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.assegno-di-maternit-dello-stato-50580.assegno-di-maternit-dello-stato.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-assegno-maternita-stato`

**Requisiti della regola:**

- *controllato:* residenza in Italia: sì
  > «la residenza in Italia al momento della nascita del bambino»
- **almeno una di queste:** «Il diritto è riconosciuto anche ai cittadini extracomunitari che siano:»
  - *controllato:* cittadinanza: italiana, di un altro paese dell'unione europea, familiare di un cittadino ue, con diritto di soggiorno, extra ue, con permesso di lungo periodo
  - *da verificare a mano:* Altri titoli di soggiorno ammessi solo a precise condizioni.
- *controllato:* mesi dalla nascita o dall'ingresso del figlio meno di 6
  > «La domanda deve essere presentata entro sei mesi:»
- *da verificare a mano:* Contributi della madre o del padre: condizioni diverse per lavoratrici, disoccupate, adozioni, affidi.
  > «Per la madre sono previsti i seguenti requisiti:»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 23. Avviso pubblico 2026 per il contributo del Fondo Inquilini Morosi Incolpevoli

- **Link:** https://www.comune.napoli.it/novita/avviso-pubblico-2026-per-laccesso-al-contributo-di-cui-al-fondo-inquilini-morosi-incolpevoli/
- **Ente:** Comune di Napoli · **origine:** estratta · **date:** apertura 2026-05-30, chiusura 2026-12-31 · **file:** `napoli-morosi-incolpevoli-2026`

**Requisiti della regola:**

- *controllato:* abitazione: in affitto
  > «Gli inquilini privati morosi»
- *controllato:* comune di residenza: Napoli
  > «mediante piattaforma informatica del Comune di Napoli»
- *da verificare a mano:* Morosità incolpevole nel pagamento del canone verso un locatore privato: mancano i campi sulla morosità e sulle sue cause.
  > «accedere al Fondo destinato agli Inquilini Morosi Incolpevoli»
- *da verificare a mano:* Gli altri requisiti e condizioni sono nell'avviso allegato in PDF, che la pagina non riporta.
  > «in possesso dei requisiti e nelle condizioni di seguito descritte»

**Note:** La pagina web non elenca i requisiti: rimanda all'Avviso pubblico rettificato (PDF allegato), che non è nel testo. ISEE, reddito, cittadinanza, contratto registrato, sfratto ecc. vanno letti lì. · La pagina non dice in modo esplicito che il contributo è riservato ai residenti di Napoli: il requisito sul comune è dedotto dal fatto che l'avviso è del Comune di Napoli per gli inquilini (citazione debole, da verificare sul PDF). · Le domande si presentano dal 30 maggio al 31 dicembre 2026 sulla piattaforma https://bandisociali.comune.napoli.it/ con SPID, CIE o CNS, procedura a sportello (Linee Guida Regionali, DGR n. 26 del 24/01/2023).

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 24. Indennità per riposi giornalieri per padri e madri dipendenti

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.50581.indennit-per-riposi-giornalieri-per-padri-e-madri-dipendenti.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-indennita-per-riposi-giornalieri-per-padri-e`

**Requisiti della regola:**

- *controllato:* situazione lavorativa: lavoro
  > «avere un valido rapporto di lavoro in corso»
- *controllato:* tipo di lavoro: dipendente
  > «Si rivolge alle lavoratrici e ai lavoratori dipendenti»
- *da verificare a mano:* Sono escluse le lavoratrici domestiche e a domicilio: il vocabolario non permette di escludere una situazione particolare né distingue il lavoro a domicilio.
  > «Le lavoratrici domestiche e a domicilio non hanno diritto ai riposi giornalieri.»
- **almeno una persona del nucleo:** «il minore deve essere vivente»
  - *controllato:* figlio: sì
- *controllato:* mesi dalla nascita o dall'ingresso del figlio meno di 12
  > «durante il primo anno di vita o, in caso di adozione o affidamento, entro il primo anno dall’ingresso in famiglia del minore»
- *da verificare a mano:* Il padre ne ha diritto solo se la madre è deceduta o gravemente inferma, oppure se la madre è lavoratrice dipendente e rinuncia o non ha diritto ai riposi; non se la madre non è lavoratrice o è in astensione, aspettativa o permessi non retribuiti: mancano i campi sul genere del richiedente e sulla situazione dell'altro genitore.
  > «può richiedere il riposo giornaliero in alternativa alla madre lavoratrice dipendente che rinuncia o non ha diritto ai riposi»
- *da verificare a mano:* La domanda va presentata prima dell'inizio del periodo di riposo e comunque entro l'anno di prescrizione: manca la data di inizio del riposo.
  > «La domanda va presentata prima dell'inizio del periodo di riposo giornaliero e comunque non oltre l’anno di prescrizione.»

**Note:** La durata dei riposi (una o due ore, raddoppio per parto plurimo, dimezzamento con asilo nido aziendale) incide solo su quanto spetta, non sul diritto. · Sono inclusi i lavoratori naviganti, marittimi e dell'aviazione civile ex IPSEMA, che rientrano tra i dipendenti.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 25. Assegno sociale

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.assegno-sociale-50184.assegno-sociale.html
- **Ente:** INPS · **origine:** riferimento · **date:** nessuna data · **file:** `inps-assegno-sociale`

**Requisiti della regola:**

- *controllato:* età almeno 67
  > «Per ottenere l'Assegno, tutti i cittadini italiani e stranieri devono soddisfare i seguenti requisiti: 67 anni di età»
- *controllato:* residenza in Italia: sì
  > «residenza effettiva in Italia»
- *controllato:* anni di residenza continuativa in Italia almeno 10
  > «requisito dei dieci anni di soggiorno legale e continuativo in Italia»
- *controllato:* cittadinanza: italiana, di un altro paese dell'unione europea, familiare di un cittadino ue, con diritto di soggiorno, extra ue, con permesso di lungo periodo, protezione internazionale (rifugiato o sussidiaria)
  > «ai cittadini italiani; ai cittadini comunitari iscritti all'Anagrafe del comune di residenza; ai cittadini extracomunitari familiari di cittadino comunitario (articolo 19, commi 2 e 3, decreto legislativo 30/2007); ai cittadini extracomunitari titolari di permesso di soggiorno UE per soggiornanti di lungo periodo e ai cittadini stranieri o apolidi titolari dello status di rifugiato politico o di protezione sussidiaria.»
- *da verificare a mano:* Reddito annuo sotto 7.101,12 euro (non coniugati) o reddito cumulato col coniuge sotto 14.202,24 euro (coniugati): mancano lo stato civile e il reddito del coniuge, e il reddito che conta qui (compresi redditi esenti, pensioni estere, prestazioni assistenziali) non coincide con reddito_richiedente (IRPEF).
  > «Il soggetto richiedente deve avere un reddito annuo inferiore a 7.101,12 euro se non coniugato, elevato a 14.202,24 euro se è coniugato.»

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 26. Assegno per il Nucleo Familiare ai pensionati

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.assegno-per-il-nucleo-familiare-ai-pensionati-53730.Assegno-per-il-Nucleo-Familiare-ai-Pensionati.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-assegno-per-il-nucleo-familiare-ai-pensionati`

**Requisiti della regola:**

- *controllato:* situazione lavorativa: sono in pensione
  > «titolari di pensione derivante da lavoro dipendente»
- *da verificare a mano:* La pensione deve derivare da lavoro dipendente; non spetta ai pensionati delle gestioni speciali degli autonomi: manca il tipo di pensione.
  > «Non spetta ai titolari di pensione a carico delle Gestioni speciali dei lavoratori autonomi»
- *da verificare a mano:* Dal 1° marzo 2022 non spetta ai nuclei con figli: il vocabolario non permette di dire che nessun componente è un figlio.
  > «limitatamente ai nuclei familiari con figli e orfanili»
- *da verificare a mano:* Almeno il 70% del reddito del nucleo deve venire da pensione o lavoro dipendente: manca la composizione del reddito.
  > «per almeno il 70%, da reddito derivante da prestazione pensionistica da lavoro dipendente»
- *da verificare a mano:* Il reddito del nucleo deve stare sotto fasce stabilite ogni anno per legge, che non sono nella scheda.
  > «che abbiano un reddito complessivo al di sotto delle fasce stabilite ogni anno per legge»

**Note:** Dal 1° marzo 2022 il nucleo comprende il richiedente, il coniuge o la parte di unione civile non separati, e fratelli, sorelle e nipoti orfani minori o inabili.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 27. Pensione di inabilità

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.pensione-di-inabilit--50297.pensione-di-inabilit-.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-pensione-di-inabilita`

**Requisiti della regola:**

- *controllato:* disabilità: sì
  > «a causa di infermità o difetto fisico o mentale»
- *da verificare a mano:* Assoluta e permanente impossibilità di svolgere qualsiasi attività lavorativa, valutata dalla Commissione Medica Legale dell'INPS: il vocabolario ha solo disabilità e percentuale di invalidità.
  > «La pensione di inabilità viene concessa in presenza di assoluta e permanente impossibilità di svolgere qualsiasi attività lavorativa»
- *da verificare a mano:* Almeno 260 contributi settimanali (cinque anni), di cui 156 nel quinquennio precedente la domanda, come lavoratore dipendente, autonomo o iscritto alla Gestione Separata: il campo disponibile conta solo le settimane degli ultimi 4 anni.
  > «di almeno 260 contributi settimanali (cinque anni di contribuzione) di cui 156 (tre anni di contribuzione) nel quinquennio precedente la data di presentazione della domanda»
- *da verificare a mano:* Cessazione di qualsiasi attività lavorativa, cancellazione da elenchi anagrafici degli operai agricoli, elenchi dei lavoratori autonomi e albi professionali, rinuncia ai trattamenti di disoccupazione e sostitutivi della retribuzione: mancano i campi.
  > «la cessazione di qualsiasi tipo di attività lavorativa;»

**Note:** La pensione privilegiata di inabilità, per i soli iscritti all'AGO dei lavoratori dipendenti con inabilità dovuta al servizio, è una variante con condizioni proprie, non modellata come requisito separato.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 28. Pensione di inabilità in regime di totalizzazione

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.50624.pensione-di-inabilit-in-regime-di-totalizzazione.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-pensione-di-inabilita-in-regime-di-totalizzaz`

**Requisiti della regola:**

- *controllato:* disabilità: sì
  > «viene accertata l'assoluta e permanente impossibilità di svolgere qualsiasi attività lavorativa»
- *da verificare a mano:* Riconoscimento dello stato di assoluta e permanente impossibilità a svolgere qualsiasi attività lavorativa: la scheda non lo traduce in una percentuale di invalidità.
  > «viene riconosciuto lo stato di assoluta e permanente impossibilità a svolgere qualsiasi attività lavorativa.»
- *da verificare a mano:* Contributi versati in più Casse, Gestioni o Fondi previdenziali: manca il campo.
  > «hanno versato contributi in diverse Casse, Gestioni o Fondi previdenziali»
- *da verificare a mano:* Requisiti di assicurazione e di contribuzione, che la scheda non quantifica.
  > «vengono rispettati i requisiti di assicurazione e di contribuzione;»

**Note:** Non si vincola la condizione lavorativa attuale: la scheda parla di lavoratori dipendenti, autonomi, Gestione Separata e liberi professionisti in base ai contributi versati, e si rivolge anche ai titolari di assegno ordinario di invalidità.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---

## 29. Pensione di vecchiaia in regime di totalizzazione

- **Link:** https://www.inps.it/it/it/dettaglio-scheda.it.schede-servizio-strumento.schede-servizi.50305.pensione-di-vecchiaia-in-regime-di-totalizzazione.html
- **Ente:** INPS · **origine:** estratta · **date:** nessuna data · **file:** `inps-pensione-di-vecchiaia-in-regime-di-totalizzaz`

**Requisiti della regola:**

- *da verificare a mano:* Aver versato contributi in diverse casse, gestioni o fondi previdenziali come lavoratore dipendente, autonomo o libero professionista: manca il campo.
  > «che hanno versato contributi in diverse casse, gestioni o fondi previdenziali»
- *controllato:* età almeno 65
  > «raggiungimento di 65 anni di età, sia per gli uomini sia per le donne;»
- *da verificare a mano:* Anzianità contributiva complessiva di almeno 20 anni (1.040 contributi settimanali): manca il campo sugli anni di contribuzione.
  > «anzianità contributiva complessiva di almeno 20 anni (1.040 contributi settimanali);»
- *da verificare a mano:* Ulteriori requisiti previsti dai singoli ordinamenti per la pensione di vecchiaia (cessazione del rapporto di lavoro, cancellazione dall'albo professionale, ecc.): mancano i campi.
  > «sussistenza degli ulteriori requisiti, diversi da quelli di età e anzianità contributiva»
- *da verificare a mano (eccezione rara):* La totalizzazione è preclusa se la pensione di vecchiaia deriva dalla trasformazione dell'assegno ordinario di invalidità: manca il campo.
  > «La totalizzazione è preclusa in caso di trasformazione dell’assegno ordinario di invalidità in pensione di vecchiaia.»

**Note:** Dal 1° gennaio 2013 il requisito di 65 anni è adeguato alla speranza di vita, ma la scheda non dice il valore attuale: 65 anni è solo il minimo scritto.

**Esito:** giusta / errori piccoli / sbagliata — nota:

---
