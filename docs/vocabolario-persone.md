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
| `lavora_in_italia` | Lavori in Italia? | sì/no | Assegno unico |
| `soggetto_irpef_italia` | Paghi le imposte sul reddito in Italia? | sì/no | Assegno unico |
| `condizione_lavorativa` | Qual è la tua situazione lavorativa? | `occupato`, `disoccupato`, `studente`, `pensionato`, `inattivo` | NASpI |
| `ultimo_lavoro_subordinato` | Il tuo ultimo lavoro era da dipendente? | sì/no | NASpI |
| `causa_fine_lavoro` | Come è finito? | `licenziamento`, `fine_contratto`, `dimissioni`, `dimissioni_giusta_causa`, `dimissioni_periodo_tutelato`, `risoluzione_consensuale`, `risoluzione_consensuale_tutelata` | NASpI |
| `giorni_da_cessazione_lavoro` | Quanti giorni fa è iniziato il termine (di solito la fine del lavoro)? | numero | NASpI |
| `settimane_contributi_4_anni` | Quante settimane di contributi hai negli ultimi 4 anni? | numero | NASpI |
| `giorni_da_evento_figlio`, `mesi_da_evento_figlio` | Quando è nato o entrato in famiglia il figlio? | una data, da cui si ricavano entrambi. I mesi sono quelli interi già compiuti, quindi un termine di N mesi si scrive `< N`: chi ha compiuto N mesi è già oltre. Un termine di N giorni si scrive `<= N` | Nuovi nati, maternità |

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
| `reddito_annuo` | Reddito annuo | euro | Assegno unico |
| `attivita` | Cosa fa? | `studio`, `tirocinio_o_lavoro`, `disoccupato_cpi`, `servizio_civile`, `nessuna` | Assegno unico |

`regione` e `comune` sono gli stessi campi delle imprese, ma nessuna delle 5 regole di prova li usa ancora.

## Scelte da discutere

1. **Niente dati giudiziari.** Condanne e misure cautelari non vengono chieste: diventano "da verificare". Peggiora l'esito dell'ADI, ma è una domanda che un servizio del genere non dovrebbe fare.
2. **Dati sensibili.** ISEE, reddito, disabilità e composizione della famiglia non vanno salvati: il profilo deve restare nel browser.
3. **Molti non conoscono il proprio ISEE.** Potremmo chiedere una fascia invece del numero, oppure proporre una stima. Da decidere con la demo.
4. **Unità della data.** Il questionario chiederà una data sola e calcolerà giorni e mesi: i due campi restano separati perché le schede usano termini diversi.
