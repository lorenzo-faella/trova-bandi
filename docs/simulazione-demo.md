# Simulazione della demo: prima e dopo le correzioni del 18/11

Una persona inventata ma plausibile risponde alla demo prima e dopo le correzioni della decisione 70. Il protocollo è stato fissato prima di vedere qualsiasi risultato, per evitare di scegliere risposte o criteri che danno ragione alle correzioni. Il punto di partenza è la prova di Lorenzo del 18/11: un profilo del Lazio senza condizioni particolari aveva 66 "possibili", troppi per essere credibili.

## Protocollo

1. **Persone scritte prima**: 4 persone plausibili, diverse dal profilo di Lorenzo e dai profili di esempio della demo, in `prove/simulazione/persone.yaml`. Ognuna ha la risposta a ogni domanda del questionario, compresi i campi nuovi. Dove la persona realisticamente non conosce il dato (ISPE, settimane di contributi) la risposta è "non lo so".
2. **Estrazione**: una persona a caso, con `random.Random(18112026)`. È uscita **Salvatore, 58 anni, Palermo**: commerciante con partita IVA (18.000 euro), vedovo, con una figlia di 19 anni all'università, casa di proprietà, ISEE 13.000. Impronta SHA-256 del file della persona: `16cebb07…591d`, uguale prima e dopo.
3. **Esecuzione**: le risposte arrivano solo dal file.
   - `prove/simulazione/rigioca.py` rigioca il questionario attraverso l'API, una domanda alla volta come la pagina.
   - Uno script con Chrome fa lo stesso sulla pagina vera e stampa il report.

   Il "prima" gira su una copia congelata del codice, presa prima di ogni modifica. Le due esecuzioni (API e pagina) danno gli stessi conteggi.
4. **Metriche, fissate prima**:
   - esiti del motore;
   - "possibili" mostrati;
   - quanti di questi sono di altre regioni;
   - quanti non hanno nessun requisito a favore;
   - pertinenza dei "possibili" mostrati in testa, al massimo 20.
5. **Giudizio alla cieca**: i "possibili" mostrati dalle due versioni, mescolati in un'unica lista (seme 7), senza dire da quale versione venisse ognuno. La domanda per ogni voce: "Salvatore potrebbe realisticamente averne diritto, quindi vale la pena controllare?". Solo dopo i giudizi sono stati abbinati alle versioni.

## Risultati

| | prima | dopo |
|---|---|---|
| esiti del motore (ti spetta / da verificare / mancano dati / non ti spetta) | 1 / 57 / 1 / 63 | 1 / 35 / 1 / 85 |
| "possibili" mostrati nelle tessere | **57** | **6** |
| di cui bandi di altre regioni | 26 | 0 (21 in un gruppo chiuso) |
| di cui senza nessun requisito a favore | 23 dei 31 vicini | 0 (8 in "Non sappiamo dirlo") |
| pertinenti fra i "possibili" mostrati in testa (giudizio alla cieca) | **1 su 20** | **2 su 6** |
| domande fatte | 20 | 20 (una nuova, "situazioni particolari"; una in meno, "un'altra casa") |

- **Pertinenti:** le due voci pertinenti sono l'indennità per morte ai superstiti e l'indennità una tantum ai superstiti: Salvatore è vedovo. Nel "prima" la prima voce era sepolta fra 57 possibili. Nel "dopo" la risposta "vedovo" (`situazioni_particolari: superstite`) le porta entrambe in evidenza.
- **Falsi no**, l'errore peggiore: 25 bandi passano da "possibile" a "non ti spetta", e sono stati controllati uno per uno. Sono tutti corretti per Salvatore:
  - 6 sono bandi di altri comuni, ora con il loro vincolo di residenza;
  - uno è il nido di Pescara (serve un figlio minorenne);
  - 14 sono benefici per gruppi di cui non fa parte (Gestione Magistrale, ex IPOST, figli di dipendenti pubblici, TBC, lavoratori domestici, coltivatori);
  - gli altri chiedono di essere dipendente, disabile, o di avere almeno 67 anni.
- **Nel senso opposto**, 3 bandi passano da "non ti spetta" a "non sappiamo dirlo". Uno è un piccolo peggioramento: gli ANF per dipendenti privati, rifatti, non escludono più un lavoratore autonomo.
- **Restano 4 "possibili" non pertinenti** su 6:
  - un incarico di volontariato del Comune di Caltanissetta: la regola non scrive il vincolo di residenza;
  - tre benefici INPS che non sono stati rifatti, oppure in cui un requisito generico risulta "a favore" (Assistenza Magistrale per malattia, talassemia, maternità della Gestione Separata).

## Confronto con la prova di Lorenzo

Nel report di Lorenzo (Lazio, codice di prima) le schede "possibili" stampate sono 29:
- 25 sono INPS, e di queste 19 sono per gruppi ristretti: ex IPOST, Gestione Magistrale, figli di dipendenti pubblici, superstiti, TBC, coltivatori;
- 4 sono bandi del Lazio.

Gli altri 37 dei suoi 66 erano bandi di altre regioni, nel gruppo chiuso che non si stampa. È la stessa composizione trovata per Salvatore: le correzioni della decisione 70 colpiscono le cause che hanno gonfiato anche il suo report.

## Limiti

- **Una persona sola**, e il giudizio di pertinenza è di chi ha fatto le correzioni, anche se dato alla cieca sulla versione. Una prova più solida servirebbe più persone, estratte da distribuzioni reali, con giudici esterni.
- **"Pertinente"** vuol dire "vale la pena controllare", non "ne ha diritto": nessuno ha verificato i bandi fino in fondo.
- **I campi nuovi escludono chi risponde "nessuna di queste".** Se una persona sbaglia la risposta (non sa che il genitore era dipendente pubblico), perde quei benefici. Il testo delle opzioni va tenuto chiaro.
- **Copertura parziale**: sono state rifatte 75 regole, quelle aperte il 18/11 con un requisito coperto dai campi nuovi. Le altre restano come prima.

## Come rifarla

```
python prove/simulazione/rigioca.py prove/simulazione/persone.yaml http://127.0.0.1:8000 risultati.json commerciante-palermo   # con `make demo` acceso
```

## Aggiornamento del 19/11

Con le regole rifatte della decisione 73 la stessa persona ottiene 4 "possibili" invece di 6. Spariscono l'avviso per ispettori volontari, che non è un aiuto, e l'assegno di malattia della Gestione Magistrale. Restano le due indennità ai superstiti, le uniche pertinenti.

## Aggiornamento del 20/11

Con le regole delle fonti miste (decisioni 74-75) e il giorno spostato al 20/11, Salvatore ha 6 "possibili". I due nuovi sono contributi della Regione Siciliana: l'acquisto di lavastoviglie e gli interessi sui prestiti al consumo. Sono bandi per i residenti in Sicilia, quindi vale la pena controllarli. Le due indennità ai superstiti restano.

Prima di correggere la regione dei bandi raccolti con le API, fra i suoi "possibili" c'era anche una candidatura dell'Emilia-Romagna, trattata come nazionale (decisione 75).
