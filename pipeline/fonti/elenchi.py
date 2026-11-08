"""Raccolta dalle pagine elenco dei bandi (regioni, poi comuni): trova i bandi, li scarica e ne salva il testo.

Per ogni fonte di data/fonti/elenchi.yaml:
  1. legge le pagine dell'elenco una dopo l'altra, finché una pagina non porta link nuovi;
  2. tiene i link che sembrano pagine di un bando (`link_bando`) e salva l'elenco in data/raw/elenchi/<fonte>_<giorno>.json:
     confrontando due giorni si vedono i bandi nuovi;
  3. per ogni bando scarica la pagina e, se c'è, il PDF del testo ufficiale (il primo link che corrisponde a `allegato`),
     e salva tutto come documento in data/raw/documenti/, nello stesso formato di pipeline/fonti/documenti.py.
Si raccoglie tutto, senza decidere ancora se il bando è per persone, imprese o enti: lo dirà l'estrazione.
Cortesia: robots.txt, una richiesta al giorno per indirizzo, pausa tra le richieste (pipeline/fonti/documenti.py), più
lunga se robots.txt la chiede (Crawl-delay) o la fonte ha `pausa`.
Fonti senza un elenco leggibile: `dal_portale` prende i bandi aperti del portale incentivi.gov.it con il link su quel sito.

Uso: python -m pipeline.fonti.elenchi <fonte> [--max N] [--solo-mancanti]
  --max: solo i primi N bandi (per provare)
  --solo-mancanti: riprova solo le voci dell'ultimo elenco senza documento (dopo errori di rete)
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
from urllib.parse import unquote, urljoin, urlparse

import yaml

from pipeline.fonti import documenti as dc

CONFIG = dc.ROOT / "data" / "fonti" / "elenchi.yaml"
DIR_ELENCHI = dc.ROOT / "data" / "raw" / "elenchi"
MAX_PAGINE = 50
# href con virgolette doppie, singole o senza (la Sicilia scrive href=/system/files/...pdf).
LINK = re.compile(r"""<a\b[^>]*?href=(?:"([^"#]+)"|'([^'#]+)'|([^\s>"'#]+))[^>]*>(.*?)</a>""", re.S | re.I)
# Testi di link che non dicono di quale bando si tratta ("DETTAGLI", "Per maggiori informazioni", ":"): non sono titoli.
# Si trattano come link senza testo, così vale il titolo di un altro link allo stesso bando, o quello della pagina.
GENERICO = re.compile(r"^(dettagli|scopri( di più)?|scopri lo strumento|per maggiori informazioni|maggiori informazioni|"
                      r"approfondisci|continua a leggere|vai alla notizia|vai alla pagina|visita|link|read more|clicca qui|leggi( di più| tutto)?|per saperne di più|https?://\S+|"
                      r"visualizza i documenti( \(\d+\))?|leggi il bando( >>)?|[\W\d_]*)$", re.I)


def pausa(url, giorno, minimo=None):
    """Pausa di cortesia, ma solo se si sta per chiedere davvero qualcosa al sito (Crawl-delay compreso)."""
    if not dc.file_cache(url, giorno).exists():
        time.sleep(dc.attesa(url, minimo))


# Nomi delle regioni come nell'export del portale -> come nel resto del progetto (pipeline/fonti/inventario.py).
NOMI_REGIONI = {"Trentino-Alto Adige/Südtirol": "Trentino-Alto Adige", "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta"}


def ultimo_export():
    files = sorted(f for f in (dc.ROOT / "data" / "raw").glob("incentivi_export_*.json") if not f.name.endswith(".meta.json"))
    if not files:
        sys.exit("manca l'export di incentivi.gov.it: make scarica")
    return json.loads(files[-1].read_text(encoding="utf-8"))


def bandi_dal_portale(fonte, giorno, export=None):
    """{url: titolo} dei bandi aperti oggi sul portale incentivi.gov.it il cui link è su questo sito (`dal_portale`).

    Per i siti che non hanno un elenco leggibile (Trento, Bolzano: il catalogo passa da indirizzi vietati da robots.txt)
    ma le cui pagine dei singoli bandi sono permesse. Limite: si vedono solo i bandi che il portale conosce.
    """
    export = ultimo_export() if export is None else export
    siti = re.compile(fonte["dal_portale"])
    escludi = re.compile(fonte["escludi"]) if fonte.get("escludi") else None  # pagine generiche: ricerche, home
    trovati = {}
    for x in export:
        url = (x.get("Link_istituzionale") or "").split("#")[0].strip()
        a, c = (x.get("Data_apertura") or "")[:10], (x.get("Data_chiusura") or "")[:10]
        # `solo_regione`: lo stesso sito può avere bandi di più regioni (albocamerale.camcom.it): si tengono quelli della fonte
        regioni = [NOMI_REGIONI.get(r, r) for r in (x.get("Regioni") or [])] if isinstance(x.get("Regioni"), list) else \
                  [NOMI_REGIONI.get(r.strip(), r.strip()) for r in str(x.get("Regioni") or "").split(",") if r.strip()]
        if fonte.get("solo_regione") and regioni != [fonte["regione"]]:
            continue
        if url and siti.search(url) and not (escludi and escludi.search(url)) and (not a or a <= giorno) and (not c or c >= giorno) and url not in trovati:
            trovati[url] = (x.get("Titolo") or "").strip()
    return trovati


def link(pagina_html, base, pulisci=None):
    """[(url assoluto, testo del link)] di una pagina HTML. `pulisci`: parte degli indirizzi da togliere, per esempio
    il codice di sessione (";jsessionid=..."), che cambia a ogni visita e cambierebbe l'id del bando ogni giorno."""
    out = []
    for doppie, singole, nude, testo in LINK.findall(pagina_html):
        href = doppie or singole or nude
        testo = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", testo))).strip()
        testo = re.sub(r"^(per saperne di più su|leggi di più|leggi tutto|vai al bando|su(?=\s*:))\s*:?\s*", "", testo, flags=re.I)
        testo = re.sub(r"\s+(approfondisci|scopri di più|leggi tutto)$", "", testo, flags=re.I)  # "Microimprese Approfondisci"
        testo = re.sub(r"^[.\s]*-->\s*", "", testo)  # resto di un commento HTML a metà (ERSU Cagliari)
        if GENERICO.match(testo):
            testo = ""
        url = urljoin(base, html.unescape(href))
        out.append((re.sub(pulisci, "", url) if pulisci else url, testo))
    return out


def link_da_js(pagina_html, regola):
    """Riscrive <a href="#" onclick="Apri(event, 'cartella/bando')"> come <a href="/cartella/bando">: `regola` è
    un'espressione regolare con un gruppo, l'indirizzo (relativo alla radice del sito, se non comincia con http)."""
    rx = re.compile(regola)

    def riscrivi(m):
        g = rx.search(html.unescape(m.group(0)))
        if not g:
            return m.group(0)
        u = g.group(1)
        return f'<a href="{u if u.startswith("http") else "/" + u.lstrip("/")}">'
    return re.sub(r"<a\b[^>]*>", riscrivi, pagina_html)


def contenuto(pagina_html):
    """La parte principale della pagina: <main>, altrimenti <article>, altrimenti il corpo senza nav, header, footer, aside."""
    for tag in ("main", "article"):
        m = re.search(rf"<{tag}\b.*?</{tag}>", pagina_html, re.S | re.I)
        if m:
            return m.group(0)
    return re.sub(r"<(nav|header|footer|aside)\b.*?</\1>", " ", pagina_html, flags=re.S | re.I)


def slug(testo, n=50):
    t = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:n].strip("-")


