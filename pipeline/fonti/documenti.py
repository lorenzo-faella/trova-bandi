"""Fonte generica: un bando su un sito qualsiasi (regione, comune, ministero), come pagina web o PDF.

Per ogni documento elencato in data/fonti/documenti.yaml scarica la pagina, ne ricava il testo e lo salva in
data/raw/documenti/<id>.json, con le pagine separate per i PDF: l'estrattore (pipeline/estrai_documenti.py) cita da qui.

Regole di cortesia (brief): si rispetta robots.txt, una richiesta per documento al giorno (il file scaricato resta in
data/cache/documenti/, fuori da git) e qualche secondo di pausa tra un sito e l'altro.
Un PDF quasi senza testo è una scansione: viene segnato `ocr_necessario` e non si estrae.

Uso: python -m pipeline.fonti.documenti [id ...]     senza id, tutti i documenti dell'elenco
I PDF richiedono pypdf (pip install pypdf); le pagine web no.
"""
import datetime as dt
import hashlib
import html.parser
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path
from urllib.parse import quote, urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
ELENCO = ROOT / "data" / "fonti" / "documenti.yaml"
USCITA = ROOT / "data" / "raw" / "documenti"
CACHE = ROOT / "data" / "cache" / "documenti"
UA = "trova-bandi (progetto universitario Bocconi 20875)"
PAUSA = 3.0
# Sotto questa media di caratteri per pagina un PDF è quasi certamente una scansione.
MIN_CARATTERI_PAGINA = 200


