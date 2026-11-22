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

Uso: python -m pipeline.fonti.elenchi <fonte> [--max N] [--solo-mancanti | --nuovi]
  --max: solo i primi N bandi (per provare)
  --solo-mancanti: riprova solo le voci dell'ultimo elenco senza documento (dopo errori di rete)
  --nuovi: rilegge l'elenco ma scarica solo i bandi che non hanno ancora un documento (aggiornamento veloce: a 3 secondi
           di pausa per pagina e PDF, riscaricare 150 bandi già salvati costa più di 20 minuti per fonte)
       python -m pipeline.fonti.elenchi --rinvii <id documento ...>
  per documenti già salvati da pagine di annuncio: segue il rinvio al PDF del bando (decisione 102)
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


# Pagine di annuncio (decisioni 102-103): una pagina breve che annuncia il bando e rimanda al PDF con i requisiti, o a
# una pagina dello stesso ente dove sta il PDF. Si segue il rinvio dentro lo stesso sito (stesso dominio, anche un
# sottodominio come servizionline.comune.x.it); un PDF su un altro sito (l'archivio dei file del portale comunale) solo
# se sia il link sia il nome del file dicono "bando" o "avviso". Fra i PDF si preferisce il bando, l'avviso o l'allegato
# A, poi gli atti che li approvano (decreto, determina); mai moduli, graduatorie, informative, versioni in inglese.
BREVE = 3000
DOCUMENTO_RINVIO = re.compile(r"\.pdf($|\?)|/download|/attachments?/|/files/|/documents/|/uploads/|allegat|ServeBLOB|output_immagine", re.I)
# (?<![a-z]) invece di \b: nei nomi dei file "LC_Allegato A_Bando" il trattino basso conta come lettera per \b
NON_LETTERA = r"(?<![a-zà-ù])"
PDF_BANDO = re.compile(NON_LETTERA + r"(bando|avviso)|allegato[ _-]?a(?![a-z])|regolamento|disciplinare|requisiti|criteri|"
                       r"foglio[ _-]informativo", re.I)
PDF_ATTO = re.compile(NON_LETTERA + r"(delibera|determina|disposizione|decreto)", re.I)
PDF_SCARTA = re.compile(r"modul|modello di domanda|schema di domanda|fac-?simile|privacy|informativa|dpia|graduatori|elenc|esiti|ammess|curricul|"
                        r"dichiarazion|delega|manifesto|locandina|faq|guida isee|istruzioni|_eng\b|\binglese\b|english|\.(png|jpe?g|gif|svg)$", re.I)
BANDO_ALTROVE = re.compile(NON_LETTERA + r"(bando|avviso)", re.I)
PAGINA_RINVIO = re.compile(NON_LETTERA + r"(bando|avviso)|requisiti|leggi il|vai (al|la) bando", re.I)
VUOTE = {"bando", "avviso", "pubblico", "della", "delle", "degli", "nella", "anno", "accademico", "comune", "regione",
         "contributo", "contributi", "domande", "domanda", "presentazione", "concessione", "assegnazione", "pagina"}


def dominio(url):
    return ".".join(urlparse(url).netloc.lower().split(":")[0].split(".")[-2:])


def parole(testo):
    return {p for p in re.findall(r"[a-zà-ù]{5,}", testo.lower()) if p not in VUOTE}


def anno_passato(testo, giorno):
    """Il testo nomina solo anni accademici già finiti ("Bando 2025/2026" a novembre 2026): è l'edizione vecchia."""
    anni = [int(a) for a, _ in re.findall(r"(20\d\d)\s*[/-]\s*((?:20)?\d\d)\b", testo)]
    if not anni:
        return False
    y, m = int(giorno[:4]), int(giorno[5:7])
    return max(anni) < (y if m >= 9 else y - 1)


