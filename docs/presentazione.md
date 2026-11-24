# Percorso per la presentazione (circa 10 minuti)

*Bozza del 22/11 (decisione 97), aggiornata il 24/11 con i profili nuovi e il confronto (decisione 104). Da provare dal vivo almeno una volta prima del 30/11.*

**Prima di iniziare:** `TROVA_BANDI_GIORNO=2026-11-22 make demo`. Con la data fissa i bandi
aperti e i risultati sono sempre gli stessi, anche se la presentazione è il 30/11 o il 4/12.

1. **Il problema (1 min).** Tanti aiuti, sparsi, spesso non chiesti. Due numeri da `docs/contesto.md` (sono anche
   sulla pagina iniziale, sotto "Perché serve").
2. **Stesse domande, strade diverse (1 min).** Sulla pagina iniziale, scorrere fino al grafico dei percorsi: parte da
   solo quando è visibile (altrimenti "▶ Guarda i percorsi"), dura circa 18 secondi.
   - Cento persone partono insieme: 95 simulate più i nostri profili, con la faccina. A ogni domanda ognuno passa
     dalla sua porta, e i fasci si separano e si incrociano. All'arrivo sono distribuite per aiuti in vista, da 0 a 13.
   - Passare sopra la porta "Studia" o "Genitore solo" per mostrare dove finiscono quelle persone; sopra la faccina della
     mamma per seguire la sua strada. Un clic sulla sua etichetta apre il suo percorso guidato.
   - Sotto, le carte dei profili (anche il negozio):

   | profilo | compatibili | possibili |
   |---|---|---|
   | Studente fuorisede | 1 | 3 |
   | Mamma sola | 5 | 6 |
   | Famiglia monoreddito | 6 | 9 |
   | Giovane in affitto | 2 | 3 |
   | Pensionata sola | 3 | 6 |
   | Negozio di quartiere | 30 | 10 |
3. **Studente di 22 anni, dal vivo (2 min).** "Rispondi tu": residenza a Milano nella prima pagina, nucleo di una
   persona, studente all'università, ISEE 14.000 €, in affitto.
   - Le domande sono 14 e non compare niente su figli o maternità: il questionario chiede solo ciò che serve a lui.
   - Alla fine, fra i possibili: bonus psicologo, le due detrazioni per l'affitto, il Fondo prima casa.
4. **Mamma sola (2 min).** Dal nome "Mamma sola" all'arrivo del grafico, o dalla sua carta: 32 anni, separata, due figli di 6 e 1 anno,
   dipendente part-time a Milano, in affitto, ISEE 9.000 €.
   - Il **percorso guidato** ripercorre il questionario una domanda alla volta, con la risposta del profilo già scelta
     e i risultati che cambiano a destra (circa 2,5 secondi a domanda, 21 domande). Commentare le prime 4-5 (residenza,
     lavoro, nucleo di tre persone), poi "Avanti" per accelerare o "Vai alla fine". "Pausa" ferma la guida per
     spiegare una domanda.
   - L'ultimo passo mostra le risposte del profilo alle verifiche finali (Sì/No, con i dati della sua storia), poi la
     pagina finale: aiuti completamente diversi dallo studente, **5 compatibili** (assegno unico, Carta "Dedicata a te",
     bonus luce e gas, detrazione per l'affitto, congedo parentale).
   - Aprire la scheda dell'assegno unico: requisiti, citazione della scheda INPS e link.
   - In "Sono possibili questi", al bonus nido ("il figlio frequenta un nido?") rispondere **Sì**: diventa
     compatibile dal vivo, e i compatibili salgono a 6.
   - Se resta tempo, "Famiglia monoreddito" fa lo stesso con due genitori: 6 compatibili, fra cui il congedo di paternità.
5. **Impresa (1 min).** Dalla carta "Negozio di quartiere": microimpresa del commercio a Bergamo, ATECO 47.71.10. Le
   domande delle imprese sono poche: lasciar scorrere il percorso guidato.
   **30 bandi compatibili** con i filtri del portale, più quelli raccolti dai siti che il portale non ha (etichetta
   "estratta automaticamente").
6. **Come funziona e quanto funziona (2 min).** Lo schema e la tabella delle misure di `docs/report-bozza.md`: citazioni
   verificate al 100%, accordo fra due estrazioni 85-94%, revisione a mano, test.
7. **Limiti e prossimi passi (1 min).** Copertura disomogenea, regole non riviste, condizioni non modellabili; idee:
   risposte a fasce per l'ISEE, aggiornamento automatico della raccolta.

**Se qualcosa va storto:** i report stampati dei profili "Mamma sola", "Famiglia monoreddito" e "Negozio di quartiere", fatti il 24/11 con la data del 22/11, sono in `docs/riserva-presentazione/`.
