# Revisione a mano delle imprese: la metà di Edoardo (10 bandi, open data)

*Numeri della lista in `docs/da-rivedere-a-mano-imprese.md`, dove si segna l'esito. Divisione incrociata: nessuno rivede una regola che ha prodotto. L'altra metà è in `docs/revisione-a-mano-imprese-lorenzo.md`. Per ogni bando: aprire il link, confrontare requisiti, citazioni e date con il bando, segnare l'esito (giusta / errori piccoli / sbagliata) e una nota se serve. Niente LLM nel giudizio (decisione 97).*

## 11. Fondo di Garanzia per le Piccole e Medie Imprese

- **Link:** https://www.mimit.gov.it/index.php/it/incentivi/fondo-di-garanzia-per-le-pmi
- **Ente:** Ministero delle Imprese e del Made in Italy · **origine:** open data · **date:** apertura 2015-11-30, chiusura 2026-12-31 · **file:** `148`
- **Visto da:** 14 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa, Professionista
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Moda e Tessile, Servizi di trasporto, Fornitura Energia, Acqua e gestione Rifiuti, Cultura, Chimica e Farmaceutica, Altri servizi, Agroalimentare, Turismo, Alberghiero, Artigianato, Autoveicoli e altri mezzi di trasporto, Commercio, Edilizia, Elettronica, ICT, Metallurgia, Mobili, Legno e Carta, Ristorazione, Salute, Meccanica
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** giusta

---

## 12. Sostegno alla domanda di servizi di cloud computing e cyber security

- **Link:** https://www.mimit.gov.it/it/incentivi/sostegno-alla-domanda-di-servizi-di-cloud-computing-e-cyber-security
- **Ente:** Ministero delle Imprese e del Made in Italy · **origine:** open data · **date:** apertura 2026-11-10, chiusura 2027-01-20 · **file:** `8802`
- **Visto da:** 14 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa, Impresa - SU/PMI innovativa, Professionista, Consorzio, Cooperative/Associazioni Non Profit, Istituto finanziario, Università/Ente di Ricerca
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)

**Esito:** giusta, nota: "«i servizi e prodotti di cloud computing e cyber security dovranno essere forniti da soggetti iscritti in apposito elenco formato e tenuto dal Ministero» i requisiti son giusti, ma bisogna mettere che bisogna controllare il fornitore"

---

## 13. Fondo Salvaguardia imprese

- **Link:** https://www.mimit.gov.it/it/incentivi/fondo-salvaguardia-imprese
- **Ente:** Ministero delle Imprese e del Made in Italy · **origine:** open data · **date:** apertura 2021-02-02, chiusura 2026-12-31 · **file:** `90`
- **Visto da:** 13 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Mobili, Legno e Carta, Moda e Tessile, Ristorazione, Salute, Servizi di trasporto, Metallurgia, Meccanica, ICT, Fornitura Energia, Acqua e gestione Rifiuti, Elettronica, Edilizia, Cultura, Commercio, Chimica e Farmaceutica, Autoveicoli e altri mezzi di trasporto, Artigianato, Turismo, Alberghiero, Agroalimentare, Altri servizi
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** sbagliata

**Requisiti del bando che la regola non ha:** Devono essere imprese in difficoltà: «Il Fondo si rivolge alle imprese che presentano le seguenti due caratteristiche: 1. Imprese in difficoltà economico finanziaria: (...), 2. Imprese che soddisfano almeno una delle seguenti condizioni: (...)»

---

## 14. Erogazione di finanziamenti agevolati da parte dei Confidi

- **Link:** https://www.mise.gov.it/it/incentivi/erogazione-di-finanziamenti-agevolati-da-parte-dei-confidi
- **Ente:** Confidi vari · **origine:** open data · **date:** apertura 2023-01-31, chiusura 2038-12-30 · **file:** `197`
- **Visto da:** 7 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Piccola Impresa, Media Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Agroalimentare, Moda e Tessile, Chimica e Farmaceutica, Metallurgia, Elettronica, Meccanica, Autoveicoli e altri mezzi di trasporto, Mobili, Legno e Carta, Edilizia, Fornitura Energia, Acqua e gestione Rifiuti, Commercio, Servizi di trasporto, Alberghiero, Ristorazione, ICT, Cultura, Turismo, Salute, Altri servizi, Artigianato
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** giusta

