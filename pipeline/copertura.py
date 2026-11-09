"""Copertura regione per regione: quanti bandi di un elenco di riferimento troviamo anche noi (proposte-fase-2, §3.5).

Lombardia: c'è un elenco ufficiale, il dataset "Anagrafica dei bandi regionali" di dati.lombardia.it (CC BY 4.0).
  Si misura la copertura di incentivi.gov.it e quella di tutte le nostre fonti insieme.
Sicilia: non c'è un elenco ufficiale. Si stima il totale con la "cattura e ricattura" (stimatore di Chapman) tra la pagina
  della Regione (con IRFIS) e incentivi.gov.it, dichiarando che le due fonti non sono davvero indipendenti.

I passi, per tutte e due:
  1. date: il portale è del 27/10, la nostra raccolta del 7/11. Contano solo i bandi aperti in tutte e due le date;
  2. filtro di rilevanza sul titolo: via gare, concorsi e personale, bandi solo per enti e comuni, atti che non sono bandi;
  3. abbinamento: prima il codice del bando nell'indirizzo (quando c'è), poi il titolo normalizzato e una somiglianza
     tra parole; le coppie in zona grigia si controllano a mano (data/copertura/revisione.yaml);
  4. intervallo di Wilson al 95% per ogni quota, e intervallo di Chao per il totale di Chapman.

Legge solo file locali, sempre gli stessi: rilanciato, dà lo stesso documento. L'unica parte in rete è `scarica-lombardia`.

Uso: python -m pipeline.copertura                    scrive docs/copertura-regioni.md
     python -m pipeline.copertura scarica-lombardia  scarica il dataset lombardo in data/raw/ (al massimo uno al giorno)
"""
import datetime as dt
import difflib
import functools
import hashlib
import json
import math
import re
import sys
import unicodedata
import urllib.request
import urllib.robotparser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ELENCHI = RAW / "elenchi"
REVISIONE = ROOT / "data" / "copertura" / "revisione.yaml"
USCITA = ROOT / "docs" / "copertura-regioni.md"
UA = "trova-bandi (progetto universitario Bocconi 20875)"

GIORNO_PORTALE = "2026-10-27"   # export di incentivi.gov.it
GIORNO_RACCOLTA = "2026-11-07"  # elenchi raccolti da noi
PORTALE = RAW / f"incentivi_export_{GIORNO_PORTALE}.json"

# Soglie della somiglianza tra titoli, scelte guardando le coppie già certe per codice (vedi la sezione "Abbinamento").
SOGLIA = 0.75   # da qui in su: stesso bando
GRIGIA = 0.60   # tra GRIGIA e SOGLIA: da controllare a mano. Sotto 0.6 c'è il rumore: tra titoli che non c'entrano
                # difflib dà spesso 0.4-0.5

LOMBARDIA_ID = "bukx-h2uy"
LOMBARDIA_SITO = "https://www.dati.lombardia.it"
LOMBARDIA_DATI = f"{LOMBARDIA_SITO}/resource/{LOMBARDIA_ID}.json?$limit=50000&$order=codice_bando"
LOMBARDIA_META = f"{LOMBARDIA_SITO}/api/views/{LOMBARDIA_ID}.json"


# --- 1. Normalizzazione e somiglianza dei titoli ---

# Parole che non distinguono un bando dall'altro. Anche i nomi delle regioni: il portale aggiunge spesso
# "- Regione Siciliana" in fondo al titolo, il sito della Regione no.
VUOTE = set("""a ad al alla alle agli ai all allo anche che con col d da dal dalla dalle dei degli del della delle dello di
e ed fra gli i il in l la le lo nel nella nelle nei negli o per su sul sulla tra un una uno
avviso avvisi pubblico pubblica bando bandi regione regionale regionali lombardia lombarda lombarde lombardi
sicilia siciliana siciliano siciliani misura misure contributi contributo""".split())


@functools.lru_cache(maxsize=None)  # gli stessi titoli si confrontano migliaia di volte
def normalizza(titolo):
    """Minuscole, senza accenti, entità HTML e punteggiatura. "Re-IMPRESA" e "Re-Impresa" diventano uguali."""
    t = re.sub(r"&[a-z]+;|&#\d+;", " ", titolo or "")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t).split())


@functools.lru_cache(maxsize=None)
def parole(titolo):
    return tuple(p for p in normalizza(titolo).split() if p not in VUOTE)


# Capoluoghi delle due regioni misurate: "Dote Impresa Asse I - Provincia di Bergamo" e "... di Como" sono due bandi.
LUOGHI = set("""bergamo brescia como cremona lecco lodi mantova milano monza pavia sondrio varese
agrigento caltanissetta catania enna messina palermo ragusa siracusa trapani""".split())
ORDINALI = set("prima primo seconda secondo terza terzo quarta quarto quinta quinto sesta sesto".split())
# I periodi di programmazione (PR FESR 2021-2027) non distinguono un'edizione dall'altra: si tolgono prima degli anni.
PERIODI = r"\b(2007 2013|2014 2020|2021 (20)?27)\b"


@functools.lru_cache(maxsize=None)
def segni(titolo, ente=""):
    """Ciò che distingue due edizioni o due copie locali della stessa misura: luoghi, anni, assi, ordinali.

    Il luogo si cerca anche nel nome dell'ente: sul portale la scheda "Regione Lombardia - Dote Impresa Collocamento
    Mirato – Assi I-II-III" è della Città Metropolitana di Milano, quindi vale solo per Milano.
    """
    t = normalizza(titolo)
    anni = frozenset(re.findall(r"\b20\d\d\b", re.sub(PERIODI, " ", t)))
    assi = set()
    for gruppo in re.findall(r"\bass[ei]((?: (?:i{1,3}|iv|v|vi{1,3}|x))+)\b", t):
        assi |= set(gruppo.split())
    parole_t = set(t.split())
    return {"luoghi": (parole_t | set(normalizza(ente).split())) & LUOGHI, "anni": anni, "assi": frozenset(assi),
            "ordinali": parole_t & ORDINALI}


def incompatibili(a, b, ente_a="", ente_b=""):
    """Vero se i due titoli nominano, per lo stesso segno, valori diversi (Bergamo / Como, 2021 / 2023, Asse I / II).

    Se il segno c'è in un titolo solo non si decide niente: "Dote Impresa Collocamento Mirato" senza provincia resta in
    gioco, e va in zona grigia se il punteggio lo porta lì. Gli anni devono coincidere tutti, i luoghi e gli assi basta
    che ne abbiano uno in comune ("Assi I-II-III" comprende "Asse II").
    """
    sa, sb = segni(a, ente_a), segni(b, ente_b)
    for k in ("luoghi", "assi", "ordinali"):
        if sa[k] and sb[k] and not sa[k] & sb[k]:
            return True
    return bool(sa["anni"] and sb["anni"] and sa["anni"] != sb["anni"])


