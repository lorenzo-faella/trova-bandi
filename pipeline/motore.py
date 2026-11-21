"""Stadio 4a: valutazione di un profilo d'impresa rispetto alle regole, con logica a tre valori.

Ogni requisito vale True (soddisfatto), False (non soddisfatto) o None (non si può dire: dato mancante,
codice ATECO troppo generico, comune fuori da un elenco che contiene comuni soppressi, requisito non modellabile).
Profilo: dict campo -> valore. tipologia, settore e ambito sono liste (un'impresa può essere sia
"Impresa" sia "Impresa - prevalenza femminile"). Campo assente o "non lo so" = non si sa.
Per le persone, "nucleo" è la lista dei componenti della famiglia, ognuno con i propri campi.
"""
import operator
from dataclasses import dataclass, field

IDONEO, QUASI, NON_IDONEO, MANCANO_DATI = "idoneo", "quasi idoneo", "non idoneo", "mancano dati"
# Nessun requisito fallito e nessun dato da chiedere, ma qualcosa che il motore non può controllare da solo.
DA_VERIFICARE = "da verificare"
# Come "da verificare", ma tutto ciò che resta aperto sono eccezioni rare (`portata: rara`): la persona è idonea
# salvo quei casi particolari, che le si mostrano con la citazione (decisioni 24 e 52).
IDONEO_SALVO = "idoneo, salvo eccezioni"
NON_SO = "non lo so"
# "Quasi idoneo" ha senso solo se il requisito mancato si può cambiare (aggiungere un codice ATECO,
# costituire l'impresa); la sede no: altrimenti metà dei bandi regionali d'Italia risulterebbe "quasi".
MODIFICABILI = {"tipologia", "settore", "ateco_2025", "ateco_2007"}


CONFRONTI = {"<=": operator.le, "<": operator.lt, ">=": operator.ge, ">": operator.gt}


def cifre(codice):
    return codice.replace(".", "")


def tutti(esiti):
    """E a tre valori: basta un no per il no; il sì richiede tutti sì."""
    esiti = list(esiti)
    if False in esiti:
        return False
    return None if None in esiti else True


def almeno_uno(esiti):
    """O a tre valori: basta un sì per il sì; il no richiede tutti no."""
    esiti = list(esiti)
    if True in esiti:
        return True
    return None if None in esiti else False


def rara(req):
    return "non_modellabile" in req and req.get("portata") == "rara"


def verifica(req, profilo, presumi_rare=False):
    """presumi_rare: le eccezioni rare valgono come soddisfatte, cioè si presume che il caso particolare non riguardi
    la persona. Mai dentro almeno_uno_di: lì un requisito presunto vero aprirebbe la via alternativa a tutti."""
    if "non_modellabile" in req:
        return True if presumi_rare and rara(req) else None
    if "almeno_uno_di" in req:
        return almeno_uno(verifica(q, profilo) for q in req["almeno_uno_di"])
    if "tutti_di" in req:
        return tutti(verifica(q, profilo, presumi_rare) for q in req["tutti_di"])
    if "almeno_un_componente" in req:
        nucleo = profilo.get("nucleo")
        if nucleo is None or nucleo == NON_SO:
            return None
        return almeno_uno(tutti(verifica(q, c, presumi_rare) for q in req["almeno_un_componente"]) for c in nucleo)
    v = profilo.get(req["campo"])
    if v is None or v == NON_SO:
        return None
    if req.get("anno_soglia") is not None and profilo.get("_anno_valutazione") != req["anno_soglia"]:
        return None  # un parametro annuale non si estende ad altri anni, né a un anno ignoto
    op = req["operatore"]
    if op in ("vero", "falso"):
        return bool(v) is (op == "vero")
    if op == "tra":
        return req["valore"][0] <= v <= req["valore"][1]
    if op in CONFRONTI:
        return CONFRONTI[op](v, req["valore"])
    valori = req["valori"]
    if op == "in":
        # una risposta multipla (chi studia e lavora: [studente, occupato]) soddisfa il requisito se una delle scelte è
        # nell'elenco (decisione 69)
        if (any(x in valori for x in v) if isinstance(v, list) else v in valori):
            return True
        return None if req.get("incerto_fuori_elenco") else False
    if op == "interseca":
        # una risposta singola è una stringa: set("occupato") sarebbe l'insieme delle sue lettere
        return bool(set(v if isinstance(v, list) else [v]) & set(valori))
    if op == "prefisso":
        # ATECO è gerarchico sulle cifre: 56 > 56.1 > 56.10 > 56.10.1
        mio = cifre(v)
        if any(mio.startswith(cifre(c)) for c in valori):
            return True
        if any(cifre(c).startswith(mio) for c in valori):
            return None  # il profilo dice "56", il bando chiede "56.10": serve il codice completo
        return False
    raise ValueError(f"operatore sconosciuto: {op}")


