"""Stadio 2: export grezzo -> data/processed/bandi.json, con tipi puliti e uno schema stabile.

Uso: python -m pipeline.normalizza data/raw/incentivi_export_AAAA-MM-GG.json AAAA-MM-GG
La data è il "giorno di riferimento" per lo stato aperto/chiuso (di solito il giorno dell'export).
"""
import csv
import html
import io
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONI = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria",
    "Lombardia", "Marche", "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana",
    "Trentino-Alto Adige/Südtirol", "Umbria", "Valle d'Aosta/Vallée d'Aoste", "Veneto",
]
# Tipologie di soggetto che una impresa (anche da costituire) o un professionista può avere.
TIPOLOGIE_IMPRESA = {
    "Impresa", "Impresa - SU/PMI innovativa", "Impresa - prevalenza femminile", "Impresa - prevalenza giovanile",
    "Impresa da costituire - Altro", "Impresa da costituire - Femminile", "Impresa da costituire - Giovanile",
    "Professionista", "Consorzio", "Rete d'impresa", "Cooperative/Associazioni Non Profit",
}
# Dal 1/4/2025 vale ATECO 2025. I bandi che non dichiarano la versione la ricevono dalla data di apertura.
INIZIO_ATECO_2025 = "2025-04-01"
CODICE_ATECO = re.compile(r"\b\d{2}(?:\.\d{1,2}){0,2}\b")
# Il sito del Ministero è passato da mise.gov.it a mimit.gov.it: il vecchio indirizzo rimanda alla pagina nuova
# passando per http://, e i browser che vogliono solo https si fermano lì. Stessa pagina, indirizzo diretto.
SITI_SPOSTATI = [(re.compile(r"^https?://(?:www\.)?mise\.gov\.it(?=[/?#]|$)", re.I), "https://www.mimit.gov.it")]


def lista(v):
    """I campi multipli arrivano come lista, stringa "a; b; c" o None; 'None' e vuoti spariscono."""
    if v is None:
        return []
    # html.unescape prima dello split: "Sant&apos;Agata" si spezzerebbe sul ";" dell'entità
    voci = v if isinstance(v, list) else html.unescape(str(v)).split(";")
    return [s.strip() for s in voci if s and s.strip() and s.strip() != "None"]


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def data(v):
    return v[:10] if v else None


def link(u):
    """Link istituzionale pulito, con l'indirizzo nuovo per i siti che hanno cambiato dominio."""
    u = (u or "").strip()
    for vecchio, nuovo in SITI_SPOSTATI:
        u = vecchio.sub(nuovo, u)
    return u or None


def stato(apertura, chiusura, oggi):
    if apertura and apertura > oggi:
        return "non ancora aperto"
    if chiusura and chiusura < oggi:
        return "chiuso"
    return "aperto" if chiusura else "aperto (senza scadenza)"


def ateco(testo, apertura):
    """Codici ATECO per versione. Prefissi: '56' copre tutta la divisione, '56.1' il gruppo.

    Il campo è testo libero: "Tutti i settori...", "ATECO 2025: 56.10; 56.21;", solo i codici, a volte frasi.
    Ciò che contiene lettere ma nessun codice finisce in non_riconosciuti invece di essere scartato.
    """
    testo = (testo or "").strip()
    if not testo or testo.startswith("Tutti"):
        return {"tutti": True, "codici": {}, "non_riconosciuti": []}
    codici, non_ric = {}, []
    # "ATECO 2007: ... ATECO 2025: ..." -> un pezzo per versione; senza etichetta la versione si deduce dalla data
    pezzi = re.split(r"ATECO\s*(\d{4})\s*:", testo)
    senza = "2025" if (apertura or "") >= INIZIO_ATECO_2025 else "2007"
    blocchi = [(senza, pezzi[0])] + list(zip(pezzi[1::2], pezzi[2::2]))
    for versione, blocco in blocchi:
        trovati = CODICE_ATECO.findall(blocco)
        if trovati:
            # dict.fromkeys: toglie i duplicati (capitano: "55.90; 55.90") mantenendo l'ordine
            codici[versione] = list(dict.fromkeys(codici.get(versione, []) + trovati))
        elif blocco.strip(" ;,.") and re.search(r"[A-Za-z]", blocco):
            non_ric.append(blocco.strip())
    if not codici:  # "N/A", "Non applicabile": nessun vincolo leggibile, ma lo segnaliamo
        return {"tutti": True, "codici": {}, "non_riconosciuti": non_ric}
    return {"tutti": False, "codici": codici, "non_riconosciuti": non_ric}


