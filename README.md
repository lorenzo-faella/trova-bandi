# trova-bandi

Progetto di Lorenzo Faella ed Edoardo Salvatore Russo per Software Engineering 20875, Bocconi. Consegna: 27 novembre 2026.

Il servizio raccoglie fonti sugli aiuti pubblici italiani e confronta un profilo con requisiti rappresentati come regole a tre valori: soddisfatto, non soddisfatto, non determinabile. Il questionario cerca le informazioni ancora utili. Una citazione autentica dimostra che il passaggio esiste nella fonte; non certifica che la regola sia completa o corretta.

**Stato del 21 novembre 2026, completamento successivo:** [registro aggiornato dei 27 rilievi e prove](docs/completamento-2026-11-21/LEGGIMI.md). Conservati il checkpoint `cc097ba`, i 164 bandi imprese delle decisioni 87–88 e il successivo commit `8cf8088` con sei documenti persone (decisione 89). Registro: 16 risolti, 10 mitigati, A23 ancora aperto per adjudicazione normativa. Il [rapporto del checkpoint](docs/verifica-2026-11-21/LEGGIMI.md) e l’audit originale restano prove storiche separate.

**Rettifiche economiche successive:** [fonti, 17 rettifiche e regressioni](docs/verifica-economia-2026-11-21/LEGGIMI.md). ISCRO usa la soglia 2026 di 12.749,18 euro sul reddito autonomo dell’anno precedente; la pensione di inabilità distingue prima liquidazione e successive. Separati periodi fiscali e tipi ISEE per le altre misure interessate. Censiti 146 confronti in 98 regole, con controllo semantico mirato: non è una certificazione normativa dell’intero corpus. Gold originale preservato.

## Perimetro della demo

- **Persone:** 336 regole caricate, di cui 16 di riferimento e 320 estratte. La provenienza da un'etichetta o da una regola scritta a mano non equivale a una revisione umana documentata. Le estratte compatibili restano accompagnate dalla riserva di interpretazione e completezza.
- **Date:** apertura secondo le date registrate, chiusura, futuro, sportello permanente documentato e disponibilità non verificata sono stati distinti. Date assenti non provano un'apertura; la data di valutazione non è l'aggiornamento della fonte. Il Bonus psicologo non viene presentato come aperto nel 2026 sulla base della finestra 2025.
- **Imprese:** filtri del catalogo su territorio, soggetto, dimensione, settore, ATECO e ambito. L'esito favorevole riguarda questi filtri: non verifica tutti i requisiti economici o amministrativi del bando. L'export locale è del 27 ottobre 2026. I 164 documenti aggiunti sono conservati; nessuna regione è aggiunta dal solo ente. Al 21/11 sono valutate 831 regole imprese: 533 aperte secondo le date rappresentate, 293 con disponibilità non verificata e 5 future. Questi stati non provano risorse ancora disponibili.
- Il territorio dell'ente è un indizio di pertinenza. Sono possibili requisiti su immobile, lavoro, futura sede o corso: la provenienza geografica non dimostra esclusione.
- Compatibilità dei requisiti, possibilità di presentare domanda, graduatoria e assegnazione effettiva sono verifiche distinte. L'assenza di una misura dal catalogo non esclude un diritto.

NASpI distingue situazione attuale, rapporto terminato e lavori rimasti. Comprende domande sulle categorie escluse, disponibilità al lavoro, precedenti cessazioni volontarie e settimane successive. La prevalenza contributiva agricola viene chiesta sui quattro anni o sugli ultimi 12 mesi. Il reddito annuo presunto autonomo è distinto dall’IRPEF passato; comunicazioni e riduzioni restano esplicite. Per part-time/misti resta una verifica del limite dell’anno, senza estendere automaticamente un importo del 2024 al 2026. Le eccezioni da trasferimento della circolare 98/2025 sono esplicitate. ADI distingue auto/moto non agevolate da barche e aerei. Le condizioni non rappresentate restano visibili.

