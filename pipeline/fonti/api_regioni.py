"""Regioni che caricano l'elenco dei bandi con JavaScript: si interroga la stessa ricerca pubblica che usa il sito.

Sono le richieste che fa il browser aprendo la pagina "Bandi": gratuite e senza chiavi. Una richiesta al giorno per
fonte (copia in data/cache/documenti/), poi si scarica il PDF principale di ogni bando con pipeline/fonti/documenti.py.
Il risultato ha lo stesso formato di pipeline/fonti/elenchi.py: elenco del giorno in data/raw/elenchi/ e un documento
per bando in data/raw/documenti/.

Le gare d'appalto si scartano subito (CIG presente, o parole come "affidamento", "procedura negoziata"):
non sono aiuti a persone o imprese.

Uso: python -m pipeline.fonti.api_regioni <fonte> [--max N]     fonti: sardegna, basilicata, lombardia
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


# --- Lombardia: "Bandi e Servizi", ricerca POST /servizi/servizio/catalogo/ricerca (frammento HTML dei risultati) ---

LOMBARDIA_BASE = "https://www.bandi.regione.lombardia.it"
LOMBARDIA_RICERCA = LOMBARDIA_BASE + "/servizi/servizio/catalogo/ricerca"
LOMBARDIA_SCARTA = re.compile(r"concorsi pubblici e avvisi sul personale", re.I)
ALLEGATO_LOMBARDIA = [r"^bando\b", r"\bbando\b", r"^avviso\b", r"\bavviso\b", r"allegato (a|1)\b", r"decreto|d\.d\.|d\.g\.r"]
_sessione = None


def post_form(url, campi, giorno):
    """POST di un modulo (come il browser), al massimo uno al giorno per richiesta. Il sito vuole un cookie di
    sessione: lo prende una volta aprendo la pagina del catalogo."""
    global _sessione
    import http.cookiejar
    from urllib.parse import urlencode
    corpo = urlencode(campi)
    cache = dc.file_cache(url + "#" + corpo, giorno)
    if cache.exists():
        return cache.read_text(encoding="utf-8")
    ok, _ = dc.ammesso(url)
    if not ok:
        raise PermissionError(f"robots.txt non permette {url}")
    if _sessione is None:
        _sessione = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        _sessione.open(urllib.request.Request(LOMBARDIA_BASE + "/servizi/servizio/catalogo",
                                              headers={"User-Agent": dc.UA}), timeout=60).read()
        time.sleep(dc.PAUSA)
    req = urllib.request.Request(url, data=corpo.encode(), method="POST",
                                 headers={"User-Agent": dc.UA, "Referer": LOMBARDIA_BASE + "/servizi/servizio/catalogo"})
    with _sessione.open(req, timeout=120) as r:
        testo = r.read().decode("utf-8", "replace")
    dc.CACHE.mkdir(parents=True, exist_ok=True)
    cache.write_text(testo, encoding="utf-8")
    return testo


ICONE_LOMBARDIA = {"citizen": "persone", "factory": "imprese", "ente": "enti"}


def pubblico_lombardia(etichette):
    """persone, imprese o enti se la scheda ha un solo tipo di destinatari; con più tipi None: lo dirà l'estrazione."""
    return etichette[0] if len(etichette) == 1 else None