def pdf_del_bando(pagina_html, base, gia=(), giorno=None):
    """Il link al PDF del bando dentro il contenuto principale della pagina, o None: prima bando, avviso, allegato A;
    poi decreto o determina che li approvano."""
    migliori = {}
    for u, t in link(contenuto(pagina_html), base):
        u = u.split("#")[0]
        nome = unquote(u.rsplit("/", 1)[-1])
        testo = f"{t} {nome}"
        if u in gia or not DOCUMENTO_RINVIO.search(u) or PDF_SCARTA.search(testo) or (giorno and anno_passato(testo, giorno)):
            continue
        if dominio(u) != dominio(base) and not (re.search(r"\.pdf($|\?)", u, re.I) and BANDO_ALTROVE.search(t) and BANDO_ALTROVE.search(nome)):
            continue
        punti = 2 if PDF_BANDO.search(testo) and not PDF_ATTO.search(testo) else 1 if PDF_BANDO.search(testo) or PDF_ATTO.search(testo) else 0
        if punti:
            migliori.setdefault((punti, dominio(u) == dominio(base)), u)
    return next((migliori[k] for k in sorted(migliori, reverse=True)), None)  # a pari livello, prima lo stesso sito


def pagine_intermedie(pagina_html, doc, gia, giorno):
    """Le pagine dello stesso ente a cui l'annuncio rimanda: un link "Leggi il bando" o "Avviso …" che ha almeno due
    parole in comune con il titolo del bando (non l'avviso della mensa sulla pagina delle borse), oppure un link senza
    testo all'Amministrazione trasparente, dove gli enti pubblici devono pubblicare gli avvisi."""
    titolo = parole(doc.get("titolo") or "")
    out = []
    for u, t in link(contenuto(pagina_html), doc["url"]):
        u = u.split("#")[0]
        if dominio(u) != dominio(doc["url"]) or u in gia or DOCUMENTO_RINVIO.search(u) or anno_passato(t, giorno):
            continue
        generico = re.search(r"leggi il|vai (al|la) bando", t, re.I)
        if (PAGINA_RINVIO.search(t) and (generico or len(parole(t) & titolo) >= 2)) or (not t and re.search(r"trasparen", u, re.I)):
            out.append(u)
    return list(dict.fromkeys(out))


def segui_rinvio(doc, pagina_html, giorno, fonte=None, scarica=dc.scarica):
    """Aggiunge al documento il PDF a cui la pagina di annuncio rimanda: sulla pagina stessa o, se non c'è, su una
    pagina intermedia dello stesso ente ("Leggi il bando"). robots.txt e pause come per il resto della raccolta."""
    gia = {doc["url"], doc.get("allegato")}
    pdf = pdf_del_bando(pagina_html, doc["url"], gia, giorno)
    if not pdf:
        for pagina in pagine_intermedie(pagina_html, doc, gia, giorno)[:1]:
            pausa(pagina, giorno, (fonte or {}).get("pausa"))
            try:
                dati, tipo, _ = scarica(pagina, giorno)
            except (PermissionError, OSError) as e:
                doc["note_download"].append(f"pagina del rinvio non scaricata: {e}")
                return doc
            if dc.e_pdf(dati, tipo):
                return aggiungi_rinvio(doc, pagina, dati, tipo)
            pdf = pdf_del_bando(dati.decode("utf-8", "replace"), pagina, gia, giorno)
            doc["pagina_rinvio"] = pagina
    if not pdf:
        return doc
    pausa(pdf, giorno, (fonte or {}).get("pausa"))
    try:
        dati, tipo, _ = scarica(pdf, giorno)
    except (PermissionError, OSError) as e:
        doc["note_download"].append(f"PDF del rinvio non scaricato: {e}")
        return doc
    return aggiungi_rinvio(doc, pdf, dati, tipo) if dc.e_pdf(dati, tipo) else doc


def aggiungi_rinvio(doc, url, dati, tipo):
    pdf = dc.testo_pdf(dati)
    doc.update(rinvio=url, pagine=doc["pagine"] + pdf["pagine"], pagine_rinvio=len(pdf["pagine"]),
               ocr_necessario=doc.get("ocr_necessario") or pdf["ocr_necessario"])
    return doc


