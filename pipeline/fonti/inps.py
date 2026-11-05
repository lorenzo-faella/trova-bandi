"""Fonte per le persone: le schede delle prestazioni sul sito INPS.

Non esiste un catalogo strutturato dei bonus: i requisiti stanno nel testo di queste pagine. Partiamo dalla sitemap
pubblica e teniamo le sezioni utili di ogni scheda. robots.txt permette tutto tranne i PDF dei moduli, che non scarichiamo.
L'HTML pesa circa 700 KB a pagina: resta compresso in data/cache/ (fuori da git), e rilanciando riprende da dove era.

Uso: python -m pipeline.fonti.inps [parola nell'URL ...]    senza parole scarica tutte le schede, una al secondo
"""
import datetime as dt
import gzip
import hashlib
import html.parser
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE = ROOT / "data" / "cache" / "inps"
SITEMAP = "https://www.inps.it/it/it.sitemap.xml"
UA = {"User-Agent": "trova-bandi (progetto universitario Bocconi 20875)"}
PAUSA = 1.0
SEZIONI = {"cos'è": "cosa", "a chi è rivolto": "destinatari", "come funziona": "funzionamento", "domanda": "domanda"}
# Parole nel titolo di una scheda che indicano una pratica o un servizio, non un beneficio da chiedere.
PRATICA = re.compile(r"consultazion|simulazion|verifica|comunicazion|certificat|certificazion|accredito|rimborso|"
                     r"riscatto|estratto conto|cedolino|portale|autorizzazion|duplicato|variazion|iscrizion|versamento|"
                     r"pagamento|modulistic|calcol|ricongiunzion|attestat|delega|conferma|domanda|rinuncia", re.I)
BENEFICIO = re.compile(r"bonus|assegn|indennit|naspi|dis-coll|carta|sostegno|nido|borsa|borse|soggiorn|vacanz|supporto|"
                       r"inclusione|congedo|ape sociale|pensione di|cittadinanza|centri estivi|home care|master", re.I)
# Prestazioni riservate agli iscritti di una gestione: vere, ma poco utili a chi cerca un aiuto generale.
NICCHIA = re.compile(r"gestione|fondo|ipost|postelegrafon|magistrale|dipendenti pubblici|iscritt|sportass|clero|"
                     r"aziende|datori", re.I)


class Sezioni(html.parser.HTMLParser):
    """Testo dentro <main>, diviso per titolo <h2>, con una riga per paragrafo. I blocchi a scomparsa restano."""
    BLOCCHI = {"p", "li", "div", "br", "h3", "h4", "tr", "ul", "ol"}
    IGNORA = {"script", "style", "noscript", "svg", "button"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.dentro_main = self.dentro_h1 = self.dentro_h2 = False
        self.ignora = 0
        self.titolo, self.corrente, self.h2 = "", None, ""
        self.testi = {}

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.dentro_main = True
        if tag in self.IGNORA:
            self.ignora += 1
        if tag == "h1":
            self.dentro_h1 = True
        if tag == "h2" and self.dentro_main:
            self.dentro_h2, self.h2 = True, ""
        if tag in self.BLOCCHI and self.corrente:
            self.testi[self.corrente].append("\n")

    def handle_endtag(self, tag):
        if tag == "main":
            self.dentro_main, self.corrente = False, None
        if tag in self.IGNORA and self.ignora:
            self.ignora -= 1
        if tag == "h1":
            self.dentro_h1 = False
        if tag == "h2" and self.dentro_h2:
            self.dentro_h2 = False
            self.corrente = re.sub(r"\s+", " ", self.h2).strip()
            self.testi.setdefault(self.corrente, [])

    def handle_data(self, data):
        if self.ignora:
            return
        if self.dentro_h1:
            self.titolo += data
        elif self.dentro_h2:
            self.h2 += data
        elif self.dentro_main and self.corrente:
            self.testi[self.corrente].append(data)


def pulisci(pezzi):
    righe = [re.sub(r"[ \t\xa0]+", " ", r).strip() for r in "".join(pezzi).split("\n")]
    return "\n".join(r for r in righe if r and r not in ("Leggi di più", "Leggi meno"))


def estrai(pagina):
    """Dall'HTML di una scheda: titolo e sezioni note. Le altre sezioni (Condividi, Documenti...) si ignorano."""
    p = Sezioni()
    p.feed(pagina)
    sezioni = {}
    for nome, pezzi in p.testi.items():
        chiave = SEZIONI.get(nome.replace("’", "'").lower())
        if chiave:
            sezioni[chiave] = pulisci(pezzi)
    return {"titolo": re.sub(r"\s+", " ", p.titolo).strip(), "sezioni": sezioni}


def sembra_beneficio(titolo):
    return bool(BENEFICIO.search(titolo)) and not PRATICA.search(titolo)


def get(url, timeout=60):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def url_schede():
    testo = get(SITEMAP).decode("utf-8", "replace")
    return sorted(u for u in re.findall(r"<loc>([^<]+)</loc>", testo) if "schede-servizi." in u)


def pagina(url):
    """L'HTML dalla cache oppure, una volta sola, dal sito: True se ha fatto una richiesta."""
    f = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".html.gz")
    if f.exists():
        return gzip.decompress(f.read_bytes()).decode("utf-8", "replace"), False
    corpo = get(url)
    f.write_bytes(gzip.compress(corpo))
    return corpo.decode("utf-8", "replace"), True


def main(filtri):
    oggi = dt.date.today().isoformat()
    CACHE.mkdir(parents=True, exist_ok=True)
    urls = url_schede()
    if filtri:
        urls = [u for u in urls if any(p in u.lower() for p in filtri)]
    schede, errori = [], []
    for i, url in enumerate(urls, 1):
        try:
            testo, richiesta = pagina(url)
        except OSError as e:  # una pagina che non risponde non deve fermare le altre: la si riprova rilanciando
            errori.append({"url": url, "errore": str(e)})
            continue
        s = estrai(testo)
        schede.append({"url": url, "beneficio": sembra_beneficio(s["titolo"]),
                       "di_nicchia": bool(NICCHIA.search(s["titolo"])), **s})
        if i % 50 == 0:
            print(f"{i}/{len(urls)}", flush=True)
        if richiesta:
            time.sleep(PAUSA)
    if filtri:
        return schede
    out = ROOT / "data" / "raw" / f"inps_schede_{oggi}.json"
    out.write_text(json.dumps(schede, ensure_ascii=False, indent=1), encoding="utf-8")
    meta = {"fonte": SITEMAP, "scaricato": oggi, "schede": len(schede), "errori": errori,
            "licenza": "nessuna licenza dichiarata sul sito; vedi docs/decisioni.md"}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{out.name}: {len(schede)} schede, {sum(s['beneficio'] for s in schede)} benefici, {len(errori)} errori")
    return schede


if __name__ == "__main__":
    risultato = main([p.lower() for p in sys.argv[1:]])
    if sys.argv[1:]:
        for s in risultato:
            print(f"\n{'=' * 70}\n{s['titolo']} | beneficio: {s['beneficio']}\n{s['url']}")
            for nome, testo in s["sezioni"].items():
                print(f"\n--- {nome} ({len(testo)} caratteri)\n{testo}")
