# Vocabolario del profilo persona

**Da rivedere insieme.** Questi sono gli unici dati che il motore può chiedere a una persona, e sono scritti nello schema (`schema/regola.schema.json`). Tutti i requisiti estratti devono usare questi campi. Quello che non ci sta diventa `non_modellabile`, cioè "da verificare". Un campo non è aggiunto finché almeno una regola non lo usa.

Ogni domanda ammette "non lo so": l'esito diventa "mancano dati", mai un no.

## Il richiedente

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `cittadinanza` | Qual è la tua cittadinanza o il tuo titolo di soggiorno? | `italiana`, `ue`, `familiare_con_diritto_soggiorno`, `extra_ue_lungo_periodo`, `protezione_internazionale`, `apolide`, `altro_titolo`, `nessun_titolo` | ADI, Assegno unico, maternità |
| `permesso_casi_speciali` | Hai un permesso per "casi speciali" (art. 18, 18-bis, 18-ter TUI)? | sì/no | ADI |
| `residente_italia` | Risiedi in Italia? | sì/no | Assegno unico, maternità |
| `anni_residenza_italia` | Da quanti anni risiedi in Italia, in totale? | numero | ADI |
| `anni_residenza_continuativa_italia` | Da quanti anni senza interruzioni? | numero | ADI |
| `anni_residenza_regione` | Da quanti anni risiedi nella tua regione? | numero | decisione 50 |
| `mesi_validita_permesso` | (solo se la cittadinanza non è italiana né UE) Per quanti mesi è valido il tuo permesso di soggiorno, in totale? | numero | decisione 50 |
| `disabile` | Hai una disabilità? (anche per i componenti del nucleo, sotto) | sì/no | decisione 50 |
| `percentuale_invalidita` | (solo se hai una disabilità) Percentuale di invalidità riconosciuta? | numero | decisione 50 |
| `lavora_in_italia` | Lavori in Italia? | sì/no | Assegno unico |
| `soggetto_irpef_italia` | Paghi le imposte sul reddito in Italia? | sì/no | Assegno unico |
| `condizione_lavorativa` | Qual è la tua situazione lavorativa? | `occupato`, `disoccupato`, `studente`, `pensionato`, `inattivo` | NASpI |
| `tipo_lavoro` | (solo se occupato) Lavori come dipendente, autonomo o collaboratore (Gestione Separata)? | `dipendente`, `autonomo`, `parasubordinato` | decisione 41 |
| `reddito_richiedente` | (solo se occupato o pensionato) Il tuo reddito complessivo IRPEF dell'anno scorso? | euro | decisione 41 |
| `ultimo_lavoro_subordinato` | Il tuo ultimo lavoro era da dipendente? | sì/no | NASpI |
| `causa_fine_lavoro` | Come è finito? | `licenziamento`, `fine_contratto`, `dimissioni`, `dimissioni_giusta_causa`, `dimissioni_periodo_tutelato`, `risoluzione_consensuale`, `risoluzione_consensuale_tutelata` | NASpI |
| `giorni_da_cessazione_lavoro` | Quanti giorni fa è iniziato il termine (di solito la fine del lavoro)? | numero | NASpI |
| `settimane_contributi_4_anni` | Quante settimane di contributi hai negli ultimi 4 anni? | numero | NASpI |
| `giorni_da_evento_figlio`, `mesi_da_evento_figlio` | Quando è nato o entrato in famiglia il figlio? | una data, da cui si ricavano entrambi. I mesi sono quelli interi già compiuti, quindi un termine di N mesi si scrive `< N`: chi ha compiuto N mesi è già oltre. Un termine di N giorni si scrive `<= N` | Nuovi nati, maternità |

