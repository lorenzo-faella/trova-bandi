"""Pagine elenco dei bandi delle Camere di commercio, ricavate dai dati invece che scritte a mano.

Non c'è un elenco nazionale dei bandi camerali, e le Camere sono un centinaio di siti diversi. Ma incentivi.gov.it ha,
per ogni bando camerale, il link alla sua pagina: la cartella che contiene quelle pagine è quasi sempre la pagina
elenco (mo.camcom.it/promozione/contributi-camerali/bandi/<bando> -> .../bandi). Per ogni Camera con bandi dal 2025:
  1. si prende la cartella più frequente tra quelle con un nome da bandi ("bandi", "contributi", "incentivi"...);
  2. si apre la pagina (una richiesta, robots.txt rispettato) e si contano i link a pagine dentro quella cartella;
  3. se ce n'è almeno uno, la Camera entra in data/fonti/camere.yaml, che pipeline/fonti/elenchi.py legge come le altre.
Le Camere senza una pagina elenco riconoscibile si scrivono in fondo al file, da sistemare a mano.

Uso: python -m pipeline.fonti.camere           (poi: python -m pipeline.fonti.elenchi <id>, oppure --tutte-le-camere)
"""
import collections
import datetime as dt
import json
import re
import sys
import time
from urllib.parse import urlparse

import yaml

from pipeline.fonti import documenti as dc
from pipeline.fonti.elenchi import link

USCITA = dc.ROOT / "data" / "fonti" / "camere.yaml"
CAMERA = re.compile(r"camer[ae] di commercio|unioncamere|unione regionale delle camere", re.I)
CARTELLA_BANDI = re.compile(r"band|contribut|incentiv|avvis|agevolaz|finanziam|voucher", re.I)
# Cartelle da non usare: gare d'appalto, e la trasparenza, che elenca i contributi già dati, non i bandi aperti.
CARTELLA_NO = re.compile(r"gar[ae]\b|appalt|trasparen|albo|concors|lavora-con-noi|personale", re.I)
# Una pagina di un singolo bando non è un elenco (es. /bando-temporary-shop_886, /pagina199048_bando-...).
SINGOLO = re.compile(r"/(bando|avviso)[-_][^/]*$|_\d+$|/pagina\d+|\.html?$|scadut", re.I)
MAX_LINK_CONTENUTO = 60
# Solo i siti delle Camere (non aziende speciali, agenzie di promozione o associazioni di categoria).
SITO_CAMERALE = re.compile(r"camcom|unioncamere|handelskammer|cameracommercio|camera(di)?commercio", re.I)
LINK_BANDI_HOME = re.compile(r"band|contribut|incentiv|agevolaz", re.I)  # su testi brevi (menu), vedi dalla_home
ALLEGATO = [r"^bando\b", r"\bbando\b", r"^avviso\b", r"\bavviso\b", r"regolamento", r"allegato (a|1)\b", r"determin"]
DAL = "2025"
NOMI = {"Trentino-Alto Adige/Südtirol": "Trentino-Alto Adige", "Valle d'Aosta/Vallée d'Aoste": "Valle d'Aosta"}


def lista(v):
    return v if isinstance(v, list) else [v] if v else []


def candidati(export):
    """{dominio: {"cartelle": Counter, "ente": nome più frequente, "regione": ...}} delle Camere con bandi recenti."""
    out = collections.defaultdict(lambda: {"cartelle": collections.Counter(), "enti": collections.Counter(),
                                           "regioni": collections.Counter(), "schema": "https"})
    for x in export:
        enti = [s for s in lista(x.get("Soggetto_Concedente")) if CAMERA.search(s)]
        quando = (x.get("Data_apertura") or x.get("Data_ultimo_aggiornamento") or "")[:4]
        if not enti or quando < DAL:
            continue
        u = urlparse(x.get("Link_istituzionale") or "")
        parti = [p for p in u.path.split("/") if p]
        if not u.netloc or len(parti) < 2:
            continue
        d = out[u.netloc.lower()]
        d["schema"] = u.scheme or "https"
        cartella = "/" + "/".join(parti[:-1])
        if CARTELLA_BANDI.search(cartella) and not CARTELLA_NO.search(cartella) and not SINGOLO.search(cartella) and \
                not re.search(r"\.(pdf|docx?)$|/files/|/sites/default", cartella, re.I):
            d["cartelle"][cartella] += 1
        d["enti"].update(enti)
        regioni = lista(x.get("Regioni"))
        if len(regioni) == 1:
            d["regioni"][NOMI.get(regioni[0], regioni[0])] += 1
    return out


def dalla_home(dominio, info, giorno):
    """Seconda strada: il link "Bandi" (o simile) nella home della Camera. Restituisce la cartella o None."""
    home = f"{info['schema']}://{dominio}/"
    try:
        dati, _, _ = dc.scarica(home, giorno)
    except (PermissionError, OSError):
        return None
    for u, t in link(dati.decode("utf-8", "replace"), home):
        p = urlparse(u)
        if p.netloc.lower().removeprefix("www.") == dominio.removeprefix("www.") and len(t.strip()) <= 45 \
                and LINK_BANDI_HOME.search(t) \
                and p.path.strip("/") and not CARTELLA_NO.search(p.path) and not SINGOLO.search(p.path.rstrip("/")):
            return "/" + p.path.strip("/")
    return None