def bandi_in_elenco(fonte, giorno, scarica=dc.scarica):
    """{url del bando: titolo} da tutte le pagine dell'elenco."""
    if fonte.get("dal_portale"):
        return bandi_dal_portale(fonte, giorno)
    if isinstance(fonte["pagine"], list):  # più pagine elenco fisse per la stessa fonte (es. Valle d'Aosta, lavoro)
        trovati = {}
        for i, pagina in enumerate(fonte["pagine"]):
            if i:
                pausa(pagina, giorno)
            trovati.update({u: t for u, t in bandi_in_elenco({**fonte, "pagine": pagina}, giorno, scarica).items()
                            if u not in trovati})
        return trovati
    trovati, buono = {}, re.compile(fonte["link_bando"])
    escludi = re.compile(fonte["escludi"]) if fonte.get("escludi") else None
    for n in range(fonte.get("prima_pagina", 1), MAX_PAGINE + 1):
        url = fonte["pagine"].format(n=n) if "{n}" in fonte["pagine"] else fonte["pagine"]
        try:
            dati, _, _ = scarica(url, giorno)
        except urllib.error.HTTPError as e:
            if e.code == 404 and n > fonte.get("prima_pagina", 1):  # dopo l'ultima pagina (WordPress): fine dell'elenco
                break
            raise
        pagina_html = dati.decode("utf-8", "replace")
        if fonte.get("link_js"):  # link con href="#" e l'indirizzo in un comando JavaScript (Valle d'Aosta Lavoro):
            pagina_html = link_da_js(pagina_html, fonte["link_js"])  # si legge l'indirizzo, senza eseguire niente
        if fonte.get("solo_contenuto"):  # i bandi sono i link del contenuto, non di menu, intestazione e piè di pagina
            pagina_html = contenuto(pagina_html)
        tutti = link(pagina_html, url, fonte.get("pulisci_url"))
        if fonte.get("solo_contenuto"):
            tutti = [(u, t) for u, t in tutti if len(t) >= 20 and u.rstrip("/") != url.rstrip("/")]
        # Uno stesso bando può avere più link (titolo, "Scadenza ... Chiuso"): si scarta se uno qualsiasi lo esclude.
        chiusi = {u for u, t in tutti if fonte.get("escludi_testo") and re.search(fonte["escludi_testo"], t or "", re.I)}
        if fonte.get("escludi_contesto"):  # stato scritto subito prima del link ("... Chiuso <a href=...>Titolo</a>")
            pagina_html = dati.decode("utf-8", "replace")
            for m in re.finditer(r'<a\b[^>]*?href=["\']?([^"\'\s>]+)', pagina_html):
                prima = re.sub(r"<[^>]+>", " ", pagina_html[max(0, m.start() - 250):m.start()])
                ultimo = prima.split("Scadenza")[-1]  # solo il testo dopo la scheda precedente
                if re.search(fonte["escludi_contesto"], ultimo, re.I):
                    chiusi.add(urljoin(url, html.unescape(m.group(1))))
        senza_titolo = fonte.get("titolo_dalla_pagina")  # link senza testo (icona "Dettaglio"): titolo dalla pagina
        # Se un bando ha più link (titolo e "DETTAGLI"), vale il testo più lungo: prima vinceva l'ultimo.
        nuovi = {}
        for u, t in tutti:
            if buono.search(u) and not (escludi and escludi.search(u)) and (t or senza_titolo) and u not in trovati \
                    and u not in chiusi and (u not in nuovi or len(t) > len(nuovi[u])):
                nuovi[u] = t
        if fonte.get("testo_bando"):  # siti che mescolano bandi e pagine informative (FVG): si tiene solo chi ne parla
            nuovi = {u: t for u, t in nuovi.items() if re.search(fonte["testo_bando"], t, re.I)}
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
    documenti = [(u, t) for u, t in link(pagina_html, base, fonte.get("pulisci_url"))
                 if re.search(r"\.pdf|Contenuto\.xml|/documents/|download|allegat|/files/|/attachments/", u, re.I)]
    for regola in regole:  # in ordine di preferenza: prima "Bando", poi "Allegato A"…
        for u, t in documenti:
            # `allegato_nome_file`: se i link dicono solo "Download" o niente (FILSE, Finmolise), si guarda anche il
            # nome del file, che può stare anche dopo il "?" ("download.php?id=3125:bando-...pdf").
            nome = unquote(u.rsplit("/", 1)[-1]) if fonte.get("allegato_nome_file") else ""
            if re.search(regola, t, re.I) or (nome and re.search(regola, nome, re.I)):
                return u
    return None


