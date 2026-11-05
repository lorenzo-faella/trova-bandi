# Etichettare a mano i 15 benefici

Le etichette scritte a mano sono la **verità di riferimento** con cui misureremo l'estrazione dell'LLM: requisiti trovati, sbagliati, inventati. È il numero centrale del report.

**Regola più importante: niente LLM mentre etichetti, e non guardare i file dell'altro.** Altrimenti la misura non vale più.

## Chi fa cosa

I file sono già pronti, con `requisiti: []` da riempire.

| | Benefici |
|---|---|
| `data/gold/lorenzo/` | Assegno sociale, Bonus asilo nido, Bonus psicologo, Bonus mamme 2026, SFL, DIS-COLL |
| `data/gold/edo/` | Maternità autonomi, Carta disabilità, Invalidità, Centri estivi, Congedo vittime di violenza, Discontinuità spettacolo |
| **in entrambe** | ISCRO, Congedo di paternità, Congedo parentale |

I 3 benefici in comune servono a misurare quanto siete d'accordo tra voi: se due persone non concordano, non possiamo pretendere che l'LLM faccia meglio.

## Come si fa (circa 15 minuti a beneficio)

1. Apri il `link` nel file e leggi la scheda: "A chi è rivolto" e "Domanda" soprattutto.
2. Scrivi un requisito per ogni condizione per **avere diritto** al beneficio. Non contano importi e procedure di domanda; i termini entro cui chiederlo sì.
3. Ogni requisito ha `fonte` (la sezione) e `citazione`, copiata **parola per parola** dalla scheda.
4. Usa solo i campi di `docs/vocabolario-persone.md`.
5. **Se un requisito non ci sta, non forzarlo:** scrivi `non_modellabile`, spiegando cosa mancherebbe. Così scopriamo quali campi aggiungere.
6. Controlla con `make controlla`: segnala errori di formato e citazioni che non si trovano nella scheda.

## Esempio

Esempi completi in `data/regole_persone/`. Le forme possibili:

```yaml
requisiti:
  # un numero
  - campo: isee
    operatore: "<="
    valore: 40000
    fonte: scheda INPS, A chi è rivolto
    citazione: "con un valore non superiore ai 40mila euro"
  # sì/no
  - campo: residente_italia
    operatore: vero
    fonte: scheda INPS, Domanda
    citazione: "la residenza in Italia"
  # una scelta da un elenco
  - campo: cittadinanza
    operatore: in
    valori: [italiana, ue]
    fonte: scheda INPS, Domanda
    citazione: "..."
  # alternative (basta una); esiste anche tutti_di
  - almeno_uno_di:
      - {campo: residente_italia, operatore: vero}
      - {campo: lavora_in_italia, operatore: vero}
    fonte: scheda INPS, Domanda
    citazione: "..."
  # un componente della famiglia con queste caratteristiche
  - almeno_un_componente:
      - {campo: eta, operatore: "<", valore: 18}
    fonte: scheda INPS, A chi è rivolto
    citazione: "..."
  # ciò che non sappiamo esprimere
  - non_modellabile: "Serve l'anzianità contributiva: campo da aggiungere."
    fonte: scheda INPS, Domanda
    citazione: "..."
```