class Testo(html.parser.HTMLParser):
    """Testo leggibile di una pagina: una riga per blocco, senza menu, intestazioni, piè di pagina e script.
    Se la pagina ha <main> o <article>, si tiene solo quello."""
    BLOCCHI = {"p", "li", "div", "br", "h1", "h2", "h3", "h4", "h5", "tr", "td", "th", "section", "article", "dd", "dt"}
    IGNORA = {"script", "style", "noscript", "svg", "nav", "header", "footer", "form", "button", "aside"}
    PRINCIPALI = {"main", "article"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ignora = 0
        self.principale = 0
        self.tutto, self.solo_principale = [], []
        self.titolo, self.in_titolo = "", False

    def handle_starttag(self, tag, attrs):
        if tag in self.IGNORA:
            self.ignora += 1
        if tag in self.PRINCIPALI:
            self.principale += 1
        if tag == "title":
            self.in_titolo = True
        if tag in self.BLOCCHI:
            self._aggiungi("\n")

    def handle_endtag(self, tag):
        if tag in self.IGNORA and self.ignora:
            self.ignora -= 1
        if tag in self.PRINCIPALI and self.principale:
            self.principale -= 1
        if tag == "title":
            self.in_titolo = False
        if tag in self.BLOCCHI:
            self._aggiungi("\n")

    def handle_data(self, data):
        if self.in_titolo:
            self.titolo += data
        elif not self.ignora:
            self._aggiungi(data)

    def _aggiungi(self, pezzo):
        self.tutto.append(pezzo)
        if self.principale:
            self.solo_principale.append(pezzo)

    def risultato(self):
        pezzi = self.solo_principale if "".join(self.solo_principale).strip() else self.tutto
        return pulisci("".join(pezzi))


def pulisci(testo):
    righe = [re.sub(r"[ \t ]+", " ", r).strip() for r in testo.splitlines()]
    return "\n".join(r for r in righe if r)


def testo_html(dati):
    parser = Testo()
    parser.feed(dati.decode("utf-8", "replace"))
    return {"tipo": "html", "titolo_pagina": pulisci(parser.titolo), "pagine": [parser.risultato()]}


def testo_pdf(dati):
    try:
        import pypdf  # solo per i PDF: il resto del progetto gira senza
    except ImportError:
        sys.exit("per i PDF serve pypdf: pip install pypdf")
    lettore = pypdf.PdfReader(io.BytesIO(dati))
    pagine = [pulisci(p.extract_text() or "") for p in lettore.pages]
    media = sum(map(len, pagine)) / max(1, len(pagine))
    return {"tipo": "pdf", "titolo_pagina": "", "pagine": pagine, "ocr_necessario": media < MIN_CARATTERI_PAGINA}


def e_pdf(dati, tipo_contenuto):
    return dati[:5] == b"%PDF-" or "pdf" in (tipo_contenuto or "").lower()


_robots = {}


def ammesso(url):
    """robots.txt del sito; se non si riesce a leggerlo, si procede ma lo si annota."""
    p = urlparse(url)
    radice = f"{p.scheme}://{p.netloc}"
    if radice not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            req = urllib.request.Request(radice + "/robots.txt", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                rp.parse(r.read().decode("utf-8", "replace").splitlines())
            _robots[radice] = rp
        except urllib.error.HTTPError as e:
            # Convenzione di robots.txt: 401/403 vuol dire "vietato a tutti", 404 "nessun divieto".
            _robots[radice] = "vietato" if e.code in (401, 403) else None
        except (urllib.error.URLError, TimeoutError):
            _robots[radice] = None
    if _robots[radice] == "vietato":
        return False, "robots.txt protetto (401/403)"
    rp = _robots[radice]
    return (True, "robots.txt non leggibile") if rp is None else (rp.can_fetch(UA, url), "")


def file_cache(url, giorno):
    return CACHE / f"{hashlib.sha1(url.encode()).hexdigest()[:16]}_{giorno}.bin"


def scarica(url, giorno=None):
    """(byte, tipo di contenuto, nota). Al massimo una richiesta al giorno per URL: poi si usa la copia locale."""
    giorno = giorno or dt.date.today().isoformat()
    cache = file_cache(url, giorno)
    if cache.exists():
        meta = json.loads(cache.with_suffix(".json").read_text(encoding="utf-8"))
        return cache.read_bytes(), meta["tipo"], "dalla copia di oggi"
    ok, nota = ammesso(url)
    if not ok:
        raise PermissionError(f"robots.txt non permette di scaricare {url}")
    # Gli indirizzi possono contenere caratteri non ASCII (ALFA Liguria: l'apostrofo ’): si codificano come fa il browser.
    # Accept è un'intestazione standard che ogni browser manda: alcuni siti (Sistema Puglia) senza rispondono 406.
    req = urllib.request.Request(quote(url, safe=":/?&=%#+,;@!$'()*~[]"),
                                 headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
                                          "Accept-Language": "it-IT,it;q=0.9"})
    with urllib.request.urlopen(req, timeout=60) as r:
        dati, tipo = r.read(), r.headers.get("Content-Type", "")
    CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(dati)
    cache.with_suffix(".json").write_text(json.dumps({"url": url, "tipo": tipo}), encoding="utf-8")
    return dati, tipo, nota


def documento(voce, giorno=None):
    dati, tipo, nota = scarica(voce["url"], giorno)
    estratto = testo_pdf(dati) if e_pdf(dati, tipo) else testo_html(dati)
    return {**{k: voce.get(k) for k in ("id", "titolo", "ente", "livello", "regione", "comune", "pubblico", "url")},
            "scaricato": giorno or dt.date.today().isoformat(), "sha256": hashlib.sha256(dati).hexdigest(),
            "note_download": [nota] if nota else [], **estratto}


def testo_completo(doc):
    """Il testo su cui si controllano le citazioni: tutte le pagine di seguito."""
    return "\n".join(doc["pagine"])


def elenco():
    return yaml.safe_load(ELENCO.read_text(encoding="utf-8"))["documenti"]


def main(ids):
    voci = [v for v in elenco() if not ids or v["id"] in ids]
    USCITA.mkdir(parents=True, exist_ok=True)
    ultimo_sito = None
    for v in voci:
        sito = urlparse(v["url"]).netloc
        if ultimo_sito is not None:
            time.sleep(PAUSA if sito != ultimo_sito else PAUSA * 2)
        ultimo_sito = sito
        try:
            doc = documento(v)
        except (PermissionError, OSError) as e:
            print(f"NO   {v['id']}: {e}")
            continue
        (USCITA / f"{v['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        avviso = " ⚠ scansione: serve OCR" if doc.get("ocr_necessario") else ""
        print(f"ok   {v['id']}: {doc['tipo']}, {len(doc['pagine'])} pagine, {len(testo_completo(doc))} caratteri{avviso}")


if __name__ == "__main__":
    main(sys.argv[1:])
