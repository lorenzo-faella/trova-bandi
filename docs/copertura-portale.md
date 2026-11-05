# Quanto copre incentivi.gov.it? (prima verifica, 28/10/2026)

Domanda (Edoardo): 747 bandi aperti alle imprese sembrano pochi per tutta Italia. Il portale contiene davvero tutto?

**Risposta breve: no.** 747 sono i bandi *pubblicati sul portale*, non quelli esistenti. Il portale copre bene alcune regioni e male altre. Per i bonus ai cittadini non copre quasi niente, e non deve farlo per legge.

## 1. Cosa dice la legge

- La piattaforma è istituita dall'art. 18-ter del D.L. 34/2019. La sezione sulle misure delle altre amministrazioni (regioni, enti locali) è dedicata alle misure "di sostegno al **tessuto produttivo**" ed è alimentata per interoperabilità con il Registro nazionale degli aiuti di Stato.
- Secondo l'art. 8, comma 3, della L. 160/2023, la pubblicità legale degli incentivi è assicurata dalla pubblicazione **sui siti istituzionali** delle amministrazioni, oltre che dalla pubblicazione delle informazioni sulla piattaforma.
- Il Codice degli incentivi (D.Lgs. 184/2025, in vigore dal 1/1/2026) rafforza il sistema "Incentivi Italia", con il portale integrato con il Registro aiuti. I servizi però sono "progressivamente implementati".
- Conseguenze:
  - il portale nasce per le **imprese**, quindi i bonus per le famiglie sono fuori per costruzione;
  - la fonte legale resta il sito di ogni ente;
  - la completezza del portale dipende da quanto ogni amministrazione lo alimenta.
- ⚠ Non abbiamo letto gli articoli del D.Lgs. 184/2025 sugli obblighi di pubblicazione (normattiva ha restituito solo l'art. 1). Da completare.

## 2. Cosa dicono i nostri dati (`data/raw/incentivi_export_2026-10-27.json`)

**Distribuzione molto irregolare tra regioni.** Bandi aperti il 27/10 per regione singola:

| | bandi aperti |
|---|---|
| Trentino-Alto Adige | 129 |
| Lombardia | 99 |
| Friuli-Venezia Giulia | 75 |
| … | |
| Sicilia | 21 |
| Lazio | 19 |
| Campania | 18 |

Che il Trentino abbia sei volte i bandi della Sicilia non è credibile come quadro reale. Indica che alcune amministrazioni caricano tutto e altre poco.

**Chi pubblica** (bandi aperti): regioni e province autonome 426, ministeri e agenzie nazionali 105, Camere di Commercio 100, comuni 56, altri 84. I comuni italiani sono circa 7.900: ne compaiono pochissimi.

**I grandi bonus per i cittadini non ci sono.** Nessun titolo nell'intero catalogo (6.007 incentivi, anche chiusi) contiene: bonus psicologo, assegno unico, carta dedicata a te, bonus nuovi nati, bonus elettrodomestici, bonus asilo nido, carta della cultura o del merito.

## 3. Prova a campione: bandi reali 2025-2026 cercati nel catalogo

Bandi trovati sul web (giornali, siti di enti e associazioni), cercati per titolo nell'export completo:

| bando | ente | sul portale? |
|---|---|---|
| Sicilia che piace 2026 (soggetti privati) | Regione Siciliana | sì |
| Sicilia efficiente (ott. 2025) | Regione Siciliana | **no** |
| Ripresa Sicilia Plus (ott. 2025) | Regione Siciliana | **no** |
| Open Innovation Sicilia (ott. 2025) | Regione Siciliana | **no** |
| Riqualificazione del capitale umano (ott. 2025) | Regione Siciliana | **no** |
| Rafforza&Innova | Regione Lombardia | sì |
| Musei d'impresa 2026 | Regione Lombardia | sì |
| Nuova Impresa 2026 | Unioncamere Lombardia | sì |
| Basket bond Lombardia | Regione Lombardia | sì |
| Ri.Circo.Lo. (edizioni 2024-2025) | Regione Lombardia | sì; l'edizione 2026 citata da un aggregatore **no** (da verificare che esista) |
| SI4.0 2026 | Unioncamere Lombardia | **no** (presenti 2023 e 2024; edizione 2026 citata solo da un aggregatore, da verificare) |
| Donne e impresa 2026 | Lazio Innova | sì |
| Valore artigiano 2026 | Regione Lazio | **no** (presente solo l'edizione 2025) |
| Digital Export 2026-2027 | Unioncamere Emilia-Romagna | sì |
| Voucher 3I | nazionale | sì |

Risultato grezzo: **9 trovati su 15**. Escludendo i 2 non verificati, 9 su 13 (circa 70%). Tutti e 4 i bandi FESR siciliani di ottobre 2025 mancano.

⚠ Limiti: il campione è piccolo e scelto a caso tra le notizie, non estratto in modo sistematico. I numeri indicano una tendenza, non una stima affidabile.

## 4. Cosa significa per il progetto

1. **Obiettivo: tutti i bandi aperti in Italia** (decisione 23, presa il 29/10). Il portale da solo non basta, quindi aggiungiamo altre fonti e raccontiamo nel report come e con quali difficoltà. Per restare corretti, dichiariamo sempre le fonti coperte e misuriamo la copertura. La copertura incompleta del portale è **un ostacolo vero da raccontare**, ed è proprio ciò che il prof chiede.
2. Per le **imprese** il portale resta la base migliore: è ufficiale, strutturato e aggiornato ogni giorno. Va però integrato almeno per le regioni dimostrative con le fonti regionali. Candidate: Sicilia (scarsa sul portale) e Lombardia (ben coperta), così il confronto è anche un risultato.
3. Per le **persone fisiche** il portale non basta per costruzione. Servono altre fonti: INPS, Agenzia delle Entrate, siti regionali e comunali. È tutto testo libero, da estrarre.
4. **Misura sistematica possibile:** prendere l'elenco ufficiale dei bandi di 1-2 regioni (portale regionale o bollettino) per un periodo fisso e contare quanti stanno su incentivi.gov.it. Dà un numero di copertura citabile.

## Fonti

- [Art. 18-ter D.L. 34/2019 e art. 8 L. 160/2023, richiamati nel D.Lgs. 184/2025 (Normattiva)](https://www.normattiva.it/eli/id/2025/12/10/25G00192/CONSOLIDATED/20260821)
- [Codice degli incentivi, sintesi (ildiritto.it)](https://ildiritto.it/amministrativo/codice-degli-incentivi-cosa-prevede/) e [Edotto](https://edotto.com/articolo/nuovo-codice-degli-incentivi-dal-2026)
- [Bandi FESR Sicilia, ottobre 2025 (Balarm)](https://www.balarm.it/news/oltre-160-milioni-di-incentivi-per-le-imprese-in-sicilia-chi-puo-richiederli-e-come-159221); [Sicilia efficiente (ANCE Enna)](https://enna.ance.it/2025/10/23/regione-siciliana-pubblicato-il-bando-sicilia-efficiente-meno-consumi-piu-futuro-per-lo-sviluppo-sostenibile-delle-imprese-siciliane/?print=pdf)
- [Bandi Lombardia 2026 (Rete Agevolazioni, aggregatore)](https://www.reteagevolazioni.it/bandi-regione-lombardia/)
- [Valore artigiano 2026 (PartitaIVA.it)](https://www.partitaiva.it/bando-valore-artigiano-2026/)
