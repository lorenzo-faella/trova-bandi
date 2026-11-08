"""Fonti dei comuni, ricavate dalle loro home invece che scritte a mano (decisione 47).

Quasi tutti i comuni capoluogo hanno il sito del modello nazionale (Designers Italia), con una pagina "Avvisi" tra le
notizie. Per ogni comune di data/fonti/capoluoghi.yaml:
  1. si apre la home (una richiesta, robots.txt rispettato) e si cerca il link "Avvisi" (o "Bandi e avvisi"...);
  2. si apre quella pagina e si contano i link alle singole notizie dello stesso sito;
  3. se ce ne sono, il comune entra in data/fonti/comuni.yaml, che pipeline/fonti/elenchi.py legge come le altre fonti.
     Lì i bandi per le persone stanno insieme a viabilità, scioperi, elezioni, gare: a sceglierli sono i filtri sul titolo
     (TESTO_BANDO, ESCLUDI_TESTO), uguali per tutti i comuni.
I comuni senza una pagina leggibile (elenco caricato con JavaScript, robots.txt, sito che non risponde) si scrivono in
fondo al file, con il motivo.

Uso: python -m pipeline.fonti.comuni        (poi: python -m pipeline.fonti.elenchi comune-<nome>)
"""
import datetime as dt
import re
import time
import unicodedata
from urllib.parse import urlparse

import yaml

from pipeline.fonti import documenti as dc
from pipeline.fonti.elenchi import CONFIG, link

CAPOLUOGHI = dc.ROOT / "data" / "fonti" / "capoluoghi.yaml"
USCITA = dc.ROOT / "data" / "fonti" / "comuni.yaml"
LINK_AVVISI = re.compile(r"^(tutti gli )?(avvisi|bandi|bandi e avvisi|avvisi e bandi|avvisi pubblici|bandi e contributi|"
                         r"bandi,? avvisi e contributi)( pubblici)?$", re.I)
# Le notizie del modello nazionale: /novita/..., /it/news/..., /notizie/..., /notizia/..., /-/... (Liferay, Bari).
NOTIZIA = r"(it/)?([Nn]ovit(a|à|%C3%A0)|news|[Nn]otizi[ae]|-)/.+"
NON_NOTIZIA = r"[?&]type=|/tipologia/|/(avvisi|avviso)/?$|/Avvisi$"
TESTO_BANDO = (r"\bband[oi]\b|avviso pubblico|contribut|bonus|voucher|agevolaz|sostegn|\bbuon[oi]\b|\bfondo\b|\bassegn[oi]\b|"
               r"borse? di studio|esenzion|rimbors|sussid|centri estivi|domand[ae]\b|incentiv")
ESCLUDI_TESTO = (r"gara|appalt|aggiudic|affidament|indagine di mercato|concors|selezion|mobilit[aà] (esterna|volontaria)|assunzion|"
                 r"incaric|nomin|revisor|posteggi|chiosc|locazione di un locale|concessione in uso|elettor|scrutator|sciopero|"
                 r"circolazione|viabilit|traffico|ordinanz|lavori|graduatori|esit[oi]|beneficiari|ammess|proroga|rettific|errata|"
                 r"commission|verbale|interruzion|chiusura|consulta|messa a disposizione|contributo di costruzione")
ALLEGATO = [r"^bando\b", r"\bbando\b", r"^avviso\b", r"\bavviso\b", r"allegato (a|1)\b"]
MIN_NOTIZIE = 3  # meno di così la pagina non è un elenco (o lo carica il JavaScript)


def nome_id(comune):
    s = unicodedata.normalize("NFKD", comune.lower()).encode("ascii", "ignore").decode()
    return "comune-" + re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def pagina_avvisi(home_html, home):
    """L'indirizzo della pagina "Avvisi" dal menu della home, o None."""
    host = urlparse(home).netloc
    for u, t in link(home_html, home):
        if LINK_AVVISI.match(t or "") and urlparse(u).netloc == host:
            return u
    return None


def notizie(pagina_html, url):
    """{url: titolo} delle singole notizie dello stesso sito che la pagina elenca."""
    host = urlparse(url).netloc
    regola = re.compile(rf"^https://{re.escape(host)}/{NOTIZIA}$")
    return {u: t for u, t in link(pagina_html, url)
            if regola.search(u) and not re.search(NON_NOTIZIA, u) and len(t) >= 20}


def prova(comune, giorno, scarica=dc.scarica):
    """(fonte per elenchi.py, None) se la pagina degli avvisi si legge, altrimenti (None, motivo)."""
    home = comune["home"]
    try:
        dati, _, _ = scarica(home, giorno)
    except PermissionError:
        return None, "robots.txt vieta il sito"
    except OSError as e:
        return None, f"la home non risponde ({str(e)[:60]})"
    url = pagina_avvisi(dati.decode("utf-8", "replace"), home)
    if not url:
        return None, "nessun link 'Avvisi' nella home (home vuota o fatta con JavaScript)"
    time.sleep(dc.attesa(url))
    try:
        dati, _, _ = scarica(url, giorno)
    except (PermissionError, OSError) as e:
        return None, f"{url}: non si legge ({str(e)[:60]})"
    trovate = notizie(dati.decode("utf-8", "replace"), url)
    if len(trovate) < MIN_NOTIZIE:
        return None, f"{url}: {len(trovate)} notizie nell'HTML, l'elenco si carica probabilmente con JavaScript"
    pertinenti = sum(1 for t in trovate.values() if re.search(TESTO_BANDO, t, re.I) and not re.search(ESCLUDI_TESTO, t, re.I))
    host = re.escape(urlparse(url).netloc)
    return {"id": nome_id(comune["nome"]), "ente": f"Comune di {comune['nome']}", "livello": "comunale",
            "regione": comune["regione"], "comune": comune["nome"], "pubblico": None, "pagine": url,
            "link_bando": rf"^https://{host}/{NOTIZIA}$", "escludi": NON_NOTIZIA, "testo_bando": TESTO_BANDO,
            "escludi_testo": ESCLUDI_TESTO, "allegato": ALLEGATO,
            "notizie_in_pagina": len(trovate), "pertinenti_oggi": pertinenti}, None


def main():
    giorno = dt.date.today().isoformat()
    gia_fatti = {f["id"] for f in yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["fonti"]}  # scritti a mano
    fonti, da_sistemare = [], []
    for c in yaml.safe_load(CAPOLUOGHI.read_text(encoding="utf-8"))["comuni"]:
        if nome_id(c["nome"]) in gia_fatti:
            continue
        fonte, motivo = prova(c, giorno)
        if fonte:
            fonti.append(fonte)
            print(f"ok   {fonte['id']}: {fonte['notizie_in_pagina']} notizie, {fonte['pertinenti_oggi']} pertinenti oggi")
        else:
            da_sistemare.append({"comune": c["nome"], "home": c["home"], "motivo": motivo})
            print(f"no   {c['nome']}: {motivo}")
        time.sleep(1)
    testa = (f"# Generato da pipeline/fonti/comuni.py il {giorno}: non modificare a mano (le correzioni vanno in elenchi.yaml).\n"
             "# I filtri sul titolo sono uguali per tutti i comuni; da_sistemare: i comuni senza una pagina avvisi leggibile.\n")
    USCITA.write_text(testa + yaml.safe_dump({"fonti": fonti, "da_sistemare": da_sistemare}, allow_unicode=True,
                                             sort_keys=False, width=200), encoding="utf-8")
    print(f"{len(fonti)} comuni con fonte, {len(da_sistemare)} da sistemare: {USCITA}")


if __name__ == "__main__":
    main()