---

## 15. Garanzia Confidi alle PMI

- **Link:** https://www.mise.gov.it/index.php/it/incentivi/impresa/garanzie-confidi
- **Ente:** Confidi vari · **origine:** open data · **date:** apertura 2017-12-22, chiusura 2038-12-30 · **file:** `51`
- **Visto da:** 7 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa, Professionista
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Agroalimentare, Moda e Tessile, Chimica e Farmaceutica, Metallurgia, Elettronica, Meccanica, Autoveicoli e altri mezzi di trasporto, Mobili, Legno e Carta, Edilizia, Fornitura Energia, Acqua e gestione Rifiuti, Commercio, Servizi di trasporto, Alberghiero, Ristorazione, ICT, Cultura, Turismo, Salute, Altri servizi, Artigianato
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** giusta

---

## 16. Voucher 3I - Investire in innovazione

- **Link:** https://www.mimit.gov.it/it/incentivi/voucher-3i-investire-in-innovazione
- **Ente:** Ministero delle Imprese e del Made in Italy · **origine:** open data · **date:** apertura 2024-12-10, chiusura 2027-12-31 · **file:** `3265`
- **Visto da:** 6 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* tipo di soggetto, almeno uno fra: Impresa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa
  (fonte: incentivi.gov.it, campo Dimensioni)

**Esito:** errori piccoli, nota: "La dimensione è correta, ma può andare anche alle startup, che sono nel 99% dei casi micro imprese, per cui va pure bene: «La misura si rivolge a startup e microimprese.»"

---

## 17. Avviso per la presentazione delle proposte progettuali nell’ambito del CLLD – progetti medi - Strategia Dolomiti Live

- **Link:** https://europa.provinz.bz.it
- **Ente:** Provincia autonoma di Bolzano - Ripartizione Europa · **origine:** open data · **date:** apertura 2022-02-22, chiusura 2029-12-31 · **file:** `813`
- **Visto da:** 2 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* regione della sede, uno fra: Trentino-Alto Adige/Südtirol, Veneto, Estero
  (fonte: incentivi.gov.it, campo Regioni)
- *controllato:* tipo di soggetto, almeno uno fra: Consorzio, Cooperative/Associazioni Non Profit, Ente Pubblico, Impresa, Impresa - SU/PMI innovativa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)

**Esito:** sbagliata

**Requisiti del bando che la regola non ha:** Dal sito: «Il requisito fondamentale per il finanziamento dei progetti è la collaborazione di almeno un partner italiano e uno austriaco. » e poi dall'avviso: «è necessario che ogni progetto coinvolga almeno un partner di entrambi gli Stati membri del Programma di cooperazione Interreg VI-A Italia - Austria.» Questa va in quelle da controllare per cui serve un requisito

---

## 18. Bando Brevetti 2023 - PR Lombardia FESR 2021-2027

- **Link:** https://www.bandi.regione.lombardia.it/servizi/servizio/bandi/dettaglio/ricerca-innovazione/ricerca-sviluppo-innovazione/brevetti-2023-RLF12023035064
- **Ente:** Regione Lombardia · **origine:** open data · **date:** apertura 2024-01-25, chiusura 2027-02-25 · **file:** `5155`
- **Visto da:** 2 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* regione della sede, uno fra: Lombardia
  (fonte: incentivi.gov.it, campo Regioni)
- *controllato:* tipo di soggetto, almeno uno fra: Impresa, Professionista
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Agroalimentare, Alberghiero, Altri servizi, Artigianato, Autoveicoli e altri mezzi di trasporto, Chimica e Farmaceutica, Commercio, Cultura, Edilizia, Elettronica, Fornitura Energia, Acqua e gestione Rifiuti, ICT, Meccanica, Metallurgia, Mobili, Legno e Carta, Moda e Tessile, Ristorazione, Salute
  (fonte: incentivi.gov.it, campo Settore_Attivita)