def somiglianza(a, b, ente_a="", ente_b=""):
    """Tra 0 e 1: il massimo tra la somiglianza delle sequenze (difflib) e la sovrapposizione delle parole (Dice).

    Due misure perché sbagliano in modo diverso: difflib premia i titoli quasi identici anche con parole tagliate,
    Dice premia le stesse parole in ordine diverso ("Investimenti - Linea sviluppo aziendale" e "Pacchetto
    investimenti – Linea sviluppo aziendale").
    Due correzioni, viste sulle coppie certe per codice:
      - titoli incompatibili (luoghi, anni, assi o ordinali diversi): 0, anche se le altre parole coincidono;
      - luogo in un titolo solo: al massimo zona grigia;
      - titolo corto tutto contenuto nell'altro ("Re-Impresa" in "Avviso Re-Impresa - Sostegno alle imprese…"), o stessa
        azione del programma ("Azione 2.1.2"): almeno la zona grigia, mai l'abbinamento automatico. Scartata
        l'inclusione come abbinamento automatico: "Re-Impresa" sarebbe contenuto in decine di titoli.
    """
    pa, pb = parole(a), parole(b)
    if not pa or not pb or incompatibili(a, b, ente_a, ente_b):
        return 0.0
    seq = difflib.SequenceMatcher(None, " ".join(pa), " ".join(pb)).ratio()
    sa, sb = set(pa), set(pb)
    dice = 2 * len(sa & sb) / (len(sa) + len(sb))
    s = max(seq, dice)
    corto = min((sa, sb), key=len)
    contenuto = (sa <= sb or sb <= sa) and (len(corto) >= 2 or len(next(iter(corto))) >= 5)
    azione = set(re.findall(r"\b\d \d \d\b", normalizza(a))) & set(re.findall(r"\b\d \d \d\b", normalizza(b)))
    if (contenuto or azione) and s < GRIGIA:
        s = GRIGIA
    if bool(segni(a, ente_a)["luoghi"]) != bool(segni(b, ente_b)["luoghi"]) and s >= SOGLIA:
        s = SOGLIA - 0.001  # una scheda regionale senza luogo può valere per tutte le province, o per nessuna: a mano
    return round(s, 3)


def migliore(titolo, candidati, ente=""):
    """(punteggio, candidato) con il titolo più simile; a parità vince il primo, così il risultato non cambia."""
    best = (0.0, None)
    for c in candidati:
        s = somiglianza(titolo, c["titolo"], ente or "", c.get("ente") or "")
        if s > best[0]:
            best = (s, c)
    return best


def esito(punteggio):
    return "sì" if punteggio >= SOGLIA else "grigio" if punteggio >= GRIGIA else "no"


# --- 2. Filtro di rilevanza ---

# Nell'ordine: la prima regola che corrisponde decide. Il titolo è già normalizzato (senza accenti, minuscolo).
NON_RILEVANTE = [
    ("non è un bando", r"graduatori|rettifica|errata corrige|ricorso|notificazione|conferenza di servizi|linee guida"
                        r"|prova di pubblicazione|vendita|locazione|alienazione|comodato|concessione (temporanea|demaniale"
                        r"|in |al pascolo|a titolo|postazioni)|concessione postazioni|postazioni arnie|interdizione"
                        r"|patrocinio|sponsor|domanda di riconoscimento|iscrizione|denunce sinistri|risarcimento|dosimetria"
                        r"|licenze per l utilizzo|convenzione (fra|tra)|asta pubblica|differimento|verbale|lotti pascolivi"
                        r"|elenco (unico|centri)|anagrafe|monitoraggio|rendicontazione|gestione (operativa|incarichi)"
                        r"|fabbisogno|capacita amministrativa|zone di innovazione"
                        r"|mappatura di opportunita|equivalenza dei titoli"),
    ("gara o fornitura", r"\bgara\b|\bgare\b|\bpcp\b|indagine di mercato|procedura negoziata|affidamento|fornitur|fornitori"
                         r"|operatori economici|consip|adesione alla convenzione|acquisizione (di |dei )?(beni|servizi)"
                         r"|\bfec \d|materiale rotabile|acquisto treni|ufficio stampa|servizio di (cattura|contabilita)"
                         r"|esperto bim|soggetti abilitati alla vendita|accreditamento|progettazione esecuzione dei lavori"
                         r"|assistenza tecnica|\bat asse|completamento depuratore|sistema fognario"),
    ("personale o concorso", r"concors|per l assunzione|assunzione a tempo (in)?determinato di|interpello|selezione interna|posizion[ei] organizzativ|personale"
                             r"|dipendenti|esperti|revisori|commissari|professionisti esterni|formatori|medic[oi]\b"
                             r"|istruttore forestale|avvocat|direttori delle piste|incarichi tecnici|valutatori"),
    ("solo enti pubblici", r"enti locali|enti pubblici|soggetti pubblici|interventi pubblici|edifici pubblici"
                           r"|illuminazione pubblica|\bcomune di\b|\bai comuni\b|comunali|enti erogatori|enti attuatori"
                           r"|soggetto attuatore|universit|politecnico|campus|conservatorio|\baler\b|\bfsc 2021"
                           r"|patto lombardia|piano lombardia|\bpsc\b|\bocdpc\b|difesa del suolo|rete acquedottistica"
                           r"|aeroport|sviluppo urbano sostenibile|aree interne|accordi negoziali|asse v\b|asse iv\b"
                           r"|incendi boschivi|piano interventi|biblioteche|palazzo sistema|metrotranvia|fondo comuni"),
]
# Titoli che non dicono di che bando si tratta ("Leggi e scarica l'avviso", "Approvazione avviso pubblico"): non si
# possono né filtrare né abbinare, quindi si contano a parte. "MICROCREDITO" invece è un titolo vero.
GENERICHE = set("leggi scarica approvazione decreto sperimentale sportello nuovo nuova".split())
# Un bando "per enti" che nomina anche imprese o privati resta dentro: "POR FESR Milano - sezione imprese".
ANCHE_PRIVATI = r"\bimpres[ae]\b|privati|famigli|cittadin|persone|student"


def rilevanza(titolo, tipo=None):
    """'rilevante' oppure il motivo per cui il bando non è per privati (persone o imprese).

    Il dataset lombardo dice il tipo di strumento ma non i destinatari, il sito siciliano nemmeno quello: resta il titolo.
    Scartato l'LLM per ora: costa, e una regola sbagliata si vede e si corregge, un giudizio del modello no.
    """
    if tipo and "concorsi" in tipo.lower():
        return "personale o concorso"
    t = normalizza(titolo)
    if not [p for p in parole(titolo) if p not in GENERICHE]:
        return "titolo senza informazioni"
    for motivo, rx in NON_RILEVANTE:
        if re.search(rx, t):
            if motivo == "solo enti pubblici" and re.search(ANCHE_PRIVATI, t):
                continue
            return motivo
    return "rilevante"


