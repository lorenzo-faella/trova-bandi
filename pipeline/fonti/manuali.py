"""Bandi salvati a mano da una persona, per i siti che i programmi non possono leggere (decisione 49).

Alcuni siti rifiutano i programmi: il Comune di Milano e Milano Abitare rispondono 403 anche a robots.txt, la Regione
Marche ha un captcha. Una persona invece li apre normalmente. Qui non si scavalca niente: la persona apre il bando nel
suo browser, lo salva (PDF, o la pagina con "Salva come" in HTML) in data/raw/manuali/, e lo descrive in
data/fonti/manuali.yaml (id, titolo, ente, livello, regione, comune, pubblico, url della pagina, file salvato).
Questo modulo ne estrae il testo come per gli altri documenti e lo salva in data/raw/documenti/, con
fonte_elenco "manuale": così l'inventario non lo conta come un sito sorvegliato.

Uso: python -m pipeline.fonti.manuali
"""
import datetime as dt
import hashlib
import json
import sys

import yaml

from pipeline.fonti import documenti as dc

ELENCO = dc.ROOT / "data" / "fonti" / "manuali.yaml"
CARTELLA = dc.ROOT / "data" / "raw" / "manuali"
CAMPI = ("id", "titolo", "ente", "livello", "regione", "comune", "pubblico", "url")


def documento(voce, cartella=CARTELLA):
    """Il documento nel formato di data/raw/documenti/, dal file salvato a mano."""
    dati = (cartella / voce["file"]).read_bytes()
    estratto = dc.testo_pdf(dati) if dc.e_pdf(dati, "") else dc.testo_html(dati)
    return {**{k: voce.get(k) for k in CAMPI}, "fonte_elenco": "manuale", "file_manuale": voce["file"],
            "scaricato": voce.get("salvato") or dt.date.today().isoformat(),
            "sha256": hashlib.sha256(dati).hexdigest(), "note_download": ["salvato a mano da una persona"], **estratto}


def main():
    if not ELENCO.exists():
        sys.exit(f"manca {ELENCO}: va scritto a mano, una voce per file salvato")
    dc.USCITA.mkdir(parents=True, exist_ok=True)
    for voce in yaml.safe_load(ELENCO.read_text(encoding="utf-8")).get("documenti") or []:
        try:
            doc = documento(voce)
        except FileNotFoundError:
            print(f"NO   {voce['id']}: manca il file {CARTELLA / voce['file']}")
            continue
        (dc.USCITA / f"{voce['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"ok   {voce['id']}: {doc['tipo']}, {len(doc['pagine'])} pagine")


if __name__ == "__main__":
    main()
