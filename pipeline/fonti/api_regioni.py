"""Regioni che caricano l'elenco dei bandi con JavaScript: si interroga la stessa ricerca pubblica che usa il sito.

Sono le richieste che fa il browser aprendo la pagina "Bandi": gratuite e senza chiavi. Una richiesta al giorno per
fonte (copia in data/cache/documenti/), poi si scarica il PDF principale di ogni bando con pipeline/fonti/documenti.py.
Il risultato ha lo stesso formato di pipeline/fonti/elenchi.py: elenco del giorno in data/raw/elenchi/ e un documento
per bando in data/raw/documenti/.

Le gare d'appalto si scartano subito (CIG presente, o parole come "affidamento", "procedura negoziata"):
non sono aiuti a persone o imprese.

Uso: python -m pipeline.fonti.api_regioni <fonte> [--max N]     fonti: sardegna, basilicata
"""
import datetime as dt
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request

from pipeline.fonti import documenti as dc
from pipeline.fonti.elenchi import DIR_ELENCHI, slug

GARA = re.compile(r"affidament|procedura (aperta|negoziata|ristretta)|appalt|\bgara\b|\bcig\b|indagine di mercato|"
                  r"risultati della procedura|aggiudicazion", re.I)
# Il PDF principale, in ordine di preferenza; moduli e fogli di calcolo no.
PDF_PRINCIPALE = [r"^bando", r"\bbando\b", r"^avviso", r"\bavviso\b", r"allegato a\b", r"disposizioni attuative", r"."]
NON_PRINCIPALE = re.compile(r"modell|modul|fac.?simile|domanda di|faq|informativa|privacy", re.I)


def post_json(url, corpo, giorno):
    """POST con risposta JSON, al massimo una al giorno per coppia indirizzo + richiesta."""
    chiave = url + "#" + json.dumps(corpo, sort_keys=True)
    cache = dc.file_cache(chiave, giorno)
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    ok, _ = dc.ammesso(url)
    if not ok:
        raise PermissionError(f"robots.txt non permette {url}")
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"User-Agent": dc.UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        testo = r.read().decode("utf-8")
    dc.CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(testo, encoding="utf-8")
    return json.loads(testo)


def scegli_pdf(documenti):
    """Il documento PDF che più probabilmente è il testo del bando."""
    pdf = [d for d in documenti if (d.get("formato") or "").lower() == "pdf" or d.get("urlFinale", "").lower().endswith(".pdf")]
    candidati = [d for d in pdf if not NON_PRINCIPALE.search(d.get("titolo") or "")] or pdf
    for regola in PDF_PRINCIPALE:
        for d in candidati:
            if re.search(regola, d.get("titolo") or "", re.I):
                return d
    return None


# --- Sardegna: ricerca Elasticsearch del portale (POST /api/search?index=contentrepository) ---

SARDEGNA_API = "https://www.regione.sardegna.it/api/search?index=contentrepository"
SARDEGNA_PAGINA = "https://www.regione.sardegna.it/atti-bandi-archivi/atti-amministrativi/bandi/{slug}"
SARDEGNA_FILE = "https://files.regione.sardegna.it/"


def bandi_sardegna(giorno):
    """[(bando normalizzato)] dei contenuti di tipo BANDO con scadenza futura, gare escluse."""
    corpo = {"body": {"size": 1000, "query": {"bool": {"filter": [
        {"term": {"tipoContenuto.keyword": "BANDO"}}, {"range": {"dataScadenza": {"gte": "now"}}}]}}}}
    risposta = post_json(SARDEGNA_API, corpo, giorno)
    out = []
    for hit in risposta["hits"]["hits"]:
        s = hit["_source"]
        titolo = re.sub(r"\s+", " ", s.get("titolo") or "").strip()
        if s.get("cig") or GARA.search(titolo):
            continue
        pdf = scegli_pdf(s.get("documentiList") or [])
        url_pdf = None
        if pdf:
            u = pdf["urlFinale"].strip()
            url_pdf = u if u.startswith("http") else SARDEGNA_FILE + u
        testo = "\n".join(x for x in [titolo, s.get("oggetto"), s.get("descrizione")] if x)
        out.append({"url": SARDEGNA_PAGINA.format(slug=s["slug"]), "titolo": titolo, "testo": testo, "pdf": url_pdf,
                    "scadenza": (s.get("dataScadenza") or "")[:10] or None, "pubblicato_da": s.get("tipoSoggetto"),
                    "documenti": [d.get("titolo") for d in s.get("documentiList") or []]})
    return out


# --- Basilicata: portale WordPress, interfaccia standard /wp-json/ (tipo di contenuto "avvisi-e-bandi") ---

BASILICATA_API = "https://portalebandi.regione.basilicata.it/wp-json/wp/v2/avvisi-e-bandi"
# L'archivio ha quasi 10.000 voci dal primo giorno: si guardano quelle pubblicate nell'ultimo anno, e di queste si
# tengono quelle con la scadenza scritta nella pagina ancora futura.
BASILICATA_GIORNI = 365
SCADENZA = re.compile(r"Scadenza:\s*(\d{2})/(\d{2})/(\d{4})")
PDF_NOME = re.compile(r"avviso|bando|allegato[-_ ]?(1|a)\b|disciplinare", re.I)


