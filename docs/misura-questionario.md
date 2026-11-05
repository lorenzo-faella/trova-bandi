# Misura del questionario adattivo

*Generato da `pipeline/misura.py` il 2026-10-27: non modificare a mano.*

- Bandi aperti il 2026-10-27 e accessibili a imprese: **747**.
- Risposte stimate su 1000 imprese fittizie (seed 1); misura su altre 300 (seed 2).
- Un bando è *deciso* quando sappiamo già se l'impresa è idonea o no.

## Bandi decisi dopo k domande (media, % dei bandi)

| strategia | k=1 | k=2 | k=3 | k=4 | k=5 | k=6 | k=7 |
|---|---|---|---|---|---|---|---|
| modulo fisso (ordine del portale) | 18.2 | 26.6 | 91.0 | 91.8 | 98.9 | 99.3 | 99.6 |
| miglior ordine fisso | 84.4 | 91.2 | 93.6 | 98.3 | 98.9 | 99.3 | 99.6 |
| questionario adattivo | 84.4 | 91.2 | 93.6 | 98.2 | 99.1 | 99.4 | 99.6 |
| oracolo (conosce le risposte) | 85.0 | 92.2 | 93.8 | 98.3 | 99.1 | 99.4 | 99.6 |

Miglior ordine fisso trovato: regione → settore → tipologia → dimensione → comune → ateco_2025 → ambito.
Ordine del portale: tipologia → dimensione → regione → comune → settore → ateco_2025 → ambito.

## Domande necessarie per decidere tutto ciò che si può decidere

| strategia | media | massimo |
|---|---|---|
| modulo fisso (ordine del portale) | 6.58 | 7 |
| questionario adattivo | 6.57 | 7 |
| oracolo (conosce le risposte) | 6.56 | 7 |

## Esiti medi per impresa

| esito | bandi per impresa |
|---|---|
| non idoneo | 682.9 |
| idoneo | 36.0 |
| quasi idoneo | 25.0 |
| mancano dati | 3.1 |

## Imprese scritte a mano

| impresa | domande (ordine adattivo) | idoneo | quasi | mancano dati |
|---|---|---|---|---|
| pizzeria_napoli | regione, settore, tipologia, dimensione, comune, ateco_2025, ambito | 29 | 20 | 1 |
| startup_milano | regione, settore, tipologia, dimensione, comune, ateco_2025, ambito | 71 | 30 | 8 |
| vigna_montalcino | regione, settore, tipologia, dimensione, comune, ambito, ateco_2025 | 30 | 34 | 5 |
| officina_vicenza | regione, settore, tipologia, dimensione, ambito, comune, ateco_2025 | 46 | 16 | 4 |
| hotel_trento | regione, settore, tipologia, dimensione, ambito, ateco_2025 | 66 | 38 | 12 |
| architetto_roma | regione, settore, tipologia, dimensione | 4 | 38 | 0 |
| negozio_palermo | regione, settore, tipologia, dimensione, comune | 5 | 31 | 0 |
| cooperativa_bologna | regione, settore, tipologia, dimensione, comune, ambito, ateco_2025 | 38 | 21 | 3 |
| chimica_bergamo | regione, settore, tipologia, dimensione, comune, ateco_2025, ambito | 36 | 18 | 2 |
| edile_cosenza | regione, settore, tipologia, dimensione, comune, ateco_2025, ambito | 36 | 19 | 6 |

## Tempi

- Preparazione delle matrici: 1.8 s (una volta all'avvio).
- Scelta di una domanda: 3 ms in media.
