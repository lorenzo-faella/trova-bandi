"""Regole probabilmente scadute e doppioni, da decidere a mano (decisione 91).

Un bando che risulta aperto ma è di anni fa ("bando 2023-2024", nessuna data di chiusura) è l'errore che si nota di più
in una demo. Qui non si cancella niente: si scrive un elenco in docs/regole-vecchie.md, e una persona decide.

Si guardano solo le regole senza chiusura: con una chiusura passata la demo le nasconde già, con una futura sono aperte.
Segnalazioni:
- "scadenza nel testo": il documento scrive "Data scadenza: 31/12/2025" (o "data di chiusura", "scadenza avviso"...)
  e la data più recente scritta così è passata: è il segnale più affidabile (decisione 100);
- "anno vecchio": l'anno più recente scritto nel titolo è prima di quello di oggi (un anno accademico "2025/2026"
  conta come 2026, quindi non viene segnalato);
- "aperta da troppo": apertura di più di due anni fa;
- "doppione": stessa regione e titoli quasi uguali (almeno l'80% delle parole in comune), da enti o pagine diversi.
Le regole già controllate a mano e ancora aperte (per esempio "L.R. 34/2004", dove l'anno è quello della legge) sono in
data/pubblico/vecchie-controllate.yaml e non si segnalano più.

Uso: python -m pipeline.vecchie [AAAA-MM-GG]
"""
import datetime as dt
import re
import sys
from itertools import combinations
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CARTELLE = [ROOT / "data" / "regole_estratte" / "documenti", ROOT / "data" / "regole_imprese_documenti"]
USCITA = ROOT / "docs" / "regole-vecchie.md"
CONTROLLATE = ROOT / "data" / "pubblico" / "vecchie-controllate.yaml"
MESI = {m: i + 1 for i, m in enumerate("gennaio febbraio marzo aprile maggio giugno luglio agosto settembre ottobre "
                                       "novembre dicembre".split())}
ETICHETTA = re.compile(r"(?:data (?:di )?scadenza|data di chiusura|scadenza (?:avviso|bando|domande)|chiusura (?:bando|"
                       r"sportello|domande))\s*:?\s*(?:ore \d{1,2}[:.]\d\d (?:del )?)?(\d{1,2})[/. -](\d{1,2}|[a-z]+)[/. -](20\d\d)",
                       re.I)
VUOTE = set("di del della dei delle e per il la le lo gli i a al alle in con da su un una anno bando avviso pubblico "
            "contributi contributo domanda domande".split())


def anno_piu_recente(titolo):
    """L'anno più recente scritto nel titolo ("a.a. 2025/2026" e "2025-26" valgono 2026), o None."""
    anni = [int(a) for a in re.findall(r"\b(20\d\d)\b", titolo)]
    anni += [2000 + int(b) for b in re.findall(r"\b20\d\d\s*[/-]\s*(\d\d)\b", titolo)]
    return max(anni) if anni else None


def scadenza_nel_testo(testo):
    """La data più recente scritta come scadenza ("Data scadenza: 31/12/2025", "DATA DI CHIUSURA ... 15/06/2021"), o None."""
    date = []
    for g, m, a in ETICHETTA.findall(testo or ""):
        try:
            date.append(dt.date(int(a), MESI.get(m.lower()) or int(m), int(g)))
        except ValueError:
            pass
    return max(date) if date else None


def parole(titolo):
    return {w for w in re.findall(r"[a-zà-ù0-9]+", titolo.lower()) if len(w) > 2 and w not in VUOTE}


def segnalazioni(regole, oggi, controllate=()):
    fuori = []
    for r in regole:
        chiusura, apertura = r.get("chiusura"), r.get("apertura")
        if chiusura or r.get("id") in controllate:
            continue
        anno, scritta = anno_piu_recente(r["titolo"]), scadenza_nel_testo(r.get("_testo"))
        if scritta and scritta < oggi:
            fuori.append((r, f"il testo scrive la scadenza {scritta.isoformat()}"))
        elif anno and anno < oggi.year:
            fuori.append((r, f"anno vecchio nel titolo ({anno})"))
        elif apertura and not chiusura and apertura < (oggi - dt.timedelta(days=730)).isoformat():
            fuori.append((r, f"aperta dal {apertura}, senza chiusura"))
    doppi = []
    for a, b in combinations(regole, 2):
        pa, pb = parole(a["titolo"]), parole(b["titolo"])
        if pa and pb and a.get("_regione") == b.get("_regione") and len(pa & pb) / len(pa | pb) >= 0.8:
            doppi.append((a, b))
    return fuori, doppi


def carica():
    from pipeline.estrai_documenti import documenti
    from pipeline.fonti.documenti import testo_completo
    from web.domande import territorio
    docs = {d["url"]: d for d in documenti()}
    regole = []
    for cartella in CARTELLE:
        for f in sorted(cartella.glob("*.yaml")):
            r = yaml.safe_load(f.read_text(encoding="utf-8"))
            r["_file"] = str(f.relative_to(ROOT))
            r["_regione"] = territorio(r)
            r["_testo"] = testo_completo(docs[r["link"]]) if r.get("link") in docs else ""
            regole.append(r)
    return regole


def main(oggi):
    regole = carica()
    controllate = yaml.safe_load(CONTROLLATE.read_text(encoding="utf-8")) if CONTROLLATE.exists() else {}
    fuori, doppi = segnalazioni(regole, oggi, set(controllate or {}))
    doppi = [(a, b) for a, b in doppi if not {a["id"], b["id"]} <= set(controllate or {})]
    righe = [f"# Regole probabilmente scadute e doppioni\n",
             f"*Generato da `pipeline/vecchie.py` il {oggi.isoformat()}: non modificare a mano. Non si cancella niente: "
             f"una persona decide: le date si correggono nella regola, le scadute senza data e i doppioni si spostano in "
             f"`scadute/` o `doppioni/`, quelle ancora aperte vanno in `data/pubblico/vecchie-controllate.yaml` "
             f"(decisioni 91, 100).*\n",
             f"{len(regole)} regole controllate: {len(fuori)} probabilmente scadute, {len(doppi)} coppie di possibili doppioni.\n",
             "## Probabilmente scadute\n", "| regola | perché | file |", "|---|---|---|"]
    righe += [f"| [{r['titolo'][:80]}]({r.get('link', '')}) | {motivo} | `{r['_file']}` |" for r, motivo in fuori]
    righe += ["\n## Possibili doppioni\n", "| prima | seconda |", "|---|---|"]
    righe += [f"| {a['titolo'][:70]} (`{Path(a['_file']).stem}`) | {b['titolo'][:70]} (`{Path(b['_file']).stem}`) |"
              for a, b in doppi]
    USCITA.write_text("\n".join(righe) + "\n", encoding="utf-8")
    print(f"{USCITA.relative_to(ROOT)} scritto: {len(fuori)} scadute, {len(doppi)} doppioni su {len(regole)} regole")


if __name__ == "__main__":
    main(dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today())