def chiave_comune(nome):
    """Confronto tra nomi di comuni di fonti diverse: niente accenti, apostrofi, maiuscole, seconda lingua."""
    nome = nome.split("/")[0]
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", nome.lower())


def carica_comuni_istat(percorso):
    """chiave_comune -> (nome ufficiale, regione)."""
    testo = Path(percorso).read_bytes().decode("latin-1")
    righe = csv.DictReader(io.StringIO(testo), delimiter=";")
    out = {}
    for r in righe:
        for nome in {r["Denominazione in italiano"], r["Denominazione (Italiana e straniera)"]}:
            out[chiave_comune(nome)] = (r["Denominazione in italiano"], r["Denominazione Regione"])
    return out


def normalizza(doc, oggi, comuni_istat):
    apertura, chiusura = data(doc.get("Data_apertura")), data(doc.get("Data_chiusura"))
    regioni = lista(doc.get("Regioni"))
    comuni, comuni_ignoti = [], []
    nomi = lista(doc.get("Comuni"))
    if any(n.lower().startswith("tutti") for n in nomi):  # "Tutti i comuni": nessun vincolo
        nomi = []
    for c in nomi:
        # i non riconosciuti sono quasi tutti comuni soppressi da fusioni (es. Rossano -> Corigliano-Rossano)
        trovato = comuni_istat.get(chiave_comune(c))
        if trovato:
            comuni.append(trovato[0])
        else:
            comuni_ignoti.append(c)
    return {
        "id": str(doc["ID_Incentivo"]),
        "titolo": html.unescape(doc.get("Titolo") or "").strip(),
        "descrizione": html.unescape(re.sub(r"<[^>]+>", " ", doc.get("Descrizione") or "")).strip(),
        "link": link(doc.get("Link_istituzionale")),
        "ente": doc.get("Soggetto_Concedente"),
        "apertura": apertura,
        "chiusura": chiusura,
        "note_apertura": doc.get("Note_di_apertura_chiusura"),
        "stato": stato(apertura, chiusura, oggi),
        "regioni": regioni,
        "nazionale": set(REGIONI) <= set(regioni),
        "comuni": comuni,
        "comuni_non_riconosciuti": comuni_ignoti,
        "tipologie": lista(doc.get("Tipologia_Soggetto")),
        "dimensioni": lista(doc.get("Dimensioni")),
        "settori": lista(doc.get("Settore_Attivita")),
        "ateco": ateco(doc.get("Codici_ATECO"), apertura),
        "ambiti": [a for a in lista(doc.get("Ambito_territoriale")) if a != "Non applicabile"],
        "forme": lista(doc.get("Forma_agevolazione")),
        "obiettivi": lista(doc.get("Obiettivo_Finalita")),
        "spesa_min": numero(doc.get("Spesa_Ammessa_min")),
        "spesa_max": numero(doc.get("Spesa_Ammessa_max")),
        "agevolazione_min": numero(doc.get("Agevolazione_Concedibile_min")),
        "agevolazione_max": numero(doc.get("Agevolazione_Concedibile_max")),
        "stanziamento": numero(doc.get("Stanziamento_incentivo")),
        "aggiornato": data(doc.get("Data_ultimo_aggiornamento")),
        "per_imprese": bool(TIPOLOGIE_IMPRESA & set(lista(doc.get("Tipologia_Soggetto")))),
    }


def main(raw, oggi):
    istat = sorted((ROOT / "data" / "raw").glob("istat_comuni_*.csv"))
    if not istat:
        sys.exit("manca l'elenco ISTAT: python -m pipeline.scarica comuni")
    comuni_istat = carica_comuni_istat(istat[-1])
    docs = json.loads(Path(raw).read_text(encoding="utf-8"))
    bandi = [normalizza(d, oggi, comuni_istat) for d in docs]
    out = ROOT / "data" / "processed" / "bandi.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"riferimento": oggi, "fonte": Path(raw).name, "bandi": bandi},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    stati = Counter(b["stato"] for b in bandi)
    ignoti = sum(len(b["comuni_non_riconosciuti"]) for b in bandi)
    print(f"{out.name}: {len(bandi)} bandi, {dict(stati)}; comuni non riconosciuti: {ignoti}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: python -m pipeline.normalizza <export.json> <AAAA-MM-GG>")
    main(sys.argv[1], sys.argv[2])