Il duplicato dei buoni scuola toscani usa un'identità esplicita di misura/edizione e conserva la versione precedente. L'ISEE minorenni è distinto dall'ordinario. La misura trentina con requisiti dei tirocinanti e denaro al maestro artigiano è sospesa dal catalogo pubblico con motivazione, senza cancellare la fonte.

## Avvio locale riproducibile

Python 3.12 o successivo. Le dipendenze dichiarate sono state installate e provate in un ambiente nuovo Python 3.14. Il Makefile sceglie `.venv/bin/python`, se esiste, altrimenti `python3`; non contiene un percorso Anaconda personale.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
make dati test
make controlla
make verifica-offline
make demo
```

Aprire [http://127.0.0.1:8000](http://127.0.0.1:8000). `PY=percorso/python` consente di scegliere un interprete diverso. Dopo l'installazione, dati tracciati e piccolo fascicolo di fonti/casi permettono le verifiche offline senza servizi esterni. Il comando predefinito `make` esegue anche la misura imprese storica.

Per fissare il giorno della demo:

```sh
TROVA_BANDI_GIORNO=2026-11-21 make demo
```

La copia pulita è stata avviata rigenerando dati e regole in un ambiente nuovo. Docker e l'infrastruttura pubblicata non sono stati verificati in questa correzione. I file `Dockerfile` e `render.yaml` restano disponibili; non costituiscono una prova di deploy riuscito.

## Questionario, risultati ed esportazioni

Le pagine permettono risposte parziali e un'età non nota per singolo componente. Studio e lavoro possono coesistere; lavoro, assenza di lavoro e inattività non possono essere selezionati contemporaneamente. La parentela non si ricava dalla differenza d'età. Il richiedente e «Tu» condividono età e disabilità.

I comuni sono riconosciuti nell'elenco ISTAT e verificati rispetto alla regione, senza correggere automaticamente refusi. Per nomi omonimi occorre la regione; se non è determinabile si usa «Non lo so». La sede del corso si sceglie con regione e comune anche per gli omonimi, con codice ISTAT. Non identifica automaticamente l'ateneo, la sede legale o uno specifico corso ammesso; ERDIS non esclude dalla sola regione didattica ed ER.GO chiede l'iscrizione postlaurea pertinente.

Gli errori numerici sono indicati accanto al controllo. Errori del server o della rete conservano i valori e permettono di riprovare. Le risposte si possono modificare dal riepilogo; l'invalidazione riguarda i dati dipendenti diventati incoerenti. Nessun account o salvataggio remoto è necessario.

Lista, conteggi ed esportazione usano la classificazione del server. Il calendario non seleziona automaticamente scadenze: si scelgono gli eventi fra i risultati ammessi, con date e pertinenza sufficienti. Gli eventi sono giornalieri e avvertono che l'orario di chiusura non è verificato; includono un promemoria tre giorni prima. La stampa crea un report indipendente da ricerca, paginazione e gruppi chiusi. Il perimetro predefinito comprende i risultati principali non esclusi; è possibile scegliere tutto il catalogo valutato e l'archivio recente. Il report comprende un indice collegato a ogni scheda, senza dipendere da ricerca o paginazione.

Il profilo completo viene inviato al server **a ogni passo**. La demo non salva il corpo delle richieste né il profilo; il browser lo mantiene in memoria nella pagina. Ricaricare perde le risposte. I font remoti sono stati rimossi. Axe-core locale e albero Accessibility di Chrome sono stati controllati in tre stati, con zero violazioni automatiche dopo le correzioni del contrasto; non sostituiscono VoiceOver con utenti. Le verifiche dell'infrastruttura pubblicata e un audit con lettore di schermo restano da fare. La compressione gzip riduce nel benchmark i byte trasferiti dell’83,6%, conservando tutte le spiegazioni.

## Verifiche e metriche

```sh
make test
make controlla                         # schema e citazioni persone/gold/revisioni
python -m pipeline.estrai_documenti controlla data/regole_estratte/documenti
make confronta                         # confronti sintetici e seconda estrazione
python -m scripts.verifica_persone --uscita docs/verifica-economia-2026-11-21
python -m scripts.verifica_economia    # inventario economico e integrità delle rettifiche
python -m scripts.verifica_completamento # integrità delle nuove prove offline
```

Il controllo completo delle citazioni dei documenti richiede le copie originali in `data/raw/documenti/`; le copie non tracciate possono differire fra macchine. Il fascicolo offline contiene un sottoinsieme esplicito di fonti, con impronte. Non dichiariamo verificato offline tutto il corpus.

Accordo sintetico ricalcolato, senza cambiare campioni o etichette: **20% su 8 benefici** estrazione/Edoardo, **8% su 3** Edoardo/Lorenzo, **75% su 9** estrazione/Lorenzo. I denominatori dei casi e i disaccordi sono nei report `docs/test-estrazione*.md` e `docs/accordo-etichette.md`. Non sono accuratezze sui cittadini; il complemento non è una percentuale di errori normativi. Il [fascicolo per l’adjudicazione](docs/completamento-2026-11-21/adjudicazione/LEGGIMI.md) contiene 14 benefici, varianti originali e 42 scenari proposti. Occorrono ancora fonti/allegati mancanti e decisioni motivate dei due autori. L’indicazione utente «da verificare» per co.co.co senza partita IVA è applicata solo alla demo ISCRO e registrata separatamente; nessuna etichetta gold è stata alterata.

Il questionario persone è misurato su otto profili fittizi, inclusi i casi dell'audit, contro un ordine fisso per frequenza dei campi, con gli stessi prerequisiti e criteri di arresto. Domande, informazioni, incertezze ed equivalenza sono in [docs/misura-questionario-persone.md](docs/misura-questionario-persone.md). Il vantaggio osservato è piccolo. Il confronto imprese storico di 6,57 contro 6,58 domande non dimostra una grande riduzione.

Mancano validazione normativa completa, riferimento indipendente adjudicato, utenti reali, misure di abbandono, copertura su inventario indipendente e validazione commerciale. Originalità e impatto sono ipotesi da verificare, non conclusioni sostenute dai soli conteggi di fonti.

## Estrazione e provenienza

```sh
python -m pipeline.estrai api <obiettivi> <uscita>
python -m pipeline.estrai prepara <obiettivi> <lavoro>
python -m pipeline.estrai importa <obiettivi> <lavoro> <uscita>
python -m pipeline.estrai_documenti prepara <lavoro> <id ...>
python -m pipeline.estrai_documenti importa <lavoro> <uscita> <id ...>
```

Le nuove estrazioni registrano separatamente data di estrazione, acquisizione se nota, versione se nota, hash di fonte/schema/prompt, autore o modello dichiarato e snapshot. La revisione umana non viene inventata. Se il prompt originale di un'importazione manca, il relativo hash resta non noto. `ultimo_controllo` nei dati storici non viene retroattivamente reinterpretato come verifica umana. La chiamata all'API LLM reale non è stata verificata: i test usano risposte simulate.

Per raccolta e configurazione delle fonti: `data/fonti/`, `pipeline/fonti/`, `docs/pipeline-per-edo.md` e le decisioni storiche. `make scarica` aggiorna i dati da rete; non è necessario per la riproduzione offline. Le estrazioni senza requisiti restano fuori dal catalogo pubblico: una regola vuota non deve diventare un aiuto assegnabile a chiunque.

## Fonti e documentazione

- incentivi.gov.it, open data IODL 2.0; ISTAT, elenco comuni CC BY 4.0.
- INPS: schede, circolari e comunicati ufficiali; fonti regionali e comunali configurate in `data/fonti/`.
- Nuove prove, fonti mirate e registro finale: `docs/completamento-2026-11-21/`; adjudicazione in attesa degli autori nella sottocartella `adjudicazione/`.
- Snapshot delle verifiche: `data/fonti_verificate/manifest.json`; documenti acquisiti e impronte in `docs/verifica-2026-11-21/fonti/`.
- Registro delle scelte: `docs/decisioni.md`; vocabolario: `docs/vocabolario-persone.md`; confronto servizi: `docs/competitor.md`.