def bandi_lombardia(giorno):
    """Le schede con stato "Aperto", 100 per pagina; si scartano concorsi e avvisi sul personale."""
    import html as H
    out, pagina, ultima = [], 1, 1
    while pagina <= ultima:
        campi = {"titolo": "", "descrizione": "", "ricercaAvanzata": "true", "pageNum": pagina, "maxPageNum": 0,
                 "targetStr": "ALL", "tableView": "true", "pageSize": 100, "stato[0]": "APERTO"}
        if pagina > 1 and not dc.file_cache(LOMBARDIA_RICERCA, giorno).exists():
            time.sleep(dc.PAUSA)
        h = post_form(LOMBARDIA_RICERCA, campi, giorno)
        m = re.search(r"Pagina \d+ di (\d+)", h)
        ultima = int(m.group(1)) if m else pagina
        for scheda in h.split('class="card card-bg card-big"')[1:]:
            href = re.search(r'href="(/servizi/servizio/catalogo/dettaglio/[^"]+)"', scheda)
            if not href:
                continue
            testo = lambda rx: (lambda x: H.unescape(re.sub(r"\s+", " ", x.group(1))).strip() if x else None)(re.search(rx, scheda, re.S))
            tipologia = testo(r'<p class="mt-1"\s*>([^<]+)</p>')
            titolo = testo(r'alt="([^"]+)"') or href.group(1)
            if (tipologia and LOMBARDIA_SCARTA.search(tipologia)) or GARA.search(titolo) or re.search(r"acquisizione (del|di) (servizi|forniture)", titolo, re.I):
                continue
            # Destinatari dalle icone: con più destinatari la scheda mostra solo le icone, senza testo.
            icone = re.findall(r'<span class="categoria"\s*>\s*<svg class="icon">\s*<use xlink:href="[^"]*#it-aria-([a-z-]+)"', scheda)
            etichette = sorted({ICONE_LOMBARDIA.get(i, i) for i in icone})
            destinatari = ", ".join(etichette) or None
            out.append({"url": LOMBARDIA_BASE + href.group(1), "titolo": titolo,
                        "testo": None, "pdf": None, "scadenza": (testo(r'class="checkCloseDate" type="hidden" value="([^"]+)"') or "")[:10] or None,
                        "pubblicato_da": None, "destinatari": destinatari, "tipologia": tipologia, "documenti": None,
                        "pubblico": pubblico_lombardia(etichette)})
        pagina += 1
    return out


FONTI = {"sardegna": {"id": "sardegna", "ente": "Regione Autonoma della Sardegna", "livello": "regionale",
                      "regione": "Sardegna", "elenco": bandi_sardegna},
         "basilicata": {"id": "basilicata", "ente": "Regione Basilicata", "livello": "regionale",
                        "regione": "Basilicata", "elenco": bandi_basilicata},
         "lombardia": {"id": "lombardia", "ente": "Regione Lombardia", "livello": "regionale",
                       "regione": "Lombardia", "elenco": bandi_lombardia, "allegato": ALLEGATO_LOMBARDIA}}


def documento(fonte, b, giorno):
    doc = {"id": f"{fonte['id']}-{slug(b['titolo'], 40)}-{hashlib.sha1(b['url'].encode()).hexdigest()[:6]}",
           "titolo": b["titolo"], "ente": fonte["ente"], "livello": fonte["livello"], "regione": fonte["regione"],
           "comune": None, "pubblico": None, "url": b["url"], "fonte_elenco": fonte["id"], "scaricato": giorno,
           "chiusura_dichiarata": b.get("scadenza"), "pubblicato_da": b.get("pubblicato_da"),
           "documenti_elencati": b.get("documenti"), "note_download": [],
           "tipo": "html", "titolo_pagina": b["titolo"], "pagine": [b["testo"] or ""],
           "destinatari_dichiarati": b.get("destinatari"), "tipologia_dichiarata": b.get("tipologia")}
    if b.get("pubblico"):
        doc["pubblico"] = b["pubblico"]
    if b.get("testo") is None:  # l'elenco dà solo il link: testo e PDF stanno nella pagina del bando
        from pipeline.fonti.elenchi import allegato_principale
        if not dc.file_cache(b["url"], giorno).exists():
            time.sleep(dc.PAUSA)
        dati, _, _ = dc.scarica(b["url"], giorno)
        doc["pagine"] = [dc.testo_html(dati)["pagine"][0]]
        b = {**b, "pdf": allegato_principale(dati.decode("utf-8", "replace"), b["url"], fonte)}
    if b.get("pdf"):
        if not dc.file_cache(b["pdf"], giorno).exists():
            time.sleep(dc.PAUSA)
        try:
            dati, tipo, _ = dc.scarica(b["pdf"], giorno)
            if dc.e_pdf(dati, tipo):
                pdf = dc.testo_pdf(dati)
                doc.update(allegato=b["pdf"], pagine=doc["pagine"] + pdf["pagine"], ocr_necessario=pdf["ocr_necessario"],
                           pagine_allegato=len(pdf["pagine"]))
        except (PermissionError, OSError) as e:
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
        try:
            doc = documento(fonte, b, giorno)
        except (PermissionError, OSError) as e:  # un bando che non si scarica non ferma gli altri
            print(f"NO   {b['url']}: {e}")
            continue
        (dc.USCITA / f"{doc['id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        extra = f" + PDF di {doc['pagine_allegato']} pagine" if doc.get("allegato") else " (senza PDF)"
        print(f"ok   {doc['id']}{extra}", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in FONTI:
        sys.exit(__doc__)
    main(a[0], int(a[a.index("--max") + 1]) if "--max" in a else None)
