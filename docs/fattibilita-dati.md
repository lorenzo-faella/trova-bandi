# Fattibilità dei dati

*Generato da `pipeline/profila.py` il 2026-11-27 da `incentivi_export_2026-10-27.json` (riferimento 2026-10-27): non modificare a mano.*

## Catalogo

- Incentivi nell'export: **6007**. Stato al 2026-10-27: chiuso 5226, aperto 556, aperto (senza scadenza) 215, non ancora aperto 10.
- Non chiusi: **781**, di cui accessibili ad almeno un tipo di impresa: **756**.
- Nazionali (tutte le 20 regioni): 77 (10%); una sola regione: 664 (88%); con elenco di comuni: 136 (18%).

## Beneficiari dei bandi non chiusi

| tipologia di soggetto | bandi |
|---|---|
| Impresa | 695 |
| Cooperative/Associazioni Non Profit | 159 |
| Professionista | 124 |
| Consorzio | 99 |
| Impresa - SU/PMI innovativa | 78 |
| Ente Pubblico | 66 |
| Rete d'impresa | 58 |
| Impresa - prevalenza femminile | 52 |
| Impresa - prevalenza giovanile | 52 |
| Impresa da costituire - Altro | 49 |
| Università/Ente di Ricerca | 44 |
| Impresa da costituire - Giovanile | 36 |
| Impresa da costituire - Femminile | 35 |
| Cittadino | 31 |
| Istituto finanziario | 25 |

## Requisiti strutturati nelle 756 regole generate

Un requisito è scritto solo se esclude qualcuno (un bando aperto a tutte le dimensioni non ha il requisito).

| campo | bandi con il requisito |
|---|---|
| tipologia | 756 (100%) |
| regione | 679 (90%) |
| dimensione | 597 (79%) |
| settore | 507 (67%) |
| comune | 313 (41%) |
| ateco_2025 | 157 (21%) |
| ambito | 83 (11%) |
| ateco_2007 | 78 (10%) |

## Problemi di qualità trovati

- **Due versioni di ATECO.** Bandi per imprese per versione dei codici: tutti i settori: 521, 2025: 157, 2007: 78. Senza etichetta la versione si deduce dalla data di apertura (ATECO 2025 dal 1/4/2025). I bandi in ATECO 2007 restano "mancano dati" finché non usiamo la tavola di raccordo ISTAT.
- **Comuni soppressi.** 28 bandi elencano comuni assenti dall'elenco ISTAT, per lo più soppressi da fusioni (130 nomi distinti, es. Cagno, Casasco d'Intelvi, Cavallasca, Pellio Intelvi, Ramponio Verna). Chi ha sede fuori dall'elenco riconosciuto riceve "mancano dati", non "non idoneo".
- **Entità HTML nei nomi.** `Sant&apos;Agata` conteneva un `;`, il separatore delle liste: senza decodificare prima, il nome si spezzava in due comuni inesistenti.
- **Settore assente** in 21 bandi per imprese: trattato come nessun vincolo.

## Requisiti che stanno solo nel testo (descrizioni dei 756 bandi per imprese)

Conteggio grezzo per parola chiave: indica quante domande in più servirebbero dopo l'estrazione, non quanti bandi hanno davvero quel requisito.

| requisito | bandi che lo menzionano |
|---|---|
| de minimis | 87 (12%) |
| fatturato / ricavi | 30 (4%) |
| numero di dipendenti / ULA | 96 (13%) |
| sede operativa / unità locale | 123 (16%) |
| anni di attività / data di costituzione | 83 (11%) |
| età del titolare / under 35 | 42 (6%) |
| regolarità contributiva (DURC) | 14 (2%) |
| rating di legalità | 21 (3%) |
| certificazioni (ISO, parità di genere) | 48 (6%) |
