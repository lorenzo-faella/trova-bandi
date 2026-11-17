# Secondo passaggio sulle etichette: convenzioni comuni

Preparato il 17/11 per Lorenzo ed Edoardo, dopo la misura della decisione 60 e la correzione di `pipeline/confronta.py` (decisione 63). Ognuno corregge solo le proprie etichette. Ogni correzione si scrive nelle `note` del file, e nel report vanno le misure prima e dopo.

## Da dove vengono le differenze

Sui 3 benefici in comune l'accordo fra le etichette è 46% (decisione 63). Su ISCRO e congedo di paternità siamo al 70-73%, sul congedo parentale al 3%. Nel congedo parentale, su 5.000 persone fittizie:

| esito con le etichette di Lorenzo | esito con quelle di Edoardo | persone |
|---|---|---|
| da verificare | idoneo | 2.803 |
| da verificare | non idoneo | 904 |
| mancano dati | idoneo | 289 |

Non è una lettura diversa della scheda. Lorenzo segna come `non_modellabile` le esclusioni che riguardano pochi (lavoratori domestici, figli adottivi), e così l'esito diventa "da verificare" per tutti; Edoardo non le segna. È una convenzione da fissare.

## Le convenzioni da decidere

**A. Vocabolario del 9/11 per tutti (proposta: sì).** Dove oggi esiste un campo, si usa quello invece di un `non_modellabile` o di un campo più generico:
- "dipendente / autonomo / Gestione Separata" → `tipo_lavoro` (non solo `condizione_lavorativa: occupato`);
- un tetto al reddito di chi fa domanda → `reddito_richiedente`;
- un figlio → componente con `figlio: vero`.

Lato Lorenzo: niente da cambiare. Lato Edoardo: paternità, maternità degli autonomi e ISCRO (`tipo_lavoro`); discontinuità (35.000 €) e ISCRO (12.000 €) (`reddito_richiedente`).

**B. `lavora_in_italia` (proposta: no, salvo che la scheda lo dica).**
- Le schede non lo scrivono, e né l'estrazione né le etichette di Lorenzo lo usano.
- C'è anche un problema tecnico: il questionario lo chiede solo a chi è occupato. Messo in un beneficio per chi ha perso il lavoro (DIS-COLL), lascerebbe l'esito su "mancano dati" per sempre.
- Se si decide sì: Lorenzo lo aggiunge a congedo di paternità, congedo parentale, ISCRO e Bonus mamme, non a DIS-COLL e SFL.
- Se si decide no: Edoardo lo toglie dalle sue 4 etichette.

**C. Esclusioni che riguardano un gruppo ristretto → `portata: rara` (proposta: sì, è già la regola di `docs/etichettatura.md`).** "Esclusi i lavoratori domestici", "salvo...", "ad eccezione di..." danno "idoneo, salvo eccezioni", non "da verificare". Un requisito centrale che il vocabolario non copre resta `non_modellabile` senza `portata`: per esempio "deve essere il padre", oppure le soglie di patrimonio dell'SFL.

Lato Lorenzo, i candidati a `portata: rara`:
- congedo parentale: "Esclusi i genitori lavoratori domestici o a domicilio";
- Bonus mamme: "Escluse le lavoratrici domestiche";
- Bonus mamme: "Escluse le madri con tre o più figli, dipendenti a tempo indeterminato".

**D. Niente requisito "pigliatutto" (proposta: sì).** Un `non_modellabile` del tipo "gli altri requisiti vanno verificati caso per caso" diventa uno per ogni condizione, ciascuno con la sua citazione, oppure va nelle `note`. Lato Edoardo: maternità degli autonomi e ISCRO.

**E. Età del figlio (proposta: età del componente).**
- "Entro i 14 anni del bambino" → componente con `figlio: vero` ed `eta < 14`.
- `mesi_da_evento_figlio` si usa per i termini che partono dalla nascita o dall'ingresso in famiglia ("entro 5 mesi dal parto").
- Dalla decisione 63 la misura tratta i due modi come coerenti, ma uno solo è più semplice da leggere.
- Lato Edoardo: congedo parentale.

**F. Incompatibilità con altri benefici (da discutere).** "Incompatibile con NASpI, DIS-COLL..." oppure "non ricevere l'ADI".
- Come `non_modellabile`, fa uscire "da verificare" per tutti.
- Nelle `note`, la regola non ne tiene conto.
- Oggi Lorenzo la mette nei requisiti (ISCRO, SFL); l'estrazione, in un caso, nelle note.

## Ordine

1. Lorenzo ed Edoardo decidono A-F. Basta un messaggio con "sì/no" per lettera.
2. Ognuno corregge le proprie etichette e scrive la correzione nelle `note`.
3. `make confronta PY=.venv/bin/python`, poi le misure prima e dopo nel report.