- *controllato:* codice ATECO 2025, codice che inizia con: 86.21, 74.30, 52.10, 05.10, 86.22, 27.40, 86.23, 86.10, 17.11, 17.12, 10.6, 52.23, 10.5, 52.24, 10.4, 52.21, 10.3, 52.22, 10.2, 10.1, 52.25, 52.26, 27.52, 56.1, 10.9, 56.2, 10.8, 56.3, 10.7, 27.51, 56.4, 64.11, 64.19, 52.31, 98.20, 52.32, 49.50, 21.2, 21.1, 27.20, 39.00, 64.22, 49.42, 32.5, 49.41, 32.4, 25.99, 27.32, 32.3, 27.33, 98.10, 32.2, 32.1, 05.20, 25.91, 25.93, 78.2, 25.92, 32.9, 27.31, 78.1, 64.21, 25.94, 15.20, 49.31, 25.63, 43.9, 47.92, 47.91, 49.39, 62.90, 43.1, 43.2, 43.3, 43.4, 49.34, 25.62, 43.5, 49.33, 64.32, 25.61, 43.6, 49.32, 64.31, 13.95, 13.96, 13.99, 13.93, 13.94, 96.99, 13.91, 13.92, 27.12, 49.20, 47.83, 47.81, 27.11, 47.82, 96.91, 74.99, 47.72, 47.73, 47.71, 74.91, 65.2, 47.78, 65.1, 47.79, 47.76, 49.12, 65.3, 47.77, 25.40, 47.74, 49.11, 47.75, 15.12, 15.11, 88.10, 41.0, 25.53, 47.61, 25.52, 47.62, 30.4, 30.3, 30.2, 30.1, 47.69, 25.51, 47.63, 30.9, 47.64, 20.17, 20.16, 20.15, 20.14, 20.13, 20.12, 20.11, 19.20, 72.10, 87.9, 60.39, 87.1, 87.2, 60.31, 87.3, 72.20, 07.29, 07.21, 52.1, 98.1, 20.20, 52.2, 98.2, 52.3, 42.22, 30.40, 63.9, 50.10, 84.25, 63.1, 84.24, 42.21, 84.21, 84.23, 84.22, 42.11, 42.12, 42.13, 19.10, 30.31, 50.20, 74.9, 30.32, 74.2, 74.1, 84.13, 74.3, 84.12, 84.11, 62.10, 50.1, 50.2, 30.20, 96.21, 96.22, 96.23, 50.30, 85.3, 85.4, 85.1, 85.2, 29.20, 85.5, 85.6, 62.20, 82.91, 82.92, 84.30, 61.2, 61.1, 96.10, 50.40, 96.9, 30.11, 30.13, 30.12, 50.3, 96.3, 82.99, 50.4, 96.4, 27.90, 96.1, 96.2, 29.32, 29.31, 17.22, 08.9, 17.23, 17.24, 72.2, 17.25, 72.1, 17.21, 74.14, 74.13, 74.12, 74.11, 96.40, 07.10, 08.1, 61.9, 94.99, 74.20, 94.91, 96.30, 94.92, 19.2, 19.1, 29.10, 08.91, 08.92, 94.1, 94.2, 43.91, 43.99, 55.90, 23.14, 23.15, 23.11, 23.12, 23.13, 69.10, 94.9, 70.2, 70.1, 11.01, 70.10, 11.03, 11.02, 11.05, 69.20, 11.04, 06.2, 11.07, 11.06, 06.1, 81.3, 81.1, 81.2, 33.20, 70.20, 08.99, 17.2, 43.60, 08.93, 17.1, 92.0, 79.90, 28.9, 33.11, 33.12, 33.19, 33.17, 33.18, 33.15, 33.16, 33.13, 33.14, 21.20, 28.4, 28.3, 28.2, 28.1, 43.50, 82.20, 59.14, 59.13, 59.12, 59.11, 39.0, 43.41, 43.42, 82.10, 43.34, 43.35, 94.20, 59.20, 43.31, 43.32, 43.33, 60.10, 82.40, 43.23, 43.24, 94.11, 94.12, 15.1, 21.10, 43.21, 43.22, 60.20, 82.30, 15.2, 90.1, 90.2, 90.3, 77.31, 77.32, 77.33, 77.34, 26.1, 77.35, 47.51, 25.22, 25.21, 77.39, 26.7, 26.6, 26.5, 47.54, 26.4, 47.55, 26.3, 47.52, 26.2, 47.53, 37.00, 77.21, 55.10, 77.22, 25.30, 47.40, 23.99, 23.91, 37.0, 13.20, 87.99, 87.91, 77.51, 77.52, 90.20, 55.20, 23.61, 23.62, 23.63, 23.64, 23.65, 23.66, 47.30, 90.13, 90.12, 13.30, 47.27, 55.30, 77.40, 90.11, 35.40, 13.3, 59.2, 13.2, 13.1, 25.11, 25.12, 47.25, 13.9, 47.23, 47.24, 47.21, 47.22, 23.70, 59.1, 55.40, 79.12, 79.11, 35.30, 24.3, 24.2, 23.41, 24.1, 23.42, 23.43, 80.09, 23.44, 23.45, 47.12, 80.01, 47.11, 24.5, 24.4, 13.10, 90.39, 35.24, 35.23, 35.22, 35.21, 90.31, 35.3, 23.51, 35.2, 23.52, 35.1, 35.4, 35.14, 35.13, 35.12, 35.11, 92.00, 46.4, 46.5, 46.6, 23.20, 46.7, 46.8, 46.9, 35.16, 35.15, 46.1, 23.31, 23.32, 11.0, 85.51, 85.53, 85.52, 75.00, 28.13, 28.14, 28.11, 22.2, 28.12, 22.1, 28.15, 85.59, 26.70, 68.1, 68.3, 68.2, 85.40, 61.90, 28.24, 28.25, 28.22, 28.23, 33.2, 33.1, 79.9, 28.29, 79.1, 28.21, 87.10, 16.12, 16.11, 26.52, 26.51, 16.24, 38.32, 16.23, 38.33, 85.61, 16.22, 16.21, 16.28, 16.27, 16.26, 16.25, 53.10, 38.31, 55.9, 85.69, 55.1, 55.2, 26.60, 55.3, 55.4, 38.21, 38.22, 38.23, 87.30, 53.20, 20.6, 20.5, 20.4, 20.3, 20.2, 20.1, 66.1, 66.3, 66.2, 26.30, 38.11, 65.12, 38.12, 87.20, 53.30, 99.00, 31.0, 77.1, 77.3, 77.2, 65.11, 77.5, 26.40, 77.4, 77.11, 77.12, 42.9, 88.9, 26.12, 26.11, 42.1, 88.1, 42.2, 65.20, 26.20, 46.90, 99.0, 63.91, 53.1, 63.92, 53.2, 53.3, 65.30, 43.12, 43.13, 95.10, 64.9, 28.99, 28.93, 64.1, 28.94, 28.91, 64.3, 28.92, 43.11, 64.2, 28.97, 28.95, 28.96, 75.0, 61.10, 51.1, 95.31, 95.32, 86.9, 86.2, 86.1, 61.20, 95.29, 62.1, 95.24, 95.25, 73.11, 95.21, 73.12, 95.22, 95.23, 31.00, 08.11, 51.2, 08.12, 97.0, 09.9, 18.12, 18.13, 18.14, 73.1, 18.11, 73.20, 62.2, 09.1, 06.20, 85.10, 62.9, 84.1, 18.20, 51.10, 73.30, 95.40, 73.3, 73.2, 06.10, 85.31, 95.1, 51.21, 51.22, 84.2, 84.3, 85.33, 85.32, 28.30, 63.10, 41.00, 85.20, 60.1, 60.3, 60.2, 97.00, 95.4, 95.2, 95.3, 28.42, 28.41, 10.51, 71.1, 05, 10.52, 06, 07, 71.2, 08, 09, 68.32, 81.10, 68.31, 07.1, 07.2, 10, 11, 10.62, 13, 10.61, 14, 15, 82.2, 16, 82.3, 17, 18, 82.1, 19, 91.41, 91.42, 18.2, 18.1, 20, 21, 22, 23, 24, 25, 10.31, 26, 93.2, 27, 28, 10.32, 29, 93.1, 93.19, 58.13, 58.12, 93.13, 58.11, 93.12, 93.11, 22.11, 58.19, 22.12, 82.4, 29.3, 10.39, 29.2, 29.1, 30, 31, 81.30, 32, 82.9, 33, 35, 36, 10.42, 42.99, 37, 10.41, 38, 39, 22.24, 22.25, 22.26, 32.50, 58.21, 22.21, 22.22, 22.23, 58.29, 81.21, 81.22, 81.23, 42.91, 41, 42, 43, 20.59, 49, 10.11, 32.40, 10.13, 10.12, 09.10, 20.51, 50, 51, 52, 05.1, 53, 05.2, 55, 80.0, 93.29, 56, 58, 10.20, 59, 93.21, 32.30, 71.11, 71.12, 30.91, 30.92, 30.99, 60, 61, 62, 20.60, 63, 16.2, 64, 16.1, 65, 66, 91.1, 68, 69, 91.4, 91.2, 27.9, 91.3, 32.20, 71.20, 70, 20.30, 71, 27.5, 72, 27.4, 73, 27.3, 74, 27.2, 75, 27.1, 77, 78, 79, 32.11, 38.1, 38.2, 38.3, 32.12, 32.13, 80, 20.42, 81, 20.41, 82, 84, 85, 86, 87, 14.10, 88, 66.19, 24.51, 46.82, 49.1, 24.52, 46.83, 49.2, 24.53, 49.3, 24.54, 46.81, 49.4, 49.5, 90, 91, 92, 93, 46.89, 94, 46.86, 66.11, 95, 46.87, 96, 66.12, 46.84, 97, 46.85, 98, 14.21, 86.97, 99, 14.22, 86.95, 86.96, 86.93, 86.94, 14.23, 86.91, 14.24, 66.29, 86.92, 14.2, 46.71, 14.1, 46.72, 14.29, 66.22, 46.73, 86.99, 66.21, 64.99, 78.20, 25.2, 25.1, 46.61, 24.31, 24.32, 24.33, 24.34, 64.92, 25.9, 66.30, 64.91, 25.6, 46.64, 25.5, 25.4, 46.62, 25.3, 46.63, 78.10, 24.41, 46.50, 24.42, 36.0, 24.43, 24.44, 24.45, 24.46, 10.92, 46.48, 46.49, 56.11, 56.12, 36.00, 91.11, 91.12, 10.91, 47.3, 47.4, 47.5, 24.10, 47.6, 47.7, 47.8, 47.9, 46.46, 46.47, 46.44, 46.45, 46.42, 46.43, 47.1, 46.41, 09.90, 46.37, 46.38, 56.21, 56.22, 24.20, 46.36, 46.33, 46.34, 46.31, 46.32, 58.1, 58.2, 10.71, 10.73, 10.72, 91.30, 56.30, 23.4, 23.3, 23.2, 23.1, 46.24, 46.22, 23.9, 46.23, 23.7, 46.21, 23.6, 68.12, 69.2, 23.5, 68.11, 69.1, 10.82, 10.81, 32.91, 88.99, 10.84, 46.19, 10.83, 10.86, 46.17, 10.85, 46.18, 46.15, 46.16, 32.99, 88.91, 91.22, 56.40, 91.21, 46.13, 10.89, 46.14, 68.20, 46.11, 46.12
  (fonte: incentivi.gov.it, campo Codici_ATECO)

