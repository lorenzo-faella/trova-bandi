"""Le parti di un bando che parlano di requisiti, per mandare all'LLM solo quelle invece di tutto il documento.

Quasi ogni bando ha una sezione "Requisiti" o "Beneficiari", ma i titoli si scrivono in modi diversi:
  "ART. 2 – SOGGETTI BENEFICIARI E REQUISITI"      (Regione Toscana)
  "Requisiti di reddito e valore economico..."      (Regione Lombardia: righe brevi, senza numero)
  nessun titolo: i requisiti all'inizio del testo   (Comune di Genova)
Quindi un titolo si riconosce in tre modi: "Art. N"; una riga numerata; una riga breve, senza punteggiatura finale,
che comincia con una parola tipica dei titoli dei bandi. Si tengono le sezioni sui requisiti e sulle esclusioni,
quelle sui termini di presentazione (servono le date), gli articoli che queste richiamano ("di cui all'articolo 1")
e l'inizio del testo se parla di requisiti. Se non si trova nessuna sezione sui requisiti, si usa tutto il documento.
"""
import re

# Parole con cui comincia un titolo di sezione: servono a riconoscere anche i titoli delle sezioni che poi si scartano.
PAROLE_TITOLO = re.compile(
    r"^(requisit|beneficiar|destinatar|soggett|chi pu|possono|ammission|ammissibil|inammissibil|esclusion|cause|"
    r"condizion|termin|scadenz|modalit|domanda|presentazione|quando|contribut|entit|importo|valore|risorse|dotazione|"
    r"finalit|oggetto|premessa|istruttori|graduatori|erogazion|liquidazion|controll|revoc|obbligh|allegat|"
    r"documentazion|trattamento|informativa|norme|responsabil|contatt|spese|interventi|tipologia|assegnazion|"
    r"criteri|priorit|cumul|durata|decadenz|rinvi|disposizion|definizion|ambito|come |cosa |a chi |tempi|descrizione)",
    re.I)
ARTICOLO = re.compile(r"^(art\.?|articolo)\s*(\d+)\b", re.I)
NUMERATA = re.compile(r"^(\d{1,2}(\.\d{1,2})*[.)]?|[A-Z][.)])\s+(?=\S)")
REQUISITI = re.compile(r"requisit|beneficiar|destinatar|soggett|chi pu|a chi \S+ rivolt|possono|ammission|inammissibil|esclusion|"
                       r"cause d|condizioni d", re.I)
# Sezioni che nominano i beneficiari ma parlano di cosa succede dopo la concessione ("Obblighi dei beneficiari").
DOPO = re.compile(r"obbligh|revoc|decadenz|erogazion|liquidazion|controll|trattamento|rendicontazion", re.I)
TERMINI = re.compile(r"termin|scadenz|modalit\S* di presentazione|presentazione delle domande|domanda di partecipazione|"
                     r"quando|tempi e scadenze", re.I)
# L'inizio di un testo senza titoli conta se dice esplicitamente chi può partecipare.
INIZIO_UTILE = re.compile(r"requisiti|possono partecipare|possono presentare|beneficiari|destinatari", re.I)
RIMANDO = re.compile(r"art(?:icolo|\.)\s*(\d+)", re.I)
MAX_PAROLE_TITOLO = 10


def e_titolo(riga):
    """(è un titolo?, numero dell'articolo o None)."""
    s = riga.strip()
    if not s or len(s) > 120:
        return False, None
    m = ARTICOLO.match(s)
    if m:
        return True, int(m.group(2))
    corpo = NUMERATA.sub("", s, count=1)
    breve = len(corpo.split()) <= MAX_PAROLE_TITOLO and not s.endswith((".", ",", ";", ":"))
    return bool(breve and PAROLE_TITOLO.match(corpo)), None


def ripetute(doc):
    """Righe uguali in cima o in fondo a più pagine: intestazioni e piè di pagina ("Allegato A"). Non sono titoli:
    altrimenti una sezione che continua sulla pagina dopo verrebbe tagliata a metà. Un vero titolo ripetuto a metà
    pagina ("Beneficiari" di due misure diverse) resta un titolo."""
    viste = {}
    for n, pagina in enumerate(doc["pagine"], 1):
        righe = [r.strip() for r in pagina.splitlines() if r.strip()]
        for riga in set(righe[:3] + righe[-3:]):
            viste.setdefault(riga, set()).add(n)
    return {r for r, pagine in viste.items() if len(pagine) >= 2}


def sezioni(doc):
    """Divide il documento in sezioni: [{titolo, articolo, righe: [(pagina, riga)]}]. La prima ha titolo None."""
    out = [{"titolo": None, "articolo": None, "righe": []}]
    escluse = ripetute(doc) if len(doc["pagine"]) > 1 else set()
    for n, pagina in enumerate(doc["pagine"], 1):
        for riga in pagina.splitlines():
            titolo, articolo = e_titolo(riga)
            if titolo and riga.strip() not in escluse:
                out.append({"titolo": riga.strip(), "articolo": articolo, "righe": []})
            out[-1]["righe"].append((n, riga))
    return [s for s in out if s["righe"]]


def testo(sezione):
    return "\n".join(r for _, r in sezione["righe"])


def scegli(tutte):
    """Le sezioni da mandare all'LLM, nell'ordine del documento, oppure None se non c'è una sezione sui requisiti."""
    def utile(s):
        if s["titolo"] is None:
            return bool(INIZIO_UTILE.search(testo(s)))
        if DOPO.search(s["titolo"]):
            return False
        return bool(REQUISITI.search(s["titolo"]) or TERMINI.search(s["titolo"]))
    scelte = {i for i, s in enumerate(tutte) if utile(s)}
    if not any(tutte[i]["titolo"] is None or REQUISITI.search(tutte[i]["titolo"]) for i in scelte):
        return None
    richiamati = {int(n) for i in scelte for n in RIMANDO.findall(testo(tutte[i]))}
    scelte |= {i for i, s in enumerate(tutte) if s["articolo"] in richiamati}
    return [tutte[i] for i in sorted(scelte)]


def estratto(doc):
    """Le sezioni scelte, come pagine con numero: {"titoli", "pezzi": [(pagina, testo)], "caratteri", "totale"}.
    None se bisogna usare tutto il documento."""
    tutte = sezioni(doc)
    scelte = scegli(tutte)
    if not scelte:
        return None
    pezzi = []
    for s in scelte:
        for pagina, riga in s["righe"]:
            if pezzi and pezzi[-1][0] == pagina:
                pezzi[-1][1].append(riga)
            else:
                pezzi.append((pagina, [riga]))
    pezzi = [(p, "\n".join(r)) for p, r in pezzi]
    return {"titoli": [s["titolo"] or "(inizio del documento)" for s in scelte], "pezzi": pezzi,
            "caratteri": sum(len(t) for _, t in pezzi), "totale": sum(map(len, doc["pagine"]))}
