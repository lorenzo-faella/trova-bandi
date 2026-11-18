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
# "\btermin": "Criteri di determinazione degli importi" non è una sezione sui termini (decisione 66).
TERMINI = re.compile(r"\btermin|scadenz|modalit\S* di presentazione|presentazione delle domande|domanda di partecipazione|"
                     r"quando|tempi e scadenze", re.I)
# L'inizio di un testo senza titoli conta se dice esplicitamente chi può partecipare.
INIZIO_UTILE = re.compile(r"requisiti|possono partecipare|possono presentare|beneficiari|destinatari", re.I)
# Si manda anche se nomina ISEE o residenza: "persone fisiche con ISEE inferiore ad Euro 30.000,00, residenti in
# Sicilia" (IRFIS). Prima della decisione 66 questi inizi passavano per caso, grazie alle parole del sommario. Non
# basta però a dire che il bando ha una sezione sui requisiti: senza, si continua a mandare tutto il documento.
INIZIO_CON_REQUISITI = re.compile(r"\bISEE\b|\bresident[ei] (?:in|nel|nella|a)\b", re.I)
RIMANDO = re.compile(r"art(?:icolo|\.)\s*(\d+)", re.I)
MAX_PAROLE_TITOLO = 10
TITOLO_FORTE = re.compile(r"(requisit|beneficiar|destinatar|chi pu|a chi )", re.I)
# Una riga che comincia con una parola minuscola (non la lettera di un elenco, "a)" o "b.") continua la frase di sopra.
CONTINUA = re.compile(r"^[a-zàèéìòù][a-zàèéìòù'’]*(\s|,|$)")
# Decisione 66. Il sommario: "ART. 8 REQUISITI ECONOMICO-PATRIMONIALI ........ 17" oppure "Art.4 Destinatari dei benefici 14".
PUNTINI = re.compile(r"(?:\.\s?){4,}|…{2,}|_{4,}")
NUMERO_PAGINA = re.compile(r"\s+\d{1,3}\s*$")
MIN_RIGHE_SOMMARIO = 3
# Decisione 66. Le tabelle in appendice ("Tab. 6 – Requisito economico-patrimoniale") e i rimandi che le richiamano
# ("i cui limiti massimi sono riportati nella tab.6"). Il titolo comincia con la maiuscola: "tabella 4 in appendice"
# a inizio riga è una frase andata a capo, non il titolo della tabella.
TABELLA = re.compile(r"^(?:Tab\.|TAB\.|Tabella|TABELLA)\s*(\d+(?:\.\s?\d+)?)\s*(?:bis\s*)?[–\-.:]", re.U)
RIMANDO_TABELLA = re.compile(r"\btab(?:ella|\.)\s*(\d+(?:\.\d+)?)", re.I)
MAX_RIGHE_TABELLA = 80


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
    # Un titolo comincia con la maiuscola: "presentazione della domanda, potrà..." è una frase andata a capo nel PDF
    # (decisione 62).
    return bool(breve and corpo[:1].isupper() and PAROLE_TITOLO.match(corpo)), None


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


def sommario(doc):
    """Le righe del sommario, come (pagina, indice della riga). Non sono titoli né testo da mandare all'LLM: prese per
    titoli aprivano decine di sezioni vuote, e il loro testo ("Art.4 Destinatari dei benefici 14") faceva scegliere
    l'inizio del documento e richiamare tutti gli articoli. Con i soli titoli del sommario in testa al testo, il
    modello ha preso il bando DSU del Lazio per "un indice del bando" (decisione 66).
    È sommario una riga con i puntini ("........ 17") che senza puntini e numero è un titolo o finisce con un numero;
    oppure una riga che finisce con un numero di pagina ed è un titolo senza quel numero, se nella stessa pagina ce ne
    sono almeno tre: un titolo vero può finire con un numero ("Tab. 6"), tre di fila sulla stessa pagina no."""
    out = set()
    for n, pagina in enumerate(doc["pagine"], 1):
        candidate = []
        for i, riga in enumerate(pagina.splitlines()):
            s = riga.strip()
            if PUNTINI.search(s):
                resto = PUNTINI.sub(" ", s).strip()
                if NUMERO_PAGINA.search(" " + resto) or e_titolo(resto)[0]:
                    out.add((n, i))
            elif NUMERO_PAGINA.search(s) and e_titolo(NUMERO_PAGINA.sub("", s))[0]:
                candidate.append((n, i))
        if len(candidate) >= MIN_RIGHE_SOMMARIO:
            out.update(candidate)
    return out