**Esito:** errori piccoli

**Requisiti del bando che la regola non ha:** Qui chiaramente serve che l'impresa abbia un brevetto o lo voglia fare. Le condizioni son giuste, ma rimane da verificare che abbia appena inventato qualcosa da brevettare (il nome comunque è auto esplicativo e ci sta che vada fra quelle compatibili)

---

## 19. CCIAA Bergamo - Bando di concorso per l’assegnazione di voucher a favore delle imprese della provincia di Bergamo per interventi di formazione - Anno 2026

- **Link:** https://www.bg.camcom.it/bandi/voucher-intersettoriali-formazione-2026
- **Ente:** Camera di Commercio, Industria, Artigianato e Agricoltura di Bergamo · **origine:** open data · **date:** apertura 2026-04-01, chiusura 2026-12-15 · **file:** `8400`
- **Visto da:** 2 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* regione della sede, uno fra: Lombardia
  (fonte: incentivi.gov.it, campo Regioni)
- *controllato:* tipo di soggetto, almeno uno fra: Impresa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Grande Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Agroalimentare, Alberghiero, Altri servizi, Artigianato, Autoveicoli e altri mezzi di trasporto, Chimica e Farmaceutica, Commercio, Cultura, Edilizia, Elettronica, Fornitura Energia, Acqua e gestione Rifiuti, ICT, Meccanica, Metallurgia, Mobili, Legno e Carta, Moda e Tessile, Ristorazione, Salute, Servizi di trasporto, Turismo
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** errori piccoli