def rileggi_rinvii(ids, giorno=None):
    """Per i documenti già salvati: rilegge la pagina dalla copia locale (o la scarica, se manca) e segue il rinvio
    (decisione 102)."""
    giorno = giorno or dt.date.today().isoformat()
    fonti = {f["id"]: f for f in tutte_le_fonti()}
    for i in ids:
        f = dc.USCITA / f"{i}.json"
        doc = json.loads(f.read_text(encoding="utf-8"))
        if doc.get("rinvio"):
            print(f"già fatto {i}")
            continue
        copia = dc.copia_recente(doc["url"])
        if copia is None:  # su un'altra macchina: la pagina si scarica, con robots.txt e pausa
            try:
                pausa(doc["url"], giorno)
                copia = dc.scarica(doc["url"], giorno)[:2]
            except (PermissionError, OSError) as e:
                print(f"NO   {i}: {e}")
                continue
        if dc.e_pdf(*copia):
            print(f"NO   {i}: la pagina è già un PDF")
            continue
        doc = segui_rinvio(doc, copia[0].decode("utf-8", "replace"), giorno, fonti.get(doc.get("fonte_elenco")))
        if doc.get("rinvio"):
            f.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"ok   {i}: + PDF di {doc['pagine_rinvio']} pagine {doc['rinvio']}", flush=True)
        else:
            perche = doc["note_download"][-1] if doc["note_download"] and "rinvio" in doc["note_download"][-1] else "nessun PDF del bando trovato"
            print(f"--   {i}: {perche}" + (f" (pagina intermedia {doc['pagina_rinvio']})" if doc.get("pagina_rinvio") else ""), flush=True)


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
    elif doc["tipo"] == "html" and len(dc.testo_completo(doc)) < BREVE:
        doc = segui_rinvio(doc, dati.decode("utf-8", "replace"), giorno, fonte, scarica)
    return doc


def tutte_le_fonti():
    """Le fonti scritte a mano (elenchi.yaml) e quelle generate per Camere di commercio (camere.yaml) e comuni (comuni.yaml)."""
    fonti = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["fonti"]
    for nome in ("camere.yaml", "comuni.yaml"):
        f = CONFIG.with_name(nome)
        if f.exists():
            fonti += yaml.safe_load(f.read_text(encoding="utf-8")).get("fonti", [])
    return fonti


def gia_salvati(nome, cartella_documenti=None):
    """Indirizzi dei bandi della fonte che hanno già un documento."""
    fatti = set()
    for f in (cartella_documenti or dc.USCITA).glob(f"{nome}-*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("fonte_elenco") == nome:
            fatti.add(d["url"])
    return fatti


def mancanti(nome, cartella_elenchi=None, cartella_documenti=None):
    """{url: titolo} delle voci dell'ultimo elenco salvato della fonte che non hanno ancora un documento: per riprovare
    dopo errori di rete senza rileggere l'elenco né riscaricare i bandi già salvati."""
    cartella_elenchi, cartella_documenti = cartella_elenchi or DIR_ELENCHI, cartella_documenti or dc.USCITA
    ultimo = sorted(cartella_elenchi.glob(f"{nome}_????-??-??.json"))[-1]
    fatti = gia_salvati(nome, cartella_documenti)
    return {b["url"]: b["titolo"] for b in json.loads(ultimo.read_text(encoding="utf-8"))["bandi"] if b["url"] not in fatti}


def main(nome, massimo=None, solo_mancanti=False, nuovi=False):
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
        if nuovi:
            fatti = gia_salvati(nome)
            bandi = {u: t for u, t in bandi.items() if u not in fatti}
            print(f"{nome}: {len(bandi)} nuovi da scaricare")
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
    if a[0] == "--rinvii":
        rileggi_rinvii(a[1:])
        sys.exit(0)
    massimo = int(a[a.index("--max") + 1]) if "--max" in a else None
    main(a[0], massimo, "--solo-mancanti" in a, "--nuovi" in a)
