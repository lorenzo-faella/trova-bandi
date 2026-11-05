# Fattibilità del ramo persone e dell'agente di raccolta (29/10/2026)

Domanda (Edoardo): si può automatizzare il processo che **trova** i bandi e i bonus per le persone, ne **scarica** i documenti, ne **estrae** i requisiti e li salva in un posto che il software legge per "accendere le caselle" del questionario?

**Risposta breve:**
- **Estrazione dei requisiti: sì.** I documenti provati sono testo leggibile, e un LLM ha estratto tutti i requisiti con la citazione. Ha però fatto almeno un errore probabile, quindi servono validazione e un controllo umano a campione.
- **Scoperta dei bandi nuovi:**
  - facile per le fonti nazionali (poche);
  - fattibile per le 20 regioni (siti diversi ma in numero finito);
  - difficile per i circa 7.900 comuni, ma ci sono scorciatoie (§3).

Non è da fare ora: è la verifica che il progetto regge.

## 1. Cosa abbiamo provato

L'estrazione è stata fatta con un LLM su tre documenti reali, chiedendo ogni requisito con la frase esatta del testo.

| documento | tipo | requisiti estratti | cosa abbiamo imparato |
|---|---|---|---|
| Bonus nuovi nati 2026 (INPS, circ. 76/2025; da articolo di InformazioneFiscale) | nazionale | 8: cittadinanza (3 casi), residenza in Italia, ISEE ≤ 40.000, figlio nel nucleo, nato o adottato dal 1/1/2025, adozioni solo minorenni | Requisiti puliti e già "a domanda". Termine relativo ("entro 120 giorni dalla nascita"), non una data fissa: lo schema deve gestirlo. |
| Dote Scuola Lombardia, DGR 5707/2026 allegato A (PDF della Regione) | regionale | residenza in Lombardia, età entro 21 anni, tipo di scuola, ISEE ≤ 15.748,78, pendolarità per scuole fuori regione | PDF testuale, requisiti in prosa. **Errore probabile:** l'LLM ha indicato l'anno scolastico "2028/2029", mentre le altre fonti parlano del 2026/27. Va verificato: è proprio il tipo di errore che la citazione obbligatoria fa scoprire. Le date di apertura non sono nella delibera ma negli avvisi: servono **due documenti** per un bando. |
| Fondo Sociale Affitti 2026, Comune di Genova (PDF) | comunale | 13: residenza a Genova dal 1/1/2025, contratto registrato, alloggio ≤ 110 mq, no categorie catastali A/1, A/7…, ISEE ≤ 9.000, ISE ≤ 25.000, patrimonio mobiliare ≤ 20.000, canone ≤ 6.000 €/anno, nessuna casa adeguata nella Città Metropolitana… | Molti requisiti non sono domande "da questionario" (mq, categoria catastale). Proposta: le domande principali accendono le caselle, i requisiti di dettaglio diventano una checklist "da verificare" mostrata con il bando. |

Conclusione: l'estrazione funziona sul testo, ma **non è affidabile al 100%**. Per questo il test del brief (10 bandi, prima a mano poi con l'LLM, poi il confronto) resta la misura chiave da fare.

