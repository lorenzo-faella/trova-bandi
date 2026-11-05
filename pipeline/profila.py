"""Stadio 6: statistiche di fattibilità sui dati -> docs/fattibilita-dati.md (generato, non scritto a mano).

Uso: python -m pipeline.profila
"""
import json
import re
import time
from collections import Counter
from pathlib import Path

from pipeline.regole import carica

ROOT = Path(__file__).resolve().parent.parent
# Requisiti tipici dei bandi per imprese che NON hanno un campo strutturato: si trovano solo nel testo.
# Ognuno è una domanda che il questionario potrà fare solo dopo l'estrazione dal testo.
NEL_TESTO = {
    "de minimis": r"de minimis",
    "fatturato / ricavi": r"fatturat|ricavi",
    "numero di dipendenti / ULA": r"dipendent|\bULA\b|addett|occupat",
    "sede operativa / unità locale": r"sede operativa|unità locale|unità produttiva",
    "anni di attività / data di costituzione": r"costituit[ae] da|anni di attivit|costituzione|iscritt[ae] al registro",
    "età del titolare / under 35": r"under 3\d|\b(18|35|36|40) anni|giovani",
    "regolarità contributiva (DURC)": r"\bDURC\b|regolarit[aà] contributiva",
    "rating di legalità": r"rating di legalit",
    "certificazioni (ISO, parità di genere)": r"\bISO\b|certificazion",
}


def pct(n, tot):
    return f"{n} ({100 * n / tot:.0f}%)" if tot else "0"


def main():
    dati = json.loads((ROOT / "data" / "processed" / "bandi.json").read_text(encoding="utf-8"))
    bandi = dati["bandi"]
    attivi = [b for b in bandi if b["stato"] != "chiuso"]
    imprese = [b for b in attivi if b["per_imprese"]]
    regole = carica()
    n = len(imprese)

    righe = [
        "# Fattibilità dei dati",
        "",
        f"*Generato da `pipeline/profila.py` il {time.strftime('%Y-%m-%d')} da `{dati['fonte']}` "
        f"(riferimento {dati['riferimento']}): non modificare a mano.*",
        "",
        "## Catalogo",
        "",
        f"- Incentivi nell'export: **{len(bandi)}**. Stato al {dati['riferimento']}: "
        + ", ".join(f"{s} {c}" for s, c in Counter(b["stato"] for b in bandi).most_common()) + ".",
        f"- Non chiusi: **{len(attivi)}**, di cui accessibili ad almeno un tipo di impresa: **{n}**.",
        f"- Nazionali (tutte le 20 regioni): {pct(sum(b['nazionale'] for b in imprese), n)}; "
        f"una sola regione: {pct(sum(len(b['regioni']) == 1 for b in imprese), n)}; "
        f"con elenco di comuni: {pct(sum(bool(b['comuni'] or b['comuni_non_riconosciuti']) for b in imprese), n)}.",
        "",
        "## Beneficiari dei bandi non chiusi",
        "",
        "| tipologia di soggetto | bandi |",
        "|---|---|",
    ]
    righe += [f"| {t} | {c} |" for t, c in Counter(t for b in attivi for t in b["tipologie"]).most_common()]
    req = Counter(q["campo"] for r in regole for q in r["requisiti"])
    righe += [
        "",
        f"## Requisiti strutturati nelle {len(regole)} regole generate",
        "",
        "Un requisito è scritto solo se esclude qualcuno (un bando aperto a tutte le dimensioni non ha il requisito).",
        "",
        "| campo | bandi con il requisito |",
        "|---|---|",
    ]
    righe += [f"| {c} | {pct(k, len(regole))} |" for c, k in req.most_common()]
    versioni = Counter(next(iter(sorted(b["ateco"]["codici"])), "tutti i settori") for b in imprese)
    con_ignoti = [b for b in imprese if b["comuni_non_riconosciuti"]]
    ignoti = Counter(c for b in con_ignoti for c in b["comuni_non_riconosciuti"])
    righe += [
        "",
        "## Problemi di qualità trovati",
        "",
        f"- **Due versioni di ATECO.** Bandi per imprese per versione dei codici: "
        + ", ".join(f"{v}: {c}" for v, c in versioni.most_common())
        + ". Senza etichetta la versione si deduce dalla data di apertura (ATECO 2025 dal 1/4/2025). "
          "I bandi in ATECO 2007 restano \"mancano dati\" finché non usiamo la tavola di raccordo ISTAT.",
        f"- **Comuni soppressi.** {len(con_ignoti)} bandi elencano comuni che nell'elenco ISTAT non esistono più "
        f"({len(ignoti)} nomi distinti, es. {', '.join(c for c, _ in ignoti.most_common(5))}). "
        "Chi ha sede fuori dall'elenco riconosciuto riceve \"mancano dati\", non \"non idoneo\".",
        "- **Entità HTML nei nomi.** `Sant&apos;Agata` conteneva un `;`, il separatore delle liste: "
        "senza decodificare prima, il nome si spezzava in due comuni inesistenti.",
        f"- **Settore assente** in {sum(not b['settori'] for b in imprese)} bandi per imprese: trattato come nessun vincolo.",
        "",
        f"## Requisiti che stanno solo nel testo (descrizioni dei {n} bandi per imprese)",
        "",
        "Conteggio grezzo per parola chiave: indica quante domande in più servirebbero dopo l'estrazione, "
        "non quanti bandi hanno davvero quel requisito.",
        "",
        "| requisito | bandi che lo menzionano |",
        "|---|---|",
    ]
    for nome, pattern in NEL_TESTO.items():
        k = sum(bool(re.search(pattern, b["descrizione"], re.I)) for b in imprese)
        righe.append(f"| {nome} | {pct(k, n)} |")
    out = ROOT / "docs" / "fattibilita-dati.md"
    out.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{out.relative_to(ROOT)} scritto")


if __name__ == "__main__":
    main()