def prova(dominio, info, giorno):
    """La fonte per elenchi.py se la pagina elenco ha link ai bandi, altrimenti (None, motivo)."""
    cartella = info["cartelle"].most_common(1)[0][0] if info["cartelle"] else None
    if not cartella:
        time.sleep(1)
        cartella = dalla_home(dominio, info, giorno)
        if not cartella:
            return None, "nessuna cartella con un nome da bandi, e nessun link 'Bandi' nella home"
    url = f"{info['schema']}://{dominio}{cartella}"
    try:
        dati, _, _ = dc.scarica(url, giorno)
    except PermissionError:
        return None, "robots.txt vieta"
    except OSError:  # la cartella del portale non c'è più (sito rifatto): si riparte dalla home
        time.sleep(1)
        cartella = dalla_home(dominio, info, giorno)
        if not cartella:
            return None, "la cartella del portale non esiste più, e nessun link ai bandi nella home"
        url = f"{info['schema']}://{dominio}{cartella}"
        try:
            dati, _, _ = dc.scarica(url, giorno)
        except (PermissionError, OSError) as e:
            return None, f"non risponde ({str(e)[:60]})"
    base = re.escape(dominio.removeprefix("www."))
    regola = rf"^https?://(www\.)?{base}{re.escape(cartella)}/[^/?#]+/?$"
    bandi = {u for u, t in link(dati.decode("utf-8", "replace"), url) if re.search(regola, u) and t}
    solo_contenuto = False
    if not bandi:  # i bandi stanno in un'altra cartella: si prendono i link del contenuto principale della pagina
        from pipeline.fonti.elenchi import contenuto
        regola = rf"^https?://(www\.)?{base}/"
        bandi = {u for u, t in link(contenuto(dati.decode("utf-8", "replace")), url)
                 if re.search(regola, u) and len(t) >= 20 and u.rstrip("/") != url.rstrip("/")}
        solo_contenuto = True
    if not bandi:
        return None, f"{url}: nessun link a bandi nella pagina"
    if solo_contenuto and len(bandi) > MAX_LINK_CONTENUTO:
        return None, f"{url}: {len(bandi)} link nel contenuto, probabilmente non è un elenco di bandi"
    etichette = [e for e in dominio.lower().removeprefix("www.").split(".") if e not in ("camcom", "cameracommercio", "handelskammer", "gov", "it")]
    nome = re.sub(r"[^a-z0-9]+", "-", etichette[0] if etichette else dominio)
    regione = info["regioni"].most_common(1)[0][0] if info["regioni"] else None
    return {"id": f"camera-{nome}", "ente": info["enti"].most_common(1)[0][0], "livello": "camera di commercio",
            "regione": regione, "pubblico": "imprese", "pagine": url, "link_bando": regola, "allegato": ALLEGATO,
            **({"solo_contenuto": True} if solo_contenuto else {}), "bandi_in_pagina": len(bandi)}, None


def main():
    files = sorted(f for f in (dc.ROOT / "data" / "raw").glob("incentivi_export_*.json") if not f.name.endswith(".meta.json"))
    export = json.loads(files[-1].read_text(encoding="utf-8"))
    giorno = dt.date.today().isoformat()
    fonti, da_fare = [], []
    visti = {}
    for dominio, info in sorted(candidati(export).items(), key=lambda kv: -sum(kv[1]["enti"].values())):
        if not SITO_CAMERALE.search(dominio):
            continue
        chiave_sito = dominio.removeprefix("www.").replace(".gov.it", ".it")  # bs.camcom.it = www.bs.camcom.it
        if chiave_sito in visti:
            continue
        visti[chiave_sito] = dominio
        if not dc.file_cache(f"{info['schema']}://{dominio}", giorno).exists():
            time.sleep(1)  # siti diversi: basta una pausa breve
        fonte, motivo = prova(dominio, info, giorno)
        if fonte:
            fonti.append(fonte)
            print(f"ok   {dominio}: {fonte['bandi_in_pagina']} bandi in {fonte['pagine']}")
        else:
            da_fare.append({"dominio": dominio, "ente": info["enti"].most_common(1)[0][0], "motivo": motivo})
            print(f"--   {dominio}: {motivo}")
    testa = ("# Generato da pipeline/fonti/camere.py: le pagine elenco delle Camere di commercio, ricavate dai link di\n"
             "# incentivi.gov.it. Le Camere in 'da_sistemare' vanno guardate a mano.\n")
    USCITA.write_text(testa + yaml.safe_dump({"fonti": fonti, "da_sistemare": da_fare}, allow_unicode=True,
                                             sort_keys=False, width=200), encoding="utf-8")
    print(f"{len(fonti)} Camere con pagina elenco, {len(da_fare)} da sistemare a mano: {USCITA}")


if __name__ == "__main__":
    main()