# --- 3. Intervalli ---

def wilson(k, n, z=1.96):
    """Quota k/n con l'intervallo di Wilson (95%): (quota, minimo, massimo). Con n = 0 non c'è niente da dire."""
    if n == 0:
        return (None, None, None)
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mezzo = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, max(0.0, centro - mezzo), min(1.0, centro + mezzo))


def chapman(n1, n2, m, z=1.96):
    """Totale stimato da due fonti: (stima, minimo, massimo, osservati).

    Chapman invece di Lincoln-Petersen (n1·n2/m): non esplode quando m è piccolo ed è quasi senza distorsione se le fonti
    sono indipendenti. Intervallo di Chao (1987), log-normale sui bandi non visti da nessuna delle due fonti: non scende
    mai sotto i bandi osservati, a differenza dell'intervallo simmetrico.
    """
    osservati = n1 + n2 - m
    stima = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m) / ((m + 1) ** 2 * (m + 2))
    non_visti = stima - osservati
    if non_visti <= 0 or var <= 0:
        return (stima, float(osservati), float(osservati), osservati)
    c = math.exp(z * math.sqrt(math.log(1 + var / non_visti ** 2)))
    return (stima, osservati + non_visti / c, osservati + non_visti * c, osservati)


# --- 4. Dati ---

def aperto(apertura, chiusura, giorno):
    """Senza data di chiusura un bando è aperto (così fanno sia il portale sia il dataset lombardo)."""
    a, c = (apertura or "")[:10], (chiusura or "")[:10]
    return (not a or a <= giorno) and (not c or c >= giorno)


def aperto_in_tutte(apertura, chiusura):
    return aperto(apertura, chiusura, GIORNO_PORTALE) and aperto(apertura, chiusura, GIORNO_RACCOLTA)


def codice_lombardia(url):
    """Il portale "Bandi e Servizi" chiude l'indirizzo con il codice del bando (es. ...-RLO12023036183)."""
    m = re.search(r"-([A-Z][A-Z0-9_]{5,})$", (url or "").rstrip("/"))
    return m.group(1) if m else None


def carica_portale(regione):
    """Bandi di una sola regione su incentivi.gov.it (i nazionali e pluriregionali non sono "della regione")."""
    out = []
    for x in json.loads(PORTALE.read_text(encoding="utf-8")):
        regioni = x.get("Regioni") or []
        regioni = regioni if isinstance(regioni, list) else [r.strip() for r in str(regioni).split(";")]
        if regioni != [regione]:
            continue
        ente = x.get("Soggetto_Concedente")
        out.append({"id": str(x.get("ID_Incentivo")), "titolo": x.get("Titolo") or "", "url": x.get("Link_istituzionale"),
                    "ente": (ente[0] if isinstance(ente, list) else ente) or "",
                    "apertura": (x.get("Data_apertura") or "")[:10] or None,
                    "chiusura": (x.get("Data_chiusura") or "")[:10] or None})
    for b in out:
        b["codice"] = codice_lombardia(b["url"])
        b["rilevanza"] = rilevanza(b["titolo"])
    return sorted(out, key=lambda b: b["id"])


def carica_elenco(fonte):
    f = ELENCHI / f"{fonte}_{GIORNO_RACCOLTA}.json"
    bandi = json.loads(f.read_text(encoding="utf-8"))["bandi"]
    for b in bandi:
        b["fonte"] = fonte
        b["codice"] = codice_lombardia(b["url"]) if fonte == "lombardia" else None
        b["rilevanza"] = rilevanza(b["titolo"])
    return bandi


def ultimo(prefisso):
    files = sorted(f for f in RAW.glob(f"{prefisso}_*.json") if not f.name.endswith(".meta.json"))
    return files[-1] if files else None


def carica_lombardia_ufficiale():
    f = ultimo("lombardia_anagrafica_bandi")
    if f is None:
        sys.exit("manca il dataset lombardo: python -m pipeline.copertura scarica-lombardia")
    meta = json.loads(f.with_suffix(".meta.json").read_text(encoding="utf-8"))
    righe = []
    for r in json.loads(f.read_text(encoding="utf-8")):
        righe.append({"codice": r["codice_bando"], "titolo": r.get("titolo_bando") or "", "tipo": r.get("tipo_strumento"),
                      "ente": r.get("ente"), "apertura": (r.get("apertura_adesione") or "")[:10] or None,
                      "chiusura": (r.get("chiusura_adesione") or "")[:10] or None})
    for r in righe:
        r["rilevanza"] = rilevanza(r["titolo"], r["tipo"])
    return sorted(righe, key=lambda r: r["codice"]), meta, f.name


def carica_revisione():
    """Decisioni prese a mano: coppie in zona grigia (stesso bando sì/no) e campioni del filtro (rilevante sì/no)."""
    if not REVISIONE.exists():
        return {"coppie": {}, "campione": {}, "revisore": None}
    d = yaml.safe_load(REVISIONE.read_text(encoding="utf-8")) or {}
    coppie = {(c["a"], c["b"]): c["stesso"] for c in d.get("coppie") or []}
    campione = {c["titolo"]: c["rilevante"] for c in (d.get("campione") or []) + (d.get("campione_fuori") or [])}
    return {"coppie": coppie, "campione": campione, "revisore": d.get("revisore")}


# --- 5. Abbinamento ---

def abbina(riferimento, candidati, revisione, per_codice=True):
    """Per ogni voce di riferimento: il candidato più simile e l'esito (sì / grigio / no), più l'esito dopo la revisione.

    Più voci possono puntare allo stesso candidato: il portale ha a volte una scheda sola per una misura che l'elenco
    ufficiale divide in tre (Dote Impresa Asse I, II, III). La domanda è "il bando c'è?", non "ci sono tante schede".
    """
    per_cod = {c["codice"]: c for c in candidati if c.get("codice")} if per_codice else {}
    out = []
    for r in riferimento:
        if r.get("codice") in per_cod:
            out.append({"rif": r, "cand": per_cod[r["codice"]], "punteggio": 1.0, "metodo": "codice", "esito": "sì",
                        "finale": True})
            continue
        s, c = migliore(r["titolo"], candidati, r.get("ente"))
        e = esito(s)
        rivisto = revisione["coppie"].get((r["titolo"], c["titolo"])) if c else None
        finale = e == "sì" if e != "grigio" else bool(rivisto)
        out.append({"rif": r, "cand": c, "punteggio": s, "metodo": "titolo", "esito": e, "rivisto": rivisto,
                    "finale": finale})
    return out