def tabelle(doc, salta=frozenset()):
    """Le tabelle con un titolo proprio: {numero: {titolo, righe: [(pagina, riga)]}}. Una tabella va dal suo titolo
    alla tabella dopo, al prossimo articolo o a MAX_RIGHE_TABELLA righe, anche su più pagine. `salta`: le righe del
    sommario e le intestazioni di pagina. La prima tabella con un numero vince: le altre sono di solito ripetizioni
    ("Tabella 5.3" su tre pagine)."""
    out, aperta = {}, None
    escluse = ripetute(doc) if len(doc["pagine"]) > 1 else set()
    for n, pagina in enumerate(doc["pagine"], 1):
        for i, riga in enumerate(pagina.splitlines()):
            s = riga.strip()
            if (n, i) in salta or s in escluse:
                continue
            m = TABELLA.match(s)
            if m or (aperta and (ARTICOLO.match(s) or len(aperta["righe"]) >= MAX_RIGHE_TABELLA)):
                aperta = None
            if m:
                numero = re.sub(r"\s", "", m.group(1))
                if numero not in out:
                    aperta = out[numero] = {"titolo": s, "righe": []}
            if aperta is not None:
                aperta["righe"].append((n, riga))
    return out


def sezioni(doc):
    """Divide il documento in sezioni: [{titolo, articolo, righe: [(pagina, riga)]}]. La prima ha titolo None."""
    out = [{"titolo": None, "articolo": None, "righe": []}]
    escluse = ripetute(doc) if len(doc["pagine"]) > 1 else set()
    indice = sommario(doc)
    for n, pagina in enumerate(doc["pagine"], 1):
        righe = pagina.splitlines()
        for i, riga in enumerate(righe):
            if (n, i) in indice:
                continue
            titolo, articolo = e_titolo(riga)
            if titolo and articolo is None:
                # Decisione 62. Una riga che continua in minuscolo sulla riga dopo è una frase andata a capo
                # ("Possono partecipare al bando ... i nuclei" / "familiari che risultino..."), non un titolo.
                # Non contano gli elenchi ("a) Forma giuridica") e i titoli tutti in maiuscolo ("4.2 REQUISITI").
                dopo = next((r.strip() for r in righe[i + 1:] if r.strip()), "")
                # Neanche le righe numerate ("1. Requisiti del soggetto proponente e dell'eventuale" / "aderente"):
                # il numero dice già che è un titolo, anche se va a capo.
                # E nemmeno i titoli sui requisiti spezzati a metà ("Chi può" / "partecipare"). "Possono partecipare
                # al bando ... i nuclei" invece è una frase: "possono" non basta.
                numerata = bool(NUMERATA.match(riga.strip()))
                forte = bool(TITOLO_FORTE.match(riga.strip()))
                if CONTINUA.match(dopo) and not riga.strip().isupper() and not numerata and not forte:
                    titolo = False
                # Subito dopo "ART. 1" da solo, la riga "REQUISITI DI PARTECIPAZIONE" è il seguito del titolo
                # dell'articolo, non una sezione nuova: si aggiunge al titolo, così la scelta delle sezioni la vede.
                elif out[-1]["articolo"] is not None and len(out[-1]["righe"]) == 1:
                    out[-1]["titolo"] += " " + riga.strip()
                    titolo = False
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
            return bool(INIZIO_UTILE.search(testo(s)) or INIZIO_CON_REQUISITI.search(testo(s)))
        # "Obblighi dei beneficiari" riguarda il dopo; "Requisiti per l'erogazione" no: conta quale parola viene prima.
        dopo, req = DOPO.search(s["titolo"]), REQUISITI.search(s["titolo"])
        if dopo and not (req and req.start() < dopo.start()):
            return False
        return bool(req or TERMINI.search(s["titolo"]))
    scelte = {i for i, s in enumerate(tutte) if utile(s)}
    if not any(INIZIO_UTILE.search(testo(tutte[i])) if tutte[i]["titolo"] is None else REQUISITI.search(tutte[i]["titolo"])
               for i in scelte):
        return None
    richiamati = {int(n) for i in scelte for n in RIMANDO.findall(testo(tutte[i]))}
    scelte |= {i for i, s in enumerate(tutte) if s["articolo"] in richiamati}
    return [tutte[i] for i in sorted(scelte)]


def tabelle_richiamate(doc, scelte):
    """Le tabelle che le sezioni scelte richiamano ("vedi tab. 6"), in fondo, come sezioni in più (decisione 66).
    "tab. 5" richiama anche 5.1, 5.2...; "tab. 5.1" solo quella. Una tabella che sta già in una sezione scelta non
    si ripete."""
    richiami = {re.sub(r"\s", "", m) for s in scelte for m in RIMANDO_TABELLA.findall(testo(s))}
    if not richiami:
        return []
    gia = {r for s in scelte for r in s["righe"]}
    out = []
    for numero, t in tabelle(doc, sommario(doc)).items():
        if any(numero == r or numero.startswith(r + ".") for r in richiami) and t["righe"][0] not in gia:
            out.append({"titolo": t["titolo"], "articolo": None, "righe": t["righe"]})
    return out


def estratto(doc):
    """Le sezioni scelte, come pagine con numero: {"titoli", "pezzi": [(pagina, testo)], "caratteri", "totale"}.
    None se bisogna usare tutto il documento."""
    tutte = sezioni(doc)
    scelte = scegli(tutte)
    if not scelte:
        return None
    scelte = scelte + tabelle_richiamate(doc, scelte)
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