def raccogli_bando(fonte, url, titolo, giorno, scarica=dc.scarica):
    dati, tipo, nota = scarica(url, giorno)
    if not titolo:
        letto = dc.testo_html(dati)
        testo = letto["pagine"][0]
        # `titolo_da`: dove sta il titolo, se non è la prima riga del testo. Si cerca nel <title> della pagina e poi
        # nel testo (Gepafin: "^(.+) - Gepafin$" nel <title>; Sardegna Ricerche: "^Oggetto: (.+)$" nel testo).
        m = re.search(fonte["titolo_da"], f"{letto['titolo_pagina']}\n{testo}", re.M) if fonte.get("titolo_da") else None
        righe = [r for r in testo.splitlines() if len(r) > 15 and r.lower() != "indietro"]
        titolo = m.group(1).strip()[:300] if m else righe[0][:300] if righe else url
    # Il titolo tagliato non basta: bandi con lo stesso inizio ("08 giugno 2026 - ST Catania - ...") si
    # sovrascrivevano. Le 6 cifre dall'indirizzo rendono l'id unico e stabile da un giorno all'altro.
    doc = {"id": f"{fonte['id']}-{slug(titolo, 40)}-{hashlib.sha1(url.encode()).hexdigest()[:6]}", "titolo": titolo, "ente": fonte["ente"], "livello": fonte["livello"],
           "regione": fonte.get("regione"), "comune": fonte.get("comune"), "pubblico": fonte.get("pubblico"), "url": url,
           "fonte_elenco": fonte["id"], "scaricato": giorno, "note_download": [nota] if nota else [],
           **(dc.testo_pdf(dati) if dc.e_pdf(dati, tipo) else dc.testo_html(dati))}
    allegato = None if doc["tipo"] == "pdf" else allegato_principale(dati.decode("utf-8", "replace"), url, fonte)
    if allegato:
        pausa(allegato, giorno, fonte.get("pausa"))
        try:
            dati_pdf, tipo_pdf, _ = scarica(allegato, giorno)
            if dc.e_pdf(dati_pdf, tipo_pdf):
                pdf = dc.testo_pdf(dati_pdf)
                doc.update(allegato=allegato, pagine=doc["pagine"] + pdf["pagine"],
                           ocr_necessario=pdf["ocr_necessario"], pagine_allegato=len(pdf["pagine"]))
        except (PermissionError, OSError) as e:
            doc["note_download"].append(f"allegato non scaricato: {e}")
    return doc