def unisci(*abbinamenti):
    """Più confronti sulle stesse voci: vale il primo che trova il bando, altrimenti quello col punteggio più alto.

    Così "portale + raccolta" non può trovare meno del portale da solo, cosa che succederebbe cercando il titolo più
    simile nell'unione: una scheda quasi uguale ma sbagliata può battere quella giusta.
    """
    out = []
    for voci in zip(*abbinamenti):
        trovato = [x for x in voci if x["finale"]]
        out.append(trovato[0] if trovato else max(voci, key=lambda x: x["punteggio"]))
    return out


def taratura(ufficiali, portale):
    """Le coppie certe per codice dicono quanto rende l'abbinamento per titolo: lo si rifà ignorando il codice.

    Come nella misura vera: per ogni bando del dataset si cerca la scheda più simile tra tutte quelle lombarde del
    portale (di ogni anno, quindi con molte edizioni vecchie che confondono). Per ogni coppia: l'esito automatico e se la
    scheda scelta è quella giusta. Una scheda con lo stesso titolo di quella giusta conta come giusta.
    """
    per_cod = {r["codice"]: r for r in ufficiali}
    righe = []
    for b in portale:
        uff = per_cod.get(b.get("codice"))
        if uff is None:
            continue
        s, scelto = migliore(uff["titolo"], portale, uff.get("ente"))
        giusto = scelto is not None and normalizza(scelto["titolo"]) == normalizza(b["titolo"])
        righe.append({"codice": uff["codice"], "esito": esito(s), "giusto": giusto, "punteggio": s,
                      "vero": somiglianza(uff["titolo"], b["titolo"], uff.get("ente") or "", b["ente"])})
    return righe


# --- 6. Le due regioni ---

def campione(voci, n=40, sale="copertura"):
    """Campione fisso per il controllo a mano: ordine dato dall'hash del titolo, quindi uguale a ogni esecuzione."""
    return sorted(voci, key=lambda v: hashlib.md5((sale + v["titolo"]).encode()).hexdigest())[:n]


def controllo_filtro(voci, revisione):
    """Confronto tra il filtro e il controllo a mano sul campione: (controllati, d'accordo, disaccordi)."""
    fatti = [(v, revisione["campione"][v["titolo"]]) for v in voci if v["titolo"] in revisione["campione"]]
    disaccordi = [(v, mano) for v, mano in fatti if (v["rilevanza"] == "rilevante") != mano]
    return len(fatti), len(fatti) - len(disaccordi), disaccordi


def lombardia(revisione):
    ufficiali, meta, nome = carica_lombardia_ufficiale()
    portale = carica_portale("Lombardia")
    nostri = carica_elenco("lombardia") + carica_elenco("finlombarda")
    aperti = [r for r in ufficiali if aperto_in_tutte(r["apertura"], r["chiusura"])]
    rilevanti = [r for r in aperti if r["rilevanza"] == "rilevante"]
    portale_aperti = [b for b in portale if aperto(b["apertura"], b["chiusura"], GIORNO_PORTALE)]
    portale_altri = [b for b in portale if b not in portale_aperti]

    a_portale = abbina(rilevanti, portale_aperti, revisione)
    a_portale_altri = abbina(rilevanti, portale_altri, revisione)  # schede che il portale dà per chiuse o future
    a_raccolta = abbina(rilevanti, nostri, revisione)
    a_portale_tutti = unisci(a_portale, a_portale_altri)
    a_unione = unisci(a_portale, a_raccolta)
    con_chiusura = [i for i, r in enumerate(rilevanti) if r["chiusura"]]
    provinciali = [i for i, r in enumerate(rilevanti) if r["codice"].startswith("PR_")]

    # Al contrario: i nostri bandi "aperti" del 7/11 che il dataset non ha o dà per chiusi.
    per_cod = {r["codice"]: r for r in ufficiali}
    racc = [b for b in carica_elenco("lombardia") if b["rilevanza"] == "rilevante"]
    stato_racc = {"nel dataset, aperti": 0, "nel dataset, ma chiusi o non ancora aperti per il dataset": 0,
                  "non nel dataset": 0}
    for b in racc:
        r = per_cod.get(b["codice"])
        if r is None:
            stato_racc["non nel dataset"] += 1
        elif aperto(r["apertura"], r["chiusura"], GIORNO_RACCOLTA):
            stato_racc["nel dataset, aperti"] += 1
        else:
            stato_racc["nel dataset, ma chiusi o non ancora aperti per il dataset"] += 1
    nuovi = sum(1 for b in racc if b["codice"] not in per_cod and re.search(r"(\d{6})$", b["codice"] or "")
                and int(b["codice"][-6:]) > max(int(c[-6:]) for c in per_cod if c[-6:].isdigit()))

    return {"meta": meta, "file": nome, "totale": len(ufficiali), "aperti": aperti, "rilevanti": rilevanti,
            "portale": portale, "portale_aperti": portale_aperti, "nostri": nostri,
            "a_portale": a_portale, "a_portale_altri": a_portale_altri, "a_portale_tutti": a_portale_tutti, "a_unione": a_unione, "a_raccolta": a_raccolta,
            "con_chiusura": con_chiusura, "provinciali": provinciali, "taratura": taratura(ufficiali, portale),
            "stato_racc": stato_racc, "racc_rilevanti": len(racc), "nuovi_dopo_dataset": nuovi,
            "controllo": controllo_filtro(campione(aperti), revisione), "campione": campione(aperti)}


DOPPIONE = 0.90


def raggruppa(voci):
    """Voci quasi uguali della stessa fonte contano come un bando solo (es. tre pubblicazioni dell'"Avviso n. 12/2024").

    Soglia alta (0.9), più severa dell'abbinamento: due finestre o due azioni dello stesso programma ("DIGIT IMPRESE"
    azione 1.1.2 e 1.2.2) restano separate. Il primo della lista rappresenta il gruppo.
    """
    gruppi = []
    for v in voci:
        for g in gruppi:
            if somiglianza(g[0]["titolo"], v["titolo"]) >= DOPPIONE:
                g.append(v)
                break
        else:
            gruppi.append([v])
    return gruppi


ENTE_SICILIA = r"regione sicilian|irfis"