def figli(req):
    return req.get("almeno_uno_di") or req.get("tutti_di") or req.get("almeno_un_componente") or []


def contiene_non_modellabile(req):
    return "non_modellabile" in req or any(contiene_non_modellabile(q) for q in figli(req))


def eccezioni_rare(req):
    """Le eccezioni rare che verifica(..., presumi_rare=True) presume soddisfatte: non quelle dentro almeno_uno_di."""
    if rara(req):
        return [req]
    if "almeno_uno_di" in req:
        return []
    return [e for q in figli(req) for e in eccezioni_rare(q)]


def serve_un_dato(req, profilo):
    """C'è una domanda che potremmo ancora fare per arrivare a un sì o un no?"""
    if "non_modellabile" in req:
        return False
    if "almeno_un_componente" in req:
        nucleo = profilo.get("nucleo")
        if nucleo is None or nucleo == NON_SO:
            return True
        return any(serve_un_dato(q, c) for q in req["almeno_un_componente"] for c in nucleo)
    if figli(req):
        return any(verifica(q, profilo) is None and serve_un_dato(q, profilo) for q in figli(req))
    v = profilo.get(req["campo"])
    return v is None or v == NON_SO


@dataclass
class Esito:
    regola: dict
    stato: str
    falliti: list = field(default_factory=list)
    mancanti: list = field(default_factory=list)
    # Con IDONEO_SALVO: le eccezioni rare presunte, da mostrare con la loro citazione.
    eccezioni: list = field(default_factory=list)


def valuta(regola, profilo):
    falliti, mancanti, eccezioni = [], [], []  # mancanti: tutti i requisiti che valgono None, per qualunque motivo
    for req in regola["requisiti"]:
        r = verifica(req, profilo)
        if r is False:
            falliti.append(req)
        elif r is None:
            mancanti.append(req)
    if not falliti:
        stato = MANCANO_DATI if any(serve_un_dato(q, profilo) for q in mancanti) else \
            DA_VERIFICARE if any(contiene_non_modellabile(q) for q in mancanti) else \
            MANCANO_DATI if mancanti else IDONEO
        # Seconda lettura: se presumendo le eccezioni rare tutto torna sì, l'unica riserva sono loro.
        if stato == DA_VERIFICARE and all(verifica(q, profilo, presumi_rare=True) is True for q in mancanti):
            stato = IDONEO_SALVO
            eccezioni = [e for q in mancanti for e in eccezioni_rare(q)]
    else:
        # "quasi" solo se tutto il resto è verificato: con dati mancanti non sappiamo se manca uno solo
        quasi = len(falliti) == 1 and not mancanti and falliti[0].get("campo") in MODIFICABILI
        stato = QUASI if quasi else NON_IDONEO
    return Esito(regola, stato, falliti, mancanti, eccezioni)


def aperta(regola, giorno):
    if regola.get("finestre"):
        return any(f["apertura"] <= giorno <= f["chiusura"] for f in regola["finestre"])
    return (not regola["apertura"] or regola["apertura"] <= giorno) and \
        (not regola["chiusura"] or regola["chiusura"] >= giorno)


def stato_temporale(regola, giorno):
    """La mancanza di date non è la prova di uno sportello aperto.

    `aperta` rimane il filtro storico degli esperimenti sui metadati. La demo
    espone questa classificazione più precisa, senza inventare nuove scadenze.
    """
    if regola.get("finestre"):
        if aperta(regola, giorno):
            return "aperto"
        return "futuro" if any(f["apertura"] > giorno for f in regola["finestre"]) else "chiuso"
    if regola.get("apertura") and regola["apertura"] > giorno:
        return "futuro"
    if regola.get("chiusura") and regola["chiusura"] < giorno:
        return "chiuso"
    if regola.get("disponibilita") == "permanente":
        return "permanente"
    if regola.get("chiusura") and regola["chiusura"] < "2040-01-01":
        return "aperto"
    return "non verificato"


def valuta_tutte(regole, profilo, giorno=None):
    return [valuta(r, profilo) for r in regole if giorno is None or aperta(r, giorno)]