def tutte_le_fonti():
    """Le fonti scritte a mano (elenchi.yaml) e quelle generate per Camere di commercio (camere.yaml) e comuni (comuni.yaml)."""
    fonti = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["fonti"]
    for nome in ("camere.yaml", "comuni.yaml"):
        f = CONFIG.with_name(nome)
        if f.exists():
            fonti += yaml.safe_load(f.read_text(encoding="utf-8")).get("fonti", [])
    return fonti


def mancanti(nome, cartella_elenchi=None, cartella_documenti=None):
    """{url: titolo} delle voci dell'ultimo elenco salvato della fonte che non hanno ancora un documento: per riprovare
    dopo errori di rete senza rileggere l'elenco né riscaricare i bandi già salvati."""
    cartella_elenchi, cartella_documenti = cartella_elenchi or DIR_ELENCHI, cartella_documenti or dc.USCITA
    ultimo = sorted(cartella_elenchi.glob(f"{nome}_????-??-??.json"))[-1]
    fatti = set()
    for f in cartella_documenti.glob(f"{nome}-*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("fonte_elenco") == nome:
            fatti.add(d["url"])
    return {b["url"]: b["titolo"] for b in json.loads(ultimo.read_text(encoding="utf-8"))["bandi"] if b["url"] not in fatti}


def main(nome, massimo=None, solo_mancanti=False):
    fonte = next(f for f in tutte_le_fonti() if f["id"] == nome)
    giorno = dt.date.today().isoformat()
    if solo_mancanti:
        bandi = mancanti(nome)
        print(f"{nome}: {len(bandi)} voci dell'ultimo elenco senza documento")
    else:
        bandi = bandi_in_elenco(fonte, giorno)
        DIR_ELENCHI.mkdir(parents=True, exist_ok=True)
        (DIR_ELENCHI / f"{nome}_{giorno}.json").write_text(json.dumps(
            {"fonte": nome, "giorno": giorno, "bandi": [{"url": u, "titolo": t} for u, t in bandi.items()]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{nome}: {len(bandi)} bandi nell'elenco")
    dc.USCITA.mkdir(parents=True, exist_ok=True)
    fatti = 0
    for url, titolo in list(bandi.items())[:massimo]:
        pausa(url, giorno, fonte.get("pausa"))
        try:
            doc = raccogli_bando(fonte, url, titolo, giorno)
        except (PermissionError, OSError) as e:
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
    main(a[0], massimo, "--solo-mancanti" in a)