def sicilia(revisione):
    portale = carica_portale("Sicilia")
    sito = carica_elenco("sicilia") + carica_elenco("irfis")
    portale_aperti = [b for b in portale if aperto_in_tutte(b["apertura"], b["chiusura"])]
    # Stessa popolazione per le due fonti: bandi della Regione o di IRFIS. Comuni, Agenzia delle Entrate, INAIL e Invitalia
    # sul sito della Regione non possono esserci per costruzione, e falserebbero la stima.
    b_tutti = [b for b in portale_aperti if re.search(ENTE_SICILIA, normalizza(b["ente"]))]
    gruppi_a = raggruppa([x for x in sito if x["rilevanza"] == "rilevante"])
    a = [g[0] for g in gruppi_a]
    b = [x for x in b_tutti if x["rilevanza"] == "rilevante"]
    abb_b = abbina(b, a, revisione, per_codice=False)   # ogni bando del portale: c'è sul sito?
    m = sum(1 for x in abb_b if x["finale"])
    # Gli stessi abbinamenti tra le liste complete: un bando del portale ritrovato tra i "non rilevanti" del sito
    # vorrebbe dire che il filtro sbaglia.
    abb_b_tutto = abbina(b, sito, revisione, per_codice=False)
    filtro_incoerente = [x for x in abb_b_tutto if x["finale"] and x["cand"]["rilevanza"] != "rilevante"]
    n1, n2 = len(a), len(b)
    stima = chapman(n1, n2, m)
    return {"portale": portale, "portale_aperti": portale_aperti, "b_tutti": b_tutti, "sito": sito, "a": a, "b": b,
            "doppioni": [g for g in gruppi_a if len(g) > 1],
            "abb_b": abb_b, "m": m, "n1": n1, "n2": n2, "stima": stima, "filtro_incoerente": filtro_incoerente,
            "esclusi_ente": [x for x in portale_aperti if x not in b_tutti],
            "controllo": controllo_filtro(campione(sito), revisione), "campione": campione(sito)}


# --- 7. Documento ---

FONTE_FUORI = "toscana"  # controllo del filtro su una lista che non è servita a scrivere le regole


def fuori_campione(revisione):
    voci = carica_elenco(FONTE_FUORI)
    return controllo_filtro(campione(voci, 30), revisione)


def pct(p):
    return "—" if p is None else f"{100 * p:.0f}%"


def quota(k, n):
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} = **{pct(p)}** ({pct(lo)}–{pct(hi)})" if n else "—"


def conta(abbinamenti, indici=None):
    voci = abbinamenti if indici is None else [abbinamenti[i] for i in indici]
    return sum(1 for x in voci if x["finale"]), len(voci)


