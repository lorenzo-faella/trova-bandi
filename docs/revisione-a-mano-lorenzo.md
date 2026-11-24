# Revisione a mano: la metà di Lorenzo (13 regole)

*Dalle schede di `docs/revisione-a-mano-schede.md` (numeri della lista in `docs/da-rivedere-a-mano.md`). Divisione incrociata: nessuno rivede una regola che ha scritto. L'altra metà è in `docs/revisione-a-mano-edoardo.md`. Per ogni regola: aprire il link, confrontare requisiti, citazioni e date con il bando, segnare l'esito (giusta / errori piccoli / sbagliata) e una nota se serve. Niente LLM nel giudizio (decisione 97).*

*Scambio del 24/11: la 8 (Comune di Milano, PDF salvato a mano da Edoardo) passa a Edoardo, la 16 a Lorenzo.*

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

**Esito:** giusta

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

**Esito:** giusta 

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

**Esito:** giusta, nota:"la pagina non dice quali e manca il campo."

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

**Esito:** giusta,  nota: 'non è superiore a 9.796 euro' corretto, si riferisce all'ISEE

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

**Esito:** giusta 

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

**Esito:** giusta - nota: "Il minore deve essere figlio, orfano o equiparato di un dipendente o pensionato della pubblica amministrazione iscritto alla Gestione Unitaria: nel vocabolario non c'è un campo sul lavoro pubblico." corretto
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

**Esito:** giusta 

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

**Esito:** giusta 

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

**Esito:** giusta

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

**Esito:** giusta

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

**Esito:** giusta 

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

**Esito:** giusta 

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

**Esito:** sbagliata: sul pdf https://static-www.comune.napoli.it/wp-content/uploads/2026/03/All_01_1121I_29042026_356-signed.pdf scaricabile iin fondo alla pagina sono presenti tutti i requisiti

---