## Studio

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `titolo_di_studio` | Il titolo di studio più alto che hai? | `nessuno`, `licenza_media`, `diploma`, `laurea_triennale`, `laurea_magistrale`, `master`, `dottorato` | decisione 50 |
| `iscrizione` | Sei iscritto (o ti stai iscrivendo) a un corso? | `universita`, `afam`, `its`, `scuola_superiore`, `nessuna` | decisione 50 |
| `anno_di_corso` | (solo se università, AFAM o ITS) A che anno sei iscritto? | numero | decisione 50 |
| `fuori_corso_o_ripetente` | (solo se università o AFAM) Sei fuori corso o ripetente? | sì/no | decisione 50 |
| `crediti_conseguiti` | (solo se università o AFAM, dal secondo anno) Quanti crediti (CFU) hai conseguito finora? | numero | decisione 50 |
| `isee_universitario` | (solo se università o AFAM) Il tuo ISEE per le prestazioni per il diritto allo studio universitario? | euro | decisione 50 |
| `ispe` | (solo se università o AFAM) L'ISPE (situazione patrimoniale equivalente) scritto sull'attestazione ISEE? | euro | decisione 50 |

## La casa

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `abitazione` | La casa in cui vivi è…? | `affitto`, `proprieta`, `altro` | decisione 50 |
| `contratto_locazione_registrato` | (solo se in affitto) Hai un contratto di affitto registrato a tuo nome o di un familiare? | sì/no | decisione 50 |
| `canone_annuo` | (solo se in affitto) Quanto paghi di affitto in un anno, senza le spese? | euro | decisione 50 |
| `mutuo_prima_casa` | (solo se di proprietà) Hai un mutuo in corso per la prima casa? | sì/no | decisione 50 |
| `proprieta_altra_abitazione` | Tu o un familiare del nucleo possedete un'altra casa adatta al nucleo? | sì/no | decisione 50 |

## La situazione economica

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `isee` | Qual è il tuo ISEE? | euro | ADI, Nuovi nati |
| `patrimonio_immobiliare` | Valore degli immobili, esclusa la casa di abitazione? | euro | ADI |
| `veicoli_esclusi` | Qualcuno in famiglia ha auto oltre 1.600 cc o moto oltre 250 cc immatricolate negli ultimi 36 mesi, oppure barche o aerei? | sì/no | ADI |

## Ogni componente del nucleo (`nucleo`)

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `eta` | Età | numero | ADI, Assegno unico |
| `disabile` | Ha una disabilità? | sì/no | ADI, Assegno unico |
| `svantaggio_certificato` | È seguito da servizi socio-sanitari per una condizione di svantaggio? | sì/no | ADI |
| `figlio_a_carico` | È un figlio a carico? | sì/no | Assegno unico |
| `figlio` | È tuo figlio (anche adottivo o in affido), che sia a carico o no? | sì/no | decisione 50 |
| `reddito_annuo` | Reddito annuo | euro | Assegno unico |
| `attivita` | Cosa fa? | `studio`, `tirocinio_o_lavoro`, `disoccupato_cpi`, `servizio_civile`, `nessuna` | Assegno unico |

`numero_figli` (numero) non si chiede: si conta dai componenti con `figlio` vero. Serve per i requisiti come "almeno tre figli", che le condizioni su un componente alla volta non riescono a scrivere.

**Questionario adattivo.** Le domande con "(solo se …)" si fanno solo dopo la risposta che le apre: chi non è iscritto all'università non vede le domande su crediti e ISEE universitario. L'elenco completo, con le condizioni, è in `data/domande_persone.yaml`, che userà l'applicazione.

`regione` e `comune` sono gli stessi campi delle imprese, ma nessuna delle 5 regole di prova li usa ancora.

## Scelte da discutere

1. **Niente dati giudiziari.** Condanne e misure cautelari non vengono chieste: diventano "da verificare". Peggiora l'esito dell'ADI, ma è una domanda che un servizio del genere non dovrebbe fare.
2. **Dati sensibili.** ISEE, reddito, disabilità e composizione della famiglia non vanno salvati: il profilo deve restare nel browser.
3. **Molti non conoscono il proprio ISEE.** Potremmo chiedere una fascia invece del numero, oppure proporre una stima. Da decidere con la demo.
4. **Unità della data.** Il questionario chiederà una data sola e calcolerà giorni e mesi: i due campi restano separati perché le schede usano termini diversi.