**Requisiti del bando che la regola non ha:** Rimane da controllare a mano, cioè fra i requisiti successivi: «a favore delle imprese con sede in Italia e almeno una sede legale od operativa nella provincia di Bergamo» Questo problema si fixa inserendo anche per le imprese, come per le persone, almeno la provincia della sede legale

---

## 20. CCIAA Brescia - Contributi diretti all'acquisizione di servizi e di consulenze specialistiche in tema di sostenibilità ambientale - AGEF 2605 - Anno 2026

- **Link:** https://bs.camcom.it/bandi-e-contributi/bandi-di-contributo-camerali/sostenibilita
- **Ente:** Camera di Commercio, Industria, Artigianato e Agricoltura di Brescia · **origine:** open data · **date:** apertura 2026-03-16, chiusura 2027-01-29 · **file:** `7958`
- **Visto da:** 2 imprese di prova su 15 (compatibile o possibile)

*Open data: i requisiti sono i filtri che incentivi.gov.it scrive per il bando (tipo di soggetto, dimensione, settore, regione, codici ATECO). Domanda principale: il bando ha condizioni che il portale non riporta (un settore, una regione, una dimensione, un tipo di progetto), per cui un'impresa qui "compatibile" in realtà non lo è?*

**Requisiti della regola:**

- *controllato:* regione della sede, uno fra: Lombardia
  (fonte: incentivi.gov.it, campo Regioni)
- *controllato:* tipo di soggetto, almeno uno fra: Impresa
  (fonte: incentivi.gov.it, campo Tipologia_Soggetto)
- *controllato:* dimensione, uno fra: Microimpresa, Media Impresa, Piccola Impresa
  (fonte: incentivi.gov.it, campo Dimensioni)
- *controllato:* settore, almeno uno fra: Agricoltura, silvicoltura e pesca, Agroalimentare, Alberghiero, Altri servizi, Artigianato, Chimica e Farmaceutica, Commercio, Edilizia, Meccanica, Metallurgia, Moda e Tessile, Ristorazione, Servizi di trasporto, Turismo
  (fonte: incentivi.gov.it, campo Settore_Attivita)

**Esito:** errori piccoli, nota: "Come prima, bisogna inserire il fatto che oltre la regione va anche la provincia."

**Requisiti del bando che la regola non ha:** «A favore delle micro, piccole e medie imprese bresciane operanti in tutti i settori economici» non devono solo essere lombarde, ma anche bresciane.

---