def get_json(url, giorno):
    dati, _, _ = dc.scarica(url, giorno)
    return json.loads(dati.decode("utf-8"))


def bandi_basilicata(giorno):
    dopo = (dt.date.fromisoformat(giorno) - dt.timedelta(days=BASILICATA_GIORNI)).isoformat()
    voci, pagina = [], 1
    while True:
        url = f"{BASILICATA_API}?per_page=100&page={pagina}&after={dopo}T00:00:00&_fields=link,title"
        if pagina > 1 and not dc.file_cache(url, giorno).exists():
            time.sleep(dc.PAUSA)
        try:
            blocco = get_json(url, giorno)
        except urllib.error.HTTPError:  # oltre l'ultima pagina WordPress risponde 400
            break
        if not blocco:
            break
        voci += blocco
        pagina += 1
    out = []
    for v in voci:
        url = v["link"]
        if not dc.file_cache(url, giorno).exists():
            time.sleep(dc.PAUSA)
        dati, _, _ = dc.scarica(url, giorno)
        testo = dc.testo_html(dati)["pagine"][0]
        m = SCADENZA.search(testo)
        scadenza = f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None
        titolo = re.sub(r"\s+", " ", html_testo(v["title"]["rendered"])).strip()
        if (scadenza and scadenza < giorno) or GARA.search(titolo):
            continue
        pdf = [u for u in re.findall(r'href="([^"]+\.pdf)"', dati.decode("utf-8", "replace"), re.I)
               if not NON_PRINCIPALE.search(u.rsplit("/", 1)[-1])]
        principale = next((u for u in pdf if PDF_NOME.search(u.rsplit("/", 1)[-1])), pdf[0] if pdf else None)
        destinatari = re.search(r"Destinatari:\s*([^\n]+)", testo)
        out.append({"url": url, "titolo": titolo, "testo": testo, "pdf": principale, "scadenza": scadenza,
                    "pubblicato_da": destinatari.group(1).strip() if destinatari else None, "documenti": pdf})
    return out


def html_testo(s):
    import html
    return html.unescape(re.sub(r"<[^>]+>", " ", s or ""))


FONTI = {"sardegna": {"id": "sardegna", "ente": "Regione Autonoma della Sardegna", "livello": "regionale",
                      "regione": "Sardegna", "elenco": bandi_sardegna},
         "basilicata": {"id": "basilicata", "ente": "Regione Basilicata", "livello": "regionale",
                        "regione": "Basilicata", "elenco": bandi_basilicata}}


def documento(fonte, b, giorno):
    doc = {"id": f"{fonte['id']}-{slug(b['titolo'], 40)}-{hashlib.sha1(b['url'].encode()).hexdigest()[:6]}",
           "titolo": b["titolo"], "ente": fonte["ente"], "livello": fonte["livello"], "regione": fonte["regione"],
           "comune": None, "pubblico": None, "url": b["url"], "fonte_elenco": fonte["id"], "scaricato": giorno,
           "chiusura_dichiarata": b.get("scadenza"), "pubblicato_da": b.get("pubblicato_da"),
           "documenti_elencati": b.get("documenti"), "note_download": [],
           "tipo": "html", "titolo_pagina": b["titolo"], "pagine": [b["testo"]]}
    if b.get("pdf"):
        if not dc.file_cache(b["pdf"], giorno).exists():
            time.sleep(dc.PAUSA)
        try:
            dati, tipo, _ = dc.scarica(b["pdf"], giorno)
            if dc.e_pdf(dati, tipo):
                pdf = dc.testo_pdf(dati)
                doc.update(allegato=b["pdf"], pagine=doc["pagine"] + pdf["pagine"], ocr_necessario=pdf["ocr_necessario"],
                           pagine_allegato=len(pdf["pagine"]))
        except (PermissionError, urllib.error.URLError, TimeoutError) as e:
            doc["note_download"].append(f"PDF non scaricato: {e}")
    return doc


def main(nome, massimo=None):
    fonte, giorno = FONTI[nome], dt.date.today().isoformat()
    bandi = fonte["elenco"](giorno)
    DIR_ELENCHI.mkdir(parents=True, exist_ok=True)
    (DIR_ELENCHI / f"{nome}_{giorno}.json").write_text(json.dumps(
        {"fonte": nome, "giorno": giorno, "bandi": [{k: b[k] for k in ("url", "titolo", "scadenza")} for b in bandi]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nome}: {len(bandi)} bandi (gare d'appalto escluse)")
    dc.USCITA.mkdir(parents=True, exist_ok=True)
    for b in bandi[:massimo]:
        doc = documento(fonte, b, giorno)
        (dc.USCITA / f"{doc['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        extra = f" + PDF di {doc['pagine_allegato']} pagine" if doc.get("allegato") else " (senza PDF)"
        print(f"ok   {doc['id']}{extra}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in FONTI:
        sys.exit(__doc__)
    main(a[0], int(a[a.index("--max") + 1]) if "--max" in a else None)
