"""Segnalazioni automatiche sulle regole estratte -> docs/regole-sospette.md (generato).

Non corregge niente e non cambia gli esiti: ordina le regole da rileggere per prime (decisione 64). Ogni controllo
cerca un errore già visto nelle misure o nelle revisioni:

- soglia assente: un numero che nel testo non compare in nessuna forma (una citazione vera può accompagnare un numero
  inventato; `pipeline/citazioni.py`, soglie_non_trovate);
- lavoro mancante: un beneficio per chi lavora senza nessuna condizione sul lavoro (l'errore più frequente nella misura
  sulle etichette, decisioni 59-60);
- data assente: apertura o chiusura che nel testo non compare (una scadenza sbagliata fa sparire o comparire un bando);
- date invertite: apertura dopo la chiusura;
- solo non modellabili: la regola dà sempre "da verificare", quindi non decide niente.

Uso: python -m pipeline.sospette [cartella ...]     di default le regole estratte che la demo può mostrare
"""
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

from pipeline.citazioni import carica_testi_inps, nodi, normalizza, soglie_non_trovate
from pipeline.fonti.documenti import USCITA as DIR_DOCUMENTI, testo_completo
from pipeline.regole import LOADER, ROOT

CARTELLE = ["data/regole_estratte/lotto-1", "data/regole_estratte/lotto-2", "data/regole_estratte/documenti"]
USCITA = ROOT / "docs" / "regole-sospette.md"
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
        "novembre", "dicembre"]
PER_CHI_LAVORA = re.compile(r"lavorat|dipendent|autonom|congedo|maternit|paternit|disoccupaz|naspi|dis-coll|iscro",
                            re.IGNORECASE)
CAMPI_LAVORO = {"condizione_lavorativa", "tipo_lavoro", "ultimo_lavoro_subordinato", "causa_fine_lavoro",
                "giorni_da_cessazione_lavoro", "settimane_contributi_4_anni", "lavora_in_italia"}


def forme_data(iso):
    """Come può comparire una data in un testo italiano: 31/01/2027, 31.1.27, 31 gennaio 2027, 1° febbraio..."""
    d = dt.date.fromisoformat(iso)
    giorni = {str(d.day), f"{d.day:02d}"} | ({"1°", "1º", "primo"} if d.day == 1 else set())
    mesi = {str(d.month), f"{d.month:02d}"}
    anni = {str(d.year), f"{d.year % 100:02d}"}
    out = {f"{g}{s}{m}{s}{a}" for g in giorni for m in mesi for a in anni for s in "/.-"}
    out |= {f"{g} {MESI[d.month - 1]}" for g in giorni}  # l'anno può mancare o essere lontano ("entro il 31 gennaio")
    return out


def data_nel_testo(iso, testo):
    t = normalizza(testo).lower()
    return any(re.search(rf"(?<![\d]){re.escape(f)}(?![\d])", t) for f in forme_data(iso))


def foglie(regola):
    return [n for req in regola["requisiti"] for n in nodi(req) if "campo" in n or "non_modellabile" in n]


SOGLIA, DATA, INVERTITE, LAVORO, SOLO_NM = ("soglia assente dal testo", "data assente dal testo", "date invertite",
                                            "beneficio per chi lavora senza condizioni sul lavoro",
                                            "solo requisiti non modellabili (sempre \"da verificare\")")


def segnalazioni(regola, testo):
    """[(tipo, dettaglio)] di una regola. `testo` è il testo intero della fonte ('' se non c'è)."""
    out = []
    if testo:
        out += [(SOGLIA, f"`{s}`") for s in soglie_non_trovate(regola, testo)]
        for chiave in ("apertura", "chiusura"):
            if regola.get(chiave) and not data_nel_testo(regola[chiave], testo):
                out.append((DATA, f"{chiave} {regola[chiave]}"))
    if regola.get("apertura") and regola.get("chiusura") and regola["apertura"] > regola["chiusura"]:
        out.append((INVERTITE, f"{regola['apertura']} > {regola['chiusura']}"))
    campi = {n["campo"] for n in foglie(regola) if "campo" in n}
    if PER_CHI_LAVORA.search(regola["titolo"]) and not campi & CAMPI_LAVORO:
        out.append((LAVORO, ""))
    if foglie(regola) and not campi:
        out.append((SOLO_NM, ""))
    return out


def testi_fonte():
    """id o link della regola -> testo intero della fonte: schede INPS per link, documenti per id."""
    inps = carica_testi_inps()
    documenti = {}
    for f in sorted(DIR_DOCUMENTI.glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        documenti[doc["id"]] = testo_completo(doc)
    return lambda regola: documenti.get(regola["id"]) or inps.get(regola["link"], "")


def main(cartelle):
    testo = testi_fonte()
    righe, conta, totale, senza_testo = [], Counter(), 0, 0
    for cartella in cartelle:
        for f in sorted((ROOT / cartella).glob("*.yaml")):
            regola = yaml.load(f.read_text(encoding="utf-8"), Loader=LOADER)
            totale += 1
            t = testo(regola)
            senza_testo += not t
            trovate = segnalazioni(regola, t)
            conta.update({tipo for tipo, _ in trovate})
            if trovate:
                righe.append((len(trovate), Path(cartella).name, regola, trovate))
    righe.sort(key=lambda x: (-x[0], x[1], x[2]["id"]))
    out = [
        "# Regole da rileggere per prime",
        "",
        f"*Generato da `pipeline/sospette.py` il {dt.date.today().isoformat()}: non modificare a mano.*",
        "",
        f"{len(righe)} regole con almeno una segnalazione su {totale} ({', '.join(f'`{c}`' for c in cartelle)}). "
        "Le segnalazioni non sono errori certi: dicono dove guardare. Il metodo è in `docs/decisioni.md`, decisione 64."
        + (f" {senza_testo} regole senza testo della fonte sul disco: su quelle i controlli sul testo non sono fatti."
           if senza_testo else ""),
        "",
        "| segnalazione | regole |",
        "|---|---|",
        *(f"| {s} | {n} |" for s, n in conta.most_common()),
        "",
        "| regola | cartella | segnalazioni |",
        "|---|---|---|",
        *(f"| [{r['titolo'][:70]}]({r['link']}) | {c} | "
          + "; ".join(f"{tipo}: {det}" if det else tipo for tipo, det in s) + " |" for _, c, r, s in righe),
    ]
    USCITA.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{USCITA.relative_to(ROOT)} scritto: {len(righe)} regole segnalate su {totale}")


if __name__ == "__main__":
    main(sys.argv[1:] or CARTELLE)