**Download automatico: provato il 29/10 dal computer di Edoardo** (`prove/prova_download.py`, report in `docs/prova-download.md`). Esito: **fattibile**.
- 7 fonti su 8 scaricate e leggibili da un programma: incentivi.gov.it, INPS (home page e open data), Agenzia delle Entrate, elenco bandi della Regione Siciliana, PDF della Regione Lombardia e del Comune di Genova.
- 1 PDF comunale (Cassano d'Adda) è una **scansione senza testo**: per i documenti di questo tipo serve l'OCR (riconoscimento del testo dall'immagine), che aggiunge possibili errori. Da contare quanti sono.
- Il robots.txt dell'Agenzia delle Entrate non era leggibile: prima di scaricare in modo sistematico va controllato a mano.

## 2. Il formato: dove finiscono i requisiti

Si riusa ciò che c'è già: un file YAML per bando, validato da `schema/regola.schema.json`, letto dal motore a tre valori. Per le persone lo schema va esteso con campi nuovi. Ogni campo corrisponde a una domanda del questionario:

- età;
- ISEE (e ISE, patrimonio);
- regione e comune di residenza, e da quando;
- cittadinanza o tipo di permesso;
- composizione del nucleo e figli (età);
- condizione: studente, lavoratore, disoccupato, pensionato;
- titolo di godimento della casa: affitto o proprietà;
- disabilità (dato sensibile: domanda facoltativa).

Regole per l'agente:
1. Estrae solo requisiti che corrispondono a un campo dello schema, sempre con **la frase citata e il link al documento**.
2. Un requisito che non corrisponde a nessun campo va in una lista "da rivedere": indica una domanda nuova da aggiungere, oppure un requisito di dettaglio per la checklist.
3. Il file passa la validazione dello schema; se non la passa, non entra nel motore.
4. Ogni file porta lo stato `estratto_da_llm` oppure `verificato` (e da chi). Nella demo si può mostrare "requisito estratto automaticamente, verifica sul bando".

## 3. Scoperta: come trovare i bandi nuovi

| livello | quanti | strategia | difficoltà |
|---|---|---|---|
| Nazionale (INPS, Agenzia delle Entrate, ministeri) | decine di misure | Elenco curato, più monitoraggio delle nuove circolari INPS e delle guide dell'Agenzia. Le misure nuove nascono da leggi (Gazzetta Ufficiale). | bassa |
| Regionale | 20 siti | Un adattatore per sito, oppure un agente che naviga la pagina "bandi" della regione. In più incentivi.gov.it per le imprese. | media |
| Comunale | circa 7.900 comuni | Vedi sotto | alta |

Tre scorciatoie per i comuni:
1. **Obbligo di trasparenza.** Il D.Lgs. 33/2013, art. 26, impone a ogni amministrazione di pubblicare criteri e modalità per sovvenzioni e contributi nella sezione "Amministrazione trasparente → Sovvenzioni, contributi, sussidi, vantaggi economici". È un indirizzo standard in tutti i siti.
2. **Schemi regionali.** Molti bandi comunali applicano una misura regionale. Per esempio il fondo affitti: la Regione Lazio pubblica un bando-schema tipo, e in Lombardia i comuni citano la DGR regionale. Si estrae lo schema una volta e si registra quali comuni lo applicano, con le loro varianti (soglie, date).
3. **Piattaforme comuni.** Molti comuni usano lo stesso fornitore di siti. Nelle ricerche di oggi molti PDF comunali stavano su `*.municipiumapp.it`, quindi un solo adattatore copre molti comuni.

Per il progetto (consegna 27/11) basta dimostrare la catena completa su: misure nazionali, 1-2 regioni e i loro comuni capoluogo. L'estensione al resto d'Italia è una questione di fonti, non di codice.

## 4. Architettura proposta dell'agente

```
fonti (elenco curato di URL: INPS, AdE, regioni, sezioni "Amministrazione trasparente" dei comuni)
  -> sorveglianza: controlla periodicamente le pagine, trova link nuovi (confronto con quanto già visto)
  -> download: pagina web o PDF, salvato con data (come data/raw/)
  -> deduplicazione: lo stesso bando su più siti diventa un solo file
  -> estrazione LLM: requisiti -> campi dello schema, con citazione; il resto alla lista "da rivedere"
  -> validazione: JSON Schema + controlli (date plausibili, soglie ISEE numeriche, citazione presente nel testo)
  -> data/regole/<id>.yaml, stato "estratto_da_llm"
  -> motore e questionario (già esistenti)
```

Il controllo "la citazione è presente nel testo" si fa con il codice, senza LLM. Avrebbe intercettato subito un errore come quello della Dote Scuola, se l'anno non compare nel documento.

## 5. Rischi

- **Errori dell'LLM**, come visto. Mitigazioni: citazione obbligatoria, controllo automatico della citazione, stato "non verificato", misura su un campione etichettato a mano.
- **Download.** Alcuni siti potrebbero bloccare gli script. Va rispettato `robots.txt` e va scaricato poco e lentamente (regola già usata da Lorenzo: al massimo una volta al giorno).
- **Costo.** Una chiamata a un LLM per documento costa nell'ordine dei centesimi. Per qualche centinaio di documenti è una spesa piccola, ma va stimata prima su un campione.
- **Dati sensibili.** ISEE, disabilità e cittadinanza sono dati delicati: il profilo non va salvato sul server (brief, idea 6).

## 6. Prossimi passi (vedi `da-fare.md`)

1. Test di estrazione del brief (task 4.3) su 10 bandi per persone e imprese: prima a mano, poi con l'LLM, poi il confronto.
2. Elenco dei campi per le persone, cioè l'estensione dello schema e le nuove domande del questionario.
3. Prova di download automatico dal nostro computer su 3 fonti (una pagina INPS, una pagina bandi regionale, una sezione "Amministrazione trasparente" di un comune).

## Fonti

- [Bonus nuovi nati 2026, requisiti (InformazioneFiscale)](https://www.informazionefiscale.it/Bonus-nuovi-nati-inps-requisiti-domanda)
- [Dote Scuola Lombardia, DGR 5707/2026, allegato A (Regione Lombardia)](https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/03-istruzione-formazione-e-lavoro/02-dote-scuola/red-dote-scuola-2026/allegati/dgr-5707-2_02_2026-allegato-a.pdf)
- [Dote Scuola 2026/27, ISEE sotto 15.748 euro (Orizzonte Scuola)](https://www.orizzontescuola.it/dote-scuola-lombardia-2026-27-domande-dal-24-marzo-per-bonus-libri-e-tecnologia-con-isee-sotto-15-748-euro/)
- [Fondo Sociale Affitti 2026, requisiti (Comune di Genova)](https://www.comune.genova.it/sites/default/files/2026-02/REQUISITI%20E%20CRITERI%20BANDO%20FSA%202026.pdf)
- [Bando-schema tipo affitti (Regione Lazio)](https://regione.lazio.it/sites/default/files/2026-01/bando-schema-tipo-2025.docx)
- [Obblighi di pubblicità, artt. 26 e 27 D.Lgs. 33/2013 (LeggiOggi)](https://www.leggioggi.it/d-lgs-332013-obblighi-di-pubblicita-dei-dati-riguardanti-contributi-sovvenzioni-ecc-artt-26-e-27-e-appalticontratti-pubblici-art-37-e-art-1-comma-32-legge-1902012/)
- [Open data INPS](https://www.inps.it/dati-ricerche-e-bilanci/open-data)
