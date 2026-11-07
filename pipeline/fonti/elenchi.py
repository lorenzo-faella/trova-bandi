"""Raccolta dalle pagine elenco dei bandi (regioni, poi comuni): trova i bandi, li scarica e ne salva il testo.

Per ogni fonte di data/fonti/elenchi.yaml:
  1. legge le pagine dell'elenco una dopo l'altra, finché una pagina non porta link nuovi;
  2. tiene i link che sembrano pagine di un bando (`link_bando`) e salva l'elenco in data/raw/elenchi/<fonte>_<giorno>.json:
     confrontando due giorni si vedono i bandi nuovi;
  3. per ogni bando scarica la pagina e, se c'è, il PDF del testo ufficiale (il primo link che corrisponde a `allegato`),
     e salva tutto come documento in data/raw/documenti/, nello stesso formato di pipeline/fonti/documenti.py.
Si raccoglie tutto, senza decidere ancora se il bando è per persone, imprese o enti: lo dirà l'estrazione.
Cortesia: robots.txt, una richiesta al giorno per indirizzo, pausa tra le richieste (pipeline/fonti/documenti.py).

Uso: python -m pipeline.fonti.elenchi <fonte> [--max N]     --max: solo i primi N bandi (per provare)
"""
import datetime as dt
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml

from pipeline.fonti import documenti as dc

CONFIG = dc.ROOT / "data" / "fonti" / "elenchi.yaml"
DIR_ELENCHI = dc.ROOT / "data" / "raw" / "elenchi"
MAX_PAGINE = 50
# href con virgolette doppie, singole o senza (la Sicilia scrive href=/system/files/...pdf).
LINK = re.compile(r"""<a\b[^>]*?href=(?:"([^"#]+)"|'([^'#]+)'|([^\s>"'#]+))[^>]*>(.*?)</a>""", re.S | re.I)


def pausa(url, giorno):
    """Pausa di cortesia, ma solo se si sta per chiedere davvero qualcosa al sito."""
    if not dc.file_cache(url, giorno).exists():
        time.sleep(dc.PAUSA)


def link(pagina_html, base):
    """[(url assoluto, testo del link)] di una pagina HTML."""
    out = []
    for doppie, singole, nude, testo in LINK.findall(pagina_html):
        href = doppie or singole or nude
        testo = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", testo))).strip()
        testo = re.sub(r"^(per saperne di più su|leggi di più|vai al bando)\s*:?\s*", "", testo, flags=re.I)
        out.append((urljoin(base, html.unescape(href)), testo))
    return out


def slug(testo, n=50):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:n].strip("-")


def bandi_in_elenco(fonte, giorno, scarica=dc.scarica):
    """{url del bando: titolo} da tutte le pagine dell'elenco."""
    trovati, buono = {}, re.compile(fonte["link_bando"])
    escludi = re.compile(fonte["escludi"]) if fonte.get("escludi") else None
    for n in range(fonte.get("prima_pagina", 1), MAX_PAGINE + 1):
        url = fonte["pagine"].format(n=n) if "{n}" in fonte["pagine"] else fonte["pagine"]
        dati, _, _ = scarica(url, giorno)
        nuovi = {u: t for u, t in link(dati.decode("utf-8", "replace"), url)
                 if buono.search(u) and not (escludi and escludi.search(u)) and t and u not in trovati}
        if not nuovi:
            break
        trovati.update(nuovi)
        if "{n}" not in fonte["pagine"]:
            break
        pausa(fonte["pagine"].format(n=n + 1), giorno)
    return trovati


def allegato_principale(pagina_html, base, fonte):
    """Il link al testo ufficiale del bando, se la pagina ne ha uno."""
    regole = fonte.get("allegato") or []
    regole = [regole] if isinstance(regole, str) else regole
    documenti = [(u, t) for u, t in link(pagina_html, base)
                 if re.search(r"\.pdf|Contenuto\.xml|/documents/|download|allegat|/files/", u, re.I)]
    for regola in regole:  # in ordine di preferenza: prima "Bando", poi "Allegato A"…
        for u, t in documenti:
            if re.search(regola, t, re.I):
                return u
    return None


def raccogli_bando(fonte, url, titolo, giorno, scarica=dc.scarica):
    dati, tipo, nota = scarica(url, giorno)
    # Il titolo tagliato non basta: bandi con lo stesso inizio ("08 giugno 2026 - ST Catania - ...") si
    # sovrascrivevano. Le 6 cifre dall'indirizzo rendono l'id unico e stabile da un giorno all'altro.
    doc = {"id": f"{fonte['id']}-{slug(titolo, 40)}-{hashlib.sha1(url.encode()).hexdigest()[:6]}", "titolo": titolo, "ente": fonte["ente"], "livello": fonte["livello"],
           "regione": fonte.get("regione"), "comune": fonte.get("comune"), "pubblico": fonte.get("pubblico"), "url": url,
           "fonte_elenco": fonte["id"], "scaricato": giorno, "note_download": [nota] if nota else [],
           **(dc.testo_pdf(dati) if dc.e_pdf(dati, tipo) else dc.testo_html(dati))}
    allegato = None if doc["tipo"] == "pdf" else allegato_principale(dati.decode("utf-8", "replace"), url, fonte)
    if allegato:
        pausa(allegato, giorno)
        try:
            dati_pdf, tipo_pdf, _ = scarica(allegato, giorno)
            if dc.e_pdf(dati_pdf, tipo_pdf):
                pdf = dc.testo_pdf(dati_pdf)
                doc.update(allegato=allegato, pagine=doc["pagine"] + pdf["pagine"],
                           ocr_necessario=pdf["ocr_necessario"], pagine_allegato=len(pdf["pagine"]))
        except (PermissionError, urllib.error.URLError, TimeoutError) as e:
            doc["note_download"].append(f"allegato non scaricato: {e}")
    return doc


def main(nome, massimo=None):
    fonte = next(f for f in yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["fonti"] if f["id"] == nome)
    giorno = dt.date.today().isoformat()
    bandi = bandi_in_elenco(fonte, giorno)
    DIR_ELENCHI.mkdir(parents=True, exist_ok=True)
    (DIR_ELENCHI / f"{nome}_{giorno}.json").write_text(json.dumps(
        {"fonte": nome, "giorno": giorno, "bandi": [{"url": u, "titolo": t} for u, t in bandi.items()]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nome}: {len(bandi)} bandi nell'elenco")
    dc.USCITA.mkdir(parents=True, exist_ok=True)
    fatti = 0
    for url, titolo in list(bandi.items())[:massimo]:
        pausa(url, giorno)
        try:
            doc = raccogli_bando(fonte, url, titolo, giorno)
        except (PermissionError, urllib.error.URLError, TimeoutError) as e:
            print(f"NO   {url}: {e}")
            continue
        (dc.USCITA / f"{doc['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        fatti += 1
        extra = f" + PDF di {doc['pagine_allegato']} pagine" if doc.get("allegato") else ""
        print(f"ok   {doc['id']}: {doc['tipo']}{extra}", flush=True)
    print(f"{nome}: {fatti} bandi salvati in {dc.USCITA}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    massimo = int(a[a.index("--max") + 1]) if "--max" in a else None
    main(a[0], massimo)
