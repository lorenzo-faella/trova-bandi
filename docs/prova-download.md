# Prova di download automatico

*Generato da `prove/prova_download.py` il 2026-10-29 10:12: non modificare a mano.*

| esito | livello | fonte | HTTP | dettaglio |
|---|---|---|---|---|
| OK | controllo | [incentivi.gov.it (già usato da scarica.py)](https://www.incentivi.gov.it/it) | 200 | 7,060 caratteri di testo, 41 link, 4 parole tipo 'bando/bonus/contributo' |
| OK | nazionale | [INPS, home page](https://www.inps.it/) | 200 | 58,656 caratteri di testo, 1257 link, 102 parole tipo 'bando/bonus/contributo' |
| OK | nazionale | [INPS, pagina open data](https://www.inps.it/dati-ricerche-e-bilanci/open-data) | 200 | 54,176 caratteri di testo, 1477 link, 82 parole tipo 'bando/bonus/contributo' |
| OK | nazionale | [Agenzia delle Entrate, portale](https://www.agenziaentrate.gov.it/portale/) | 200 | 3,607 caratteri di testo, 35 link, 2 parole tipo 'bando/bonus/contributo' (robots.txt non leggibile) |
| OK | regionale | [Regione Siciliana, elenco bandi](https://www.regione.sicilia.it/istituzioni/servizi-informativi/bandi) | 200 | 5,582 caratteri di testo, 139 link, 16 parole tipo 'bando/bonus/contributo' |
| OK | regionale | [Regione Lombardia, PDF Dote Scuola 2026](https://www.regione.lombardia.it/content/dam/rl/canali-tematici-servizi/03-istruzione-formazione-e-lavoro/02-dote-scuola/red-dote-scuola-2026/allegati/dgr-5707-2_02_2026-allegato-a.pdf) | 200 | PDF con testo (202 KB) |
| OK | comunale | [Comune di Genova, PDF fondo affitti 2026](https://www.comune.genova.it/sites/default/files/2026-02/REQUISITI%20E%20CRITERI%20BANDO%20FSA%202026.pdf) | 200 | PDF con testo (1445 KB) |
| NON LEGGIBILE | comunale | [Comune di Cassano d'Adda (piattaforma municipiumapp), PDF Dote Scuola](https://cassano-d-adda-api.municipiumapp.it/s3/1553/allegati/notizie/dote-scuola-2026-2027.pdf) | 200 | PDF senza font: probabilmente una scansione, servirebbe l'OCR |

## Riepilogo per livello (almeno una fonte OK)

- controllo: sì
- nazionale: sì
- regionale: sì
- comunale: sì

**Esito: FATTIBILE: ogni livello ha almeno una fonte scaricabile e leggibile da un programma.**
