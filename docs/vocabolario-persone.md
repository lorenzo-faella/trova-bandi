# Vocabolario del profilo persona

**Da rivedere insieme.** Questi sono gli unici dati che il motore può chiedere a una persona, e sono scritti nello schema (`schema/regola.schema.json`). Tutti i requisiti estratti devono usare questi campi. Quello che non ci sta diventa `non_modellabile`, cioè "da verificare". Un campo non è aggiunto finché almeno una regola non lo usa.

Ogni domanda ammette "non lo so": l'esito diventa "mancano dati", mai un no.

## Il richiedente

| Campo | Domanda | Risposta | Usato da |
|---|---|---|---|
| `eta` | (non si chiede: è l'età data per "Tu", il primo componente del nucleo) | numero | decisione 58 |
| `situazioni_particolari` | Ti riguarda una di queste situazioni? (anche più di una) | `dipendente_pubblico`, `genitore_dipendente_pubblico`, `poste_ipost`, `gestione_magistrale`, `superstite`, `forze_ordine`, `lavoro_domestico`, `lavoro_agricolo`, `malattia_tbc`, `nessuna` | decisione 70 |
| `cittadinanza` | Qual è la tua cittadinanza o il tuo titolo di soggiorno? | `italiana`, `ue`, `familiare_con_diritto_soggiorno`, `extra_ue_lungo_periodo`, `protezione_internazionale`, `apolide`, `altro_titolo`, `nessun_titolo` | ADI, Assegno unico, maternità |
| `permesso_casi_speciali` | Hai un permesso per "casi speciali" (art. 18, 18-bis, 18-ter TUI)? | sì/no | ADI |
| `residente_italia` | Risiedi in Italia? | sì/no | Assegno unico, maternità |
| `anni_residenza_italia` | Da quanti anni risiedi in Italia, in totale? | numero | ADI |
| `anni_residenza_continuativa_italia` | Da quanti anni senza interruzioni? | numero | ADI |
| `domicilio_diverso` | Vivi abitualmente in un altro comune, per esempio per studio o lavoro? | sì/no | decisione 71 |
| `regione_domicilio`, `comune_domicilio` | (solo se sì) In che regione e in che comune vivi abitualmente? Se no, sono la regione e il comune di residenza | come `regione` e `comune` | decisione 71 |
| `anni_residenza_regione` | Da quanti anni risiedi nella tua regione? | numero | decisione 50 |
| `mesi_validita_permesso` | (solo se la cittadinanza non è italiana né UE) Per quanti mesi è valido il tuo permesso di soggiorno, in totale? | numero | decisione 50 |
| `disabile` | Hai una disabilità? (anche per i componenti del nucleo, sotto) | sì/no | decisione 50 |
| `percentuale_invalidita` | (solo se hai una disabilità) Percentuale di invalidità riconosciuta? | numero | decisione 50 |
| `lavora_in_italia` | Lavori in Italia? | sì/no | Assegno unico |
| `soggetto_irpef_italia` | Paghi le imposte sul reddito in Italia? | sì/no | Assegno unico |
| `condizione_lavorativa` | Qual è la tua situazione lavorativa? (anche più di una: decisione 69) | `occupato`, `disoccupato`, `studente`, `pensionato`, `inattivo` | NASpI |
| `tipo_lavoro` | (solo se occupato; anche più di una) Lavori come dipendente, autonomo o collaboratore (Gestione Separata)? | `dipendente`, `autonomo`, `parasubordinato` | decisione 41 |
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
| `livello_corso` | (solo se università, AFAM o ITS) Che corso frequenti? | `laurea_triennale`, `laurea_magistrale`, `ciclo_unico`, `dottorato`, `specializzazione`, `master`, `its`, `afam_primo_livello`, `afam_secondo_livello` | decisione 73 |
| `comune_ateneo` | (solo se università, AFAM o ITS) In che comune è la sede del tuo corso? | il nome del comune | decisione 73 |
| `provincia_ateneo`, `regione_ateneo` | (non si chiedono: si ricavano dal comune della sede, con i dati ISTAT) | il nome della provincia (come la chiama l'ISTAT: `Catania`, `Milano`) e della regione | decisioni 70 e 73 |
| `tempo_parziale` | (solo se università o AFAM) Sei iscritto a tempo parziale? | sì/no | decisione 73 |
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

`numero_figli` (numero) non si chiede: si conta dai componenti con `figlio` vero. Serve per i requisiti come "almeno tre figli", che le condizioni su un componente alla volta non riescono a scrivere. Allo stesso modo `numero_componenti` (numero) si conta dai componenti del nucleo, compreso chi risponde: serve per "nuclei di almeno 3 componenti".

**Questionario adattivo.** Le domande con "(solo se …)" si fanno solo dopo la risposta che le apre: chi non è iscritto all'università non vede le domande su crediti e ISEE universitario. L'elenco completo, con le condizioni, è in `data/domande_persone.yaml`, che userà l'applicazione.

`regione` e `comune` sono gli stessi campi delle imprese, ma nessuna delle 5 regole di prova li usa ancora.

**`situazioni_particolari`** (decisione 70) serve ai benefici riservati a gruppi ristretti. Si scrive con l'operatore `interseca` e i valori che il beneficio ammette: per esempio `{campo: situazioni_particolari, operatore: interseca, valori: [superstite]}` per una prestazione ai superstiti. Chi risponde `nessuna` non ha nessuna di queste situazioni. I valori:
- `dipendente_pubblico`: dipendente o pensionato pubblico (Gestione unitaria, ex INPDAP);
- `genitore_dipendente_pubblico`: figlio od orfano di un dipendente o pensionato pubblico;
- `poste_ipost`: dipendente o pensionato di Poste Italiane / ex IPOST, o suo familiare;
- `gestione_magistrale`: iscritto alla Gestione Assistenza Magistrale, o suo familiare;
- `superstite`: coniuge o figlio superstite di un lavoratore o pensionato;
- `forze_ordine`: forze armate, forze di polizia, vigili del fuoco;
- `lavoro_domestico`: colf, badanti, lavoratori domestici;
- `lavoro_agricolo`: coltivatori diretti, coloni, mezzadri, lavoratori agricoli;
- `malattia_tbc`: malattia tubercolare riconosciuta.

**Residenza e domicilio** (decisione 71): `regione` e `comune` sono quelli di **residenza** (anagrafe). Se il bando parla di domicilio, cioè di dove la persona vive di fatto (uno studente fuorisede, un lavoratore in trasferta), si usano `regione_domicilio` e `comune_domicilio`. Per chi vive dove risiede valgono gli stessi.

**Sede e livello del corso** (decisione 73): per i bandi "per gli iscritti agli atenei con sede in…" usa `regione_ateneo`, oppure `provincia_ateneo` quando il bando divide per provincia (gli ERSU siciliani: Catania, Messina, Palermo, Enna) o `comune_ateneo` per una sede precisa. Per "iscritti a corsi di laurea magistrale" o "dottorandi" usa `livello_corso`; per gli studenti a tempo parziale, `tempo_parziale`.

**`regione_ateneo`**: la regione della sede del corso (bandi per il diritto allo studio "per gli iscritti agli atenei con sede in…"). Con l'operatore `in`, come `regione`.

## Scelte da discutere

1. **Niente dati giudiziari.** Condanne e misure cautelari non vengono chieste: diventano "da verificare". Peggiora l'esito dell'ADI, ma è una domanda che un servizio del genere non dovrebbe fare.
2. **Dati sensibili.** ISEE, reddito, disabilità e composizione della famiglia non vanno salvati: il profilo deve restare nel browser.
3. **Molti non conoscono il proprio ISEE.** Potremmo chiedere una fascia invece del numero, oppure proporre una stima. Da decidere con la demo.
4. **Unità della data.** Il questionario chiederà una data sola e calcolerà giorni e mesi: i due campi restano separati perché le schede usano termini diversi.