def motivi(voci):
    c = {}
    for v in voci:
        c[v["rilevanza"]] = c.get(v["rilevanza"], 0) + 1
    return ", ".join(f"{k} {n}" for k, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def corto(t, n=80):
    t = " ".join(re.sub(r"&[a-z]+;", " ", t or "").split()).replace("|", "/")
    return t if len(t) <= n else t[: n - 1] + "…"


def coppie_grigie(*gruppi):
    """Coppie in zona grigia, una volta sola anche se compaiono in più confronti, nell'ordine dei confronti."""
    viste, out = set(), []
    for etichetta, abbinamenti in gruppi:
        for x in abbinamenti:
            k = (x["rif"]["titolo"], x["cand"]["titolo"]) if x["cand"] else None
            if x["esito"] == "grigio" and k not in viste:
                viste.add(k)
                out.append((etichetta, x))
    return out


def scrivi(lo, si, revisione, fuori):
    k_p, n = conta(lo["a_portale"])
    k_pt, _ = conta(lo["a_portale_tutti"])
    k_u, _ = conta(lo["a_unione"])
    k_r, _ = conta(lo["a_raccolta"])
    k_p_auto = sum(1 for x in lo["a_portale"] if x["esito"] == "sì")
    k_p_max = sum(1 for x in lo["a_portale"] if x["esito"] != "no")
    k_pc, n_c = conta(lo["a_portale"], lo["con_chiusura"])
    k_uc, _ = conta(lo["a_unione"], lo["con_chiusura"])
    senza_prov = [i for i in range(n) if i not in set(lo["provinciali"])]
    k_ps, n_s = conta(lo["a_portale"], senza_prov)
    k_pp, n_p = conta(lo["a_portale"], lo["provinciali"])
    per_codice = sum(1 for x in lo["a_portale"] if x["metodo"] == "codice")
    tar = lo["taratura"]
    t_auto_giusti = sum(1 for t in tar if t["esito"] == "sì" and t["giusto"])
    t_auto_sbagliati = sum(1 for t in tar if t["esito"] == "sì" and not t["giusto"])
    t_grigi_giusti = sum(1 for t in tar if t["esito"] == "grigio" and t["giusto"])
    t_grigi_sbagliati = sum(1 for t in tar if t["esito"] == "grigio" and not t["giusto"])
    t_persi = sum(1 for t in tar if t["esito"] == "no")
    meta = lo["meta"]
    agg = (meta.get("righe_aggiornate_il") or "?")[:10]

    N, Nlo, Nhi, oss = si["stima"]
    n1, n2, m = si["n1"], si["n2"], si["m"]
    sicilia_quote = {nome: (k / N, k / Nhi, k / Nlo) for nome, k in (("portale", n2), ("sito", n1), ("unione", oss))}

    def q_si(nome):
        p, a, b = sicilia_quote[nome]
        return f"**{pct(p)}** ({pct(a)}–{pct(b)})"

    c_lo, acc_lo, dis_lo = lo["controllo"]
    c_si, acc_si, dis_si = si["controllo"]
    c_fu, acc_fu, dis_fu = fuori
    grigie = coppie_grigie(("Lombardia: dataset ↔ portale", lo["a_portale"]),
                           ("Lombardia: dataset ↔ nostra raccolta", lo["a_raccolta"]),
                           ("Lombardia: dataset ↔ schede chiuse del portale", lo["a_portale_altri"]),
                           ("Sicilia: portale ↔ siti della Regione", si["abb_b"]))
    da_fare = sum(1 for _, x in grigie if x.get("rivisto") is None)
    revisore = revisione.get("revisore") or "—"

    r = [
        "# Copertura regione per regione: Lombardia e Sicilia",
        "",
        "*Generato da `pipeline/copertura.py` (`python -m pipeline.copertura`): non modificare a mano. "
        "Metodo in `docs/proposte-fase-2.md`, §3.5; scelte nella decisione 54 di `docs/decisioni.md`.*",
        "",
        "**Domanda:** dei bandi aperti per privati (persone, imprese, Terzo settore) di una regione, quanti ne troviamo? "
        "Ogni quota ha il suo intervallo di Wilson al 95%: con poche decine di bandi l'incertezza è grande.",
        "",
        "## Riepilogo per il report",
        "",
        "| regione | riferimento | fonti misurate | bandi di riferimento | trovati | copertura (IC 95%) | metodo |",
        "|---|---|---|---|---|---|---|",
        f"| Lombardia | elenco ufficiale (dataset regionale) | incentivi.gov.it | {n} | {k_p} | {quota(k_p, n)} | confronto con l'elenco |",
        f"| Lombardia | elenco ufficiale (dataset regionale) | portale + nostre raccolte | {n} | {k_u} | {quota(k_u, n)} | confronto con l'elenco ⚠ |",
        f"| Sicilia | nessun elenco: totale stimato {N:.0f} ({Nlo:.0f}–{Nhi:.0f}) | incentivi.gov.it | ≈{N:.0f} | {n2} | {q_si('portale')} | cattura e ricattura ⚠ |",
        f"| Sicilia | nessun elenco: totale stimato {N:.0f} ({Nlo:.0f}–{Nhi:.0f}) | portale + nostre raccolte | ≈{N:.0f} | {oss} | {q_si('unione')} | cattura e ricattura ⚠ |",
        "",
        f"Date: portale {GIORNO_PORTALE}, nostre raccolte {GIORNO_RACCOLTA}, dataset lombardo aggiornato al {agg}. "
        f"Contano i bandi aperti in tutte e due le date.",
        "",
        "Come leggerla:",
        f"- **incentivi.gov.it da solo non basta nemmeno in Lombardia**, una delle regioni che lo alimentano di più: ha "
        f"circa {pct(k_p / n if n else None)} dei bandi regionali per privati. In Sicilia ne ha ancora meno, e anche "
        f"l'estremo alto dell'intervallo resta basso.",
        f"- ⚠ La seconda riga lombarda è **alta per costruzione**: la nostra raccolta lombarda legge Bandi e Servizi, lo "
        f"stesso sistema da cui nasce il dataset. Dice che il raccoglitore funziona, non che abbiamo scovato bandi nascosti. "
        f"Il dato utile è quanti bandi le nostre raccolte aggiungono al portale: da {k_p} a {k_u} su {n}.",
        f"- ⚠ La stima siciliana regge solo se le due fonti fossero indipendenti, e non lo sono (sezione Sicilia). "
        f"Con {m} bandi in comune è un ordine di grandezza, non una misura.",
        "",
        "## Date",
        "",
        f"- incentivi.gov.it: export del **{GIORNO_PORTALE}**. Nostre raccolte: **{GIORNO_RACCOLTA}**. Dataset lombardo: "
        f"scaricato il {meta['scaricato'][:10]}, ma con le righe aggiornate al **{agg}** (campo `rowsUpdatedAt`).",
        f"- Per non contare come \"mancanti\" i bandi chiusi o aperti tra le due date, si tengono solo i bandi **aperti sia il "
        f"{GIORNO_PORTALE} sia il {GIORNO_RACCOLTA}**, secondo le date dell'elenco di riferimento (per il portale siciliano, "
        f"le date del portale). Il sito siciliano non dà date: lì vale il filtro \"non scaduti\" del sito.",
        f"- Il dataset lombardo è fermo al {agg}: i bandi pubblicati dopo non ci sono, e le proroghe arrivate dopo non si "
        f"vedono. Il denominatore lombardo è quindi \"i bandi già pubblicati a inizio ottobre e ancora aperti\".",
        "",
        "## Lombardia",
        "",
        f"**Elenco di riferimento:** \"{meta.get('dataset')}\" (dati.lombardia.it, `{LOMBARDIA_ID}`, licenza "
        f"{meta.get('licenza')}, attribuzione: {meta.get('attribuzione')}), {lo['totale']} righe dal 2016. "
        f"Aperte in tutte e due le date: **{len(lo['aperti'])}**. Il filtro di rilevanza ne toglie "
        f"{len(lo['aperti']) - n} ({motivi([x for x in lo['aperti'] if x['rilevanza'] != 'rilevante'])}): restano "
        f"**{n} bandi per privati**.",
        "",
        f"**Fonti misurate:** {len(lo['portale_aperti'])} schede di incentivi.gov.it aperte il {GIORNO_PORTALE} con la sola "
        f"Lombardia come regione (di ogni ente); {len(lo['nostri'])} voci delle nostre raccolte del {GIORNO_RACCOLTA} "
        f"(Bandi e Servizi {sum(1 for b in lo['nostri'] if b['fonte'] == 'lombardia')}, Finlombarda "
        f"{sum(1 for b in lo['nostri'] if b['fonte'] == 'finlombarda')}). Le Camere di commercio non entrano: i loro bandi "
        f"non sono nel dataset della Regione.",
        "",
        "| misura | copertura (IC 95%) |",
        "|---|---|",
        f"| **incentivi.gov.it**, schede aperte il {GIORNO_PORTALE} | {quota(k_p, n)} |",
        f"| … solo abbinamenti automatici (zona grigia tutta esclusa) | {quota(k_p_auto, n)} |",
        f"| … zona grigia tutta accettata (limite alto) | {quota(k_p_max, n)} |",
        f"| … contando anche le schede che il portale dà per chiuse o future | {quota(k_pt, n)} |",
        f"| … solo bandi con una data di chiusura | {quota(k_pc, n_c)} |",
        f"| … senza le {n_p} voci provinciali del collocamento mirato (PR_*) | {quota(k_ps, n_s)} |",
        f"| … solo le {n_p} voci provinciali (PR_*) | {quota(k_pp, n_p)} |",
        f"| **nostre raccolte** da sole (Bandi e Servizi + Finlombarda) | {quota(k_r, n)} |",
        f"| **portale + nostre raccolte** | {quota(k_u, n)} |",
        f"| … solo bandi con una data di chiusura | {quota(k_uc, n_c)} |",
        "",
        f"- Abbinamenti con il portale: {per_codice} per codice del bando nell'indirizzo, gli altri per titolo.",
        f"- Le {n_p} voci \"PR_*\" sono la stessa misura (Dote Impresa e Dote Unica Lavoro per il collocamento mirato, "
        f"servizi integrativi) ripetuta per ogni Provincia. Il dataset le conta una per una e così facciamo noi; pesano "
        f"molto, per questo le due righe separate.",
        f"- Le voci senza data di chiusura ({n - n_c} su {n}) sono aperte per il dataset, ma alcune sembrano misure mai "
        f"chiuse nel sistema (aperte nel 2019-2020). La riga \"solo bandi con una data di chiusura\" è la più sicura.",
        f"- Mancano anche alla nostra raccolta {n - k_r} voci: sono aperte per il dataset ma non per il sito, o il "
        f"raccoglitore le scarta (concorsi, gare). Il dataset fermo al {agg} spiega una parte della differenza.",
        "",
        f"**Al contrario** (le nostre voci del {GIORNO_RACCOLTA} contro il dataset): delle {lo['racc_rilevanti']} voci "
        f"rilevanti raccolte da Bandi e Servizi, "
        + "; ".join(f"{k} {v}" for k, v in lo["stato_racc"].items())
        + f". Delle voci assenti, {lo['nuovi_dopo_dataset']} hanno un codice più recente dell'ultimo del dataset "
        f"(pubblicate dopo l'aggiornamento); le altre sono soprattutto servizi sempre aperti (anagrafi, albi, "
        f"procedimenti) che il filtro sul titolo non riconosce. Le voci \"chiuse per il dataset\" ma aperte sul sito sono "
        f"probabilmente proroghe arrivate dopo il {agg}.",
        "",
        "## Sicilia",
        "",
        "Non c'è un elenco ufficiale scaricabile. Si stima il totale con la **cattura e ricattura** (il metodo per contare i "
        "pesci di un lago): due fonti, A e B; se B ritrova una parte p dei bandi di A, si suppone che anche A abbia una "
        "parte p di tutti i bandi esistenti.",
        "",
        "- **Popolazione:** bandi aperti per privati della Regione Siciliana o di IRFIS, la sua finanziaria.",
        f"- **A, siti della Regione** ({GIORNO_RACCOLTA}): {len(si['sito'])} voci (pagina \"Bandi\" filtrata su \"non "
        f"scaduti\" e \"Avvisi pubblici\", più IRFIS). Il filtro di rilevanza ne toglie "
        f"{sum(1 for x in si['sito'] if x['rilevanza'] != 'rilevante')} "
        f"({motivi([x for x in si['sito'] if x['rilevanza'] != 'rilevante'])}); "
        f"{sum(len(g) - 1 for g in si['doppioni'])} sono ripubblicazioni dello stesso avviso. **n₁ = {n1}**.",
        f"- **B, incentivi.gov.it** ({GIORNO_PORTALE}): {len(si['portale_aperti'])} schede aperte in tutte e due le date "
        f"con la sola Sicilia; {len(si['esclusi_ente'])} sono di altri enti (Comuni, Agenzia delle Entrate, INAIL, "
        f"Invitalia), che sul sito della Regione non possono esserci, e restano fuori. **n₂ = {n2}**.",
        f"- **In comune:** m = {m}. Stimatore di Chapman: N = (n₁+1)(n₂+1)/(m+1) − 1 = **{N:.0f}**; intervallo di Chao "
        f"al 95%: **{Nlo:.0f}–{Nhi:.0f}**. Bandi visti da almeno una fonte: {oss}.",
        "",
        "| fonte | bandi | quota del totale stimato (IC 95%) |",
        "|---|---|---|",
        f"| incentivi.gov.it | {n2} | {q_si('portale')} |",
        f"| siti della Regione e IRFIS | {n1} | {q_si('sito')} |",
        f"| tutte e due | {oss} | {q_si('unione')} |",
        "",
        f"Le quote usano l'intervallo del totale, non quello di Wilson. Senza stimare il totale, due quote dirette: il "
        f"portale ha {quota(m, n1)} dei bandi dei siti della Regione; i siti della Regione hanno {quota(m, n2)} delle "
        f"schede del portale.",
        "",
        "Le schede del portale, una per una:",
        "",
        "| scheda del portale | voce più simile sui siti della Regione | punteggio | stesso bando? |",
        "|---|---|---|---|",
    ]
    for x in si["abb_b"]:
        dec = "sì" if x["finale"] else "no"
        if x["esito"] == "grigio":
            dec += " (a mano)" if x.get("rivisto") is not None else " (da rivedere)"
        r.append(f"| {corto(x['rif']['titolo'])} | {corto((x['cand'] or {}).get('titolo', '—'))} | "
                 f"{x['punteggio']:.2f} | {dec} |")
    r += [
        "",
        "**Perché l'indipendenza non regge, e in che direzione sbaglia la stima:**",
        "- *Dipendenza positiva:* la Regione carica sul portale gli stessi bandi che pubblica sul suo sito. Un bando visto "
        "da A ha più probabilità di essere visto anche da B: m cresce e N **si sottostima**.",
        "- *Eterogeneità:* il portale per legge riguarda le imprese (art. 18-ter D.L. 34/2019). Un bando per le persone "
        "(lavastoviglie, donne vittime di violenza, prestito d'onore) non ha quasi nessuna probabilità di stare sul portale. "
        "Anche questo fa **sottostimare** N. Il totale va letto come un minimo e le coperture come un massimo.",
        "- *Numeri piccoli:* con m così basso basta un abbinamento in più o in meno per spostare molto N: per questo la "
        "tabella delle schede, da controllare.",
        "- Il sito non dà la data di apertura: un bando aperto dopo il 27/10 non poteva stare nell'export del portale. "
        "Pochi casi, nella stessa direzione.",
        "- Scartato: stimare la Sicilia dal solo portale con il rapporto della Lombardia. Le regioni alimentano il portale "
        "in modo troppo diverso (`docs/copertura-portale.md`).",
        "",
        "## Filtro di rilevanza",
        "",
        "Regole sul titolo (in Lombardia anche sul tipo \"Concorsi Pubblici e Avvisi sul Personale\"), in "
        "`NON_RILEVANTE` di `pipeline/copertura.py`. Si tolgono: atti che non sono bandi (vendite, locazioni, graduatorie, "
        "rettifiche, iscrizioni a elenchi), gare e forniture, personale e concorsi, bandi solo per enti pubblici (enti "
        "locali, comuni, università, opere FSC, ordinanze di protezione civile). Un bando \"per enti\" che nomina anche "
        "imprese, famiglie, studenti o privati resta dentro. Il Terzo settore e le associazioni contano come privati.",
        "",
        f"**Controllo a mano** su campioni fissi (ordinati per hash del titolo, quindi uguali a ogni esecuzione; "
        f"revisione: {revisore}):",
        f"- Lombardia, voci aperte del dataset: d'accordo {quota(acc_lo, c_lo)}.",
        f"- Sicilia, voci dei siti della Regione: d'accordo {quota(acc_si, c_si)}.",
        f"- ⚠ Questi due campioni vengono dalle stesse liste su cui sono state scritte le regole: l'accordo è ottimista. "
        f"Per questo un terzo campione da una lista mai guardata prima, la raccolta della Toscana del {GIORNO_RACCOLTA} "
        f"(regole non più toccate dopo averlo visto): d'accordo {quota(acc_fu, c_fu)}. È la stima onesta della "
        f"qualità del filtro su dati nuovi. Quasi tutti gli errori lasciano dentro voci che non sono bandi per privati.",
    ]
    for v, mano in dis_lo + dis_si + dis_fu:
        r.append(f"  - disaccordo: \"{corto(v['titolo'], 90)}\": filtro *{v['rilevanza']}*, a mano "
                 f"*{'rilevante' if mano else 'non rilevante'}*")
    if si["filtro_incoerente"]:
        r.append("- Schede del portale ritrovate tra le voci scartate del sito siciliano: "
                 + "; ".join(f"\"{corto(x['cand']['titolo'], 60)}\" ({x['cand']['rilevanza']})"
                             for x in si["filtro_incoerente"]))
    r += [
        "",
        "## Abbinamento",
        "",
        "1. **Codice:** gli indirizzi di Bandi e Servizi finiscono con il codice del bando, lo stesso del dataset "
        "(`...-RLO12023036183`). Quando il portale o la nostra raccolta rimandano lì, l'abbinamento è certo.",
        f"2. **Titolo:** minuscole, senza accenti né punteggiatura, senza parole vuote (articoli, \"avviso\", \"bando\", "
        f"nomi della regione). Punteggio = massimo tra somiglianza delle sequenze (`difflib`) e sovrapposizione delle "
        f"parole (Dice). **Stesso bando da {SOGLIA:.2f}**; zona grigia tra {GRIGIA:.2f} e {SOGLIA:.2f}, da decidere a mano.",
        "3. **Correzioni**, aggiunte guardando gli errori: luoghi, anni, assi o ordinali diversi (\"Provincia di Bergamo\" "
        "e \"di Como\", \"Brevetti 2021\" e \"2023\", \"Asse I\" e \"Asse II\") danno 0; il luogo si legge anche dal nome "
        "dell'ente. Un luogo in un titolo solo porta al massimo in zona grigia. Un titolo corto tutto contenuto nell'altro "
        "(\"Re-Impresa\"), o la stessa azione di programma (\"Azione 2.1.2\"), porta almeno in zona grigia.",
        f"4. **Taratura sulle coppie certe:** {len(tar)} schede del portale (di ogni stato) hanno il codice di un bando del "
        f"dataset. Rifacendo l'abbinamento solo per titolo, tra tutte le {len(lo['portale'])} schede lombarde del portale: "
        f"automatico e giusto {t_auto_giusti}, automatico e sbagliato {t_auto_sbagliati}, zona grigia con la scheda giusta "
        f"{t_grigi_giusti}, zona grigia con una sbagliata {t_grigi_sbagliati}, perso {t_persi}. La soglia è prudente: "
        f"sbaglia di rado da sola, e lascia molto alla revisione a mano.",
        "",
        f"**Zona grigia: {len(grigie)} coppie**, decise nel file `data/copertura/revisione.yaml` (revisione: {revisore}); "
        f"{da_fare} ancora da fare, che contano come non trovate.",
        "",
        "| confronto | voce di riferimento | più simile | punteggio | stesso bando? |",
        "|---|---|---|---|---|",
    ]
    for etichetta, x in grigie:
        dec = {True: "sì", False: "no", None: "da fare"}[x.get("rivisto")]
        r.append(f"| {etichetta} | {corto(x['rif']['titolo'], 70)} | {corto(x['cand']['titolo'], 70)} | "
                 f"{x['punteggio']:.2f} | {dec} |")
    r += [
        "",
        "## Limiti",
        "",
        f"- **Il filtro di rilevanza è sul titolo**, e su una lista nuova sbaglia {c_fu - acc_fu} voci su {c_fu} "
        f"(campione toscano). Il dataset lombardo non ha i destinatari, il sito "
        f"siciliano nemmeno il tipo di atto. Un denominatore che contiene voci non rilevanti fa sembrare la copertura più "
        f"bassa.",
        "- **Lombardia: \"elenco ufficiale\" vuol dire \"Bandi e Servizi\".** Il dataset è della Regione: mancano Camere di "
        "commercio, Comuni, ATS e le misure che Finlombarda pubblica solo sul suo sito. Per la Lombardia nel complesso la "
        "copertura vera è più bassa di quella in tabella.",
        "- **Il denominatore mescola persone e imprese.** Il portale per legge copre le imprese: una parte della sua bassa "
        "copertura è fuori dal suo compito, non un difetto. Per separarle servono i destinatari, che il dataset non ha; le "
        "schede di Bandi e Servizi li danno con le icone (nei documenti raccolti, fuori da git): si può aggiungere.",
        "- **Revisione delle coppie e dei campioni:** fatta da Claude (Opus 5.5) leggendo titoli, enti e date, senza aprire "
        "i bandi. Va confermata da Edoardo o Lorenzo.",
        "- **Una sola data, due sole regioni:** il caso migliore e uno dei peggiori del portale "
        "(`docs/copertura-portale.md`), non un campione delle regioni.",
        "",
    ]
    USCITA.write_text("\n".join(r), encoding="utf-8")


def scarica_lombardia(oggi):
    """Dataset lombardo in data/raw/, con i metadati (data, indirizzo, licenza). Al massimo uno al giorno."""
    out = RAW / f"lombardia_anagrafica_bandi_{oggi}.json"
    if out.exists():
        return out, "già presente"
    rp = urllib.robotparser.RobotFileParser(LOMBARDIA_SITO + "/robots.txt")
    rp.read()
    for url in (LOMBARDIA_DATI, LOMBARDIA_META):
        if not rp.can_fetch(UA, url):
            raise PermissionError(f"robots.txt non permette {url}")
    def get(url):
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
            return json.loads(r.read())
    righe = get(LOMBARDIA_DATI)
    vista = get(LOMBARDIA_META)
    out.write_text(json.dumps(righe, ensure_ascii=False, indent=0), encoding="utf-8")
    meta = {"fonte": LOMBARDIA_DATI, "dataset": vista.get("name"), "id": LOMBARDIA_ID,
            "scaricato": dt.datetime.now().isoformat(timespec="seconds"), "righe": len(righe),
            "licenza": (vista.get("license") or {}).get("name"), "attribuzione": vista.get("attribution"),
            "righe_aggiornate_il": dt.datetime.fromtimestamp(vista["rowsUpdatedAt"]).isoformat(timespec="seconds")
            if vista.get("rowsUpdatedAt") else None}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return out, f"{len(righe)} righe"


def main(argv):
    if argv == ["scarica-lombardia"]:
        percorso, esito_ = scarica_lombardia(dt.date.today().isoformat())
        print(f"{percorso.name}: {esito_}")
        return
    if argv:
        sys.exit(__doc__)
    revisione = carica_revisione()
    lo, si = lombardia(revisione), sicilia(revisione)
    scrivi(lo, si, revisione, fuori_campione(revisione))
    k, n = conta(lo["a_portale"])
    print(f"Lombardia: portale {k}/{n}; Sicilia: n1={si['n1']} n2={si['n2']} m={si['m']} "
          f"N={si['stima'][0]:.0f} ({si['stima'][1]:.0f}-{si['stima'][2]:.0f}). Scritto {USCITA.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
